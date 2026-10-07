"""Bridge sanity check on REAL strongly regular graphs with lambda = 1, mu = 2 and an involution with exactly one fixed vertex.

  Paley(9)  = srg(9,4,1,2),    sigma: x -> -x on F_9      (c = r - s = 3,  r = 1,  s = -2)
  BvLS      = srg(243,22,1,2), sigma: x -> -x on F_3^5    (c = 9,          r = 4,  s = -5)
  (the 99-graph would be       srg(99,14,1,2)             (c = 7,          r = 3,  s = -4): no graph, formulas only)

For each graph the script builds, with exact integer / rational arithmetic only:
  1. the signed orbit matrix S (S_ij = A[x_i,x_j] - A[x_i,sigma x_j], S_ii = -A[x_i,sigma x_i]) for a RANDOM choice of orbit representatives,
     and H = r I - S (the Gram matrix of the "frame"); checks S^2 + S = (k-2) I, H^2 = c H, rank, norms, cell structure;
  2. an abstract integral lattice U' = <f_1..f_n> + Z y1 + Z y2 + Z g, where the f_i have Gram H, y1, y2 have norm c and are orthogonal
     to the f_i and to each other, and g is a glue vector with non-zero components on y1, y2 (so U' is not just L + Zy1 + Zy2);
  3. for random v in U':  a_i = (v, f_i)  (must be integers),  E(v) = c N(v) - (v,y1)^2 - (v,y2)^2,
     phi_v = lift of a to the vertices (a_i on x_i, -a_i on sigma x_i, 0 on the fixed vertex), and checks
         sum_i a_i^2 = E(v),   A phi_v = s phi_v at EVERY vertex (fixed vertex included),   sum_x phi_v(x)^2 = 2 E(v).
  4. negative controls: the even lift (a_i on both vertices of the orbit) and the complementary Gram S - s I.
No solver. Usage: python graph_check.py"""
import random, itertools, json, sys
from fractions import Fraction as F
import numpy as np

random.seed(20261007)
OUT = {}


def paley9():
    els = [(a, b) for a in range(3) for b in range(3)]                      # a + b i, i^2 = -1
    idx = {e: k for k, e in enumerate(els)}
    mul = lambda x, y: ((x[0] * y[0] - x[1] * y[1]) % 3, (x[0] * y[1] + x[1] * y[0]) % 3)
    sq = {mul(e, e) for e in els if e != (0, 0)}
    A = np.zeros((9, 9), dtype=np.int64)
    for x in els:
        for y in els:
            d = ((x[0] - y[0]) % 3, (x[1] - y[1]) % 3)
            if d in sq: A[idx[x], idx[y]] = 1
    sig = [idx[((-e[0]) % 3, (-e[1]) % 3)] for e in els]
    return A, sig


def bvls():
    Bm = [[1, 1, 1, 1, 1], [0, 1, 2, 2, 1], [1, 0, 1, 2, 2], [2, 1, 0, 1, 2], [2, 2, 1, 0, 1], [1, 2, 2, 1, 0]]   # ternary Golay code [I6 | B]
    cols = [tuple((-Bm[j][i]) % 3 for i in range(5)) for j in range(6)] + [tuple(int(i == j) for i in range(5)) for j in range(5)]  # H = [-B^T | I5]
    conn = set(cols) | {tuple((-x) % 3 for x in c) for c in cols}
    assert len(conn) == 22
    els = list(itertools.product(range(3), repeat=5)); idx = {e: k for k, e in enumerate(els)}
    A = np.zeros((243, 243), dtype=np.int64)
    for x in els:
        for d in conn:
            A[idx[x], idx[tuple((a + b) % 3 for a, b in zip(x, d))]] = 1
    sig = [idx[tuple((-a) % 3 for a in e)] for e in els]
    return A, sig


def kernel_mod(M, q):
    """basis (rows, entries in [0,q)) of {z : M z = 0 mod q}, q prime"""
    M = [[int(x) % q for x in row] for row in M]; n = len(M[0]); piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; inv = pow(M[r][c], -1, q); M[r] = [x * inv % q for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % q for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]; out = []
    for fc in free:
        z = [0] * n; z[fc] = 1
        for i, pc in enumerate(piv): z[pc] = (-M[i][fc]) % q
        out.append(z)
    return out


