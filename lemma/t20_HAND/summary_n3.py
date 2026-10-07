"""Summary of a run of the n_3 = 2 branch: reads every n3_*_0of1.json under the given folder.
Usage: python summary_n3.py <output dir>"""
import sys, os, json, glob, collections
out = sys.argv[1]; G = collections.defaultdict(lambda: collections.Counter()); surv = []; touts = []
EXPECT = {"I0": 44, "I1": 227, "I2": 87, "I3": 121, "I4": 146, "I5": 75}
for f in sorted(glob.glob(os.path.join(out, "**", "n3_*_0of1.json"), recursive=True)):
    r = json.load(open(f)); g = os.path.basename(f).split("_")[1]; c = G[g]
    c["bases"] += 1; c["nodes"] += sum(r["visited"]); c["candidates"] += sum(r["candidates"])
    c["rej_budget"] += sum(r["rejected_budget"]); c["rej_psd"] += sum(r["rejected_psd"]); c["rej_rank"] += sum(r["rejected_rank"])
    c["seconds"] += int(r["seconds"]); c["exact_elimination"] += sum(v for k, v in r["stats"].items() if k.startswith("rejected_by_exact_elimination"))
    if r["timeout"]: c["timeout"] += 1; touts.append(os.path.basename(f))
    elif r["survivors"]: c["with_survivors"] += 1; surv.append((os.path.basename(f), len(r["survivors"])))
    else: c["closed"] += 1
    for lvl, v in enumerate(r["visited"]): c["level_%02d" % lvl] += v
allclosed = True
for g in sorted(EXPECT):
    c = G[g]; ok = c["closed"] == EXPECT[g]; allclosed &= ok
    print("%s: bases %d of %d | closed %d | timeout %d | with survivors %d | nodes %d | candidates %d | rejected: budget %d, psd %d (of which exact elimination %d), rank %d | cpu %.1f h | %s" % (
        g, c["bases"], EXPECT[g], c["closed"], c["timeout"], c["with_survivors"], c["nodes"], c["candidates"], c["rej_budget"], c["rej_psd"],
        c["exact_elimination"], c["rej_rank"], c["seconds"] / 3600, "ALL CLOSED" if ok else "NOT CLOSED"))
    print("    nodes per level:", [c["level_%02d" % l] for l in range(13)])
print("timeouts:", touts[:40], "..." if len(touts) > 40 else "")
print("bases with complete configurations:", surv)
print("RESULT:", "every base of the six graphs is closed: no configuration with n_3 = 2 (one program)" if allclosed else "NOT complete")
