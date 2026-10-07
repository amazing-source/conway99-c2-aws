"""Branch-split driver for ONE hard pair of frame_dfs (C2, 27/09): the depth-0 branches of dfs_generic are dealt round-robin to
K processes (a skipped branch is removed from the candidates exactly as after its exploration, so the union of the K runs is the
sequential search). Usage: python frame_dfs_split.py U.json pairs.json k K r out.jsonl"""
import sys, os, json, time
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"): os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frame_dfs import *
from frame_dfs import U1, o24_gens

@nb.njit(cache=True)
def dfs_generic_split(compat, through, supp, suppn, Z, Pp, Pn, Bd, NZ, target, allM, allW, node_limit, cap, Hc, Wc, V, WS, HS, bmod, brem):
    """o24_dfs kernel 2 on general points (no support tables: only need <= left), with leaf_l7 at the leaves"""
    nMw = compat.shape[1]; nWw = Z.shape[1]; npt = target.shape[0]; nW = Wc.shape[0]
    cand = np.zeros((8, nMw), np.uint64); Cs = np.zeros((8, nMw), np.uint64)
    nzw = np.zeros((8, nMw), np.int64); nnz = np.zeros(8, np.int64)
    need = np.zeros((8, npt), np.int64)
    ge1 = np.zeros((8, nWw), np.uint64); ge2 = np.zeros((8, nWw), np.uint64); good = np.zeros((8, nWw), np.uint64)
    P = np.zeros(8, np.int64); curj = np.zeros(8, np.int64); nodes = np.zeros(8, np.int64)
    leaves = np.zeros((cap, 7), np.int64); nleaves = 0; overflow = False; counts = np.zeros(3, np.int64)
    slots = np.zeros((12, nW), np.int64); slen = np.zeros(12, np.int64); part = np.zeros((13, npt), np.int64); pos = np.zeros(13, np.int64)
    for w in range(nMw):
        cand[0, w] = allM[w]; nzw[0, w] = w
    nnz[0] = nMw
    for w in range(nWw): good[0, w] = allW[w]
    for i in range(npt): need[0, i] = target[i]
    total = 0; stop = False; d = 0; action = 0; bcnt = 0
    while True:
        if action == 0:
            nodes[d] += 1; total += 1
            if node_limit > 0 and total >= node_limit: stop = True
            if stop:
                action = 2; continue
            if d == 7:
                counts[0] += 1
                res = leaf_l7(P, Hc, Wc, V, WS, HS, Z, Pp, Pn, allW, slots, slen, part, pos, npt)
                if res >= 1: counts[1] += 1
                if res == 2:
                    counts[2] += 1
                    if nleaves < cap:
                        for x in range(7): leaves[nleaves, x] = P[x]
                        nleaves += 1
                    else: overflow = True
                action = 2; continue
            left = 7 - d; best = -1; bkey = 1 << 30; pruned = False
            for i in range(npt):
                r = need[d, i]
                if r > left:
                    pruned = True; break
                if r > 0:
                    n = 0
                    for t in range(nnz[d]):
                        w = nzw[d, t]; n += popc(cand[d, w] & through[i, w])
                    if n < r:
                        pruned = True; break
                    if n - r < bkey:
                        best = i; bkey = n - r
            if pruned:
                action = 2; continue
            for t in range(nnz[d]):
                w = nzw[d, t]; Cs[d, w] = cand[d, w] & through[best, w]
            curj[d] = 0
            action = 1; continue
        elif action == 1:
            j = -1
            while curj[d] < nnz[d]:
                w = nzw[d, curj[d]]; x = Cs[d, w]
                if x != 0:
                    low = x & (~x + U1)
                    j = w * 64 + popc(low - U1); Cs[d, w] = x ^ low
                    break
                curj[d] += 1
            if j < 0:
                action = 2; continue
            if d == 0:
                bcnt += 1
                if (bcnt - 1) % bmod != brem:
                    cand[0, j >> 6] &= ~(U1 << np.uint64(j & 63))
                    action = 1; continue
            P[d] = j
            e1 = d + 1
            for w in range(nWw):
                good[e1, w] = good[d, w] & ~Bd[j, w]
                ge1[e1, w] = ge1[d, w] | NZ[j, w]
                ge2[e1, w] = ge2[d, w] | (ge1[d, w] & NZ[j, w])
            left = 7 - e1; ok = True
            for x in range(e1):
                if not ok: break
                for y in range(x + 1, e1):
                    c = P[x]; e = P[y]; same = np.uint64(0); opp = np.uint64(0)
                    for w in range(nWw):
                        zo = good[e1, w]
                        for f in range(e1):
                            if f != x and f != y: zo &= Z[P[f], w]
                        same |= ((Pp[c, w] & Pp[e, w]) | (Pn[c, w] & Pn[e, w])) & zo
                        opp |= ((Pp[c, w] & Pn[e, w]) | (Pn[c, w] & Pp[e, w])) & zo
                    if same == 0 or opp == 0:
                        ok = False; break
            if ok and left > 0:
                n = 0
                for w in range(nWw): n += popc(good[e1, w] & ~ge1[e1, w])
                if n < left * (left - 1): ok = False
                else:
                    for x in range(e1):
                        c = P[x]; n = 0
                        for w in range(nWw): n += popc(NZ[c, w] & good[e1, w] & ~ge2[e1, w])
                        if n < 2 * left:
                            ok = False; break
            if ok:
                for i in range(npt): need[e1, i] = need[d, i]
                cnt = 0
                for t in range(nnz[d]):
                    w = nzw[d, t]; v = cand[d, w] & compat[j, w]
                    if v != 0:
                        cand[e1, w] = v; nzw[e1, cnt] = w; cnt += 1
                nnz[e1] = cnt
                for q in range(suppn[j]):
                    x = supp[j, q]; need[e1, x] -= 1
                    if need[e1, x] == 0:
                        for t in range(cnt):
                            w = nzw[e1, t]; cand[e1, w] &= ~through[x, w]
                d = e1; action = 0; continue
            cand[d, j >> 6] &= ~(U1 << np.uint64(j & 63))
            action = 1; continue
        else:
            if d == 0: break
            d -= 1; j = P[d]
            cand[d, j >> 6] &= ~(U1 << np.uint64(j & 63))
            action = 2 if stop else 1
    return nodes, leaves[:nleaves], not stop, overflow, counts




