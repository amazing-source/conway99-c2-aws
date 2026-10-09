"""Jacobi forms of LEVEL 1 (Eichler-Zagier) through their Taylor development, exact.

For phi = sum c(n, r) q^n zeta^r in J_{k,m}(SL_2(Z)), k even, the modified Taylor coefficients
      xi_{2nu} = sum_n ( sum_r p_{2nu}(r, n m) c(n, r) ) q^n ,   p_{2nu}(r, N) = coefficient of t^(2nu) in (1 - r t + N t^2)^(-(k-1)),
lie in M_{k+2nu}(SL_2(Z)) (cusp forms for nu >= 1), and for m <= 3 the map phi -> (xi_0, ..., xi_{2m}) is an isomorphism
onto M_k + S_{k+2} + ... + S_{k+2m}.  c(n, r) depends only on (4mn - r^2, r mod 2m) and c(n, -r) = c(n, r).

Tools:  basis(k)  -> q-expansions of a basis of M_k ;   cusp(k) -> basis of S_k ;   gegen(k, nu, r, N) ;
        solve_coeffs(k, m, xi, NMAX) -> {(n, r): value} for 0 <= r <= m, where xi[nu][n] are numbers or affine forms (lists)."""
from fractions import Fraction as Fr
from math import comb, isqrt
NQ = 40


def sigma(n, k): return sum(d ** k for d in range(1, n + 1) if n % d == 0)
E4 = [1] + [240 * sigma(n, 3) for n in range(1, NQ + 1)]
E6 = [1] + [-504 * sigma(n, 5) for n in range(1, NQ + 1)]
def mul(f, g): return [sum(f[i] * g[n - i] for i in range(n + 1)) for n in range(NQ + 1)]
def power(f, e):
    r = [1] + [0] * NQ
    for _ in range(e): r = mul(r, f)
    return r


def basis(k):
    out = []
    for b in range(k // 6 + 1):
        if (k - 6 * b) >= 0 and (k - 6 * b) % 4 == 0: out.append(mul(power(E4, (k - 6 * b) // 4), power(E6, b)))
    return out


def cusp(k):
    B = basis(k)
    return [[x - y for x, y in zip(f, B[0])] for f in B[1:]]      # all basis elements have constant term 1


def gegen(k, nu, r, N):
    s = k - 1
    return sum(comb(s + 2 * nu - j - 1, 2 * nu - j) * comb(2 * nu - j, j) * (-Fr(N)) ** j * Fr(r) ** (2 * nu - 2 * j) for j in range(nu + 1))


def rref(rows):
    rows = [list(map(Fr, r)) for r in rows]; n = len(rows); piv = []; r = 0
    for col in range(len(rows[0])):
        p = next((i for i in range(r, n) if rows[i][col] != 0), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]
        iv = 1 / rows[r][col]; rows[r] = [x * iv for x in rows[r]]
        for i in range(n):
            if i != r and rows[i][col] != 0:
                f = rows[i][col]; rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        piv.append(col); r += 1
        if r == n: break
    return rows[:r], piv


def solve_coeffs(k, m, xi, NMAX, zero=None):
    """xi[nu][n]: affine forms (lists of Fractions, same length) for nu = 0..m.  Returns C[(n, r)] for 0 <= r <= m (affine forms)."""
    L = len(xi[0][0])
    Z = [Fr(0)] * L
    add = lambda f, g, s=1: [x + s * y for x, y in zip(f, g)]
    C = {}
    def val(n, r):
        r = abs(r)
        lam = -((r + m) // (2 * m))                    # r + 2 m lam in (-m, m]
        rr = r + 2 * m * lam; nn = n + lam * r + m * lam * lam
        if nn < 0: return Z
        return C.get((nn, abs(rr)), Z)
    for n in range(0, NMAX + 1):
        rmax = isqrt(4 * m * n)
        R = [list(xi[nu][n]) for nu in range(m + 1)]
        for r in range(m + 1, rmax + 1):
            v = val(n, r)
            if any(x != 0 for x in v):
                for nu in range(m + 1): R[nu] = add(R[nu], v, -2 * gegen(k, nu, r, n * m))
        # unknowns c(n, r), r = 0..min(m, rmax); those with 4mn - r^2 < 0 are zero
        rs = [r for r in range(0, m + 1) if r * r <= 4 * m * n]
        mat = [[(1 if r == 0 else (2 if r < m else (2 if True else 1))) * gegen(k, nu, r, n * m) for r in rs] for nu in range(len(rs))]
        # r = m: the two values +m and -m are distinct exponents of zeta, both counted
        aug = [mat[i] + R[i] for i in range(len(rs))]
        red, piv = rref(aug)
        assert piv[:len(rs)] == list(range(len(rs))), (n, piv)
        for i, r in enumerate(rs): C[(n, r)] = red[i][len(rs):]
        for r in range(0, m + 1):
            if r not in rs: C[(n, r)] = Z
        # the remaining equations (nu > len(rs) - 1) must hold identically: return them as constraints
        for nu in range(len(rs), m + 1):
            lhs = list(R[nu])
            for i, r in enumerate(rs): lhs = add(lhs, C[(n, r)], -(1 if r == 0 else 2) * gegen(k, nu, r, n * m))
            if any(x != 0 for x in lhs): C.setdefault("constraints", []).append((n, nu, lhs))
    return C


if __name__ == "__main__":
    # test: the Leech lattice and one of its minimal vectors (k = 12, m = 2): J_{12,2} has dimension 3
    # theta = 1 + 196560 q^2 + ...; no roots: c(1, r) = 0.  Expected kissing distribution: c(2,2) = 4600, c(2,1) = 47104, c(2,0) = 93150.
    k, m = 12, 2
    B0 = basis(12); S14 = cusp(14); S16 = cusp(16)
    # theta_Leech = E4^3 - 720 Delta ; in the basis (E4^3, E6^2):
    red, piv = rref([[B0[0][n], B0[1][n], [1, 0][n]] for n in range(2)])
    th = [red[0][2] * B0[0][n] + red[1][2] * B0[1][n] for n in range(NQ + 1)]
    assert th[2] == 196560
    # parameters: one coordinate on S16 (S14 = 0)
    xi = [[[Fr(th[n]), Fr(0)] for n in range(NQ + 1)], [[Fr(0), Fr(0)] for n in range(NQ + 1)], [[Fr(0), Fr(S16[0][n])] for n in range(NQ + 1)]]
    C = solve_coeffs(k, m, xi, 4)
    # condition c(1, r) = 0 for r = 0, 1, 2
    print("Leech, n = 1:", {r: [str(x) for x in C[(1, r)]] for r in range(3)})
    t = -C[(1, 2)][0] / C[(1, 2)][1] if C[(1, 2)][1] != 0 else None
    ev = lambda f: f[0] + f[1] * t
    print("parameter:", t, " c(1,.) =", [str(ev(C[(1, r)])) for r in range(3)], " c(2,.) =", [str(ev(C[(2, r)])) for r in range(3)])
