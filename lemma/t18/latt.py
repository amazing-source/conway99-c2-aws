# Exact tools on the orbit ("frame") level.  Pure Python integers / Fractions.
#
# Orbit Gram matrix:  G = 3I - Ahat,  Ahat_{OO'} = A_{x y} - A_{x, sigma y},  Ahat_{OO} = -A_{x, sigma x}.
# For the 9 active orbits T (e(S+) = 0):  G_T = 3I + B + D_h   (B = minus-edge graph, D_h = 1 on h orbits).
# phi <-> c = 1_T.   For integers k and n in Z^W (W a set of orbits whose mutual Gram G_W is known)
#     lam = k c + G n   is an integer vector of the lattice Lambda (sigma-odd integer (-4)-eigenfunctions),
#     |lam|^2 = Q(k, n) = 9 k^2 + 14 k (n . 1_T) + 7 n^T G_W n.
# (H16) = the 04/10 lemma: every non-zero vector of Lambda has |lam|^2 >= 9.
# So a configuration is impossible as soon as Q takes a value in {1,...,8} (or a negative value: not PSD).
from fractions import Fraction
import itertools


def ldl(Q):
    """Exact LDL^T of a symmetric rational matrix without pivoting.
    Returns (d, L) if all pivots > 0 (positive definite), else None with the reason."""
    n = len(Q)
    A = [[Fraction(x) for x in row] for row in Q]
    d = [Fraction(0)] * n
    L = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        s = A[i][i] - sum(L[i][k] * L[i][k] * d[k] for k in range(i))
        if s <= 0:
            return None, (i, s)
        d[i] = s
        L[i][i] = Fraction(1)
        for j in range(i + 1, n):
            t = A[j][i] - sum(L[j][k] * L[i][k] * d[k] for k in range(i))
            L[j][i] = t / s
    return (d, L), None


def psd_exact(Q):
    """Exact PSD test with symmetric pivoting.  Returns (is_psd, rank)."""
    n = len(Q)
    A = [[Fraction(x) for x in row] for row in Q]
    idx = list(range(n))
    rank = 0
    while idx:
        # negative diagonal -> not PSD
        for i in idx:
            if A[i][i] < 0:
                return False, None
        piv = None
        for i in idx:
            if A[i][i] > 0:
                piv = i; break
        if piv is None:
            # all remaining diagonals zero: remaining block must vanish
            for i in idx:
                for j in idx:
                    if A[i][j] != 0:
                        return False, None
            return True, rank
        rank += 1
        idx.remove(piv)
        p = A[piv][piv]
        for i in idx:
            f = A[i][piv] / p
            if f != 0:
                for j in idx:
                    A[i][j] -= f * A[piv][j]
    return True, rank


def short_vectors(Q, bound, limit=1):
    """Q positive definite integer matrix.  Enumerate non-zero integer x (up to sign) with x^T Q x <= bound.
    Exact Fincke-Pohst with Fractions.  Returns list of (value, x) (at most `limit`)."""
    res, why = ldl(Q)
    if res is None:
        raise ValueError("not positive definite")
    d, L = res
    n = len(Q)
    # x^T Q x = sum_i d_i (x_i + sum_{j>i} L[j][i] x_j)^2
    out = []
    x = [0] * n

    def isqrt_floor(fr):
        # floor(sqrt(fr)) for fr >= 0 rational
        if fr < 0:
            return -1
        num, den = fr.numerator, fr.denominator
        import math
        r = math.isqrt(num // den)
        while Fraction((r + 1) * (r + 1)) <= fr:
            r += 1
        while Fraction(r * r) > fr:
            r -= 1
        return r

    def rec(i, rem):
        if len(out) >= limit:
            return
        if i < 0:
            if any(x):
                # normalise sign: first non-zero from the top index positive -> count once
                for t in range(n - 1, -1, -1):
                    if x[t] != 0:
                        if x[t] > 0:
                            val = sum(x[a] * Q[a][b] * x[b] for a in range(n) for b in range(n))
                            out.append((val, list(x)))
                        break
            return
        c = sum(L[j][i] * x[j] for j in range(i + 1, n))
        # d_i (x_i + c)^2 <= rem
        r = rem / d[i]
        # x_i in [-c - sqrt(r), -c + sqrt(r)]
        import math
        # bounds: use integer search around -c
        centre = -c
        lo = math.floor(centre) - isqrt_floor(r) - 1
        hi = math.ceil(centre) + isqrt_floor(r) + 1
        for xi in range(lo, hi + 1):
            t = d[i] * (xi + c) * (xi + c)
            if t <= rem:
                x[i] = xi
                rec(i - 1, rem - t)
                x[i] = 0
                if len(out) >= limit:
                    return

    rec(n - 1, Fraction(bound))
    return out


def lattice_test(GW, cW, drop):
    """GW: integer Gram of the orbits in W, cW: 0/1 vector (1 on T), drop: index of one active orbit to
    eliminate (7p = sum_T f_i makes the generators dependent).
    Returns None if no violation found, or a tuple describing the violation:
       ('notPSD',) or ('short', value, k, n-vector)   with 0 < value <= 8."""
    m = len(GW)
    keep = [i for i in range(m) if i != drop]
    # generators: p (index 0) and f_i for i in keep
    Q = [[0] * (len(keep) + 1) for _ in range(len(keep) + 1)]
    Q[0][0] = 9
    for a, i in enumerate(keep):
        Q[0][a + 1] = Q[a + 1][0] = 7 * cW[i]
        for b, j in enumerate(keep):
            Q[a + 1][b + 1] = 7 * GW[i][j]
    ok, rank = psd_exact(Q)
    if not ok:
        return ("notPSD",)
    if rank < len(Q):
        return ("degenerate", rank)
    sv = short_vectors(Q, 8, limit=1)
    if sv:
        val, x = sv[0]
        n = [0] * m
        for a, i in enumerate(keep):
            n[i] = x[a + 1]
        return ("short", val, x[0], n)
    return None


def G_T_of(m, h):
    G = [[0] * 9 for _ in range(9)]
    for i in range(9):
        G[i][i] = 3 + (1 if i in h else 0)
        for j in range(9):
            if i != j and (m[i][j] & 1):
                G[i][j] = 1
    return G
