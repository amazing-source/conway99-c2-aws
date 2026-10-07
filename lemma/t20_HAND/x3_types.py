"""T20, case I (k = 0): the types (U ; V) of a vertex z of X_3 (three neighbours x_i, i in U, three neighbours y_j, j in V), for the
six graphs B. Written from lemma/T20_WORK.md only. Exact integer / rational arithmetic. Tiny: under a second, a few MB.

Graph rule (L) on S u {z, sigma z}:
  (a) |U n V| <= 1                     (z, sigma z are non-adjacent and share x_i, y_i for i in U n V; at most 2);
  (b) i in U: |B(i) n V| <= 1          (z ~ x_i: at most one common neighbour);   j in V: |B(j) n U| <= 1;
  (c) i not in U: |B(i) n V| <= 2      (z, x_i non-adjacent);                     j not in V: |B(j) n U| <= 2;
  (d) i, i' in U: |B(i) n B(i')| <= 1  (x_i, x_i' share z);                       same in V.
Then the Gram test: the odd Gram of the 10 support orbits and the orbit of z is [[3I + B, b], [b^T, 3]], b = 1_V - 1_U; it must be
positive semidefinite, i.e. rho = 3 - b^T (3I + B)^(-1) b >= 0 when 3I + B is invertible.
Printed per class under Aut(B) x (U <-> V): U, V, |U n V|, e_B(U), e_B(V), e_B(U,V), rho."""
import itertools as it, sys
from fractions import Fraction as F
E = {"I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79", "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
     "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89", "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
     "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79", "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89"}


def solve(M, b):
    n = len(M); A = [[F(x) for x in r] + [F(y)] for r, y in zip(M, b)]
    for c in range(n):
        p = next((r for r in range(c, n) if A[r][c] != 0), None)
        if p is None: return None
        A[c], A[p] = A[p], A[c]; A[c] = [x / A[c][c] for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0: A[r] = [x - A[r][c] * y for x, y in zip(A[r], A[c])]
    return [A[r][n] for r in range(n)]


for name, es in E.items():
    nb = [set() for _ in range(10)]
    for e in es.split(): a, b = int(e[0]), int(e[1]); nb[a].add(b); nb[b].add(a)
    assert all(len(s) == 4 for s in nb)
    auts = [p for p in it.permutations(range(10)) if all((p[j] in nb[p[i]]) == (j in nb[i]) for i in range(10) for j in range(i))]
    M = [[3 * (i == j) + (j in nb[i]) for j in range(10)] for i in range(10)]
    eB = lambda X, Y=None: sum(1 for i in X for j in (Y if Y is not None else X) if j in nb[i] and (Y is not None or i < j))
    seen = set(); rows = []
    for U in it.combinations(range(10), 3):
        if any(len(nb[i] & nb[j]) > 1 for i, j in it.combinations(U, 2)): continue
        for V in it.combinations(range(10), 3):
            if any(len(nb[i] & nb[j]) > 1 for i, j in it.combinations(V, 2)): continue
            Us, Vs = set(U), set(V)
            if len(Us & Vs) > 1: continue
            if any(len(nb[i] & Vs) > (1 if i in Us else 2) for i in range(10)): continue
            if any(len(nb[j] & Us) > (1 if j in Vs else 2) for j in range(10)): continue
            key = min(min((tuple(sorted(p[i] for i in X)), tuple(sorted(p[i] for i in Y))) for p in auts) for X, Y in ((U, V), (V, U)))
            if key in seen: continue
            seen.add(key)
            b = [(i in Vs) - (i in Us) for i in range(10)]; x = solve(M, b)
            rho = None if x is None else 3 - sum(bi * xi for bi, xi in zip(b, x))
            rows.append((U, V, len(Us & Vs), eB(U), eB(V), eB(U, V), rho))
    ok = [r for r in rows if r[6] is None or r[6] >= 0]
    print("%s: |Aut| %d, det(3I+B) %s; classes passing (L): %d; with rho >= 0: %d" % (name, len(auts), "0" if solve(M, [0] * 10) is None else "nonzero", len(rows), len(ok)))
    for U, V, c, eu, ev, euv, rho in ok:
        print("   U=%s V=%s |UnV|=%d e(U)=%d e(V)=%d e(U,V)=%d rho=%s" % ("".join(map(str, U)), "".join(map(str, V)), c, eu, ev, euv, rho))
