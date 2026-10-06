# T20: common tools.  Exact integer / rational arithmetic only.  No solver.
#
# S-structure (definition used by every script of this folder):
#   10 sigma-orbits i = 0..9, x_i = vertex i (phi = +1), y_i = sigma x_i = vertex 10+i (phi = -1), p = vertex 20.
#   Orbit pair state for i < j:  bit 1 = "minus": x_i ~ y_j and x_j ~ y_i;   bit 2 = "plus": x_i ~ x_j and y_i ~ y_j.
#   H = set of inner orbits: x_i ~ y_i, p ~ x_i, p ~ y_i.  p has no other neighbour in S.
# Conditions:
#   (E) eigen-equation on S+:  d-(x_i) = d+(x_i) + 4,  i.e.  minusdeg(i) + [i in H] = plusdeg(i) + 4;
#   (L) in the induced graph on S u {p} (21 vertices): adjacent pairs have <= 1 common neighbour,
#       non-adjacent pairs <= 2   (lambda = 1, mu = 2).
# Everything else (N(p) is a perfect matching, a word is never adjacent to both a_c and b_c, a word has at most
# two neighbours in N(p), ...) follows from (L) because p is in the vertex set.
from fractions import Fraction
from math import gcd
import itertools

N = 10
NV = 2 * N + 1
PV = 2 * N
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]


def X(i):
    return i


def Y(i):
    return N + i


def graph_of(state, H):
    """state: dict (i,j)->0..3 (missing = 0).  Returns list of adjacency bitmasks on 21 vertices."""
    adj = [0] * NV

    def add(u, v):
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for (i, j), s in state.items():
        if s & 1:
            add(X(i), Y(j)); add(X(j), Y(i))
        if s & 2:
            add(X(i), X(j)); add(Y(i), Y(j))
    for i in H:
        add(X(i), Y(i)); add(PV, X(i)); add(PV, Y(i))
    return adj


def local_ok(adj, n=NV):
    for u in range(n):
        au = adj[u]
        for v in range(u + 1, n):
            c = bin(au & adj[v]).count("1")
            if c > 2:
                return False
            if c > 1 and (au >> v) & 1:
                return False
    return True


def eigen_ok(state, H):
    m = [0] * N
    pl = [0] * N
    for (i, j), s in state.items():
        if s & 1:
            m[i] += 1; m[j] += 1
        if s & 2:
            pl[i] += 1; pl[j] += 1
    return all(m[i] + (1 if i in H else 0) == pl[i] + 4 for i in range(N))


def mat_of(state):
    m = [[0] * N for _ in range(N)]
    for (i, j), s in state.items():
        m[i][j] = m[j][i] = s
    return m


# ---------- exact positive semidefiniteness ----------

def psd_exact(Q):
    """Exact PSD test of a symmetric integer/rational matrix (symmetric elimination, Fractions).
    Returns (is_psd, rank)."""
    n = len(Q)
    A = [[Fraction(x) for x in row] for row in Q]
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


def int_matrices(adj, verts):
    """M1 = 9(3I-A)+J (= 63 E_{-4}),  M2 = 11(4I+A)-2J (= 77 E_3), restricted to the vertex list verts."""
    n = len(verts)
    A = [[(adj[verts[a]] >> verts[b]) & 1 for b in range(n)] for a in range(n)]
    M1 = [[9 * (3 * (a == b) - A[a][b]) + 1 for b in range(n)] for a in range(n)]
    M2 = [[11 * (4 * (a == b) + A[a][b]) - 2 for b in range(n)] for a in range(n)]
    return A, M1, M2


def neg_vector(Q):
    """An integer vector v with v^T Q v < 0 (checked with Python ints), for a symmetric integer matrix Q that is
    not PSD.  Exact: follows the elimination until a negative pivot (or a zero pivot with a non-zero row) appears
    and reconstructs the vector by back-substitution in Fractions, then clears denominators."""
    n = len(Q)
    A = [[Fraction(x) for x in row] for row in Q]
    # T tracks the congruence: current A = T^T Q T restricted to remaining indices (columns of T are vectors)
    T = [[Fraction(int(a == b)) for b in range(n)] for a in range(n)]   # T[:,i] = vector attached to index i
    idx = list(range(n))

    def finish(vec):
        den = 1
        for t in vec:
            den = den * t.denominator // gcd(den, t.denominator)
        v = [int(t * den) for t in vec]
        q = sum(v[a] * Q[a][b] * v[b] for a in range(n) for b in range(n))
        assert q < 0
        return v
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
                        # zero diagonals, non-zero off-diagonal: v = t_i - sign * t_j has form -2|A_ij| < 0
                        s = 1 if A[i][j] > 0 else -1
                        return finish([T[a][i] - s * T[a][j] for a in range(n)])
            return None
        # zero diagonal with non-zero entry against a positive pivot is handled later by the elimination:
        idx.remove(piv)
        pp = A[piv][piv]
        for i in idx:
            f = A[i][piv] / pp
            if f != 0:
                for a in range(n):
                    T[a][i] -= f * T[a][piv]
        # recompute the reduced block exactly from T (simple and safe)
        for i in idx:
            ti = [T[a][i] for a in range(n)]
            Qti = [sum(Q[a][b] * ti[b] for b in range(n)) for a in range(n)]
            for j in idx:
                A[i][j] = sum(T[a][j] * Qti[a] for a in range(n))
    return None


