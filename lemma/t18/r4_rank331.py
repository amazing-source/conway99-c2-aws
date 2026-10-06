# Round 4.  The rank test applied to profile (3,3,1) (B1), on the Y-tables of round 2.
# Y = S u X_0 u X_2 (45 vertices) has 22 non-fixed orbits: the odd bound (rank <= 22) says nothing on Y.
# Y u {w, sigma w} for ONE mate pair of W = N(p) n X_1 has 23 orbits and is completely determined (A10: w = (i ; j),
# w ~ p, w ~ sigma w, exactly 2 neighbours in X_2, both outside A_p, no neighbour in X_0 except p), so
#       G_odd (23 x 23) must be SINGULAR and PSD;   the even matrix (24 x 24, with p) must have rank <= 22.
# For each saved table and each (type, pair of X_2-neighbours) allowed by the budgets on these 47 vertices we compute
# exactly det G_odd (fraction-free Bareiss) and, when it vanishes, the exact even rank; and, for comparison, the PSD
# verdict used in round 2 (integer certificate).  A table is "dead by the rank test at the first pair" when no type
# solution has, for each of its 3 types, at least one candidate passing the rank conditions.
# Numbering as in r2_ext2.py: support 0..17, X_0 18..26 (p = 18), X_2 27..44, w = 45, sigma w = 46.
# usage: python r4_rank331.py <max number of tables> <time limit s> <json files of r2_stage2.py ...>
import json, os, sys, itertools, time
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()
maxtab = int(sys.argv[1]); tl = float(sys.argv[2])
B = np.zeros((9, 9), dtype=np.int64)
for e in "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78".split():
    B[int(e[0]), int(e[1])] = B[int(e[1]), int(e[0])] = 1
C2 = B @ B
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if C2[a, b] == 1]


def det_bareiss(M):
    A = [[int(x) for x in r] for r in M]
    n = len(A); sign = 1; prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            sw = None
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    sw = i; break
            if sw is None:
                return 0
            A[k], A[sw] = A[sw], A[k]; sign = -sign
        Ak = A[k]; akk = Ak[k]
        for i in range(k + 1, n):
            Ai = A[i]; aik = Ai[k]
            for j in range(k + 1, n):
                Ai[j] = (Ai[j] * akk - aik * Ak[j]) // prev
        prev = akk
    return sign * A[n - 1][n - 1]


