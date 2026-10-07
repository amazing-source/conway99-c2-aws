"""Checker of a fixed-y1 certificate (C2 lab, 2026-10-07). Standard library only, no package code, exact rationals.

  python check_cert_y1.py <lattice file U/<lid>.json> <plan.json> <certificate json>

Reads the 24 generators of U (lattice file), the plan (integer coordinates of the y1 representatives, basis_sha) and the
certificate of q/cert_y1.py. For each representative i of the certificate:
  0. the indices are distinct, in [0, number of representatives of the plan), and equal to the certificate's list `covered`;
  a. the certificate's basis has the plan's basis_sha (sha256 of the json of its strings, first 16 hex digits), and
     y1 = y1_reps[i] . basis, exactly: the vector is the one the producer's chunk i refers to;
  b. y1 and r are integer combinations of the 24 generators (exact solve): both are in U;
  c. (y1,y1) = 7, (r,r) = 2, (r,y1) = +-2, from the ambient rational vectors.
Then E(r) = 7*2 - 4 - (r,y2)^2 = 10 - (r,y2)^2 for every y2 of U: the fixed-y1 lemma applies (pending T18 and T20).
Prints one line per representative and "ok" only if all hold; exit 0 = ok."""
import sys, json, hashlib
from fractions import Fraction as F


def solve_left(v, M):
    """x with x M = v, for M square invertible (Fractions): Gauss on the transposed system"""
    n = len(M); A = [[M[j][i] for j in range(n)] + [v[i]] for i in range(n)]
    for k in range(n):
        p = next(i for i in range(k, n) if A[i][k] != 0); A[k], A[p] = A[p], A[k]
        piv = A[k][k]; A[k] = [x / piv for x in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]; A[i] = [x - f * y for x, y in zip(A[i], A[k])]
    return [A[i][n] for i in range(n)]


def main():
    rec = json.load(open(sys.argv[1])); plan = json.load(open(sys.argv[2])); cert = json.load(open(sys.argv[3]))
    gens = [[F(str(x)) for x in g] for g in rec["gens"]]; assert len(gens) == 24
    ok = rec["id"] == plan["id"] == cert["id"]
    ok &= hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest() == cert["plan_sha256"]
    ok &= hashlib.sha256(json.dumps(cert["basis"]).encode()).hexdigest()[:16] == plan["basis_sha"] == cert["plan_basis_sha"]
    B = [[F(s) for s in row] for row in cert["basis"]]
    dot = lambda u, v: sum(a * b for a, b in zip(u, v))
    NR = len(plan["y1_reps"]); keys = sorted(int(k) for k in cert["reps"])
    ok &= all(str(i) in cert["reps"] and 0 <= i < NR for i in keys) and len(keys) == len(cert["reps"]) and keys == cert.get("covered")
    print("header (ids, plan sha256, basis sha, indices in range and equal to the list `covered`): %s" % ("ok" if ok else "FAIL"))
    for key, e in sorted(cert["reps"].items(), key=lambda t: int(t[0])):
        i = int(key)
        if not (0 <= i < NR): print("representative %s: index out of range: FAIL" % key); ok = False; continue
        y1 = [F(s) for s in e["y1"]]; r = [F(s) for s in e["r"]]; c = plan["y1_reps"][i]
        a = e["chunk"] == [i, len(plan["y1_reps"])] and [int(x) for x in c] == e["y1_coordinates"] and \
            [sum(int(c[k]) * B[k][j] for k in range(24)) for j in range(24)] == y1
        b = all(x.denominator == 1 for x in solve_left(y1, gens)) and all(x.denominator == 1 for x in solve_left(r, gens))
        n = (dot(y1, y1), dot(r, r), dot(r, y1)); cc = n[0] == 7 and n[1] == 2 and abs(n[2]) == 2
        ok &= bool(a and b and cc)
        print("representative %d: plan vector %s, in U %s, (y1,y1) = %s, (r,r) = %s, (r,y1) = %s: %s" % (i, a, b, n[0], n[1], n[2], "ok" if a and b and cc else "FAIL"))
    print("ok" if ok else "FAIL"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
