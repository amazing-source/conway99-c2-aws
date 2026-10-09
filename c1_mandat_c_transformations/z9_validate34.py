"""END-TO-END VALIDATION of the CUBIC (z9cubic.py) and QUARTIC (z9quartic.py) nine-class systems on a lattice that exists.
M_0 = K_8 + B^18 as in z9_validate.py (formal rank r = 27):  O = K_8^* + B^18,  L_9 = sqrt7 K_8^* + sqrt7 (B^*)^18.
Harmonic polynomials on R^44, zonal with pole u = first coordinate axis of the K_8 part (t = <x,u>):
    cubic   P3(x) = t^3 - (3/46)|x|^2 t,        quartic  P4(x) = t^4 - (1/8)|x|^2 t^2 + (1/736)|x|^4.
The class series T_k = sum P(sqrt7 x) q^(x^2/2), X_c = sum P(y) q^(y^2/2) are computed directly and must satisfy every modular
equation.  (For the cubic everything is divided by sqrt7.)        usage: z9_validate34.py [N]"""
import sys, math
from fractions import Fraction as Fr
import mf7, z9theta as Z, z9cubic as ZC, z9quartic as ZQ
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
EMAX = 18 * N
# ---- K_8^* vectors (s/3, y): integer type s in Z, y in Z^7, s + sum y even; half type s, y_i in Z + 1/2, s + sum y even... (as in z9_validate.py)
# moments by class: mom[k][E18] = [sum t^0, t^1, ..., t^4],  E18 = 18 * (|x1|^2/2) = s^2 + 9|y|^2 (integer type) ; class = s mod 9
def conv(f, g, cap):
    out = {}
    for a, x in f.items():
        for b, y in g.items():
            if a[0] + b[0] <= cap:
                key = (a[0] + b[0], (a[1] + b[1]) % 2); out[key] = out.get(key, 0) + x * y
    return out
R = int(math.isqrt(EMAX // 9)) + 2
yint = {}
for b in range(-R, R + 1):
    if 9 * b * b <= EMAX: yint[(9 * b * b, b % 2)] = yint.get((9 * b * b, b % 2), 0) + 1
P7 = {(0, 0): 1}
for _ in range(7): P7 = conv(P7, yint, EMAX)
mom = {k: {} for k in range(9)}
def put(k, E, t):
    m = mom[k].setdefault(E, [Fr(0)] * 5)
    for j in range(5): m[j] += t ** j
S_ = int(math.isqrt(EMAX)) + 2
for s in range(-S_, S_ + 1):
    for (e, par), v in P7.items():
        if (s + par) % 2: continue
        E = s * s + e
        if E <= EMAX:
            m = mom[s % 9].setdefault(E, [Fr(0)] * 5); t = Fr(s, 3)
            for j in range(5): m[j] += v * t ** j
yh = {}
for b in range(-R - 1, R + 1):
    val = 9 * (2 * b + 1) ** 2
    if val <= 4 * EMAX: yh[(val, b % 2)] = yh.get((val, b % 2), 0) + 1
Ph = {(0, 0): 1}
for _ in range(7): Ph = conv(Ph, yh, 4 * EMAX)
for a in range(-S_ - 1, S_ + 1):
    for (e, par), v in Ph.items():
        if (a + par) % 2: continue
        E4 = (2 * a + 1) ** 2 + e
        if E4 % 4: continue
        E = E4 // 4
        if E <= EMAX:
            m = mom[(a - 4) % 9].setdefault(E, [Fr(0)] * 5); t = Fr(2 * a + 1, 6)
            for j in range(5): m[j] += v * t ** j
# ---- h^18 and its norm moments: sum over x2 in B^18 of |x2|^(2i) q^(|x2|^2/2), |x2|^2 = 2n
h18 = [1] + [0] * mf7.N
for _ in range(18): h18 = mf7.mul(h18, mf7.H1)
def layer(k, side, P):
    """{num9: value} of sum P over the vectors of class k, exponent num9/9.  P(t, a, b) with t = <x1,u>, a = |x1|^2, b = |x2|^2
    for the M side the vector is sqrt7 (x1, x2) (so P is evaluated at sqrt7 t, 7a, 7b); for the L side it is (sqrt7 x1, x2)."""
    out = {}
    for E, m in mom[k].items():
        a = Fr(E, 9)                                            # |x1|^2
        for n in range(0, N + 1):
            if not h18[n]: continue
            b = 2 * n
            if side == "T": num9 = E // 2 + 9 * n if E % 2 == 0 else None
            else: num9 = 7 * E // 2 + 9 * n if (7 * E) % 2 == 0 else None
            if num9 is None or num9 > 9 * N: continue
            out[num9] = out.get(num9, Fr(0)) + h18[n] * P(m, a, b, side)
    return out
def P4(m, a, b, side):
    if side == "T": return 49 * (m[4] - Fr(1, 8) * (a + b) * m[2] + Fr(1, 736) * (a + b) ** 2 * m[0])
    return 49 * m[4] - Fr(1, 8) * (7 * a + b) * 7 * m[2] + Fr(1, 736) * (7 * a + b) ** 2 * m[0]
def P3(m, a, b, side):                                          # divided by sqrt7
    if side == "T": return 7 * (m[3] - Fr(3, 46) * (a + b) * m[1])
    return 7 * m[3] - Fr(3, 46) * (7 * a + b) * m[1]
for name, Sys, P, classes in (("quartic", ZQ.Even(27, N), P4, range(0, 5)), ("cubic", ZC.Cubic(27, N), P3, range(1, 5))):
    nfix = 0
    cache = {(side, k): layer(k, side, P) for side in "TX" for k in classes}
    for nm, idx in list(Sys.index.items()):
        if nm[0] == "x": continue
        side, k, j = nm
        num9 = (Z.RHO if side == "T" else Z.SIG)[k] + 9 * j
        Sys.rows.append({idx: Fr(1)}); Sys.rhs.append(cache[(side, k)].get(num9, Fr(0))); nfix += 1
    if name == "quartic": free, expr = Sys.reduce(); ok = free is not None
    else:
        from flint import fmpq, fmpq_mat
        nv = len(Sys.names); M = fmpq_mat(len(Sys.rows), nv + 1)
        for i, (row, b) in enumerate(zip(Sys.rows, Sys.rhs)):
            for j, c in row.items(): M[i, j] = fmpq(c.numerator, c.denominator)
            M[i, nv] = fmpq(b.numerator, b.denominator)
        Rm, rk = M.rref(); ok = all(next(j for j in range(nv + 1) if Rm[i, j] != 0) != nv for i in range(rk))
    nz = sum(1 for (side, k), d in cache.items() for v in d.values() if v != 0)
    print(f"{name}: {nfix} class values imposed ({nz} non-zero layer sums), modular system consistent: {ok}", flush=True)
