"""P3/N25, stage 1: EXACT certificate of infeasibility of the linear relaxation for one support.

Rows: pair rows (= r), point rows (= dZ), triple rows (<= 1), over the filtered blocks.
Certificate (Farkas): rationals y (one per pair / point row, any sign) and w >= 0 (one per triple row) such that
        for every admissible block B:   y . a_B + w . t_B  >= 0        and        y . b + sum(w)  <  0 .
Then no x >= 0 satisfies the rows (multiply the rows by y, w and add: 0 <= sum_B (y.a_B + w.t_B) x_B <= y.b + sum w < 0).
The floating-point dual of an elastic LP is rounded to rationals, the column inequalities are repaired exactly by raising the
multipliers of the POINT rows of the block when needed, and everything is re-checked in exact arithmetic.
usage: p3n25_cert.py register.jsonl id [denominator]"""
import sys, json, time, itertools
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack, identity, csr_matrix
import p3n25_ilp as I, p3n25_lp2 as L2

def build(d):
    adj, r, dZ, Ms, n0, info = L2.filtered_masks(d); nb = len(Ms)
    pair_row = {}; row = 0; rhs = []
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
    prow = list(range(row, row + 28)); rhs += dZ; row += 28
    cols_eq = []; trip = {}
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        cols_eq.append([prow[s] for s in pts] + [pair_row[pr] for pr in itertools.combinations(pts, 2)])
        for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
    trows = [(tr, lst) for tr, lst in trip.items() if len(lst) >= 2]
    cols_tr = [[] for _ in range(nb)]
    for j, (tr, lst) in enumerate(trows):
        for i in lst: cols_tr[i].append(j)
    return Ms, rhs, cols_eq, cols_tr, len(trows), row, pair_row, prow

def certificate(d, DEN=10 ** 6):
    Ms, rhs, cols_eq, cols_tr, ntr, neq, pair_row, prow = build(d); nb = len(Ms)
    # elastic LP: min sum(sp + sm):  Aeq x + sp - sm = b,  Atr x <= 1,  x >= 0
    r_, c_, v_ = [], [], []
    for i, lst in enumerate(cols_eq):
        for rw in lst: r_.append(rw); c_.append(i); v_.append(1.0)
    Aeq = coo_matrix((v_, (r_, c_)), shape=(neq, nb)).tocsr()
    r2, c2, v2 = [], [], []
    for i, lst in enumerate(cols_tr):
        for rw in lst: r2.append(rw); c2.append(i); v2.append(1.0)
    Atr = coo_matrix((v2, (r2, c2)), shape=(ntr, nb)).tocsr()
    A1 = hstack([Aeq, identity(neq), -identity(neq)]).tocsr()
    A2 = hstack([Atr, csr_matrix((ntr, 2 * neq))]).tocsr()
    cost = np.concatenate([np.zeros(nb), np.ones(2 * neq)])
    res = linprog(cost, A_ub=A2, b_ub=np.ones(ntr), A_eq=A1, b_eq=np.array(rhs, dtype=float), bounds=(0, None), method="highs-ipm")
    if res.status != 0: return None, f"elastic LP status {res.status}"
    if res.fun < 1e-7: return None, f"LP feasible (elastic optimum {res.fun:.2e})"
    # duals: minimise c x s.t. A1 x = b (mult lam), A2 x <= 1 (mult mu <= 0): dual feasible: A1^T lam + A2^T mu <= c ; objective b.lam + 1.mu = optimum > 0
    lam = res.eqlin.marginals; mu = res.ineqlin.marginals
    # certificate: y = -lam, w = -mu  (then y.a_B + w.t_B >= 0 for the block columns and y.b + sum w = -optimum < 0)
    y = [Fr(round(-float(v) * DEN), DEN) for v in lam]; w = [max(Fr(0), Fr(round(-float(v) * DEN), DEN)) for v in mu]
    # exact repair: for every block column with negative value, raise the multiplier of one of its point rows
    for _ in range(50):
        worst = Fr(0); bad = 0
        for i in range(nb):
            val = sum(y[rw] for rw in cols_eq[i]) + sum(w[rw] for rw in cols_tr[i])
            if val < 0:
                bad += 1
                y[cols_eq[i][0]] -= val                      # the first listed row of the block is a point row
        if bad == 0: break
    ok_cols = all(sum(y[rw] for rw in cols_eq[i]) + sum(w[rw] for rw in cols_tr[i]) >= 0 for i in range(nb))
    total = sum(y[k] * rhs[k] for k in range(neq)) + sum(w)
    info = {"blocks": nb, "eq_rows": neq, "triple_rows": ntr, "elastic_optimum": float(res.fun), "exact_value": str(total),
            "columns_ok": ok_cols, "nonzero_y": sum(1 for v in y if v != 0), "nonzero_w": sum(1 for v in w if v != 0)}
    return (y, w, total, ok_cols), info

if __name__ == "__main__":
    fn, sid = sys.argv[1], int(sys.argv[2]); DEN = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
    d = I.load(fn, sid); t0 = time.time()
    cert, info = certificate(d, DEN)
    print(f"support id {sid} (delta {d['delta']}): {info}  [{time.time()-t0:.1f}s]")
    if cert:
        y, w, total, ok = cert
        print("   EXACT CERTIFICATE VALID (all block columns >= 0 and total < 0):", bool(ok and total < 0))
