"""C2's independent enumeration of the admissible pairs (y1, y2) of an envelope U, for the rigid family (second reader of C1's
y_pairs; conditions proven in notes/140-141 and by structures).
- y norm 7. From min N* >= 8/7 and 7 I_2 primitive (projection of v onto N has norm v^2 - Y(v)/7 >= 8/7, or v in span(y)):
  Y(v) = (v, y1)^2 + (v, y2)^2 <= 7 v^2 - 8 for every v != 0 with v^2 <= 6. Used here for the roots (Y <= 6) and the norm-3 vectors
  (Y <= 13); single-y versions: (alpha, y)^2 <= 6 and (v, y)^2 <= 13.
- New roots beta (shadow, norm 2): the frame identity at beta gives |(y, beta)| <= 3/2, and no beta is hit at 3/2 by both y.
- y1 up to the Weyl group W(R) (R = roots of U, W <= Aut U, and (F) is Aut U-invariant): one W-dominant representative per
  W-orbit (reflections in my own simple roots). y2 up to Stab_W(y1) = W_J (J = simple roots orthogonal to y1) and up to sign.
Then scripts/frame_dfs.py runs on every pair (--run).
Usage: python ypairs_c2.py <U.json> <out.json> [--run <out.jsonl>]"""
import sys, os, json, time
from fractions import Fraction as F
import numpy as np
import numba as nb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frame_dfs as FD


@nb.njit(cache=True)
def norm7_filtered(G, Lu, d, RG, SG, X3G, maxout):
    """all x with x^T G x = 7 (Fincke-Pohst, exact check) and, for the rows of RG = roots @ G: (alpha, x)^2 <= 6;
    SG = (2 beta) @ G: |2 (beta, x)| <= 3; X3G = norm-3 rows @ G: (v, x)^2 <= 13. Returns the vectors (one per +- pair)."""
    n = G.shape[0]; out = np.zeros((maxout, n), np.int8); cnt = 0; tot = 0
    x = np.zeros(n, np.int64); rem = np.zeros(n + 1); cen = np.zeros(n); hi = np.zeros(n, np.int64)
    bound = 7.0 + 1e-7; i = n - 1; rem[n] = bound; cen[i] = 0.0
    r = np.sqrt(rem[n] / d[i]); x[i] = np.int64(np.ceil(-r)); hi[i] = np.int64(np.floor(r))
    while True:
        if x[i] > hi[i]:
            i += 1
            if i >= n: break
            x[i] += 1
            continue
        t = x[i] - cen[i]; rr = rem[i + 1] - d[i] * t * t
        if rr < -1e-9:
            x[i] += 1
            continue
        if i == 0:
            q = 0
            for a in range(n):
                if x[a] != 0:
                    for b in range(n): q += x[a] * G[a, b] * x[b]
            if q == 7:
                first = 0
                while x[first] == 0: first += 1
                if x[first] > 0:
                    tot += 1; ok = True
                    for k in range(RG.shape[0]):
                        s = 0
                        for a in range(n): s += RG[k, a] * x[a]
                        if s * s > 6:
                            ok = False; break
                    if ok:
                        for k in range(SG.shape[0]):
                            s = 0
                            for a in range(n): s += SG[k, a] * x[a]
                            if s > 3 or s < -3:
                                ok = False; break
                    if ok:
                        for k in range(X3G.shape[0]):
                            s = 0
                            for a in range(n): s += X3G[k, a] * x[a]
                            if s * s > 13:
                                ok = False; break
                    if ok:
                        if cnt < maxout:
                            for a in range(n): out[cnt, a] = np.int8(x[a])
                        cnt += 1
            x[i] += 1
            continue
        rem[i] = rr; i -= 1
        c = 0.0
        for j in range(i + 1, n): c -= Lu[i, j] * x[j]
        cen[i] = c
        r = np.sqrt(max(rem[i + 1], 0.0) / d[i])
        x[i] = np.int64(np.ceil(cen[i] - r)); hi[i] = np.int64(np.floor(cen[i] + r))
    return out[:min(cnt, maxout)], cnt, tot


