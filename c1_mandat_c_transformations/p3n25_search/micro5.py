"""Microscopic study, step 5: the SMALLEST set of support vertices that already makes a killed support impossible.

Restricted LP on T (a subset of S): variables = traces B inter T of the admissible blocks (the empty trace included), rows:
pair rows inside T (= r), point rows of T (= dZ), total number of outside vertices (= 71), triple rows inside T (<= 1 is NOT kept:
traces of different blocks may coincide, so only the pair / point / total rows are used).  If this LP is infeasible, the obstruction
lives on T.  Greedy deletion of vertices gives an inclusion-minimal T.          usage: micro5.py id [id ...]"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import p3n25_ilp as I, p3n25_batch as PB

def feasible_on(T, Ms, r, dZ):
    Tm = 0
    for s in T: Tm |= 1 << s
    traces = sorted({B & Tm for B in Ms} | {0})
    rows = {}; rhs = []
    for s, t in itertools.combinations(T, 2):
        if r[s][t] > 0: rows[(s, t)] = len(rhs); rhs.append(r[s][t])
    for s in T: rows[(s,)] = len(rhs); rhs.append(dZ[s])
    rows["tot"] = len(rhs); rhs.append(71)
    rr, cc = [], []
    for j, tr in enumerate(traces):
        pts = [s for s in T if (tr >> s) & 1]
        rr.append(rows["tot"]); cc.append(j)
        for s in pts: rr.append(rows[(s,)]); cc.append(j)
        for pr in itertools.combinations(pts, 2):
            if pr not in rows: return None                       # cannot happen: a pair inside a block has r >= 1
            rr.append(rows[pr]); cc.append(j)
    A = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(rhs), len(traces))).tocsr()
    res = linprog(np.zeros(len(traces)), A_eq=A, b_eq=np.array(rhs, dtype=float), bounds=(0, None), method="highs")
    return res.status == 0, len(traces)

def minimal_T(d):
    adj, r, dZ, Ms = PB.blocks_F1(d)
    T = list(range(28))
    ok, _ = feasible_on(T, Ms, r, dZ)
    if ok: return None, adj, r, dZ
    changed = True
    while changed:
        changed = False
        for s in sorted(T, key=lambda v: -v):                    # try to drop the isolated / high-numbered vertices first
            T2 = [v for v in T if v != s]
            ok, nt = feasible_on(T2, Ms, r, dZ)
            if not ok: T = T2; changed = True
    return T, adj, r, dZ

if __name__ == "__main__":
    for sid in map(int, sys.argv[1:]):
        d = I.load("register/supports_open_4581.jsonl", sid); t0 = time.time()
        T, adj, r, dZ = minimal_T(d)
        lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
        if T is None: print(f"support {sid}: the pair/point/total LP on all of S is feasible (the triple rows or block traces matter)"); continue
        R1 = sum(dZ[s] for s in T); R2 = sum(r[s][t] for s, t in itertools.combinations(T, 2))
        print(f"support {sid} (delta {d['delta']}): minimal obstruction on {len(T)} vertices: {' '.join(lab(s) for s in T)}  [{time.time()-t0:.0f}s]")
        print(f"   edges inside: {' '.join(lab(a) + '-' + lab(b) for a, b in d['edges'] if a in T and b in T)}")
        print(f"   R1 = {R1}, R2 = {R2}, R1 - R2 = {R1 - R2}  (pigeonhole bound 71)")
