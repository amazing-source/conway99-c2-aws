"""Components with m = 1 or 2 lines per layer (6 or 12 vertices) of girth >= 5: none?  (normal form as in comp66.py)"""
import itertools
def matchings(e):
    e = list(e)
    if not e: yield (); return
    a = e[0]
    for b in e[1:]:
        for m in matchings([x for x in e if x not in (a, b)]): yield ((a, b),) + m
for m in (1, 2):
    n = 2 * m; cnt = tot = 0
    def inv(mm):
        v = [0] * n
        for a, b in mm: v[a] = b; v[b] = a
        return v
    ms = [inv(x) for x in matchings(range(n))]
    for iota in ms[:1]:
        for t1 in ms:
            for t2 in ms:
                for pi in itertools.permutations(range(n)):
                    tot += 1
                    adj = [set() for _ in range(3 * n)]
                    def e(x, y): adj[x].add(y); adj[y].add(x)
                    for i in range(n):
                        e(i, iota[i]); e(n + i, n + t1[i]); e(2 * n + i, 2 * n + t2[i]); e(i, n + i); e(i, 2 * n + i); e(n + i, 2 * n + pi[i])
                    ok = all(len(s) == 3 for s in adj)
                    for u in range(3 * n):
                        for v in range(u + 1, 3 * n):
                            c = len(adj[u] & adj[v])
                            if (v in adj[u] and c) or c > 1: ok = False
                    if ok: cnt += 1
    print(f"m = {m}: {tot} normal forms, with girth >= 5: {cnt}")
