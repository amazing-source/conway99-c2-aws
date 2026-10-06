# Round 3, final bookkeeping for B1, profile (2,5,0): coverage after the third launch round, comparison of the stage-B sets
# with the verifier on everything completed, list of stage-C survivors, what remains.  No import from the enumerators.
import json, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
cov = json.load(open(os.path.join(HERE, "r3_coverage_B1.json")))
done = set(cov["done"]); left = cov["not_done"]
files3 = {0: None, 1: None}
for fn in os.listdir(HERE):
    if fn.startswith("r3_p250_1_0of2_idx") and fn.endswith("_BC.json"):
        files3[0] = fn
    if fn.startswith("r3_p250_1_1of2_idx") and fn.endswith("_BC.json"):
        files3[1] = fn
done3 = set()
for g in (0, 1):
    if files3[g] is None:
        print("third-round file missing for group", g); continue
    lst = left[g::2]
    d = json.load(open(os.path.join(HERE, files3[g])))
    assert d["totals"]["tau"] == len(lst)
    done3.update(lst[:d["totals"]["tau_done"]])
    print(f"{files3[g]}: matchings {len(lst)}, completed {d['totals']['tau_done']}, timed_out {d['timed_out']}, "
          f"H {d['totals']['H_after_counts']}, C_nodes {d['totals']['C_nodes']}, survivors {d['totals']['C_survivors']}")
alld = done | done3
rest = sorted(set(range(1259)) - alld)
print(f"coverage: {len(done)} + {len(done3)} = {len(alld)} of 1259 matchings completed; not done: {len(rest)}")
json.dump({"done": sorted(alld), "not_done": rest}, open(os.path.join(HERE, "r3_coverage_B1_final.json"), "w"))


def min_y2(t):
    return min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t)


MY = {t: 2 * min_y2(t) for t in range(10)}
reps = json.load(open(os.path.join(HERE, "r2_tau_1.json")))["reps"]
enum_files = [f"r3_p250_1_{q}of3_BC_round1.json" for q in range(3)] + \
             ["r3_p250_1_0of3_idx752_BC.json", "r3_p250_1_1of3_idx755_BC.json", "r3_p250_1_2of3_idx758_BC.json"] + \
             [f for f in files3.values() if f]
theirs = set(); surv = {}
for fn in enum_files:
    d = json.load(open(os.path.join(HERE, fn)))
    for e in d["H_stageB"]:
        if e["tau"] in alld:
            theirs.add((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
    for e in d["survivors"]:
        surv[tuple(e["rows"])] = (e["tau"], tuple(e["F"]), tuple(tuple(x) for x in e["types"]), fn)
mine = set(); rest_tr = 0; rest_tau = set()
for q in range(3):
    for e in json.load(open(os.path.join(HERE, f"r3v_B250_1_{q}of3.json")))["H"]:
        tau = reps[e["tau"]]
        mem = [k for o in e["F"] for k in (o, tau[o])]
        degs = [bin(h).count("1") for h in e["H"]]
        t = sum(degs) // 2
        okc = t <= 9 and sum(degs[k] - 1 for k in mem) <= 8 and sum(x * (x - 1) for x in degs) + MY[t] <= 36
        if e["tau"] in alld:
            if okc:
                mine.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
        elif okc:
            rest_tr += 1; rest_tau.add(e["tau"])
print(f"stage B on the completed matchings: verifier {len(mine)} triples, enumerator {len(theirs)}, identical sets: {mine == theirs}")
print(f"stage-C survivors (distinct 47-vertex configurations) on the completed matchings: "
      f"{sum(1 for v in surv.values() if v[0] in alld)}")
for rows, v in sorted(surv.items(), key=lambda kv: kv[1][:2]):
    print(f"   matching #{v[0]}, F = {list(v[1])}, W types {[list(x) for x in v[2]]}   [{v[3]}]"
          + ("" if v[0] in alld else "   (matching not completed)"))
print(f"NOT enumerated at stage C: {len(rest)} matchings, carrying {rest_tr} stage-B triples (verifier) in {len(rest_tau)} matchings")
