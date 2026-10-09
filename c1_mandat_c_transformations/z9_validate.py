"""END-TO-END VALIDATION of the nine-class programme (z9theta.py) on a lattice that exists.
K_8 = diag(3,1,...,1) E_8 (even, det 9, discriminant form opposite to A_8; K_8 + A_8 glues to D_16^+), B = [[2,1],[1,4]] (7-modular).
Take  M_0 = K_8 + B^18  (rank 44, level 63, 7-part of the determinant 7^18, i.e. the formal rank r = 27):
   O   = K_8^* + B^18,            Theta_k(tau) = theta_{K_8^*, class k}(tau) h(tau)^18,
   L_9 = sqrt7 M_0^* = sqrt7 K_8^* + B^18,   Xi_c(tau) = theta_{K_8^*, class c}(7 tau) h(tau)^18.
These series must satisfy every modular equation of Model(27, N) for some form coordinates."""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, z9theta as Z
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
# ---- theta of K_8^* by class, exponents in units of 1/18:  E18 = s^2 + 9 |y|^2  (norm/2 = E18/18)
EMAX = 18 * N
def conv(f, g):
    out = {}
    for a, x in f.items():
        for b, y in g.items():
            if a[0] + b[0] <= EMAX:
                key = (a[0] + b[0], (a[1] + b[1]) % 2); out[key] = out.get(key, 0) + x * y
    return out
import math
R = int(math.isqrt(EMAX // 9)) + 2
yint = {(9 * b * b, b % 2): 0 for b in range(-R, R + 1) if 9 * b * b <= EMAX}
for b in range(-R, R + 1):
    if 9 * b * b <= EMAX: yint[(9 * b * b, b % 2)] += 1
P = {(0, 0): 1}
for _ in range(7): P = conv(P, yint)                     # y in Z^7: (9 |y|^2, parity of sum)
theta = {k: {} for k in range(9)}
S = int(math.isqrt(EMAX)) + 2
for s in range(-S, S + 1):
    for (e, par), v in P.items():
        if (s + par) % 2: continue                       # s + sum y even
        E = s * s + e
        if E <= EMAX: theta[s % 9][E] = theta[s % 9].get(E, 0) + v
# half-integer part: s = a + 1/2, y_i = b_i + 1/2; 4 * (s^2 + 9|y|^2) = (2a+1)^2 + 9 sum (2b+1)^2 ; parity: s + sum y = a + sum b + 4 even
yh = {}
for b in range(-R - 1, R + 1):
    val = 9 * (2 * b + 1) ** 2
    if val <= 4 * EMAX: yh[(val, b % 2)] = yh.get((val, b % 2), 0) + 1
def conv4(f, g):
    out = {}
    for a, x in f.items():
        for b, y in g.items():
            if a[0] + b[0] <= 4 * EMAX:
                key = (a[0] + b[0], (a[1] + b[1]) % 2); out[key] = out.get(key, 0) + x * y
    return out
Ph = {(0, 0): 1}
for _ in range(7): Ph = conv4(Ph, yh)
for a in range(-S - 1, S + 1):
    for (e, par), v in Ph.items():
        if (a + par) % 2: continue
        E4 = (2 * a + 1) ** 2 + e
        assert E4 % 4 == 0
        E = E4 // 4
        if E <= EMAX:
            k = (a - 4) % 9                              # class of s = a + 1/2 :  s - 9/2 = a - 4
            theta[k][E] = theta[k].get(E, 0) + v
tot = {}
for k in range(9):
    for E, v in theta[k].items(): tot[E] = tot.get(E, 0) + v
print("class 0 of K_8^* (= K_8), first coefficients by exponent/18:", sorted(theta[0].items())[:6])
print("minimal exponents by class (units 1/18):", {k: min(theta[k]) for k in range(9)}, " expected class k: 10 k^2 mod 18 pattern")
# ---- h^18
h18 = [1] + [0] * mf7.N
for _ in range(18): h18 = mf7.mul(h18, mf7.H1)
def times_h18(ser18, scale):
    """ser18: {E18: v} at tau*scale; returns {num9: coefficient} of the product with h^18, exponent = num9/9"""
    out = {}
    for E, v in ser18.items():
        base = E * scale                                  # exponent * 18
        if base % 2: raise ValueError("odd exponent")
        for n in range(0, N + 1):
            num9 = base // 2 + 9 * n
            if num9 <= 9 * N and h18[n]: out[num9] = out.get(num9, 0) + v * h18[n]
    return out
Mo = Z.Model(27, N)
nfix = 0
for name, idx in Mo.index.items():
    if name[0] == "x": continue
    side, k, j = name
    num9 = (Z.RHO if side == "T" else Z.SIG)[k] + 9 * j
    ser = times_h18(theta[k], 1 if side == "T" else 7)
    Mo.eq({idx: Fr(1)}, ser.get(num9, 0), "test value"); nfix += 1
ok, piv, free, Rm = Mo.solve()
print(f"validation on K_8 + B^18 (formal rank 27), truncation {N}: {nfix} class values imposed, modular system consistent: {ok}")
