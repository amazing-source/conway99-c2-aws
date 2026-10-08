"""Triangle-free components (m = 2, 3) by type of 4-cycles.  A 4-cycle of G(T) is either
  type I : mate, transversal, mate, transversal  (two lines through two points of T joined by a matching = a prism of
           Gamma through an edge of T), or
  type II: one mate edge and three transversal edges.
With P = 0 (no prism anywhere in Gamma) only type II can occur."""
import itertools, collections
from multi import matchings, build, ok_tf
for m in (2, 3):
    n = 2 * m
    def inv(mm):
        v = [0] * n
        for a, b in mm: v[a] = b; v[b] = a
        return tuple(v)
    ms = [inv(x) for x in matchings(range(n))]; iota = ms[0]
    tot = noI = g5 = 0
    for t1 in ms:
        for t2 in ms:
            for pi in itertools.permutations(range(n)):
                adj = build((iota, t1, t2, pi))
                if not ok_tf(adj): continue
                tot += 1
                lay = lambda v: v // n
                mate = [next(z for z in adj[v] if lay(z) == lay(v)) for v in range(3 * n)]
                typeI = False; any4 = False
                for w in range(3 * n):
                    for z in range(w + 1, 3 * n):
                        if z not in adj[w] and len(adj[w] & adj[z]) == 2: any4 = True
                    x = mate[w]
                    for y in adj[w]:
                        if lay(y) != lay(w) and mate[y] in adj[x]: typeI = True
                if not typeI: noI += 1
                if not any4: g5 += 1
    print(f"m = {m}: triangle-free normal forms {tot}; without type-I 4-cycle {noI}; girth >= 5: {g5}")
