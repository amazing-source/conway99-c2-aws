"""P3/N25, stage 1, LINEAR RELAXATION of the block programme with the triple rows (floating point, HiGHS).

x_B in [0, 1] for every admissible block B;  pair rows (= r), point rows (= dZ), triple rows (<= 1).
If the LP is infeasible the support has no system of 71 outside vertices: it is excluded, PROVIDED the infeasibility is then
certified in exact arithmetic (Farkas multipliers); this script only screens and measures.
usage: p3n25_lp.py register.jsonl first last [notriple]        (ids of the register, inclusive range by position)"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import p3n25_ilp as I

def lp_support(d, triples=True):
    adj, r, dZ = I.boundary(d["edges"]); Ms = I.masks(adj, r); nb = len(Ms)
    rows, cols, vals, rhs = [], [], [], []
    row = 0; pair_row = {}
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
    prow = list(range(row, row + 28)); rhs += dZ; row += 28
    trip = {}
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        for s in pts: rows.append(prow[s]); cols.append(i); vals.append(1.0)
        for pr in itertools.combinations(pts, 2): rows.append(pair_row[pr]); cols.append(i); vals.append(1.0)
        if triples:
            for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
    Aeq = coo_matrix((vals, (rows, cols)), shape=(row, nb)).tocsr(); beq = np.array(rhs, dtype=float)
    missing = [pr for pr in pair_row if Aeq[pair_row[pr]].nnz == 0]
    if missing: return "infeasible (a required pair lies in no admissible block)", nb, 0
    Aub = bub = None; ntr = 0
    if triples:
        r2, c2, v2 = [], [], []
        for tr, lst in trip.items():
            if len(lst) >= 2:
                for i in lst: r2.append(ntr); c2.append(i); v2.append(1.0)
                ntr += 1
        if ntr: Aub = coo_matrix((v2, (r2, c2)), shape=(ntr, nb)).tocsr(); bub = np.ones(ntr)
    res = linprog(np.zeros(nb), A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=(0, 1), method="highs-ipm", options={"time_limit": 300})
    return ("feasible" if res.status == 0 else ("infeasible" if res.status == 2 else f"status {res.status}")), nb, ntr

if __name__ == "__main__":
    fn = sys.argv[1]; first, last = int(sys.argv[2]), int(sys.argv[3]); triples = "notriple" not in sys.argv
    lines = open(fn, encoding="utf-8").read().splitlines()
    step = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 1
    for pos in range(first, min(last, len(lines) - 1) + 1, step):
        d = json.loads(lines[pos]); t0 = time.time()
        st, nb, ntr = lp_support(d, triples)
        print(f"pos {pos} id {d['id']} delta {d['delta']}: {nb} blocks, {ntr} triple rows: LP {st}  [{time.time()-t0:.1f}s]", flush=True)
