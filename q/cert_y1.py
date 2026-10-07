"""Exact certificate "fixed y1" for y1 representatives of a stream plan (C2 lab, 2026-10-07; lemma of Codex, same day).
It pronounces no exclusion.

  python cert_y1.py <package dir> <lid> <plan.json> <out.json> [--reps 181,176 | --all]

Lemma (fixed y1). Let y1 in U have norm 7 and let r in U be a root, (r,r) = 2, with (r,y1) = +-2. Then for EVERY y2 in U the
bridge function E(r) = 7 (r,r) - (r,y1)^2 - (r,y2)^2 equals 10 - b^2, b = (r,y2) an integer:
  |b| >= 2 gives E <= 6, against (R-vi) (E >= 8); b = +-1 gives E = 9 (T18); b = 0 gives E = 10 (T20).
So, once T18 and T20 are accepted, no frame of U has this y1, whatever y2: neither the enumeration of the y2 nor the swap rule
is used. The statement is invariant under Aut(U), so it covers the whole orbit of y1, hence the chunk of the plan that holds
this representative.

What is checked here, all in exact rational arithmetic (the package is used ONLY to get the producer's basis B, which the plan's
coordinates refer to, and a list of candidate roots):
  1. the plan: basis_sha of the plan equals the sha of B (same formula as c1/code/y_pairs_gamma.py); sha256 of the plan file;
  2. the lattice: every row of B is an integer combination of the 24 generators of the lattice file, with a unimodular
     coefficient matrix (so B is a basis of U = Z-span of the generators); G = B B^T is integral with determinant +-1;
  3. for each requested representative i: c = y1_reps[i] (integers), y1 = c B, (y1,y1) = 7; among the candidate roots, the
     first r = d B (d integers) with (r,r) = 2 and |(r,y1)| = 2, all three products computed from the ambient rational vectors.
Output: per representative, c, y1 (ambient), d, r (ambient), the three products; the representatives without such a root are
listed apart (they are not covered by the lemma). The basis B is stored, so that a checker needs no package code:
q/check_cert_y1.py (lattice file + plan + this output only)."""
import sys, os, json, hashlib, time
from fractions import Fraction as F


def inverse(M):
    """inverse of a square matrix of Fractions (Gauss-Jordan), and its determinant"""
    n = len(M); A = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(M)]; det = F(1)
    for k in range(n):
        p = next(i for i in range(k, n) if A[i][k] != 0)
        if p != k: A[k], A[p] = A[p], A[k]; det = -det
        det *= A[k][k]; piv = A[k][k]; A[k] = [x / piv for x in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]; A[i] = [x - f * y for x, y in zip(A[i], A[k])]
    return [r[n:] for r in A], det


def dot(u, v): return sum(a * b for a, b in zip(u, v))
def comb(c, B): return [sum(c[i] * B[i][j] for i in range(len(B))) for j in range(len(B[0]))]


def main():
    pkg, lid, planf, outf = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), sys.argv[3], sys.argv[4]
    t0 = time.time(); sys.path.insert(0, os.path.join(pkg, "c1", "code"))
    import numpy as np
    import y_pairs as YP
    uf = os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)
    rec = json.load(open(uf)); plan = json.load(open(planf)); assert "%03d" % plan["id"] == lid == "%03d" % rec["id"]
    B, Gi, Bf, R, X3, Snew = YP.setup(rec["gens"])
    Bs = [[str(x) for x in row] for row in B]
    bsha = hashlib.sha256(json.dumps(Bs).encode()).hexdigest()[:16]
    assert bsha == plan["basis_sha"], "plan made in another basis (%s / %s)" % (plan["basis_sha"], bsha)
    Bq = [[F(s) for s in row] for row in Bs]; gens = [[F(str(x)) for x in g] for g in rec["gens"]]
    assert len(gens) == 24 and len(Bq) == 24
    ginv, gdet = inverse(gens); assert gdet != 0
    T = [comb(row, ginv) for row in Bq]                                   # B = T gens
    assert all(x.denominator == 1 for row in T for x in row), "a basis vector is not in the span of the generators"
    _, tdet = inverse(T); assert abs(tdet) == 1, "B is not a basis of U"
    G = [[dot(u, v) for v in Bq] for u in Bq]
    assert all(x.denominator == 1 for row in G for x in row); _, det = inverse(G); assert abs(det) == 1
    Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in Bq]))
    cand = []                                                            # candidate roots: integer coordinates, exact norm 2
    for d in np.rint(np.asarray(R, dtype=float) @ Binv).astype(np.int64):
        d = [int(x) for x in d]; r = comb(d, Bq)
        if dot(r, r) == 2: cand.append((d, r))
    reps = plan["y1_reps"]
    if "--all" in sys.argv: want = list(range(len(reps)))
    else: want = [int(x) for x in sys.argv[sys.argv.index("--reps") + 1].split(",")]
    out = {}; without = []
    for i in want:
        c = [int(x) for x in reps[i]]; y1 = comb(c, Bq); assert dot(y1, y1) == 7, "representative %d is not of norm 7" % i
        w = next(((d, r) for d, r in cand if abs(dot(r, y1)) == 2), None)
        if w is None: without.append(i); continue
        d, r = w
        out[str(i)] = {"chunk": [i, len(reps)], "y1_coordinates": c, "y1": [str(x) for x in y1], "r_coordinates": d, "r": [str(x) for x in r],
                       "(y1,y1)": int(dot(y1, y1)), "(r,r)": int(dot(r, r)), "(r,y1)": int(dot(r, y1))}
    res = {"what": "fixed-y1 certificate (q/cert_y1.py): for each listed y1 representative of the plan, a root r of U with (r,y1) = +-2. "
                   "With T18 and T20 no frame of U has such a y1, whatever y2. No exclusion is pronounced here.",
           "id": int(lid), "roots": rec.get("roots"), "plan_sha256": hashlib.sha256(open(planf, "rb").read()).hexdigest(),
           "plan_basis_sha": plan["basis_sha"], "plan_gamma_sha": plan.get("gamma_sha"), "y1_reps_in_plan": len(reps),
           "lattice_file_sha256": hashlib.sha256(open(uf, "rb").read()).hexdigest(), "basis": Bs,
           "lattice_checks": {"basis_in_span_of_generators": True, "change_of_basis_det": int(tdet), "gram_integral": True, "gram_det": int(det)},
           "candidate_roots": len(cand), "requested": want, "covered": sorted(int(k) for k in out), "not_covered": without, "reps": out,
           "pending": ["T18", "T20"], "cert_y1_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
           "seconds": round(time.time() - t0, 1), "t": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    json.dump(res, open(outf, "w"), indent=0)
    print(json.dumps({k: res[k] for k in ("id", "plan_basis_sha", "y1_reps_in_plan", "candidate_roots", "covered", "not_covered", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
