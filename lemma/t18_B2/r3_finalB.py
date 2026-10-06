# Round 3, final comparison on ALL 1259 matchings of B1 (profile (2,5,0)):
# union of the stage-B sets of every enumerator run  versus  the complete stage-B set of the independent verifier;
# and the complete list of stage-C survivors.  No import from the enumerators.
import json, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))


def min_y2(t):
    return min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t)


MY = {t: 2 * min_y2(t) for t in range(10)}
reps = json.load(open(os.path.join(HERE, "r2_tau_1.json")))["reps"]
theirs = set(); surv = set(); nfiles = 0
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3_p250_1_") and fn.endswith(".json") and "_BC" in fn:
        d = json.load(open(os.path.join(HERE, fn)))
        if 'H_stageB' not in d:
            continue          # trial runs made before the stage-B sets were saved
        nfiles += 1
        for e in d["H_stageB"]:
            theirs.add((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
        for e in d["survivors"]:
            surv.add((e["tau"], tuple(e["F"]), tuple(tuple(x) for x in e["types"]), tuple(e["rows"])))
mine = set(); mine_all = 0
for q in range(3):
    for e in json.load(open(os.path.join(HERE, f"r3v_B250_1_{q}of3.json")))["H"]:
        mine_all += 1
        tau = reps[e["tau"]]
        mem = [k for o in e["F"] for k in (o, tau[o])]
        degs = [bin(h).count("1") for h in e["H"]]
        t = sum(degs) // 2
        if t <= 9 and sum(degs[k] - 1 for k in mem) <= 8 and sum(x * (x - 1) for x in degs) + MY[t] <= 36:
            mine.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
print(f"enumerator files read: {nfiles}")
print(f"stage B, all 1259 matchings: verifier {mine_all} triples, {len(mine)} after the counting conditions; "
      f"enumerator (union of all runs) {len(theirs)}; identical sets: {mine == theirs}; "
      f"only verifier {len(mine - theirs)}, only enumerator {len(theirs - mine)}")
print(f"stage C, all 1259 matchings: {len(surv)} distinct survivors on 47 vertices:")
for s in sorted(surv):
    print("    matching", s[0], "F", list(s[1]), "W types", [list(x) for x in s[2]])
