"""Exact certificate for the DEFERRED pairs of a Golay-family lattice (001, 002) (C2 lab, 2026-10-07). Same checks as
cert_stream.py; no producer is needed: the pair lists are files of the package and the records keep y1, y2 of every open pair.

  .venv/Scripts/python.exe scripts/cloud/cert_golay.py <package dir> <lid> <out.json>

Pairs to certify: every pair index whose best state over the accepted records (import_sweep.py: same reading, same checks) is
DEFERRED. For each of them, in exact integers:
  * the entry (index, y1, y2) of the record equals the pair of that index in the package's pair files (data/golay/<lid>/pairs_*.json,
    sorted by name, concatenated; their sha256 is the one the records carry);
  * y1, y2 are in U (U unimodular: (b, y) integral for the 24 basis vectors b), (y1,y1) = (y2,y2) = 7, (y1,y2) = 0, in the frame's
    scale (norm = a.a / scale);
  * a candidate root r of U, (r,r) = 2, has (r,y1)^2 + (r,y2)^2 = 5 (state T18) or 4 (state T20; a root with 5 is noted).
The lattice: Gram of the basis integral, symmetric, determinant +-1 (exact). The engine only supplies the basis and the candidate
roots. This pronounces no exclusion."""
import sys, os, json, glob, hashlib, time, math, collections
from fractions import Fraction as F
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import import_sweep as IS
from cert_stream import exact_det, toF


