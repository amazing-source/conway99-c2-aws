"""Parallel wrapper around the package's stream consumer (C2, 2026-10-06). NOT part of the package: the engine is untouched.

  <producer> | python par_consumer.py <package dir> <lid> - <out.jsonl> <node_limit> <P> [<W>]

A one-y1 stream job is a single process: it reads the pairs of its chunk and writes ONE record at the end, so a heavy y1 holds one
core for hours and restarts from zero when the machine is reclaimed. The verdict of a pair depends on that pair only, so this
wrapper
  1. reads the whole producer stream (info lines, pair lines, end line) and recomputes its sha256 and pair count, exactly like
     scripts/hstage_stream_next.py;
  2. deals the pair lines round-robin into P shards, each closed by its own end line (pairs and sha256 of the shard);
  3. runs the UNCHANGED scripts/hstage_stream_next.py once per shard (same arguments, same environment, cwd = package), at most W
     at a time (default W = P). With P a few times W the shards are small, so the cores stay busy until the end instead of
     waiting for the shard that drew the heaviest pairs;
  4. adds the P records up into one record of the same format: verdict counts, twin_deferred, telemetry and not_excluded are summed
     or concatenated; n_pairs, sha256, producer and the chunk_ok / chunk_done formulas are those of the FULL stream.
Deferral mode (Q_DEFER=1, user's decision of 06/10 evening): each shard is run through q/defer_consumer.py instead, i.e. the same
consumer with the long searches of the pairs covered by the open lemmas T18 / T20 replaced by a "DEFERRED (pending ...)" verdict
(see that file). Those pairs come back in not_excluded; here they are replaced by their 0-based positions among the pair lines of
the producer stream (field "deferred"), which with the stream sha256 identifies them exactly. chunk_done is then false: nothing
is ever counted as excluded on the strength of an unproved lemma.
The merged record carries "merged": {shards, mode, par_consumer_sha256}. A shard that fails, or whose record does not match the
pairs and sha256 it was given, makes chunk_ok false: nothing is ever counted as excluded on a partial run."""
import sys, os, json, time, hashlib, subprocess, collections, tempfile, shutil


DEF18 = "DEFERRED (pending T18: root r with (r,y1)^2+(r,y2)^2 = 5)"
DEF20 = "DEFERRED (pending T20: root r with (r,y1)^2+(r,y2)^2 = 4)"


def positions(shard_file, i, P, entries):
    """Stream positions of the not_excluded entries of shard i: the consumer lists them in stream order, and line j of the shard is
    pair i + j * P of the stream. Returns None if an entry is not found."""
    out = []; it = iter(entries); cur = next(it, None); j = 0
    for raw in open(shard_file, "rb"):
        line = raw.rstrip(b"\r\n")
        if not line or cur is None: continue
        rec = json.loads(line)
        if rec.get("end"): break
        if "o" not in rec or "y1" not in rec: continue
        if rec["o"] == cur["o"] and rec["y1"] == cur["y1"] and rec["y2"] == cur["y2"]:
            out.append(i + j * P); cur = next(it, None)
        j += 1
    return out if cur is None else None


