"""T20, case I: the "dual-norm test" on the support alone, for the six graphs B. Exact integer arithmetic; tiny (seconds, a few MB).

Fact used (proved earlier in the project): the dual L* of the frame lattice has no nonzero vector of squared norm < 10/7
(sum of squares of the orbit vector <= 7: AUDIT_NORME1; = 8: the 04/10 lemma; = 9: T18).
Let v in L* be the vector of phi (orbit vector c = 1 on the 10 support orbits, |v|^2 = 10/7), F_i the frame vector of orbit i
(representative x_i): (F_i, F_j) = 3 delta_ij + B_ij, (v, F_i) = 1. For integers k and m in Z^10, u = k v - sum m_i F_i is in L* and
    7 |u|^2 = 10 k^2 + 7 (m^T (3I + B) m - 2 k sum m_i)  =: N(k, m).
So N(k, m) must be 0 or >= 10. A pair (k, m) with 1 <= N <= 9 is an exact certificate that B is impossible.
k and 7 - k give the same cosets (7 v = sum F_i is in L), so k = 1, 2, 3 suffice.
Search: all m in {-1, 0, 1, 2}^10 (4^10 = 1,048,576 vectors per k), vectorised in int64. This is a search for certificates, not a
proof of absence: a graph with no certificate here is simply not excluded by this test on S."""
import itertools as it, numpy as np
E = {"I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79", "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
     "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89", "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
     "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79", "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89"}
vals = np.array([-1, 0, 1, 2], dtype=np.int64)
M = np.array(list(it.product(range(4), repeat=10)), dtype=np.int8); M = vals[M]          # (4^10, 10)
for name, es in E.items():
    B = np.zeros((10, 10), dtype=np.int64)
    for e in es.split(): a, b = int(e[0]), int(e[1]); B[a, b] = B[b, a] = 1
    G = 3 * np.eye(10, dtype=np.int64) + B
    quad = np.einsum("ij,jk,ik->i", M, G, M); s = M.sum(1)
    alpha = max(len(I) for r in range(1, 6) for I in it.combinations(range(10), r) if not any(B[i, j] for i, j in it.combinations(I, 2)))
    out = []
    for k in (1, 2, 3):
        N = 10 * k * k + 7 * (quad - 2 * k * s)
        assert N.min() >= 0, "positive semidefiniteness violated"
        bad = np.flatnonzero((N >= 1) & (N <= 9))
        out.append("k=%d: min N>0 is %d%s" % (k, N[N > 0].min(), "" if len(bad) == 0 else "  CERTIFICATE m=%s N=%d" % (M[bad[0]].tolist(), N[bad[0]])))
    print("%s: independence number %d | %s" % (name, alpha, " | ".join(out)))
