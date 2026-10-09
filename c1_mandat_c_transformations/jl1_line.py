"""S0 (rank 43): LEVEL-1 Jacobi form of ONE line.

At rank 43, U = M + N_4 glued (N_4 = O_K + O_K) is an even unimodular lattice of rank 48.  In S0 its roots are the 4 roots of N_4,
and its vectors of norm 4 are: the 1000 of M, the 12 of N_4, and the 4 x 329 lifts (z/sqrt7, b) of the vectors z of norm 26 of L1
lying in the four classes whose N_4-partner has minimum 2/7.  So theta_U = 1 + 4 q + 2328 q^2 + ... is determined.
For a line l, v = (h_l, 0) has norm 4 and is orthogonal to the 4 roots, and
      phi_l = sum_{u in U} q^(|u|^2/2) zeta^<u,v>   lies in J_{24,2}(SL_2(Z)), of dimension 6 = 3 + 1 + 2.
theta_U (3 coordinates) and the root distribution c(1,0) = 4, c(1,1) = c(1,2) = 0 (2 conditions) leave ONE parameter:
      t_l = c(2,2) = #{u in U of norm 4 : <u, v> = 2}.
Question: for which integers t_l are all c(n, r) non-negative integers?"""
import sys
from fractions import Fraction as Fr
import jl1
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 14
A1 = int(sys.argv[2]) if len(sys.argv) > 2 else 4
A2 = int(sys.argv[3]) if len(sys.argv) > 3 else 2328
k, m = 24, 2
B = jl1.basis(24); S26 = jl1.cusp(26); S28 = jl1.cusp(28)
assert len(B) == 3 and len(S26) == 1 and len(S28) == 2
red, piv = jl1.rref([[B[0][n], B[1][n], B[2][n], [1, A1, A2][n]] for n in range(3)])
th = [sum(red[i][3] * B[i][n] for i in range(3)) for n in range(jl1.NQ + 1)]
print("theta_U =", [str(x) for x in th[:6]])
# parameters: x (coordinate on S26), y1, y2 (coordinates on S28): affine forms [const, x, y1, y2]
xi = [[[Fr(th[n]), 0, 0, 0] for n in range(jl1.NQ + 1)],
      [[0, Fr(S26[0][n]), 0, 0] for n in range(jl1.NQ + 1)],
      [[0, 0, Fr(S28[0][n]), Fr(S28[1][n])] for n in range(jl1.NQ + 1)]]
xi = [[[Fr(v) for v in f] for f in row] for row in xi]
C = jl1.solve_coeffs(k, m, xi, NMAX)
# root distribution: c(1,1) = 0, c(1,2) = 0 ; then c(2,2) = t
rows = [C[(1, 1)][1:] + [-C[(1, 1)][0]], C[(1, 2)][1:] + [-C[(1, 2)][0]]]
red, piv = jl1.rref(rows)
free = [j for j in range(3) if j not in piv]
assert len(piv) == 2 and len(free) == 1
def subst(f):
    """affine form in (x, y1, y2) -> [const, coefficient of the free coordinate]"""
    c0 = f[0]; cf = Fr(0)
    for j in range(3):
        if f[1 + j] == 0: continue
        if j in piv:
            rw = red[piv.index(j)]; c0 += f[1 + j] * rw[3]; cf -= f[1 + j] * rw[free[0]]
        else: cf += f[1 + j]
    return [c0, cf]
D = {key: subst(f) for key, f in C.items() if key != "constraints"}
assert D[(1, 1)] == [0, 0] and D[(1, 2)] == [0, 0], (D[(1, 1)], D[(1, 2)])
print("c(1,0) =", D[(1, 0)])
a, b = D[(2, 2)]
assert b != 0
conv = lambda f: [f[0] - f[1] * a / b, f[1] / b]                 # in terms of t = c(2,2)
T = {key: conv(f) for key, f in D.items()}
lo, hi = None, None
print("all coefficients as  A + B t   (t = c(2,2)):")
for n in range(1, NMAX + 1):
    for r in range(0, 3):
        A_, B_ = T[(n, r)]
        if n <= 5: print(f"   c({n},{r}) = {A_} + ({B_}) t")
        if B_ > 0: lo = max(lo, -A_ / B_) if lo is not None else -A_ / B_
        elif B_ < 0: hi = min(hi, -A_ / B_) if hi is not None else -A_ / B_
        elif A_ < 0: print(f"   NEGATIVE CONSTANT c({n},{r}) = {A_}")
print(f"non-negativity up to n = {NMAX}:  {float(lo) if lo is not None else None} <= t <= {float(hi) if hi is not None else None}   (exact: {lo} .. {hi})")
import math
dens = sorted({math.lcm(A_.denominator, B_.denominator) for (A_, B_) in T.values()})
print("denominators of the coefficient forms:", dens)
