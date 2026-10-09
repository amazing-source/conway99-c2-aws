"""P3/N25, stage 1.5 (experiment): pair conflicts between blocks from the two Gram matrices, used as cutting planes.

Two outside vertices z, z' with blocks B, B' are adjacent or not.  With G_E = 3I - A + J/9 and G_F = 4I + A - (2/11)J on S u {z, z'}:
the residuals of z, z' orthogonal to the span of S have norms sigma(B), sigma(B') (Schur complements) and inner product
     g = G_zz' - c_B^T G_S^+ c_B'         (G_zz' = -8/9 or 1/9 for E;  1 - 2/11 or -2/11 for F),
and Cauchy-Schwarz g^2 <= sigma sigma' must hold on BOTH sides for the SAME adjacency.  Also |B inter B'| <= 1 if adjacent, <= 2 if not.
If neither adjacency is possible, x_B + x_B' <= 1.     usage: p3n25_cuts.py register.jsonl id [rounds]"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, vstack, csr_matrix
import p3n25_ilp as I, p3n25_lp2 as L2
TOL = 1e-7
fn, sid = sys.argv[1], int(sys.argv[2]); ROUNDS = int(sys.argv[3]) if len(sys.argv) > 3 else 6
d = I.load(fn, sid); t0 = time.time()
adj, r, dZ, Ms, n0, info = L2.filtered_masks(d); nb = len(Ms)
A = np.zeros((28, 28))
for a, b in d["edges"]: A[a, b] = A[b, a] = 1.0
Bm = np.array([[(B >> s) & 1 for s in range(28)] for B in Ms], dtype=float)
GE = 3 * np.eye(28) - A + np.ones((28, 28)) / 9; GF = 4 * np.eye(28) + A - 2 * np.ones((28, 28)) / 11
GEi = np.linalg.pinv(GE, rcond=1e-10); GFi = np.linalg.pinv(GF, rcond=1e-10)
CE = -Bm + 1 / 9; CF = Bm - 2 / 11
sE = (3 + 1 / 9) - np.einsum("ij,jk,ik->i", CE, GEi, CE); sF = (4 - 2 / 11) - np.einsum("ij,jk,ik->i", CF, GFi, CF)
print(f"support id {sid}: {nb} blocks; sigma_E: min {sE.min():.3f} mean {sE.mean():.3f} max {sE.max():.3f}; sigma_F: min {sF.min():.3f} mean {sF.mean():.3f} max {sF.max():.3f}; "
      f"blocks with sigma_E < 1e-6: {(sE < 1e-6).sum()}, sigma_F < 1e-6: {(sF < 1e-6).sum()}", flush=True)
# base LP
pair_row = {}; row = 0; rhs = []
for s in range(28):
    for t in range(s + 1, 28):
        if r[s][t] > 0: pair_row[(s, t)] = row; rhs.append(r[s][t]); row += 1
prow = list(range(row, row + 28)); rhs += dZ; neq = row + 28
r_, c_ = [], []; trip = {}
for i, B in enumerate(Ms):
    pts = [s for s in range(28) if (B >> s) & 1]
    for s in pts: r_.append(prow[s]); c_.append(i)
    for pr in itertools.combinations(pts, 2): r_.append(pair_row[pr]); c_.append(i)
    for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
Aeq = coo_matrix((np.ones(len(r_)), (r_, c_)), shape=(neq, nb)).tocsr(); beq = np.array(rhs, dtype=float)
r2, c2 = [], []; ntr = 0
for tr, lst in trip.items():
    if len(lst) >= 2:
        for i in lst: r2.append(ntr); c2.append(i)
        ntr += 1
Aub = coo_matrix((np.ones(len(r2)), (r2, c2)), shape=(ntr, nb)).tocsr(); bub = np.ones(ntr)
def conflicts(idx):
    """boolean matrix: pairs (i, j) of idx that cannot coexist"""
    BE = CE[idx]; BF = CF[idx]; Bi = Bm[idx]
    inter = Bi @ Bi.T
    gE0 = BE @ GEi @ BE.T; gF0 = BF @ GFi @ BF.T
    se = sE[idx]; sf = sF[idx]
    capE = np.sqrt(np.maximum(np.outer(se, se), 0)) + TOL; capF = np.sqrt(np.maximum(np.outer(sf, sf), 0)) + TOL
    ok_adj = (inter <= 1) & (np.abs(-8 / 9 - gE0) <= capE) & (np.abs(1 - 2 / 11 - gF0) <= capF)
    ok_non = (inter <= 2) & (np.abs(1 / 9 - gE0) <= capE) & (np.abs(-2 / 11 - gF0) <= capF)
    conf = ~(ok_adj | ok_non); np.fill_diagonal(conf, False)
    return conf, ok_adj, ok_non
cuts_r, cuts_c, ncut = [], [], 0
for rnd in range(ROUNDS):
    Au = vstack([Aub, coo_matrix((np.ones(len(cuts_r)), (cuts_r, cuts_c)), shape=(ncut, nb)).tocsr()]).tocsr() if ncut else Aub
    bu = np.ones(ntr + ncut)
    t1 = time.time()
    res = linprog(np.zeros(nb), A_ub=Au, b_ub=bu, A_eq=Aeq, b_eq=beq, bounds=(0, 1), method="highs-ipm", options={"time_limit": 300})
    if res.status == 2: print(f"round {rnd}: LP INFEASIBLE with {ncut} conflict cuts  [{time.time()-t0:.0f}s]"); break
    if res.status != 0: print(f"round {rnd}: LP status {res.status}"); break
    x = res.x; idx = np.where(x > 1e-6)[0]
    conf, ok_adj, ok_non = conflicts(idx)
    ii, jj = np.where(np.triu(conf, 1))
    viol = [(idx[i], idx[j]) for i, j in zip(ii, jj) if x[idx[i]] + x[idx[j]] > 1 + 1e-6]
    print(f"round {rnd}: LP feasible, support {len(idx)} blocks, conflicting pairs in the support {len(ii)}, violated {len(viol)}; "
          f"pairs forced adjacent {int((ok_adj & ~ok_non).sum() // 2)}, forced non-adjacent {int((ok_non & ~ok_adj).sum() // 2)}  [{time.time()-t0:.0f}s]", flush=True)
    # add all conflicts found in the support as cuts (not only the violated ones), up to a limit
    added = 0
    for i, j in zip(ii, jj):
        cuts_r += [ncut, ncut]; cuts_c += [idx[i], idx[j]]; ncut += 1; added += 1
        if added >= 200000: break
    if not len(ii): break
