"""LEVEL 2: the two lemmas applied to S u {z}, as exact filters on the blocks, then the linear screen on the surviving blocks.

For an outside vertex z with block B (indicator b), d_z = 14 - |B| and kappa_B(s) = (1 if s in B else 2) - |adj(s) inter B| is the
number of common neighbours of z and s OUTSIDE S (so: among the other outside vertices).

(P)  Lemma A on S u {z} with weights (w, w_z):
        Phi'(w, w_z, a) = Phi(w, a) - (w.b - a)(w.b - a - 1) + d_z w_z^2 + w_z (2 w.kappa_B - (2a+1) d_z)   >= 0.
     For a pool of pairs (w, a) with small Phi(w, a), the best integer w_z is taken; a negative value kills the block.
(C1) Lemma B on S u {z} with v = z, X = B, u outside B:   sum_{x in B} r(u,x) <= 2 (dZ(u) - kappa_B(u)) + min(kappa_B(u), unmatched(B)).
(C2) Lemma B with u = z, X = N_S(v):   v outside B:  sum_{x ~ v} kappa_B(x) <= 2 (d_z - kappa_B(v)) + min(kappa_B(v), #{x ~ v: r(v,x) = 1});
                                        v in B:       sum_{x ~ v} kappa_B(x) <= d_z - kappa_B(v).
All tests are in integer arithmetic.      usage: level2.py register.jsonl id [id ...]"""
import sys, json, time, itertools, random
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import p3n25_ilp as I, p3n25_batch as PB, parabola as PA

def prepare(d):
    adj, r, dZ, Ms = PB.blocks_F1(d)
    A = np.zeros((28, 28), dtype=np.int64)
    for a_, b_ in d["edges"]: A[a_, b_] = A[b_, a_] = 1
    R = np.array(r, dtype=np.int64); dv = np.array(dZ, dtype=np.int64)
    Bm = np.array([[(B >> s) & 1 for s in range(28)] for B in Ms], dtype=np.int64)
    kap = np.where(Bm > 0, 1, 2) - Bm @ A
    dz = 14 - Bm.sum(axis=1)
    unm = (Bm * ((Bm @ A) == 0)).sum(axis=1)
    return {"adj": adj, "r": r, "dZ": dZ, "Ms": Ms, "A": A, "R": R, "dv": dv, "Bm": Bm, "kap": kap, "dz": dz, "unm": unm}

def make_pool(R, dv, rng, thresh=14, restarts=400, wmax=2, cap=4000):
    """pairs (w, a) with 0 <= Phi(w, a) <= thresh, found along coordinate descents (all visited points are kept)"""
    M = np.diag(dv) + R; seen = {}
    def visit(w, a, val):
        if 0 <= val <= thresh and w.any(): seen[(a, tuple(int(x) for x in w))] = val
    for a in (0, 1, -1, 2):
        for k in range(restarts):
            w = np.array([rng.choice([0, 0, 0, 0, 1, 1, -1]) for _ in range(28)], dtype=np.int64)
            val = PA.phi(w, a, R, dv); improved = True
            while improved:
                improved = False; g = M @ w
                for s in rng.sample(range(28), 28):
                    for step in (1, -1):
                        if abs(w[s] + step) > wmax: continue
                        dl = 2 * step * int(g[s]) + int(M[s, s]) - (2 * a + 1) * step * int(dv[s])
                        if dl < 0:
                            w[s] += step; val += dl; g = M @ w; improved = True; visit(w, a, val); break
            visit(w, a, val)
            # neighbours of the local minimum (one flip) are also useful
            g = M @ w
            for s in range(28):
                for step in (1, -1):
                    if abs(w[s] + step) > wmax: continue
                    dl = 2 * step * int(g[s]) + int(M[s, s]) - (2 * a + 1) * step * int(dv[s])
                    if val + dl <= thresh:
                        w2 = w.copy(); w2[s] += step; visit(w2, a, val + dl)
    items = sorted(seen.items(), key=lambda kv: kv[1])[:cap]
    W = np.array([k[1] for k, _ in items], dtype=np.int64).reshape(-1, 28); a = np.array([k[0] for k, _ in items], dtype=np.int64)
    ph = np.array([v for _, v in items], dtype=np.int64)
    return W, a, ph

