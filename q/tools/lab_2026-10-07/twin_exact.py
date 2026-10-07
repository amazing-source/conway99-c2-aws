"""Exact evaluation of the twin rule on the pairs of one lattice (C2 lab, 2026-10-07; contract of Codex, message of 20:10 UTC).

  .venv/Scripts/python.exe scripts/cloud/twin_exact.py <lid> <plan json> <identity gamma json> <out.json>

For every pair (y1, y2) of the producer's stream (plan given, identity symmetry) that the characteristic-vector rule does not
exclude, the twin lattice's roots are built in INTEGERS: for x in the lists of norm 2, 3, 4 with (norm, Y) in
{(2,0), (2,5), (3,8), (3,9), (4,18)}, a = (x,y1), b = (x,y2), (c,d) = (2a+2b, -2a+2b) reduced mod 7 into [-3,3],
    Q = 7 x + (c - a) y1 + (d - b) y2          (7 times the twin root, integer coordinates).
Checked exactly: Q G Q^T = 98 on the diagonal; all products divisible by 49, giving the integer matrix P of products of the twin
roots; the rows are distinct up to sign; (Q, y1) and (Q, y2) divisible by 7.
From P only: components; for a component with m lines, n1 = number of lines non-orthogonal to its first line, h = (n1 + 4) / 2,
rank = 2m / h (asserted integral), type A / D / E from (rank, m) with m = r(r+1)/2, r(r-1) or (6,36), (7,63), (8,120) asserted.
Reported per pair class, with NO use of any tracker status:
  richer       the twin has strictly more roots than the lattice (transfer sound by induction on the number of roots);
  same_type    the twin has the lattice's own root type (candidate for the canonical rule);
  other        the twin has at most as many roots and another type: a transfer of such a pair needs an independent proof of
               the target, or the pair must be examined directly;
and the comparison with the engine's own floating-point type (twin_transfer.rtype): number of pairs where they differ.
A measure on one lattice; it pronounces nothing."""
import sys, os, json, subprocess, math, collections, time
from fractions import Fraction as F
import numpy as np
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); PKG = os.path.join(LAB, "c2_cloud_run_v10")
sys.path.insert(0, os.path.join(PKG, "scripts"))


def twin_Q(L, G, y1, y2, cache):
    out = []
    for key, n, Ys in (("R", 2, (0, 5)), ("X3", 3, (8, 9)), ("X4", 4, (18,))):
        if key not in cache: X = np.asarray(L[key], dtype=np.int64).reshape(-1, 24); cache[key] = (X, X @ G)
        X, XG = cache[key]
        a = XG @ y1; b = XG @ y2; m = np.isin(a * a + b * b, Ys)
        a, b, Xm = a[m], b[m], X[m]
        c = (2 * a + 2 * b + 3) % 7 - 3; d = (-2 * a + 2 * b + 3) % 7 - 3
        out.append(7 * Xm + np.outer(c - a, y1) + np.outer(d - b, y2))
    return np.vstack(out)


def exact_type(Q, G, y1, y2):
    assert np.abs(Q).max(initial=0) < 2 ** 20                                # products below stay far from 2^63
    QG = Q @ G; P49 = QG @ Q.T; assert (np.diag(P49) == 98).all() and (P49 % 49 == 0).all(), "not twin roots"
    assert ((QG @ y1) % 7 == 0).all() and ((QG @ y2) % 7 == 0).all()
    S = {tuple(int(v) for v in q) for q in Q}; assert len(S) == len(Q) and not any(tuple(-v for v in q) in S for q in S), "lines not distinct"
    P = P49 // 49; n = len(Q); comp = -np.ones(n, int); k = 0
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
        idx = np.flatnonzero(comp == q); m = len(idx); h2 = int((np.abs(P[idx[0], idx]) == 1).sum()) + 4
        assert (4 * m) % h2 == 0; r = 4 * m // h2
        t = ("E", r) if (r, m) in ((6, 36), (7, 63), (8, 120)) else ("A", r) if m == r * (r + 1) // 2 else ("D", r)
        assert t[0] != "D" or m == r * (r - 1), "component is none of A, D, E"
        c[t] += 1
    return tuple(sorted(c.items()))


def main():
    import frame_dfs_next as FD, twin_transfer as TT
    lid, plan, gam, outf = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]), os.path.abspath(sys.argv[4]); t0 = time.time()
    U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", lid + ".json"); st = outf + ".stream.jsonl"
    r = subprocess.run([sys.executable, os.path.join(PKG, "c1", "code", "y_pairs_gamma.py"), U, gam, outf + ".stats.json", "--from-plan", plan, "--stream", st, "--max-seconds", "240"],
                       cwd=os.path.join(PKG, "c1", "code"), capture_output=True, text=True); assert r.returncode == 0, r.stderr[-300:]
    t1 = time.time(); rec = json.load(open(U)); L = FD.lattice_data(rec["gens"], F(1)); G = np.asarray(L["G"], dtype=np.int64); own = TT.parse(rec["roots"]); nown = len(L["R"])
    Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]; DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * int(x.denominator) // math.gcd(DEN, int(x.denominator))
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); Binv = np.linalg.inv(BD.astype(np.float64)); cache = {}
    c = collections.Counter(); n = 0
    for line in open(st):
        d = json.loads(line)
        if "y1" not in d: continue
        n += 1; cs = []
        for key in ("y1", "y2"):
            v = np.array([int(F(x) * DEN) for x in d[key]], dtype=np.int64); cc = np.rint(v.astype(np.float64) @ Binv).astype(np.int64); assert (cc @ BD == v).all(); cs.append(cc)
        if FD.char_trap(L, cs[0], cs[1]) is not None: c["characteristic-vector rule"] += 1; continue
        Q = twin_Q(L, G, cs[0], cs[1], cache)
        if not len(Q): c["no twin root"] += 1; continue
        ty = exact_type(Q, G, cs[0], cs[1]); Rt = TT.twin_roots(L, cs[0], cs[1])
        assert len(Rt) == len(Q); c["float type differs"] += int(TT.rtype(Rt, G) != ty)
        c["richer" if len(Q) > nown else "same_type" if ty == own else "other"] += 1
    os.remove(st)
    out = {"id": int(lid), "pairs": n, "own_root_lines": nown, "classes": dict(c), "seconds_producer": round(t1 - t0, 1), "seconds_twin": round(time.time() - t1, 1)}
    json.dump(out, open(outf, "w"), indent=1); print(json.dumps(out))


if __name__ == "__main__":
    main()
