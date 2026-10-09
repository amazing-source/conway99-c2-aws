"""P3/N25, stage 1, linear relaxation with FILTERED blocks (screen; floating point).

Block filters added to p3n25_ilp.masks (all are necessary conditions for B = N(z) inter S in an srg(99,14,1,2)):
  (F1) every s of S outside B has at most 2 neighbours in B                       (mu = 2 for the pair {s, z});
  (F2) the two Gram matrices  3I - A + J/9  and  4I + A - (2/11)J  of the induced graph on S u {z} are positive semidefinite
       (they are 7 x and 7 x principal submatrices of the two eigen-projectors);  tested by the Schur complement on S.
Then the same LP as p3n25_lp.py (pair rows, point rows, triple rows), interior point.
usage: p3n25_lp2.py register.jsonl first last [step] [noF1] [noF2]"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import p3n25_ilp as I
TOL = 1e-7

def filtered_masks(d, useF1=True, useF2=True):
    adj, r, dZ = I.boundary(d["edges"]); Ms = I.masks(adj, r); n0 = len(Ms)
    A = np.zeros((28, 28))
    for a, b in d["edges"]: A[a, b] = A[b, a] = 1.0
    Bm = np.array([[(B >> s) & 1 for s in range(28)] for B in Ms], dtype=float)          # nb x 28
    keep = np.ones(len(Ms), dtype=bool)
    if useF1:
        cnt = Bm @ A                                                                     # number of neighbours of s inside B
        keep &= ((cnt * (1 - Bm)).max(axis=1) <= 2)
    info = {}
    if useF2:
        GE = 3 * np.eye(28) - A + np.ones((28, 28)) / 9; GF = 4 * np.eye(28) + A - 2 * np.ones((28, 28)) / 11
        for name, G, cvec, dd in (("E", GE, -Bm + 1 / 9, 3 + 1 / 9), ("F", GF, Bm - 2 / 11, 4 - 2 / 11)):
            w = np.linalg.eigvalsh(G); info[name] = float(w.min())
            Gi = np.linalg.pinv(G, rcond=1e-10)
            sch = dd - np.einsum("ij,jk,ik->i", cvec, Gi, cvec)
            keep &= (sch >= -TOL)
    Ms2 = [B for B, k in zip(Ms, keep) if k]
    return adj, r, dZ, Ms2, n0, info

def lp(d, useF1=True, useF2=True):
    adj, r, dZ, Ms, n0, info = filtered_masks(d, useF1, useF2); nb = len(Ms)
    rows, cols, vals, rhs = [], [], [], []; row = 0; pair_row = {}
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
    prow = list(range(row, row + 28)); rhs += dZ; row += 28
    trip = {}; used_pairs = set()
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        for s in pts: rows.append(prow[s]); cols.append(i); vals.append(1.0)
        for pr in itertools.combinations(pts, 2): rows.append(pair_row[pr]); cols.append(i); vals.append(1.0); used_pairs.add(pr)
        for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
    if any(pr not in used_pairs for pr in pair_row): return "infeasible (uncovered pair)", n0, nb, info
    Aeq = coo_matrix((vals, (rows, cols)), shape=(row, nb)).tocsr(); beq = np.array(rhs, dtype=float)
    r2, c2, v2 = [], [], []; ntr = 0
    for tr, lst in trip.items():
        if len(lst) >= 2:
            for i in lst: r2.append(ntr); c2.append(i); v2.append(1.0)
            ntr += 1
    Aub = coo_matrix((v2, (r2, c2)), shape=(ntr, nb)).tocsr() if ntr else None
    res = linprog(np.zeros(nb), A_ub=Aub, b_ub=(np.ones(ntr) if ntr else None), A_eq=Aeq, b_eq=beq, bounds=(0, 1), method="highs-ipm", options={"time_limit": 300})
    return ("feasible" if res.status == 0 else ("infeasible" if res.status == 2 else f"status {res.status}")), n0, nb, info

if __name__ == "__main__":
    fn = sys.argv[1]; first, last = int(sys.argv[2]), int(sys.argv[3])
    step = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 1
    useF1 = "noF1" not in sys.argv; useF2 = "noF2" not in sys.argv
    lines = open(fn, encoding="utf-8").read().splitlines()
    for pos in range(first, min(last, len(lines) - 1) + 1, step):
        d = json.loads(lines[pos]); t0 = time.time()
        st, n0, nb, info = lp(d, useF1, useF2)
        print(f"pos {pos} id {d['id']} delta {d['delta']}: blocks {n0} -> {nb}: LP {st}  [{time.time()-t0:.1f}s]  min eig E {info.get('E', 0):.4f} F {info.get('F', 0):.4f}", flush=True)
