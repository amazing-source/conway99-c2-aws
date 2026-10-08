"""Counts of triangle-free components (4-cycles allowed, at most 2 common neighbours for non-adjacent vertices) with m = 2
and m = 3 lines per layer, in the normal form of comp66.py; a cheap invariant gives a lower bound on the number of types."""
import itertools, collections
def matchings(e):
    e = list(e)
    if not e: yield (); return
    a = e[0]
    for b in e[1:]:
        for m in matchings([x for x in e if x not in (a, b)]): yield ((a, b),) + m
for m in (2, 3):
    n = 2 * m
    def inv(mm):
        v = [0] * n
        for a, b in mm: v[a] = b; v[b] = a
        return v
    ms = [inv(x) for x in matchings(range(n))]
    iota = ms[0]; cnt = 0; g5 = 0; invs = collections.Counter()
    for t1 in ms:
        for t2 in ms:
            for pi in itertools.permutations(range(n)):
                adj = [set() for _ in range(3 * n)]
                def e(x, y): adj[x].add(y); adj[y].add(x)
                for i in range(n):
                    e(i, iota[i]); e(n + i, n + t1[i]); e(2 * n + i, 2 * n + t2[i]); e(i, n + i); e(i, 2 * n + i); e(n + i, 2 * n + pi[i])
                ok = True; c4 = 0
                for u in range(3 * n):
                    for v in range(u + 1, 3 * n):
                        c = len(adj[u] & adj[v])
                        if v in adj[u]:
                            if c: ok = False; break
                        elif c > 2: ok = False; break
                        elif c == 2: c4 += 1
                    if not ok: break
                if not ok: continue
                seen = {0}; st = [0]
                while st:
                    x = st.pop()
                    for y in adj[x]:
                        if y not in seen: seen.add(y); st.append(y)
                if len(seen) != 3 * n: continue
                cnt += 1
                if c4 == 0: g5 += 1
                # invariant: number of 4-cycle pairs, and sorted distance-2 multiset sizes per vertex
                prof = tuple(sorted(sum(1 for v in range(3 * n) if v != u and len(adj[u] & adj[v]) == 2) for u in range(3 * n)))
                invs[(c4, prof)] += 1
    print(f"m = {m}: triangle-free connected normal forms {cnt} (of which girth >= 5: {g5}); distinct values of a cheap invariant: {len(invs)}")
