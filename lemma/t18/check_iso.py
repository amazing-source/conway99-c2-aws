import json
from enum_S import isomorphic
res = json.load(open("structures.json"))
S = res[0]["survivors"]
def mk(edges):
    m = [[0]*9 for _ in range(9)]
    for i, j in edges:
        m[i][j] = m[j][i] = 1
    return m
c9 = mk([(i, (i+s) % 9) for i in range(9) for s in (1, 2)])
k33 = mk([((a, b), (c, d)) and (3*a+b, 3*c+d) for a in range(3) for b in range(3) for c in range(3) for d in range(3)
          if (a, b) < (c, d) and ((a == c) != (b == d))])
for name, g in (("C9(1,2)", c9), ("K3xK3", k33)):
    print(name, [isomorphic(g, [], s, []) for s in S])
# independence number and max clique of each survivor
import itertools
for idx, m in enumerate(S):
    al = max(len(I) for r in range(1, 6) for I in itertools.combinations(range(9), r)
             if all(not m[a][b] for a, b in itertools.combinations(I, 2)))
    om = max(len(I) for r in range(1, 6) for I in itertools.combinations(range(9), r)
             if all(m[a][b] for a, b in itertools.combinations(I, 2)))
    ind3 = sum(1 for I in itertools.combinations(range(9), 3) if all(not m[a][b] for a, b in itertools.combinations(I, 2)))
    print(f"B{idx}: independence number {al}, clique number {om}, independent triples {ind3}")
