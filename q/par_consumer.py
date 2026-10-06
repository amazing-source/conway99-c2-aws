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
Deferral mode (Q_DEFER=1, user's decision of 06/10 evening): the pairs that have a root r of U with (r,y1)^2 + (r,y2)^2 = 5 or 4 are
NOT sent to the consumer. They are exactly the pairs the open lemmas T18 (dual minimum >= 10/7) and T20 (>= 11/7) would exclude
(LEMMA_TARGET_2026-10-06.md), and they hold 99 % of the search time. They are counted under two "DEFERRED (pending ...)" verdicts
and listed by their position in the stream (field "deferred"); chunk_done is then false, so nothing is ever counted as excluded
on the strength of an unproved lemma. Every other pair goes through the unchanged consumer as usual.
The merged record carries "merged": {shards, mode, par_consumer_sha256}. A shard that fails, or whose record does not match the
pairs and sha256 it was given, makes chunk_ok false: nothing is ever counted as excluded on a partial run."""
import sys, os, json, time, hashlib, subprocess, collections, tempfile, shutil


DEF18 = "DEFERRED (pending T18: root r with (r,y1)^2+(r,y2)^2 = 5)"
DEF20 = "DEFERRED (pending T20: root r with (r,y1)^2+(r,y2)^2 = 4)"


def classify(pkg, lid, pairs, deferred):
    """Fill deferred["T18"], deferred["T20"] with the stream positions of the pairs that have a witness root, and return the positions
    of the others. The y are converted to lattice coordinates exactly as scripts/hstage_stream_next.py does; a pair whose
    conversion fails is NOT deferred (the consumer will report it INVALID)."""
    import math
    sys.path.insert(0, os.path.join(pkg, "scripts"))
    import numpy as np
    from fractions import Fraction as F
    from frame_dfs_next import lattice_data
    gens = json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%03d.json" % int(lid))))["gens"]
    L = lattice_data(gens, F(1)); Bq = [[F(x) for x in row] for row in L["B"]]
    Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
    DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * x.denominator // math.gcd(DEN, x.denominator)
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64)
    RG = (L["R"] @ L["G"]).astype(np.int64)                             # one row per +- pair of roots
    keep = []
    if len(RG) == 0:
        return list(range(len(pairs)))
    for idx, line in enumerate(pairs):
        rec = json.loads(line); yy = []
        for key in ("y1", "y2"):
            num = []; ok_ = True
            for x in rec[key]:
                q = F(x)
                if DEN % q.denominator: ok_ = False; break
                num.append(q.numerator * (DEN // q.denominator))
            if not ok_: yy = None; break
            exD = np.array(num, dtype=object)
            cf = np.rint(np.array([float(v) for v in exD]) / DEN @ Binv).astype(np.int64)
            if not (np.abs(cf).max() < 2 ** 20 and np.array_equal(cf @ BD, exD.astype(np.int64))): yy = None; break
            yy.append(cf)
        if yy is None:
            keep.append(idx); continue
        a = RG @ yy[0]; b = RG @ yy[1]; Y = a * a + b * b
        if (Y == 5).any(): deferred["T18"].append(idx)
        elif (Y == 4).any(): deferred["T20"].append(idx)
        else: keep.append(idx)
    return keep


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
    deferred = {"T18": [], "T20": []}
    if os.environ.get("Q_DEFER", "") == "1" and n:
        keep_idx = classify(pkg, lid, pairs, deferred)
        pairs = [pairs[i] for i in keep_idx]
    ndef = len(deferred["T18"]) + len(deferred["T20"])
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
            running[nxt] = subprocess.Popen([sys.executable, cons, lid, f, o, lim], cwd=pkg, env=os.environ.copy(),
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
           "merged": {"shards": P, "workers": W, "mode": "round-robin", "defer": os.environ.get("Q_DEFER", "") == "1", "bad": bad,
                      "par_consumer_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]}}
    ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and end.get("sha256") == full_sha
    ok = ok and not bad and len(recs) == P
    ok = ok and sum(r["n_pairs"] for r in recs) + ndef == n
    if ndef:
        cnt[DEF18] += len(deferred["T18"]); cnt[DEF20] += len(deferred["T20"])
        out["verdicts"] = {k: v for k, v in cnt.items() if v}
        out["deferred"] = {"rule": "root r of U (one per +- pair) with (r,y1)^2 + (r,y2)^2 = 5 (T18) or, failing that, = 4 (T20); "
                                   "indices are 0-based positions among the pair lines of the producer stream",
                           "T18": deferred["T18"], "T20": deferred["T20"]}
    out["chunk_ok"] = ok
    out["chunk_done"] = ok and n == sum(c for v, c in cnt.items() if v.startswith("EXCLUDED") or v.startswith("SWAP-COVERED") or v == "TWIN-DEFERRED"
                                        or v.startswith("TWIN-CANON"))
    open(outp, "a").write(json.dumps(out) + "\n")
    print(json.dumps({k: out[k] for k in ("id", "chunk", "n_pairs", "orbits", "verdicts", "chunk_ok", "chunk_done", "wall_secs")} | {"shards": P, "workers": W, "bad": bad}), flush=True)
    if ok: shutil.rmtree(tmp, ignore_errors=True)                  # on a problem the shard files and logs are kept


if __name__ == "__main__":
    main()