def run(name, A, sig, trials=300):
    res = {}; n = len(A); k = int(A[0].sum()); J = np.ones((n, n), dtype=np.int64); I = np.eye(n, dtype=np.int64)
    assert (A == A.T).all() and (A.diagonal() == 0).all() and (A.sum(axis=1) == k).all()
    assert np.array_equal(A @ A, (k - 2) * I - A + 2 * J), "not an srg(v,k,1,2)"
    c2 = 4 * k - 7; c = int(round(c2 ** 0.5)); assert c * c == c2; r, s = (c - 1) // 2, -(c + 1) // 2
    P = np.zeros((n, n), dtype=np.int64); P[np.arange(n), sig] = 1
    assert np.array_equal(P @ P, I) and np.array_equal(P @ A @ P.T, A), "sigma is not an involutive automorphism"
    fixed = [x for x in range(n) if sig[x] == x]; assert len(fixed) == 1; p = fixed[0]
    assert int(np.trace(P @ A)) == k                                     # the vertices adjacent to their mate are the k neighbours of p
    assert all((A[x, sig[x]] == 1) == (A[x, p] == 1) for x in range(n) if x != p)
    reps = []
    for x in range(n):
        if x < sig[x]: reps.append(x if random.random() < 0.5 else sig[x])     # random representative: exercises the sign freedom
    m = len(reps); R = np.array(reps); SR = np.array([sig[x] for x in reps])
    S = A[np.ix_(R, R)] - A[np.ix_(R, SR)]                                # diagonal: 0 - A[x, sigma x]
    assert np.array_equal(S, S.T) and all(S[i, i] == -A[reps[i], sig[reps[i]]] for i in range(m))
    Im = np.eye(m, dtype=np.int64)
    assert np.array_equal(S @ S + S, (k - 2) * Im)
    H = r * Im - S
    assert np.array_equal(H @ H, c * H)
    tr = int(np.trace(H)); assert tr % c == 0; rank = tr // c                 # H / c is a projector, so rank = trace / c exactly
    assert np.linalg.matrix_rank(H.astype(float)) == rank
    # multiplicities: f + g = n - 1, k + r f + s g = 0
    g_ = (k + r * (n - 1)) // (r - s); assert (k + r * (n - 1)) % (r - s) == 0; f_ = n - 1 - g_
    assert rank * 2 == g_, (rank, g_)                                     # sigma-odd part of V_s is exactly half of V_s
    inner = [i for i in range(m) if S[i, i] == -1]; outer = [i for i in range(m) if S[i, i] == 0]
    assert len(inner) == k // 2 and len(inner) + len(outer) == m
    assert all(H[i, i] == r + 1 for i in inner) and all(H[i, i] == r for i in outer)
    off = H - np.diag(np.diag(H)); assert set(np.unique(off).tolist()) <= {-1, 0, 1}
    assert not off[np.ix_(inner, inner)].any()                             # the h are pairwise orthogonal
    assert all(int(np.abs(off[np.ix_(inner, [u])]).sum()) == 2 for u in outer)   # every u meets exactly two h
    cells = {}
    for u in outer:
        cd = tuple(i for i in inner if off[i, u]); cells.setdefault(cd, []).append(int(off[cd[0], u] * off[cd[1], u]))
    assert len(cells) == len(inner) * (len(inner) - 1) // 2 and all(sorted(v) == [-1, 1] for v in cells.values())   # Same and Opp per pair
    res.update({"v": n, "k": k, "r": r, "s": s, "c": c, "orbits": m, "inner(norm r+1)": len(inner), "outer(norm r)": len(outer),
                "rank H": rank, "mult(s)": g_, "mult(r)": f_})
    # ---- abstract integral lattice U' = <f_i> + Z y1 + Z y2 + Z g
    q = 3 if c in (3, 9) else c
    Hl = [[int(x) for x in row] for row in H]
    ker = kernel_mod(Hl, q); glue = None
    random.shuffle(ker)
    for z in ker + [[(a + b) % q for a, b in zip(ker[i], ker[j])] for i in range(min(len(ker), 12)) for j in range(i)]:
        a1 = [sum(Hl[i][j] * z[j] for j in range(m)) for i in range(m)]
        assert all(x % q == 0 for x in a1); a1 = [x // q for x in a1]
        if not any(a1): continue
        n2 = sum(x * x for x in a1)                                       # = c * N(w), w = sum (z_i/q) f_i
        sol = [(al, be) for al in range(c) for be in range(c) if (al * al + be * be + n2) % c == 0 and (al or be)]
        if sol: glue = (z, a1, sol[0]); break
        if glue is None and n2 % c == 0: glue = (z, a1, (0, 0))             # fallback: a glue vector without normal component
    assert glue is not None, "no glue vector found"
    z, a1, (al0, be0) = glue
    Ng = F(sum(z[i] * Hl[i][j] * z[j] for i in range(m) for j in range(m)), q * q) + F(al0 * al0 + be0 * be0, c)
    assert Ng.denominator == 1                                            # U' is integral: (g,g), (g,f_j) = a1_j, (g,y) = al0, be0 are integers
    res["glue"] = {"N(g)": int(Ng), "(g,y1)": al0, "(g,y2)": be0, "sum (g,f_i)^2": sum(x * x for x in a1), "E(g) = c N(g) - Y(g)": c * int(Ng) - al0 * al0 - be0 * be0}
    A_l = [[int(x) for x in row] for row in A]
    nb = [[y for y in range(n) if A_l[x][y]] for x in range(n)]
    Es = {}; nonzero_checked = 0; even_fail = 0; nontriv = 0
    for t in range(trials):
        sup = random.sample(range(m), min(m, random.choice([1, 2, 3, 5, 8])))
        mm = [0] * m
        for i in sup: mm[i] = random.choice([-2, -1, 1, 2])
        n1, n2_, tg = random.choice([-1, 0, 0, 1]), random.choice([-1, 0, 0, 1]), random.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        if t % 7 == 0: mm = [0] * m                                       # pure glue + normals
        cv = [F(mm[i]) + F(tg * z[i], q) for i in range(m)]
        alpha = F(n1) + F(tg * al0, c); beta = F(n2_) + F(tg * be0, c)
        Hc = [sum(Hl[i][j] * cv[j] for j in range(m)) for i in range(m)]  # a_i = (v, f_i)
        assert all(x.denominator == 1 for x in Hc); a = [int(x) for x in Hc]
        Nv = sum(cv[i] * Hc[i] for i in range(m)) + c * (alpha * alpha + beta * beta)
        vy1, vy2 = c * alpha, c * beta
        assert Nv.denominator == 1 and vy1.denominator == 1 and vy2.denominator == 1
        E = c * int(Nv) - int(vy1) ** 2 - int(vy2) ** 2
        assert sum(x * x for x in a) == E, ("sum a^2 != E", sum(x * x for x in a), E)
        phi = [0] * n
        for i, x in enumerate(reps): phi[x] = a[i]; phi[sig[x]] = -a[i]
        assert phi[p] == 0
        assert all(sum(phi[y] for y in nb[x]) == s * phi[x] for x in range(n)), "A phi != s phi"
        assert sum(x * x for x in phi) == 2 * E
        Es[E] = Es.get(E, 0) + 1; nonzero_checked += E > 0; nontriv += (tg % q != 0)
        if E > 0:                                                         # negative control: the EVEN lift is not an eigenfunction for s
            ev = [0] * n
            for i, x in enumerate(reps): ev[x] = a[i]; ev[sig[x]] = a[i]
            even_fail += not all(sum(ev[y] for y in nb[x]) == s * ev[x] for x in range(n))
    res["random vectors"] = {"trials": trials, "with E > 0": nonzero_checked, "with a glue component not in L+Zy1+Zy2": nontriv,
                             "distinct E values": len(Es), "min positive E": min(e for e in Es if e > 0),
                             "identities sum a^2 = E, A phi = s phi (all vertices), sum phi^2 = 2E": "all hold",
                             "even lift fails to be an s-eigenfunction": "%d of %d" % (even_fail, nonzero_checked)}
    # negative control 2: the complementary Gram S - s I (eigenvalue r) has the OTHER norm pattern
    H2 = S - s * Im; assert np.array_equal(H2 @ H2, c * H2)
    res["complementary Gram S - sI"] = {"rank": int(np.trace(H2)) // c, "norm on inner": int(H2[inner[0], inner[0]]), "norm on outer": int(H2[outer[0], outer[0]])}
    res["frame Gram rI - S"] = {"rank": rank, "norm on inner": r + 1, "norm on outer": r}
    # smallest non-zero integer vectors of the s-eigenspace of S found among the rows of H (= products of f_i with the frame)
    res["min |a|^2 over rows of H (a = (f_i, f_j)_j)"] = int(min((H[i] ** 2).sum() for i in range(m)))
    OUT[name] = res
    print(name, json.dumps(res, indent=1), flush=True)


run("Paley(9)", *paley9(), trials=300)
run("BvLS(243)", *bvls(), trials=300)
k = 14; c = 7; r = 3; s = -4; n = 99
OUT["99 (formulas only, no graph)"] = {"orbits": 49, "inner(norm 4)": 7, "outer(norm 3)": 42, "trace(3I - S) = 3*49 + 7": 154, "rank = trace/7": 22,
                                      "mult(-4)": (k + r * (n - 1)) // (r - s), "E(v) = 7 N(v) - Y(v) = sum a_i^2, sum phi^2 = 2 E(v)": "root, Y=5 -> 18; root, Y=4 -> 20; norm 3, Y=13 -> 16"}
print(json.dumps(OUT["99 (formulas only, no graph)"], indent=1))
json.dump(OUT, open(__file__.replace(".py", ".out.json"), "w"), indent=1)
print("ALL CHECKS PASSED")