def rank_exact(M):
    A = [[Fraction(int(x)) for x in r] for r in M]
    n = len(A); r = 0
    for c in range(n):
        pr = None
        for i in range(r, n):
            if A[i][c] != 0:
                pr = i; break
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        for i in range(r + 1, n):
            if A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def psd_violation(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * A + 1, 44 * I + 11 * A - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -1e-7:
            for sc in (8, 30, 100, 1000, 10 ** 5):
                x = np.rint(sc * V[:, 0]).astype(np.int64)
                if int(x @ (M @ x)) < 0:
                    return True
    return False


tables = []
for fn in sys.argv[3:]:
    d = json.load(open(os.path.join(HERE, fn)))
    for ex in d.get("examples", []):
        tables.append(("PSD-passing on Y", ex))
    for ex in d.get("rejected_examples", []):
        tables.append(("PSD-rejected on Y", ex))
TOT = {}
done = 0
for label, ex in tables[:maxtab]:
    if time.time() - T0 > tl:
        break
    tau, Az, H, G, F = ex["tau"], ex["Az"], ex["H"], ex["G"], ex["F"]
    A = np.zeros((47, 47), dtype=np.int64)
    A[:9, 9:18] = B; A[9:18, :9] = B
    for k in range(18):
        for i in DEF[k]:
            A[27 + k, i] = A[i, 27 + k] = 1
        for j in DEF[tau[k]]:
            A[27 + k, 9 + j] = A[9 + j, 27 + k] = 1
        for l in range(18):
            if (H[k] >> l) & 1:
                A[27 + k, 27 + l] = 1
    for q in range(9):
        for k in range(18):
            if (Az[q] >> k) & 1:
                A[18 + q, 27 + k] = A[27 + k, 18 + q] = 1
        for r in range(9):
            if (G[q] >> r) & 1:
                A[18 + q, 18 + r] = 1
    # sigma on the 47 vertices: X_0: p fixed, 19<->20, 21<->22, 23<->24, 25<->26
    sig = list(range(9, 18)) + list(range(9)) + [18, 20, 19, 22, 21, 24, 23, 26, 25] + [27 + tau[k] for k in range(18)] + [46, 45]
    Y = list(range(45))
    assert all(A[u, v] == A[sig[u], sig[v]] for u in Y for v in Y), "Y-table not sigma-invariant"
    mem = [k for k in range(18) if (Az[0] >> k) & 1]
    outside = [k for k in range(18) if k not in mem]
    f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
    defi = [2 - x for x in f]
    pairs = [(i, j) for i in range(9) for j in range(i + 1, 9)]
    tsols = [c for c in itertools.combinations(pairs, 3)
             if all(sum(1 for (a, b) in c if i in (a, b)) == defi[i] for i in range(9))]
    types = sorted(set(p for c in tsols for p in c))
    R = [v for v in range(47) if v < sig[v]]
    res = {}
    cnt = {"cand": 0, "budget_ok": 0, "odd_singular": 0, "rank_ok": 0, "psd_ok": 0, "rank_ok_and_psd_ok": 0}
    for (i, j) in types:
        ok_rank = ok_psd = 0
        for s1, s2 in itertools.combinations(outside, 2):
            if s2 == tau[s1]:
                continue
            for a_, b_ in ((s1, s2), (tau[s1], s2)):          # w sees one vertex of each of the two orbits: 2 inequivalent choices
                cnt["cand"] += 1
                A2 = A.copy()
                for u, v in ((45, 18), (46, 18), (45, 46), (45, i), (45, 9 + j), (46, j), (46, 9 + i),
                             (45, 27 + a_), (45, 27 + b_), (46, 27 + tau[a_]), (46, 27 + tau[b_])):
                    A2[u, v] = A2[v, u] = 1
                Cn = A2 @ A2
                np.fill_diagonal(Cn, 0)
                if (Cn > 2 - A2).any():
                    continue
                cnt["budget_ok"] += 1
                Godd = [[(3 if x == y else 0) - int(A2[R[x], R[y]]) + int(A2[R[x], sig[R[y]]]) for y in range(23)] for x in range(23)]
                rank_ok = False
                if det_bareiss(Godd) == 0:
                    cnt["odd_singular"] += 1
                    Nev = [[0] * 24 for _ in range(24)]
                    Nev[0][0] = 28
                    for x in range(23):
                        Nev[0][x + 1] = Nev[x + 1][0] = 2 - 18 * int(A2[18, R[x]])
                        for y in range(23):
                            Nev[x + 1][y + 1] = (4 + 18 * (3 - int(A2[R[x], sig[R[x]]]))) if x == y else \
                                (4 - 18 * (int(A2[R[x], R[y]]) + int(A2[R[x], sig[R[y]]])))
                    if rank_exact(Godd) <= 22 and rank_exact(Nev) <= 22:
                        rank_ok = True
                p_ok = not psd_violation(A2)
                cnt["rank_ok"] += rank_ok; cnt["psd_ok"] += p_ok; cnt["rank_ok_and_psd_ok"] += (rank_ok and p_ok)
                ok_rank += rank_ok; ok_psd += p_ok
        res[(i, j)] = (ok_rank, ok_psd)
    alive_rank = any(all(res[p][0] > 0 for p in c) for c in tsols)
    alive_psd = any(all(res[p][1] > 0 for p in c) for c in tsols)
    done += 1
    key = label
    t = TOT.setdefault(key, {"tables": 0, "dead_by_rank_at_first_pair": 0, "dead_by_psd_at_first_pair": 0, "cand": 0,
                             "budget_ok": 0, "odd_singular": 0, "rank_ok": 0, "psd_ok": 0, "rank_ok_and_psd_ok": 0})
    t["tables"] += 1
    t["dead_by_rank_at_first_pair"] += (not alive_rank)
    t["dead_by_psd_at_first_pair"] += (not alive_psd)
    for k in cnt:
        t[k] += cnt[k]
    print(f"table {done} [{label}] F={F}: type solutions {len(tsols)}, {cnt}, "
          f"alive after rank test: {alive_rank}, alive after PSD test: {alive_psd}   [{time.time() - T0:.0f}s]", flush=True)
print(f"tables examined: {done} of {len(tables)} saved")
for k, v in TOT.items():
    print(f"   {k}: {v}")
