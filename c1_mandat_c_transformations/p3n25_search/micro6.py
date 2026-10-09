"""Microscopic study, step 6: the obstruction of a killed support on a small vertex set T, written out.
Prints r and dZ on T, the admissible traces on T (by type), and an l1-minimal certificate of the restricted LP.
usage: micro6.py id v1,v2,...   (vertices of T; 0,1,2 = A,B,C)"""
import sys, json, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack, vstack
import p3n25_ilp as I, p3n25_batch as PB
sid = int(sys.argv[1]); T = [int(v) for v in sys.argv[2].split(",")]
d = I.load("register/supports_open_4581.jsonl", sid)
adj, r, dZ, Ms = PB.blocks_F1(d)
lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
print(f"support {sid}: delta {d['delta']}, labels {d['labels_N']}, paths {d['path_counts']}")
print("T =", " ".join(lab(s) for s in T)); print("dZ:", {lab(s): dZ[s] for s in T})
print("r on T:"); 
for s in T: print("   ", lab(s).ljust(10), " ".join(str(r[s][t]) if s != t else "." for t in T))
Tm = sum(1 << s for s in T)
from collections import Counter
tr = Counter(B & Tm for B in Ms)
traces = sorted(set(tr) | {0})
print(f"{len(traces)} distinct traces on T (of {len(Ms)} blocks). Traces:")
for t_ in traces: print("    {" + ", ".join(lab(s) for s in T if (t_ >> s) & 1) + "}", f"  ({tr.get(t_, 0)} blocks)")
rows = []
for s, t in itertools.combinations(T, 2):
    if r[s][t] > 0: rows.append((s, t))
rows += [(s,) for s in T] + ["tot"]
idx = {rw: k for k, rw in enumerate(rows)}
b = np.array([r[rw[0]][rw[1]] if len(rw) == 2 and rw != "tot" else (71 if rw == "tot" else dZ[rw[0]]) for rw in rows], dtype=float)
rr, cc = [], []
for j, t_ in enumerate(traces):
    pts = [s for s in T if (t_ >> s) & 1]
    rr.append(j); cc.append(idx["tot"])
    for s in pts: rr.append(j); cc.append(idx[(s,)])
    for pr in itertools.combinations(pts, 2): rr.append(j); cc.append(idx[pr])
Acol = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(traces), len(rows))).tocsr()
A1 = hstack([-Acol, Acol]).tocsr(); A2 = coo_matrix(np.concatenate([b, -b]).reshape(1, -1))
res = linprog(np.ones(2 * len(rows)), A_ub=vstack([A1, A2]).tocsr(), b_ub=np.concatenate([np.zeros(len(traces)), [-1.0]]), bounds=(0, None), method="highs")
if res.status != 0: print("restricted LP is feasible (no certificate)"); sys.exit()
y = res.x[:len(rows)] - res.x[len(rows):]
nz = [(k, y[k]) for k in range(len(rows)) if abs(y[k]) > 1e-9]; sc = min(abs(v) for _, v in nz)
print("certificate (multiplier, row, right-hand side):")
for k, v in nz:
    rw = rows[k]
    name = "total number of outside vertices" if rw == "tot" else (f"point {lab(rw[0])}" if len(rw) == 1 else f"pair {lab(rw[0])}, {lab(rw[1])}")
    print(f"   {v/sc:+7.3f}   {name}   = {b[k]:.0f}")
print("   sum of multiplier x right-hand side =", round(float(sum(y[k] * b[k] for k in range(len(rows))) / sc), 4), " (< 0)")
