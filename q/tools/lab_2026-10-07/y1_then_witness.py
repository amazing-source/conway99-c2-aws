"""Exclusion without search, as far as it goes (C2 lab, 2026-10-07): for a lattice with a plan of ALL its admissible y1 up to the
Weyl group (identity-only symmetry file), first the fixed-y1 lemma, then the witness rules on the pairs of the y1 that are left.

  .venv/Scripts/python.exe scripts/cloud/y1_then_witness.py <plan dir> <cert_y1 dir> <out dir> [seconds budget=230] [lid ...]   (resumable)

Per lattice:
  1. the y1 representatives of the plan that are NOT in the fixed-y1 certificate (no root r with (r,y1) = +-2);
  2. for those only, the package producer (c1/code/y_pairs_gamma.py --from-plan, identity symmetry): all pairs (y1, y2), y2 up to sign,
     that pass its necessary filters;
  3. for each pair, in exact integers: (y1,y1) = (y2,y2) = 7, (y1,y2) = 0, and the minimum of E(v) = 7 (v,v) - (v,y1)^2 - (v,y2)^2
     over the vectors v of norm 2 and 3 of the lattice, and of norm 4 when those give no witness (so the recorded minimum is the
     true minimum over norms 2, 3, 4 only when it is >= 11 or comes from norm 4; a pair is a survivor only if ALL three lists give >= 11) (lists of frame_dfs_next.lattice_data, complete: shell check of 07/10).
     E(v) < 8 contradicts (R-vi); E = 8, 9, 10 contradict T16, T18, T20. A pair with such a v is excluded by that witness (stored: one
     witness per pair). A pair whose minimum is >= 11 has NO such witness: it is listed in <out dir>/<lid>_survivors.json and
     needs a frame search.
Output <out dir>/<lid>.json: counts by value of the minimum, sha256 of the stream, the survivors' number. It pronounces no exclusion
by itself; it says how much of a lattice falls to the lemmas alone."""
import sys, os, json, time, hashlib, subprocess, math, collections
from fractions import Fraction as F
import numpy as np
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); PKG = os.path.join(LAB, "c2_cloud_run_v10"); REPO = os.path.join(LAB, "aws_repo")
sys.path.insert(0, os.path.join(PKG, "scripts"))


