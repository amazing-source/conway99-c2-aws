"""Lattice 143 (root system a_15 a_8): the exact facts used by lemma/upstream/LATTICE_143.md (C2 lab, 2026-10-07).

  python budget_143.py <package dir> [<out.json>]

The package is used ONLY for a basis of U and for the lists of its vectors of norm 2 and 3 (scripts/frame_dfs_next.lattice_data).
The lists are complete: their sizes are the theta-series values 312 and 4096 (asserted). Everything else is exact integer or
rational arithmetic done here:
  1. the roots split into two classes under non-orthogonality, with 72 and 240 roots, of ranks 8 and 15 (exact elimination);
     so W = span of the first class has dimension 8, and for every x: |P_W x|^2 = S_8(x) / 18, S_8(x) = sum of (alpha,x)^2 over the
     72 roots (an irreducible root system with n h roots of norm 2 and rank n has sum of alpha alpha^T = 2 h P; here h = 72 / 8);
  2. the vectors of U orthogonal to all roots are the multiples of one primitive z (exact null space), and (z,z) = 144; so the
     orthogonal complement l of the root span is the line R z and |P_l x|^2 = (x,z)^2 / 144;
  3. the table of ((x,z)^2, S_8(x)) over the 4096 vectors of norm 3:  (81, 0): 1120,  (169, 16): 288,  (9, 36): 2688  (asserted).
Then the argument of LATTICE_143.md is the two lines printed at the end. No solver, no floating-point decision."""
import sys, os, json, collections, math
from fractions import Fraction as F
import numpy as np


def echelon(M):
    """reduced row echelon form of an integer matrix over Q: (rows, pivot columns)"""
    A = [[F(int(x)) for x in r] for r in M]; piv = []; r = 0; nc = len(A[0])
    for c in range(nc):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]; q = A[r][c]; A[r] = [x / q for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv.append(c); r += 1
    return A[:r], piv


def main():
    pkg = os.path.abspath(sys.argv[1]); sys.path.insert(0, os.path.join(pkg, "scripts"))
    import frame_dfs_next as FD
    rec = json.load(open(os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", "143.json")))
    L = FD.lattice_data(rec["gens"], F(1)); G = np.asarray(L["G"], dtype=np.int64)
    R = np.asarray(L["R"], dtype=np.int64).reshape(-1, 24); X3 = np.asarray(L["X3"], dtype=np.int64).reshape(-1, 24)   # one vector per pair +-
    assert (G == G.T).all() and (np.einsum("ij,jk,ik->i", R, G, R) == 2).all() and (np.einsum("ij,jk,ik->i", X3, G, X3) == 3).all()
    assert len({tuple(x) for x in R} | {tuple(-x) for x in R}) == 312 and len({tuple(x) for x in X3} | {tuple(-x) for x in X3}) == 4096
    P = R @ G @ R.T; comp = -np.ones(len(R), dtype=int); k = 0
    for s in range(len(R)):
        if comp[s] >= 0: continue
        st = [s]; comp[s] = k
        while st:
            a = st.pop()
            for b in np.flatnonzero(P[a] != 0):
                if comp[b] < 0: comp[b] = k; st.append(b)
        k += 1
    assert k == 2
    sizes = [2 * int((comp == i).sum()) for i in range(2)]; ranks = [len(echelon(R[comp == i])[1]) for i in range(2)]
    i8 = sizes.index(72); assert sorted(zip(sizes, ranks)) == [(72, 8), (240, 15)]
    # z: integer coordinates c with (c, alpha) = 0 for every root, i.e. (R G) c = 0
    E, piv = echelon(R @ G); assert len(piv) == 23
    free = [c for c in range(24) if c not in piv]; assert len(free) == 1
    z = [F(0)] * 24; z[free[0]] = F(1)
    for row, c in zip(E, piv): z[c] = -row[free[0]]
    den = 1
    for x in z: den = den * x.denominator // math.gcd(den, x.denominator)
    z = [int(x * den) for x in z]; g = 0
    for x in z: g = math.gcd(g, abs(x))
    z = np.array([x // g for x in z], dtype=np.int64)
    assert not (R @ G @ z).any(); zz = int(z @ G @ z); assert zz == 144
    t = X3 @ G @ z; s8 = 2 * ((X3 @ G @ R[comp == i8].T) ** 2).sum(axis=1)
    table = collections.Counter((int(a) ** 2, int(b)) for a, b in zip(t, s8))
    table = {k_: 2 * v for k_, v in table.items()}                                   # both signs
    assert table == {(81, 0): 1120, (169, 16): 288, (9, 36): 2688}, table
    # the same projections from the other side, as a check: |x|^2 = S_8/18 + S_15/32 + (x,z)^2/144
    s15 = 2 * ((X3 @ G @ R[comp == 1 - i8].T) ** 2).sum(axis=1)
    assert all(F(int(a), 18) + F(int(b), 32) + F(int(c) ** 2, 144) == 3 for a, b, c in zip(s8, s15, t))
    out = {"id": 143, "roots": 312, "components": {"roots": sizes, "ranks": ranks}, "(z,z)": zz, "norm3_vectors": 4096,
           "table ((x,z)^2, S_8(x)) -> vectors": {"%d,%d" % k_: v for k_, v in sorted(table.items())},
           "types (|P_W x|^2, |P_l x|^2)": {"%s,%s" % (F(b, 18), F(a, 144)): v for (a, b), v in sorted(table.items())}}
    print(json.dumps(out))
    print("budget on W (dimension 8): 56; a u with (x,z)^2 = 9 has |P_W u|^2 = 2, so at most 28 of the 42 u are of that kind")
    print("the other u, at least 14, have |P_l u|^2 >= 81/144: total >= 14 * 81/144 = %s > 7 = budget on l (dimension 1): no frame" % F(14 * 81, 144))
    if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
