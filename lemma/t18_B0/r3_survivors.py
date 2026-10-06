# Round 3.  Independent examination of the configurations left by r3_p250.py on S u {p} u X_2 u W (47 vertices).
# No import from the enumerators.  For each saved survivor: rebuild the graph from the saved rows, check that it is the
# claimed structure (support graph of B1, X_2 types given by the matching, p ~ A_p u W, types of W, sigma-invariance),
# recount the common-neighbour budgets by integer matrix products, and decide positive semidefiniteness of
# 9(3I-A)+J and 11(4I+A)-2J EXACTLY (rational elimination).  A survivor that passes all this is a genuine open case.
# usage: python r3_survivors.py <structure> <json files ...>
import json, os, sys
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
s = int(sys.argv[1])
B = np.zeros((9, 9), dtype=np.int64)
for e in EDGES[s].split():
    B[int(e[0]), int(e[1])] = B[int(e[1]), int(e[0])] = 1
C = B @ B
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if C[a, b] == 1]
td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
assert [tuple(d) for d in td["DEF"]] == DEF
reps = td["reps"]


def is_psd_exact(M):
    n = len(M)
    A = [[Fraction(int(x)) for x in r] for r in M]
    rows = list(range(n))
    rank = 0
    while rows:
        piv = None
        for i in rows:
            if A[i][i] < 0:
                return False, None
            if A[i][i] > 0 and piv is None:
                piv = i
        if piv is None:
            return all(A[i][j] == 0 for i in rows for j in rows), rank
        rank += 1
        rows.remove(piv)
        p = A[piv][piv]
        for i in rows:
            f = A[i][piv] / p
            if f:
                Ai = A[i]; Ap = A[piv]
                for j in rows:
                    Ai[j] -= f * Ap[j]
    return True, rank


seen = set()
for fn in sys.argv[2:]:
    d = json.load(open(os.path.join(HERE, fn)))
    for e in d["survivors"]:
        rows = e["rows"]
        key = tuple(rows)
        if key in seen:
            continue
        seen.add(key)
        n = 47
        A = np.array([[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)], dtype=np.int64)
        tau = reps[e["tau"]]
        F = e["F"]
        mem = sorted(k for o in F for k in (o, tau[o]))
        checks = {}
        checks["symmetric, zero diagonal"] = bool((A == A.T).all() and not A.diagonal().any())
        sup = np.zeros((18, 18), dtype=np.int64)
        sup[:9, 9:] = B; sup[9:, :9] = B
        checks["support graph"] = bool((A[:18, :18] == sup).all())
        okx = True
        for k in range(18):
            exp = [0] * 18
            for i in DEF[k]:
                exp[i] = 1
            for j in DEF[tau[k]]:
                exp[9 + j] = 1
            okx = okx and list(A[19 + k, :18]) == exp
        checks["X_2 types = matching"] = okx
        checks["N(p) = A_p u W"] = [v for v in range(n) if A[18, v]] == [19 + k for k in mem] + list(range(37, 47))
        okw = True
        for c, (i, j) in enumerate(e["types"]):
            w, sw = 37 + 2 * c, 38 + 2 * c
            okw = okw and [v for v in range(18) if A[w, v]] == sorted([i, 9 + j]) and [v for v in range(18) if A[sw, v]] == sorted([j, 9 + i])
            okw = okw and A[w, sw] == 1
        checks["W types and mate edges"] = bool(okw)
        sig = list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)] + [38 + 2 * (c // 2) - (c % 2) if False else (37 + (c ^ 1)) for c in range(10)]
        P = np.zeros((n, n), dtype=np.int64)
        for v in range(n):
            P[v, sig[v]] = 1
        checks["sigma-invariant"] = bool((P.T @ A @ P == A).all())
        C2 = A @ A
        np.fill_diagonal(C2, 0)
        checks["budgets"] = not bool((C2 > 2 - A).any())
        I = np.eye(n, dtype=np.int64)
        r1 = is_psd_exact((27 * I - 9 * A + 1).tolist())
        r2 = is_psd_exact((44 * I + 11 * A - 2).tolist())
        checks["9(3I-A)+J exactly PSD (rank)"] = r1
        checks["11(4I+A)-2J exactly PSD (rank)"] = r2
        a2 = [int(A[v, 19:37].sum()) for v in range(n)]
        t = sum(a2[19:37]) // 2
        req_ok = all(int(A[19 + k, [19 + q for q in mem]].sum()) + int(A[19 + k, 37:47].sum()) == 2 for k in range(18) if k not in mem)
        checks["every s outside A_p has 2 neighbours in N(p)"] = bool(req_ok)
        print(f"survivor: matching #{e['tau']}, F = {F} (A_p = X_2 vertices {mem}), W types {e['types']}")
        print(f"   t = e(X_2) = {t}; a_2 on A_p: {[a2[19 + k] for k in mem]}; a_2 on W: {a2[37:47]}; a_2 on X_2: {a2[19:37]}")
        for k, v in checks.items():
            print(f"   {k}: {v}")
print("distinct survivors examined:", len(seen))
