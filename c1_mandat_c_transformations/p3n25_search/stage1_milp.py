"""STAGE 1 IN INTEGERS for one support: choose 71 blocks (0/1) meeting every pair row and point row, two blocks sharing at most 2 points
(triple rows).  Branch-and-cut (HiGHS) on the blocks left by the level-2 filters.  A solution found is re-checked by direct counting and
saved; 'infeasible' from the solver is only an indication (no certificate).
usage: stage1_milp.py register.jsonl id seed time_limit"""
import sys, json, time, itertools, random
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
import p3n25_ilp as I, level2 as L2

fn, sid, seed, TL = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
d = I.load(fn, sid); t0 = time.time()
P = L2.prepare(d); pool = L2.make_pool(P["R"], P["dv"], random.Random(5)); c1, c2, pk = L2.filter_blocks(P, pool); keep = ~(c1 | c2 | pk)
Ms = [B for B, k in zip(P["Ms"], keep) if k]; r, dZ = P["r"], P["dZ"]; nb = len(Ms)
pair_row = {}; rhs = []
for s in range(28):
    for t in range(s + 1, 28):
        if r[s][t] > 0: pair_row[(s, t)] = len(rhs); rhs.append(r[s][t])
npair = len(rhs); rhs += list(dZ)
rr, cc = [], []; trip = {}
for i, B in enumerate(Ms):
    pts = [s for s in range(28) if (B >> s) & 1]
    for s in pts: rr.append(npair + s); cc.append(i)
    for pr in itertools.combinations(pts, 2): rr.append(pair_row[pr]); cc.append(i)
    for tr in itertools.combinations(pts, 3): trip.setdefault(tr, []).append(i)
Aeq = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(rhs), nb)).tocsr()
r2, c2_ = [], []; ntr = 0
for tr, lst in trip.items():
    if len(lst) >= 2: r2 += [ntr] * len(lst); c2_ += lst; ntr += 1
Aub = coo_matrix((np.ones(len(r2)), (r2, c2_)), shape=(ntr, nb)).tocsr()
rng = np.random.default_rng(seed)
cost = rng.random(nb) if seed else np.zeros(nb)
print(f"support {sid}: {nb} blocks, {len(rhs)} equalities, {ntr} triple rows; seed {seed}  [{time.time()-t0:.0f}s]", flush=True)
res = milp(cost, constraints=[LinearConstraint(Aeq, rhs, rhs), LinearConstraint(Aub, -np.inf, 1)], integrality=np.ones(nb), bounds=Bounds(0, 1),
           options={"time_limit": TL, "disp": False})
print(f"   status {res.status} ({res.message.strip()[:90]})  [{time.time()-t0:.0f}s]", flush=True)
if res.x is not None:
    sel = [Ms[i] for i in range(nb) if res.x[i] > 0.5]
    # direct re-check
    ok = len(sel) == 71
    for s in range(28):
        ok &= sum((B >> s) & 1 for B in sel) == dZ[s]
        for t in range(s + 1, 28): ok &= sum(((B >> s) & 1) & ((B >> t) & 1) for B in sel) == r[s][t]
    for B, C in itertools.combinations(sel, 2): ok &= bin(B & C).count("1") <= 2
    print(f"   integer solution with {len(sel)} blocks; direct re-check: {ok}", flush=True)
    json.dump({"id": sid, "seed": seed, "blocks": sel, "checked": bool(ok)}, open(f"stage1_sol_{sid}_{seed}.json", "w"))
