"""S0 (rank 43): LEVEL-1 Jacobi form of ONE vertex.

In the even unimodular lattice W = M_0 + A_8 + N_4 (rank 56), the vertex v lifts to  V = (w_v, a_i, 0),  w_v = sqrt7 E e_v (norm 28/9),
a_i = e_i - (1/9)1 (norm 8/9): |V|^2 = 4.  phi_V lies in J_{28,2}(SL_2(Z)), of dimension 7 = 3 + 2 + 2.
Roots of W in S0: 72 (A_8) + 4 (N_4); products with V: +1 and -1 eight times each, 0 sixty times.
Parameters left: w2 = a_2(W), x1 = c(2,1), x2 = c(2,2).      usage: jl1_vertex.py"""
import sys
from fractions import Fraction as Fr
import jl1
k, m = 28, 2
B28 = jl1.basis(28); S30, S32 = jl1.cusp(30), jl1.cusp(32)
red, piv = jl1.rref([[B28[0][n], B28[1][n], B28[2][n]] + [[1, 0], [76, 0], [0, 1]][n] for n in range(3)])
th = [[sum(red[i][3] * B28[i][n] for i in range(3)), sum(red[i][4] * B28[i][n] for i in range(3))] for n in range(jl1.NQ + 1)]
def form(const=0, w2=0, cusp=None):
    f = [Fr(const), Fr(w2)] + [Fr(0)] * 4
    if cusp:
        for j, vv in cusp.items(): f[2 + j] = Fr(vv)
    return f
xi = [[form(th[n][0], th[n][1]) for n in range(jl1.NQ + 1)],
      [form(cusp={0: S30[0][n], 1: S30[1][n]}) for n in range(jl1.NQ + 1)],
      [form(cusp={2: S32[0][n], 3: S32[1][n]}) for n in range(jl1.NQ + 1)]]
NMAX = 12
C = jl1.solve_coeffs(k, m, xi, NMAX)
rootdist = {1: 8, 2: 0}
rows = []
for r in (1, 2):
    f = C[(1, r)]; rows.append([f[j] for j in range(2, 6)] + [rootdist[r] - f[0], -f[1], 0, 0])
for i, r in enumerate((1, 2)):
    f = C[(2, r)]; rhs = [-f[0], -f[1], 0, 0]; rhs[2 + i] = Fr(1)
    rows.append([f[j] for j in range(2, 6)] + rhs)
red, piv = jl1.rref(rows)
assert piv[:4] == [0, 1, 2, 3], piv
sol = [red[i][4:] for i in range(4)]
def conv(f):
    out = [f[0], f[1], Fr(0), Fr(0)]
    for i in range(4):
        if f[2 + i] != 0: out = [o + f[2 + i] * s for o, s in zip(out, sol[i])]
    return out
T = {key: conv(f) for key, f in C.items() if key != "constraints"}
print("c(1,0) =", T[(1, 0)], "(expected 60)")
sh = lambda f: f"{f[0]} + ({f[1]}) w2 + ({f[2]}) x1 + ({f[3]}) x2"
for n in (2, 3, 4, 5):
    for r in range(0, 3): print(f"   c({n},{r}) = {sh(T[(n, r)])}")
import pickle; pickle.dump(T, open("jl1_vertex.pkl", "wb"))
# pure S0: x2 = 0, x1 = 396 + chi, w2 = 3376 + iota ; known vectors of norm 6 with product 2: 840 + 8 chi
f = T[(3, 2)]
print("\npure S0 (x2 = 0, x1 = 396 + chi, w2 = 3376 + iota):")
for n in (3, 4, 5, 6):
    for r in range(0, 3):
        g = T[(n, r)]; print(f"   c({n},{r}) = {g[0] + 3376 * g[1] + 396 * g[2]} + ({g[1]}) iota + ({g[2]}) chi")
g = T[(3, 2)]
print("   c(3,2) minus the known vectors of product 2 (840 + 8 chi):", g[0] + 3376 * g[1] + 396 * g[2] - 840, "+ (", g[1], ") iota + (", g[2] - 8, ") chi")
