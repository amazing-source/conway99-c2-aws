"""P3/N25 supports: generation of valid supports and their boundary data.

Support S = P u N: P = {0, 1, 2} pairwise non-adjacent, N = {3, ..., 27}.  Conditions used (all are consequences of the
srg(99,14,1,2) axioms and of the eigen-equation (A + 4I)(1_P - 1_N) = -4.1):
  (E1) every p in P has exactly 8 neighbours in N;      (E2) every x in N has as many neighbours in P as in N;
  (L)  every edge of S is in at most one triangle of S;  no triangle inside N (a line inside N gives a class-4 vector of norm 166/9);
  (M)  two non-adjacent vertices of S have at most 2 common neighbours in S;
  (K)  the S-neighbourhood of every vertex induces a partial matching;      (C4) four vertices of N span at most 3 edges.
Boundary data: r(s, s') = (1 if adjacent else 2) - (common neighbours in S)  = number of OUTSIDE common neighbours,
               dZ(s) = 14 - deg_S(s) = number of outside neighbours.
usage: p3n25_support.py [seed] [count]      (random valid supports, printed as JSON lines)"""
import sys, json, random, itertools
P = [0, 1, 2]; N = list(range(3, 28)); S = P + N


def check(adj):
    """adj: list of sets (28).  Returns None if invalid, else dict of boundary data"""
    for p in P:
        if any(q in adj[p] for q in P): return None
        if len(adj[p]) != 8: return None
    for x in N:
        dp = sum(1 for p in P if p in adj[x]); dn = len(adj[x]) - dp
        if dp != dn: return None
    # no triangle inside N
    for x in N:
        nn = [w for w in adj[x] if w >= 3]
        for a, b in itertools.combinations(nn, 2):
            if b in adj[a]: return None
    r = {}
    for s, t in itertools.combinations(S, 2):
        c = len(adj[s] & adj[t])
        if t in adj[s]:
            if c > 1: return None
            r[(s, t)] = 1 - c
        else:
            if c > 2: return None
            r[(s, t)] = 2 - c
    # (K) partial matching in every S-neighbourhood
    for s in S:
        for a in adj[s]:
            if len(adj[a] & adj[s]) > 1: return None
    # (C4) four vertices of N span at most 3 edges: no 4-cycle in N (triangles are already excluded)
    for x, w in itertools.combinations(N, 2):
        if w not in adj[x] and len([v for v in adj[x] & adj[w] if v >= 3]) >= 2: return None
    dZ = {s: 14 - len(adj[s]) for s in S}
    return {"r": r, "dZ": dZ}


def invariants(adj):
    """Codex's quantities: t_p (edges inside N(p) inter N), delta, u"""
    t = []
    for p in P:
        nb = [x for x in adj[p]]
        t.append(sum(1 for a, b in itertools.combinations(nb, 2) if b in adj[a]))
    eN = sum(1 for x in N for w in adj[x] if w > x)
    delta = eN - sum(t)
    u = sum(len(adj[p] & adj[q]) for p, q in itertools.combinations(P, 2))
    codex = []
    for i, p in enumerate(P):
        others = [q for q in P if q != p]
        cs = [len(adj[p] & adj[q]) for q in others]
        X = sum(c * (c - 1) // 2 for c in cs)
        W = sum((lambda k: k * (k - 1) // 2)(len([v for v in adj[w] & adj[p] if v >= 3])) for w in N)
        codex.append(5 + 2 * sum(cs) - X - W - 3 * t[i])
    return {"t": t, "delta": delta, "u": u, "ell": codex}


def random_support(rng, tries=200000):
    for _ in range(tries):
        # 1. types: P-neighbourhood of each N-vertex
        cpair = {pq: rng.choice([0, 1, 2, 2]) for pq in itertools.combinations(P, 2)}
        types = []
        for pq, c in cpair.items(): types += [set(pq)] * c
        deg = [sum(1 for t in types if p in t) for p in P]
        if any(d > 8 for d in deg): continue
        for p in P: types += [{p}] * (8 - deg[p])
        if len(types) > 25: continue
        types += [set()] * (25 - len(types))
        rng.shuffle(types)
        adj = [set() for _ in range(28)]
        for i, t in enumerate(types):
            for p in t: adj[p].add(3 + i); adj[3 + i].add(p)
        need = {3 + i: len(t) for i, t in enumerate(types)}
        # 2. random graph on N with these degrees, triangle-free, built edge by edge with checks at the end
        stubs = [x for x in N for _ in range(need[x])]
        ok = False
        for _ in range(60):
            rng.shuffle(stubs); edges = set(); good = True
            for a, b in zip(stubs[::2], stubs[1::2]):
                if a == b or (min(a, b), max(a, b)) in edges: good = False; break
                edges.add((min(a, b), max(a, b)))
            if not good: continue
            adj2 = [set(s) for s in adj]
            for a, b in edges: adj2[a].add(b); adj2[b].add(a)
            data = check(adj2)
            if data is not None: ok = True; break
        if ok: return adj2, data
    return None, None


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rng = random.Random(seed); out = 0; seen = 0
    while out < count and seen < 400:
        adj, data = random_support(rng); seen += 1
        if adj is None: break
        inv = invariants(adj)
        if min(inv["ell"]) < 0 or not all(1 <= t <= 3 for t in inv["t"]): continue      # Codex's analytic filter (note 246)
        edges = sorted((a, b) for a in range(28) for b in adj[a] if b > a)
        print(json.dumps({"edges": edges, **inv}), flush=True); out += 1
