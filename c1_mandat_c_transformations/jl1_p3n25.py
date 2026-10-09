"""S0 (rank 43): LEVEL-1 Jacobi form of ONE P3/N25 vector.

W = M_0 + A_8 + N_4 glued is an even unimodular lattice of rank 56.  A vector y = 2/9 + 1_P - 1_N of L_9 (class 2, norm 208/9,
F_7^2-class d of norm type 20) lifts to  v = (y/sqrt7, a0, b0),  a0 = e_1 + e_2 - (2/9)1 (norm 14/9),  b0 minimal in the partner
class of N_4^# (norm 8/7):  |v|^2 = 208/63 + 14/9 + 8/7 = 6.  So
      phi_v = sum_{u in W} q^(|u|^2/2) zeta^<u,v>   lies in J_{28,3}(SL_2(Z)),   of dimension 9 = 3 + 2 + 2 + 2.
In S0 the roots of W are those of A_8 and N_4 (76), with known products with v.  Step 1 (this script): the root distribution, the
general form of all c(n, r) in terms of  w2 = a_2(W)  and the distribution c(2, .) of the products of v with the vectors of norm 4.
usage: jl1_p3n25.py [A|B]      (type of the N_4 component: A = (norm 8/7, 0), B = (norm 4/7, norm 4/7))"""
import sys, itertools
from fractions import Fraction as Fr
import jl1
TYPE = sys.argv[1] if len(sys.argv) > 1 else "A"
k, m = 28, 3
# ---------------- N_4 = O_K + O_K, vectors of the dual as ((x1,y1),(x2,y2))/7 with x = 3y mod 7 in each block
def okdual(maxn49):
    out = []; Bd = int((maxn49 / 2) ** 0.5) + 3
    for x in range(-Bd, Bd + 1):
        for y in range(-Bd, Bd + 1):
            if (x - 3 * y) % 7: continue
            n49 = 2 * x * x + 2 * x * y + 4 * y * y
            if n49 <= maxn49: out.append((x, y, n49))
    return out
OK = okdual(49 * 8)
def ip49(u, v): return 2 * u[0] * v[0] + u[0] * v[1] + u[1] * v[0] + 4 * u[1] * v[1]
def n4(maxnorm, integral=None):
    """vectors (u1, u2) of N_4^# with norm <= maxnorm; integral=True keeps those of N_4 only"""
    out = []
    for u1 in OK:
        for u2 in OK:
            if u1[2] + u2[2] > 49 * maxnorm: continue
            isint = all(c % 7 == 0 for c in (u1[0], u1[1], u2[0], u2[1]))
            if integral is None or integral == isint: out.append((u1, u2))
    return out
def nip(b, c): return Fr(ip49(b[0], c[0]) + ip49(b[1], c[1]), 49)
N4int = n4(6, True)
N4roots = [b for b in N4int if b[0][2] + b[1][2] == 98]; N4n4 = [b for b in N4int if b[0][2] + b[1][2] == 196]
assert len(N4roots) == 4 and len(N4n4) == 12, (len(N4roots), len(N4n4))
min47 = [u for u in OK if u[2] == 28]; min87 = [u for u in OK if u[2] == 56]; zero = (0, 0, 0)
if TYPE == "A": b0 = (min87[0], zero)
else: b0 = (min47[0], min47[0])
assert nip(b0, b0) == Fr(8, 7)
# ---------------- A_8^*: integer 9-tuples z, a = z - (sum z / 9) 1
def aip(z, w): return Fr(sum(x * y for x, y in zip(z, w))) - Fr(sum(z) * sum(w), 9)
def tuples(sumz, sq):
    """integer 9-tuples with given sum and given sum of squares (small values)"""
    out = []
    def rec(i, cur, s, q):
        if i == 9:
            if s == sumz and q == sq: out.append(tuple(cur))
            return
        for x in (-2, -1, 0, 1, 2):
            if q + x * x <= sq: rec(i + 1, cur + [x], s + x, q + x * x)
    rec(0, [], 0, 0); return out
A8roots = tuples(0, 2); A8n4 = tuples(0, 4)
assert len(A8roots) == 72 and len(A8n4) == 756
a0 = (1, 1, 0, 0, 0, 0, 0, 0, 0)
assert aip(a0, a0) == Fr(14, 9)
cls1 = tuples(1, 1)                                   # e_i - 1/9 : 9 vectors
# ---------------- root distribution
from collections import Counter
roots = Counter()
for z in A8roots: roots[aip(z, a0)] += 1
for b in N4roots: roots[nip(b, b0)] += 1
print(f"type {TYPE}: products of v with the 76 roots:", dict(sorted(roots.items())))
# ---------------- vectors of norm 4 of W in pure S0 with known products with v
n4known = Counter()
for z in A8n4: n4known[aip(z, a0)] += 1               # (0, a, 0)
for b in N4n4: n4known[nip(b, b0)] += 1               # (0, 0, b)
for z in A8roots:
    for b in N4roots: n4known[aip(z, a0) + nip(b, b0)] += 1
