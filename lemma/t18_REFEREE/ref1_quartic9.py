# Referee check 1 (independent of every script of the repo).
# All labelled 4-regular graphs on 9 vertices, their isomorphism classes, and the classes with all codegrees <= 2.
# Claims tested:  (a) there are 16 classes, all connected (sanity of this enumerator);
#                 (b) exactly 3 classes have max codegree <= 2, with 55440 labelled graphs = 9!/72 + 9!/12 + 9!/18;
#                 (c) they are the graphs B0, B1, B2 printed in T18_REPORT.md; none has a pair of codegree 0.
import itertools, sys, time
import numpy as np

N = 9
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
PIDX = {p: k for k, p in enumerate(PAIRS)}

def enum_regular(deg=4):
    """Backtracking row by row: for vertex v choose its neighbours among the larger vertices."""
    out = []
    adj = [0] * N          # bitmask
    need = [deg] * N
    def rec(v):
        if v == N:
            out.append(tuple(adj))
            return
        r = need[v]
        cand = [u for u in range(v + 1, N) if need[u] > 0]
        if r > len(cand):
            return
        for comb in itertools.combinations(cand, r):
            for u in comb:
                adj[v] |= 1 << u; adj[u] |= 1 << v; need[u] -= 1
            need[v] = 0
            rec(v + 1)
            need[v] = r
            for u in comb:
                adj[v] &= ~(1 << u); adj[u] &= ~(1 << v); need[u] += 1
    rec(0)
    return out

def code(adj):
    c = 0
    for k, (i, j) in enumerate(PAIRS):
        if adj[i] >> j & 1:
            c |= 1 << k
    return c

def decode(c):
    return [PAIRS[k] for k in range(36) if c >> k & 1]

def maxcodeg(adj):
    return max(bin(adj[i] & adj[j]).count("1") for i, j in PAIRS)

def mincodeg(adj):
    return min(bin(adj[i] & adj[j]).count("1") for i, j in PAIRS)

def connected(adj):
    seen = 1; front = 1
    while front:
        nxt = 0
        for v in range(N):
            if front >> v & 1:
                nxt |= adj[v]
        front = nxt & ~seen
        seen |= nxt
    return seen == (1 << N) - 1

t0 = time.time()
G = enum_regular(4)
print("labelled 4-regular graphs on 9 vertices:", len(G), f"({time.time()-t0:.1f}s)")
codes = {code(a): a for a in G}
assert len(codes) == len(G)

perms = np.array(list(itertools.permutations(range(N))), dtype=np.int64)   # 362880 x 9
# pair index table for (min,max)
PT = np.zeros((N, N), dtype=np.int64)
for (i, j), k in PIDX.items():
    PT[i, j] = k; PT[j, i] = k

def orbit(c):
    e = decode(c)
    acc = np.zeros(len(perms), dtype=np.int64)
    for (i, j) in e:
        acc |= np.left_shift(np.int64(1), PT[perms[:, i], perms[:, j]])
    return acc

remaining = set(codes)
classes = []
while remaining:
    c = min(remaining)
    orb = orbit(c)
    uo = set(int(x) for x in np.unique(orb))
    assert uo <= remaining, "orbit leaves the set of 4-regular graphs?"
    aut = len(perms) // len(uo)
    assert aut * len(uo) == len(perms)
    remaining -= uo
    classes.append((c, len(uo), aut))
print("isomorphism classes:", len(classes))
tot = 0
good = []
for c, size, aut in classes:
    adj = codes[c]
    mc = maxcodeg(adj); mn = mincodeg(adj)
    A = np.zeros((N, N), dtype=np.int64)
    for i, j in decode(c):
        A[i, j] = A[j, i] = 1
    tri = int(np.trace(A @ A @ A)) // 6
    cod = A @ A
    hist_adj = sorted(int(cod[i, j]) for i, j in PAIRS if A[i, j])
    hist_non = sorted(int(cod[i, j]) for i, j in PAIRS if not A[i, j])
    ev = np.round(np.linalg.eigvalsh(A.astype(float)), 4)
    print(f"  class |orbit|={size:6d} |Aut|={aut:4d} connected={connected(adj)} triangles={tri:2d} max codeg={mc} min codeg={mn}",
          "  <-- codeg<=2" if mc <= 2 else "")
    tot += size
    if mc <= 2:
        good.append((c, size, aut, tri, hist_adj, hist_non, ev))
print("sum of orbit sizes:", tot)
print()
print("classes with all codegrees <= 2:", len(good), " labelled:", sum(g[1] for g in good))

# the three graphs of the report
REP = {
 "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
 "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
 "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}
def code_from_str(s):
    c = 0
    for w in s.split():
        i, j = int(w[0]), int(w[1])
        c |= 1 << PIDX[(min(i, j), max(i, j))]
    return c
orbs = {}
for c, size, aut, tri, ha, hn, ev in good:
    orbs[c] = set(int(x) for x in np.unique(orbit(c)))
for name, s in REP.items():
    c = code_from_str(s)
    assert c in codes, name + " is not 4-regular"
    hit = [g for g in good if c in orbs[g[0]]]
    assert len(hit) == 1, name + " not among the codeg<=2 classes"
    g = hit[0]
    from collections import Counter
    print(f"{name}: |Aut|={g[2]} triangles={g[3]} codeg(adjacent)={dict(Counter(g[4]))} codeg(non-adjacent)={dict(Counter(g[5]))}")
    print(f"     spectrum {list(g[6])}")
    print(f"     deficient pairs (codeg 1): {len([1 for x in g[4]+g[5] if x==1])}, pairs of codeg 0: {len([1 for x in g[4]+g[5] if x==0])}")
names_hit = set()
for name, s in REP.items():
    c = code_from_str(s)
    for g in good:
        if c in orbs[g[0]]:
            names_hit.add(g[0])
print("the three report graphs are pairwise non-isomorphic and exhaust the list:", len(names_hit) == 3 == len(good))

# K3xK3 and C9(1,2) identification
def circ(S):
    c = 0
    for i in range(9):
        for s in S:
            j = (i + s) % 9
            c |= 1 << PIDX[(min(i, j), max(i, j))]
    return c
def k3k3():
    c = 0
    for a in range(9):
        for b in range(a + 1, 9):
            if (a // 3 == b // 3) or (a % 3 == b % 3):
                c |= 1 << PIDX[(a, b)]
    return c
for nm, cc in (("C9(1,2)", circ((1, 2))), ("K3xK3", k3k3())):
    for name, s in REP.items():
        c = code_from_str(s)
        g = [g for g in good if c in orbs[g[0]]][0]
        if cc in orbs[g[0]]:
            print(nm, "is isomorphic to", name)
