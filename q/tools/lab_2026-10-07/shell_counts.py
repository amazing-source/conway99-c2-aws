"""Shells of norm 2, 3, 4 of the 156 lattices: exact checks of the engine's lists (C2 lab, 2026-10-07; hole H3 of the engine audit).

  .venv/Scripts/python.exe scripts/cloud/shell_counts.py <out.json> [seconds budget, default 250]     (resumable: run it again)

For each lattice, the lists are the ones the search engine builds for its candidates: frame_dfs_next.lattice_data(gens, 1) of the
package c2_cloud_run_v10, on external_runs/structures_3eceb4d/U/<lid>.json: R (roots), X3, X4 (norms 3 and 4), one vector per
pair +-x, in integer coordinates of the engine's basis B. Checked here in exact arithmetic (Python integers / fractions):
  a. B is a basis of U: every row of B is an integer combination of the 24 generators of the lattice file, with a coefficient
     matrix of determinant +-1; G = B B^T is the engine's Gram matrix, integral, of determinant 1;
  b. every listed vector has integer coordinates (so it is in U) and exactly the norm of its list (c G c^T = 2, 3, 4);
  c. in each list the vectors are distinct and no vector is listed with its opposite; so the list holds exactly 2 len vectors;
  d. N4 = 196560 - 24 N2 - 24 N3 with N_k = 2 len (theta series of an odd unimodular lattice of rank 24 without norm 1).
Why (a)-(d) prove that the three lists are complete: by (a)-(c) each N_k^enum <= N_k^true; the identity holds for the true counts;
if it also holds for the enumerated ones, then (N4^true - N4^enum) + 24 (N2^true - N2^enum) + 24 (N3^true - N3^enum) = 0 with three
terms >= 0. Also recorded: N3 (4096 expected), the number of pairs of doubled new roots S2 (norm 8, (N2 + 48)/2 expected... only
recorded), sha256 of the lattice file and of the engine, sha of the basis (the lists are those of THIS basis; another machine may
reduce to another basis and build its lists again with the same code).
The first table measures/SHELL_COUNTS_2026-10-07.json was written at 13:37 UTC by an inline command (kept in
q/tools/lab_2026-10-07/shell_counts_first_run.txt) that made check d and the exact norm of X4 only."""
import sys, os, json, time, hashlib
from fractions import Fraction as F
import numpy as np
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); PKG = os.path.join(LAB, "c2_cloud_run_v10")
sys.path.insert(0, os.path.join(PKG, "scripts"))


def inv_det(M):
    n = len(M); A = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(M)]; det = F(1)
    for k in range(n):
        p = next((i for i in range(k, n) if A[i][k] != 0), None)
        if p is None: return None, F(0)
        if p != k: A[k], A[p] = A[p], A[k]; det = -det
        det *= A[k][k]; q = A[k][k]; A[k] = [x / q for x in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]; A[i] = [x - f * y for x, y in zip(A[i], A[k])]
    return [r[n:] for r in A], det


def main():
    import frame_dfs_next as FD
    outf = sys.argv[1]; budget = float(sys.argv[2]) if len(sys.argv) > 2 else 250.0; t0 = time.time()
    done = json.load(open(outf)) if os.path.exists(outf) else {}
    esha = hashlib.sha256(open(os.path.join(PKG, "scripts", "frame_dfs_next.py"), "rb").read()).hexdigest()[:16]
    for i in range(156):
        lid = "%03d" % i
        if lid in done: continue
        if time.time() - t0 > budget: break
        uf = os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", lid + ".json"); gens_s = json.load(open(uf))["gens"]
        L = FD.lattice_data(gens_s, F(1)); G = np.asarray(L["G"], dtype=np.int64)
        gens = [[F(str(x)) for x in g] for g in gens_s]; B = [[F(str(x)) for x in row] for row in L["B"]]
        ginv, gdet = inv_det(gens); T = [[sum(row[k] * ginv[k][j] for k in range(24)) for j in range(24)] for row in B]
        _, tdet = inv_det(T); Gq = [[sum(a * b for a, b in zip(u, v)) for v in B] for u in B]; _, det = inv_det(Gq)
        a = (len(gens) == 24 and all(x.denominator == 1 for r in T for x in r) and abs(tdet) == 1 and
             all(Gq[p][q] == int(G[p][q]) for p in range(24) for q in range(24)) and det == 1)
        res = {}; b = True; c = True
        for name, key, norm in (("N2", "R", 2), ("N3", "X3", 3), ("N4", "X4", 4)):
            X = np.asarray(L[key], dtype=np.int64).reshape(-1, 24)
            b &= bool((np.einsum("ij,jk,ik->i", X, G, X) == norm).all()) if len(X) else True
            S = {tuple(int(v) for v in x) for x in X}
            c &= len(S) == len(X) and not any(tuple(-v for v in x) in S for x in S)
            res[name] = 2 * len(X)
        d = res["N4"] == 196560 - 24 * res["N2"] - 24 * res["N3"]
        done[lid] = dict(res, basis_of_U=bool(a), norms_exact=bool(b), distinct_up_to_sign=bool(c), identity=bool(d), ok=bool(a and b and c and d),
                         S2_pairs=int(len(L["S2"])), lattice_file_sha256=hashlib.sha256(open(uf, "rb").read()).hexdigest()[:16], engine_sha256=esha,
                         basis_sha=hashlib.sha256(json.dumps([[str(x) for x in row] for row in L["B"]]).encode()).hexdigest()[:16])
        json.dump(done, open(outf, "w"), indent=0)
    ok = sum(1 for v in done.values() if v.get("ok")); n3 = sum(1 for v in done.values() if v.get("N3") == 4096)
    print("lattices done: %d of 156; all four checks ok: %d; N3 = 4096: %d; not ok: %s; %.0f s" % (
        len(done), ok, n3, [l for l, v in done.items() if not v.get("ok")], time.time() - t0))


if __name__ == "__main__":
    main()
