"""Audit of the rigid kernel (C2 lab, 2026-10-07; hole found by Codex in lemma/upstream/AUDIT_ENGINE_RULES.md, H2).

  <producer of the job> | python audit_rigid.py <package dir> <lid> <out.json> [k n]

The engine chooses its kernel per pair: general = flex.any() (frame_dfs_next.search). The general kernels branch, when no point is
pending, on every remaining candidate h; the rigid kernel dfs_generic (pairs WITHOUT flex point) does not: a frame containing an h
with zero footprint on the points (the new roots) is never built there. A norm-4 vector h has zero footprint only if the two even
neighbours of U have the same Coxeter number H and h lies in the span of the root components of U of Coxeter number H
(sum over the new roots of (h,beta)^2 = 8 (H1 + H2) - 4 sum_j h_j |P_j h|^2 >= 8 |H1 - H2|). 27 of the 156 lattices are in that case.

This consumer reads a producer stream (hashed exactly like the package consumer) and, for every pair, with the engine's own
pair_setup_fast:
  setup_impossible  the pair set-up rejects the pair (a y beyond 3/2 at a new root, or both y at 3/2 on the same one);
  general           the pair has a flex point: the engine used a general kernel (complete);
  rigid             no flex point: the engine used dfs_generic;
  exposed           rigid AND some candidate h (norm 4, orthogonal to y1, y2, |(h,beta)| <= 1) has zero footprint.
Only an exposed pair can have been excluded wrongly. Each exposed pair is searched again here with FD_FORCE_GENERAL=1 (the
engine's own switch: general kernel, complete), node limit AUDIT_NODE_LIMIT (default 2e8), and its verdict is recorded.
ok = the stream is complete and every exposed pair is EXCLUDED again (or there is none). Nothing here pronounces an exclusion of a
lattice; a pair not excluded again is listed for a full search."""
import sys, os, json, hashlib, time
from fractions import Fraction as F
import numpy as np


def main():
    pkg, lid, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3]
    chunk = [int(sys.argv[4]), int(sys.argv[5])] if len(sys.argv) > 5 else None
    t0 = time.time(); sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs_next as FD
    gens = json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))["gens"]
    L = FD.lattice_data(gens, F(1)); G = np.asarray(L["G"], dtype=np.int64)
    Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]
    Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in Bq]))
    X4 = np.asarray(L["X4"], dtype=np.int64); S2 = np.asarray(L["S2"], dtype=np.int64)
    zero_lines = int((np.abs(X4 @ G @ S2.T).max(axis=1) == 0).sum()) if len(X4) else 0     # norm-4 lines of zero footprint in U
    lim = int(os.environ.get("AUDIT_NODE_LIMIT", "200000000"))

    def conv(v):                                                    # ambient fractions -> integer coordinates, checked exactly
        cf = np.rint(np.array([float(F(x)) for x in v]) @ Binv).astype(np.int64)
        assert all(sum(int(c) * Bq[i][j] for i, c in enumerate(cf)) == F(v[j]) for j in range(len(v))), "y not in U"
        return cf
    sh = hashlib.sha256(); n = 0; end = None; c = {"setup_impossible": 0, "general": 0, "rigid": 0, "exposed": 0}; exposed = []
    for raw in sys.stdin.buffer:
        line = raw.rstrip(b"\r\n")
        if not line: continue
        r = json.loads(line)
        if r.get("end"): end = r; break
        if "o" not in r or "y1" not in r: continue
        sh.update(line + b"\n"); pos = n; n += 1
        y1, y2 = conv(r["y1"]), conv(r["y2"])
        ps, why = FD.pair_setup_fast(L, y1, y2)
        if ps is None: c["setup_impossible"] += 1; continue
        if bool(ps["flex"].any()): c["general"] += 1; continue
        c["rigid"] += 1
        if zero_lines == 0 or len(ps["H"]) == 0 or not bool((np.abs(ps["HS"]).max(axis=1) == 0).any()): continue
        c["exposed"] += 1
        os.environ["FD_FORCE_GENERAL"] = "1"
        try: res = FD.search(L, y1, y2, node_limit=lim); v = res["verdict"]; nodes = res.get("nodes")
        except AssertionError as e: v = "INVALID (%s)" % str(e)[:80]; nodes = None
        finally: os.environ.pop("FD_FORCE_GENERAL", None)
        exposed.append({"position": pos, "o": r["o"], "y1": r["y1"], "y2": r["y2"], "verdict_general_kernel": v,
                        "nodes": None if nodes is None else int(np.sum(nodes)),
                        "zero_footprint_candidates": int((np.abs(ps["HS"]).max(axis=1) == 0).sum())})
    stream_ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and end.get("sha256") == sh.hexdigest()
    notex = [e for e in exposed if not str(e["verdict_general_kernel"]).startswith("EXCLUDED")]
    out = {"id": int(lid), "chunk": chunk or (end or {}).get("chunk"), "n_pairs": n, "sha256": sh.hexdigest(), "stream_ok": stream_ok,
           "lattice": {"rigid": bool(L["rigid"]), "norm4_lines": int(len(X4)), "zero_footprint_norm4_lines": zero_lines, "new_root_pairs": int(len(S2))},
           "counts": c, "exposed": exposed[:200], "exposed_not_excluded_again": len(notex), "ok": bool(stream_ok and not notex),
           "audit_rigid_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
           "engine_sha256": hashlib.sha256(open(os.path.join(pkg, "scripts", "frame_dfs_next.py"), "rb").read()).hexdigest()[:16],
           "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    json.dump(out, open(outf, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("id", "chunk", "n_pairs", "stream_ok", "counts", "exposed_not_excluded_again", "ok", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
