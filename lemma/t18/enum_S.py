# Step (a): enumerate all structures on S = S+ u S- (9 sigma-orbits) for T18.
# Exact integer arithmetic only.  No solver.
#
# Vertices: x_i = i (S+), y_i = sigma x_i = 9+i (S-), inf = 18.
# Orbit pair state for i<j:  0 none, 1 minus (x_i~y_j, x_j~y_i), 2 plus (x_i~x_j, y_i~y_j), 3 both.
# h-type orbit: x_i ~ y_i (the orbit lies in N(inf)); pattern (ii) has exactly two of them (orbits 7, 8).
# Constraints imposed:
#   * minus-degree(i) + [i is h] = plus-degree(i) + 4         (eigen-equation on S+)
#   * number of plus edges = e
#   * in the induced graph on S u {inf}: adjacent pairs have <= 1 common neighbour, non-adjacent <= 2
#   * pattern (ii): the two h orbits are not joined (a_c, b_c, a_c', b_c' induce 2K2), a word orbit is never
#     joined to an h orbit in state 3 (x never adjacent to both a_c and b_c)
#   * exact PSD test of 9(3I-A)+J  (= 63 E_{-4}) and 11(4I+A)-2J (= 77 E_3) on S u {inf}
#     (a rejection is certified by an integer vector with negative quadratic form, computed with Python ints)
# Output: isomorphism classes (permutations of the 9 orbits preserving h-flags), written to structures.json
import sys, json, itertools
import numpy as np

X = lambda i: i
Y = lambda i: 9 + i
INF = 18
PAIRS = [(i, j) for i in range(9) for j in range(i + 1, 9)]


def graph_of(state, h):
    """adjacency bitmasks on 19 vertices"""
    adj = [0] * 19
    def add(u, v):
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for (i, j), s in state.items():
        if s & 1:
            add(X(i), Y(j)); add(X(j), Y(i))
        if s & 2:
            add(X(i), X(j)); add(Y(i), Y(j))
    for i in h:
        add(X(i), Y(i)); add(INF, X(i)); add(INF, Y(i))
    return adj


def local_ok(adj, final=False):
    n = 19
    for u in range(n):
        au = adj[u]
        for v in range(u + 1, n):
            c = bin(au & adj[v]).count("1")
            if c > 2:
                return False
            if c > 1 and (au >> v) & 1:
                return False
    return True


def enumerate_structs(e_plus_edges, h, fixed=None):
    """e_plus_edges: list of orbit pairs that carry a plus edge (states 2 or 3 allowed there).
    h: tuple of h-type orbits.  fixed: dict pair -> forced state.  Yields dict pair->state."""
    fixed = fixed or {}
    plus_set = set(e_plus_edges)
    pdeg = [0] * 9
    for (i, j) in plus_set:
        pdeg[i] += 1; pdeg[j] += 1
    target = [pdeg[i] + 4 - (1 if i in h else 0) for i in range(9)]
    hs = set(h)
    state = {}
    mdeg = [0] * 9
    # remaining pairs count per orbit (for feasibility pruning)
    rem = [8] * 9
    out = []

    def options(p):
        i, j = p
        if p in fixed:
            return [fixed[p]]
        if i in hs and j in hs:
            return [0]
        if p in plus_set:
            if i in hs or j in hs:
                return [2]
            return [2, 3]
        return [0, 1]

    def rec(k):
        if k == len(PAIRS):
            adj = graph_of(state, h)
            if local_ok(adj):
                out.append(dict(state))
            return
        p = PAIRS[k]
        i, j = p
        for s in options(p):
            m = s & 1
            if mdeg[i] + m > target[i] or mdeg[j] + m > target[j]:
                continue
            if mdeg[i] + m + rem[i] - 1 < target[i] or mdeg[j] + m + rem[j] - 1 < target[j]:
                continue
            state[p] = s
            mdeg[i] += m; mdeg[j] += m; rem[i] -= 1; rem[j] -= 1
            ok = True
            if s:
                # cheap partial local check on the partial graph (counts only grow)
                adj = graph_of(state, h)
                for u in (X(i), X(j), Y(i), Y(j)):
                    au = adj[u]
                    for v in range(19):
                        if v == u:
                            continue
                        c = bin(au & adj[v]).count("1")
                        if c > 2 or (c > 1 and (au >> v) & 1):
                            ok = False; break
                    if not ok:
                        break
                # a word orbit has at most 2 neighbours in N(inf) (exactly 2 in Gamma)
                if ok and hs:
                    for w in (i, j):
                        if w not in hs:
                            cnt = 0
                            for c in hs:
                                q = (min(w, c), max(w, c))
                                if state.get(q, 0):
                                    cnt += 1
                            if cnt > 2:
                                ok = False
            if ok:
                rec(k + 1)
            mdeg[i] -= m; mdeg[j] -= m; rem[i] += 1; rem[j] += 1
            del state[p]

    rec(0)
    return out


def int_matrices(adj, n=19):
    A = [[(adj[u] >> v) & 1 for v in range(n)] for u in range(n)]
    M1 = [[9 * (3 * (u == v) - A[u][v]) + 1 for v in range(n)] for u in range(n)]     # 63 E_{-4}
    M2 = [[11 * (4 * (u == v) + A[u][v]) - 2 for v in range(n)] for u in range(n)]    # 77 E_3
    return A, M1, M2


