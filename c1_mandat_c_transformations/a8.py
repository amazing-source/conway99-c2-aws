"""Class theta series of A_8^* with zonal harmonic weights, exact.

A_8^* = pi(Z^9) (projection on the hyperplane sum = 0); a = z - (s/9) 1, s = sum z; class = s mod 9;
|a|^2 = |z|^2 - s^2/9.  One representative z per a in the class k (0 <= k <= 8): sum z = k exactly.
Exponent of q for a: |a|^2 / 2 = (9 |z|^2 - k^2) / 18;  series are stored as {E18: coefficient}, E18 = 9 |z|^2 - k^2.

Zonal harmonic of degree m in R^8 with pole v:  Z_m(a) = sum_i c(m,i) (a.v)^(m-2i) (|v|^2 |a|^2)^i,
    c(m,i) = (-1)^i m! / ( i! (m-2i)! 4^i prod_{j=1..i} (m + 3 - j) )            (d = 8: d/2 + m - 1 - j = m + 3 - j).
Poles: 'r' : v = e_1 - e_2 (|v|^2 = 2, a.v = z_1 - z_2);   'w' : v = e_1 - (1/9) 1 (|v|^2 = 8/9, a.v = z_1 - k/9).

    series(k, m, pole, N)  ->  {E18: Fraction}  for exponents <= N  (E18 <= 18 N)."""
from fractions import Fraction as Fr
from math import factorial, comb
from functools import lru_cache


def zonal_coeffs(m):
    out = []
    for i in range(m // 2 + 1):
        den = factorial(i) * factorial(m - 2 * i) * 4 ** i
        for j in range(1, i + 1): den *= (m + 3 - j)
        out.append(Fr((-1) ** i * factorial(m), den))
    return out


def pmul(f, g, nmax):
    """product of two series {(n, s): c} truncated at n <= nmax"""
    out = {}
    for (n1, s1), c1 in f.items():
        for (n2, s2), c2 in g.items():
            n = n1 + n2
            if n <= nmax:
                key = (n, s1 + s2); out[key] = out.get(key, 0) + c1 * c2
    return out


@lru_cache(maxsize=None)
def base(nmax):
    R = int(nmax ** 0.5) + 1
    theta = {(z * z, z): 1 for z in range(-R, R + 1) if z * z <= nmax}
    T = {(0, 0): 1}; powers = [T]
    for _ in range(8):
        T = pmul(T, theta, nmax); powers.append(T)
    return R, powers          # powers[j] = theta^j


@lru_cache(maxsize=None)
def moment_r(j, nmax):
    """sum over z in Z^9 of (z1 - z2)^j q^|z|^2 zeta^(sum z)"""
    R, powers = base(nmax)
    D = {}
    for z1 in range(-R, R + 1):
        for z2 in range(-R, R + 1):
            n = z1 * z1 + z2 * z2
            if n <= nmax:
                key = (n, z1 + z2); D[key] = D.get(key, 0) + (z1 - z2) ** j
    D = {k: v for k, v in D.items() if v}
    return pmul(D, powers[7], nmax)


@lru_cache(maxsize=None)
def moment_w(i, nmax):
    """sum over z in Z^9 of z1^i q^|z|^2 zeta^(sum z)"""
    R, powers = base(nmax)
    D = {(z * z, z): z ** i for z in range(-R, R + 1) if z * z <= nmax and (z ** i)}
    if i == 0: D = {(z * z, z): 1 for z in range(-R, R + 1) if z * z <= nmax}
    return pmul(D, powers[8], nmax)


@lru_cache(maxsize=None)
def series(k, m, pole, N):
    """zonal class series of class k (0..8), degree m, exponents <= N, as a tuple of (E18, value) sorted"""
    nmax = 2 * N + 8
    cz = zonal_coeffs(m); out = {}
    v2 = Fr(2) if pole == "r" else Fr(8, 9)
    for i, c in enumerate(cz):
        p = m - 2 * i                               # power of a.v
        if pole == "r":
            mom = moment_r(p, nmax)
            vals = {n: v for (n, s), v in mom.items() if s == k}
        else:
            vals = {}
            for t in range(p + 1):                  # (z1 - k/9)^p = sum_t C(p,t) z1^t (-k/9)^(p-t)
                cf = comb(p, t) * Fr(-k, 9) ** (p - t)
                if cf == 0: continue
                for (n, s), v in moment_w(t, nmax).items():
                    if s == k: vals[n] = vals.get(n, 0) + cf * v
        for n, v in vals.items():
            E18 = 9 * n - k * k
            if E18 > 18 * N or v == 0: continue
            a2 = Fr(E18, 9)                         # |a|^2
            out[E18] = out.get(E18, Fr(0)) + c * (v2 * a2) ** i * v
    return tuple(sorted((e, v) for e, v in out.items() if v != 0))


if __name__ == "__main__":
    N = 8
    t0 = dict(series(0, 0, "r", N)); t3 = dict(series(3, 0, "r", N))
    print("theta of A_8, class 0:", [t0.get(18 * n, 0) for n in range(N + 1)])
    e8 = [t0.get(18 * n, 0) + 2 * t3.get(18 * n, 0) for n in range(N + 1)]
    sig3 = lambda n: sum(d ** 3 for d in range(1, n + 1) if n % d == 0)
    print("class 0 + 2 class 3 = E_4:", e8 == [1] + [240 * sig3(n) for n in range(1, N + 1)])
    for pole in ("r", "w"):
        for m in (2, 4, 6, 8, 10):
            s0 = dict(series(0, m, pole, N)); s3 = dict(series(3, m, pole, N))
            comb_ = [s0.get(18 * n, 0) + 2 * s3.get(18 * n, 0) for n in range(N + 1)]
            lead = {k: (series(k, m, pole, N)[0] if series(k, m, pole, N) else None) for k in range(5)}
            print(f"pole {pole} degree {m}: E_8 combination {[str(x) for x in comb_]}")
            print(f"      leading terms by class (E18, value): { {k: (v[0], str(v[1])) if v else None for k, v in lead.items()} }")
