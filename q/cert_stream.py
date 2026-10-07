"""Exact certificate for the DEFERRED pairs of one stream record (C2 lab, 2026-10-07). Second computation of the deferral rule,
with the checks the quick deferral path does not make. It pronounces no exclusion.

  <producer of the job> | python cert_stream.py <package dir> <lid> <record.json> <out.json>

<record.json>: the accepted sweep record of the job (fields id, chunk, sha256, n_pairs, deferred = {T18: [...], T20: [...]},
0-based positions among the pair lines of the producer stream). The producer is the package's own command for that job
(c1/code/y_pairs_gamma.py ... --from-plan <plan> --chunk k/n --stream -).

What is checked, all in exact integer arithmetic (the engine is used ONLY to get a basis B of U and a list of candidate roots):
  1. the lattice: G = B B^T is integral, symmetric, with determinant +-1 (exact fraction-free elimination);
     every candidate root c (integer coordinates) has c G c^T = 2;
  2. the stream: the pair lines are hashed exactly like the consumer does; at the end the sha256 and the number of pairs must be
     those of the record, and the end line must say complete;
  3. for every pair at a deferred position, with y1, y2 the rational vectors of the line and D the common denominator of B:
       D y is integral, w = B y is integral (so y is in U, U being unimodular), (y1,y1) = (y2,y2) = 7, (y1,y2) = 0;
       a_r = (r,y1) = c_r . w1 and b_r = (r,y2) = c_r . w2 for every candidate root r;
       listed T18: some root has a^2 + b^2 = 5.  listed T20: some root has a^2 + b^2 = 4 (a root with 5 is noted: the pair is
       then covered by T18 as well).
       listed T20_norm4 (rule Q_DEFER_N4 of q/defer_consumer.py, 07/10): some candidate vector x of norm 4 (integer coordinates c,
       c G c^T = 4 checked) has |(x,y1)| = |(x,y2)| = 3. Then E(x) = 7 * 4 - 9 - 9 = 10: by the bridge, which holds for every
       vector of U, an eigenfunction of squared norm 20 (T20).
ok = 1, 2 and 3 hold for every deferred pair. One witness root per pair is not stored; `--witnesses` stores the first 20.
By the bridge (lemma/BRIDGE.md of the compute repo) such a root gives a sigma-odd integer (-4)-eigenfunction of squared norm
18 (T18) or 20 (T20) for any frame hosted by (U, y1, y2)."""
import sys, os, json, hashlib, time, math
from fractions import Fraction as F
import numpy as np


def toF(x):
    """exact Fraction of a basis entry (Fraction, Python int, numpy integer, or a string)"""
    if isinstance(x, F): return F(int(x.numerator), int(x.denominator))
    if isinstance(x, (int, np.integer)): return F(int(x))
    return F(str(x))


