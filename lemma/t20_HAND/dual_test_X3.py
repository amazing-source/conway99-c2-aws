"""T20, case I: the dual-norm test on S plus one orbit of X_3, for every type (U ; V) kept by x3_types.py.
Same fact and same formula as dual_test_S.py, with 11 orbits: Gram [[3I + B, b], [b^T, 3]], b = 1_V - 1_U (the orbit of z, represented
by z), orbit vector c = (1,...,1, 0). N(k, m) = 10 k^2 + 7 (m^T Gram m - 2 k sum_{i < 10} m_i) must be 0 or >= 10.
Search: m in {-1,0,1,2}^10 x {-2,...,2}; exact int64. A certificate (1 <= N <= 9) excludes the type. Tiny: about a minute, < 1 GB."""
import itertools as it, numpy as np
E = {"I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79", "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
     "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89", "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
     "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79", "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89"}
TYPES = {"I.0": ["034 179"], "I.1": ["034 178", "034 258", "034 278", "257 268", "257 368", "257 678", "258 345", "278 349", "368 457"],
         "I.2": ["034 189", "034 589", "345 389"], "I.3": ["034 156", "034 159", "159 168", "159 368"],
         "I.4": ["025 279", "027 035", "035 169", "035 279", "279 348"], "I.5": ["012 168", "012 579", "016 359"]}
vals = np.array([-1, 0, 1, 2], dtype=np.int64)
M = vals[np.array(list(it.product(range(4), repeat=10)), dtype=np.int8)]
s = M.sum(1)
for name, es in E.items():
    B = np.zeros((10, 10), dtype=np.int64)
    for e in es.split(): a, b = int(e[0]), int(e[1]); B[a, b] = B[b, a] = 1
    G = 3 * np.eye(10, dtype=np.int64) + B
    quad = np.einsum("ij,jk,ik->i", M, G, M)
    for ty in TYPES[name]:
        U, V = [[int(ch) for ch in part] for part in ty.split()]
        bz = np.zeros(10, dtype=np.int64)
        for i in V: bz[i] += 1
        for i in U: bz[i] -= 1
        lin = M @ bz; found = None; best = {}
        for k in (1, 2, 3):
            for mz in range(-2, 3):
                N = 10 * k * k + 7 * (quad + 2 * mz * lin + 3 * mz * mz - 2 * k * s)
                assert N.min() >= 0, "positive semidefiniteness violated: %s %s" % (name, ty)
                pos = N[N > 0]; best[k] = min(best.get(k, 10 ** 9), int(pos.min()))
                bad = np.flatnonzero((N >= 1) & (N <= 9))
                if len(bad) and found is None: found = (k, M[bad[0]].tolist(), mz, int(N[bad[0]]))
        print("%s  U=%s V=%s  smallest N > 0 for k=1,2,3: %s  %s" % (name, ty.split()[0], ty.split()[1], [best[k] for k in (1, 2, 3)],
              "no certificate" if found is None else "EXCLUDED: k=%d m=%s m_z=%d N=%d" % found), flush=True)
