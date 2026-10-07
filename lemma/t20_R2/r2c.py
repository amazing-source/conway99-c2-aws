# T20 round 2: common tools.  Exact integer / rational arithmetic for every rejection.  No solver.
#
# Vertices of the base graph (S u {p}, 21 vertices): x_i = i (phi = +1), y_i = 10 + i (phi = -1), p = 20.
# Orbit pair state m[i][j] (i != j): bit 1 = minus (x_i ~ y_j, x_j ~ y_i), bit 2 = plus (x_i ~ x_j, y_i ~ y_j).
# H = inner orbits (x_i ~ y_i, p ~ x_i, p ~ y_i).
import json, os, sys, time, itertools
from fractions import Fraction
from math import gcd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 10
PV = 20


def load_structs():
    d = {}
    for fn in ("structures_I.json", "structures_III_IIb_IIa.json"):
        d.update(json.load(open(os.path.join(HERE, fn))))
    out = {}
    for i, rec in enumerate(d["I"]):
        out["I.%d" % i] = (rec["m"], rec["H"])
    for i, rec in enumerate(d["IIa"]):
        out["IIa.%d" % i] = (rec["m"], rec["H"])
    for i, rec in enumerate(d["III"]):
        out["III.%d" % i] = (rec["m"], rec["H"])
    return out


def base_graph(m, H):
    A = np.zeros((21, 21), dtype=np.int64)

    def add(u, v):
        A[u, v] = 1
        A[v, u] = 1
    for i in range(N):
        for j in range(i + 1, N):
            if m[i][j] & 1:
                add(i, 10 + j); add(j, 10 + i)
            if m[i][j] & 2:
                add(i, j); add(10 + i, 10 + j)
    for i in H:
        add(i, 10 + i); add(PV, i); add(PV, 10 + i)
    return A


def check_base(A, H):
    """sanity: eigen-equation on S, lambda/mu caps"""
    phi = np.array([1] * 10 + [-1] * 10 + [0])
    r = A @ phi
    assert all(r[i] == -4 * phi[i] for i in range(20)), "eigen-equation fails"
    assert budgets_ok(A)


# ---------------- exact tests ----------------

def budgets_ok(A):
    """every pair u != v of the (induced, completely known) graph has at most 2 - A[u,v] common neighbours"""
    C = A @ A
    V = C > (2 - A)
    np.fill_diagonal(V, False)
    return not V.any()


def budget_violation(A):
    C = A @ A
    V = C > (2 - A)
    np.fill_diagonal(V, False)
    if V.any():
        u, v = np.argwhere(V)[0]
        return int(u), int(v), int(C[u, v]), int(A[u, v])
    return None


def M1_of(A):
    n = A.shape[0]
    return 9 * (3 * np.eye(n, dtype=np.int64) - A) + 1


def M2_of(A):
    n = A.shape[0]
    return 11 * (4 * np.eye(n, dtype=np.int64) + A) - 2


def qform_exact(M, x):
    """x^T M x in Python integers"""
    n = len(x)
    xs = [int(t) for t in x]
    tot = 0
    for a in range(n):
        if xs[a] == 0:
            continue
        row = M[a]
        s = 0
        for b in range(n):
            if xs[b]:
                s += int(row[b]) * xs[b]
        tot += xs[a] * s
    return tot


SCALES = (3, 6, 12, 30, 100, 300, 1000, 10000, 100000, 10 ** 6, 10 ** 8, 10 ** 10)


def cert_from_vec(M, v):
    """integer vector x with x^T M x < 0 (exact), built from an approximate eigenvector v; None if not found"""
    mx = float(np.max(np.abs(v)))
    if mx == 0:
        return None
    for sc in SCALES:
        x = np.rint(v * (sc / mx)).astype(np.int64)
        if not x.any():
            continue
        # fast exact evaluation in int64 (no overflow: |x| <= 1e10 only for the last scales, use Python ints there)
        if sc <= 10 ** 6:
            q = int(x @ (M @ x))
            if q < 0:
                q2 = qform_exact(M, x)
                assert q2 == q
                return [int(t) for t in x], q2
        else:
            q2 = qform_exact(M, x)
            if q2 < 0:
                return [int(t) for t in x], q2
    return None


def psd_exact(Q):
    """exact PSD decision by symmetric rational elimination.  Returns (is_psd, rank)."""
    n = len(Q)
    A = [[Fraction(int(x)) for x in row] for row in Q]
    idx = list(range(n))
    rank = 0
    while idx:
        for i in idx:
            if A[i][i] < 0:
                return False, None
        piv = None
        for i in idx:
            if A[i][i] > 0:
                piv = i
                break
        if piv is None:
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


