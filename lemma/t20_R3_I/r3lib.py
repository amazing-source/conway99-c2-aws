# T20 round 3, case I (k = 0): common tools.  Exact rejections only.
#   vertices: x_i = i, y_i = 10 + i (i = 0..9), p = 20; further vertices are added in sigma-orbits (v, v+1).
#   B = the 4-regular "minus graph": x_i ~ y_j iff i ~_B j.  S+ and S- are independent, p has no neighbour in S.
import json, os, itertools
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPHS = ("I.0", "I.1", "I.2", "I.3", "I.4", "I.5")


def load_B(name):
    d = json.load(open(os.path.join(HERE, "structures_I.json")))
    case, idx = name.split(".")
    rec = d[case][int(idx)]
    assert rec["H"] == []
    m = [[int(v) & 1 for v in row] for row in rec["m"]]
    assert all(sum(r) == 4 for r in m) and all(m[i][i] == 0 for i in range(10))
    return m


def aut_group(m):
    """all permutations g of 0..9 with m[g i][g j] = m[i][j] (backtracking)"""
    out = []
    g = [-1] * 10
    used = [False] * 10

    def rec(k):
        if k == 10:
            out.append(tuple(g))
            return
        for t in range(10):
            if used[t]:
                continue
            if all(m[k][a] == m[t][g[a]] for a in range(k)):
                g[k] = t
                used[t] = True
                rec(k + 1)
                used[t] = False
                g[k] = -1
    rec(0)
    return out


def support(m, extra=0):
    A = np.zeros((21 + extra, 21 + extra), dtype=np.int64)
    for i in range(10):
        for j in range(10):
            if m[i][j]:
                A[i, 10 + j] = A[10 + j, i] = 1
    return A


def units_of(m):
    """deficient pairs {i,j} of S+ with multiplicity 2 - codeg_B(i,j) (number of common neighbours outside S)"""
    u = {}
    for i in range(10):
        for j in range(i + 1, 10):
            c = sum(m[i][k] * m[j][k] for k in range(10))
            assert c <= 2
            if c < 2:
                u[(i, j)] = 2 - c
    assert sum(u.values()) == 30
    return u


def sigma_of(n):
    s = list(range(n))
    for i in range(10):
        s[i], s[10 + i] = 10 + i, i
    for v in range(21, n, 2):
        s[v], s[v + 1] = v + 1, v
    return s


def budget_viol(A):
    """exact: some pair with more than 2 - [adjacent] common neighbours (valid on any spanning subgraph)"""
    C = A @ A + A
    np.fill_diagonal(C, 0)
    return bool((C > 2).any())


def qf(M, x):
    """x^T M x in Python integers"""
    n = len(x)
    nz = [a for a in range(n) if x[a]]
    tot = 0
    for a in nz:
        row = M[a]
        tot += x[a] * sum(int(row[b]) * x[b] for b in nz)
    return tot


def M1M2(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    return 9 * (3 * I - A) + 1, 11 * (4 * I + A) - 2


def exact_psd(Q):
    n = len(Q)
    A = [[Fraction(int(x)) for x in row] for row in Q]
    idx = list(range(n))
    while idx:
        for i in idx:
            if A[i][i] < 0:
                return False
        piv = None
        for i in idx:
            if A[i][i] > 0:
                piv = i
                break
        if piv is None:
            return all(A[i][j] == 0 for i in idx for j in idx)
        idx.remove(piv)
        p = A[piv][piv]
        for i in idx:
            f = A[i][piv] / p
            if f != 0:
                for j in idx:
                    A[i][j] -= f * A[piv][j]
    return True


SCALES = (1, 2, 3, 4, 6, 12, 30, 60, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10)


def psd_viol(A, tol=1e-7):
    """None = kept (FLOAT decision, proves nothing).  Otherwise an EXACT rejection (name, x, q):
    x integer vector, q = x^T M x < 0 evaluated in Python integers, M = M1 = 9(3I-A)+J or M2 = 11(4I+A)-2J on the
    whole (completely known) vertex set of A; x = None when decided by exact rational elimination."""
    M1, M2 = M1M2(A)
    for name, M in (("M1", M1), ("M2", M2)):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] >= -tol:
            continue
        v = V[:, 0]
        mx = float(np.max(np.abs(v)))
        Ml = M.tolist()
        for sc in SCALES:
            x = [int(round(float(t) * sc / mx)) for t in v]
            if not any(x):
                continue
            q = qf(Ml, x)
            if q < 0:
                return (name, x, q)
        if not exact_psd(Ml):
            return (name, None, None)
    return None


def check_cert(A, cert):
    """independent re-evaluation of a certificate (name, x, q) with Python integers from the 0/1 matrix A"""
    name, x, q = cert
    n = len(A)
    tot = 0
    sx = sum(x)
    for a in range(n):
        if not x[a]:
            continue
        ra = A[a]
        s = sum(x[b] for b in range(n) if ra[b])
        if name == "M1":
            tot += x[a] * (27 * x[a] - 9 * s + sx)
        else:
            tot += x[a] * (44 * x[a] + 11 * s - 2 * sx)
    return tot == q and tot < 0