@nb.njit(cache=True)
def dfs_general_u_split(compat, through, supp, suppn, Z, Pp, Pn, Bd, NZ, target, isflex, whitb, allM, allW, node_limit, cap, Hc, Wc, V, WS, HS, hitb, bmod, brem):
    """GENERAL mode + C1 LEMMA U+ (notes/145): a frame word hits (at 3/2) ONLY new roots that end at w = 1 and are not y-hits, and has the
    D7 pattern on the 7 h (exactly two (u,h) = +-1). At a node a word is VALID iff: no |(u,h)| = 2 and <= 2 nonzero on the chosen h,
    no 3/2-hit on a y-hit point, none on a flex point already covered >= 2 (monotone). The cells (Same/Opp) and the counting checks
    use the valid words only; a flex point at w <= 2 without a valid hitter must reach 3; at the leaf a w = 1 flex point needs a
    hitter with exactly 2 nonzero.
    GENERAL mode (flex points): target[p] = 1 or 3 exactly, or 0 for a flex point (final coverage 1 or 3). Pending points:
    exact points with need > 0, flex points with coverage 0 or 2. Branch on a pending point (smallest-index member through it);
    with no pending point, on the smallest-index remaining member (all candidates). Saturated: exact need 0, flex coverage 3."""
    nMw = compat.shape[1]; nWw = Z.shape[1]; npt = target.shape[0]; nW = Wc.shape[0]
    cand = np.zeros((8, nMw), np.uint64); Cs = np.zeros((8, nMw), np.uint64)
    nzw = np.zeros((8, nMw), np.int64); nnz = np.zeros(8, np.int64)
    need = np.zeros((8, npt), np.int64); cov = np.zeros((8, npt), np.int64)
    ge1 = np.zeros((8, nWw), np.uint64); ge2 = np.zeros((8, nWw), np.uint64); good = np.zeros((8, nWw), np.uint64)
    ge3 = np.zeros((8, nWw), np.uint64); bad = np.zeros((8, nWw), np.uint64); vm = np.zeros(nWw, np.uint64)
    P = np.zeros(8, np.int64); curj = np.zeros(8, np.int64); nodes = np.zeros(8, np.int64)
    leaves = np.zeros((cap, 7), np.int64); leafcov = np.zeros((cap, npt), np.int64); nleaves = 0; overflow = False
    counts = np.zeros(3, np.int64)
    slots = np.zeros((12, nW), np.int64); slen = np.zeros(12, np.int64); part = np.zeros((13, npt), np.int64); pos = np.zeros(13, np.int64)
    allowed = np.zeros(nWw, np.uint64)
    for w in range(nMw):
        cand[0, w] = allM[w]; nzw[0, w] = w
    nnz[0] = nMw
    for w in range(nWw): good[0, w] = allW[w]
    for i in range(npt):
        need[0, i] = target[i]
        if target[i] == 1:
            for w in range(nWw): bad[0, w] |= hitb[i, w]
    total = 0; stop = False; d = 0; action = 0; bcnt = 0
    while True:
        if action == 0:
            nodes[d] += 1; total += 1
            if node_limit > 0 and total >= node_limit: stop = True
            if stop:
                action = 2; continue
            if d == 7:
                valid = True
                for i in range(npt):
                    if isflex[i]:
                        if cov[d, i] != 1 and cov[d, i] != 3:
                            valid = False; break
                        if cov[d, i] == 1:                                   # Lemma U at the leaf: a hitter with exactly 2 nonzero
                            hv = False
                            for w in range(nWw):
                                if good[d, w] & ge2[d, w] & ~ge3[d, w] & ~bad[d, w] & hitb[i, w]:
                                    hv = True; break
                            if not hv:
                                valid = False; break
                    elif need[d, i] != 0:
                        valid = False; break
                if valid:
                    counts[0] += 1
                    res = leaf_general(P, cov[d], isflex, whitb, Hc, Wc, V, WS, HS, Z, Pp, Pn, allW, slots, slen, part, pos, npt, allowed)
                    if res >= 1: counts[1] += 1
                    if res == 2:
                        counts[2] += 1
                        if nleaves < cap:
                            for x in range(7): leaves[nleaves, x] = P[x]
                            for i in range(npt): leafcov[nleaves, i] = cov[d, i]
                            nleaves += 1
                        else: overflow = True
                action = 2; continue
            left = 7 - d; best = -1; bkey = 1 << 30; pruned = False
            for i in range(npt):
                if isflex[i]:
                    c = cov[d, i]
                    if c >= 3: r = 0
                    else:
                        hv = False
                        for w in range(nWw):
                            if good[d, w] & ~ge3[d, w] & ~bad[d, w] & hitb[i, w]:
                                hv = True; break
                        if hv: r = 1 if (c == 0 or c == 2) else 0
                        else: r = 3 - c                                      # Lemma U: w = 1 impossible, must reach 3
                else:
                    r = need[d, i]
                if r > left:
                    pruned = True; break
                if r > 0:
                    n = 0
                    for t in range(nnz[d]):
                        w = nzw[d, t]; n += popc(cand[d, w] & through[i, w])
                    if n < r:
                        pruned = True; break
                    if n - r < bkey:
                        best = i; bkey = n - r
            if pruned:
                action = 2; continue
            if best >= 0:
                for t in range(nnz[d]):
                    w = nzw[d, t]; Cs[d, w] = cand[d, w] & through[best, w]
            else:                                                        # no pending point: any remaining member
                for t in range(nnz[d]):
                    w = nzw[d, t]; Cs[d, w] = cand[d, w]
            curj[d] = 0
            action = 1; continue
        elif action == 1:
            j = -1
            while curj[d] < nnz[d]:
                w = nzw[d, curj[d]]; x = Cs[d, w]
                if x != 0:
                    low = x & (~x + U1)
                    j = w * 64 + popc(low - U1); Cs[d, w] = x ^ low
                    break
                curj[d] += 1
            if j < 0:
                action = 2; continue
            if d == 0:
                bcnt += 1
                if (bcnt - 1) % bmod != brem:
                    cand[0, j >> 6] &= ~(U1 << np.uint64(j & 63))
                    action = 1; continue
            P[d] = j
            e1 = d + 1
            for w in range(nWw):
                good[e1, w] = good[d, w] & ~Bd[j, w]
                ge1[e1, w] = ge1[d, w] | NZ[j, w]
                ge2[e1, w] = ge2[d, w] | (ge1[d, w] & NZ[j, w])
                ge3[e1, w] = ge3[d, w] | (ge2[d, w] & NZ[j, w])
                bad[e1, w] = bad[d, w]
            for q in range(suppn[j]):                                        # flex points reaching coverage >= 2: their hitters die
                x = supp[j, q]
                if isflex[x] and cov[d, x] + 1 >= 2:
                    for w in range(nWw): bad[e1, w] |= hitb[x, w]
            for w in range(nWw): vm[w] = good[e1, w] & ~ge3[e1, w] & ~bad[e1, w]
            left = 7 - e1; ok = True
            for x in range(e1):
                if not ok: break
                for y in range(x + 1, e1):
                    c = P[x]; e = P[y]; same = np.uint64(0); opp = np.uint64(0)
                    for w in range(nWw):
                        zo = vm[w]
                        for f in range(e1):
                            if f != x and f != y: zo &= Z[P[f], w]
                        same |= ((Pp[c, w] & Pp[e, w]) | (Pn[c, w] & Pn[e, w])) & zo
                        opp |= ((Pp[c, w] & Pn[e, w]) | (Pn[c, w] & Pp[e, w])) & zo
                    if same == 0 or opp == 0:
                        ok = False; break
            if ok and left > 0:
                n = 0
                for w in range(nWw): n += popc(vm[w] & ~ge1[e1, w])
                if n < left * (left - 1): ok = False
                else:
                    for x in range(e1):
                        c = P[x]; n = 0
                        for w in range(nWw): n += popc(NZ[c, w] & vm[w] & ~ge2[e1, w])
                        if n < 2 * left:
                            ok = False; break
            if ok:
                for i in range(npt):
                    need[e1, i] = need[d, i]; cov[e1, i] = cov[d, i]
                cnt = 0
                for t in range(nnz[d]):
                    w = nzw[d, t]; v = cand[d, w] & compat[j, w]
                    if v != 0:
                        cand[e1, w] = v; nzw[e1, cnt] = w; cnt += 1
                nnz[e1] = cnt
                for q in range(suppn[j]):
                    x = supp[j, q]; cov[e1, x] += 1
                    sat = False
                    if isflex[x]:
                        sat = cov[e1, x] == 3
                    else:
                        need[e1, x] -= 1; sat = need[e1, x] == 0
                    if sat:
                        for t in range(cnt):
                            w = nzw[e1, t]; cand[e1, w] &= ~through[x, w]
                d = e1; action = 0; continue
            cand[d, j >> 6] &= ~(U1 << np.uint64(j & 63))
            action = 1; continue
        else:
            if d == 0: break
            d -= 1; j = P[d]
            cand[d, j >> 6] &= ~(U1 << np.uint64(j & 63))
            action = 2 if stop else 1
    return nodes, leaves[:nleaves], leafcov[:nleaves], not stop, overflow, counts



