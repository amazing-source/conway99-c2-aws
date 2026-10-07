"""F4: compare the stream producer's pair list with an independent enumeration (C2 lab, 2026-10-07).

  python f4_compare.py <package dir> <lid> <producer stream (identity-only symmetry file)> <ypairs_c2 output json> <out.json>

Two enumerations of the admissible pairs (y1, y2) of one lattice, with no code in common:
  * the producer of the sweep, c1/code/y_pairs_gamma.py, run with an identity-only symmetry file: y1 W(R)-dominant, y2 dominant
    for the stabiliser W_J of y1 and taken up to sign;
  * the lab's ypairs_c2.py: Fincke-Pohst enumeration of ALL vectors of norm 7 with the admissibility filters, then the W(R)-dominant
    y1 and, for each, the W_J-dominant y2 up to sign (its own simple roots).
Both lists are sets of representatives of the same equivalence (W(R) on the pair, sign of y2), under the same necessary filters
(roots: |(alpha,y)| <= 2 and Y <= 6; norm 3: Y <= 13; new roots: <= 3/2, never both; the producer's "trap 8/7" adds nothing to
these: every dual vector with E <= 7 has a representative among the roots and the norm-3 vectors). So after bringing every pair
to one canonical form the two sets must be EQUAL.
Canonical form, in the integer coordinates of ypairs_c2's basis, with its simple roots: reflect (y1, y2) together until y1 is
dominant; then y2 -> the smaller of its W_J-dominant form and the W_J-dominant form of -y2 (as ypairs_c2 does).
Also checked: the number of lines of norm 7 found by ypairs_c2 equals 11178 * N3 / 2 (theta series), when the log is given
(--log <file>). Output: counts on both sides, the sizes of the two differences, and up to 20 pairs of each."""
import sys, os, json, re, time
from fractions import Fraction as F
import numpy as np


def main():
    pkg, lid, streamf, indf, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
    t0 = time.time(); sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs as FD                                             # only for lattice_data and the simple roots of ypairs_c2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ind = json.load(open(indf)); Bq = [[F(x) for x in row] for row in ind["basis"]]
    Gq = [[sum(a * b for a, b in zip(u, v)) for v in Bq] for u in Bq]; G = np.array([[int(x) for x in row] for row in Gq], dtype=np.int64)
    Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in Bq]))
    L = FD.lattice_data(json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))["gens"])
    assert [[str(x) for x in row] for row in L["B"]] == ind["basis"], "ypairs_c2 output made in another basis"
    import ypairs_c2 as YC                                             # importable: no top-level work
    Sm = YC.simple_roots(L["R"], G) if len(L["R"]) else np.zeros((0, 24), dtype=np.int64); SG = Sm @ G

    def canon(y1, y2):
        y1 = y1.copy(); y2 = y2.copy()
        while len(Sm):
            ip = SG @ y1; k = int(np.argmin(ip))
            if ip[k] >= 0: break
            y2 = y2 - int(SG[k] @ y2) * Sm[k]; y1 = y1 - int(ip[k]) * Sm[k]
        J = Sm[(SG @ y1) == 0] if len(Sm) else Sm
        v = YC.dominant(y2, J, G) if len(J) else y2; w = YC.dominant(-y2, J, G) if len(J) else -y2
        return tuple(int(t) for t in y1), min(tuple(int(t) for t in v), tuple(int(t) for t in w))

    A = set(); ny1a = set()
    for y1, y2 in ind["pairs"]:
        c = canon(np.array(y1, dtype=np.int64), np.array(y2, dtype=np.int64)); A.add(c); ny1a.add(c[0])
    assert len(A) == len(ind["pairs"]), "ypairs_c2 pairs are not distinct after canonicalisation"
    B = set(); ny1b = set(); n = 0; end = None; dup = 0
    for raw in open(streamf, "rb"):
        line = raw.strip()
        if not line: continue
        r = json.loads(line)
        if r.get("end"): end = r; break
        if "o" not in r or "y1" not in r: continue
        n += 1; ys = []
        for key in ("y1", "y2"):
            v = [F(x) for x in r[key]]; cf = np.rint(np.array([float(x) for x in v]) @ Binv).astype(np.int64)
            assert all(sum(int(c_) * Bq[i][j] for i, c_ in enumerate(cf)) == v[j] for j in range(24)), "y not in U"
            ys.append(cf)
        c = canon(ys[0], ys[1])
        if c in B: dup += 1
        B.add(c); ny1b.add(c[0])
    stream_ok = bool(end) and end.get("complete") is True and end.get("pairs") == n
    onlyA = sorted(A - B)[:20]; onlyB = sorted(B - A)[:20]
    out = {"id": int(lid), "independent": {"pairs": len(A), "y1_orbits": len(ny1a), "n_admissible_lines": ind.get("n_admissible_lines")},
           "producer": {"pairs_in_stream": n, "distinct_after_canonical_form": len(B), "duplicates": dup, "y1_orbits": len(ny1b), "stream_complete": stream_ok},
           "only_in_independent": len(A - B), "only_in_producer": len(B - A), "examples_only_in_independent": onlyA, "examples_only_in_producer": onlyB,
           "equal": bool(stream_ok and A == B), "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    if "--log" in sys.argv:
        txt = open(sys.argv[sys.argv.index("--log") + 1], errors="replace").read(); m = re.search(r"norm-7 lines (\d+)", txt)
        if m: out["norm7_lines"] = int(m.group(1)); out["norm7_lines_expected"] = 11178 * 4096 // 2; out["norm7_count_ok"] = out["norm7_lines"] == out["norm7_lines_expected"]
    json.dump(out, open(outf, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("examples")}), flush=True)


if __name__ == "__main__":
    main()
