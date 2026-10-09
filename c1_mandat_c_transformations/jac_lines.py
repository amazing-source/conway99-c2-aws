"""JACOBI FORM OF THE LINE CONFIGURATION (index 2) in the scenario S0 of rank 43.

NEW FACT USED.  The 231 line vectors h_l = sqrt7 E 1_l are vectors of norm 4 of the even lattice M, so
    phi(tau, z) = sum_l sum_{x in M} q^(|x|^2/2) zeta^<x,h_l>
is a Jacobi form of weight 22 and index 2 on Gamma_0(7).  Its coefficient
    c(n, r) = #{(x, l) : |x|^2 = 2n, <x, h_l> = r}          (r = sum of the three coordinates of sqrt7 x on the line l)
depends only on (8n - r^2, r mod 4).  Same on the dual side (y in L1 = sqrt7 M^#, N = |y|^2/2, s = y(l)):
    cL(N, s) depends only on (8N - 7 s^2, s mod 4).
The three Taylor coefficients of phi are: 231 theta (weight 22), 0 (weight 24: the lines form a 2-design, sum_l h_l h_l^T = 21 E)
and the quartic series G of weight 26 (the series P_T of section 9).  So every c(n, r), cL(N, s) is determined by theta and G.
In S0, theta is known and G lies in a space of dimension 1 or 2: all the c are affine in one or two real parameters and must be
non-negative integers.          usage: jac_lines.py [NMAX]"""
import sys, math
from fractions import Fraction as Fr
import mf7, thetalp
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 42
R = 43

