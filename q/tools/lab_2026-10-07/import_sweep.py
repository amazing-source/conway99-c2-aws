"""Lab import of the deferral sweep (C2, 2026-10-07). READS, CHECKS and REPORTS; it does not write the tracker.

  .venv/Scripts/python.exe scripts/cloud/import_sweep.py [--json out.json] [--compare <laptop SWEEP_STATE json>] [--lids 013,016]
                                                         [--manifest out.json]   (list of the records to certify, for q/qcert.py)

Records: aws_repo/resultats_q/<machine>/results/<lid>_<k>_<n>.jsonl (copied by `q/monitor_q.py --fetch`), kinds "stream" and
"golay_pairs", for the lattices still open in the tracker; plus the records already in data/finishC/stream/<lid>/chunks.jsonl
(chunks done before the queue existed are only there), under the same checks.

Checks on a record (a record failing one is REFUSED and listed):
  * chunk_ok; the lattice id and the chunk agree with the file name; 0 <= k < n;
  * engine: code_sha equals the engine of one of the lab packages c2_cloud_run*/MANIFEST.json (stream: engine_code_sha; Golay:
    engine_code_sha_golay);
  * the verdict counts add up to n_pairs;
  * stream: the producer's end line says complete = true, with the same sha256 and the same number of pairs as the record
    (this is the condition for a raised producer cap, merged.producer_max_out, and it is required of every record that has the
    field "producer");
  * merged records: no bad shard; the sha256 of par_consumer.py / defer_consumer.py is one of the versions of the compute repo;
  * deferral: the DEFERRED verdict counts equal the lengths of the index lists (stream: "deferred"; Golay: the DEFERRED entries of
    not_excluded); the indices are distinct and inside the stream;
  * no verdict outside the known classes.
A DEFERRED pair is NOT excluded. Classes of verdicts: at once (char-vector trap, dual minimum 9/7, set-up), search, twin, swap,
DEFERRED pending T18, DEFERRED pending T20, INCOMPLETE, other.

State of a stream lattice (plan.json gives its R y1 representatives; chunk k/n holds the representatives k, k+n, ...):
  records are taken in this order: every chunk_done record, then the records whose only open pairs are DEFERRED, each only if it
  covers a representative not yet covered. "fully computed" = the chunk_done records cover all R; "swept" = all R covered with the
  deferral records; representatives covered twice by the selected records are reported (their pairs are then counted twice).
State of a Golay lattice (001, 002): pair by pair over [0, pairs_total): best state among the records covering the pair
  (excluded > deferred T18 > deferred T20 > incomplete or other > not covered).
Twin classes: the classes the selected records deferred pairs to, with their state in the tracker."""
import sys, os, json, glob, hashlib, subprocess, collections
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(LAB, "scripts"))
REPO = os.path.join(LAB, "aws_repo")
CLASSES = ("excl_at_once", "excl_search", "twin", "swap", "defer_T18", "defer_T20", "incomplete", "other")


def cls(v):
    if v.startswith("DEFERRED (pending T18"): return "defer_T18"
    if v.startswith("DEFERRED (pending T20"): return "defer_T20"
    if "INCOMPLETE" in v: return "incomplete"
    if v.startswith("SWAP-COVERED"): return "swap"
    if v.startswith("TWIN") or "twin transfer" in v: return "twin"
    if "stage 1" in v or "star" in v or "Lemma Z" in v: return "excl_search"
    if v.startswith("EXCLUDED"): return "excl_at_once"
    return "other"


def engines():
    st, go = {}, {}
    for f in sorted(glob.glob(os.path.join(LAB, "c2_cloud_run*", "MANIFEST.json"))):
        m = json.load(open(f)); name = os.path.basename(os.path.dirname(f))
        if "engine_code_sha" in m: st.setdefault(json.dumps(m["engine_code_sha"], sort_keys=True), name)
        if "engine_code_sha_golay" in m: go.setdefault(json.dumps(m["engine_code_sha_golay"], sort_keys=True), name)
    return st, go


def wrapper_shas(path):
    """sha256 (16 hex) of every committed version of a file of the compute repo"""
    out = set()
    revs = subprocess.run(["git", "-C", REPO, "log", "--all", "--format=%H", "--", path], capture_output=True, text=True).stdout.split()
    for r in revs:
        b = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (r, path)], capture_output=True).stdout
        if b: out.add(hashlib.sha256(b).hexdigest()[:16]); out.add(hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()[:16])
    return out


