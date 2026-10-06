# n3_check.py -- arithmetic companion of the hand proof "n_3 = 0" (T18, outside vertices with d = 3).
#
# The proof is by hand; it was returned in full in the final message of the agent that wrote this
# script (no REPORT.md could be written from that session).  What this script checks:
#   Lemma 1 (part A, E): z outside S with d(z) = d  =>  sum of d(w) over the neighbours w of z
#       outside S equals 18 - 5d; so d <= 3, and a d = 3 vertex has >= 5 neighbours in X_0.
#   Lemma 2 (part B): n_0 = 9 - n_3, n_1 = 54 + 3 n_3, n_2 = 18 - 3 n_3.
#   Theorem (part C): two distinct vertices of X_3 (z and sigma z) would share at least
#       5 + 5 - (9 - n_3) >= 3 neighbours in X_0, against lambda = 1, mu = 2.  Hence n_3 = 0.
#   By-product (part D): for n_3 = 0, a_0(z) <= 5 for every z outside S, z != p (z, sigma z share <= 2).
# It only re-does the arithmetic exhaustively, in exact integer arithmetic, and tests the
# double-counting identity behind Lemma 1 on two REAL strongly regular graphs with lambda = 1,
# mu = 2 (it cannot be tested on the 99-graph, which is not available).
# No solver.  Pure Python integers; numpy int64 only for 0/1 matrix products (entries < 2^31).
#
# Usage: python n3_check.py > n3_check.out
import itertools, random
import numpy as np

def C2(x):
    return x * (x - 1) // 2

print("=" * 78)
print("PART A.  Outside neighbourhood of a vertex z with d(z) = d  (Lemma 1 + degree 14)")
print("  solutions (a_0, a_1, a_2, a_3) >= 0 of")
print("     a_0 + a_1 + a_2 + a_3 = 14 - 2d,     a_1 + 2 a_2 + 3 a_3 = 18 - 5d")
print("=" * 78)
min_a0 = {}
for d in range(0, 8):
    sols = []
    tot = 14 - 2 * d
    rhs = 18 - 5 * d
    if tot >= 0:
        for a3 in range(0, tot + 1):
            for a2 in range(0, tot + 1 - a3):
                for a1 in range(0, tot + 1 - a3 - a2):
                    a0 = tot - a1 - a2 - a3
                    if a1 + 2 * a2 + 3 * a3 == rhs:
                        # closed form of the report (A8): a_0 = a_2 + 2 a_3 + 3d - 4
                        assert a0 == a2 + 2 * a3 + 3 * d - 4
                        sols.append((a0, a1, a2, a3))
    min_a0[d] = min(s[0] for s in sols) if sols else None
    if d <= 3:
        print("d = %d: %d solutions, min a_0 = %s" % (d, len(sols), min_a0[d]))
    else:
        print("d = %d: %d solutions" % (d, len(sols)))
    if d == 3:
        for s in sols:
            print("        (a_0, a_1, a_2, a_3) = %s" % (s,))
assert min_a0[3] == 5
assert all(min_a0[d] is None for d in range(4, 8))
print("CHECK A: d >= 4 has no solution; for d = 3 every solution has a_0 >= 5.  OK")

print()
print("=" * 78)
print("PART B.  Sizes n_d = |X_d| (Lemma 2): all solutions (n_0, n_1, n_2, n_3) >= 0 of")
print("     sum n_d = 81,   sum d n_d = 90,   sum C(d,2) n_d = 18")
print("=" * 78)
solsB = []
for n3 in range(0, 82):
    for n2 in range(0, 82 - n3):
        if n2 + 3 * n3 != 18:
            continue
        n1 = 90 - 2 * n2 - 3 * n3
        n0 = 81 - n1 - n2 - n3
        if n1 < 0 or n0 < 0:
            continue
        solsB.append((n0, n1, n2, n3))
        assert n0 == 9 - n3 and n1 == 54 + 3 * n3 and n2 == 18 - 3 * n3
for s in solsB:
    print("   (n_0, n_1, n_2, n_3) = %s" % (s,))
