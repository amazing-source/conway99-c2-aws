# t18_B2 / rankbound.py -- the rank bound P2 of lemma/t18_STRUCT/REPORT.md, section 2, as an exact test (own code).
# 27I - 9A + J = 63 E_{-4} has rank 44 and sigma splits its eigenspace 22 + 22 (trace sigma = 1, trace sigma A = 14).
# So for a sigma-invariant determined vertex set: the odd Gram 3I - A^ on its orbits has rank <= 22, and the even part of
# 27I - 9A + J (orbits, plus p if present) has rank <= 22.
# Functions take a 0/1 adjacency (list of bitmask rows), the list of orbit representatives and sigma.
from fractions import Fraction


def bareiss_det(M):
    n = len(M)
    A = [[int(x) for x in r] for r in M]
    sign = 1; prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if A[i][k] != 0), None)
            if sw is None:
                return 0
            A[k], A[sw] = A[sw], A[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def rank_exact(M):
    A = [[Fraction(int(x)) for x in r] for r in M]
    n = len(A); m = len(A[0]) if A else 0
    rank = 0
    for c in range(m):
        piv = next((i for i in range(rank, n) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        for i in range(rank + 1, n):
            if A[i][c] != 0:
                f = A[i][c] / A[rank][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[rank])]
        rank += 1
    return rank


def odd_gram(rows, reps, sig):
    """Gram matrix 3I - A^ of the orbits {x, sigma x}, x in reps:  A^_{OO'} = A_xy - A_{x, sigma y},  A^_{OO} = -A_{x, sigma x}"""
    a = lambda u, v: (rows[u] >> v) & 1
    return [[(3 + a(x, sig[x])) if x == y else -(a(x, y) - a(x, sig[y])) for y in reps] for x in reps]


def even_part(rows, reps, sig, fixed=None):
    """even part of 27I - 9A + J on the vectors e_x + e_{sigma x} (x in reps) and e_p (if fixed is given)"""
    def m(u, v):
        return (27 if u == v else 0) - 9 * ((rows[u] >> v) & 1) + 1
    vecs = [(x, sig[x]) for x in reps] + ([(fixed,)] if fixed is not None else [])
    return [[sum(m(u, v) for u in U for v in V) for V in vecs] for U in vecs]