def check(d, lid, k, n, ST, GO, PAR, DEF):
    """list of reasons to refuse the record (empty = accepted)"""
    bad = []
    if not d.get("chunk_ok"): return ["not chunk_ok"]
    if "%03d" % d.get("id", -1) != lid or list(d.get("chunk", [])) != [k, n] or not (0 <= k < n): bad.append("id / chunk do not match the file name")
    kind = d.get("kind", "stream"); cs = json.dumps(d.get("code_sha") or {}, sort_keys=True)
    if (kind == "stream" and cs not in ST) or (kind == "golay_pairs" and cs not in GO): bad.append("engine not of a lab package: %s" % cs)
    if sum(d["verdicts"].values()) != d.get("n_pairs"): bad.append("verdict counts do not add up to n_pairs")
    nd18 = sum(c for v, c in d["verdicts"].items() if cls(v) == "defer_T18"); nd20 = sum(c for v, c in d["verdicts"].items() if cls(v) == "defer_T20")
    if kind == "stream":
        p = d.get("producer")
        if p is not None and not (p.get("complete") is True and p.get("sha256") == d.get("sha256") and p.get("pairs") == d.get("n_pairs")):
            bad.append("producer end line: not complete, or sha256 / pairs differ")
        if p is None and (d.get("merged") or {}).get("producer_max_out"): bad.append("raised producer cap without the producer end line")
        df = d.get("deferred") or {}; i18 = df.get("T18", []); i20 = df.get("T20", [])
        if (nd18, nd20) != (len(i18), len(i20)): bad.append("DEFERRED counts differ from the index lists")
        allidx = list(i18) + list(i20)
        if len(set(allidx)) != len(allidx) or any(not (0 <= i < d.get("n_pairs", 0)) for i in allidx): bad.append("deferred indices repeated or out of range")
        if (nd18 or nd20) and not (d.get("merged") or {}).get("defer") and not df: bad.append("DEFERRED verdicts without deferral fields")
    else:
        ne = d.get("not_excluded") or []
        e18 = sum(1 for e in ne if cls(str(e.get("verdict", ""))) == "defer_T18"); e20 = sum(1 for e in ne if cls(str(e.get("verdict", ""))) == "defer_T20")
        if (nd18, nd20) != (e18, e20): bad.append("DEFERRED counts differ from not_excluded")
        a, b = d.get("range", [0, 0])
        if b - a != d.get("n_pairs") or any(not (a <= e.get("index", -1) < b) for e in ne): bad.append("range / indices inconsistent")
    m = d.get("merged")
    if m:
        if m.get("bad"): bad.append("merged record with bad shards")
        if m.get("par_consumer_sha256") and m["par_consumer_sha256"] not in PAR: bad.append("unknown par_consumer %s" % m["par_consumer_sha256"])
        if m.get("defer_consumer_sha256") and m["defer_consumer_sha256"] not in DEF: bad.append("unknown defer_consumer %s" % m["defer_consumer_sha256"])
    dl = d.get("deferral")
    if dl and dl.get("defer_consumer_sha256") and dl["defer_consumer_sha256"] not in DEF: bad.append("unknown defer_consumer %s" % dl["defer_consumer_sha256"])
    if any(cls(v) == "other" for v in d["verdicts"]): bad.append("unknown verdict: %s" % [v for v in d["verdicts"] if cls(v) == "other"][:2])
    return bad


def open_state(d):
    """'done' (every pair excluded / twin / swap), 'deferred' (the only open pairs are DEFERRED), or 'open'"""
    c = collections.Counter()
    for v, n in d["verdicts"].items(): c[cls(v)] += n
    if c["incomplete"] or c["other"]: return "open"
    if c["defer_T18"] or c["defer_T20"]: return "deferred"
    return "done" if d.get("chunk_done") else "open"


