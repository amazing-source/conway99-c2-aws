"""minimal set T of support vertices whose neighbour rules ('in', 'out', sharing) make a positive star-less; the size and row rules are
kept for all vertices.   usage: star_core.py id p"""
import sys, json, time, itertools, collections
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I
sid, p = int(sys.argv[1]), int(sys.argv[2]); d = I.load("register/supports_open_4581.jsonl", sid)
A = np.zeros((28, 28), dtype=np.int64)
for x, y in d["edges"]: A[x, y] = A[y, x] = 1
C = A @ A; r = np.where(A == 1, 1, 2) - C; np.fill_diagonal(r, 0)
Np = [x for x in range(3, 28) if A[p, x]]; U = [x for x in Np if not any(A[x, y] for y in Np)]; u = len(U)
partner = {}
for i in range(u, 6, 2): partner[i] = i + 1; partner[i + 1] = i
others = [s for s in range(28) if s != p]
lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[q] for q in range(3) if A[s, q]) or "-")
def feasible(T, share=True, rrule=True):
    m = cp_model.CpModel(); a = {}
    for z in range(6):
        for s in others:
            a[z, s] = m.NewBoolVar("")
            if r[p, s] == 0: m.Add(a[z, s] == 0)
    for i, x in enumerate(U):
        for z in range(6): m.Add(a[z, x] == (1 if z == i else 0))
    for z in range(6):
        m.Add(sum(a[z, s] for s in others if s >= 3) - sum(a[z, s] for s in others if s < 3) == 5)
        if rrule:
            for s, t in itertools.combinations(others, 2):
                if r[s, t] <= 0 and s in T and t in T: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
        for s in others:
            if s not in T: continue
            ns = sum(a[z, t] for t in others if A[s, t] and t in T) + int(A[s, p]); pz = partner.get(z)
            m.Add(ns + (a[pz, s] if pz is not None else 0) <= 2 - a[z, s])
    for s in others: m.Add(sum(a[z, s] for z in range(6)) == int(r[p, s]))
    if share:
        for z, z2 in itertools.combinations(range(6), 2):
            prods = []
            for s in others:
                if r[p, s] >= 2:
                    b = m.NewBoolVar(""); m.AddMultiplicationEquality(b, [a[z, s], a[z2, s]]); prods.append(b)
            m.Add(sum(prods) <= (0 if partner.get(z) == z2 else 1))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 60; sv.parameters.num_workers = 4
    return sv.Solve(m) != cp_model.INFEASIBLE
T = set(others); assert not feasible(T)
for s in sorted(others, key=lambda v: -v):
    if not feasible(T - {s}): T.discard(s)
print(f"support {sid}, positive {'ABC'[p]}: unmatched neighbours {[lab(x) for x in U]}, matched {[lab(x) for x in Np if x not in U]}")
print(f"   minimal T ({len(T)} vertices): {[lab(s) + ':rho' + str(int(r[p, s])) for s in sorted(T)]}")
print(f"   without the r >= 1 rule on T: {'still no star' if not feasible(T, rrule=False) else 'a star exists'}")
print(f"   edges inside T: {[(lab(x), lab(y)) for x, y in itertools.combinations(sorted(T), 2) if A[x, y]]}")
print(f"   pairs of T with r = 0 (never in the same block): {[(lab(x), lab(y)) for x, y in itertools.combinations(sorted(T), 2) if r[x, y] <= 0 and not A[x,y]]}")
print(f"   neighbours in N_p of the vertices of T: { {lab(s): [lab(x) for x in Np if A[s, x]] for s in sorted(T) if s not in Np} }")
print(f"   all vertices: rho = 2: {[lab(s) for s in others if r[p, s] == 2]}; rho = 1 outside N_p: {[lab(s) for s in others if r[p, s] == 1 and s not in Np]}; rho = 0 outside N_p: {[lab(s) for s in others if r[p, s] == 0 and s not in Np]}")
