"""Symmetry reduction for the pairs of components with torsion in both (cases 22 and 23 of sweepX.py).
A balanced subspace B = graph of an injective map M from the torsion space E1 of the first component to the torsion space
E2 of the second one.  An automorphism g of the ball (it preserves each component; the three layers may be permuted, by
the same permutation in both components) sends a graph with B balanced to a graph with g(B) balanced, so "impossible"
is a property of the orbit of M: it is enough to run one map per orbit (at the same test vertex).
In coordinates: g.E1[k] = sum_j R1[k][j] E1[j], g.E2[l] = sum_m R2[l][m] E2[m], and g(B) = graph of R1^-1 M R2.
A layer-respecting automorphism is determined by the image of one vertex of each component (every vertex has exactly
one neighbour in each layer), so the group has at most 6 * 6 * 6 elements for components with three lines per layer."""
import itertools, random
from gen66 import torsion_vectors, nullspace7
from multi import make_ball


def component_maps(adj, lay, comp, which, sigma):
    """all maps of component `which` to itself that send layer l to layer sigma[l] and preserve adjacency"""
    idx = [v for v in range(36) if comp[v] == which]; v0 = idx[0]; out = []
    nb = lambda v, l: next(w for w in adj[v] if lay[w] == l)
    for w0 in idx:
        if lay[w0] != sigma[lay[v0]]: continue
        g = {v0: w0}; st = [v0]; ok = True
        while st and ok:
            v = st.pop()
            for l in range(3):
                v2 = nb(v, l); w2 = nb(g[v], sigma[l])
                if v2 in g:
                    if g[v2] != w2: ok = False; break
                else: g[v2] = w2; st.append(v2)
        if ok and len(g) == len(idx) and len(set(g.values())) == len(idx) and all((g[b] in adj[g[a]]) for a in idx for b in adj[a]):
            out.append(g)
    return out


def automorphisms(adj, lay, comp):
    out = []
    for sigma in itertools.permutations(range(3)):
        m0 = component_maps(adj, lay, comp, 0, sigma); m1 = component_maps(adj, lay, comp, 1, sigma)
        for g0 in m0:
            for g1 in m1:
                g = dict(g0); g.update(g1); out.append([g[v] for v in range(36)])
    return out


def coords(E, vec):
    t = len(E)
    for c in itertools.product(range(7), repeat=t):
        if all(sum(ci * e[v] for ci, e in zip(c, E)) % 7 == vec[v] for v in range(36)): return list(c)
    raise AssertionError("vector outside the torsion space")


def matinv(R):
    n = len(R); A = [[x % 7 for x in r] + [int(i == j) for j in range(n)] for i, r in enumerate(R)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c]); A[c], A[p] = A[p], A[c]
        iv = pow(A[c][c], -1, 7); A[c] = [(x * iv) % 7 for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]


def matmul(A, B):
    return [[sum(a * b for a, b in zip(r, col)) % 7 for col in zip(*B)] for r in A]


def orbit_reps(keys, maps):
    """maps: list of matrices (tuples of tuples).  Returns (group order, [(representative, orbit size)])"""
    adj, lay, comp = make_ball(keys, [(0, 1, 2)] * 2)
    E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
    G = automorphisms(adj, lay, comp); acts = []
    for g in G:
        inv = [0] * 36
        for v in range(36): inv[g[v]] = v
        push = lambda e: [e[inv[v]] for v in range(36)]            # (g.e)(v) = e(g^-1 v)
        R1 = [coords(E1, push(e)) for e in E1]; R2 = [coords(E2, push(e)) for e in E2]
        acts.append((matinv(R1), R2, g, inv))
    # check of the formula on random maps: the image of B by g is the graph of R1^-1 M R2
    rnd = random.Random(1)
    comb = lambda E, c: [sum(ci * e[v] for ci, e in zip(c, E)) % 7 for v in range(36)]
    for _ in range(40):
        M = rnd.choice(maps); R1i, R2, g, inv = rnd.choice(acts)
        Mp = matmul(matmul(R1i, [list(r) for r in M]), R2)
        B = [[(x + y) % 7 for x, y in zip(E1[k], comb(E2, M[k]))] for k in range(len(E1))]
        gB = [[b[inv[v]] for v in range(36)] for b in B]
        Bp = [[(x + y) % 7 for x, y in zip(E1[k], comb(E2, Mp[k]))] for k in range(len(E1))]
        rank = lambda rows: len(rows[0]) - len(nullspace7([r[:] for r in rows]))
        assert rank(gB + Bp) == len(E1), "action formula wrong"
    seen = set(); reps = []
    for M in maps:
        if M in seen: continue
        orb = set()
        for R1i, R2, g, inv in acts:
            orb.add(tuple(tuple(r) for r in matmul(matmul(R1i, [list(r) for r in M]), R2)))
        assert M in orb
        seen |= orb; reps.append((M, len(orb)))
    assert sum(s for _, s in reps) == len(maps)
    return len(G), reps


if __name__ == "__main__":
    from sweepX import TWO, THREE, KEY, rank2
    maps = [M for M in itertools.product(itertools.product(range(7), repeat=3), repeat=2) if rank2(M, 2, 3)]
    n, reps = orbit_reps([KEY[TWO[0]], KEY[THREE[0]]], maps)
    print("case 23: group order", n, "maps", len(maps), "orbits", len(reps), "orbit sizes", sorted(set(s for _, s in reps)))
    maps = [M for M in itertools.product(itertools.product(range(7), repeat=2), repeat=2) if (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % 7]
    n, reps = orbit_reps([KEY[TWO[0]], KEY[TWO[0]]], maps)
    print("case 22 (without the swap of the two components): group order", n, "maps", len(maps), "orbits", len(reps))
