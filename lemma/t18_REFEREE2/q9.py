# Referee 2: independent enumeration of the 4-regular graphs on 9 vertices.
# No code from the repository. Pure Python.
import sys, itertools, math
from collections import defaultdict

N = 9
K = 4

# ---------- 1. all labelled 4-regular graphs on 9 vertices (count), by rows ----------
def gen_all():
    """yield adjacency as tuple of 9 bitmasks. Vertex v chooses its neighbours among w>v."""
    adj = [0] * N
    deg = [0] * N

    def rec(v):
        if v == N:
            yield tuple(adj)
            return
        need = K - deg[v]
        if need < 0:
            return
        cand = [w for w in range(v + 1, N) if deg[w] < K]
        if len(cand) < need:
            return
        for comb in itertools.combinations(cand, need):
            for w in comb:
                adj[v] |= 1 << w
                adj[w] |= 1 << v
                deg[w] += 1
            deg[v] += need
            # quick feasibility: remaining vertices must be able to complete
            ok = True
            rem = [K - deg[w] for w in range(v + 1, N)]
            # each remaining vertex w needs rem[w] neighbours among other remaining vertices with rem>0
            pos = sum(1 for r in rem if r > 0)
            for r in rem:
                if r > 0 and r > pos - 1:
                    ok = False
                    break
            if ok and sum(rem) % 2 == 0:
                yield from rec(v + 1)
            deg[v] -= need
            for w in comb:
                adj[v] &= ~(1 << w)
                adj[w] &= ~(1 << v)
                deg[w] -= 1

    yield from rec(0)

def popcount(x):
    return bin(x).count("1")

def codegs(adj):
    return [[popcount(adj[i] & adj[j]) for j in range(N)] for i in range(N)]

def maxcodeg(adj):
    m = 0
    for i in range(N):
        for j in range(i + 1, N):
            c = popcount(adj[i] & adj[j])
            if c > m:
                m = c
    return m

def mincodeg(adj):
    m = 99
    for i in range(N):
        for j in range(i + 1, N):
            c = popcount(adj[i] & adj[j])
            if c < m:
                m = c
    return m

def invariant(adj):
    # per-vertex: sorted list of (adjacent?, codegree) to the others; plus triangles
    per = []
    for i in range(N):
        l = []
        for j in range(N):
            if j == i:
                continue
            l.append(((adj[i] >> j) & 1, popcount(adj[i] & adj[j])))
        per.append(tuple(sorted(l)))
    return tuple(sorted(per))

def iso_count(a, b, count_all=False):
    """number of isomorphisms a -> b (backtracking); if not count_all return 1 as soon as one is found."""
    va = []
    for i in range(N):
        l = sorted(((a[i] >> j) & 1, popcount(a[i] & a[j])) for j in range(N) if j != i)
        va.append(tuple(l))
    vb = []
    for i in range(N):
        l = sorted(((b[i] >> j) & 1, popcount(b[i] & b[j])) for j in range(N) if j != i)
        vb.append(tuple(l))
    img = [-1] * N
    used = [False] * N
    cnt = 0

    def rec(i):
        nonlocal cnt
        if i == N:
            cnt += 1
            return not count_all
        for t in range(N):
            if used[t] or va[i] != vb[t]:
                continue
            ok = True
            for j in range(i):
                if ((a[i] >> j) & 1) != ((b[t] >> img[j]) & 1):
                    ok = False
                    break
            if ok:
                img[i] = t
                used[t] = True
                if rec(i + 1):
                    return True
                used[t] = False
                img[i] = -1
        return False

    rec(0)
    return cnt

def connected(adj):
    seen = 1
    stack = [0]
    while stack:
        v = stack.pop()
        m = adj[v] & ~seen
        while m:
            w = (m & -m).bit_length() - 1
            m &= m - 1
            seen |= 1 << w
            stack.append(w)
    return seen == (1 << N) - 1

def main():
    total = 0
    total_le2 = 0
    buckets = defaultdict(list)   # invariant -> list of (rep, labelled count)
    nclass_hits = 0
    for adj in gen_all():
        total += 1
        if maxcodeg(adj) <= 2:
            total_le2 += 1
        inv = invariant(adj)
        lst = buckets[inv]
        found = False
        for ent in lst:
            if iso_count(adj, ent[0]) == 1:
                ent[1] += 1
                found = True
                break
        if not found:
            lst.append([adj, 1])
    print("labelled 4-regular graphs on 9 vertices:", total)
    print("labelled with all codegrees <= 2      :", total_le2)
    classes = []
    for inv, lst in buckets.items():
        for rep, c in lst:
            classes.append((rep, c))
    print("isomorphism classes:", len(classes))
    print("invariant buckets  :", len(buckets))
    tot2 = 0
    f9 = math.factorial(9)
    classes.sort(key=lambda rc: (maxcodeg(rc[0]), -rc[1]))
    for rep, c in classes:
        aut = iso_count(rep, rep, count_all=True)
        edges = [(i, j) for i in range(N) for j in range(i + 1, N) if (rep[i] >> j) & 1]
        tri = sum(1 for i in range(N) for j in range(i + 1, N) for k in range(j + 1, N)
                  if (rep[i] >> j) & 1 and (rep[i] >> k) & 1 and (rep[j] >> k) & 1)
        print("class: labelled=%7d  |Aut|=%4d  9!/|Aut|=%7d  %s  maxcodeg=%d mincodeg=%d triangles=%d connected=%s edges=%s"
              % (c, aut, f9 // aut, "OK" if c == f9 // aut else "MISMATCH", maxcodeg(rep), mincodeg(rep), tri,
                 connected(rep), " ".join("%d%d" % e for e in edges)))
        tot2 += f9 // aut
    print("sum 9!/|Aut| =", tot2)
    # pairwise non-isomorphism of the representatives (exhaustive)
    bad = 0
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            if iso_count(classes[i][0], classes[j][0]) != 0:
                bad += 1
    print("pairs of representatives found isomorphic (must be 0):", bad)

    # compare with the three graphs printed in the document
    doc = {
        "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
        "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
        "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
    }
    le2 = [rc for rc in classes if maxcodeg(rc[0]) <= 2]
    print("classes with all codegrees <= 2:", len(le2))
    for name, s in doc.items():
        adj = [0] * N
        for e in s.split():
            i, j = int(e[0]), int(e[1])
            adj[i] |= 1 << j
            adj[j] |= 1 << i
        adj = tuple(adj)
        assert all(popcount(x) == 4 for x in adj), name
        hits = [idx for idx, rc in enumerate(le2) if iso_count(adj, rc[0]) == 1]
        print(name, "is isomorphic to codeg<=2 class number(s)", hits, " labelled size", [le2[h][1] for h in hits])

if __name__ == "__main__":
    main()
