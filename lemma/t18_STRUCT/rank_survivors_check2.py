# Second route for rank_survivors.py: (a) exact integer determinant of the 23x23 sigma-odd part by fraction-free
# Bareiss elimination (pure Python integers), (b) float eigenvalues (numpy) as a sanity look, (c) rank modulo two primes.
# If det != 0 the 23 odd frame vectors would be independent in a 22-dimensional space: impossible.
import json, glob, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T18 = os.path.join(os.path.dirname(HERE), "t18")

def bareiss_det(M):
    M = [r[:] for r in M]; n = len(M); sign = 1; prev = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
            if sw is None: return 0
            M[k], M[sw] = M[sw], M[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[-1][-1]

def rank_mod(M, p):
    M = [[x % p for x in r] for r in M]; n = len(M); r = 0
    for c in range(n):
        piv = next((i for i in range(r, n) if M[i][c]), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], -1, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r

reps_tau = json.load(open(os.path.join(T18, "r2_tau_1.json")))["reps"]
seen = set()
for f in sorted(glob.glob(os.path.join(T18, "r3_p250_1_*_BC.json"))):
    for e in json.load(open(f)).get("survivors", []):
        key = tuple(e["rows"])
        if key in seen: continue
        seen.add(key)
        n = 47; rows = e["rows"]
        A = [[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)]
        tau = reps_tau[e["tau"]]
        sig = list(range(n))
        for i in range(9): sig[i] = i + 9; sig[i + 9] = i
        for k in range(18): sig[19 + k] = 19 + tau[k]
        for x in range(10): sig[37 + x] = 37 + (x ^ 1)
        reps = [v for v in range(n) if sig[v] > v]
        # odd Gram in frame normalisation: G = 3I - Ahat, Ahat_OO' = A_xy - A_x,sigma(y), Ahat_OO = -A_x,sigma(x)
        G = [[(3 if u == v else 0) - (A[u][v] - A[u][sig[v]]) for v in reps] for u in reps]
        assert all(G[i][j] == G[j][i] for i in range(23) for j in range(23))
        d = bareiss_det(G)
        w = np.linalg.eigvalsh(np.array(G, dtype=float))
        print("tau #%d F=%s: det(odd Gram 23x23) = %d ; smallest / largest eigenvalue (float) %.4f / %.4f ; rank mod 1000003: %d, mod 998244353: %d"
              % (e["tau"], e["F"], d, w[0], w[-1], rank_mod(G, 1000003), rank_mod(G, 998244353)))
