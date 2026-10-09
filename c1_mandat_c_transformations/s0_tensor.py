"""Rank 43, scenario S0 (no root, no vector of L1 of norm 16..24): second-moment tensors of all layers.
For a traceless symmetric S on the eigenspace, G_L = sum_{y in L1} (y^t S y) q^(|y|^2/2) and G_M = sum_{x in M} (x^t S x) q^(|x|^2/2)
are cusp forms of weight 24 on Gamma_0(7), G_L | W7 = -7^(-10) G_M, G_L[7n] = 7 G_M[n] (rank 43), G_L[n] = 0 for n <= 12,
G_M[1] = 0.  Question: how many free tensors, and what interval do the positivities of all layers leave for the
eigenvalues of the traceless tensor T of the norm-4 layer of M ?"""
from fractions import Fraction as Fr
import mf7
from thetalp import Theta
S = mf7.Space(24); D = len(S.ser); NMAX = 80
V = [[sum(S.W[i][j] * S.ser[j][n] for j in range(D)) for n in range(NMAX + 1)] for i in range(D)]
c = -Fr(7) ** (-10)
# unknown coordinates x (D): G_L = sum x_i ser_i ; G_M = (G_L | W7) / c
GL = lambda n: [Fr(S.ser[i][n]) for i in range(D)]
GM = lambda n: [V[i][n] / c for i in range(D)]
rows = [GL(n) for n in range(0, 13)] + [GM(0), GM(1)]
rows += [[a - 7 * b for a, b in zip(GL(7 * n), GM(n))] for n in range(2, NMAX // 7 + 1)]
red, piv, _ = mf7.rref(rows)
free = [i for i in range(D) if i not in piv]
print("dimension of the weight-24 space:", D, " rank of the conditions:", len(red), " free tensors:", len(free))
assert len(free) == 1
# the one-dimensional solution
x = [Fr(0)] * D; x[free[0]] = Fr(1)
for rw, p in zip(red, piv): x[p] = -rw[free[0]]
gl = [sum(x[i] * S.ser[i][n] for i in range(D)) for n in range(NMAX + 1)]
gm = [sum(x[i] * V[i][n] for i in range(D)) / c for n in range(NMAX + 1)]
s = gm[2]; gl = [v / s for v in gl]; gm = [v / s for v in gm]          # normalise G_M[2] = 1 : T = tensor of the norm-4 layer of M
print("G_M[2..8] / G_M[2]:", [str(v) for v in gm[2:9]])
print("G_L[13..20]:", [str(v) for v in gl[13:21]])
# counts in S0
T = Theta(43, NMAX, standard=False)
rows = [T.a[n][1:] + [-T.a[n][0]] for n in range(7, 13)] + [T.b[1][1:] + [-T.b[1][0]]]
red2, piv2, _ = mf7.rref(rows); cc = [red2[i][7] for i in range(7)]
val = lambda f: f[0] + sum(f[1 + i] * cc[i] for i in range(7))
a = [val(T.a[n]) for n in range(NMAX + 1)]; b = [val(T.b[n]) for n in range(NMAX // 7 + 2)]
# positivity of each layer: (2n count / 44) E + coefficient * T >= 0   (T traceless, eigenvalue lam)
lo, hi = None, None; who_lo = who_hi = None
def upd(n, cnt, coef, tag):
    global lo, hi, who_lo, who_hi
    if coef == 0: return
    bound = -Fr(2 * n * cnt, 44) / coef
    if coef > 0:
        if lo is None or bound > lo: lo, who_lo = bound, (tag, n)
    else:
        if hi is None or bound < hi: hi, who_hi = bound, (tag, n)
for n in range(2, NMAX // 7 + 1): upd(n, b[n], gm[n], "M")
for n in range(13, NMAX + 1): upd(n, a[n], gl[n], "L1")
print(f"eigenvalues of T confined to [{float(lo):.4f} (from {who_lo}), {float(hi):.4f} (from {who_hi})]")
print("for comparison: T = (extras tensor) - (2152/44) E, so its eigenvalues are >= -48.909 and sum to 0; a 2-design would be T = 0")
