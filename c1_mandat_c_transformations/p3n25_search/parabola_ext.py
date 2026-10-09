"""The integer parabola lemma on S u {z}: a filter on the blocks that uses the neighbours of z outside S.

For an outside vertex z with block B, the set S' = S u {z} has: dZ'(s) = dZ(s) - [s in B], r'(s,t) = r(s,t) - [s,t in B],
dZ'(z) = 14 - |B|, r'(z, s) = kappa_B(s) = (1 if s in B else 2) - |adj(s) inter B|, and 70 outside vertices.
If some integer (w, w_z, a) gives Phi' < 0, the block B cannot occur.   Test on a sample of blocks of one support.
usage: parabola_ext.py id [sample]"""
import sys, json, random, time
import numpy as np
import p3n25_ilp as I, p3n25_batch as PB
sid = int(sys.argv[1]); SAMPLE = int(sys.argv[2]) if len(sys.argv) > 2 else 100
d = I.load("register/supports_open_4581.jsonl", sid)
adj, r, dZ, Ms = PB.blocks_F1(d)
A = np.zeros((28, 28), dtype=np.int64)
for a_, b_ in d["edges"]: A[a_, b_] = A[b_, a_] = 1
R = np.array(r, dtype=np.int64); dv = np.array(dZ, dtype=np.int64)
rng = random.Random(3); t0 = time.time()
def ext_data(B):
    b = np.array([(B >> s) & 1 for s in range(28)], dtype=np.int64)
    kap = np.where(b > 0, 1, 2) - A @ b
    R2 = np.zeros((29, 29), dtype=np.int64); R2[:28, :28] = R - np.outer(b, b) * (1 - np.eye(28, dtype=np.int64))
    R2[28, :28] = kap; R2[:28, 28] = kap
    d2 = np.concatenate([dv - b, [14 - int(b.sum())]])
    return R2, d2
def phi(w, a, R2, d2): return int((w * w - (2 * a + 1) * w) @ d2 + w @ R2 @ w + 70 * a * (a + 1))
def search(R2, d2, restarts=25, wmax=2):
    M = np.diag(d2) + R2; Mp = np.linalg.pinv(M.astype(float)); best = (10 ** 9, None, None)
    for a in (0, 1, -1):
        for k in range(restarts):
            if k == 0: w = np.clip(np.round((2 * a + 1) / 2 * (Mp @ d2)), -wmax, wmax).astype(np.int64)
            else: w = np.array([rng.choice([0, 0, 0, 1, 1, -1]) for _ in range(29)], dtype=np.int64)
            val = phi(w, a, R2, d2); improved = True
            while improved:
                improved = False; g = M @ w
                for s in rng.sample(range(29), 29):
                    for step in (1, -1):
                        if abs(w[s] + step) > wmax: continue
                        dl = 2 * step * int(g[s]) + int(M[s, s]) - (2 * a + 1) * step * int(d2[s])
                        if dl < 0: w[s] += step; val += dl; g = M @ w; improved = True; break
            if val < best[0]: best = (val, w.copy(), a)
            if best[0] < 0: return best
    return best
idxs = rng.sample(range(len(Ms)), min(SAMPLE, len(Ms))); dead = 0; withz = 0
for i in idxs:
    R2, d2 = ext_data(Ms[i]); val, w, a = search(R2, d2)
    if val < 0: dead += 1; withz += int(w[28] != 0)
print(f"support {sid}: {len(Ms)} blocks; sample {len(idxs)}: blocks with a parabola witness on S u {{z}}: {dead} ({withz} with w_z != 0)  [{time.time()-t0:.0f}s]")
