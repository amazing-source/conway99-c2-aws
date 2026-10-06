# Round 3.  Coverage of the enumerator runs (r3_p250.py, B1, profile (2,5,0)) and comparison of its stage-B sets
# (tau, F, H) with the independent verifier (r3_verify.py B250), restricted to the matchings the enumerator completed.
# No import from the enumerators.  The lists of matchings of the two launch rounds are recomputed here from the launch
# rule: round 1 = residues mod 3 (completed: the first 262 / 314 / 250 of each), round 2 = the remaining indices, sorted,
# dealt into 3 groups (completed: the first 42 / 50 / 50 of each).
import json, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
NREP = 1259
R1 = {0: 262, 1: 314, 2: 250}
R2 = {0: 42, 1: 50, 2: 50}
R2FILES = {0: "r3_p250_1_0of3_idx752_BC.json", 1: "r3_p250_1_1of3_idx755_BC.json", 2: "r3_p250_1_2of3_idx758_BC.json"}
done = set()
for q in range(3):
    lst = [i for i in range(NREP) if i % 3 == q]
    d = json.load(open(os.path.join(HERE, f"r3_p250_1_{q}of3_BC_round1.json")))
    assert d["totals"]["tau_done"] == R1[q] and d["totals"]["tau"] == len(lst)
    done.update(lst[:R1[q]])
rem = sorted(set(range(NREP)) - done)
done2 = set()
for g in range(3):
    lst = rem[g::3]
    d = json.load(open(os.path.join(HERE, R2FILES[g])))
    assert d["totals"]["tau_done"] == R2[g] and d["totals"]["tau"] == len(lst), (g, d["totals"]["tau"], len(lst))
    done2.update(lst[:R2[g]])
alld = done | done2
left = sorted(set(range(NREP)) - alld)
print(f"enumerator coverage: round 1 completed {len(done)} matchings, round 2 completed {len(done2)}, total {len(alld)} of {NREP}; "
      f"not done: {len(left)}")
json.dump({"done": sorted(alld), "not_done": left}, open(os.path.join(HERE, "r3_coverage_B1.json"), "w"))


def min_y2(t):
    return min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t)


MY = {t: 2 * min_y2(t) for t in range(10)}
reps = json.load(open(os.path.join(HERE, "r2_tau_1.json")))["reps"]
theirs = set()
for fn in [f"r3_p250_1_{q}of3_BC_round1.json" for q in range(3)] + list(R2FILES.values()):
    for e in json.load(open(os.path.join(HERE, fn)))["H_stageB"]:
        if e["tau"] in alld:
            theirs.add((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
mine_all = 0; mine = set(); mine_done_all = 0
for q in range(3):
    d = json.load(open(os.path.join(HERE, f"r3v_B250_1_{q}of3.json")))
    assert not d["timed_out"]
    for e in d["H"]:
        mine_all += 1
        tau = reps[e["tau"]]
        mem = [k for o in e["F"] for k in (o, tau[o])]
        degs = [bin(h).count("1") for h in e["H"]]
        t = sum(degs) // 2
        okc = t <= 9 and sum(degs[k] - 1 for k in mem) <= 8 and sum(x * (x - 1) for x in degs) + MY[t] <= 36
        if e["tau"] in alld:
            mine_done_all += 1
            if okc:
                mine.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
print(f"verifier stage B (all 1259 matchings): {mine_all} triples (tau, F, H)")
print(f"on the {len(alld)} matchings completed by the enumerator: verifier {mine_done_all} triples, {len(mine)} after the counting "
      f"conditions of A14 g; enumerator {len(theirs)}; identical sets: {mine == theirs}; only verifier {len(mine - theirs)}; "
      f"only enumerator {len(theirs - mine)}")
nd = [e for q in range(3) for e in json.load(open(os.path.join(HERE, f'r3v_B250_1_{q}of3.json')))["H"] if e["tau"] not in alld]
print(f"stage-B triples of the verifier on the {len(left)} matchings NOT done by the enumerator: {len(nd)}, "
      f"in {len(set(e['tau'] for e in nd))} matchings")
