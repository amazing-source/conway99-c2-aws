# Round 4.  INDEPENDENT check of stage D (X_0 stage).  No import from the other scripts; exact rational arithmetic.
#
# Principle (a hand argument plus exact linear algebra, no eigenvalue computation):
#   Let Y47 = S u {p} u X_2 u W be a stage-C survivor and M = 9(3I-A)+J on Y47.  M is positive semidefinite and singular
#   (checked exactly here): there is u != 0 with M u = 0.  If z is any further vertex of the graph, the matrix on
#   Y47 u {z} must be positive semidefinite; a PSD matrix that vanishes on a vector as a quadratic form kills it, so the
#   row of z must be orthogonal to (u, 0):
#               sum_v (1 - 9 A_zv) u_v = 0,   i.e.   9 * sum_{v ~ z} u_v = sum_v u_v.            (K)
#   For z in X_0 \ {p} the neighbours of z in Y47 are a set Z of vertices of X_2 u W.
# The script (1) recomputes the kernel of M exactly and checks M u = 0 and M >= 0 by rational elimination;
# (2) enumerates, with its own generator (decreasing order, budgets recounted by matrix products on the 48 vertices
# after every addition), all sets Z allowed by the forced numbers (a_2(z) >= 4, |Z n A_p| + |Z n W| = 2, no neighbour w
# of W with a_2(w) = 2, no vertex whose requirement is 0, common-neighbour budgets);  (3) counts those satisfying (K).
# If none satisfies (K), no vertex of X_0 \ {p} can exist: contradiction with |X_0| = 9.
# usage: python r4_verifyD.py <structure> <survivor json files ...>
import json, os, sys
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
s_idx = int(sys.argv[1])
reps = json.load(open(os.path.join(HERE, f"r2_tau_{s_idx}.json")))["reps"]


def exact_kernel_and_psd(M):
    """M integer symmetric (list of lists).  Returns (is_psd, rank, kernel basis as integer vectors)."""
    n = len(M)
    A = [[Fraction(int(x)) for x in r] for r in M]
    # PSD test by symmetric elimination
    W = [row[:] for row in A]
    rows = list(range(n)); rank = 0; psd = True
    while rows and psd:
        piv = None
        for i in rows:
            if W[i][i] < 0:
                psd = False; break
            if W[i][i] > 0 and piv is None:
                piv = i
        if not psd:
            break
        if piv is None:
            psd = all(W[i][j] == 0 for i in rows for j in rows)
            break
        rank += 1
        rows.remove(piv)
        pv = W[piv][piv]
        for i in rows:
            f = W[i][piv] / pv
            if f:
                Wi = W[i]; Wp = W[piv]
                for j in rows:
                    Wi[j] -= f * Wp[j]
    # kernel by row reduction
    R = [row[:] for row in A]
    pivcols = []; r = 0
    for c in range(n):
        pr = None
        for i in range(r, n):
            if R[i][c] != 0:
                pr = i; break
        if pr is None:
            continue
        R[r], R[pr] = R[pr], R[r]
        pv = R[r][c]
        R[r] = [x / pv for x in R[r]]
        for i in range(n):
            if i != r and R[i][c] != 0:
                f = R[i][c]
                R[i] = [a - f * b for a, b in zip(R[i], R[r])]
        pivcols.append(c); r += 1
    free = [c for c in range(n) if c not in pivcols]
    basis = []
    for fc in free:
        v = [Fraction(0)] * n
        v[fc] = Fraction(1)
        for i, pc_ in enumerate(pivcols):
            v[pc_] = -R[i][fc]
        den = 1
        for x in v:
            den = den * x.denominator // np.gcd(den, x.denominator)
        vi = [int(x * den) for x in v]
        basis.append(vi)
    return psd, rank, basis


def violation(G):
    """True iff an integer vector x with x^T M x < 0 is found for M = 9(3I-A)+J or 11(4I+A)-2J (exact, Python ints)"""
    n = G.shape[0]
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * G + 1, 44 * I + 11 * G - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -1e-7:
            Ml = M.tolist()
            for sc in (10, 60, 500, 10 ** 4, 10 ** 6):
                x = [int(round(sc * float(c))) for c in V[:, 0]]
                if sum(x[a] * sum(Ml[a][b] * x[b] for b in range(n)) for a in range(n)) < 0:
                    return True
            AMB[0] += 1
    return False


