# IIa.0, exploration: number of "bases" S u N[p] u X_0 (35 vertices): W type set (87), two X_0 orbits with their
# two W-neighbours each, edge pattern between the two orbits (none / z0~z1), up to relabelling.
# Tests: budgets (exact) and PSD (exact certificates for rejections; 'kept' is a float decision).
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
bases = []
nb_single = 0
for wi, sol in enumerate(good):
    A = build(sol)
    node = eng2.Node(A, sig); node.prepare()
    opts = []
    for a, b in itertools.combinations(range(21, 31), 2):
        if (a - 21) // 2 == (b - 21) // 2:
            continue
        row = np.zeros(31, dtype=np.int64); row[a] = 1; row[b] = 1
        if node.budget_fail(row, 0) or node.psd_fail(row, 0, st) is not None:
            continue
        opts.append((a, b))
    sigp = lambda ab: tuple(sorted((sig[ab[0]], sig[ab[1]])))
    reps = sorted(set(min(o, sigp(o)) for o in opts))
    nb_single += len(reps)
    for ia, alpha in enumerate(reps):
        row0 = np.zeros(31, dtype=np.int64); row0[list(alpha)] = 1
        nd = node.child(row0, 0); nd.prepare()
        for beta in reps[ia:]:
            for orient in (beta, sigp(beta)):
                for pat in (0, 1):
                    if pat == 0 and orient != beta:
                        continue          # same graph as the other orientation
                    if alpha == beta and orient != beta and pat == 1:
                        pass
                    row1 = np.zeros(33, dtype=np.int64); row1[list(orient)] = 1
                    if pat:
                        row1[31] = 1
                    if nd.budget_fail(row1, 0) or nd.psd_fail(row1, 0, st) is not None:
                        continue
                    bases.append((wi, alpha, orient, pat))
print("W type sets 87; admissible single X_0 orbits (classes under sigma), total over the W-sets:", nb_single)
print("bases S u N[p] u X_0 passing budgets and PSD on 35 vertices:", len(bases),
      " (no edge in X_0: %d, one edge orbit: %d)" % (sum(1 for b in bases if b[3] == 0), sum(1 for b in bases if b[3] == 1)))
per = {}
for b in bases:
    per[b[0]] = per.get(b[0], 0) + 1
print("W-sets with at least one base:", len(per), " max bases for one W-set:", max(per.values()))
print("exact PSD rejections:", st.c)
json.dump([[b[0], list(b[1]), list(b[2]), b[3]] for b in bases], open("iia_bases.json", "w"))