def exact_det(M):
    """determinant of an integer matrix, fraction-free (Bareiss), Python integers"""
    A = [[int(x) for x in row] for row in M]; n = len(A); sign = 1; prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            p = next((i for i in range(k + 1, n) if A[i][k] != 0), None)
            if p is None: return 0
            A[k], A[p] = A[p], A[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def main():
    pkg, lid, recf, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3], sys.argv[4]
    rec = json.load(open(recf)); t0 = time.time()
    assert "%03d" % rec["id"] == lid
    want = {}
    for tag in ("T18", "T20", "T20_norm4"):
        for i in rec["deferred"].get(tag, []):
            assert i not in want; want[i] = tag
    sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs_next as FD
    gens = json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))["gens"]
    L = FD.lattice_data(gens, F(1))
    Bq = [[toF(x) for x in row] for row in L["B"]]
    # 1. the lattice
    Gq = [[sum(a * b for a, b in zip(u, v)) for v in Bq] for u in Bq]
    assert all(x.denominator == 1 for row in Gq for x in row) and all(Gq[i][j] == Gq[j][i] for i in range(24) for j in range(24)), "Gram not integral"
    G = [[int(x) for x in row] for row in Gq]; det = exact_det(G); assert det in (1, -1), "determinant %d" % det
    CR = [[int(x) for x in r] for r in L["R"]]
    for c in CR:
        assert sum(c[i] * G[i][j] * c[j] for i in range(24) for j in range(24)) == 2, "a candidate root has not norm 2"
    DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * x.denominator // math.gcd(DEN, x.denominator)
    DEN = int(DEN)
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); CRn = np.array(CR, dtype=np.int64).reshape(-1, 24)
    CX4 = np.zeros((0, 24), dtype=np.int64)
    if any(t == "T20_norm4" for t in want.values()):                    # candidate vectors of norm 4 (one per +- pair), checked exactly
        CX4 = np.array([[int(x) for x in r] for r in L["X4"]], dtype=np.int64).reshape(-1, 24); Gn = np.array(G, dtype=np.int64)
        assert int(abs(CX4).max(initial=0)) ** 2 * int(abs(Gn).max()) * 576 < 2 ** 62
        assert (np.einsum("ij,jk,ik->i", CX4, Gn, CX4) == 4).all(), "a candidate vector of norm 4 has not norm 4"
    # 2. the stream
    sh = hashlib.sha256(); n = 0; end = None; got = {}
    for raw in sys.stdin.buffer:
        line = raw.rstrip(b"\r\n")
        if not line: continue
        r = json.loads(line)
        if r.get("end"): end = r; break
        if "o" not in r or "y1" not in r: continue
        sh.update(line + b"\n")
        if n in want: got[n] = (r["y1"], r["y2"])
        n += 1
    stream_ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and n == rec["n_pairs"] and sh.hexdigest() == rec["sha256"] == end.get("sha256")
    # 3. the pairs
    res = {"T18": {"listed": len(rec["deferred"]["T18"]), "certified": 0}, "T20": {"listed": len(rec["deferred"]["T20"]), "certified": 0, "also_T18": 0},
           "T20_norm4": {"listed": len(rec["deferred"].get("T20_norm4", [])), "certified": 0, "also_root": 0}}
    invalid = []; missing = sorted(set(want) - set(got)); wit = []
    idx = sorted(got)
    for s in range(0, len(idx), 2000):
        part = idx[s:s + 2000]; Y = []
        for i in part:
            row = []
            for key in (0, 1):
                v = [F(x) * DEN for x in got[i][key]]
                if any(q.denominator != 1 for q in v): row = None; break
                row.append([int(q) for q in v])
            Y.append(row)
        good = [k for k, row in enumerate(Y) if row is not None]
        for k, row in enumerate(Y):
            if row is None: invalid.append([part[k], "D y not integral"])
        if not good: continue
        Y1 = np.array([Y[k][0] for k in good], dtype=np.int64); Y2 = np.array([Y[k][1] for k in good], dtype=np.int64)
        assert max(abs(Y1).max(), abs(Y2).max()) * max(1, abs(BD).max()) * 24 < 2 ** 62
        W1 = Y1 @ BD.T; W2 = Y2 @ BD.T; D2 = DEN * DEN
        inU = ((W1 % D2) == 0).all(axis=1) & ((W2 % D2) == 0).all(axis=1)
        n1 = (Y1 * Y1).sum(axis=1); n2 = (Y2 * Y2).sum(axis=1); n12 = (Y1 * Y2).sum(axis=1)
        normal = (n1 == 7 * D2) & (n2 == 7 * D2) & (n12 == 0)
        W1 //= D2; W2 //= D2
        A = W1 @ CRn.T; B = W2 @ CRn.T; YY = A * A + B * B
        has5 = (YY == 5).any(axis=1); has4 = (YY == 4).any(axis=1)
        has33 = np.zeros(len(good), dtype=bool)
        for q in [q for q, k in enumerate(good) if want[part[k]] == "T20_norm4"]:      # |(x,y1)| = |(x,y2)| = 3 for a norm-4 x: E = 28 - 18 = 10
            has33[q] = bool(((np.abs(CX4 @ W1[q]) == 3) & (np.abs(CX4 @ W2[q]) == 3)).any())
        for q, k in enumerate(good):
            i = part[k]; tag = want[i]
            if not inU[q]: invalid.append([i, "y not in U"]); continue
            if not normal[q]: invalid.append([i, "norms / orthogonality: %d %d %d over D^2 = %d" % (n1[q], n2[q], n12[q], D2)]); continue
            if tag == "T20_norm4":
                if has33[q]: res["T20_norm4"]["certified"] += 1; res["T20_norm4"]["also_root"] += int(has5[q] or has4[q])
                else: invalid.append([i, "listed T20_norm4 but no norm-4 vector with (3, 3)"])
                continue
            if tag == "T18":
                if has5[q]: res["T18"]["certified"] += 1
                else: invalid.append([i, "listed T18 but no root with 5"])
            else:
                if has4[q] or has5[q]: res["T20"]["certified"] += 1; res["T20"]["also_T18"] += int(has5[q])
                else: invalid.append([i, "listed T20 but no root with 4 or 5"])
            if "--witnesses" in sys.argv and len(wit) < 20:
                j = int(np.flatnonzero(YY[q] == (5 if has5[q] else 4))[0])
                wit.append({"position": i, "y1": got[i][0], "y2": got[i][1], "root_coordinates": CR[j], "a": int(A[q, j]), "b": int(B[q, j])})
    ok = stream_ok and not invalid and not missing and all(res[t]["certified"] == res[t]["listed"] for t in res)        # the three lists
    out = {"id": rec["id"], "chunk": rec["chunk"], "sha256": rec["sha256"], "n_pairs": rec["n_pairs"], "stream_pairs": n, "stream_sha256": sh.hexdigest(),
           "stream_ok": stream_ok, "lattice": {"det": det, "roots_pm": len(CR), "norm4_pm": int(len(CX4)), "denominator": DEN}, "T18": res["T18"], "T20": res["T20"],
           "T20_norm4": res["T20_norm4"],
           "invalid": invalid[:50], "n_invalid": len(invalid), "positions_not_in_stream": missing[:50], "ok": ok, "witnesses": wit,
           "cert_stream_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
           "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    json.dump(out, open(outf, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("id", "chunk", "stream_ok", "T18", "T20", "T20_norm4", "n_invalid", "ok", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
