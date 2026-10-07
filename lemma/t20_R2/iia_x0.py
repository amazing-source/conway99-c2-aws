# IIa.0, exploration: S u N[p] (31 vertices, 87 type sets for W, file iia_w.json) plus the vertices of X_0.
# A vertex z of X_0 is a word with no neighbour in S u {p} and exactly 2 neighbours in W (two different pairs).
# For each W-set: number of choices N(z) n W for which S u N[p] u {z, sigma z} (33 vertices) passes budgets + PSD.
import json, itertools, numpy as np
import r2c, eng2
from r2c import *
m, H = r2c.load_structs()["IIa.0"]
A0 = r2c.base_graph(m, H)
good = json.load(open("iia_w.json"))
def build(sol):
    n = 31
    A = np.zeros((n, n), dtype=np.int64); A[:21, :21] = A0
    for t, (i, k) in enumerate(sol):
        w, sw = 21 + 2 * t, 22 + 2 * t
        for (u, v) in ((w, sw), (w, PV), (sw, PV), (w, i), (w, 10 + k), (sw, k), (sw, 10 + i)):
            A[u, v] = A[v, u] = 1
    return A
sig = list(range(10, 20)) + list(range(0, 10)) + [20] + [22, 21, 24, 23, 26, 25, 28, 27, 30, 29]
st = eng2.Counter()
tot = 0
res = []
for sol in good:
    A = build(sol)
    node = eng2.Node(A, sig); node.prepare()
    opts = []
    for a, b in itertools.combinations(range(21, 31), 2):
        if (a - 21) // 2 == (b - 21) // 2:
            continue
        row = np.zeros(31, dtype=np.int64); row[a] = 1; row[b] = 1
        if node.budget_fail(row, 0):
            continue
        if node.psd_fail(row, 0, st) is not None:
            continue
        opts.append((a, b))
    # classes under sigma
    cls = set()
    for a, b in opts:
        cls.add(min((a, b), tuple(sorted((sig[a], sig[b])))))
    res.append((sol, len(opts), len(cls)))
    tot += len(cls)
dead = [r for r in res if r[1] == 0]
print("W type sets:", len(good), " with no admissible X_0 vertex at all:", len(dead))
print("admissible X_0 orbits per W-set (classes under sigma): min %d max %d total %d" % (min(r[2] for r in res), max(r[2] for r in res), tot))
print("exact PSD rejections:", st.c)
json.dump(res, open("iia_x0.json", "w"))