def search_split(L, y1, y2, bmod, brem, node_limit=0, cap=2_000_000):
    t0 = time.time(); ps, why = pair_setup(L, y1, y2)
    if ps is None: return {"verdict": "EXCLUDED (%s)" % why}
    H, HS, W, WS, V, target = ps["H"], ps["HS"], ps["W"], ps["WS"], ps["V"], ps["target"]; G = L["G"]
    general = bool(ps["flex"].any())
    if general: cap = min(cap, int(os.environ.get("FD_CAP_GENERAL", "50000")))
    if general: assert os.environ.get("FD_LEMMA_U"), "general mode: only the U+ kernel is split (set FD_LEMMA_U=1)"
    nH, nW = len(H), len(W); SUP = (HS != 0); HG = H @ G
    CBb = compat_nb(HG, H, pack64(V == 1), pack64(V == -1), pack64(SUP & (target == 1)[None, :]))
    supn = SUP.sum(axis=1); supp = np.full((nH, int(supn.max()) if nH else 1), -1, dtype=np.int64)
    for i in range(nH): supp[i, :supn[i]] = np.flatnonzero(SUP[i])
    u = {"compat": CBb, "through": pack64(SUP.T), "Z": pack64(V == 0), "Pp": pack64(V == 1), "Pn": pack64(V == -1),
         "Bd": pack64(np.abs(V) == 2), "NZ": pack64(np.abs(V) == 1)}
    allM = pack64(np.ones((1, nH), dtype=bool))[0]; allW = pack64(np.ones((1, nW), dtype=bool))[0]
    t1 = time.time()
    if not general:
        nodes, leaves, complete, overflow, counts = dfs_generic_split(u["compat"], u["through"], supp, supn.astype(np.int64), u["Z"], u["Pp"], u["Pn"],
                                                                      u["Bd"], u["NZ"], target, allM, allW, node_limit, cap, H, W,
                                                                      V.astype(np.int64), WS.astype(np.int64), HS.astype(np.int64), bmod, brem)
        lcov = [None] * len(leaves)
    else:
        nodes, leaves, lcov, complete, overflow, counts = dfs_general_u_split(u["compat"], u["through"], supp, supn.astype(np.int64), u["Z"],
            u["Pp"], u["Pn"], u["Bd"], u["NZ"], target, ps["flex"], pack64(ps["whit"]), allM, allW, node_limit, cap, H, W,
            V.astype(np.int64), WS.astype(np.int64), HS.astype(np.int64), pack64(ps["whit"].T), bmod, brem)
    assert not overflow
    t2 = time.time(); joint_ok, full = [], []
    for Pl, cv in zip(leaves, lcov):
        F1 = None if cv is None else (ps["flex"] & (np.asarray(cv) == 1))
        sols = joint(list(Pl), H, W, V, ps, G, F1=F1)
        joint_ok.append(len(sols)); full += [full_check(list(Pl), s, H, W, V, ps, G) for s in sols]
    return {"nodes": [int(x) for x in nodes], "complete": bool(complete), "leaves": int(counts[0]), "lemmaZ": int(counts[1]),
            "local_star_sums": int(counts[2]), "joint": sum(1 for x in joint_ok if x), "frame": sum(1 for f in full if f == 3),
            "secs": round(time.time() - t0, 1), "bmod": bmod, "brem": brem}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--o24":                                                   # python frame_dfs_split.py --o24 <class> K r out.jsonl
        k, K, r, outp = int(a[1]), int(a[2]), int(a[3]), a[4]
        gens, DAT = o24_gens(); L = lattice_data(gens, F(1, 8))
        Bf = np.array([[float(x) for x in row] for row in L["B"]]); Binv = np.linalg.inv(Bf); cl = DAT["orbits"][k]; yy = []
        for key in ("a1", "a2"):
            y = np.rint(np.array(cl[key], dtype=float) @ Binv).astype(np.int64); assert np.allclose(y @ Bf, cl[key]); yy.append(y)
    else:
        gens = json.load(open(a[0]))["gens"]; pairs = json.load(open(a[1]))["pairs"]; k, K, r, outp = int(a[2]), int(a[3]), int(a[4]), a[5]
        L = lattice_data(gens, F(1)); Bq = np.array([[F(x) for x in row] for row in L["B"]], dtype=object)
        Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]])); yy = []
        for c in pairs[k]:
            v = np.array([float(F(x)) for x in c]); cf = np.rint(v @ Binv).astype(np.int64)
            assert np.array_equal(cf @ Bq, np.array([F(x) for x in c], dtype=object)), "y not in U"
            yy.append(cf)
    res = search_split(L, yy[0], yy[1], K, r, node_limit=int(os.environ.get("FD_NODE_LIMIT", "0"))); res["k"] = k
    open(outp, "a").write(json.dumps(res) + chr(10)); print(json.dumps(res), flush=True)
