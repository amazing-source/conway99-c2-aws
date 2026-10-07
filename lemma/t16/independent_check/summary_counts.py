#!/usr/bin/env python
"""Class counts per stage and structure of N_Y(x) for the stage-1 survivors."""
import sys
import numpy as np
import wagner_check as W

profile = sys.argv[1]
store = W.run_profile(profile, do_stage2=False)

# Aut(B)-classes of matchings at L1 / L2
L1, L2 = set(), set()
for M in W.MATCHINGS:
    A = W.base_matrix(M)
    C = A @ A
    if not all(C[W.P(i), W.Q(j)] <= (1 if W.B[i][j] else 2) for i in range(8) for j in range(8)):
        continue
    L1.add(W.match_key(M))
    unk = [(u, v) for u in W.X2 for v in W.X2 if u < v]
    if W.violations(A, list(range(16)) + W.X2, unk):
        continue
    L2.add(W.match_key(M))
print("Aut(B)-classes: L1 matchings %d, L2 matchings %d" % (len(L1), len(L2)))

# iso classes of (matching, xy, incidence) = config with X0-internal edges deleted
inc_cls = {}
for key, (A, M, mxy, masks, comb) in store.items():
    A2 = A.copy()
    for u in W.X0:
        for v in W.X0:
            A2[u, v] = 0
    k = W.canon(A2)
    inc_cls.setdefault(k, []).append(key)
print("iso classes of X0-X2 incidence structures (with matching, xy): %d; configs per class: %s" % (
    len(inc_cls), sorted(len(v) for v in inc_cls.values())))

names = {}
for i in range(8):
    names[W.P(i)] = "P%d" % i
    names[W.Q(i)] = "Q%d" % i
names[W.PV] = "p"
for k in range(5):
    names[W.W(k)] = "w%d" % k
    names[W.W(k, 1)] = "sw%d" % k
for m in range(4):
    names[W.Z(m)] = "z%d" % m
    names[W.Z(m, 1)] = "sz%d" % m

# N_Y(x) structure for each config (x = z_mxy)
hist = {}
for n, (key, (A, M, mxy, masks, comb)) in enumerate(sorted(store.items())):
    x = W.Z(mxy)
    N = [v for v in range(35) if A[x, v]]
    inner = [(names[u], names[v]) for u in N for v in N if u < v and A[u, v]]
    unmatched = [names[v] for v in N if sum(A[v, u] for u in N) == 0]
    r = {}
    for v in range(35):
        if v == x:
            continue
        r[v] = (1 if A[x, v] else 2) - sum(int(A[v, u]) for u in N)
    rX0 = {names[w]: r[w] for w in W.X0 if r[w]}
    demand_in = {names[w]: r[w] for w in W.X0 if r[w] and A[x, w]}
    sig = (len(inner), len(unmatched), tuple(sorted(rX0.values())), len(demand_in))
    hist[sig] = hist.get(sig, 0) + 1
    if n < 3 or profile == "B":
        print("config #%d x=%s: N_Y(x)=%s" % (n, names[x], [names[v] for v in N]))
        print("   edges inside N_Y(x): %s ; vertices of N_Y(x) with no partner yet: %s" % (inner, unmatched))
        print("   r on P: %s  r on Q: %s" % ([r[W.P(i)] for i in range(8)], [r[W.Q(j)] for j in range(8)]))
        print("   r on X0 (nonzero): %s ; of which inside N(x): %s" % (rX0, demand_in))
        print("   r on X2\\{x} (nonzero): %s" % {names[z]: r[z] for z in W.X2 if z != x and r[z]})
print("histogram (#edges in N_Y(x), #unmatched, sorted nonzero r on X0, #X0 in N(x) with r>0):")
for k, v in sorted(hist.items()):
    print("  ", v, k)