print("CHECK B: in all %d solutions n_0 = 9 - n_3, n_1 = 54 + 3 n_3, n_2 = 18 - 3 n_3.  OK" % len(solsB))
# the two totals used: 9 * (14 - 4) = 90 and 2 * C(9,2) - 9 * C(4,2) = 18
assert 9 * (14 - 4) == 90 and 2 * C2(9) - 9 * C2(4) == 18

print()
print("=" * 78)
print("PART C.  Pigeonhole of Theorem N3: two distinct vertices of X_3 share at least")
print("     5 + 5 - |X_0| = 1 + n_3  neighbours in X_0; allowed: at most 2 (lambda = 1, mu = 2)")
print("=" * 78)
for (n0, n1, n2, n3) in solsB:
    if n3 == 0:
        continue
    lb = 2 * min_a0[3] - n0
    status = "CONTRADICTION" if (n3 >= 2 and lb > 2) else ("(only one vertex in X_3: excluded by sigma, n_3 even)" if n3 == 1 else "no contradiction")
    print("   n_3 = %d: |X_0| = %d, forced common neighbours >= %d  -> %s" % (n3, n0, lb, status))
    assert n3 == 1 or lb > 2
print("CHECK C: every n_3 >= 2 is contradictory; n_3 = 1 is excluded by parity.  OK")

print()
print("=" * 78)
print("PART D.  By-product (case n_3 = 0): sigma-pair bound a_0(z) <= 5 for z outside S, z != p")
print("     z in N(p):     T = N(z) n X_0 contains p, T n sigma T = {p},  2|T| - 1 <= 9")
print("     z not in N(p): T inside X_0 minus p (8 vertices), |T n sigma T| <= 2,  2|T| - 2 <= 8")
print("=" * 78)
for label, univ, common in (("z in N(p)", 9, 1), ("z not in N(p)", 8, 2)):
    best = max(t for t in range(0, 15) if 2 * t - common <= univ)
    print("   %-14s max |T| = %d" % (label, best))
    assert best == 5
print("   hence on X_2 (a_0 = a_2 + 2): a_2 <= 3;  on X_1 (a_0 = a_2 - 1): a_2 <= 6;  on X_0 minus p (a_0 = a_2 - 4): a_2 <= 9")
print("   X_0 minus p, z not adjacent to p: T inside X_0 minus {p, z, sigma z} (6 vertices): max |T| = %d, a_2 <= 8"
      % max(t for t in range(0, 15) if 2 * t - 2 <= 6))

print()
print("=" * 78)
print("PART E.  Test of the double count behind Lemma 1 on real srg's with lambda = 1, mu = 2")
print("     identity: for every vertex set S and every z,")
print("        sum_{w ~ z} |N(w) n S| = (k - mu) [z in S] + (lambda - mu) |N(z) n S| + mu |S|")
print("     and, when S induces an r-regular graph and z is outside S with c = |N(z) n S|:")
print("        sum_{w ~ z, w outside S} |N(w) n S| = mu |S| - (mu - lambda + r) c")
print("     (99-graph: k = 14, r = 4, |S| = 18, c = 2d, |N(w) n S| = 2 d(w):  sum d(w) = 18 - 5d)")
print("=" * 78)

def cayley_f3(dim, gens):
    """Cayley graph on F_3^dim with connection set +-gens."""
    verts = list(itertools.product(range(3), repeat=dim))
    idx = {v: i for i, v in enumerate(verts)}
    conn = set()
    for g in gens:
        g = tuple(x % 3 for x in g)
        conn.add(g)
        conn.add(tuple((-x) % 3 for x in g))
    n = len(verts)
    A = np.zeros((n, n), dtype=np.int64)
    for v in verts:
        for g in conn:
            w = tuple((a + b) % 3 for a, b in zip(v, g))
            A[idx[v], idx[w]] = 1
    return A, verts, idx

def srg_params(A):
    n = A.shape[0]
    k = int(A[0].sum())
    A2 = A @ A
    lam = int(A2[0][A[0] == 1][0])
    nonadj = [j for j in range(1, n) if A[0, j] == 0]
    mu = int(A2[0, nonadj[0]])
    I = np.eye(n, dtype=np.int64)
    J = np.ones((n, n), dtype=np.int64)
    ok = bool(((A == A.T).all()) and (np.diag(A) == 0).all()
              and (A2 == (k - mu) * I + (lam - mu) * A + mu * J).all())
    return n, k, lam, mu, ok

