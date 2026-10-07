"""T20, branch n_3 = 2: measure, run in pieces, and summarise (lab session, 07/10).

Why: the bases are very unequal. Most close in seconds or minutes, but many need hours on one core (measured: about 2 million
nodes for I.0 base 0). `run_n3.py` treats a base in one piece, so an interrupted machine loses all the work inside its bases, and
the static sharing leaves most cores idle at the end. Here a base is cut into `nparts` parts with the engine's own splitting
(the tasks are the children of the nodes of level 2, dealt in turn to the parts; every part walks the levels 0-2 again and
checks the task list by its sha1), the parts of all bases go through one pool, and there is one result file per part.

  python n3_split.py sample  <out> <nproc> [N=200] [tlim=900]
      for every base not yet closed: part 0 of N (the levels 0-2 in full, then one task in N, taken in turn).
      Estimate of the base: nodes = (nodes of levels 0-2) + N * (nodes below level 2 in the sample);
      seconds = (seconds of the sample) * (estimated nodes) / (nodes visited by the sample), i.e. the node rate of that very
      run on that very machine. A sample cut by the time limit gives a lower bound (flagged).
      Writes <out>/sample/ESTIMATE.json and ESTIMATE.txt.
  python n3_split.py run     <out> <nproc> [part_seconds=900] [tlim=10800]
      plan = for every base not yet closed, nparts = ceil(estimate / part_seconds), between 1 and 64 (16 if no estimate);
      written once in <out>/split/plan.json and reused when the run is resumed. Then every (base, part), heaviest first.
  python n3_split.py summary <out>
      recounts the coverage of the 700 classes from the files and prints the result.

Environment: N3_SKIP_LEMMA=1 leaves out the bases excluded by hand (isolation lemma of lemma/t20_CODEX/PROFILE_421.md: profile
(4,2,1) with an edge between the inner orbit of X_0' and another orbit); they are counted apart in the summary.
N3_ONLY="I.0:1,I.0:6" restricts to some bases (tests). N3_NO_RANK=1 turns the rank test off (machines without python-flint).

A base is closed by search when either its one-piece file <out>/<graph>/n3_<g>_<idx>_0of1.json has "timeout" false and no
survivor, or all its parts <out>/split/<graph>/n3s_<g>_<idx>_<p>of<n>.json exist with "timeout" false, the same task list
(sha1 and number), every own task done, the own tasks adding up to the number of tasks, and no survivor."""
import sys, os, json, time, math, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for v_ in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(v_, "1")
GRAPHS = ["I.0", "I.1", "I.2", "I.3", "I.4", "I.5"]
EXPECT = {"I.0": 44, "I.1": 227, "I.2": 87, "I.3": 121, "I.4": 146, "I.5": 75}
DEPTH = 2
_REPS = {}


def reps_of(name):
    if name not in _REPS:
        import n3_cases as NC
        recs, counts = NC.labelled_bases(name); _REPS[name] = NC.quotient(recs, NC.bmat(name))
        assert len(_REPS[name]) == EXPECT[name], (name, len(_REPS[name]))
    return _REPS[name]


def lemma_violation(rec):
    """profile (4,2,1) and an edge orbit between the inner orbit of X_0' and another orbit: impossible by the isolation lemma"""
    import n3_cases as NC
    return rec["inner"] is not None and any((rec["bits"] >> (2 * t)) & 3 for t, pr in enumerate(NC.PAIRS) if rec["inner"] in pr)


def g_(name): return name.replace(".", "")
def one_piece(out, name, idx): return os.path.join(out, name, "n3_%s_%04d_0of1.json" % (g_(name), idx))
def part_file(out, name, idx, p, n): return os.path.join(out, "split", name, "n3s_%s_%04d_%dof%d.json" % (g_(name), idx, p, n))


def load(f):
    try: return json.load(open(f))
    except Exception: return None


def closed_one_piece(out, name, idx):
    r = load(one_piece(out, name, idx))
    return r is not None and not r["timeout"] and not r["survivors"]


def split_state(out, name, idx, n):
    """(closed, text) for a base cut into n parts"""
    rs = [load(part_file(out, name, idx, p, n)) for p in range(n)]
    if any(r is None for r in rs): return False, "parts missing: %d of %d" % (sum(r is None for r in rs), n)
    if any(r["timeout"] for r in rs): return False, "time-out in %d part(s)" % sum(r["timeout"] for r in rs)
    if any(r["survivors"] for r in rs): return False, "COMPLETE CONFIGURATION(S): %d" % sum(len(r["survivors"]) for r in rs)
    if len({(r["task_list_sha1"], r["tasks_total"], r["nparts"], r["split_depth"]) for r in rs}) != 1: return False, "parts disagree on the task list"
    if any(r["tasks_done"] != r["tasks_mine"] for r in rs): return False, "own tasks not all done"
    if sum(r["tasks_mine"] for r in rs) != rs[0]["tasks_total"] or sorted(r["part"] for r in rs) != list(range(n)): return False, "tasks do not add up"
    return True, "closed"