def neg_certificate(M):
    """Return an integer vector v with v^T M v < 0 (exact), or None if none found by rounding eigenvectors."""
    Mf = np.array(M, dtype=float)
    w, V = np.linalg.eigh(Mf)
    if w[0] > -1e-7:
        return None
    for scale in (10, 100, 1000, 10 ** 5):
        v = [int(round(scale * t)) for t in V[:, 0]]
        q = sum(v[a] * M[a][b] * v[b] for a in range(len(v)) for b in range(len(v)))
        if q < 0:
            return v
    return None


def psd_filter(state, h):
    adj = graph_of(state, h)
    A, M1, M2 = int_matrices(adj)
    c1 = neg_certificate(M1)
    if c1 is not None:
        return ("E-4", c1)
    c2 = neg_certificate(M2)
    if c2 is not None:
        return ("E3", c2)
    return None


def mat_of(state):
    m = [[0] * 9 for _ in range(9)]
    for (i, j), s in state.items():
        m[i][j] = m[j][i] = s
    return m


def invariant(m, h):
    hs = set(h)
    rows = sorted((i in hs, tuple(sorted(m[i]))) for i in range(9))
    # second-order: for each orbit, sorted multiset of (state, neighbour row profile)
    prof = [(i in hs, tuple(sorted(m[i]))) for i in range(9)]
    rows2 = sorted((prof[i], tuple(sorted((m[i][j], prof[j]) for j in range(9) if j != i))) for i in range(9))
    A = np.array([[1 if (m[i][j] & 1) else 0 for j in range(9)] for i in range(9)], dtype=np.int64)
    P = np.array([[1 if (m[i][j] & 2) else 0 for j in range(9)] for i in range(9)], dtype=np.int64)
    tr = []
    Z = np.eye(9, dtype=np.int64)
    W = A + 3 * P
    for k in range(1, 8):
        Z = Z @ W
        tr.append(int(np.trace(Z)))
    return (tuple(rows), tuple(rows2), tuple(tr))


def isomorphic(m1, h1, m2, h2):
    hs1, hs2 = set(h1), set(h2)
    prof1 = [(i in hs1, tuple(sorted(m1[i]))) for i in range(9)]
    prof2 = [(i in hs2, tuple(sorted(m2[i]))) for i in range(9)]
    perm = [-1] * 9
    used = [False] * 9

    def rec(i):
        if i == 9:
            return True
        for t in range(9):
            if used[t] or prof1[i] != prof2[t]:
                continue
            ok = True
            for k in range(i):
                if m1[i][k] != m2[t][perm[k]]:
                    ok = False; break
            if ok:
                perm[i] = t; used[t] = True
                if rec(i + 1):
                    return True
                used[t] = False; perm[i] = -1
        return False

    return rec(0)


def dedupe(structs, h):
    buckets = {}
    reps = []
    for st in structs:
        m = mat_of(st)
        inv = invariant(m, h)
        lst = buckets.setdefault(inv, [])
        for r in lst:
            if isomorphic(m, h, r, h):
                break
        else:
            lst.append(m)
            reps.append(m)
    return reps


def run_case(name, plus_edges, h, fixed_list):
    allst = []
    for fixed in fixed_list:
        allst += enumerate_structs(plus_edges, h, fixed)
    n_lab = len(allst)
    reps = dedupe(allst, h)
    n_iso = len(reps)
    surv, killed = [], []
    for m in reps:
        st = {(i, j): m[i][j] for (i, j) in PAIRS}
        cert = psd_filter(st, h)
        if cert is None:
            surv.append(m)
        else:
            killed.append((m, cert))
    print(f"{name}: labelled (after symmetry breaking) {n_lab}, iso classes {n_iso}, "
          f"killed by exact PSD certificate {len(killed)}, surviving {len(surv)}")
    sys.stdout.flush()
    return {"name": name, "h": list(h), "plus_edges": [list(p) for p in plus_edges],
            "survivors": surv, "killed": [{"m": m, "which": c[0], "vector": c[1]} for m, c in killed]}


if __name__ == "__main__":
    res = []
    # ---- pattern (i), e = 0 : fix row 0 = minus to {1,2,3,4}
    fixed = {(0, j): (1 if j <= 4 else 0) for j in range(1, 9)}
    res.append(run_case("(i) e=0", [], (), [fixed]))
    # ---- pattern (ii), e = 0 : h = {7,8}; row 7 minus to words {0,1,2}; row 8 by overlap k
    fl = []
    for k in range(0, 4):
        f = {(j, 7): (1 if j <= 2 else 0) for j in range(7)}
        n8 = list(range(k)) + list(range(3, 3 + 3 - k))
        for j in range(7):
            f[(j, 8)] = 1 if j in n8 else 0
        fl.append(f)
    res.append(run_case("(ii) e=0", [], (7, 8), fl))
    # ---- pattern (i), e = 1 : plus edge on orbits (0,1) (state 2 or 3), no further symmetry breaking
    res.append(run_case("(i) e=1", [(0, 1)], (), [None]))
    # ---- pattern (ii), e = 1 : plus edge word-word (0,1), or word-h (0,7) meaning x_0 ~ a_7
    res.append(run_case("(ii) e=1 word-word", [(0, 1)], (7, 8), [None]))
    res.append(run_case("(ii) e=1 word-h", [(0, 7)], (7, 8), [None]))
    # ---- e = 2 (already excluded by counting, enumerated only as a cross-check of the S-level filters)
    res.append(run_case("(i) e=2 disjoint", [(0, 1), (2, 3)], (), [None]))
    res.append(run_case("(i) e=2 path", [(0, 1), (1, 2)], (), [None]))
    json.dump(res, open(__file__.replace("enum_S.py", "structures.json"), "w"))
    print("written structures.json")