def neg_vector_exact(Q):
    """integer vector with negative form for a non-PSD symmetric integer matrix (exact elimination)."""
    n = len(Q)
    Qi = [[int(x) for x in row] for row in Q]
    A = [[Fraction(x) for x in row] for row in Qi]
    T = [[Fraction(int(a == b)) for b in range(n)] for a in range(n)]
    idx = list(range(n))

    def finish(vec):
        den = 1
        for t in vec:
            den = den * t.denominator // gcd(den, t.denominator)
        v = [int(t * den) for t in vec]
        q = sum(v[a] * Qi[a][b] * v[b] for a in range(n) for b in range(n))
        assert q < 0
        return v, q
    while idx:
        for i in idx:
            if A[i][i] < 0:
                return finish([T[a][i] for a in range(n)])
        piv = None
        for i in idx:
            if A[i][i] > 0:
                piv = i
                break
        if piv is None:
            for i in idx:
                for j in idx:
                    if A[i][j] != 0:
                        s = 1 if A[i][j] > 0 else -1
                        return finish([T[a][i] - s * T[a][j] for a in range(n)])
            return None
        idx.remove(piv)
        pp = A[piv][piv]
        for i in idx:
            f = A[i][piv] / pp
            if f != 0:
                for a in range(n):
                    T[a][i] -= f * T[a][piv]
                for j in idx:
                    A[i][j] -= f * A[piv][j]
    return None


class Stats:
    def __init__(self):
        self.c = {}

    def add(self, k, n=1):
        self.c[k] = self.c.get(k, 0) + n

    def __repr__(self):
        return ", ".join("%s=%d" % (k, self.c[k]) for k in sorted(self.c))


TOL = 1e-7
STATS = Stats()
CERT_SINK = None       # optional file object: certificates are appended as json lines (capped by CERT_CAP)
CERT_CAP = 0
_ncert = 0


def psd_reject(A, tag=""):
    """Returns None if no violation is found (float-based 'kept'), or (matrix name, x, q) with x^T M x = q < 0 exact."""
    global _ncert
    for name, M in (("M1", M1_of(A)), ("M2", M2_of(A))):
        w, v = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -TOL:
            c = cert_from_vec(M, v[:, 0])
            if c is None:
                ok, _ = psd_exact(M.tolist())
                if ok:
                    STATS.add("float_negative_but_exactly_psd")
                    continue
                c = neg_vector_exact(M.tolist())
                STATS.add("cert_by_exact_elimination")
            STATS.add("psd_reject_" + name)
            if CERT_SINK is not None and _ncert < CERT_CAP:
                _ncert += 1
                CERT_SINK.write(json.dumps({"tag": tag, "M": name, "A": ["".join(map(str, r)) for r in A.tolist()],
                                            "x": c[0], "q": c[1]}) + "\n")
            return name, c[0], c[1]
    return None


def psd_exact_report(A):
    """exact: for M1 and M2 returns (is_psd, rank)"""
    return psd_exact(M1_of(A).tolist()), psd_exact(M2_of(A).tolist())


# ---------------- rank bound ----------------

def odd_gram(A, reps, sig):
    """G = 3I - A[R,R] + A[R,sigma R]   (sigma-odd part of 3I - A on the orbits with representatives reps)"""
    R = list(reps)
    SR = [sig[r] for r in R]
    n = len(R)
    G = 3 * np.eye(n, dtype=np.int64) - A[np.ix_(R, R)] + A[np.ix_(R, SR)]
    return G


def even_M1(A, reps, sig, fixed):
    """even part of M1 = 9(3I-A)+J on generators e_f (f fixed) and e_v + e_{sigma v}"""
    M = M1_of(A)
    gens = []
    n = A.shape[0]
    for f in fixed:
        g = np.zeros(n, dtype=np.int64); g[f] = 1; gens.append(g)
    for r in reps:
        g = np.zeros(n, dtype=np.int64); g[r] = 1; g[sig[r]] = 1; gens.append(g)
    Gm = np.array(gens)
    return Gm @ M @ Gm.T


def rank_exact(M):
    import flint
    return flint.fmpz_mat([[int(x) for x in row] for row in M.tolist()]).rank()


def det_exact(M):
    import flint
    return int(flint.fmpz_mat([[int(x) for x in row] for row in M.tolist()]).det())


def rank_mod_p(M, p=1000003):
    """rank over GF(p) (a lower bound of the rank over Q); independent of flint"""
    a = [[int(x) % p for x in row] for row in M.tolist()]
    n = len(a); mcol = len(a[0]) if n else 0
    r = 0
    for c in range(mcol):
        piv = None
        for i in range(r, n):
            if a[i][c]:
                piv = i; break
        if piv is None:
            continue
        a[r], a[piv] = a[piv], a[r]
        inv = pow(a[r][c], p - 2, p)
        a[r] = [(t * inv) % p for t in a[r]]
        for i in range(n):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(s - f * t) % p for s, t in zip(a[i], a[r])]
        r += 1
        if r == n:
            break
    return r
