import json, itertools
from latt import short_vectors, G_T_of
res = json.load(open("structures.json"))
m = res[0]["survivors"][0]; GT = G_T_of(m, [])
keep = list(range(1, 9))
Q = [[0]*9 for _ in range(9)]
Q[0][0] = 9
for a,i in enumerate(keep):
    Q[0][a+1] = Q[a+1][0] = 7
    for b,j in enumerate(keep):
        Q[a+1][b+1] = 7*GT[i][j]
sv = short_vectors(Q, 16, limit=10**6)
from collections import Counter
print("FP counts by value (up to sign):", sorted(Counter(v for v,x in sv).items()))
# brute force cross-check on the box [-2,2]^9
cnt = Counter()
for x in itertools.product(range(-2,3), repeat=9):
    v = sum(x[a]*Q[a][b]*x[b] for a in range(9) for b in range(9))
    if 0 < v <= 16: cnt[v] += 1
print("brute force box [-2,2]^9 (both signs):", sorted(cnt.items()))