def main():
    pkg, lid, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3]; t0 = time.time()
    ST, GO = IS.engines(); PAR = IS.wrapper_shas("q/par_consumer.py"); DEF = IS.wrapper_shas("q/defer_consumer.py")
    recs = []
    for f in glob.glob(os.path.join(IS.REPO, "resultats_q", "*", "results", lid + "_*_*.jsonl")):
        b = os.path.basename(f)[:-6].split("_")
        for l in open(f, errors="replace"):
            if '"verdicts"' not in l: continue
            try: d = json.loads(l)
            except ValueError: continue
            if d.get("kind") != "golay_pairs" or not d.get("chunk_ok"): continue
            if not IS.check(d, lid, int(b[1]), int(b[2]), ST, GO, PAR, DEF): recs.append(d)
    N = recs[0]["pairs_total"]; state = bytearray(N); entry = {}
    for d in recs:
        a, b = d["range"]; opn = {}
        for e in d.get("not_excluded") or []:
            x = IS.cls(str(e.get("verdict", ""))); s = 3 if x == "defer_T18" else 2 if x == "defer_T20" else 1; opn[e["index"]] = s
            if s >= 2: entry.setdefault((e["index"], s), e)
        for i in range(a, b):
            s = opn.get(i, 4)
            if s > state[i]: state[i] = s
    need = {i: ("T18" if state[i] == 3 else "T20") for i in range(N) if state[i] in (2, 3)}
    # the pair files
    files = sorted(glob.glob(os.path.join(pkg, "data", "golay", lid, "pairs_*.json"))); h = hashlib.sha256(); off = 0; meta = None; pairs = {}
    for f in files:
        raw = open(f, "rb").read(); h.update(raw); d = json.loads(raw)
        m = (d["basis"], d["scale"])
        if meta is None: meta = m
        assert m == meta
        P = d["pairs"] if "pairs" in d else None; c = len(P) if P is not None else len(d["y2s"])
        for i in need:
            if off <= i < off + c: pairs[i] = P[i - off] if P is not None else [d["y1"], d["y2s"][i - off]]
        off += c; del d, raw
    assert off == N, (off, N)
    fsha = h.hexdigest(); assert all(r["pair_files_sha256"] == fsha for r in recs), "pair files differ from the records'"
    basis, scale = meta; scale = int(scale)
    sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs_next as FD
    L = FD.lattice_data([[F(x) for x in row] for row in basis], F(1, scale)); Bq = [[toF(x) for x in row] for row in L["B"]]
    Gq = [[sum(a * b for a, b in zip(u, v)) / scale for v in Bq] for u in Bq]
    assert all(x.denominator == 1 for row in Gq for x in row) and all(Gq[i][j] == Gq[j][i] for i in range(24) for j in range(24)), "Gram not integral"
    G = [[int(x) for x in row] for row in Gq]; det = exact_det(G); assert det in (1, -1), det
    CR = [[int(x) for x in r] for r in L["R"]]
    for c in CR: assert sum(c[i] * G[i][j] * c[j] for i in range(24) for j in range(24)) == 2
    DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * x.denominator // math.gcd(DEN, x.denominator)
    DEN = int(DEN)
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); CRn = np.array(CR, dtype=np.int64).reshape(-1, 24)
    res = {"T18": {"listed": 0, "certified": 0}, "T20": {"listed": 0, "certified": 0, "also_T18": 0}}; invalid = []
    idx = sorted(need)
    for s in range(0, len(idx), 2000):
        part = idx[s:s + 2000]; ok_rows = []; Y1 = []; Y2 = []
        for i in part:
            tag = need[i]; res[tag]["listed"] += 1; e = entry.get((i, 3 if tag == "T18" else 2))
            if e is None or [str(x) for x in pairs[i][0]] != [str(x) for x in e["y1"]] or [str(x) for x in pairs[i][1]] != [str(x) for x in e["y2"]]:
                invalid.append([i, "record entry differs from the pair file"]); continue
            v1 = [F(x) for x in e["y1"]]; v2 = [F(x) for x in e["y2"]]
            if any(q.denominator != 1 for q in v1 + v2): invalid.append([i, "not integral in the frame"]); continue
            ok_rows.append(i); Y1.append([int(q) for q in v1]); Y2.append([int(q) for q in v2])
        if not ok_rows: continue
        Y1 = np.array(Y1, dtype=np.int64); Y2 = np.array(Y2, dtype=np.int64); DS = DEN * scale
        W1 = Y1 @ BD.T; W2 = Y2 @ BD.T
        inU = ((W1 % DS) == 0).all(axis=1) & ((W2 % DS) == 0).all(axis=1)
        normal = ((Y1 * Y1).sum(axis=1) == 7 * scale) & ((Y2 * Y2).sum(axis=1) == 7 * scale) & ((Y1 * Y2).sum(axis=1) == 0)
        W1 //= DS; W2 //= DS
        A = W1 @ CRn.T; B = W2 @ CRn.T; YY = A * A + B * B; has5 = (YY == 5).any(axis=1); has4 = (YY == 4).any(axis=1)
        for q, i in enumerate(ok_rows):
            tag = need[i]
            if not inU[q]: invalid.append([i, "y not in U"]); continue
            if not normal[q]: invalid.append([i, "norms / orthogonality"]); continue
            if tag == "T18":
                if has5[q]: res["T18"]["certified"] += 1
                else: invalid.append([i, "state T18 but no root with 5"])
            else:
                if has4[q] or has5[q]: res["T20"]["certified"] += 1; res["T20"]["also_T18"] += int(has5[q])
                else: invalid.append([i, "state T20 but no root with 4 or 5"])
    ok = not invalid and all(res[t]["certified"] == res[t]["listed"] for t in res)
    hs = collections.Counter(state)
    out = {"id": int(lid), "pairs_total": N, "pair_files_sha256": fsha, "records": len(recs),
           "state": {"not_covered": hs[0], "incomplete_or_other": hs[1], "deferred_T20": hs[2], "deferred_T18": hs[3], "excluded": hs[4]},
           "lattice": {"det": det, "roots_pm": len(CR), "denominator": DEN, "scale": scale}, "T18": res["T18"], "T20": res["T20"],
           "invalid": invalid[:50], "n_invalid": len(invalid), "ok": ok,
           "cert_golay_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
           "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    json.dump(out, open(outf, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("id", "pairs_total", "state", "T18", "T20", "n_invalid", "ok", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