def only():
    s = os.environ.get("N3_ONLY", "")
    return {(a.split(":")[0], int(a.split(":")[1])) for a in s.split(",") if a} or None


def todo_bases(out):
    """bases that still need a search: (name, idx), in a fixed order"""
    skip = os.environ.get("N3_SKIP_LEMMA", "0") == "1"; sel = only(); plan = load(os.path.join(out, "split", "plan.json")) or {}
    res = []
    for name in GRAPHS:
        for idx, rec in enumerate(reps_of(name)):
            if sel is not None and (name, idx) not in sel: continue
            if closed_one_piece(out, name, idx): continue
            n = plan.get("%s:%d" % (name, idx))
            if n and split_state(out, name, idx, n)[0]: continue
            if skip and lemma_violation(rec): continue
            res.append((name, idx))
    return res


def engine(name, idx, part, nparts, tlim, depth, tag):
    import n3_cases as NC, eng5z
    prob = NC.CaseIN3(reps_of(name)[idx]); os.makedirs(os.path.dirname(tag), exist_ok=True)
    so = sys.stdout; sys.stdout = open(os.devnull, "w")
    try: res = eng5z.run(prob, part, nparts, tlim, depth, tag, use_rank=os.environ.get("N3_NO_RANK", "0") != "1")
    finally: sys.stdout.close(); sys.stdout = so
    return res


def w_sample(a):
    out, name, idx, N, tlim = a
    tag = os.path.join(out, "sample", name, "samp_%s_%04d" % (g_(name), idx))
    r = engine(name, idx, 0, N, tlim, DEPTH, tag)                        # the levels 0..DEPTH in full, then one task in N
    sk = sum(r["visited"][:DEPTH + 1]); deep = sum(r["visited"][DEPTH + 1:]); run = max(1, sk + deep); est = sk + N * deep
    return {"base": "%s:%d" % (name, idx), "name": r["name"], "N": N, "tasks_seen": r["tasks_total"], "tasks_mine": r["tasks_mine"],
            "tasks_done": r["tasks_done"], "seconds": r["seconds"], "nodes_run": run, "timeout": bool(r["timeout"]),
            "est_nodes": est, "est_seconds": r["seconds"] * est / run, "survivors": len(r["survivors"])}


def w_run(a):
    out, name, idx, part, nparts, tlim = a
    f = part_file(out, name, idx, part, nparts); r = load(f)
    if r is not None and not r["timeout"]: return ("%s:%d" % (name, idx), part, nparts, "kept", 0.0, 0)
    res = engine(name, idx, part, nparts, tlim, DEPTH if nparts > 1 else 99, f[:-len("_%dof%d.json" % (part, nparts))])
    return ("%s:%d" % (name, idx), part, nparts, "timeout" if res["timeout"] else "done", res["seconds"], len(res["survivors"]))


def pool_map(fn, tasks, nproc, label):
    import multiprocessing as mp
    t0 = time.time(); k = 0
    with mp.Pool(nproc) as pool:
        for r in pool.imap_unordered(fn, tasks, chunksize=1):
            k += 1
            print("%s %d/%d  %.0f s  %s" % (label, k, len(tasks), time.time() - t0, json.dumps(r) if isinstance(r, dict) else r), flush=True)
            yield r


def cmd_sample(out, nproc, N=200, tlim=900):
    bases = todo_bases(out); print("sample: %d bases not closed, N = %d, depth %d" % (len(bases), N, DEPTH), flush=True)
    rows = list(pool_map(w_sample, [(out, n, i, N, tlim) for n, i in bases], nproc, "SAMPLE"))
    rows.sort(key=lambda r: -r["est_seconds"]); d = os.path.join(out, "sample"); os.makedirs(d, exist_ok=True)
    json.dump({"N": N, "depth": DEPTH, "tlim": tlim, "rows": rows}, open(os.path.join(d, "ESTIMATE.json"), "w"), indent=0)
    tot = sum(r["est_seconds"] for r in rows); cut = [r for r in rows if r["timeout"]]
    nodes = sum(r["est_nodes"] for r in rows); rate = sum(r["nodes_run"] for r in rows) / max(1e-9, sum(r["seconds"] for r in rows))
    L = ["bases sampled: %d; estimated total %.1f core-hours on this machine (%d samples cut by the time limit: their estimate is a lower bound)" % (len(rows), tot / 3600, len(cut)),
         "estimated nodes: %.3g; node rate of the samples: %.0f per second; at 129 per second (rate of the 183 closed bases): %.1f core-hours" % (nodes, rate, nodes / 129 / 3600),
         "method: per base, one task in %d below level %d, taken in turn; nodes = levels 0-%d in full + %d x sampled nodes; margin: about 20 %% on the total, more on a single base" % (N, DEPTH, DEPTH, N),
         "bases over 4 h: %d, 1-4 h: %d, 15 min - 1 h: %d, under 15 min: %d" % (
             sum(r["est_seconds"] > 14400 for r in rows), sum(3600 < r["est_seconds"] <= 14400 for r in rows),
             sum(900 < r["est_seconds"] <= 3600 for r in rows), sum(r["est_seconds"] <= 900 for r in rows)),
         "complete configurations met in the samples: %d" % sum(r["survivors"] for r in rows), "heaviest:"]
    L += ["  %-9s %8.2f h  %10.3g nodes  tasks %d%s  %s" % (r["base"], r["est_seconds"] / 3600, r["est_nodes"], r["tasks_seen"], " (cut)" if r["timeout"] else "", r["name"]) for r in rows[:25]]
    open(os.path.join(d, "ESTIMATE.txt"), "w").write("\n".join(L) + "\n"); print("\n".join(L), flush=True)


