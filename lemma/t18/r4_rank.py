# Round 4.  Rank test on the 4 stage-C survivors of B1 (own check of the structural agent's computation).
# 63 E_{-4} = 27I - 9A + J has rank 44 and sigma splits the (-4)-eigenspace 22 + 22, so for a sigma-invariant vertex set:
#   odd part : G_odd = 3I - A[R,R] + A[R, sigma R]  (R = one vertex per non-fixed orbit) has rank <= 22;
#   even part: the Gram matrix of e_p and the e_v + e_{sigma v}, times 9:
#              N[O,O'] = 4 - 18 (A[v,v'] + A[v, sigma v']),  N[O,O] = 4 + 18 (3 - A[v, sigma v]),
#              N[p,O] = 2 - 18 A[p,v],  N[p,p] = 28,   has rank <= 22.
# Exact arithmetic only: rank by rational elimination (Fractions), determinant by fraction-free Bareiss (Python ints).
# No import from other scripts.   usage: python r4_rank.py <structure> <survivor json files of r3_p250.py ...>
import json, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
s_idx = int(sys.argv[1])
reps = json.load(open(os.path.join(HERE, f"r2_tau_{s_idx}.json")))["reps"]


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
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


seen = set()
for fn in sys.argv[2:]:
    for e in json.load(open(os.path.join(HERE, fn)))["survivors"]:
        if tuple(e["rows"]) in seen:
            continue
        seen.add(tuple(e["rows"]))
        rows = e["rows"]; n = len(rows)
        A = [[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)]
        tau = reps[e["tau"]]
        sig = list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)] + [37 + (x ^ 1) for x in range(10)]
        assert all(A[u][v] == A[sig[u]][sig[v]] for u in range(n) for v in range(n)), "not sigma-invariant"
        R = [v for v in range(n) if v < sig[v]]
        m = len(R)
        Godd = [[(3 if a == b else 0) - A[R[a]][R[b]] + A[R[a]][sig[R[b]]] for b in range(m)] for a in range(m)]
        Nev = [[0] * (m + 1) for _ in range(m + 1)]
        Nev[0][0] = 28
        for a in range(m):
            Nev[0][a + 1] = Nev[a + 1][0] = 2 - 18 * A[18][R[a]]
            for b in range(m):
                if a == b:
                    Nev[a + 1][b + 1] = 4 + 18 * (3 - A[R[a]][sig[R[a]]])
                else:
                    Nev[a + 1][b + 1] = 4 - 18 * (A[R[a]][R[b]] + A[R[a]][sig[R[b]]])
        ro, do = rank_exact(Godd), det_bareiss(Godd)
        re_ = rank_exact(Nev)
        print(f"survivor matching #{e['tau']}, F = {e['F']}: {n} vertices, {m} non-fixed orbits")
        print(f"   odd part : {m} x {m}, exact rank {ro} (bound 22), determinant {do}  ->  "
              f"{'VIOLATION (rank > 22)' if ro > 22 else 'no violation'}")
        print(f"   even part: {m + 1} x {m + 1}, exact rank {re_} (bound 22)  ->  "
              f"{'VIOLATION (rank > 22)' if re_ > 22 else 'no violation'}")
print("survivors examined:", len(seen))
