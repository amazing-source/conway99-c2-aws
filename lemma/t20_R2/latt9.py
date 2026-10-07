# T20 round 2: lattice test on the support, for the nine configurations.  CONDITIONAL tool: it compares with
# H16 (the 04/10 lemma: no non-zero sigma-odd integer (-4)-eigenfunction of squared norm <= 16) and with T18.
#
# G_T = orbit Gram of the support (10 x 10): G_ii = 3 + [i inner], G_ij = [minus edge ij] - [plus edge ij].
# c = 1_T satisfies G c = 7 c.  For k in Z, n in Z^T the function  psi = k phi + sum_i n_i g_i,
# g_i = (3I - A)(e_{x_i} - e_{y_i}), is a sigma-odd integer (-4)-eigenfunction with
#     (1/2) sum_x psi(x)^2 = Q(k, n) = 10 k^2 + 14 k (n.1) + 7 n^T G_T n  = 7 (n + (k/7) 1)^T G_T (n + (k/7) 1).
# (g_i = 7 E_{-4}(e_{x_i} - e_{y_i}); the values of psi outside the support depend on the unknown graph, its norm
# does not.)  psi = 0 iff Q = 0.  Exhaustive exact enumeration (rational LDL^T, Fincke-Pohst backtracking) of all
# (k mod 7, n) with 0 < Q <= BOUND.
import sys, json, os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
BOUND = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def structs():
    d = {}
    for fn in ("structures_I.json", "structures_III_IIb_IIa.json"):
        d.update(json.load(open(os.path.join(HERE, fn))))
    out = []
    for case in ("I", "IIa", "III"):
        for i, rec in enumerate(d[case]):
            out.append(("%s.%d" % (case, i), rec["m"], rec["H"]))
    return out


def gram(m, H):
    G = [[0] * 10 for _ in range(10)]
    for i in range(10):
        G[i][i] = 3 + (1 if i in H else 0)
        for j in range(10):
            if i != j:
                G[i][j] = (1 if m[i][j] & 1 else 0) - (1 if m[i][j] & 2 else 0)
    return G


def ldl(G):
    """G = L D L^T exactly (G positive definite), returns (D, L) with L unit lower triangular"""
    n = len(G)
    L = [[Fraction(0)] * n for _ in range(n)]
    D = [Fraction(0)] * n
    for i in range(n):
        for j in range(i):
            s = Fraction(G[i][j]) - sum(L[i][k] * L[j][k] * D[k] for k in range(j))
            L[i][j] = s / D[j]
        D[i] = Fraction(G[i][i]) - sum(L[i][k] * L[i][k] * D[k] for k in range(i))
        assert D[i] > 0, "not positive definite"
        L[i][i] = Fraction(1)
    return D, L


def enum_shifted(G, shift, bound):
    """all n in Z^10 with (n + shift)^T G (n + shift) <= bound (exact).  Form = sum_j D_j (y_j + sum_{i>j} L_ij y_i)^2,
    y = n + shift."""
    n = len(G)
    D, L = ldl(G)
    sols = []
    y = [Fraction(0)] * n
    x = [0] * n
    nodes = [0]

    def rec(j, rest):
        # variables j+1..n-1 fixed; choose x_j
        nodes[0] += 1
        if j < 0:
            sols.append(list(x))
            return
        cj = sum(L[i][j] * y[i] for i in range(j + 1, n))      # y_j + cj appears squared with weight D_j
        # D_j (x_j + shift_j + cj)^2 <= rest
        center = -(shift[j] + cj)
        # integer candidates around center
        import math
        r = rest / D[j]
        # |x_j - center| <= sqrt(r): enumerate integers by exact test
        lo = math.floor(center) - int(math.isqrt(int(r) + 1)) - 1
        hi = math.ceil(center) + int(math.isqrt(int(r) + 1)) + 1
        for v in range(lo, hi + 1):
            t = Fraction(v) - center
            w = D[j] * t * t
            if w <= rest:
                x[j] = v
                y[j] = Fraction(v) + shift[j]
                rec(j - 1, rest - w)
        x[j] = 0
        y[j] = Fraction(0)

    rec(n - 1, Fraction(bound))
    return sols, nodes[0]


def Q(G, k, nvec):
    s = sum(nvec)
    q = sum(nvec[i] * G[i][j] * nvec[j] for i in range(10) for j in range(10))
    return 10 * k * k + 14 * k * s + 7 * q


for name, m, H in structs():
    G = gram(m, H)
    assert all(sum(G[i]) == 7 for i in range(10))
    found = {}
    totnodes = 0
    for k in range(7):
        shift = [Fraction(k, 7)] * 10
        sols, nodes = enum_shifted(G, shift, Fraction(BOUND, 7))
        totnodes += nodes
        for nv in sols:
            q = Q(G, k, nv)
            assert 0 <= q <= BOUND
            if q > 0:
                found.setdefault(q, []).append((k, tuple(nv)))
    print("%s: values of Q(k,n) in 1..%d that occur (number of (k mod 7, n)): %s   [%d nodes]" % (
        name, BOUND, {q: len(v) for q, v in sorted(found.items())}, totnodes))
    for q in sorted(found):
        if q <= 9:
            k, nv = found[q][0]
            print("     example with Q = %d: k = %d, n = %s" % (q, k, list(nv)))