prof = {Fr(11, 9): 3, Fr(-7, 9): 25, Fr(2, 9): 71}    # coordinates of y
for yv, cnt in prof.items():
    for z in cls1:
        r = yv + aip(z, a0)
        n4known[r] += cnt; n4known[-r] += cnt         # +-(w_u, a_i, 0)
assert all(r.denominator == 1 for r in n4known)
print("known vectors of norm 4 (A_8, N_4, root+root, vertex lifts) by product with v:", dict(sorted(n4known.items())), " total", sum(n4known.values()))
# ---------------- the Jacobi form: parameters w2, and coordinates on S30, S32, S34
B28 = jl1.basis(28); S30, S32, S34 = jl1.cusp(30), jl1.cusp(32), jl1.cusp(34)
assert (len(B28), len(S30), len(S32), len(S34)) == (3, 2, 2, 2)
# theta_W = 1 + 76 q + w2 q^2 + ... : affine in w2
red, piv = jl1.rref([[B28[0][n], B28[1][n], B28[2][n]] + [[1, 0], [76, 0], [0, 1]][n] for n in range(3)])
th = [[sum(red[i][3] * B28[i][n] for i in range(3)), sum(red[i][4] * B28[i][n] for i in range(3))] for n in range(jl1.NQ + 1)]
NP = 1 + 1 + 6                                         # const, w2, six cusp coordinates
def form(const=0, w2=0, cusp=None):
    f = [Fr(const), Fr(w2)] + [Fr(0)] * 6
    if cusp:
        for j, vv in cusp.items(): f[2 + j] = Fr(vv)
    return f
xi = [[form(th[n][0], th[n][1]) for n in range(jl1.NQ + 1)],
      [form(cusp={0: S30[0][n], 1: S30[1][n]}) for n in range(jl1.NQ + 1)],
      [form(cusp={2: S32[0][n], 3: S32[1][n]}) for n in range(jl1.NQ + 1)],
      [form(cusp={4: S34[0][n], 5: S34[1][n]}) for n in range(jl1.NQ + 1)]]
NMAX = 10
C = jl1.solve_coeffs(k, m, xi, NMAX)
# impose the root distribution c(1, r) = roots[r] for r = 1, 2, 3 (r = 0 follows from the total 76), then express everything
# in terms of w2, x1 = c(2,1), x2 = c(2,2), x3 = c(2,3)
eqs = []
for r in (1, 2, 3): eqs.append([C[(1, r)][j] for j in range(2, 8)] + [C[(1, r)][1], roots.get(Fr(r), 0) - C[(1, r)][0]])
# unknown vector: (six cusp coordinates) ; right-hand side affine in w2:  sum coef * cusp = rhs_const - coef_w2 * w2
# add the definitions x_r = c(2, r) as new variables: solve for the six cusp coordinates in terms of (1, w2, x1, x2, x3)
rows = []
for r in (1, 2, 3):
    f = C[(1, r)]; rows.append([f[j] for j in range(2, 8)] + [roots.get(Fr(r), 0) - f[0], -f[1], 0, 0, 0])
for i, r in enumerate((1, 2, 3)):
    f = C[(2, r)]; rhs = [-f[0], -f[1], 0, 0, 0]; rhs[2 + i] = Fr(1)
    rows.append([f[j] for j in range(2, 8)] + rhs)
red, piv = jl1.rref(rows)
assert piv[:6] == list(range(6)), piv
sol = [red[i][6:] for i in range(6)]                   # cusp coordinate i = affine in (1, w2, x1, x2, x3)
def conv(f):
    out = [f[0], f[1], Fr(0), Fr(0), Fr(0)]
    for i in range(6):
        if f[2 + i] != 0: out = [o + f[2 + i] * s for o, s in zip(out, sol[i])]
    return out
T = {key: conv(f) for key, f in C.items() if key != "constraints"}
assert T[(1, 0)][1:] == [0, 0, 0, 0], T[(1, 0)]
print("c(1,0) =", T[(1, 0)][0], " (expected", roots.get(Fr(0), 0), ")")
sh = lambda f: f"{f[0]} + ({f[1]}) w2 + ({f[2]}) x1 + ({f[3]}) x2 + ({f[4]}) x3"
print("with w2 = a_2(W), x_r = c(2, r):")
for n in (2, 3, 4):
    for r in range(0, 4): print(f"   c({n},{r}) = {sh(T[(n, r)])}")
import pickle
pickle.dump({"T": T, "roots": dict(roots), "n4known": dict(n4known), "TYPE": TYPE}, open(f"jl1_p3n25_{TYPE}.pkl", "wb"))