def main():
    import frame_dfs_next as FD
    pd, cd, od = [os.path.abspath(x) for x in sys.argv[1:4]]; rest = sys.argv[4:]
    budget = 230.0
    if rest and rest[0].isdigit() and int(rest[0]) > 155: budget = float(rest[0]); rest = rest[1:]     # lattice ids are 000..155
    lids = [x for x in rest if len(x) == 3] or sorted(f[5:8] for f in os.listdir(pd) if f.startswith("plan_"))
    os.makedirs(od, exist_ok=True); t0 = time.time()
    for lid in lids:
        outf = os.path.join(od, lid + ".json")
        if os.path.exists(outf): continue
        if time.time() - t0 > budget: print("budget reached before", lid); break
        P = json.load(open(os.path.join(pd, "plan_%s.json" % lid))); C = json.load(open(os.path.join(cd, "cert_y1_%s.json" % lid)))
        left = C["not_covered"]; assert sorted(left + C["covered"]) == list(range(len(P["y1_reps"])))
        res = {"id": int(lid), "roots": C.get("roots"), "y1": len(P["y1_reps"]), "y1_with_root_of_product_2": len(C["covered"]), "y1_left": len(left)}
        if not left:
            res.update(pairs=0, survivors=0, by_min_E={}); json.dump(res, open(outf, "w"), indent=1); continue
        tmp = os.path.join(od, "tmp"); os.makedirs(tmp, exist_ok=True)
        pl = os.path.join(tmp, "plan_left_%s.json" % lid); json.dump(dict(P, y1_reps=[P["y1_reps"][i] for i in left]), open(pl, "w"))
        U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", lid + ".json"); st = os.path.join(tmp, "stream_%s.jsonl" % lid)
        r = subprocess.run([sys.executable, os.path.join(PKG, "c1", "code", "y_pairs_gamma.py"), U, os.path.join(REPO, "q", "audit_data", "gamma_%s_identity.json" % lid),
                            os.path.join(tmp, "stats_%s.json" % lid), "--from-plan", pl, "--stream", st, "--max-seconds", "200"], cwd=os.path.join(PKG, "c1", "code"), capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-300:]
        L = FD.lattice_data(json.load(open(U))["gens"], F(1)); G = np.asarray(L["G"], dtype=np.int64)
        Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]; DEN = 1
        for row in Bq:
            for x in row: DEN = DEN * int(x.denominator) // math.gcd(DEN, int(x.denominator))
        BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); Binv = np.linalg.inv(BD.astype(np.float64))
        shells = [(7 * nrm, np.asarray(L[k], dtype=np.int64).reshape(-1, 24) @ G, np.asarray(L[k], dtype=np.int64).reshape(-1, 24), nrm) for k, nrm in (("R", 2), ("X3", 3), ("X4", 4))]
        sh = hashlib.sha256(); n = 0; end = None; by = collections.Counter(); surv = []; wit = []; buf = []

        def flush():
            if not buf: return
            Y = []
            for b in buf:
                row = []
                for key in ("y1", "y2"):
                    v = [F(x) * DEN for x in b[key]]; assert all(q.denominator == 1 for q in v); row.append([int(q) for q in v])
                Y.append(row)
            Y1 = np.array([r_[0] for r_ in Y], dtype=np.int64); Y2 = np.array([r_[1] for r_ in Y], dtype=np.int64)
            C1 = np.rint(Y1.astype(np.float64) @ Binv).astype(np.int64); C2 = np.rint(Y2.astype(np.float64) @ Binv).astype(np.int64)
            assert (C1 @ BD == Y1).all() and (C2 @ BD == Y2).all(), "y not in U"
            g1 = C1 @ G; assert (np.einsum("ij,ij->i", g1, C1) == 7).all() and (np.einsum("ij,ij->i", C2 @ G, C2) == 7).all() and (np.einsum("ij,ij->i", g1, C2) == 0).all()
            best = np.full(len(buf), 10 ** 6, dtype=np.int64); arg = [None] * len(buf)
            for c7, XG, X, nrm in shells:                                 # norm 4 (the long list) only for the pairs without a witness of norm 2 or 3
                sel = np.arange(len(buf)) if nrm < 4 else np.flatnonzero(best >= 11)
                if not len(X) or not len(sel): continue
                E = c7 - (C1[sel] @ XG.T) ** 2 - (C2[sel] @ XG.T) ** 2; j = E.argmin(axis=1); m = E[np.arange(len(sel)), j]; assert (m > 0).all()
                for t in np.flatnonzero(m < best[sel]): q = sel[t]; best[q] = m[t]; arg[q] = (nrm, [int(x) for x in X[j[t]]])
            for q, b in enumerate(buf):
                e = int(best[q]); by[str(e) if e <= 10 else ">=11"] += 1
                if e <= 10:
                    if len(wit) < 50: wit.append({"o": b["o"], "min_E": e, "witness_norm": arg[q][0], "witness_coordinates": arg[q][1]})
                else: surv.append({"o": b["o"], "y1": b["y1"], "y2": b["y2"], "min_E": e})
            buf.clear()

        for raw in open(st, "rb"):
            line = raw.rstrip(b"\r\n")
            if not line: continue
            d = json.loads(line)
            if d.get("end"): end = d; break
            if "o" not in d or "y1" not in d: continue
            sh.update(line + b"\n"); buf.append(d); n += 1
            if len(buf) >= 150: flush()
        flush()
        ok = bool(end) and end.get("complete") is True and end.get("pairs") == n
        res.update(pairs=n, stream_complete=ok, stream_sha256=sh.hexdigest(), by_min_E=dict(by), survivors=len(surv), first_witnesses=wit, y1_left_indices=left,
                   engine_sha256=hashlib.sha256(open(os.path.join(PKG, "scripts", "frame_dfs_next.py"), "rb").read()).hexdigest()[:16], seconds=round(time.time() - t0, 1))
        json.dump(surv, open(os.path.join(od, lid + "_survivors.json"), "w")); json.dump(res, open(outf, "w"), indent=1)
        os.remove(st)
    rows = [json.load(open(os.path.join(od, f))) for f in sorted(os.listdir(od)) if len(f) == 8 and f.endswith(".json")]
    print("%-4s %-18s %5s %6s %5s %8s %9s | %s" % ("lid", "roots", "y1", "by Y1", "left", "pairs", "survivors", "pairs by minimum of E over norms 2, 3, 4"))
    for r in rows: print("%03d  %-18s %5d %6d %5d %8d %9d | %s%s" % (r["id"], r["roots"], r["y1"], r["y1_with_root_of_product_2"], r["y1_left"], r["pairs"], r["survivors"], dict(sorted(r["by_min_E"].items())),
                                                              "" if r["pairs"] == 0 or r.get("stream_complete") else "  STREAM NOT COMPLETE"))
    print("lattices done: %d; with no pair left for a search: %d (%s); survivors in all: %d" % (len(rows), sum(1 for r in rows if r["survivors"] == 0),
          " ".join("%03d" % r["id"] for r in rows if r["survivors"] == 0), sum(r["survivors"] for r in rows)))


if __name__ == "__main__":
    main()
