"""LEVEL-2 CERTIFICATE of a support: a pair {s, t} of the support that must have r(s,t) >= 1 common neighbours outside, while EVERY
admissible neighbourhood B (in the support) of such a common neighbour z is refuted by Lemma A or Lemma B applied to S u {z}.

Certificate (JSON line): id, pair, and for each admissible block B containing the pair one witness:
     {"B": [...], "k": "A", "w": [28 integers], "h": weight of z, "a": a}        Lemma A on S u {z}:  Phi < 0
     {"B": [...], "k": "B", "u": u, "v": v}      (z is numbered 28)             Lemma B on S u {z} with X = N(v) minus u: violated
The independent checker is level2_check.py.          usage: level2_cert.py register.jsonl out.jsonl id [id ...]"""
import sys, json, time, random
import numpy as np
import p3n25_ilp as I, level2 as L2, parabola as PA

def witnesses(P, pool, chunk=150):
    """for every block: None or a witness (same tests as level2.filter_blocks, keeping the first witness found)"""
    Bm, kap, dz, unm, R, dv, A = P["Bm"], P["kap"], P["dz"], P["unm"], P["R"], P["dv"], P["A"]
    nb = len(Bm); wit = [None] * nb
    L = Bm @ R; bound = 2 * (dv[None, :] - kap) + np.minimum(kap, unm[:, None]); bad = (L > bound) & (Bm == 0)
    for j in np.nonzero(bad.any(axis=1))[0]:
        wit[j] = {"k": "B", "u": int(np.nonzero(bad[j])[0][0]), "v": 28}
    S2 = kap @ A; n1 = ((R == 1) & (A == 1)).sum(axis=1)
    b_out = 2 * (dz[:, None] - kap) + np.minimum(kap, n1[None, :]); b_in = dz[:, None] - kap
    bad = ((S2 > b_out) & (Bm == 0)) | ((S2 > b_in) & (Bm == 1))
    for j in np.nonzero(bad.any(axis=1))[0]:
        if wit[j] is None: wit[j] = {"k": "B", "u": 28, "v": int(np.nonzero(bad[j])[0][0])}
    W, a, ph = pool
    for i in range(len(W)): assert PA.phi(W[i], int(a[i]), R, dv) == int(ph[i])          # the pool values are recomputed directly
    BmT = Bm.T; kapT = kap.T
    for i0 in range(0, len(W), chunk):
        Wc = W[i0:i0 + chunk]; ac = a[i0:i0 + chunk][:, None]; pc = ph[i0:i0 + chunk][:, None]
        TB = Wc @ BmT; base = pc - (TB - ac) * (TB - ac - 1)
        CK = 2 * (Wc @ kapT) - (2 * ac + 1) * dz[None, :]
        wz = np.rint(-CK / (2.0 * dz[None, :])).astype(np.int64)
        best = None; arg = None
        for dlt in (-1, 0, 1):
            w2 = wz + dlt; val = base + dz[None, :] * w2 * w2 + CK * w2
            if best is None: best, arg = val, w2
            else:
                m = val < best; best = np.where(m, val, best); arg = np.where(m, w2, arg)
        neg = best < 0
        for j in np.nonzero(neg.any(axis=0))[0]:
            if wit[j] is None:
                i = int(np.nonzero(neg[:, j])[0][0])
                wit[j] = {"k": "A", "w": [int(x) for x in Wc[i]], "h": int(arg[i, j]), "a": int(ac[i, 0])}
    return wit

def certificate(d, rng=None, **kw):
    P = L2.prepare(d); pool = L2.make_pool(P["R"], P["dv"], rng or random.Random(5), **kw)
    wit = witnesses(P, pool); Bm = P["Bm"]; r = P["r"]
    alive = np.array([w is None for w in wit])
    cover = (Bm[alive].T @ Bm[alive])                                   # number of surviving blocks through each pair / point
    full = Bm.T @ Bm
    dead_pairs = [(s, t) for s in range(28) for t in range(s + 1, 28) if r[s][t] > 0 and cover[s, t] < r[s][t]]
    dead_points = [s for s in range(28) if cover[s, s] < P["dZ"][s]]
    return P, wit, alive, cover, full, dead_pairs, dead_points

if __name__ == "__main__":
    fn, outfn = sys.argv[1], sys.argv[2]
    with open(outfn, "a") as out:
        for sid in map(int, sys.argv[3:]):
            d = I.load(fn, sid); t0 = time.time()
            P, wit, alive, cover, full, dead_pairs, dead_points = certificate(d)
            adj = P["adj"]; lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
            print(f"support {sid} (delta {d['delta']}): {len(wit)} blocks, {int(alive.sum())} left; pairs without enough blocks: {len(dead_pairs)}; "
                  f"points without enough blocks: {len(dead_points)}  [{time.time()-t0:.0f}s]")
            if not dead_pairs: continue
            # the pair with the fewest blocks to refute, among those left with NO block
            zero = [q for q in dead_pairs if cover[q[0], q[1]] == 0] or dead_pairs
            s, t = min(zero, key=lambda q: full[q[0], q[1]])
            Bm = P["Bm"]; idx = [j for j in range(len(wit)) if Bm[j, s] and Bm[j, t]]
            if any(wit[j] is None for j in idx): print("   (the pair keeps some blocks, fewer than r: certificate of another kind)"); continue
            rec = {"id": sid, "pair": [s, t], "blocks": [dict(B=[int(x) for x in np.nonzero(Bm[j])[0]], **wit[j]) for j in idx]}
            out.write(json.dumps(rec) + "\n")
            import collections
            kinds = collections.Counter((w["k"], w.get("a"), w.get("h")) if w["k"] == "A" else ("B", "z is u" if w["u"] == 28 else "z is v", None) for w in (wit[j] for j in idx))
            print(f"   pair {lab(s)} , {lab(t)}  (adjacent: {bool((adj[s] >> t) & 1)}, r = {P['r'][s][t]}): {len(idx)} admissible blocks contain it, all refuted")
            print(f"   witnesses by kind (lemma, a, weight of z): {sorted(kinds.items(), key=lambda kv: -kv[1])}")
            print(f"   all pairs left without block: {[(lab(a), lab(b), int(full[a, b])) for a, b in zero][:12]}")