# ---------------- theta in S0
T = thetalp.Theta(R, nmax=NMAX, standard=False)
eqs = [T.a[n] for n in range(7, 13)] + [[x - y for x, y in zip(T.a[14], T.b[2])]]
red, piv, _ = mf7.rref([f[1:] + [-f[0]] for f in eqs])
assert piv == list(range(7)), "theta not determined"
c = [red[i][7] for i in range(7)]
val = lambda f: f[0] + sum(x * y for x, y in zip(f[1:], c))
a = [val(T.a[n]) for n in range(NMAX + 1)]; b = [val(T.b[n]) for n in range(NMAX + 1)]
assert a[13] == 2632 and b[2] == 1000 and b[1] == 0 and all(a[7 * k] == b[k] for k in range(1, NMAX // 7 + 1))
assert all(x.denominator == 1 and x >= 0 for x in a + b)
print("S0 theta: a13 =", a[13], " b2 =", b[2], " b3 =", b[3], " a14 =", a[14], " a15 =", a[15])

# ---------------- the quartic series G (weight 26)
S = mf7.Space(26); D = len(S.ser)
fac = -Fr(7) ** ((R - 23) // 2)
def coefL(n): return [Fr(S.ser[i][n]) for i in range(D)]
def coefM(n): return [fac * sum(S.W[i][j] * S.ser[j][n] for j in range(D)) for i in range(D)]
rows = [coefL(n) for n in range(0, 13)] + [coefM(0), coefM(1)]
def nullspace(rows):
    red, piv, _ = mf7.rref(rows)
    out = []
    for fcol in [j for j in range(D) if j not in piv]:
        v = [Fr(0)] * D; v[fcol] = Fr(1)
        for rw, p in zip(red, piv): v[p] = -rw[fcol]
        out.append(v)
    return out
ns0 = nullspace(rows)
print(f"quartic series with the S0 zeros (G_L[0..12] = 0, G_M[0] = G_M[1] = 0): dimension {len(ns0)}")
tr = [[x - 49 * y for x, y in zip(coefL(7 * n), coefM(n))] for n in range(2, NMAX // 7 + 1)]
ns = nullspace(rows + tr)
print(f"with the rank-43 class equality G_L[7n] = 49 G_M[n] (n = 2..{NMAX // 7}): dimension {len(ns)}")
K = len(ns)
GL = [[sum(x * y for x, y in zip(coefL(n), v)) for v in ns] for n in range(NMAX + 1)]      # G_L[n] as a vector over the parameters
GM = [[sum(x * y for x, y in zip(coefM(n), v)) for v in ns] for n in range(NMAX + 1)]
# normalise each basis vector: make G_M[2] or the first non-zero coefficient equal to 1
print("G_M[2..5] per basis vector:", [[str(GM[n][k]) for n in range(2, 6)] for k in range(K)])
print("G_L[13..15] per basis vector:", [[str(GL[n][k]) for n in range(13, 16)] for k in range(K)])

# affine forms in the K parameters: [const, coef_1..coef_K]
def aff(const, vec=None): return [Fr(const)] + ([Fr(0)] * K if vec is None else [Fr(x) for x in vec])
def add(*fs): return [sum(x) for x in zip(*fs)]
def sc(f, s): return [x * s for x in f]

# ---------------- M side: c(n, r), classes (8n - r^2, r mod 4)
CM = {}
def red_M(n, r):
    """reduced representative (n', r') with r' in {-1, 0, 1, 2}"""
    lam = -((r + 1) // 4); rp = r + 4 * lam; return n + lam * r + 2 * lam * lam, rp
def cM(n, r):
    n2, r2 = red_M(n, r)
    if r2 == -1: r2 = 1                                             # symmetry x -> -x
    if n2 < 0 or (n2 == 0 and r2 != 0): return aff(0)
    if n2 == 0: return aff(231)
    return CM[(n2, r2)]
for n in range(1, NMAX + 1):
    rmax = math.isqrt(8 * n)
    R0 = aff(231 * b[n]); R2 = aff(42 * n * b[n]); R4 = add(sc(aff(0, GM[n]), 49), aff(Fr(504, 23) * n * n * b[n]))
    for r in range(3, rmax + 1):
        v = cM(n, r); R0 = add(R0, sc(v, -2)); R2 = add(R2, sc(v, -2 * r * r)); R4 = add(R4, sc(v, -2 * r ** 4))
    c2 = sc(add(R4, sc(R2, -1)), Fr(1, 24)) if rmax >= 2 else aff(0)
    c1 = sc(add(R2, sc(c2, -8)), Fr(1, 2))
    c0 = add(R0, sc(c1, -2), sc(c2, -2))
    CM[(n, 0)], CM[(n, 1)], CM[(n, 2)] = c0, c1, c2
# ---------------- L side: cL(N, s), classes (8N - 7 s^2, s mod 4)
CL = {}
def cLf(N, s):
    lam = -((s + 1) // 4); sp = s + 4 * lam; N2 = N + 7 * lam * (s + 2 * lam)
    if sp == -1: sp = 1
    if N2 < 0 or (N2 == 0 and sp != 0): return aff(0)
    if N2 == 0: return aff(231)
    return CL[(N2, sp)]
for Nn in range(1, NMAX + 1):
    smax = math.isqrt(8 * Nn // 7)
    R0 = aff(231 * a[Nn]); R2 = aff(6 * Nn * a[Nn]); R4 = add(aff(0, GL[Nn]), aff(Fr(72, 161) * Nn * Nn * a[Nn]))
    for s in range(3, smax + 1):
        v = cLf(Nn, s); R0 = add(R0, sc(v, -2)); R2 = add(R2, sc(v, -2 * s * s)); R4 = add(R4, sc(v, -2 * s ** 4))
    c2 = sc(add(R4, sc(R2, -1)), Fr(1, 24))
    c1 = sc(add(R2, sc(c2, -8)), Fr(1, 2))
    c0 = add(R0, sc(c1, -2), sc(c2, -2))
    CL[(Nn, 0)], CL[(Nn, 1)], CL[(Nn, 2)] = c0, c1, c2
# consistency required by the geometry: a pair (N, s) with 8N - 7 s^2 < 0 cannot occur (Cauchy-Schwarz), and cL(7n, s) = c(n, s)
import pickle
pickle.dump({"K": K, "CM": CM, "CL": CL, "a": a, "b": b, "GL": GL, "GM": GM}, open("jac_lines.pkl", "wb"))
show = lambda f: " + ".join([str(f[0])] + [f"({f[1 + k]})*t{k + 1}" for k in range(K) if f[1 + k] != 0])
print("\nM side, norm 4 (n = 2):  c(2,0) =", show(CM[(2, 0)]), ";  c(2,1) =", show(CM[(2, 1)]), ";  c(2,2) =", show(CM[(2, 2)]))
print("L side, norm 26 (N = 13): cL(13,0) =", show(CL[(13, 0)]), ";  cL(13,1) =", show(CL[(13, 1)]), ";  cL(13,2) =", show(CL[(13, 2)]))
bad = [(n, s) for n in range(1, NMAX // 7 + 1) for s in (0, 1, 2) if CL[(7 * n, s)] != CM[(n, s)]]
print("class equality cL(7n, s) = c(n, s) for all n, s:", "holds identically" if not bad else f"FAILS at {bad[:6]}")