def filter_blocks(P, pool, chunk=150):
    Bm, kap, dz, unm, R, dv, A = P["Bm"], P["kap"], P["dz"], P["unm"], P["R"], P["dv"], P["A"]
    nb = len(Bm)
    # (C1)
    L = Bm @ R; bound = 2 * (dv[None, :] - kap) + np.minimum(kap, unm[:, None])
    c1 = ((L > bound) & (Bm == 0)).any(axis=1)
    # (C2)
    S2 = kap @ A; n1 = ((R == 1) & (A == 1)).sum(axis=1)
    b_out = 2 * (dz[:, None] - kap) + np.minimum(kap, n1[None, :]); b_in = dz[:, None] - kap
    c2 = (((S2 > b_out) & (Bm == 0)) | ((S2 > b_in) & (Bm == 1))).any(axis=1)
    # (P)
    W, a, ph = pool; pk = np.zeros(nb, dtype=bool)
    BmT = Bm.T; kapT = kap.T
    for i0 in range(0, len(W), chunk):
        Wc = W[i0:i0 + chunk]; ac = a[i0:i0 + chunk][:, None]; pc = ph[i0:i0 + chunk][:, None]
        TB = Wc @ BmT; base = pc - (TB - ac) * (TB - ac - 1)
        CK = 2 * (Wc @ kapT) - (2 * ac + 1) * dz[None, :]
        wz = np.rint(-CK / (2.0 * dz[None, :])).astype(np.int64)
        best = None
        for dlt in (-1, 0, 1):                        # exact integer minimum is at the rounded point; neighbours guard rounding ties
            w2 = wz + dlt; val = dz[None, :] * w2 * w2 + CK * w2
            best = val if best is None else np.minimum(best, val)
        pk |= ((base + best) < 0).any(axis=0)
    return c1, c2, pk

def lp_blocks(P, keep):
    Ms = [B for B, k in zip(P["Ms"], keep) if k]; r, dZ = P["r"], P["dZ"]; nb = len(Ms)
    pair_row = {}; row = 0; rhs = []
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
    prow = list(range(row, row + 28)); rhs += list(dZ); neq = row + 28
    rr, cc = [], []; trip = {}; used = set()
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        for s in pts: rr.append(prow[s]); cc.append(i)
        for pr in itertools.combinations(pts, 2): rr.append(pair_row[pr]); cc.append(i); used.add(pr)
        for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
    if any(pr not in used for pr in pair_row): return "infeasible (uncovered pair)"
    Aeq = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(neq, nb)).tocsr()
    r2, c2 = [], []; ntr = 0
    for tr, lst in trip.items():
        if len(lst) >= 2:
            r2 += [ntr] * len(lst); c2 += lst; ntr += 1
    Aub = coo_matrix((np.ones(len(r2)), (r2, c2)), shape=(ntr, nb)).tocsr() if ntr else None
    res = linprog(np.zeros(nb), A_ub=Aub, b_ub=(np.ones(ntr) if ntr else None), A_eq=Aeq, b_eq=np.array(rhs, dtype=float), bounds=(0, 1),
                  method="highs-ipm", options={"time_limit": 300})
    return "feasible" if res.status == 0 else ("infeasible" if res.status == 2 else f"status {res.status}")

if __name__ == "__main__":
    fn = sys.argv[1]; rng = random.Random(5)
    for sid in map(int, sys.argv[2:]):
        d = I.load(fn, sid); t0 = time.time()
        P = prepare(d); pool = make_pool(P["R"], P["dv"], rng)
        t1 = time.time()
        c1, c2, pk = filter_blocks(P, pool)
        keep = ~(c1 | c2 | pk); t2 = time.time()
        st = lp_blocks(P, keep)
        print(f"support {sid} (delta {d['delta']}): {len(P['Ms'])} blocks; pool {len(pool[0])} (min Phi {int(pool[2].min()) if len(pool[2]) else None}); "
              f"killed by C1 {int(c1.sum())}, C2 {int(c2.sum())}, P {int(pk.sum())}; left {int(keep.sum())}; LP {st}  "
              f"[pool {t1-t0:.0f}s, filter {t2-t1:.0f}s, LP {time.time()-t2:.0f}s]", flush=True)