def simple_roots(R, G):
    """positive system from a generic vector; simple = positive roots that are not a sum of two positive roots"""
    rng = np.random.default_rng(12345); t = rng.normal(size=R.shape[1])
    Rall = np.vstack([R, -R]); val = (Rall @ G) @ t
    assert np.all(np.abs(val) > 1e-9)
    Pos = Rall[val > 0]; S = set(map(tuple, Pos))
    simple = [a for a in Pos if not any(tuple(a - b) in S for b in Pos if not np.array_equal(a, b))]
    return np.array(simple, dtype=np.int64)


@nb.njit(cache=True)
def dominant_rows(Y8, SGs):
    """rows r and signs s with s * Y8[r] W-dominant ((s y, alpha_i) >= 0 for every simple root)"""
    rows = []; sg = []
    for r in range(Y8.shape[0]):
        for s in (1, -1):
            ok = True
            for k in range(SGs.shape[0]):
                v = 0
                for a in range(Y8.shape[1]): v += SGs[k, a] * Y8[r, a]
                if s * v < 0:
                    ok = False; break
            if ok:
                rows.append(r); sg.append(s)
    return np.array(rows, dtype=np.int64), np.array(sg, dtype=np.int64)


def dominant_all_unused(Yb, Sm, G):
    """dominant representative of every row (reflections in the simple roots, (y, alpha) < 0)"""
    SG = Sm @ G; out = Yb.copy(); n = Yb.shape[1]
    for r in range(Yb.shape[0]):
        while True:
            kmin = -1; vmin = 0
            for k in range(SG.shape[0]):
                v = 0
                for a in range(n): v += SG[k, a] * out[r, a]
                if v < vmin:
                    vmin = v; kmin = k
            if kmin < 0: break
            for a in range(n): out[r, a] -= vmin * Sm[kmin, a]
    return out


@nb.njit(cache=True)
def y2_candidates(Y8, Gy1, R1, V1, S1, RG, X3G, SG):
    """rows y2 of Y8 (one per +- line) with (y2, y1) = 0 and the pair filters: (a, y1)^2 + (a, y2)^2 <= 6 on the roots,
    <= 13 on the norm-3 lines, and no new root hit at 3/2 by both (|2 (beta, y)| = 3)"""
    n = Y8.shape[1]; out = []
    for r in range(Y8.shape[0]):
        s = 0
        for a in range(n): s += Gy1[a] * Y8[r, a]
        if s != 0: continue
        ok = True
        for k in range(RG.shape[0]):
            v = 0
            for a in range(n): v += RG[k, a] * Y8[r, a]
            if R1[k] * R1[k] + v * v > 6:
                ok = False; break
        if not ok: continue
        for k in range(SG.shape[0]):
            v = 0
            for a in range(n): v += SG[k, a] * Y8[r, a]
            if (v == 3 or v == -3) and (S1[k] == 3 or S1[k] == -3):
                ok = False; break
        if not ok: continue
        for k in range(X3G.shape[0]):
            v = 0
            for a in range(n): v += X3G[k, a] * Y8[r, a]
            if V1[k] * V1[k] + v * v > 13:
                ok = False; break
        if ok: out.append(r)
    return np.array(out, dtype=np.int64)


def dominant(y, Sm, G):
    """W-dominant representative: reflect in simple roots alpha with (y, alpha) < 0 (alpha^2 = 2: s(y) = y - (y, alpha) alpha)"""
    y = y.copy(); SG = Sm @ G
    while True:
        ip = SG @ y; k = int(np.argmin(ip))
        if ip[k] >= 0: return y
        y = y - ip[k] * Sm[k]


def _pairs_part(k):
    """07/10 (laptop session), YP_WORKERS > 1 only: the y1 of index k, k + NW, ... of Y1, each treated by the same statements as the
    sequential loop of the main block (copied below), in a process forked after Y, Y1 and the tables were built."""
    out = []
    for t in range(k, len(Y1), NW):
        y1 = Y1[t]; res = []
        idx = y2_candidates(Y, G @ y1, RG @ y1, X3G @ y1, SG @ y1, RG, X3G, SG)
        J = Sm[(Sm @ G @ y1) == 0] if len(Sm) else Sm; JG = J @ G
        seen = set()
        for i in idx:
            for s_ in (1, -1):
                v = s_ * Y[i].astype(np.int64)
                if len(J) and (JG @ v < 0).any(): continue
                w = dominant(-v, J, G) if len(J) else -v
                key = min(tuple(v), tuple(w))
                if key not in seen: seen.add(key); res.append([[int(t_) for t_ in y1], [int(t_) for t_ in key]])
        out.append((t, res))
    return out


