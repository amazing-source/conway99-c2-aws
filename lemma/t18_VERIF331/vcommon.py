"""Independent verifier for T18 / profile (3,3,1).  Common tools.
Written from the mathematical description only (T18_REPORT.md rounds 1-2, A8-A10).
Exact arithmetic: budgets in integers; PSD decided exactly
  - rejection: integer vector x with x^T M x < 0 (checked in Python ints), or exact charpoly sign test;
  - acceptance (when asked exact=True): exact characteristic polynomial (python-flint), Descartes sign rule.
M1 = 9(3I - A) + J  (= 63 E_{-4} on the full graph, so every principal submatrix is PSD);
M2 = 11(4I + A) - 2J (= 77 E_3), used when T18_MATS=2 (default).
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import itertools as it
import numpy as np
from flint import fmpz_mat

EDGE_TEXT = {
    0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
    1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
    2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}


def support_graph(g):
    B = np.zeros((9, 9), dtype=np.int64)
    for w in EDGE_TEXT[g].split():
        i, j = int(w[0]), int(w[1])
        assert i != j and B[i, j] == 0
        B[i, j] = B[j, i] = 1
    assert (B.sum(axis=0) == 4).all()
    return B


def automorphisms(B):
    n = len(B)
    out = []

    def rec(perm):
        k = len(perm)
        if k == n:
            out.append(tuple(perm))
            return
        for v in range(n):
            if v in perm:
                continue
            if all(B[k, a] == B[v, perm[a]] for a in range(k)):
                perm.append(v)
                rec(perm)
                perm.pop()
    rec([])
    return out


def deficient_pairs(B):
    """pairs {i,j} of S+ with exactly one common neighbour in S-; checks that every other pair has two."""
    C = B @ B
    D = []
    for i, j in it.combinations(range(9), 2):
        assert C[i, j] in (1, 2), "codegree outside {1,2}"
        if C[i, j] == 1:
            D.append((i, j))
    assert len(D) == 18
    return D


# ---------------------------------------------------------------- exact tests
def budgets_ok(A):
    """|N(u) n N(v)| <= 2 - A_uv for all u != v, inside the induced graph A."""
    C = A @ A + A
    np.fill_diagonal(C, 0)
    return bool((C <= 2).all())


def gram(A):
    n = len(A)
    return 27 * np.eye(n, dtype=np.int64) - 9 * A + 1


def exact_psd_charpoly(M):
    """exact: symmetric integer M is PSD iff (-1)^n p(-t) has no negative coefficient."""
    n = len(M)
    p = fmpz_mat([[int(v) for v in row] for row in M]).charpoly()
    co = [int(c) for c in p.coeffs()]
    co += [0] * (n + 1 - len(co))
    for k, c in enumerate(co):
        s = c if (n - k) % 2 == 0 else -c
        if s < 0:
            return False
    return True


STAT = {'float_rej_cert': 0, 'charpoly_calls': 0, 'float_acc': 0, 'charpoly_rej': 0, 'rej_by_M1': 0, 'rej_by_M2': 0}
# T18_MATS=1 : only M1 = 9(3I-A)+J  (= 63 E_{-4});   T18_MATS=2 (default): also M2 = 11(4I+A)-2J (= 77 E_3).
# Both are positive semidefinite on the full graph (A has eigenvalues 14, 3, -4 with multiplicities 1, 54, 44),
# hence on every induced subgraph.
MODE = int(os.environ.get('T18_MATS', '2'))
assert MODE in (1, 2)


def gram2(A):
    n = len(A)
    return 44 * np.eye(n, dtype=np.int64) + 11 * A - 2


def _psd_one(M, exact):
    w, V = np.linalg.eigh(M.astype(np.float64))
    if w[0] < -1e-7:
        v = V[:, 0]
        v = v / np.abs(v).max()
        for k in (6, 30, 200, 2000, 40000):
            x = np.rint(v * k).astype(np.int64)
            q = int(x @ M @ x)
            if q < 0:
                # recheck in Python integers
                xs = [int(t) for t in x]
                nz = [a for a in range(len(xs)) if xs[a]]
                qq = sum(xs[a] * int(M[a, b]) * xs[b] for a in nz for b in nz)
                assert qq == q and qq < 0
                STAT['float_rej_cert'] += 1
                return False
        STAT['charpoly_calls'] += 1
        r = exact_psd_charpoly(M)
        if not r:
            STAT['charpoly_rej'] += 1
        return r
    if w[0] > 1e-7 and not exact:
        STAT['float_acc'] += 1
        return True
    STAT['charpoly_calls'] += 1
    r = exact_psd_charpoly(M)
    if not r:
        STAT['charpoly_rej'] += 1
    return r


def psd_ok(A, exact=False):
    """Decide PSD of M1 (and of M2 when MODE = 2).  A False answer is always exact (integer vector x with
    x^T M x < 0 rechecked in Python integers, or exact characteristic polynomial).  A True answer is exact when
    exact=True or when the float spectrum was ambiguous; otherwise it is a float acceptance, which is never
    used as a proof of anything: accepting only continues the search."""
    if not _psd_one(gram(A), exact):
        STAT['rej_by_M1'] += 1
        return False
    if MODE == 2 and not _psd_one(gram2(A), exact):
        STAT['rej_by_M2'] += 1
        return False
    return True


# ---------------------------------------------------------------- vertex layout helpers
# Global labelling of the support: x_i -> i, y_i -> 9 + i  (i = 0..8).
def support_adj(B):
    A = np.zeros((18, 18), dtype=np.int64)
    A[:9, 9:] = B
    A[9:, :9] = B.T
    return A


class Builder:
    """Grow an induced graph vertex by vertex; each new vertex is given by its neighbours among the old ones."""

    def __init__(self, A, names):
        self.A = A.copy()
        self.names = list(names)
        self.idx = {n: k for k, n in enumerate(self.names)}

    def copy(self):
        return Builder(self.A, self.names)

    def add(self, name, nbr_names):
        n = len(self.A)
        A = np.zeros((n + 1, n + 1), dtype=np.int64)
        A[:n, :n] = self.A
        for m in nbr_names:
            k = self.idx[m]
            A[n, k] = A[k, n] = 1
        self.A = A
        self.idx[name] = n
        self.names.append(name)
