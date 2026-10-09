"""P3/N25, stage 1, PHASE A: linear screen of a range of supports of Codex's register, with an exact certificate for every
support whose linear relaxation is infeasible.

For each support: admissible blocks with the EXACT filter F1 only (every s outside B has at most 2 neighbours in B; no floating
spectral filter, so that the certificate covers every block allowed by the stated integer conditions), LP by interior point;
if infeasible: Farkas multipliers rounded to rationals, repaired and re-checked exactly (p3n25_cert logic).
Output: one JSON line per support in the result file (append).     usage: p3n25_batch.py register.jsonl first last out.jsonl"""
import sys, json, time, itertools
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack, identity, csr_matrix
import p3n25_ilp as I

def blocks_F1(d):
    adj, r, dZ = I.boundary(d["edges"]); Ms = I.masks(adj, r)
    out = []
    for B in Ms:
        ok = True
        for s in range(28):
            if not (B >> s) & 1 and bin(adj[s] & B).count("1") > 2: ok = False; break
        if ok: out.append(B)
    return adj, r, dZ, out

def run(d, DEN=10 ** 6):
    adj, r, dZ, Ms = blocks_F1(d); nb = len(Ms)
    pair_row = {}; row = 0; rhs = []
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
    prow = list(range(row, row + 28)); rhs += dZ; neq = row + 28
    cols_eq = []; trip = {}; used = set()
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        cols_eq.append([prow[s] for s in pts] + [pair_row[pr] for pr in itertools.combinations(pts, 2)])
        used.update(itertools.combinations(pts, 2))
        for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
    if any(pr not in used for pr in pair_row):
        return {"status": "infeasible", "reason": "a required pair lies in no admissible block", "blocks": nb, "certified": True}
    trows = [lst for lst in trip.values() if len(lst) >= 2]; ntr = len(trows)
    cols_tr = [[] for _ in range(nb)]
    for j, lst in enumerate(trows):
        for i in lst: cols_tr[i].append(j)
    r_, c_ = [], []
    for i, lst in enumerate(cols_eq):
        for rw in lst: r_.append(rw); c_.append(i)
    Aeq = coo_matrix((np.ones(len(r_)), (r_, c_)), shape=(neq, nb)).tocsr()
    r2, c2 = [], []
    for i, lst in enumerate(cols_tr):
        for rw in lst: r2.append(rw); c2.append(i)
    Atr = coo_matrix((np.ones(len(r2)), (r2, c2)), shape=(ntr, nb)).tocsr()
    A1 = hstack([Aeq, identity(neq), -identity(neq)]).tocsr(); A2 = hstack([Atr, csr_matrix((ntr, 2 * neq))]).tocsr()
    cost = np.concatenate([np.zeros(nb), np.ones(2 * neq)])
    res = linprog(cost, A_ub=A2, b_ub=np.ones(ntr), A_eq=A1, b_eq=np.array(rhs, dtype=float), bounds=(0, None), method="highs-ipm", options={"time_limit": 600})
    if res.status != 0: return {"status": f"lp_status_{res.status}", "blocks": nb}
    if res.fun < 1e-6: return {"status": "feasible", "blocks": nb, "elastic": float(res.fun)}
    lam = res.eqlin.marginals; mu = res.ineqlin.marginals
    y = [Fr(round(-float(v) * DEN), DEN) for v in lam]; w = [max(Fr(0), Fr(round(-float(v) * DEN), DEN)) for v in mu]
    for _ in range(50):
        bad = 0
        for i in range(nb):
            val = sum(y[rw] for rw in cols_eq[i]) + sum(w[rw] for rw in cols_tr[i])
            if val < 0: bad += 1; y[cols_eq[i][0]] -= val
        if bad == 0: break
    ok_cols = all(sum(y[rw] for rw in cols_eq[i]) + sum(w[rw] for rw in cols_tr[i]) >= 0 for i in range(nb))
    total = sum(y[k] * rhs[k] for k in range(neq)) + sum(w)
    return {"status": "infeasible", "blocks": nb, "elastic": float(res.fun), "certified": bool(ok_cols and total < 0), "exact_value": str(total),
            "y": [str(v) for v in y], "w_nonzero": {str(j): str(v) for j, v in enumerate(w) if v != 0}}

if __name__ == "__main__":
    fn, first, last, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    lines = open(fn, encoding="utf-8").read().splitlines()
    done = set()
    try:
        for ln in open(out, encoding="utf-8"): done.add(json.loads(ln)["id"])
    except FileNotFoundError: pass
    with open(out, "a", encoding="utf-8") as fo:
        for pos in range(first, min(last, len(lines) - 1) + 1):
            d = json.loads(lines[pos])
            if d["id"] in done: continue
            t0 = time.time(); res = run(d)
            res.update({"id": d["id"], "pos": pos, "delta": d["delta"], "seconds": round(time.time() - t0, 1)})
            fo.write(json.dumps(res) + "\n"); fo.flush()
