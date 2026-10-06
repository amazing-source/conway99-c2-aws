# The representatives stored in the repo (lemma/t18/r2_tau_<s>.json, shared by all the programs) against my own stage 1:
# same deficient pairs in the same order, every stored representative is one of my matchings, one per orbit, all orbits hit.
import json, itertools
import numpy as np
REPO = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma\t18"
REP = {"B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
       "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
       "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
for si, name in ((0, "B0"), (1, "B1"), (2, "B2")):
    th = json.load(open(REPO + rf"\r2_tau_{si}.json"))
    mine = json.load(open(f"ref4_stageB_{name}_0of1.json"))
    DEF = [tuple(d) for d in mine["DEF"]]
    B = np.zeros((9, 9), dtype=int)
    for w in REP[name].split():
        i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
    auts = [q for q in itertools.permutations(range(9)) if all(B[q[i], q[j]] == B[i, j] for i in range(9) for j in range(i + 1, 9))]
    idx = {d: k for k, d in enumerate(DEF)}
    gd = [[idx[tuple(sorted((q[a], q[b])))] for (a, b) in DEF] for q in auts]
    def canon(s):
        best = None
        for g in gd:
            img = [0] * 18
            for a in range(18): img[g[a]] = g[s[a]]
            img = tuple(img)
            if best is None or img < best: best = img
        return best
    cm = [canon(tuple(r)) for r in mine["reps"]]
    ct = [canon(tuple(r)) for r in th["reps"]]
    print(f"{name}: same DEF list: {[tuple(d) for d in th['DEF']] == DEF}; repo n_tau {th['n_tau']}; repo reps {len(ct)} (distinct orbits {len(set(ct))}); "
          f"mine {len(cm)} (distinct {len(set(cm))}); same set of orbits: {set(cm) == set(ct)}; same list in the same order: {[tuple(r) for r in th['reps']] == [tuple(r) for r in mine['reps']]}")
