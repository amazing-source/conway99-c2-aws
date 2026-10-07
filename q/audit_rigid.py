"""Audit of the rigid kernel (C2 lab, 2026-10-07; hole H2 found by Codex, lemma/upstream/AUDIT_ENGINE_RULES.md).

  <producer of the job> | python audit_rigid.py <package dir> <lid> <out.json> [k n]
  Golay-family lattices (pairs in the package's files, no producer):
  python golay_stream.py <package dir> <lid> | AUDIT_GOLAY=1 python audit_rigid.py <package dir> <lid> <out.json>

The engine chooses its kernel per pair: general = flex.any() (frame_dfs_next.search). The general kernels branch, when no point is
pending, on every remaining candidate h; the rigid kernel dfs_generic (pairs WITHOUT flex point) does not: a frame containing an h
with zero footprint on the points (the new roots) is never built there. A norm-4 vector h has zero footprint only if the two even
neighbours of U have the same Coxeter number H and h lies in the span of the root components of U of Coxeter number H
(sum over the new roots of (h,beta)^2 = 8 (H1 + H2) - 4 sum_j h_j |P_j h|^2 >= 8 |H1 - H2|). 27 of the 156 lattices are in that case.

Only a pair that (a) has no flex point and (b) has a zero-footprint candidate h orthogonal to y1 and y2 can have been excluded
wrongly by a search. This consumer reads a producer stream (hashed exactly like the package consumer) and counts, for ALL pairs,
with the flex test of the engine's pair set-up redone in exact integers:
  setup_impossible     the pair set-up rejects the pair (a y beyond 3/2 at a new root, or both y at 3/2 on the same one);
  general              the pair has a flex point: the engine used a general kernel (complete);
  rigid                no flex point: the engine used dfs_generic;
  with_zero_candidate  some norm-4 line of zero footprint is orthogonal to y1, y2 (Z = the zero-footprint lines of U);
  exposed              rigid AND with a zero-footprint candidate. For these the engine's own pair_setup_fast is called and must agree.
Each exposed pair is searched again here with FD_FORCE_GENERAL=1 (the engine's own switch: general kernel), node limit
AUDIT_NODE_LIMIT (default 2e8), and its verdict is recorded.
ok = the stream is complete and every exposed pair is EXCLUDED again (or there is none). A pair not excluded again is listed for
a full search. Nothing here pronounces an exclusion of a lattice."""
import sys, os, json, hashlib, time, math
from fractions import Fraction as F
import numpy as np


