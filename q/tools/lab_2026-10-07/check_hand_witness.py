"""Exact checker of the witness certificates of y1_then_witness.py (C2 lab, 2026-10-07). No package code, no enumeration.

  python check_hand_witness.py <U/<lid>.json> <plan_<lid>.json> <cert_y1_<lid>.json> <<lid>.json> <<lid>_pairs.npz>

Checks, in Python integers and fractions (numpy only to read the arrays):
  1. the basis B of <lid>.json is a basis of U: its rows are integer combinations of the 24 generators with a coefficient matrix
     of determinant +-1; G = B B^T is integral; the pairs file has the sha256 recorded in <lid>.json;
  2. the y1 of the file are the representatives of the plan that the fixed-y1 certificate does NOT cover, in this order: each y1,
     written in the basis B, equals (as an ambient vector) the plan's representative written in the plan's basis (the basis stored
     in the fixed-y1 certificate, whose hash is the plan's basis_sha);
  3. for EVERY pair: (y1,y1) = (y2,y2) = 7 and (y1,y2) = 0; and either it is marked survivor (e >= 11, no witness claimed), or its
     witness w has integer coordinates, norm wn in {2, 3, 4} equal to w G w^T, and E = 7 wn - (w,y1)^2 - (w,y2)^2 satisfies
     0 < E <= 10 and equals the recorded value.
  4. the counts by value of E and the number of survivors are those of <lid>.json.
A valid witness excludes its pair by (R-vi) (E < 8), T16 (8), T18 (9) or T20 (10), whatever the completeness of any list. What this
checker does NOT establish: that the file lists all the pairs of those y1 (that is the producer), and that a survivor has no
short witness (that needs the complete lists of norm 2, 3, 4). Exit 0 = all checks pass."""
import sys, json, hashlib, collections
from fractions import Fraction as F
import numpy as np


def inv_det(M):
    n = len(M); A = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(M)]; det = F(1)
    for k in range(n):
        p = next(i for i in range(k, n) if A[i][k] != 0)
        if p != k: A[k], A[p] = A[p], A[k]; det = -det
        det *= A[k][k]; q = A[k][k]; A[k] = [x / q for x in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]; A[i] = [x - f * y for x, y in zip(A[i], A[k])]
    return [r[n:] for r in A], det


def main():
    rec = json.load(open(sys.argv[1])); plan = json.load(open(sys.argv[2])); cy = json.load(open(sys.argv[3])); res = json.load(open(sys.argv[4])); npz = sys.argv[5]
    ok = rec["id"] == plan["id"] == cy["id"] == res["id"]
    ok &= hashlib.sha256(open(npz, "rb").read()).hexdigest() == res["pairs_file_sha256"]
    gens = [[F(str(x)) for x in g] for g in rec["gens"]]; B = [[F(s) for s in row] for row in res["basis"]]
    assert len(gens) == len(B) == 24 and all(len(r) == 24 for M in (gens, B) for r in M), "bases must be 24 by 24"
    ginv, _ = inv_det(gens); T = [[sum(row[k] * ginv[k][j] for k in range(24)) for j in range(24)] for row in B]; _, td = inv_det(T)
    ok &= all(x.denominator == 1 for r in T for x in r) and abs(td) == 1
    G = [[sum(a * b for a, b in zip(u, v)) for v in B] for u in B]; ok &= all(x.denominator == 1 for r in G for x in r); G = [[int(x) for x in r] for r in G]
    Z = np.load(npz, allow_pickle=False)
    # Coordinate integrality is essential: rational reflections preserve norms
    # and E but need not preserve U. Do not silently truncate arrays with int().
    assert set(Z.files) == {"left", "y1_o", "y1", "o", "y2", "w", "wn", "e"}, "unexpected certificate arrays"
    assert all(Z[k].dtype.kind in "iu" for k in Z.files), "all certificate arrays must have integer dtype"
    assert all(Z[k].ndim == 1 for k in ("left", "y1_o", "o", "wn", "e")), "index/value arrays must be one-dimensional"
    assert Z["y1"].shape == (len(Z["y1_o"]), 24), "bad y1 array shape"
    assert Z["y2"].shape == Z["w"].shape == (len(Z["o"]), 24), "bad pair/witness array shape"
    assert len(Z["wn"]) == len(Z["e"]) == len(Z["o"]), "pair array lengths differ"
    left = [int(x) for x in Z["left"]]; y1o = [int(x) for x in Z["y1_o"]]; Y1 = [[int(x) for x in r] for r in Z["y1"]]
    assert len(set(left)) == len(left) and all(0 <= i < len(plan["y1_reps"]) for i in left), "bad plan indices"
    assert len(set(y1o)) == len(y1o) and set(Z["o"].tolist()) <= set(y1o), "bad y1 references"
    ok &= left == [int(i) for i in cy["not_covered"]] == res["y1_left_indices"] and hashlib.sha256(json.dumps(cy["basis"]).encode()).hexdigest()[:16] == plan["basis_sha"]
    PB = [[F(s) for s in row] for row in cy["basis"]]
    assert len(PB) == 24 and all(len(r) == 24 for r in PB), "bad plan basis shape"
    assert all(len(r) == 24 and all(type(x) is int for x in r) for r in plan["y1_reps"]), "plan coordinates must be integers"
    amb = lambda c, M: [sum(int(c[i]) * M[i][j] for i in range(24)) for j in range(24)]
    for o, c in zip(y1o, Y1): ok &= 0 <= o < len(left) and amb(c, B) == amb(plan["y1_reps"][left[o]], PB)
    y1 = dict(zip(y1o, Y1)); Gy1 = {o: [sum(G[i][j] * c[j] for j in range(24)) for i in range(24)] for o, c in y1.items()}
    ok &= all(sum(a * b for a, b in zip(y1[o], Gy1[o])) == 7 for o in y1)
    O = Z["o"].tolist(); Y2 = Z["y2"].tolist(); W = Z["w"].tolist(); WN = Z["wn"].tolist(); E = Z["e"].tolist(); by = collections.Counter(); bad = 0
    ok &= len(O) == res["pairs"] == len(Y2) == len(W) == len(WN) == len(E)
    for o, c2, w, wn, e in zip(O, Y2, W, WN, E):
        g2 = [sum(G[i][j] * c2[j] for j in range(24)) for i in range(24)]
        good = sum(a * b for a, b in zip(c2, g2)) == 7 and sum(a * b for a, b in zip(c2, Gy1[o])) == 0
        if e >= 11: by[">=11"] += 1; good &= wn == 0
        else:
            n = sum(w[i] * G[i][j] * w[j] for i in range(24) for j in range(24)); a = sum(x * y for x, y in zip(w, Gy1[o])); b = sum(x * y for x, y in zip(w, g2))
            good &= n == wn and wn in (2, 3, 4) and 7 * n - a * a - b * b == e and 0 < e <= 10; by[str(e)] += 1
        bad += not good
    ok &= bad == 0 and dict(by) == res["by_min_E"] and by.get(">=11", 0) == res["survivors"]
    print("lattice %03d: y1 %d, pairs %d, with a valid witness %d, survivors %d, invalid %d: %s" % (res["id"], len(y1), len(O), len(O) - by.get(">=11", 0), by.get(">=11", 0), bad, "ok" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
