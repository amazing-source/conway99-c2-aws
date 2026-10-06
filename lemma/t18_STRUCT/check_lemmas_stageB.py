# Consistency check of the hand lemmas (t even, t <= 6, a_2 <= 2 on A_p) against the stage-B triples (tau, F, H)
# produced by the other agents (budgets + PSD on S u {p} u X_2).  Read-only.  The lemmas are proved by hand;
# this only counts how many stage-B triples they remove.
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FILES = {0: [("t18_B0/r3_p250_0_0of1_B.json", "H_stageB")],
         1: [("t18/r3v_B250_1_%dof3.json" % i, "H") for i in range(3)],
         2: [("t18/r3v_B250_2_0of1.json", "H")]}
for s in (0, 1, 2):
    reps = json.load(open(os.path.join(ROOT, "t18", "r2_tau_%d.json" % s)))["reps"]
    seen = set(); ct = Counter(); cA = Counter(); killed = 0; n = 0; cmax = Counter()
    for fn, key in FILES[s]:
        d = json.load(open(os.path.join(ROOT, fn)))
        for e in d[key]:
            k = (e["tau"], tuple(e["F"]), tuple(e["H"]))
            if k in seen: continue
            seen.add(k); n += 1
            tau = reps[e["tau"]]
            a2 = [bin(h).count("1") for h in e["H"]]
            t = sum(a2) // 2
            mem = sorted(q for o in e["F"] for q in (o, tau[o]))
            aA = tuple(sorted(a2[q] for q in mem))
            ct[t] += 1; cA[aA] += 1; cmax[max(a2)] += 1
            if t % 2 or t > 6 or max(aA) > 2:
                killed += 1
    print("B%d: %d stage-B triples; t: %s; a_2 on A_p (sorted): %s; max a_2 on X_2: %s; removed by the lemmas: %d"
          % (s, n, sorted(ct.items()), sorted(cA.items()), sorted(cmax.items()), killed))
