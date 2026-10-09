"""LIFTED SCREEN: fix one outside vertex z with block B and ask the linear screen for the 29-vertex set S u {z}.

The 70 other outside vertices z' carry a block B' in S and a bit eps = [z' ~ z].  Admissible (B', eps):
   eps = 0:  |B inter B'| <= 2;
   eps = 1:  |B inter B'| <= 1; a common point s is unmatched in B and in B' (triangle z z' s); every s in B \ B' has at most one
             neighbour in B'; every s in B' has kappa_B(s) >= 1.
Rows:  pairs of S: sum = r(s,t) - [s,t in B];   points of S: sum = dZ(s) - [s in B];   pairs (s, z): sum over eps = 1 and B' containing s
= kappa_B(s);   point z: sum over eps = 1 = 14 - |B|;   triples of S: <= 1;   triples (s, t, z): sum over eps = 1, B' containing s, t <= 1.
If this LP is infeasible, no outside vertex has block B.          usage: lift.py register.jsonl id [nsample] [workers]"""
import sys, json, time, itertools, random, pickle, os
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, csc_matrix, hstack, vstack
import p3n25_ilp as I, level2 as L2

def base(P, keep):
    idx = np.nonzero(keep)[0]; Bm = P["Bm"][idx]; nb = len(idx); r = P["r"]
    pair_id = {}; rhs = []
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: pair_id[(s, t)] = len(rhs); rhs.append(r[s][t])
    pr, pc, tr_, tc = [], [], [], []; trip = {}
    for j in range(nb):
        pts = np.nonzero(Bm[j])[0].tolist()
        for q in itertools.combinations(pts, 2): pr.append(pair_id[q]); pc.append(j)
        for q in itertools.combinations(pts, 3):
            k = trip.setdefault(q, len(trip)); tr_.append(k); tc.append(j)
    Apair = coo_matrix((np.ones(len(pr)), (pr, pc)), shape=(len(rhs), nb)).tocsc()
    Atri = coo_matrix((np.ones(len(tr_)), (tr_, tc)), shape=(len(trip), nb)).tocsc()
    Apt = csc_matrix(Bm.T.astype(float))
    AB = Bm @ P["A"]; Um = Bm * (AB == 0)
    return {"idx": idx, "Bm": Bm, "pair_id": pair_id, "pair_rhs": np.array(rhs, dtype=float), "trip": trip, "Apair": Apair, "Atri": Atri, "Apt": Apt,
            "AB": AB, "Um": Um, "kap": P["kap"][idx], "dz": P["dz"][idx], "dZ": np.array(P["dZ"], dtype=float)}

def lift(Bs, j, time_limit=200, alive=None):
    Bm, AB, Um = Bs["Bm"], Bs["AB"], Bs["Um"]; nb = len(Bm); b = Bm[j]; kapB = Bs["kap"][j]; dz = int(Bs["dz"][j])
    if (kapB < 0).any(): return "infeasible", None
    c = Bm @ b
    ok = np.ones(nb, dtype=bool) if alive is None else alive.copy()
    ok[j] = False
    c0 = ok & (c <= 2)
    common = Bm * b[None, :]
    c1 = ok & (c <= 1) & ((common * (1 - Um * Um[j][None, :])).sum(axis=1) == 0)
    c1 &= (((AB > 1) & (b[None, :] == 1) & (Bm == 0)).sum(axis=1) == 0)
    c1 &= ((Bm * (kapB[None, :] <= 0)).sum(axis=1) == 0)
    i0 = np.nonzero(c0)[0]; i1 = np.nonzero(c1)[0]; n0, n1 = len(i0), len(i1)
    # equalities
    inB = b.astype(float)
    pair_rhs = Bs["pair_rhs"].copy()
    pts = np.nonzero(b)[0].tolist()
    for q in itertools.combinations(pts, 2): pair_rhs[Bs["pair_id"][q]] -= 1
    Apair = hstack([Bs["Apair"][:, i0], Bs["Apair"][:, i1]]); Apt = hstack([Bs["Apt"][:, i0], Bs["Apt"][:, i1]])
    Z0 = csc_matrix((28, n0)); Az = hstack([Z0, Bs["Apt"][:, i1]])
    Arow = hstack([csc_matrix((1, n0)), csc_matrix(np.ones((1, n1)))])
    Aeq = vstack([Apair, Apt, Az, Arow]).tocsr()
    beq = np.concatenate([pair_rhs, Bs["dZ"] - inB, kapB.astype(float), [float(dz)]])
    Atri = hstack([Bs["Atri"][:, i0], Bs["Atri"][:, i1]]).tocsr()
    nzr = np.diff(Atri.indptr) >= 2; Atri = Atri[nzr]
    Ap1 = hstack([csc_matrix((Bs["Apair"].shape[0], n0)), Bs["Apair"][:, i1]]).tocsr()
    nz2 = np.diff(Ap1.indptr) >= 2; Ap1 = Ap1[nz2]
    Aub = vstack([Atri, Ap1]).tocsr()
    res = linprog(np.zeros(n0 + n1), A_ub=Aub, b_ub=np.ones(Aub.shape[0]), A_eq=Aeq, b_eq=beq, bounds=(0, 1), method="highs-ipm",
                  options={"time_limit": time_limit})
    st = "feasible" if res.status == 0 else ("infeasible" if res.status == 2 else f"status {res.status}")
    return st, (n0, n1)

_G = {}
def _init(fn):
    _G["Bs"] = pickle.load(open(fn, "rb"))
def _job(j):
    t0 = time.time(); st, sz = lift(_G["Bs"], j)
    return j, st, sz, time.time() - t0

if __name__ == "__main__":
    from multiprocessing import Pool
    fn, sid = sys.argv[1], int(sys.argv[2]); NS = int(sys.argv[3]) if len(sys.argv) > 3 else 36; NW = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    rng = random.Random(11); d = I.load(fn, sid); t0 = time.time()
    P = L2.prepare(d); pool = L2.make_pool(P["R"], P["dv"], random.Random(5)); c1, c2, pk = L2.filter_blocks(P, pool); keep = ~(c1 | c2 | pk)
    Bs = base(P, keep); pf = f"lift_base_{sid}.pkl"; pickle.dump(Bs, open(pf, "wb"))
    Bm = Bs["Bm"]; nb = len(Bm); size = Bm.sum(axis=1); npos = Bm[:, :3].sum(axis=1)
    print(f"support {sid} (delta {d['delta']}): {nb} blocks after the level-2 filters; by number of positives: "
          f"{[int((npos == k).sum()) for k in range(4)]}  [{time.time()-t0:.0f}s]", flush=True)
    sample = []
    for k in range(4):
        cand = [j for j in range(nb) if npos[j] == k]; rng.shuffle(cand); sample += cand[:NS // 4 if k else NS // 4 + NS % 4]
    with Pool(NW, initializer=_init, initargs=(pf,)) as pl:
        out = pl.map(_job, sample, chunksize=1)
    for k in range(4):
        rs = [o for o in out if npos[o[0]] == k]
        if rs: print(f"   blocks with {k} positive(s): {len(rs)} tried, infeasible {sum(o[1] == 'infeasible' for o in rs)}, feasible {sum(o[1] == 'feasible' for o in rs)}, "
                     f"other {sum(o[1] not in ('feasible', 'infeasible') for o in rs)}; mean time {np.mean([o[3] for o in rs]):.0f}s; columns {rs[0][2]}", flush=True)
    json.dump([[int(o[0]), o[1]] for o in out], open(f"lift_sample_{sid}.json", "w"))
