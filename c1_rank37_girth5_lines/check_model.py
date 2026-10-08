"""Numerical check of the algebra used for the balls with 7-torsion (cases 01u and 11 of gen66.py).
An explicit model of the 36-dimensional space V is built from the ball: spanning vectors p_w (w in N(T)), m, and (case
11) n, with Gram  [[M0, beta, 0], [beta^T, 0, 0], [0, 0, c0]];  its rank must be 36 and its kernel the true relations.
For random admissible shadows and random scalars, the vector p = sum c_w p_w + (alpha - c.beta) phi + s m + nu n is formed
and its products with the ball vectors and with another such vector are computed from the Gram matrix; they must be
3 + n(z) and  g(i,j) + alpha_i s_j + alpha_j s_i + c0 nu_i nu_j  (the formulas given to the solver)."""
import json, itertools, random
from star66 import kmatrix, candidates
from gen66 import make_ball_any, torsion_vectors, Solver, nullspace7

types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
rng = random.Random(11)


def rank7(M):
    return len(M[0]) - len(nullspace7(M))


def check(case, i1, i2, r, lam=2, c0=3, ntest=200):
    rho = list(itertools.permutations(range(3)))[r]
    adj, lay, comp = make_ball_any(key(types[i1]), key(types[i2]), rho)
    K = kmatrix(adj, lay)
    z0 = [1 if comp[v] == 0 else 6 for v in range(36)]
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    if case == "01u":
        phi = torsion_vectors(adj, comp, 1)[0]; Tv = [z0]; C0 = 0
    else:
        t1 = torsion_vectors(adj, comp, 0)[0]; t2 = torsion_vectors(adj, comp, 1)[0]
        phi = t1; Tv = [z0, [(a + lam * b) % 7 for a, b in zip(t1, t2)]]; C0 = c0
    # beta with beta.phi = 1, beta.T = 0
    rows = [phi] + Tv
    A = [row[:] + [int(i == 0)] for i, row in enumerate(rows)]; piv = []; rr = 0
    for c in range(36):
        p = next((i for i in range(rr, len(A)) if A[i][c] % 7), None)
        if p is None: continue
        A[rr], A[p] = A[p], A[rr]; iv = pow(A[rr][c], -1, 7); A[rr] = [(x * iv) % 7 for x in A[rr]]
        for i in range(len(A)):
            if i != rr and A[i][c] % 7:
                f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[rr])]
        piv.append(c); rr += 1
    beta = [0] * 36
    for i, c in enumerate(piv): beta[c] = A[i][36]
    dim = 38
    Gm = [[0] * dim for _ in range(dim)]
    for i in range(36):
        for j in range(36): Gm[i][j] = M0[i][j]
        Gm[i][36] = Gm[36][i] = beta[i]
    Gm[37][37] = C0 if C0 else 0
    rk = rank7(Gm)
    ker = nullspace7(Gm)
    # the kernel must be exactly the true relations (and the dummy coordinate n when there is no residue)
    expected = len(Tv) + (0 if C0 else 1)
    okrank = (rk == 36) and (len(ker) == expected)
    sol = Solver(M0)
    cands = [n for n in candidates(0, adj, lay, comp, K) if not any(sum(tv[z] for z in n) % 7 for tv in Tv)]
    bil = lambda x, y: sum(x[i] * Gm[i][j] * y[j] for i in range(dim) for j in range(dim) if x[i] and y[j]) % 7
    bad = 0
    def vec(n, al, nu):
        s = sum(phi[z] for z in n) % 7
        rhs = [(3 + (1 if z in n else 0) - s * beta[z]) % 7 for z in range(36)]
        c = sol.solve(rhs); cb = sum(a * b for a, b in zip(c, beta)) % 7
        x = [(c[w] + (al - cb) * phi[w]) % 7 for w in range(36)] + [s, nu if C0 else 0]
        return x, c, rhs, s
    for _ in range(ntest):
        n1, n2 = rng.choice(cands), rng.choice(cands)
        a1, a2, v1, v2 = (rng.randrange(7) for _ in range(4))
        x1, c1, rhs1, s1 = vec(n1, a1, v1); x2, c2, rhs2, s2 = vec(n2, a2, v2)
        for z in range(36):
            e = [0] * dim; e[z] = 1
            if bil(x1, e) != (3 + (1 if z in n1 else 0)) % 7: bad += 1
        lhs = bil(x1, x2)
        g = sum(a * b for a, b in zip(c1, rhs2)) % 7
        if lhs != (g + a1 * s2 + a2 * s1 + (C0 * v1 * v2 if C0 else 0)) % 7: bad += 1
        g11 = sum(a * b for a, b in zip(c1, rhs1)) % 7
        if bil(x1, x1) != (g11 + 2 * a1 * s1 + (C0 * v1 * v1 if C0 else 0)) % 7: bad += 1
    print(f"case {case} types ({i1},{i2}) rho={r}: Gram of the model has rank {rk}, kernel dimension {len(ker)} (expected {expected}): "
          f"{'ok' if okrank else 'PROBLEM'}; shadows after the balance filter {len(cands)}; formula mismatches in {ntest} random pairs: {bad}")


check("01u", 0, 2, 0); check("01u", 4, 3, 3); check("11", 2, 3, 1, lam=2, c0=3); check("11", 3, 3, 4, lam=5, c0=1)
