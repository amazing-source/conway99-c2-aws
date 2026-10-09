"""THE INTEGER PARABOLA LEMMA and its test on the supports killed by the linear screen.

Lemma.  Let S be a set of vertices of an srg(99,14,1,2), Z its complement, dZ(s) = 14 - deg_S(s) and, for s != t in S,
r(s,t) = (1 if s ~ t else 2) - (number of common neighbours of s, t inside S).  For every integer weighting w of S and every
integer a,
     Phi(w, a) := sum_s (w_s^2 - (2a+1) w_s) dZ(s) + 2 sum_{s<t} w_s w_t r(s,t) + |Z| a (a+1)  >=  0.
Proof.  For z in Z put t_z = sum of w_s over the neighbours s of z in S: an INTEGER.  Counting incidences, sum_z t_z = sum_s w_s dZ(s)
and sum_z t_z^2 = sum_s w_s^2 dZ(s) + 2 sum_{s<t} w_s w_t r(s,t).  Hence Phi(w,a) = sum_z (t_z - a)(t_z - a - 1), and an integer times
the next integer is >= 0.  QED
A pair (w, a) with Phi(w, a) < 0 is a certificate that the induced graph on S cannot occur; it is checked by a few additions.

This script searches such a witness for every killed support (local search on integer weights) and checks that none is found on
the survivors.         usage: parabola.py [wmax]"""
import sys, json, glob, time, itertools, random, pickle
import numpy as np
import p3n25_ilp as I

def data(d):
    adj, r, dZ = I.boundary(d["edges"])
    R = np.array(r, dtype=np.int64); dv = np.array(dZ, dtype=np.int64)
    return adj, R, dv

def phi(w, a, R, dv, nz=71):
    w = np.asarray(w, dtype=np.int64)
    return int((w * w - (2 * a + 1) * w) @ dv + w @ R @ w + nz * a * (a + 1))

def search(R, dv, rng, wmax=2, restarts=40, seeds=()):
    M = np.diag(dv) + R                                      # Phi = w^T M w - (2a+1) dv.w + 71 a(a+1)
    best = (10 ** 9, None, None)
    Mp = np.linalg.pinv(M.astype(float))
    for a in (0, 1, -1, 2):
        starts = [np.clip(np.round((2 * a + 1) / 2 * (Mp @ dv)), -wmax, wmax).astype(np.int64)] + [np.array(s, dtype=np.int64) for s in seeds]
        for k in range(restarts):
            w = starts[k].copy() if k < len(starts) else np.array([rng.choice([0, 0, 0, 1, 1, -1]) for _ in range(28)], dtype=np.int64)
            val = phi(w, a, R, dv)
            improved = True
            while improved:
                improved = False
                g = M @ w
                for s in rng.sample(range(28), 28):
                    for step in (1, -1):
                        if abs(w[s] + step) > wmax: continue
                        # change of Phi when w_s -> w_s + step
                        dl = 2 * step * int(g[s]) + int(M[s, s]) - (2 * a + 1) * step * int(dv[s])
                        if dl < 0:
                            w[s] += step; val += dl; g = M @ w; improved = True; break
            if val < best[0]: best = (val, w.copy(), a)
    return best

if __name__ == "__main__":
    WMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    reg = {}
    for line in open("register/supports_open_4581.jsonl", encoding="utf-8"):
        d = json.loads(line); reg[d["id"]] = d
    res = {}
    for f in glob.glob("phaseA/chunk_*.jsonl"):
        for l in open(f):
            rr = json.loads(l); res[rr["id"]] = rr["status"]
    rng = random.Random(7); t0 = time.time()
    dead = sorted(s for s in res if res[s] == "infeasible"); alive = sorted(s for s in res if res[s] == "feasible")
    out = {}; nexp = 0
    for sid in dead:
        adj, R, dv = data(reg[sid])
        val, w, a = search(R, dv, rng, WMAX)
        assert phi(w, a, R, dv) == val
        out[sid] = (val, w.tolist(), a); nexp += val < 0
    print(f"killed supports: {len(dead)};  with an integer-parabola witness (Phi < 0): {nexp};  without: {len(dead) - nexp}  [{time.time()-t0:.0f}s]")
    rest = [s for s in dead if out[s][0] >= 0]; print("   not explained:", rest[:40])
    import collections
    print("   values of a used:", sorted(collections.Counter(out[s][2] for s in dead if out[s][0] < 0).items()))
    print("   largest |w_s| in the witnesses:", sorted(collections.Counter(int(max(abs(x) for x in out[s][1])) for s in dead if out[s][0] < 0).items()))
    print("   number of non-zero weights:", sorted(collections.Counter(sum(1 for x in out[s][1] if x) for s in dead if out[s][0] < 0).items()))
    print("   value of Phi:", sorted(collections.Counter(out[s][0] for s in dead if out[s][0] < 0).items()))
    bad = 0
    for sid in alive[:400]:
        adj, R, dv = data(reg[sid]); val, w, a = search(R, dv, rng, WMAX, restarts=12)
        bad += val < 0
    print(f"   survivors checked: {min(400, len(alive))}; witnesses found among them (must be 0): {bad}")
    pickle.dump(out, open("parabola_dead.pkl", "wb"))