def main():
    import twin_transfer as TT
    lids = None
    if "--lids" in sys.argv: lids = set(sys.argv[sys.argv.index("--lids") + 1].split(","))
    T = json.load(open(os.path.join(LAB, "data", "finishC", "finishC_tracker.json")))
    OPEN = ["%03d" % v["id"] for v in T["lattices"] if v["status"] != "excluded"]
    if lids: OPEN = [l for l in OPEN if l in lids]
    ST, GO = engines(); PAR = wrapper_shas("q/par_consumer.py"); DEF = wrapper_shas("q/defer_consumer.py"); CL = TT.classes()
    recs = collections.defaultdict(list); refused = []; nfiles = 0; nold = 0
    for lid in OPEN:
        for f in glob.glob(os.path.join(REPO, "resultats_q", "*", "results", lid + "_*_*.jsonl")):
            nfiles += 1; b = os.path.basename(f)[:-6].split("_")
            try: k, n = int(b[1]), int(b[2])
            except ValueError: continue
            for l in open(f, errors="replace"):
                if '"verdicts"' not in l: continue
                try: d = json.loads(l)
                except ValueError: continue
                if d.get("kind") == "resolve" or "verdicts" not in d: continue
                if not d.get("chunk_ok"): continue
                bad = check(d, lid, k, n, ST, GO, PAR, DEF)
                if bad: refused.append((f.replace(REPO, ""), bad)); continue
                d["_src"] = [os.path.basename(os.path.dirname(os.path.dirname(f))), os.path.basename(f)]
                recs[lid].append(d)
        # records imported earlier by import_results.py (chunks done before the queue existed are only there)
        cf = os.path.join(LAB, "data", "finishC", "stream", lid, "chunks.jsonl")
        if os.path.exists(cf):
            have = {(tuple(d["chunk"]), d.get("sha256"), json.dumps(d["verdicts"], sort_keys=True)) for d in recs[lid]}
            for l in open(cf, errors="replace"):
                if not l.strip(): continue
                d = json.loads(l)
                if not d.get("chunk_ok") or "verdicts" not in d: continue
                kk = (tuple(d["chunk"]), d.get("sha256"), json.dumps(d["verdicts"], sort_keys=True))
                if kk in have: continue
                bad = check(d, lid, d["chunk"][0], d["chunk"][1], ST, GO, PAR, DEF)
                if bad: refused.append(("chunks.jsonl of %s, chunk %s" % (lid, d["chunk"]), bad)); continue
                have.add(kk); recs[lid].append(d); nold += 1
    out = {}; manifest = []
    print("files read: %d; records accepted: %d (of which %d only in the lab's chunks.jsonl); refused: %d" % (nfiles, sum(len(v) for v in recs.values()), nold, len(refused)))
    for f, bad in refused[:20]: print("  REFUSED %s: %s" % (f, "; ".join(bad)))
    print("%-4s %7s %11s | %10s %9s %9s %10s | %9s %9s %6s | %s" % ("lid", "records", "pairs", "at once", "search", "twin", "swap", "T18", "T20", "INCOMP", "state"))
    for lid in sorted(OPEN, reverse=True):
        R = recs.get(lid, []); c = collections.Counter(); o = {"records_accepted": len(R)}
        if R and R[0].get("kind") == "golay_pairs":
            N = R[0]["pairs_total"]; state = bytearray(N)        # 0 not covered, 1 incomplete/other, 2 deferred T20, 3 deferred T18, 4 excluded
            assert all(d["pairs_total"] == N for d in R)
            for d in R:
                a, b = d["range"]; opn = {}
                for e in d.get("not_excluded") or []:
                    x = cls(str(e.get("verdict", ""))); opn[e["index"]] = 3 if x == "defer_T18" else 2 if x == "defer_T20" else 1
                for i in range(a, b):
                    s = opn.get(i, 4)
                    if s > state[i]: state[i] = s
            h = collections.Counter(state)
            o.update(pairs=N, not_covered=h[0], incomplete=h[1], defer_T20=h[2], defer_T18=h[3], excluded=h[4], kind="golay")
            st = ("fully computed" if h[4] == N else "swept; %d + %d pairs pending T18 / T20" % (h[3], h[2]) if not (h[0] or h[1]) else
                  "NOT swept: %d pairs not covered, %d incomplete" % (h[0], h[1]))
            print("%-4s %7d %11d | %10s %9s %9s %10s | %9d %9d %6d | %s" % (lid, len(R), N, "(%d excluded)" % h[4], "", "", "", h[3], h[2], h[1], st))
        else:
            pf = os.path.join(LAB, "data", "finishC", "stream", lid, "plan.json")
            NR = len(json.load(open(pf))["y1_reps"]); cov = [0] * NR; sel = []; twins = collections.Counter()
            def key(d): return (tuple(d["chunk"]), d.get("sha256"))
            for want in ("done", "deferred"):
                seen = set()
                for d in sorted((d for d in R if open_state(d) == want), key=lambda d: (d["chunk"][1], d["chunk"][0], d.get("t", ""))):
                    if key(d) in seen: continue
                    k, n = d["chunk"]; mine = range(k, NR, n)
                    if all(cov[i] for i in mine): continue
                    seen.add(key(d)); sel.append(d)
                    for i in mine: cov[i] += 1
                if want == "done": full = all(cov)
            for d in sel:
                for v, m in d["verdicts"].items(): c[cls(v)] += m
                twins.update(d.get("twin_deferred") or {})
                df = d.get("deferred") or {}
                if df.get("T18") or df.get("T20"):
                    assert "_src" in d, "a deferral record that is only in chunks.jsonl"
                    manifest.append({"key": "%s:%d:%d" % (lid, d["chunk"][0], d["chunk"][1]), "lid": lid, "k": d["chunk"][0], "n": d["chunk"][1],
                                     "sha256": d["sha256"], "n_pairs": d["n_pairs"], "T18": len(df.get("T18", [])), "T20": len(df.get("T20", [])),
                                     "branch": "run/" + d["_src"][0], "file": d["_src"][1], "wall_secs": d.get("wall_secs"),
                                     "producer_max_out": (d.get("merged") or {}).get("producer_max_out")})
            npairs = sum(d["n_pairs"] for d in sel); dbl = sum(1 for x in cov if x > 1); miss = sum(1 for x in cov if x == 0)
            pend = sorted(k for k in twins if CL.get(eval(k), {"?"}) != {"excluded"})
            st = ("NOT swept: %d of %d y1 representatives not covered" % (miss, NR) if miss else
                  "fully computed" if full else "swept; %d + %d pairs pending T18 / T20" % (c["defer_T18"], c["defer_T20"]))
            if dbl: st += "; %d representatives covered twice" % dbl
            st += "; twin classes not yet excluded: %d of %d" % (len(pend), len(twins))
            o.update(pairs=npairs, selected=len(sel), y1_reps=NR, not_covered=miss, covered_twice=dbl, kind="stream", twin_classes=len(twins),
                     twin_pending=pend, **{x: c[x] for x in CLASSES})
            print("%-4s %7d %11d | %10d %9d %9d %10d | %9d %9d %6d | %s" % (lid, len(R), npairs, c["excl_at_once"], c["excl_search"], c["twin"], c["swap"],
                                                                     c["defer_T18"], c["defer_T20"], c["incomplete"], st))
        o["state"] = st; out[lid] = o
    if "--compare" in sys.argv:
        L = json.load(open(sys.argv[sys.argv.index("--compare") + 1])); print("comparison with the laptop's sweep report:")
        for lid in sorted(out, reverse=True):
            a = out[lid]; b = L.get(lid)
            if b is None: print("  %s: not in the laptop file" % lid); continue
            if a["kind"] == "golay":
                p = b.get("pairwise", {}); same = all(a[x] == p.get(y) for x, y in (("pairs", "pairs_total"), ("defer_T18", "defer_T18"), ("defer_T20", "defer_T20"), ("excluded", "excluded")))
            else:
                same = a["pairs"] == b["pairs"] and all(a[x] == b[x] for x in CLASSES)
            print("  %s: %s" % (lid, "same counts" if same else "DIFFERENT (lab %s / laptop %s)" % (
                {x: a.get(x) for x in ("pairs", "defer_T18", "defer_T20")}, {x: b.get(x) for x in ("pairs", "defer_T18", "defer_T20", "jobs_done", "jobs")})))
    if "--manifest" in sys.argv:
        manifest.sort(key=lambda m: (-m["n_pairs"], m["key"]))
        json.dump({"what": "stream records with DEFERRED pairs selected by the lab import (scripts/cloud/import_sweep.py); one certificate per "
                           "record (q/cert_stream.py): the stream is regenerated and every deferred position is checked", "records": manifest},
                  open(sys.argv[sys.argv.index("--manifest") + 1], "w"), indent=0)
        print("manifest: %d records, %d + %d deferred pairs, wall of the original jobs %.0f h" % (
            len(manifest), sum(m["T18"] for m in manifest), sum(m["T20"] for m in manifest), sum(m["wall_secs"] or 0 for m in manifest) / 3600))
    if "--json" in sys.argv: json.dump({"lattices": out, "refused": refused}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
