"""STAR LOOK-AHEAD ON A FORCED OUTSIDE VERTEX.

An edge {s, t} of the support with r(s,t) = 1 has its triangle outside: a vertex z exists with s, t in its block.  For each candidate
block B of z (after the level-2 filters) the base graph G = S u {z} is known; the star engine is run for each positive over G.
If some positive has no star, the block is impossible.  If every candidate block of z is impossible, the support is impossible.
usage: apex_star.py workers id [id ...]"""
import sys, json, time, random, itertools
from multiprocessing import Pool
import numpy as np
import p3n25_ilp as I, level2_cert as LC, shell_ext as SE
FN = "register/supports_open_4581.jsonl"

def job(args):
    sid, B, seed = args; d = I.load(FN, sid); rng = random.Random(seed)
    G = np.zeros((29, 29), dtype=np.int64)
    for x, y in d["edges"]: G[x, y] = G[y, x] = 1
    for s in B: G[28, s] = G[s, 28] = 1
    pos_in = [p for p in range(3) if p in B]
    for c in range(3):
        if c in pos_in: continue                                    # z adjacent to c: the star of c would have to contain z (not handled here)
        S = SE.GenStar(G, c); st, it, Ap = S.run(rng, rounds=40, tl=60, workers=1, percut=4)
        if st == "no star": return B, c, len(S.cuts), "dead"
        if st != "shell without witness": return B, c, len(S.cuts), st
    return B, None, 0, "alive"

if __name__ == "__main__":
    NW = int(sys.argv[1])
    for sid in map(int, sys.argv[2:]):
        d = I.load(FN, sid); t0 = time.time()
        P, wit, alive, cover, full, dead_pairs, dead_points = LC.certificate(d)
        A = P["A"]; r = P["r"]; Bm = P["Bm"]
        cands = sorted((int(cover[s, t]), s, t) for s in range(28) for t in range(s + 1, 28) if A[s, t] and r[s][t] == 1)
        if not cands: print(f"support {sid}: no edge with outside triangle"); continue
        nb, s, t = cands[0]
        blocks = [[int(v) for v in np.nonzero(Bm[j])[0]] for j in range(len(Bm)) if alive[j] and Bm[j, s] and Bm[j, t]]
        with Pool(NW) as pl: out = pl.map(job, [(sid, B, 7 * k + 1) for k, B in enumerate(blocks)], chunksize=2)
        import collections
        c = collections.Counter(o[3] for o in out)
        print(f"support {sid} (delta {d['delta']}): edge ({s},{t}), {len(blocks)} candidate blocks for the triangle vertex: {dict(c)}; "
              f"cuts in the deaths: {sorted(collections.Counter(o[2] for o in out if o[3] == 'dead').items())}  [{time.time()-t0:.0f}s]", flush=True)
        json.dump([[o[0], o[1], o[2], o[3]] for o in out], open(f"apex_star_{sid}.json", "w"))
