# Independent brute-force re-check of step 4 (r2_ext2.py) on a few PSD-surviving Y-tables.
# Differences with r2_ext2.py: no incremental pruning (all 60*24*4 = 5760 assignments of X_2-neighbours to W are built in
# full), no compatibility prefilter on the types (all 3-sets of unordered pairs {i,j} with the right deficits and an
# admissible single type), budgets checked by integer matrix multiplication (numpy), PSD only on budget-valid graphs.
# usage: python r2_ext2_bruteforce.py <structure> <json of r2_stage2.py> <number of tables>
import json, os, sys, itertools
import numpy as np
from enum_S import neg_certificate
here = os.path.dirname(os.path.abspath(__file__))
si = int(sys.argv[1]); ntab = int(sys.argv[3])
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(d) for d in td["DEF"]]
AS1 = set((Np[0], Nm[0]) for Np, Nm, flag in types[name] if flag and len(Np) == 1)
d = json.load(open(os.path.join(here, sys.argv[2])))
for ex in d["examples"][:ntab]:
    tau, Az, H, G, F = ex["tau"], ex["Az"], ex["H"], ex["G"], ex["F"]
    A0 = np.zeros((51, 51), dtype=np.int64)
    def add(M, u, v):
        M[u, v] = 1; M[v, u] = 1
    for i in range(9):
        for j in range(9):
            if i != j and m[i][j] & 1:
                add(A0, i, 9 + j)
    for k in range(18):
        for i in DEF[k]:
            add(A0, 27 + k, i)
        for j in DEF[tau[k]]:
            add(A0, 27 + k, 9 + j)
        for l in range(18):
            if (H[k] >> l) & 1:
                add(A0, 27 + k, 27 + l)
    for q in range(9):
        for k in range(18):
            if (Az[q] >> k) & 1:
                add(A0, 18 + q, 27 + k)
        for r in range(9):
            if (G[q] >> r) & 1:
                add(A0, 18 + q, 18 + r)
    mem = [k for k in range(18) if (Az[0] >> k) & 1]
    outside = [k for k in range(18) if k not in mem]
    f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
    defi = [2 - x for x in f]
    pairs = [(i, j) for i in range(9) for j in range(i + 1, 9) if (i, j) in AS1 and (j, i) in AS1]
    typesols = [c for c in itertools.combinations(pairs, 3)
                if all(sum(1 for (a, b) in c if i in (a, b)) == defi[i] for i in range(9))]
    tested = passed_budget = passed_all = 0
    for sol in typesols:
        A1 = A0.copy()
        for c, (i, j) in enumerate(sol):
            w, sw = 45 + 2 * c, 46 + 2 * c
            add(A1, w, 18); add(A1, sw, 18); add(A1, w, sw)
            add(A1, w, i); add(A1, w, 9 + j); add(A1, sw, j); add(A1, sw, 9 + i)
        for p0 in itertools.combinations(outside, 2):
            if p0[1] == tau[p0[0]]:
                continue
            rem1 = [k for k in outside if k not in (p0[0], p0[1], tau[p0[0]], tau[p0[1]])]
            for p1 in itertools.combinations(rem1, 2):
                if p1[1] == tau[p1[0]]:
                    continue
                rem2 = [k for k in rem1 if k not in (p1[0], p1[1], tau[p1[0]], tau[p1[1]])]
                for p2 in itertools.combinations(rem2, 2):
                    if p2[1] == tau[p2[0]]:
                        continue
                    A = A1.copy()
                    for c, pr in enumerate((p0, p1, p2)):
                        w, sw = 45 + 2 * c, 46 + 2 * c
                        for s in pr:
                            add(A, w, 27 + s); add(A, sw, 27 + tau[s])
                    tested += 1
                    C2 = A @ A
                    np.fill_diagonal(C2, 0)
                    if (C2 > 2 - A).any():
                        continue
                    passed_budget += 1
                    n = 51
                    ok = True
                    for Mx in (27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2):
                        if np.linalg.eigvalsh(Mx.astype(float))[0] < -1e-7 and neg_certificate(Mx.tolist()) is not None:
                            ok = False; break
                    if ok:
                        passed_all += 1
    print(f"table F={F}: type candidates {len(typesols)}, full assignments built {tested}, "
          f"budget-valid {passed_budget}, also PSD-valid {passed_all}", flush=True)