AMB = [0]
seen = set()
total_K = 0
total_pass49 = 0
for fn in sys.argv[2:]:
    d = json.load(open(os.path.join(HERE, fn)))
    for e in d["survivors"]:
        key = tuple(e["rows"])
        if key in seen:
            continue
        seen.add(key)
        rows = e["rows"]
        A = np.array([[(rows[a] >> b) & 1 for b in range(47)] for a in range(47)], dtype=np.int64)
        assert (A == A.T).all() and not A.diagonal().any()
        tau = reps[e["tau"]]
        mem = sorted(k for o in e["F"] for k in (o, tau[o]))
        M = (27 * np.eye(47, dtype=np.int64) - 9 * A + 1)
        psd, rank, basis = exact_kernel_and_psd(M.tolist())
        assert psd and len(basis) == 47 - rank
        for u in basis:
            assert all(sum(int(M[i, j]) * u[j] for j in range(47)) == 0 for i in range(47))
        a2 = [int(A[19 + q, 19:37].sum()) for q in range(28)]
        t = sum(a2[:18]) // 2
        need = [a2[q] + 2 - (1 if q in mem else 0) if q < 18 else a2[q] - 2 for q in range(28)]
        sig = [tau[q] if q < 18 else 18 + ((q - 18) ^ 1) for q in range(28)]
        special = [q >= 18 or q in mem for q in range(28)]
        # own generator: items in DECREASING order, budget of the 48-vertex graph recounted after each addition
        cnt = {"sets": 0, "sets_mate_ok": 0, "K": 0, "pass48": 0, "budget49": 0, "pass49": 0}
        Ksets = []
        def budgets48(Z):
            G = np.zeros((48, 48), dtype=np.int64)
            G[:47, :47] = A
            for q in Z:
                G[47, 19 + q] = G[19 + q, 47] = 1
            C = G @ G
            np.fill_diagonal(C, 0)
            return not (C > 2 - G).any()
        def rec(top, Z, nx2, nsp):
            if nx2 >= 4 and nsp == 2:
                cnt["sets"] += 1
                sZ = sorted(sig[q] for q in Z)
                use = [Z.count(q) + sZ.count(q) for q in range(28)]
                if all(use[q] <= need[q] for q in range(28)) and len(set(Z) & set(sZ)) <= 2 and budgets48(sZ):
                    cnt["sets_mate_ok"] += 1
                    G = np.zeros((49, 49), dtype=np.int64)
                    G[:47, :47] = A
                    for q in Z:
                        G[47, 19 + q] = G[19 + q, 47] = 1
                    for q in sZ:
                        G[48, 19 + q] = G[19 + q, 48] = 1
                    if not violation(G[:48, :48]):
                        cnt["pass48"] += 1
                    C49 = G @ G
                    np.fill_diagonal(C49, 0)
                    if not (C49 > 2 - G).any():
                        cnt["budget49"] += 1
                        if not violation(G):
                            cnt["pass49"] += 1
                    # condition (K) for every kernel vector
                    if all(9 * sum(u[19 + q] for q in Z) == sum(u) for u in basis):
                        cnt["K"] += 1
                        Ksets.append(sorted(Z))
            for q in range(top - 1, -1, -1):
                if need[q] < 1:
                    continue
                if special[q] and nsp >= 2:
                    continue
                if q < 18 and nx2 >= 4 + t:
                    continue
                Z2 = Z + [q]
                if budgets48(Z2):
                    rec(q, Z2, nx2 + (1 if q < 18 else 0), nsp + (1 if special[q] else 0))
        rec(28, [], 0, 0)
        total_K += cnt["K"]
        total_pass49 += cnt["pass49"]
        print(f"survivor matching #{e['tau']}, F = {e['F']}: M = 9(3I-A)+J on 47 vertices exactly PSD: {psd}, rank {rank}, "
              f"kernel dimension {len(basis)}")
        for u in basis:
            print(f"   kernel vector (integers): on S+ {u[:9]}, on S- {u[9:18]}, at p {u[18]}, on X_2 {u[19:37]}, on W {u[37:47]}; sum = {sum(u)}")
        print(f"   admissible neighbour sets Z of a vertex of X_0 \\ {{p}} (budgets on 48 vertices): {cnt['sets']}; "
              f"with an admissible mate: {cnt['sets_mate_ok']}; satisfying the kernel condition (K): {cnt['K']}")
        print(f"   of these {cnt['sets_mate_ok']}: no PSD violation found on Y47 u {{z}} (48 vertices): {cnt['pass48']}; "
              f"budgets hold on Y47 u {{z, sigma z}}: {cnt['budget49']}; no PSD violation on these 49 vertices: {cnt['pass49']}")
print(f"survivors examined: {len(seen)}; sets Z satisfying (K) in total: {total_K}; "
      f"candidates (z, sigma z) with no violation on 49 vertices: {total_pass49}; ambiguous float cases: {AMB[0]}")
