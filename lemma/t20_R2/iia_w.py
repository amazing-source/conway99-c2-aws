# IIa.0: enumeration of N(p).  N(p) = {x0,y0,x1,y1} u W, W = 5 mate pairs w = (i;k), sigma w = (k;i) (d = 1).
# x_i (word) has exactly 2 - r_i neighbours in W, r_i = number of active inner neighbours of x_i.
import itertools, json, numpy as np
import r2c
from r2c import *
m, H = r2c.load_structs()["IIa.0"]
A0 = r2c.base_graph(m, H); r2c.check_base(A0, H)
words = [i for i in range(10) if i not in H]
need = {i: 2 - int(A0[i, 0] + A0[i, 10] + A0[i, 1] + A0[i, 11]) for i in words}
print("W-degree of x_i:", need, "sum", sum(need.values()))
sols = []
def rec(edges, deg, start):
    if len(edges) == 5:
        if all(deg[i] == need[i] for i in words):
            sols.append(tuple(edges))
        return
    for a in range(start, len(allpairs)):
        i, k = allpairs[a]
        if deg[i] < need[i] and deg[k] < need[k]:
            deg[i] += 1; deg[k] += 1
            rec(edges + [(i, k)], deg, a + 1)
            deg[i] -= 1; deg[k] -= 1
allpairs = [(i, k) for i in words for k in words if i < k]
rec([], {i: 0 for i in words}, 0)
print("type sets (5 distinct unordered pairs with the right degrees):", len(sols))
def build(sol):
    n = 31
    A = np.zeros((n, n), dtype=np.int64); A[:21, :21] = A0
    for t, (i, k) in enumerate(sol):
        w, sw = 21 + 2 * t, 22 + 2 * t
        for (u, v) in ((w, sw), (w, PV), (sw, PV), (w, i), (w, 10 + k), (sw, k), (sw, 10 + i)):
            A[u, v] = A[v, u] = 1
    return A
good = []
nb = npsd = 0
for sol in sols:
    A = build(sol)
    if not budgets_ok(A):
        nb += 1; continue
    r = psd_reject(A)
    if r is not None:
        npsd += 1; continue
    good.append(sol)
print("rejected by budgets:", nb, " by PSD certificate:", npsd, " kept:", len(good))
for g in good:
    print("  ", g, psd_exact_report(build(g)))
json.dump(good, open("iia_w.json", "w"))
print(r2c.STATS)
