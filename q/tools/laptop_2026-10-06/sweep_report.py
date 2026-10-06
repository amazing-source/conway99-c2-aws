"""State of the 14 lattices after (or during) the deferral sweep, read from the queue and the result files (laptop, 2026-10-07).
  python sweep_report.py <repo> [--json out.json]
For each lattice of the queue:
  * jobs: queue keys done / total;
  * the record kept for a job key is, among its chunk_ok records, one with chunk_done if there is one, else the last one;
  * pairs by class, summed over the kept records: excluded at once (char-vector trap, dual minimum 9/7, pair set-up), excluded by a
    search, twin (transfer / deferred to a twin / canonical), swap-covered, DEFERRED pending T18, DEFERRED pending T20, INCOMPLETE,
    other not excluded;
  * golay lattices (001, 002): the records overlap (coarse old blocks, fine new ones), so the state is also resolved pair by pair
    over the whole pair list: a pair is "open" in a record if it is listed in not_excluded, and the best state among the records
    covering it is kept (excluded > deferred > incomplete).
Nothing here pronounces an exclusion: that is the lab's import. A DEFERRED pair is NOT excluded."""
import sys, os, json, subprocess, collections, io, zipfile, time
REPO = sys.argv[1]
ORDER = ["016", "015", "014", "013", "012", "011", "009", "008", "007", "006", "005", "003", "002", "001"]


def git(*a, binary=False):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=not binary).stdout


def cls(v):
    if v.startswith("DEFERRED (pending T18"): return "defer_T18"
    if v.startswith("DEFERRED (pending T20"): return "defer_T20"
    if "INCOMPLETE" in v: return "incomplete"
    if v.startswith("SWAP-COVERED"): return "swap"
    if v.startswith("TWIN") or "twin transfer" in v: return "twin"
    if "stage 1" in v or "star" in v or "Lemma Z" in v: return "excl_search"
    if v.startswith("EXCLUDED"): return "excl_at_once"
    return "other"


git("fetch", "-q", "--prune", "origin", "+refs/heads/queue:refs/remotes/origin/queue", "+refs/heads/run/q-*:refs/remotes/origin/run/q-*")
order = [l.strip() for l in git("show", "origin/queue:order.txt").splitlines() if l.strip()]
ev = [json.loads(l) for l in git("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
done = {j for e in ev if e["op"] == "done" for j in e["jobs"]}
recs = collections.defaultdict(list)                                # job key -> [(branch time, record)]
for r in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*").split():
    data = git("archive", "--format=zip", r, "results", binary=True)
    if not data:
        continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for f in z.namelist():
        b = f.split("/")[-1]
        if not b.endswith(".jsonl") or not b[:3].isdigit():
            continue
        key = b[:-6].replace("_", ":")
        for l in z.read(f).decode(errors="replace").splitlines():
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if "verdicts" in d and d.get("chunk_ok"):
                recs[key].append(d)
out = {}; print("state at %s UTC" % time.strftime("%d/%m %H:%M", time.gmtime()))
print("%-4s %11s %10s | %10s %10s %9s %9s | %9s %9s %7s %6s  %s" % ("lid", "jobs", "pairs", "at once", "search", "twin", "swap", "T18", "T20", "INCOMP", "other", "state"))
for lid in ORDER:
    keys = [j for j in order if j.split(":")[0] == lid]; c = collections.Counter(); nrec = 0; npairs = 0; missing = 0
    for k in keys:
        rr = recs.get(k, [])
        if k not in done or not rr:
            missing += 1; continue
        best = ([d for d in rr if d.get("chunk_done")] or rr)[-1]; nrec += 1; npairs += best.get("n_pairs", 0)
        for v, n in best["verdicts"].items(): c[cls(v)] += n
    o = {"jobs": len(keys), "jobs_done": len(keys) - missing, "pairs": npairs, **{x: c[x] for x in ("excl_at_once", "excl_search", "twin", "swap", "defer_T18", "defer_T20", "incomplete", "other")}}
    if lid in ("001", "002"):                                         # pair-by-pair resolution over the whole pair list
        N = None; state = None
        for k, rr in recs.items():
            if k.split(":")[0] != lid: continue
            for d in rr:
                if "range" not in d: continue
                if N is None:
                    N = d["pairs_total"]; state = bytearray(N)        # 0 not covered, 1 incomplete/other, 2 deferred T20, 3 deferred T18, 4 excluded
                a, b = d["range"]; opn = {}
                for e in d.get("not_excluded", []):
                    v = str(e.get("verdict", "")); opn[e["index"]] = 3 if v.startswith("DEFERRED (pending T18") else 2 if v.startswith("DEFERRED (pending T20") else 1
                for i in range(a, b):
                    s = opn.get(i, 4)
                    if s > state[i]: state[i] = s
        if N:
            h = collections.Counter(state)
            o["pairwise"] = {"pairs_total": N, "not_covered": h[0], "incomplete_or_other": h[1], "defer_T20": h[2], "defer_T18": h[3], "excluded": h[4]}
    if missing:
        st = "%d jobs left" % missing
    elif lid in ("001", "002") and "pairwise" in o:
        p = o["pairwise"]
        st = ("fully computed" if not (p["not_covered"] or p["incomplete_or_other"] or p["defer_T18"] or p["defer_T20"]) else
              "swept; %d + %d pairs pending T18 / T20" % (p["defer_T18"], p["defer_T20"]) if not (p["not_covered"] or p["incomplete_or_other"]) else
              "NOT swept: %d pairs not covered, %d incomplete" % (p["not_covered"], p["incomplete_or_other"]))
    elif c["incomplete"] or c["other"]:
        st = "NOT swept: %d incomplete, %d other" % (c["incomplete"], c["other"])
    elif c["defer_T18"] or c["defer_T20"]:
        st = "swept; %d + %d pairs pending T18 / T20" % (c["defer_T18"], c["defer_T20"])
    else:
        st = "fully computed (twin dependencies and exclusion: lab import)"
    o["state"] = st; out[lid] = o
    print("%-4s %11s %10d | %10d %10d %9d %9d | %9d %9d %7d %6d  %s" % (lid, "%d/%d" % (o["jobs_done"], o["jobs"]), npairs, c["excl_at_once"], c["excl_search"], c["twin"], c["swap"],
                                                                 c["defer_T18"], c["defer_T20"], c["incomplete"], c["other"], st))
    if "pairwise" in o: print("       pair by pair: %s" % o["pairwise"])
if "--json" in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