def cmd_run(out, nproc, part_seconds=900, tlim=10800):
    d = os.path.join(out, "split"); os.makedirs(d, exist_ok=True); pf = os.path.join(d, "plan.json"); plan = load(pf) or {}
    est = {r["base"]: r["est_seconds"] for r in (load(os.path.join(out, "sample", "ESTIMATE.json")) or {"rows": []})["rows"]}
    bases = todo_bases(out)
    for name, idx in bases:
        k = "%s:%d" % (name, idx)
        if k not in plan: plan[k] = max(1, min(64, math.ceil(est[k] / part_seconds))) if k in est else 16
    json.dump(plan, open(pf, "w"), indent=0)
    tasks = [(out, name, idx, p, plan["%s:%d" % (name, idx)], tlim) for name, idx in bases for p in range(plan["%s:%d" % (name, idx)])]
    tasks.sort(key=lambda a: -(est.get("%s:%d" % (a[1], a[2]), 1e9) / a[4]))
    print("run: %d bases, %d parts, %d processes, limit %d s per part" % (len(bases), len(tasks), nproc, tlim), flush=True)
    bad = [r for r in pool_map(w_run, tasks, nproc, "PART") if r[3] == "timeout" or r[5]]
    print("parts with a time-out or a complete configuration:", bad, flush=True)


def cmd_summary(out):
    plan = load(os.path.join(out, "split", "plan.json")) or {}
    tot = {"search": 0, "hand": 0, "open": 0, "nodes": 0, "cpu": 0.0, "hand_also_searched": 0}; alarms = []; opened = []
    for name in GRAPHS:
        c = {"search": 0, "hand": 0, "open": 0, "nodes": 0, "cpu": 0.0, "hand_also_searched": 0}
        for idx, rec in enumerate(reps_of(name)):
            k = "%s:%d" % (name, idx); n = plan.get(k); viol = lemma_violation(rec); files = []
            if closed_one_piece(out, name, idx): ok, txt, files = True, "closed", [one_piece(out, name, idx)]
            elif n:
                ok, txt = split_state(out, name, idx, n); files = [part_file(out, name, idx, p, n) for p in range(n)]
            else:
                r = load(one_piece(out, name, idx)); ok = False
                txt = "no file" if r is None else ("COMPLETE CONFIGURATION(S): %d" % len(r["survivors"]) if r["survivors"] else "time-out")
            if "COMPLETE" in txt: alarms.append((k, txt))
            if ok:
                c["search"] += 1; c["hand_also_searched"] += viol
                for f in files:
                    r = load(f); c["nodes"] += sum(r["visited"]); c["cpu"] += r["seconds"]
            elif viol: c["hand"] += 1
            else: c["open"] += 1; opened.append((k, txt))
        print("%s: %d classes | closed by search %d (of which %d also excluded by the hand lemma) | excluded by the hand lemma only %d | open %d | nodes %d | cpu %.1f h" % (
            name, EXPECT[name], c["search"], c["hand_also_searched"], c["hand"], c["open"], c["nodes"], c["cpu"] / 3600), flush=True)
        for q in tot: tot[q] += c[q]
    print("TOTAL: 700 classes | closed by search %d (%d also by the hand lemma) | hand lemma only %d | open %d | nodes %d | cpu %.1f h" % (
        tot["search"], tot["hand_also_searched"], tot["hand"], tot["open"], tot["nodes"], tot["cpu"] / 3600))
    print("open bases (first 30):", opened[:30])
    print("COMPLETE CONFIGURATIONS:", alarms if alarms else "none")
    if alarms: print("RESULT: a complete configuration exists: human review needed")
    elif tot["open"]: print("RESULT: NOT complete (%d bases open)" % tot["open"])
    elif tot["hand"]: print("RESULT: every class is closed, %d by search and %d by the hand lemma only: no configuration with n_3 = 2 (one program + the lemma)" % (tot["search"], tot["hand"]))
    else: print("RESULT: every class is closed by search: no configuration with n_3 = 2 (one program)")


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]; a = sys.argv[3:]
    if cmd == "sample": cmd_sample(out, int(a[0]), *[int(x) for x in a[1:3]])
    elif cmd == "run": cmd_run(out, int(a[0]), *[int(x) for x in a[1:3]])
    elif cmd == "summary": cmd_summary(out)
    else: raise SystemExit(__doc__)