if __name__ == "__main__":
    t0 = time.time(); rec = json.load(open(sys.argv[1])); outp = sys.argv[2]
    L = FD.lattice_data(rec["gens"]); G = L["G"]; R = L["R"]; X3 = L["X3"]; S2 = L["S2"]
    if not L["rigid"]: print("NON-rigid envelope: same admissibility filters (they are general); run the h-stage with FD_LEMMA_U=1", flush=True)
    Lu, d = FD.ldl(G)
    Y, cnt, tot = norm7_filtered(G, Lu, d, R @ G, S2 @ G, X3 @ G, 40_000_000)
    assert cnt <= 40_000_000
    print("U: r %d; norm-7 lines %d, admissible (roots, new roots, norm 3) %d (%.0fs)" % (L["r"], tot, cnt, time.time() - t0), flush=True)
    Sm = simple_roots(R, G) if len(R) else np.zeros((0, 24), dtype=np.int64)
    print("simple roots: %d (rank of R)" % len(Sm), flush=True)
    Y = Y[:cnt].copy()                                                  # free the enumeration buffer
    SGs = (Sm @ G).astype(np.int64) if len(Sm) else np.zeros((0, 24), dtype=np.int64)
    # the admissible set is W-invariant (the filters are), so its W-orbits <-> its W-dominant members
    rows, sgn = dominant_rows(Y, SGs)
    Y1 = sorted({tuple(int(v) * int(s_) for v in Y[r]) for r, s_ in zip(rows, sgn)})
    Y1 = [np.array(k, dtype=np.int64) for k in Y1]
    print("W-orbits of admissible y (both signs): %d (%.0fs)" % (len(Y1), time.time() - t0), flush=True)
    RG, X3G, SG = R @ G, X3 @ G, S2 @ G
    pairs = []
    NW = int(os.environ.get("YP_WORKERS", "1"))
    if NW > 1:                                                          # 07/10: the loop over y1 dealt to NW forked processes
        import multiprocessing as mp
        with mp.get_context("fork").Pool(NW) as pool: parts = pool.map(_pairs_part, range(NW))
        done = sorted((t, res) for part in parts for t, res in part)
        assert [t for t, _ in done] == list(range(len(Y1))), "a y1 is missing or doubled"
        for _, res in done: pairs.extend(res)                              # same order as the sequential loop
        print("y2 stage on %d processes" % NW, flush=True)
    else:
        for y1 in Y1:
            idx = y2_candidates(Y, G @ y1, RG @ y1, X3G @ y1, SG @ y1, RG, X3G, SG)
            # candidates are W_J-invariant (W_J = Stab_W(y1), J = simple roots orthogonal to y1): keep the J-dominant members,
            # and identify v with the J-dominant representative of -v (pairs up to the sign of y2)
            J = Sm[(Sm @ G @ y1) == 0] if len(Sm) else Sm; JG = J @ G
            seen = set()
            for i in idx:
                for s_ in (1, -1):
                    v = s_ * Y[i].astype(np.int64)
                    if len(J) and (JG @ v < 0).any(): continue
                    w = dominant(-v, J, G) if len(J) else -v
                    key = min(tuple(v), tuple(w))
                    if key not in seen: seen.add(key); pairs.append([[int(t) for t in y1], [int(t) for t in key]])   # plain ints (json)
    print("pairs (y1 W-dominant, y2 W_J-dominant up to sign): %d (%.0fs)" % (len(pairs), time.time() - t0), flush=True)
    json.dump({"source": sys.argv[1], "basis": [[str(x) for x in row] for row in L["B"]], "coords": "coefficients in 'basis'",
               "n_admissible_lines": int(cnt), "n_y1_orbits": len(Y1), "pairs": pairs}, open(outp, "w"))
    if "--run" in sys.argv:
        o = sys.argv[sys.argv.index("--run") + 1]; done = set()
        if os.path.exists(o):
            for l in open(o): done.add(json.loads(l)["k"])
        for k, (a, b) in enumerate(pairs):
            if k in done: continue
            r = FD.search(L, np.array(a, dtype=np.int64), np.array(b, dtype=np.int64)); r["k"] = k
            open(o, "a").write(json.dumps(r) + chr(10))
        print("frame_dfs on all pairs: done (%.0fs)" % (time.time() - t0), flush=True)