def main():
    pkg, lid, src, outp, lim, P = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], max(1, int(sys.argv[6]))
    cons = os.path.join(pkg, "scripts", "hstage_stream_next.py"); t0 = time.time()
    fh = sys.stdin.buffer if src == "-" else open(src, "rb")
    sh = hashlib.sha256(); n = 0; end = None; info_raw = []; info = []; pairs = []; orbits = set()
    for raw in fh:                                                    # same reading rules as hstage_stream_next.py
        line = raw.rstrip(b"\r\n")
        if not line: continue
        rec = json.loads(line)
        if rec.get("end"): end = rec; break
        if "o" not in rec or "y1" not in rec:
            info_raw.append(line); info.append(rec); continue
        sh.update(line + b"\n"); n += 1; orbits.add(rec["o"]); pairs.append(line)
    full_sha = sh.hexdigest()
    defer = os.environ.get("Q_DEFER", "") == "1"
    dcons = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defer_consumer.py")
    aside = {"T18": [], "T20": []}                                     # stream positions of the pairs set aside (deferral mode)
    P = max(1, min(P, max(1, len(pairs))))
    W = max(1, int(sys.argv[7])) if len(sys.argv) > 7 else P
    tmp = tempfile.mkdtemp(prefix="par_%s_" % os.path.basename(outp).replace(".jsonl", ""), dir=os.path.dirname(os.path.abspath(outp)))
    shards = []
    for i in range(P):
        mine = pairs[i::P]; s = hashlib.sha256()
        f = os.path.join(tmp, "shard_%d.jsonl" % i)
        with open(f, "wb") as w:
            for l in info_raw: w.write(l + b"\n")
            for l in mine: w.write(l + b"\n"); s.update(l + b"\n")
            e = {"end": True, "id": (end or {}).get("id"), "chunk": (end or {}).get("chunk"), "pairs": len(mine), "complete": True,
                 "sha256": s.hexdigest(), "shard": [i, P]}
            w.write(json.dumps(e).encode() + b"\n")
        shards.append((f, os.path.join(tmp, "shard_%d_out.jsonl" % i), len(mine), s.hexdigest()))
    del pairs
    running = {}; nxt = 0; rcs = [None] * P
    while nxt < P or running:                                         # at most W consumers at a time
        while nxt < P and len(running) < W:
            f, o, ni, si = shards[nxt]
            running[nxt] = subprocess.Popen([sys.executable, dcons, pkg, lid, f, o, lim] if defer else [sys.executable, cons, lid, f, o, lim],
                                            cwd=pkg, env=os.environ.copy(),
                                            stdout=open(os.path.join(tmp, "shard_%d.log" % nxt), "w"), stderr=subprocess.STDOUT)
            nxt += 1
        for i, p in list(running.items()):
            rc = p.poll()
            if rc is not None:
                rcs[i] = rc; del running[i]
        if running: time.sleep(0.5)
    recs = []; bad = []
    for i, (f, o, ni, si) in enumerate(shards):
        rc = rcs[i]; r = None
        if os.path.exists(o):
            ls = [l for l in open(o) if l.strip()]
            if ls: r = json.loads(ls[-1])
        if rc != 0 or r is None or r.get("chunk_ok") is not True or r.get("n_pairs") != ni or r.get("sha256") != si:
            bad.append({"shard": i, "exit": rc, "record": None if r is None else {k: r.get(k) for k in ("chunk_ok", "n_pairs", "sha256")},
                        "expected": [ni, si]})
        if r is not None and defer:                                  # DEFERRED pairs: y vectors -> stream positions
            for tag, name in (("T18", DEF18), ("T20", DEF20)):
                pos = positions(f, i, P, [e for e in r.get("not_excluded", []) if e.get("verdict") == name])
                if pos is None or len(pos) != r.get("verdicts", {}).get(name, 0):
                    bad.append({"shard": i, "deferred_not_located": tag})
                else: aside[tag] += pos
            r["not_excluded"] = [e for e in r.get("not_excluded", []) if e.get("verdict") not in (DEF18, DEF20)]
        if r is not None: recs.append(r)
    cnt = collections.Counter(); deferred = collections.Counter(); tel = collections.defaultdict(collections.Counter); keep = []; sample = []
    for r in recs:
        cnt.update(r.get("verdicts", {})); deferred.update(r.get("twin_deferred", {})); keep += r.get("not_excluded", [])
        sample += r.get("sample_search", [])
        for k, v in r.get("telemetry", {}).items(): tel[k].update(v)
    shas = {json.dumps(r.get("code_sha"), sort_keys=True) for r in recs}
    if len(shas) > 1: bad.append({"code_sha": sorted(shas)})
    step = max(1, (len(sample) + 49) // 50)
    out = {"id": int(lid), "chunk": end.get("chunk") if end else None, "n_pairs": n, "orbits": len(orbits), "sha256": full_sha,
           "producer": end, "producer_info": info[:3], "verdicts": dict(cnt), "twin_deferred": dict(deferred),
           "telemetry": {k: dict(v) for k, v in tel.items()}, "sample_search": sample[::step][:50], "not_excluded": keep,
           "wall_secs": round(time.time() - t0, 1), "machine": "labpc", "frame_dfs": recs[0].get("frame_dfs") if recs else None,
           "code_sha": recs[0].get("code_sha") if recs else None, "node_limit": int(lim),
           "conway99_c1_commit": recs[0].get("conway99_c1_commit") if recs else None, "t": time.strftime("%Y-%m-%d %H:%M:%S"),
           "merged": {"shards": P, "workers": W, "mode": "round-robin", "defer": defer, "bad": bad,
                      "par_consumer_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]}}
    if defer:
        out["merged"]["defer_consumer_sha256"] = hashlib.sha256(open(dcons, "rb").read()).hexdigest()[:16]
        out["merged"]["defer_nodes"] = int(os.environ.get("Q_DEFER_NODES", "10000"))
    ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and end.get("sha256") == full_sha
    ok = ok and not bad and len(recs) == P
    ok = ok and sum(r["n_pairs"] for r in recs) == n
    if defer:
        ok = ok and cnt.get(DEF18, 0) == len(aside["T18"]) and cnt.get(DEF20, 0) == len(aside["T20"])
        out["deferred"] = {"rule": "pair not decided by the engine within defer_nodes nodes, and U has a root r (one per +- pair) with "
                                   "(r,y1)^2 + (r,y2)^2 = 5 (T18) or, failing that, = 4 (T20); "
                                   "indices are 0-based positions among the pair lines of the producer stream",
                           "T18": sorted(aside["T18"]), "T20": sorted(aside["T20"])}
    out["chunk_ok"] = ok
    out["chunk_done"] = ok and n == sum(c for v, c in cnt.items() if v.startswith("EXCLUDED") or v.startswith("SWAP-COVERED") or v == "TWIN-DEFERRED"
                                        or v.startswith("TWIN-CANON"))
    open(outp, "a").write(json.dumps(out) + "\n")
    print(json.dumps({k: out[k] for k in ("id", "chunk", "n_pairs", "orbits", "verdicts", "chunk_ok", "chunk_done", "wall_secs")} | {"shards": P, "workers": W, "bad": bad}), flush=True)
    if ok: shutil.rmtree(tmp, ignore_errors=True)                  # on a problem the shard files and logs are kept


if __name__ == "__main__":
    main()
