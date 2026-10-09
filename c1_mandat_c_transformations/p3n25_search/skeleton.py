"""THE THREE STARS: the outside vertices adjacent to a positive.

Every pair (p, s) with p positive is covered only by blocks through p, so the rows of the positives are decided by the blocks that
contain a positive.  Master problem (integers): choose such blocks with
     point rows of the positives (= 6), pair rows (p, q) and (p, s) (= r);   rows inside N: <= ;   triples <= 1.
Sub-problem for a master solution: the residual pair / point demands inside N must be met by blocks WITHOUT positive (4-subsets of N):
linear screen of the residual.  If the residual screen is infeasible, the master solution is forbidden (no-good cut) and the master is
solved again.  The loop ends with 'no three-star' (the support is impossible, solver verdict to be re-proved) or with a three-star
whose residual is linearly feasible.              usage: skeleton.py register.jsonl id [rounds] [time_limit]"""
import sys, json, time, itertools, random
import numpy as np
from scipy.optimize import milp, linprog, LinearConstraint, Bounds
from scipy.sparse import coo_matrix, vstack, csr_matrix
import p3n25_ilp as I, level2 as L2

def setup(d):
    P = L2.prepare(d); pool = L2.make_pool(P["R"], P["dv"], random.Random(5)); c1, c2, pk = L2.filter_blocks(P, pool); keep = ~(c1 | c2 | pk)
    Bm = P["Bm"][keep]; npos = Bm[:, :3].sum(axis=1)
    return P, Bm[npos > 0], Bm[npos == 0]

def master_matrices(P, Bp):
    r, dZ = P["r"], P["dZ"]; nb = len(Bp)
    eq_rows = {}; le_rows = {}; eq_rhs = []; le_rhs = []
    for p in range(3): eq_rows[(p,)] = len(eq_rhs); eq_rhs.append(dZ[p])
    for p in range(3):
        for s in range(p + 1, 28):
            if r[p][s] > 0: eq_rows[(p, s)] = len(eq_rhs); eq_rhs.append(r[p][s])
    for s in range(3, 28): le_rows[(s,)] = len(le_rhs); le_rhs.append(dZ[s])
    for s in range(3, 28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: le_rows[(s, t)] = len(le_rhs); le_rhs.append(r[s][t])
    er, ec, lr, lc = [], [], [], []; trip = {}
    for j in range(nb):
        pts = np.nonzero(Bp[j])[0].tolist()
        for s in pts:
            if s < 3: er.append(eq_rows[(s,)]); ec.append(j)
            else: lr.append(le_rows[(s,)]); lc.append(j)
        for q in itertools.combinations(pts, 2):
            if q[0] < 3: er.append(eq_rows[q]); ec.append(j)
            else: lr.append(le_rows[q]); lc.append(j)
        for q in itertools.combinations(pts, 3): trip.setdefault(q, []).append(j)
    tr_, tc = [], []; nt = 0
    for q, lst in trip.items():
        if len(lst) >= 2: tr_ += [nt] * len(lst); tc += lst; nt += 1
    Aeq = coo_matrix((np.ones(len(er)), (er, ec)), shape=(len(eq_rhs), nb)).tocsr()
    Ale = coo_matrix((np.ones(len(lr)), (lr, lc)), shape=(len(le_rhs), nb)).tocsr()
    Atr = coo_matrix((np.ones(len(tr_)), (tr_, tc)), shape=(nt, nb)).tocsr()
    return Aeq, np.array(eq_rhs, float), Ale, np.array(le_rhs, float), Atr, le_rows

def residual_lp(P, B0, sel_blocks):
    """linear screen of what is left inside N after the chosen blocks (blocks without positive only)"""
    r, dZ = P["r"], P["dZ"]
    cov = sel_blocks.T @ sel_blocks
    rows = {}; rhs = []
    for s in range(3, 28): rows[(s,)] = len(rhs); rhs.append(dZ[s] - cov[s, s])
    for s in range(3, 28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: rows[(s, t)] = len(rhs); rhs.append(r[s][t] - cov[s, t])
    if min(rhs) < 0: return "infeasible"
    # a block without positive may not share 3 points with a chosen block
    ok = (B0 @ sel_blocks.T).max(axis=1) <= 2
    Bq = B0[ok]; rr, cc = [], []; trip = {}
    for j in range(len(Bq)):
        pts = np.nonzero(Bq[j])[0].tolist()
        for s in pts: rr.append(rows[(s,)]); cc.append(j)
        for q in itertools.combinations(pts, 2): rr.append(rows[q]); cc.append(j)
        for q in itertools.combinations(pts, 3): trip.setdefault(q, []).append(j)
    A = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(rhs), len(Bq))).tocsr()
    tr_, tc = [], []; nt = 0
    for q, lst in trip.items():
        if len(lst) >= 2: tr_ += [nt] * len(lst); tc += lst; nt += 1
    Aub = coo_matrix((np.ones(len(tr_)), (tr_, tc)), shape=(nt, len(Bq))).tocsr() if nt else None
    res = linprog(np.zeros(len(Bq)), A_ub=Aub, b_ub=(np.ones(nt) if nt else None), A_eq=A, b_eq=np.array(rhs, float), bounds=(0, 1), method="highs")
    return "feasible" if res.status == 0 else ("infeasible" if res.status == 2 else f"status {res.status}")

def run(d, rounds=30, tl=300, seed=1, verbose=True):
    t0 = time.time(); P, Bp, B0 = setup(d)
    Aeq, beq, Ale, ble, Atr, _ = master_matrices(P, Bp); nb = len(Bp)
    cons = [LinearConstraint(Aeq, beq, beq), LinearConstraint(Ale, -np.inf, ble), LinearConstraint(Atr, -np.inf, 1)]
    cuts = []; rng = np.random.default_rng(seed)
    if verbose: print(f"support {d['id']} (delta {d['delta']}): {nb} blocks with a positive, {len(B0)} without; {len(beq)} equalities  [{time.time()-t0:.0f}s]", flush=True)
    for it in range(rounds):
        cc = list(cons)
        if cuts: cc.append(LinearConstraint(csr_matrix(np.array(cuts, float)), -np.inf, [c.sum() - 1 for c in cuts]))
        res = milp(rng.random(nb), constraints=cc, integrality=np.ones(nb), bounds=Bounds(0, 1), options={"time_limit": tl})
        if res.status == 2: return "no three-star", it, time.time() - t0, None
        if res.x is None: return f"master status {res.status}", it, time.time() - t0, None
        x = (res.x > 0.5); sel = Bp[x]
        st = residual_lp(P, B0, sel)
        if verbose: print(f"   round {it}: three-star with {int(x.sum())} blocks; residual screen: {st}  [{time.time()-t0:.0f}s]", flush=True)
        if st == "feasible": return "three-star with feasible residual", it, time.time() - t0, sel
        cuts.append(x.astype(np.int64))
    return "undecided", rounds, time.time() - t0, None

if __name__ == "__main__":
    fn = sys.argv[1]; sid = int(sys.argv[2]); R = int(sys.argv[3]) if len(sys.argv) > 3 else 30; TL = float(sys.argv[4]) if len(sys.argv) > 4 else 300
    d = I.load(fn, sid); st, it, t, sel = run(d, R, TL)
    print(f"support {sid}: {st} after {it} round(s)  [{t:.0f}s]")
    if sel is not None: json.dump({"id": sid, "blocks": [[int(v) for v in np.nonzero(b)[0]] for b in sel]}, open(f"skeleton_{sid}.json", "w"))