# Paley(9) = K3 x K3 = Cayley(F_3^2, +-(1,0), +-(0,1));  srg(9,4,1,2)
A9, V9, I9 = cayley_f3(2, [(1, 0), (0, 1)])
# Berlekamp - van Lint - Seidel graph: cosets of the perfect ternary Golay code [11,6,5];
# = Cayley(F_3^5, +- the 11 columns of a parity-check matrix).  Generator [I_6 | P]:
P = [(1, 1, 1, 1, 1),
     (0, 1, 2, 2, 1),
     (1, 0, 1, 2, 2),
     (2, 1, 0, 1, 2),
     (2, 2, 1, 0, 1),
     (1, 2, 2, 1, 0)]
units = [tuple(1 if i == j else 0 for j in range(5)) for i in range(5)]
A243, V243, I243 = cayley_f3(5, P + units)

random.seed(20261006)
for name, A, verts, idx in (("Paley(9)", A9, V9, I9), ("BvLS(243)", A243, V243, I243)):
    n, k, lam, mu, ok = srg_params(A)
    print("%s: n = %d, k = %d, lambda = %d, mu = %d, A^2 = (k-mu)I + (lambda-mu)A + mu J exactly: %s" % (name, n, k, lam, mu, ok))
    assert ok and lam == 1 and mu == 2
    # (1) random subsets, all vertices z
    ntest = 0
    for trial in range(200):
        size = random.randint(1, n - 1)
        S = random.sample(range(n), size)
        s = np.zeros(n, dtype=np.int64)
        s[S] = 1
        nb = A @ s                      # |N(w) n S| for every w
        lhs = A @ nb                    # sum over w ~ z
        rhs = (k - mu) * s + (lam - mu) * nb + mu * size
        assert (lhs == rhs).all()
        ntest += n
    print("   general identity: %d (S, z) instances checked, all exact" % ntest)
    # (2) subsets inducing a regular graph: subgroups generated by 1, 2 or 3 connection elements
    dim = len(verts[0])
    gens = [verts[j] for j in range(n) if A[0, j] == 1]
    seen = set()
    nreg = 0
    ninst = 0
    for r_ in (1, 2, 3):
        combos = list(itertools.combinations(range(len(gens)), r_))
        if len(combos) > 300:
            combos = random.sample(combos, 300)
        for combo in combos:
            span = {tuple([0] * dim)}
            for gi in combo:
                g = gens[gi]
                span = {tuple((a + c * b) % 3 for a, b in zip(v, g)) for v in span for c in range(3)}
            key = frozenset(span)
            if key in seen or len(span) == n:
                continue
            seen.add(key)
            S = [idx[v] for v in span]
            s = np.zeros(n, dtype=np.int64)
            s[S] = 1
            nb = A @ s
            degs = set(int(nb[i]) for i in S)
            assert len(degs) == 1       # the induced graph is regular (translation invariant)
            r = degs.pop()
            nreg += 1
            out = (1 - s)
            lhs = A @ (nb * out)        # sum over w ~ z, w outside S, of |N(w) n S|
            for z in range(n):
                if s[z] == 0:
                    c = int(nb[z])
                    assert int(lhs[z]) == mu * len(S) - (mu - lam + r) * c
                    ninst += 1
    print("   regular-subset identity: %d subsets S (subgroups), %d pairs (S, z outside S) checked, all exact" % (nreg, ninst))
# specialisation to the 99-graph: mu |S| - (mu - lambda + r) c = 36 - 5 * (2d) = 2 (18 - 5d)
for d in range(0, 4):
    assert 2 * 18 - (2 - 1 + 4) * (2 * d) == 2 * (18 - 5 * d)
print("CHECK E: identities exact on both graphs; specialisation k=14, r=4, |S|=18, c=2d gives sum d(w) = 18 - 5d.  OK")

print()
print("ALL CHECKS PASSED")
