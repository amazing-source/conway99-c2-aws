"""T20, branch n_3 = 2: run the engine eng5z on the bases of one graph.
Usage: python run_n3.py <graph> <part> <nparts> <seconds per base> <output dir> [first] [count]
The bases of the graph (n3_cases.labelled_bases, then one representative per class of relabellings, in a fixed order) are numbered
0, 1, ...; this process treats those with index % nparts == part (optionally only indices first .. first + count - 1).
One JSON per base in the output dir (engine output: nodes per level, rejections, complete configurations, timeout flag) and one
line per base on stdout. A base is closed when "timeout" is false and "complete" is 0."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for v_ in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(v_, "1")
import n3_cases as NC, eng5z
name, part, nparts, tlim, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
first = int(sys.argv[6]) if len(sys.argv) > 6 else 0; count = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
os.makedirs(out, exist_ok=True)
recs, counts = NC.labelled_bases(name); reps = NC.quotient(recs, NC.bmat(name))
print("%s: %d classes of bases (labelled %s)" % (name, len(reps), counts), flush=True)
for idx, rec in enumerate(reps):
    if idx % nparts != part or idx < first or idx >= first + count: continue
    tag = os.path.join(out, "n3_%s_%04d" % (name.replace(".", ""), idx))
    if os.path.exists(tag + "_0of1.json") and not json.load(open(tag + "_0of1.json"))["timeout"]: continue
    prob = NC.CaseIN3(rec); t = time.time()
    so = sys.stdout; sys.stdout = open(os.devnull, "w")
    try: res = eng5z.run(prob, 0, 1, tlim, 99, tag)
    finally: sys.stdout.close(); sys.stdout = so
    print("BASE %s %d | %s | class size %d | h2 %d alpha %d | timeout %s | visited %s | kept %s | rej budget %d psd %d rank %d | complete %d | %.1f s" % (
        name, idx, prob.name, rec["class_size"], prob.h2, prob.alpha, res["timeout"], res["visited"], res["kept"], sum(res["rejected_budget"]),
        sum(res["rejected_psd"]), sum(res["rejected_rank"]), len(res["survivors"]), time.time() - t), flush=True)