def main():
    pkg, lid, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3]
    chunk = [int(sys.argv[4]), int(sys.argv[5])] if len(sys.argv) > 5 else None
    t0 = time.time(); sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs_next as FD
    if os.environ.get("AUDIT_GOLAY", "") == "1":                         # Golay-family lattice: frame of the package's pair files
        import glob
        d0 = json.load(open(sorted(glob.glob(os.path.join(pkg, "data", "golay", lid, "pairs_*.json")))[0]))
        L = FD.lattice_data([[F(x) for x in row] for row in d0["basis"]], F(1, int(d0["scale"])))
    else:
        gens = json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))["gens"]
        L = FD.lattice_data(gens, F(1))
    G = np.asarray(L["G"], dtype=np.int64)
    Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]
    DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * int(x.denominator) // math.gcd(DEN, int(x.denominator))
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64)
    Binv = np.linalg.inv(BD.astype(np.float64))                          # coordinates of D y in the basis D B, i.e. of y in B
    X4 = np.asarray(L["X4"], dtype=np.int64).reshape(-1, 24); S2 = np.asarray(L["S2"], dtype=np.int64).reshape(-1, 24)
    assert len(X4) == 0 or (np.einsum("ij,jk,ik->i", X4, G, X4) == 4).all()
    Z = X4[np.abs(X4 @ G @ S2.T).max(axis=1) == 0] if len(X4) and len(S2) else X4[:0]   # norm-4 lines of zero footprint
    ZG = Z @ G
    X3 = np.asarray(L["X3"], dtype=np.int64).reshape(-1, 24); X3G = X3 @ G                      # norm-3 lines
    HIT3 = (np.abs(X3G @ S2.T) == 3).astype(np.float32) if len(S2) else np.zeros((len(X3), 0), np.float32)   # 3/2-hits of the norm-3 lines
    GS = G @ S2.T                                                                             # (., 2 beta)
    lim = int(os.environ.get("AUDIT_NODE_LIMIT", "200000000"))
    c = {"setup_impossible": 0, "general": 0, "rigid": 0, "with_zero_candidate": 0, "exposed": 0}
    sh = hashlib.sha256(); n = 0; end = None; exposed = []; buf = []

    def flush():
        if not buf: return
        pos = [b[0] for b in buf]
        Y = []
        for b in buf:
            row = []
            for key in ("y1", "y2"):
                v = [F(x) * DEN for x in b[1][key]]
                assert all(q.denominator == 1 for q in v), "D y not integral"
                row.append([int(q) for q in v])
            Y.append(row)
        Y1 = np.array([r[0] for r in Y], dtype=np.int64); Y2 = np.array([r[1] for r in Y], dtype=np.int64)
        C1 = np.rint(Y1.astype(np.float64) @ Binv).astype(np.int64); C2 = np.rint(Y2.astype(np.float64) @ Binv).astype(np.int64)
        assert (C1 @ BD == Y1).all() and (C2 @ BD == Y2).all(), "y not in U"          # exact: y = c B
        # the flex test of pair_setup, in exact integers, for the whole batch
        S1 = np.abs(C1 @ GS); S2y = np.abs(C2 @ GS)                                  # |2 (y, beta)|
        imp = (np.maximum(S1, S2y).max(axis=1) > 3) | ((S1 == 3) & (S2y == 3)).any(axis=1) if GS.shape[1] else np.zeros(len(buf), dtype=bool)
        yhit = (S1 == 3) | (S2y == 3)
        Wm = ((C1 @ X3G.T == 0) & (C2 @ X3G.T == 0)).astype(np.float32)             # norm-3 lines orthogonal to y1, y2
        flexany = ((Wm @ HIT3 > 0.5) & ~yhit).any(axis=1) if GS.shape[1] else np.zeros(len(buf), dtype=bool)
        cand = ((C1 @ ZG.T == 0) & (C2 @ ZG.T == 0)).any(axis=1) if len(ZG) else np.zeros(len(buf), dtype=bool)
        c["setup_impossible"] += int(imp.sum()); c["general"] += int((~imp & flexany).sum()); c["rigid"] += int((~imp & ~flexany).sum())
        c["with_zero_candidate"] += int((~imp & cand).sum())
        for q in np.flatnonzero(~imp & ~flexany & cand):
            ps, why = FD.pair_setup_fast(L, C1[q], C2[q])                             # the engine's own set-up: must agree
            assert ps is not None and not bool(ps["flex"].any()), "flex test differs from the engine's pair set-up"
            assert bool((np.abs(ps["HS"]).max(axis=1) == 0).any()), "zero-footprint candidate not in the engine's candidate list"
            c["exposed"] += 1
            os.environ["FD_FORCE_GENERAL"] = "1"
            try: res = FD.search(L, C1[q], C2[q], node_limit=lim); v = res["verdict"]; nodes = res.get("nodes")
            except AssertionError as e: v = "INVALID (%s)" % str(e)[:80]; nodes = None
            finally: os.environ.pop("FD_FORCE_GENERAL", None)
            exposed.append({"position": pos[q], "o": buf[q][1]["o"], "y1": buf[q][1]["y1"], "y2": buf[q][1]["y2"], "verdict_general_kernel": v,
                            "nodes": None if nodes is None else int(np.sum(nodes)),
                            "zero_footprint_candidates": int((np.abs(ps["HS"]).max(axis=1) == 0).sum())})
        buf.clear()

    for raw in sys.stdin.buffer:
        line = raw.rstrip(b"\r\n")
        if not line: continue
        r = json.loads(line)
        if r.get("end"): end = r; break
        if "o" not in r or "y1" not in r: continue
        sh.update(line + b"\n"); buf.append((n, r)); n += 1
        if len(buf) >= 2000: flush()
    flush()
    stream_ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and end.get("sha256") == sh.hexdigest()
    notex = [e for e in exposed if not str(e["verdict_general_kernel"]).startswith("EXCLUDED")]
    out = {"id": int(lid), "chunk": chunk or (end or {}).get("chunk"), "n_pairs": n, "sha256": sh.hexdigest(), "stream_ok": stream_ok,
           "lattice": {"rigid": bool(L["rigid"]), "norm4_lines": int(len(X4)), "zero_footprint_norm4_lines": int(len(Z)), "new_root_pairs": int(len(S2))},
           "counts": c, "exposed": exposed[:500], "exposed_not_excluded_again": len(notex), "ok": bool(stream_ok and not notex),
           "audit_rigid_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
           "engine_sha256": hashlib.sha256(open(os.path.join(pkg, "scripts", "frame_dfs_next.py"), "rb").read()).hexdigest()[:16],
           "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    json.dump(out, open(outf, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("id", "chunk", "n_pairs", "stream_ok", "counts", "exposed_not_excluded_again", "ok", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
