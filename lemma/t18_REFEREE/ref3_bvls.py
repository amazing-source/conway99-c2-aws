# Referee check 3: the general hand facts tested on REAL graphs with the same local rules (lambda = 1, mu = 2) and an
# involution with exactly one fixed point:  Paley(9) = srg(9,4,1,2) and the Berlekamp-van Lint-Seidel graph srg(243,22,1,2),
# both with sigma : x -> -x.
#   (A0)  x ~ sigma x  iff  x in N(p);  for x outside N[p] the two common neighbours of x, sigma x form one orbit outside N[p];
#         orbit map is a fixed-point-free involution; nobody but p is adjacent to both vertices of an edge {a, sigma a} of N(p).
#   (P2)  trace(sigma | V_theta) = 0 on both non-trivial eigenspaces, so the odd and even parts have equal rank;
#         the general idempotent formulas  (r - s) E_s = rI - A + ((k - r)/v) J ,  (r - s) E_r = A - sI - ((k - s)/v) J.
#   (counting identities in general form) for a sigma-odd {0,+-1} eigenfunction (taken from a character).
import itertools
import numpy as np
from fractions import Fraction

def check(name, V, adj_fn, neg_fn, k, r, s):
    n = len(V); pos = {v: i for i, v in enumerate(V)}
    A = np.zeros((n, n), dtype=np.int64)
    for v in V:
        for u in adj_fn(v):
            A[pos[v], pos[u]] = 1
    assert (A == A.T).all() and (A.sum(1) == k).all()
    J = np.ones((n, n), dtype=np.int64); I = np.eye(n, dtype=np.int64)
    assert (A @ A == (k - 2) * I - A + 2 * J).all(), "not srg(v,k,1,2)"
    sig = np.array([pos[neg_fn(v)] for v in V])
    fixed = [i for i in range(n) if sig[i] == i]
    assert len(fixed) == 1
    p = fixed[0]
    assert (A[np.ix_(sig, sig)] == A).all(), "sigma is not an automorphism"
    # A0
    for x in range(n):
        if x == p: continue
        assert (A[x, sig[x]] == 1) == (A[x, p] == 1)
    Np = set(np.nonzero(A[p])[0])
    for a in Np:
        both = [x for x in range(n) if A[x, a] and A[x, sig[a]]]
        assert both == [p]
    iota = {}
    for x in range(n):
        if x == p or x in Np: continue
        cn = [z for z in range(n) if A[x, z] and A[sig[x], z]]
        assert len(cn) == 2 and sig[cn[0]] == cn[1] and cn[0] not in Np and p not in cn
        iota[frozenset((x, int(sig[x])))] = frozenset(int(c) for c in cn)
    assert all(iota[iota[o]] == o and iota[o] != o for o in iota)
    print(f"{name}: srg({n},{k},1,2) OK; sigma automorphism with one fixed point; A0 (a), (b) hold; "
          f"iota is a fixed-point-free involution on {len(iota)} outer orbits; N(p) = {len(Np)//2} mate edges")
    # traces
    P = np.zeros((n, n), dtype=np.int64); P[np.arange(n), sig] = 1
    tr1 = int(np.trace(P)); trA = int(np.trace(P @ A)); trJ = int(np.trace(P @ J))
    Es_num = r * I * n - A * n + (k - r) * J          # = n (r - s) E_s
    Er_num = A * n - s * I * n - (k - s) * J          # = n (r - s) E_r
    # idempotent checks (integer arithmetic): X^2 = n (r-s) X
    assert (Es_num @ Es_num == n * (r - s) * Es_num).all() and (Er_num @ Er_num == n * (r - s) * Er_num).all()
    assert (A @ Es_num == s * Es_num).all() and (A @ Er_num == r * Er_num).all()
    ms = Fraction(int(np.trace(Es_num)), n * (r - s)); mr = Fraction(int(np.trace(Er_num)), n * (r - s))
    ts = Fraction(int(np.trace(P @ Es_num)), n * (r - s)); tr_ = Fraction(int(np.trace(P @ Er_num)), n * (r - s))
    print(f"   trace(sigma) = {tr1}, trace(sigma A) = {trA} (= k), trace(sigma J) = {trJ}; "
          f"mult(s={s}) = {ms}, mult(r={r}) = {mr}; trace(sigma|V_s) = {ts}, trace(sigma|V_r) = {tr_}")
    # ranks of odd / even parts
    reps = [x for x in range(n) if x < sig[x]]
    Dm = np.zeros((len(reps), n)); Dp = np.zeros((len(reps) + 1, n))
    for t, x in enumerate(reps):
        Dm[t, x] = 1; Dm[t, sig[x]] = -1
        Dp[t, x] = 1; Dp[t, sig[x]] = 1
    Dp[len(reps), p] = 1
    Es = Es_num.astype(float) / (n * (r - s)); Er = Er_num.astype(float) / (n * (r - s))
    rk = lambda M: int(np.linalg.matrix_rank(M, tol=1e-8))
    print(f"   rank E_s odd / even: {rk(Dm @ Es @ Dm.T)} / {rk(Dp @ Es @ Dp.T)};  rank E_r odd / even: {rk(Dm @ Er @ Dm.T)} / {rk(Dp @ Er @ Dp.T)}")
    # the odd orbit Gram  (r I - A[R,R] + A[R, sigma R])  equals (r - s)/2 * Dm E_s Dm^T
    R = np.array(reps)
    Godd = r * np.eye(len(R)) - A[np.ix_(R, R)] + A[np.ix_(R, sig[R])]
    assert np.allclose(Godd, (r - s) / 2 * Dm @ Es @ Dm.T)
    print(f"   odd orbit Gram rI - A[R,R] + A[R,sigma R] = (r-s)/2 * Gram of E_s(e_x - e_sigma x): OK, rank {rk(Godd)} of {len(R)}")
    return A, sig, p, pos

