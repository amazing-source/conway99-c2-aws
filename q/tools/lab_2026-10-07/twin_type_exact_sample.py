"""Sample check of the one floating-point decision of the twin rule (C2 lab, 2026-10-07).

  .venv/Scripts/python.exe scripts/cloud/twin_type_exact_sample.py <lid> <plan json> <identity gamma json> <out.json>

For every pair of the producer's stream of one lattice (plan given, identity symmetry): the twin roots as the engine builds them
(scripts/twin_transfer.twin_roots), then the root type of the twin computed twice:
  * as the engine does (twin_transfer.rtype: components from the rounded integer products, RANK of each component by
    numpy.linalg.matrix_rank, i.e. floating point);
  * from INTEGERS only: for a component with m positive roots, the number of positive roots non-orthogonal to a given one is
    2h - 4 (h = Coxeter number), so h is read from the integer product matrix and the rank is 2m / h; no rank computation at all.
Reports the number of pairs with twin roots, the number where the two types differ (expected 0), and the types met.
A sample on one lattice, not a proof for the sweep."""
import sys, os, json, subprocess, math, collections
from fractions import Fraction as F
import numpy as np
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); PKG = os.path.join(LAB, "c2_cloud_run_v10")
sys.path.insert(0, os.path.join(PKG, "scripts"))


def rtype_int(Rt, G):
    P = np.rint(Rt @ G @ Rt.T).astype(np.int64); n = len(Rt); comp = -np.ones(n, int); k = 0
    for s in range(n):
        if comp[s] >= 0: continue
        st = [s]; comp[s] = k
        while st:
            a = st.pop()
            for b in np.flatnonzero(P[a] != 0):
                if comp[b] < 0: comp[b] = k; st.append(b)
        k += 1
    c = collections.Counter()
    for q in range(k):
        idx = np.flatnonzero(comp == q); m = len(idx); n1 = int((np.abs(P[idx[0], idx]) == 1).sum()); h2 = n1 + 4          # 2h
        assert (4 * m) % h2 == 0, "not a root system"; r = 4 * m // h2                                                        # r = 2m / h
        t = ("E", r) if (r, m) in ((6, 36), (7, 63), (8, 120)) else ("A", r) if m == r * (r + 1) // 2 else ("D", r)
        if t[0] == "D": assert m == r * (r - 1), "component is none of A, D, E"
        c[t] += 1
    return tuple(sorted(c.items()))


def main():
    import frame_dfs_next as FD, twin_transfer as TT
    lid, plan, gam, outf = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]), os.path.abspath(sys.argv[4])
    U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", lid + ".json"); st = outf + ".stream.jsonl"
    r = subprocess.run([sys.executable, os.path.join(PKG, "c1", "code", "y_pairs_gamma.py"), U, gam, outf + ".stats.json", "--from-plan", plan, "--stream", st, "--max-seconds", "200"],
                       cwd=os.path.join(PKG, "c1", "code"), capture_output=True, text=True); assert r.returncode == 0, r.stderr[-300:]
    L = FD.lattice_data(json.load(open(U))["gens"], F(1)); G = np.asarray(L["G"], dtype=np.int64)
    Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]; DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * int(x.denominator) // math.gcd(DEN, int(x.denominator))
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); Binv = np.linalg.inv(BD.astype(np.float64))
    n = with_roots = differ = 0; types = collections.Counter(); ex = []
    for line in open(st):
        d = json.loads(line)
        if "y1" not in d: continue
        n += 1; cs = []
        for key in ("y1", "y2"):
            v = np.array([int(F(x) * DEN) for x in d[key]], dtype=np.int64); c = np.rint(v.astype(np.float64) @ Binv).astype(np.int64); assert (c @ BD == v).all(); cs.append(c)
        Rt = TT.twin_roots(L, cs[0], cs[1])
        if not len(Rt): continue
        with_roots += 1; a = TT.rtype(Rt, G); b = rtype_int(Rt, G); types[str(b)] += 1
        if a != b:
            differ += 1
            if len(ex) < 5: ex.append({"pair": n - 1, "float": str(a), "integers": str(b)})
    os.remove(st)
    out = {"id": int(lid), "pairs": n, "pairs_with_twin_roots": with_roots, "types_differ": differ, "examples": ex, "distinct_twin_types": len(types), "most_common": types.most_common(8)}
    json.dump(out, open(outf, "w"), indent=1); print(json.dumps({k: out[k] for k in ("id", "pairs", "pairs_with_twin_roots", "types_differ", "distinct_twin_types")}))


if __name__ == "__main__":
    main()