def psd_report(adj, verts):
    """Returns dict: for M1, M2: ('psd', rank) or ('neg', integer vector)."""
    A, M1, M2 = int_matrices(adj, verts)
    out = {}
    for name, M in (("M1", M1), ("M2", M2)):
        ok, rank = psd_exact(M)
        if ok:
            out[name] = ("psd", rank)
        else:
            v = neg_vector(M)
            q = sum(v[a] * M[a][b] * v[b] for a in range(len(v)) for b in range(len(v)))
            assert q < 0
            out[name] = ("neg", v, q)
    return out


# ---------- isomorphism of S-structures (permutations of the 10 orbits preserving H and all states) ----------

def profile(m, H):
    """vertex invariants (3 rounds of refinement), compressed to ints with hash() of int tuples.
    Only used to speed up the search: equal structures have equal profiles, the isomorphism test itself is exact."""
    hs = set(H)
    p = [hash((i in hs, tuple(sorted(m[i])))) for i in range(N)]
    for _ in range(2):
        p = [hash((p[i], tuple(sorted((m[i][j], p[j]) for j in range(N) if j != i)))) for i in range(N)]
    return p


def invariant(m, H):
    return tuple(sorted(profile(m, H)))


def _order(m):
    """an order of the orbits in which each new orbit is joined (state != 0) to an earlier one when possible"""
    order = []
    seen = [False] * N
    while len(order) < N:
        best = None
        for i in range(N):
            if seen[i]:
                continue
            sc = sum(1 for a in order if m[i][a])
            if best is None or sc > best[0]:
                best = (sc, i)
        order.append(best[1])
        seen[best[1]] = True
    return order


def iso_count(m1, H1, m2, H2, first_only=True, pr1=None, pr2=None):
    """number of isomorphisms m1 -> m2 (1 at most if first_only)."""
    if pr1 is None:
        pr1 = profile(m1, H1)
    if pr2 is None:
        pr2 = profile(m2, H2)
    if sorted(pr1) != sorted(pr2):
        return 0
    order = _order(m1)
    perm = [-1] * N
    used = [False] * N
    cnt = 0

    def rec(k):
        nonlocal cnt
        if k == N:
            cnt += 1
            return first_only
        i = order[k]
        for t in range(N):
            if used[t] or pr1[i] != pr2[t]:
                continue
            ok = True
            for q in range(k):
                a = order[q]
                if m1[i][a] != m2[t][perm[a]]:
                    ok = False
                    break
            if ok:
                perm[i] = t
                used[t] = True
                if rec(k + 1):
                    return True
                used[t] = False
                perm[i] = -1
        return False
    rec(0)
    return cnt


def classes(structs, H):
    """structs: list of state dicts (same H).  Returns list of [representative matrix, number of labelled members]."""
    buckets = {}
    for st in structs:
        m = mat_of(st)
        pr = profile(m, H)
        inv = tuple(sorted(pr))
        lst = buckets.setdefault(inv, [])
        for rec in lst:
            if iso_count(rec[0], H, m, H, pr1=rec[2], pr2=pr):
                rec[1] += 1
                break
        else:
            lst.append([m, 1, pr])
    out = []
    for inv in sorted(buckets):
        out.extend([r[0], r[1]] for r in buckets[inv])
    return out


def aut_order(m, H):
    return iso_count(m, H, m, H, first_only=False)


def edges_str(m, bit):
    return " ".join("%d%d" % (i, j) for i in range(N) for j in range(i + 1, N) if m[i][j] & bit)


def charpoly_int(M):
    """characteristic polynomial of an integer matrix (Faddeev-LeVerrier, exact).  Coefficients, leading first."""
    n = len(M)
    c = [Fraction(1)]
    Mk = [[Fraction(0)] * n for _ in range(n)]
    I = [[Fraction(int(a == b)) for b in range(n)] for a in range(n)]
    Mk = [row[:] for row in I]          # M_1 = I
    for k in range(1, n + 1):
        AM = [[sum(Fraction(M[a][t]) * Mk[t][b] for t in range(n)) for b in range(n)] for a in range(n)]
        ck = -sum(AM[a][a] for a in range(n)) / k
        c.append(ck)
        Mk = [[AM[a][b] + ck * I[a][b] for b in range(n)] for a in range(n)]
    return [int(t) for t in c]