# ---- Paley 9 ----
F9 = [(a, b) for a in range(3) for b in range(3)]          # a + b i, i^2 = -1
mul = lambda u, v: ((u[0] * v[0] - u[1] * v[1]) % 3, (u[0] * v[1] + u[1] * v[0]) % 3)
sq = set(mul(u, u) for u in F9 if u != (0, 0))
check("Paley(9)", F9, lambda v: [((v[0] + q[0]) % 3, (v[1] + q[1]) % 3) for q in sq],
      lambda v: ((-v[0]) % 3, (-v[1]) % 3), 4, 1, -2)

# ---- BvLS: Cayley graph of F_3^5 on +-(x^i mod g), g = x^5 + x^4 - x^3 + x^2 - 1 (ternary Golay code, QR length 11) ----
g = [2, 0, 1, 2, 1, 1]          # coefficients of 1, x, ..., x^5  (-1 = 2)
def xpow_mod(i):
    v = [0] * 5; v[0] = 1
    for _ in range(i):
        c = v[4]
        v = [0] + v[:4]
        # x^5 = -(g0 + g1 x + ... + g4 x^4)
        v = [(v[t] - c * g[t]) % 3 for t in range(5)]
    return tuple(v)
cols = [xpow_mod(i) for i in range(11)]
conn = set(cols) | set(tuple((-a) % 3 for a in c) for c in cols)
assert len(conn) == 22
V = list(itertools.product(range(3), repeat=5))
add = lambda u, v: tuple((a + b) % 3 for a, b in zip(u, v))
A, sig, p, pos = check("BvLS", V, lambda v: [add(v, c) for c in conn], lambda v: tuple((-a) % 3 for a in v), 22, 4, -5)

# ---- counting identities in general form, on a real sigma-odd {0,+-1} eigenfunction of BvLS ----
n = len(V)
done = 0
for a in V:
    if a == (0,) * 5: continue
    phi = np.array([{0: 0, 1: 1, 2: -1}[sum(x * y for x, y in zip(a, v)) % 3] for v in V])
    lam = (A @ phi)
    if not (lam == -5 * phi).all(): continue
    assert (phi[sig] == -phi).all()
    Sp = np.nonzero(phi == 1)[0]; Sm = np.nonzero(phi == -1)[0]; out = np.nonzero(phi == 0)[0]
    m = len(Sp)
    dplus = A[:, Sp].sum(1); dminus = A[:, Sm].sum(1)
    assert (dminus[Sp] == dplus[Sp] + 5).all() and (dplus[out] == dminus[out]).all()
    e = int(dplus[Sp].sum()) // 2
    Q = int((dplus[Sp] ** 2).sum())
    d = dplus[out]
    lhs = int((d * (d - 1) // 2).sum())
    # general identity: sum_{z outside} C(d,2) = m(m-1) - e - sum_{S+} [C(d+,2) + C(d+ + |s|, 2)]
    rhs = m * (m - 1) - e - int(sum(x * (x - 1) // 2 + (x + 5) * (x + 4) // 2 for x in dplus[Sp]))
    assert lhs == rhs, (lhs, rhs)
    assert int(d.sum()) == int(sum(22 - 2 * x - 5 for x in dplus[Sp]))
    kk = int(dplus[p])
    # parity law in this graph: sum over outside z != p of C(d,2) is even
    assert (lhs - kk * (kk - 1) // 2) % 2 == 0
    # Lemma 1 in general form: for z outside, sum_{w ~ z, w outside} d(w) = 2m - d(z) - sum_{w ~ z, w in S} d+(w)
    for z in out:
        nb = np.nonzero(A[z])[0]
        s_in = sum(int(dplus[w]) for w in nb if phi[w] != 0)
        s_out = sum(int(dplus[w]) for w in nb if phi[w] == 0)
        assert s_out == 2 * m - int(dplus[z]) - s_in
    done += 1
print(f"BvLS: {done} sigma-odd {{0,+-1}} (-5)-eigenfunctions from characters: general counting identity, edge count, "
      f"parity of the outside sum and the path-count identity all hold")
