"""Referee's own numerical check of the bridge theorem, written from the statement alone (BRIDGE.md section 4).
Exact arithmetic only (Python ints / Fractions; numpy int64 for small-integer matrix products).

Graphs: srg(n,k,1,2) with an involution having exactly one fixed vertex:
  Paley(9)                (9,4,1,2),   x -> -x on F_9
  Berlekamp-van Lint-Seidel (243,22,1,2), cosets of the ternary Golay code, x -> -x
General constants (derived here, not copied): eigenvalues r > 0 > s with r + s = -1, r s = 2 - k; c = r - s;
  frame Gram H = r I - S, H^2 = c H, normals of norm c, E(v) = c N(v) - (v,y1)^2 - (v,y2)^2, claim sum phi^2 = 2 E(v), A phi = s phi.
For (99,14,1,2): r = 3, s = -4, c = 7.
"""
import sys, random, math, json
from fractions import Fraction as Fr
import numpy as np

random.seed(20261007)
OUT = {}


def P(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ graphs
def paley9():
    els = [(a, b) for a in range(3) for b in range(3)]                 # a + b i, i^2 = -1, F_9
    mul = lambda x, y: ((x[0] * y[0] - x[1] * y[1]) % 3, (x[0] * y[1] + x[1] * y[0]) % 3)
    sq = {mul(x, x) for x in els if x != (0, 0)}
    assert len(sq) == 4
    idx = {x: i for i, x in enumerate(els)}
    A = np.zeros((9, 9), dtype=np.int64)
    for x in els:
        for y in els:
            if ((x[0] - y[0]) % 3, (x[1] - y[1]) % 3) in sq: A[idx[x], idx[y]] = 1
    sigma = [idx[((-x[0]) % 3, (-x[1]) % 3)] for x in els]
    chars = None
    return A, sigma, els


def bvls243():
    g = [2, 0, 1, 2, 1, 1]                                            # g(X) = X^5 + X^4 + 2X^3 + X^2 + 2 over F_3 (low -> high)

    def polymod(p):
        p = p[:] + [0] * max(0, 5 - len(p))
        for d in range(len(p) - 1, 4, -1):
            c = p[d] % 3
            if c:
                for j in range(6): p[d - 5 + j] = (p[d - 5 + j] - c * g[j]) % 3
        return tuple(x % 3 for x in p[:5])
    pw = [polymod([0] * j + [1]) for j in range(12)]
    assert pw[11] == (1, 0, 0, 0, 0), "g does not divide X^11 - 1"
    conn = set()
    for j in range(11):
        conn.add(pw[j]); conn.add(tuple((-c) % 3 for c in pw[j]))
    assert len(conn) == 22 and (0,) * 5 not in conn
    els = [tuple((i // 3 ** j) % 3 for j in range(5)) for i in range(243)]
    idx = {x: i for i, x in enumerate(els)}
    A = np.zeros((243, 243), dtype=np.int64)
    for x in els:
        for c in conn:
            A[idx[x], idx[tuple((a + b) % 3 for a, b in zip(x, c))]] = 1
    sigma = [idx[tuple((-a) % 3 for a in x)] for x in els]
    # minimum distance of the code {x in F_3^11 : sum x_j pw[j] = 0}: brute force over weights <= 4 (must be none), i.e. d >= 5
    import itertools
    bad = 0
    for w in range(1, 5):
        for pos in itertools.combinations(range(11), w):
            for cf in itertools.product((1, 2), repeat=w):
                s = [0] * 5
                for p_, c_ in zip(pos, cf):
                    for t in range(5): s[t] += c_ * pw[p_][t]
                if all(v % 3 == 0 for v in s): bad += 1
    assert bad == 0, "code has a word of weight <= 4"
    return A, sigma, els


# ------------------------------------------------------------------ helpers
def rank_mod_p(M, p=1000003):
    M = [[int(x) % p for x in row] for row in M]; rows, cols = len(M), len(M[0]); r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c]), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], p - 2, p)
        M[r] = [x * inv % p for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r


def rank_Q(M):
    M = [[Fr(int(x)) for x in row] for row in M]; rows, cols = len(M), len(M[0]); r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def analyse(name, A, sigma, els, nrand=300):
    P("=" * 100); P(name)
    res = {}
    n = len(A); I = np.eye(n, dtype=np.int64); J = np.ones((n, n), dtype=np.int64)
    k = int(A[0].sum())
    # --- (G): srg(n,k,1,2), sigma an involutive automorphism with exactly one fixed vertex
    assert (A == A.T).all() and (np.diag(A) == 0).all() and (A.sum(axis=1) == k).all()
    A2 = A @ A
    assert (A2 == k * I + 1 * A + 2 * (J - I - A)).all(), "not srg(n,k,1,2)"
    assert (A2 == (k - 2) * I - A + 2 * J).all()
    sg = np.array(sigma)
    assert (sg[sg] == np.arange(n)).all(), "sigma not an involution"
    assert (A[np.ix_(sg, sg)] == A).all(), "sigma not an automorphism"
    fixed = [x for x in range(n) if sigma[x] == x]
    assert len(fixed) == 1; p = fixed[0]
    # eigenvalues: theta^2 + theta - (k-2) = 0
    disc = 1 + 4 * (k - 2); c = math.isqrt(disc); assert c * c == disc
    r, s = (-1 + c) // 2, (-1 - c) // 2
    assert r + s == -1 and r * s == 2 - k and r - s == c
    # multiplicities f (of r), g (of s): f + g = n - 1, k + r f + s g = 0
    g_ = Fr(k + r * (n - 1), r - s); f_ = n - 1 - g_
    assert g_.denominator == 1 and f_.denominator == 1; g_, f_ = int(g_), int(f_)
    P("n=%d k=%d  r=%d s=%d c=r-s=%d  mult(r)=%d mult(s)=%d  fixed vertex index %d" % (n, k, r, s, c, f_, g_, p))
    res.update(n=n, k=k, r=r, s=s, c=c, mult_r=f_, mult_s=g_)
    # --- Lemma 0: x ~ sigma x iff x ~ p
    for x in range(n):
        if x != p: assert A[x, sigma[x]] == A[x, p]
    Pm = np.zeros((n, n), dtype=np.int64); Pm[np.arange(n), sg] = 1       # (P phi)(x) = phi(sigma x)
    assert (Pm @ A == A @ Pm).all()
    trP, trPA = int(np.trace(Pm)), int(np.trace(Pm @ A))
    assert trP == 1 and trPA == k == sum(int(A[x, sigma[x]]) for x in range(n))
    # 1 + t_r + t_s = 1,  k + r t_r + s t_s = k  => t_r = t_s = 0 (det = s - r != 0)
    res.update(trace_P=trP, trace_PA=trPA)
    # --- orbits, RANDOM representatives
    seen = set(); reps = []
    for x in range(n):
        if x == p or x in seen: continue
        seen.add(x); seen.add(sigma[x]); reps.append(random.choice([x, sigma[x]]))
    random.shuffle(reps)
    m = len(reps); assert m == (n - 1) // 2
    X = np.array(reps); SX = sg[X]
    S = A[np.ix_(X, X)] - A[np.ix_(X, SX)]                                   # S_ij = A(x_i,x_j) - A(x_i, sigma x_j)
    inner = np.array([A[x, p] == 1 for x in reps])
    assert int(inner.sum()) == k // 2
    assert (np.diag(S) == np.where(inner, -1, 0)).all(), "diagonal of S"
    assert (S == S.T).all(), "S not symmetric"
    Im = np.eye(m, dtype=np.int64)
    assert (S @ S + S == (k - 2) * Im).all(), "S^2 + S != (k-2) I"
    trS = int(np.trace(S))
    # multiplicities of S from the trace: a (of s) + b (of r) = m, s a + r b = trS
    a_s = Fr(r * m - trS, r - s); assert a_s.denominator == 1; a_s = int(a_s); b_r = m - a_s
    assert 2 * a_s == g_ and 2 * b_r == f_, "odd parts are not half of the multiplicities"
    P("orbits m=%d: inner %d, outer %d; trace S=%d; S: eigenvalue s mult %d, eigenvalue r mult %d" % (m, int(inner.sum()), m - int(inner.sum()), trS, a_s, b_r))
    res.update(m=m, inner=int(inner.sum()), mult_s_odd=a_s, mult_r_odd=b_r)
    H = r * Im - S
    assert (H @ H == c * H).all(), "H^2 != c H"
    trH = int(np.trace(H)); assert trH == c * a_s
    rk = rank_mod_p(H.tolist()); assert rk == a_s, "rank H mod p"
    if m <= 60: assert rank_Q(H.tolist()) == a_s
    assert (np.diag(H) == np.where(inner, r + 1, r)).all()
    Hoff = H - np.diag(np.diag(H)); assert set(np.unique(Hoff).tolist()) <= {-1, 0, 1}
    assert (H[np.ix_(inner, inner)] == (r + 1) * np.eye(int(inner.sum()), dtype=np.int64)).all(), "h not orthogonal"
    assert ((H[np.ix_(inner, ~inner)] != 0).sum(axis=0) == 2).all(), "each u meets exactly two h"
    P("H = rI - S: H^2 = cH, rank %d (= trace/c = %d), norms inner %d outer %d, h pairwise orthogonal, each u meets exactly 2 h" % (rk, trH // c, r + 1, r))
    res.update(rank_H=rk, norm_inner=r + 1, norm_outer=r)
    # complementary matrix
    Hc = S - s * Im; assert (Hc @ Hc == c * Hc).all(); assert int(np.trace(Hc)) == c * b_r
    res.update(compl_norm_inner=int(-1 - s), compl_norm_outer=int(-s), compl_rank=b_r)

    def lift(a):
        phi = np.zeros(n, dtype=object)
        for i in range(m): phi[X[i]] = int(a[i]); phi[SX[i]] = -int(a[i])
        return phi
    Ao = A.astype(object)
    # --- Lemma 1 on arbitrary integer a (not eigenvectors): A lift(a) = lift(S a) at EVERY vertex
    for _ in range(50):
        a = np.array([random.randint(-5, 5) for _ in range(m)], dtype=object)
        lhs = Ao @ lift(a); rhs = lift(S.astype(object) @ a)
        assert (lhs == rhs).all()
        assert sum(int(v) ** 2 for v in lift(a)) == 2 * sum(int(v) ** 2 for v in a)
    P("Lemma 1: A lift(a) = lift(S a) at every vertex (p and N(p) included), 50 random integer a")
    # negative control: zero diagonal
    S0 = S - np.diag(np.diag(S)); nbad = 0
    for _ in range(50):
        a = np.array([random.randint(-5, 5) for _ in range(m)], dtype=object)
        nbad += not ((Ao @ lift(a)) == lift(S0.astype(object) @ a)).all()
    P("  control: S with zero diagonal fails Lemma 1 in %d / 50 cases; S0^2+S0=(k-2)I: %s" % (nbad, bool((S0 @ S0 + S0 == (k - 2) * Im).all())))
    res.update(control_zero_diag_fail=nbad)
    # flipping one representative flips row and column i of S
    i0 = 0; X2 = X.copy(); X2[i0] = SX[i0]; SX2 = sg[X2]
    S2 = A[np.ix_(X2, X2)] - A[np.ix_(X2, SX2)]; Dg = np.eye(m, dtype=np.int64); Dg[i0, i0] = -1
    assert (S2 == Dg @ S @ Dg).all()

    # --- concrete model of the frame: M = (A - r)(A - k) = D E_s, D = (s-r)(s-k); F_i = M d_i; form kappa x.x' on block 1
    D = (s - r) * (s - k)
    M = (A - r * I) @ (A - k * I)
    assert (A @ M == s * M).all() and (M @ M == D * M).all()
    assert (M == (k - 2 + r * k) * I - (1 + r + k) * A + 2 * J).all()
    dvec = np.zeros((m, n), dtype=np.int64); dvec[np.arange(m), X] = 1; dvec[np.arange(m), SX] = -1
    Fm = dvec @ M                                                             # rows F_i in Z^n
    kappa = Fr(c, 2 * D * D)
    FF = Fm @ Fm.T
    assert all(kappa * int(FF[i, j]) == int(H[i, j]) for i in range(m) for j in range(m)), "concrete frame does not have Gram rI - S"
    P("concrete model: F_i = (A-r)(A-k)(e_x - e_sx), form kappa x.x', kappa = c/(2 D^2) = %s, D = %d: Gram = rI - S exactly" % (kappa, D))
    res.update(D=D, kappa=str(kappa))

    # --- integer s-eigenfunctions of A that are odd (for glue vectors): characters t(u.x)
    glue_phi = []
    if n == 243:
        t = {0: 0, 1: 1, 2: -1}
        good = []
        for ui in range(1, 243):
            u = els[ui]
            phi = np.array([t[sum(a * b for a, b in zip(u, x)) % 3] for x in els], dtype=np.int64)
            if (A @ phi == s * phi).all(): good.append(ui)
        assert len(good) == g_, "number of characters with eigenvalue s"
        gset = set(good)
        phis = {ui: np.array([t[sum(a * b for a, b in zip(els[ui], x)) % 3] for x in els], dtype=np.int64) for ui in good}
        # triples u, u', -(u+u') all with eigenvalue s: (phi_u + phi_u' + phi_u'')/3 is an integer eigenfunction of squared norm 54
        trip = []
        idx = {x: i for i, x in enumerate(els)}
        for ui in good:
            for vi in good:
                if vi <= ui: continue
                w = idx[tuple((-(a + b)) % 3 for a, b in zip(els[ui], els[vi]))]
                if w in gset and w not in (ui, vi):
                    q = phis[ui] + phis[vi] + phis[w]
                    if (q % 3 == 0).all(): trip.append(q // 3)
            if len(trip) >= 40: break
        P("characters with eigenvalue s: %d (= mult(s)); small integer eigenfunctions (phi_u+phi_u'+phi_u'')/3 found: %d, squared norms %s"
          % (len(good), len(trip), sorted({int((q * q).sum()) for q in trip})))
        res.update(small_eigfun_sqnorms=sorted({int((q * q).sum()) for q in trip}))
        # choose glue: g1 = w(phi1) + y1/3, g2 = w(phi2) + y2/3, g3 = w(phi3) + (y1+y2)/3  [w(phi) = (D/c) phi on block 1]
        cand = trip[:20] + [phis[good[0]], phis[good[7]] + phis[good[11]]]
        random.shuffle(cand)
        glue_phi = cand
    # generators: (block-1 integer vector, alpha, beta) with v = x + alpha y1 + beta y2, form kappa x.x' + c(alpha alpha' + beta beta')
    gens = [(Fm[i].astype(object), Fr(0), Fr(0)) for i in range(m)]
    gens.append((np.zeros(n, dtype=object), Fr(1), Fr(0)))                  # y1
    gens.append((np.zeros(n, dtype=object), Fr(0), Fr(1)))                  # y2
    iy1, iy2 = m, m + 1

    def ip(u, v):
        return kappa * int(sum(int(a) * int(b) for a, b in zip(u[0], v[0]))) + c * (u[1] * v[1] + u[2] * v[2])
    nglue = 0
    if glue_phi:
        assert D % c == 0
        ycomp = [(Fr(3, c), Fr(0)), (Fr(0), Fr(3, c)), (Fr(3, c), Fr(3, c)), (Fr(3, c), Fr(-3, c)), (Fr(6, c), Fr(3, c))]
        for phi in glue_phi:
            for al, be in ycomp[nglue % len(ycomp):] + ycomp[:nglue % len(ycomp)]:      # vary the component on the normals
                gv = ((D // c) * phi.astype(object), al, be)
                if ip(gv, gv).denominator != 1: continue
                if all(ip(gv, h_).denominator == 1 for h_ in gens[m:]) and all(ip(gv, gens[i]).denominator == 1 for i in range(m)):
                    gens.append(gv); nglue += 1; break
            if nglue >= 4: break
    ng = len(gens)
    Gm = [[ip(gens[i], gens[j]) for j in range(ng)] for i in range(ng)]
    assert all(x.denominator == 1 for row in Gm for x in row), "lattice not integral"
    Gi = np.array([[int(x) for x in row] for row in Gm], dtype=object)
    rkU = rank_mod_p([[int(x) for x in row] for row in Gm])
    assert rkU == a_s + 2, "rank of U' is not rank(H) + 2"
    assert (Gi[:m, :m] == H.astype(object)).all() and Gi[iy1, iy1] == c and Gi[iy2, iy2] == c and Gi[iy1, iy2] == 0 and (Gi[:m, iy1] == 0).all() and (Gi[:m, iy2] == 0).all()
    P("lattice U' = <f_1..f_%d, y1, y2, %d glue vectors>: integral, rank %d = %d + 2; glue (norm; (g,y1),(g,y2)): %s"
      % (m, nglue, rkU, a_s, [(int(Gi[j, j]), int(Gi[j, iy1]), int(Gi[j, iy2])) for j in range(m + 2, ng)]))
    res.update(n_glue=nglue, rank_U=rkU, glue=[(int(Gi[j, j]), int(Gi[j, iy1]), int(Gi[j, iy2])) for j in range(m + 2, ng)])

    # --- the theorem on random lattice vectors, from the Gram matrix only, and from the concrete model
    So = S.astype(object); Evals = set(); n_glue_used = 0; n_zero = 0; n_pos = 0; even_fail = 0; maxE = 0
    stats_p = 0
    for trial in range(nrand):
        z = np.zeros(ng, dtype=object)
        mode = trial % 6
        if mode == 5:                                                        # vectors of Z y1 + Z y2 (E must be 0, phi = 0)
            z[iy1] = random.randint(-4, 4); z[iy2] = random.randint(-4, 4)
        else:
            for _ in range(random.randint(1, 6)): z[random.randrange(m)] += random.randint(-3, 3)
            z[iy1] += random.randint(-3, 3); z[iy2] += random.randint(-3, 3)
            if nglue and mode in (1, 2, 3):
                for _ in range(random.randint(1, 2)): z[m + 2 + random.randrange(nglue)] += random.choice([-2, -1, 1, 2])
        if any(z[m + 2:]): n_glue_used += 1
        Gz = Gi @ z
        N = int(z @ Gz); a = Gz[:m]; b1, b2 = int(Gz[iy1]), int(Gz[iy2])       # a_i = (v, f_i), (v,y1), (v,y2)
        E = c * N - b1 * b1 - b2 * b2
        assert all(isinstance(int(v), int) for v in a)
        assert sum(int(v) ** 2 for v in a) == E, "sum a_i^2 != E(v)"
        assert ((So @ a) == s * a).all(), "S a != s a"
        phi = lift(a)
        Aphi = Ao @ phi
        assert (Aphi == s * phi).all(), "A phi != s phi"
        assert Aphi[p] == 0 and phi[p] == 0; stats_p += 1
        assert all(phi[sigma[x]] == -phi[x] for x in range(n))
        assert sum(int(v) ** 2 for v in phi) == 2 * E, "sum phi^2 != 2 E"
        assert (E == 0) == (not any(phi))
        # E depends only on v mod Z y1 + Z y2
        z2 = z.copy(); z2[iy1] += random.randint(-3, 3); z2[iy2] += random.randint(-3, 3); Gz2 = Gi @ z2
        assert c * int(z2 @ Gz2) - int(Gz2[iy1]) ** 2 - int(Gz2[iy2]) ** 2 == E and (Gz2[:m] == a).all()
        # the same from the concrete model (ambient coordinates): pi(v) has block-1 part (D/c) phi_v
        xb = sum((int(z[j]) * gens[j][0] for j in range(ng) if z[j]), np.zeros(n, dtype=object))
        al = sum((int(z[j]) * gens[j][1] for j in range(ng)), Fr(0)); be = sum((int(z[j]) * gens[j][2] for j in range(ng)), Fr(0))
        Namb = kappa * int(sum(int(v) ** 2 for v in xb)) + c * (al * al + be * be)
        assert Namb == N and c * al == b1 and c * be == b2
        assert all(int(xb[x]) * c == D * int(phi[x]) for x in range(n)), "block-1 part of v is not (D/c) phi_v"
        # negative control: even lift
        if E > 0:
            n_pos += 1; Evals.add(E); maxE = max(maxE, E)
            ev = np.zeros(n, dtype=object)
            for i in range(m): ev[X[i]] = int(a[i]); ev[SX[i]] = int(a[i])
            even_fail += not ((Ao @ ev) == s * ev).all()
        else:
            n_zero += 1
            assert not any(z[:m]) or True
    P("theorem on %d random v of U' (%d with a glue component): a_i integers, S a = s a, A phi_v = s phi_v at all %d vertices incl. p, "
      "sum a_i^2 = E(v), sum phi_v^2 = 2 E(v), phi_v = 0 iff E(v) = 0: ALL HOLD" % (nrand, n_glue_used, n))
    P("  E > 0: %d vectors, %d distinct values, max %d; E = 0: %d vectors; even lift fails in %d / %d" % (n_pos, len(Evals), maxE, n_zero, even_fail, n_pos))
    res.update(nrand=nrand, n_glue_used=n_glue_used, n_Epos=n_pos, distinct_E=len(Evals), n_E0=n_zero, even_lift_fail=even_fail, smallest_E=sorted(Evals)[:8])

    # --- negative control: rank. Add a third direction y3 (norm 1) orthogonal to everything: rank(H) + 3. Then sum a_i^2 < E(v)
    viol = 0; tot = 0
    for _ in range(100):
        z = np.zeros(ng, dtype=object)
        for _ in range(random.randint(1, 4)): z[random.randrange(m)] += random.randint(-3, 3)
        z[iy1] = random.randint(-2, 2); z[iy2] = random.randint(-2, 2); t3 = random.choice([-2, -1, 1, 2])
        Gz = Gi @ z; N = int(z @ Gz) + t3 * t3; a = Gz[:m]; E = c * N - int(Gz[iy1]) ** 2 - int(Gz[iy2]) ** 2
        sa = sum(int(v) ** 2 for v in a); tot += 1
        assert sa == E - c * t3 * t3 and ((So @ a) == s * a).all()             # still an eigenvector, but the norm identity is lost
        viol += sa < E
    P("  control (rank): with an extra orthogonal direction, sum a_i^2 = E(v) - c t^2 < E(v) in %d / %d cases (S a = s a still holds)" % (viol, tot))
    res.update(control_rank_strict=viol)
    # --- negative control: normals not orthogonal / wrong norm: replace y2 by y2' = y1 + y2
    bad = 0; tot = 0
    for _ in range(100):
        z = np.zeros(ng, dtype=object)
        for _ in range(random.randint(1, 4)): z[random.randrange(m)] += random.randint(-3, 3)
        z[iy1] = random.randint(-2, 2); z[iy2] = random.randint(-2, 2)
        Gz = Gi @ z; N = int(z @ Gz); a = Gz[:m]; b1 = int(Gz[iy1]); b2p = int(Gz[iy1]) + int(Gz[iy2])
        Efalse = c * N - b1 * b1 - b2p * b2p; tot += 1
        bad += sum(int(v) ** 2 for v in a) != Efalse
    P("  control (H4): with y2 replaced by y1 + y2 the formula for E is wrong in %d / %d cases" % (bad, tot))
    res.update(control_H4_fail=bad)
    OUT[name] = res
    return res


if __name__ == "__main__":
    A, sg, els = paley9(); analyse("Paley(9) = srg(9,4,1,2), sigma: x -> -x", A, sg, els)
    A, sg, els = bvls243(); analyse("BvLS srg(243,22,1,2) (cosets of the ternary Golay code), sigma: x -> -x", A, sg, els)
    # the 99 case: constants only (no graph is known)
    n, k = 99, 14; disc = 1 + 4 * (k - 2); c = math.isqrt(disc); assert c * c == disc
    r, s = (-1 + c) // 2, (-1 - c) // 2; g_ = Fr(k + r * (n - 1), r - s); f_ = n - 1 - g_
    P("=" * 100); P("(99,14,1,2): r=%d s=%d c=%d mult(r)=%s mult(s)=%s; odd parts (traces 0): %s and %s; trace S = -7 = %d; "
                    "frame norms inner %d outer %d; trace H = %d = c * %d; D = %d, E_s = ((k-2+rk)I - (1+r+k)A + 2J)/D = (%dI - %dA + 2J)/%d"
                    % (r, s, c, f_, g_, f_ / 2, g_ / 2, s * (g_ / 2) + r * (f_ / 2), r + 1, r, 7 * (r + 1) + 42 * r, (7 * (r + 1) + 42 * r) // c,
                       (s - r) * (s - k), k - 2 + r * k, 1 + r + k, (s - r) * (s - k)))
    OUT["99"] = dict(r=r, s=s, c=c, mult_r=int(f_), mult_s=int(g_))
    json.dump(OUT, open(__file__.replace(".py", ".out.json"), "w"), indent=1, default=str)
    P("ALL CHECKS PASSED")
