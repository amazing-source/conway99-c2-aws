"""Microscopic study, step 2: SPARSE certificate of a killed support.

Dual LP:  y = yp - ym (one multiplier per pair row and per point row),  minimise sum(yp + ym)  subject to
     for every admissible block B:  sum of y over the rows of B >= 0,        y . b <= -1.
The l1-minimal multiplier vector is usually supported on few rows: they show WHICH pairs and points make the support impossible.
usage: micro2.py id [id ...]"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack
import p3n25_ilp as I, p3n25_batch as PB

def sparse_cert(d):
    adj, r, dZ, Ms = PB.blocks_F1(d); nb = len(Ms)
    rows = []
    for s in range(28):
        for t in range(s + 1, 28):
            if r[s][t] > 0: rows.append(("pair", s, t))
    pair_row = {(rw[1], rw[2]): k for k, rw in enumerate(rows)}
    prow = {s: len(rows) + s for s in range(28)}
    rows += [("point", s) for s in range(28)]
    b = np.array([r[rw[1]][rw[2]] if rw[0] == "pair" else dZ[rw[1]] for rw in rows], dtype=float); nr = len(rows)
    rr, cc = [], []
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        for s in pts: rr.append(i); cc.append(prow[s])
        for pr in itertools.combinations(pts, 2): rr.append(i); cc.append(pair_row[pr])
    Acol = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(nb, nr)).tocsr()          # block x row incidence
    # variables (yp, ym) >= 0:  -Acol (yp - ym) <= 0 ;  b.(yp - ym) <= -1
    A1 = hstack([-Acol, Acol]).tocsr()
    A2 = coo_matrix(np.concatenate([b, -b]).reshape(1, -1))
    from scipy.sparse import vstack
    Aub = vstack([A1, A2]).tocsr(); bub = np.concatenate([np.zeros(nb), [-1.0]])
    res = linprog(np.ones(2 * nr), A_ub=Aub, b_ub=bub, bounds=(0, None), method="highs")
    if res.status != 0: return None, rows, adj, r, dZ
    y = res.x[:nr] - res.x[nr:]
    return y, rows, adj, r, dZ

if __name__ == "__main__":
    for sid in map(int, sys.argv[1:]):
        d = I.load("register/supports_open_4581.jsonl", sid); t0 = time.time()
        y, rows, adj, r, dZ = sparse_cert(d)
        lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
        if y is None: print(f"support {sid}: dual LP failed"); continue
        nz = [(k, y[k]) for k in range(len(y)) if abs(y[k]) > 1e-9]
        scale = min(abs(v) for _, v in nz)
        pts = sorted({s for k, _ in nz for s in rows[k][1:]})
        print(f"\nsupport {sid} (delta {d['delta']}, paths {d['path_counts']}): l1-minimal certificate uses {len(nz)} rows of {len(y)}, on {len(pts)} vertices  [{time.time()-t0:.0f}s]")
        print("   vertices:", " ".join(lab(s) for s in pts))
        print("   edges of the support among them:", " ".join(f"{lab(a)}-{lab(b)}" for a, b in d["edges"] if a in pts and b in pts))
        for k, v in sorted(nz, key=lambda kv: (rows[kv[0]][0] != "point", -abs(kv[1]))):
            rw = rows[k]
            if rw[0] == "point": print(f"      {v/scale:+8.3f}  point {lab(rw[1])}  (needs {dZ[rw[1]]} blocks)")
            else: print(f"      {v/scale:+8.3f}  pair {lab(rw[1])} , {lab(rw[2])}  (r = {r[rw[1]][rw[2]]}{', adjacent' if (adj[rw[1]] >> rw[2]) & 1 else ''})")
