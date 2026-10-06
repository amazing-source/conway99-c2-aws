# T20, enumerator 1 of the S-structures (definition: t20_common.py).
# Backtracking over the 45 orbit pairs in lexicographic order (numba kernel t20_kernel.py): incremental check of (L)
# on the 21 vertices of S u {p}, degree pruning for (E).  Every structure found is re-checked in pure Python.
# Symmetry breaking is declared per case; the number of labelled structures is checked against
# sum over classes of |G| / |Aut|  (orbit-stabiliser), G = group of the relabellings respecting the case.
import sys, json, time
from math import factorial
import numpy as np
from t20_common import *
from t20_kernel import search

CASES = {
    # name: (H, plus_edges, fixed, |G|, description)
    "I":    ((), [], {(0, j): (1 if j <= 4 else 0) for j in range(1, N)}, None,
             "k=0, e=0; row 0 of B fixed to {1,2,3,4} (labelled count must be sum 10!/(126 |Aut|))"),
    "IIa":  ((0, 1), [(2, 3)], None, 2 * 2 * factorial(6),
             "k=2 (inner orbits 0,1), e=1, plus edge between the word orbits 2,3"),
    "IIb":  ((0, 1), [(0, 2)], None, factorial(7),
             "k=2 (inner orbits 0,1), e=1, plus edge between inner orbit 0 and word orbit 2"),
    "III":  ((0, 1, 2, 3), [], None, factorial(4) * factorial(6),
             "k=4 (inner orbits 0..3), e=0"),
    # combinations excluded by the parity law (hand proof), listed for information only
    "X_k0e1": ((), [(0, 1)], None, 2 * factorial(8), "k=0, e=1 (excluded by the parity law)"),
    "X_k2e0": ((0, 1), [], None, 2 * factorial(8), "k=2, e=0 (excluded by the parity law)"),
    "X_k4e1ww": ((0, 1, 2, 3), [(4, 5)], None, factorial(4) * 2 * factorial(4), "k=4, e=1 word-word (parity)"),
    "X_k4e1wh": ((0, 1, 2, 3), [(0, 4)], None, factorial(3) * factorial(5), "k=4, e=1 word-inner (parity)"),
}


def enumerate_structs(H, plus_edges, fixed=None, maxout=2000000, maxnodes=4 * 10 ** 9):
    hs = set(H)
    fixed = fixed or {}
    plus_set = set(plus_edges)
    pdeg = [0] * N
    for (i, j) in plus_set:
        pdeg[i] += 1; pdeg[j] += 1
    target = np.array([pdeg[i] + 4 - (1 if i in hs else 0) for i in range(N)], np.int64)
    adj0 = np.array(graph_of({}, H), np.int64)
    pi = np.array([p[0] for p in PAIRS], np.int64)
    pj = np.array([p[1] for p in PAIRS], np.int64)
    opt = np.zeros((45, 2), np.int64)
    nopt = np.zeros(45, np.int64)
    for k, pr in enumerate(PAIRS):
        if pr in fixed:
            o = [fixed[pr]]
        elif pr in plus_set:
            o = [2, 3]
        else:
            o = [0, 1]
        nopt[k] = len(o)
        for t, s in enumerate(o):
            opt[k, t] = s
    out = np.zeros((maxout, 45), np.int8)
    nout, nodes, complete = search(pi, pj, opt, nopt, target, adj0, out, maxnodes)
    return out[:min(nout, maxout)], nout, nodes, complete


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or ["III", "IIb", "IIa", "I"]
    maxnodes = 4 * 10 ** 9
    for a in sys.argv[1:]:
        if a.startswith("--maxnodes="):
            maxnodes = int(a.split("=")[1])
    res = {}
    for name in names:
        H, plus_edges, fixed, G, desc = CASES[name]
        t0 = time.time()
        arr, nout, nodes, complete = enumerate_structs(H, plus_edges, fixed, maxnodes=maxnodes)
        print("case %s: %s" % (name, desc))
        print("  labelled structures found: %d   (search nodes %d, complete %s, %.1f s)" % (nout, nodes, complete, time.time() - t0))
        if not complete or nout > len(arr):
            print("  INCOMPLETE - no conclusion"); sys.stdout.flush(); continue
        structs = []
        for row in arr:
            st = {PAIRS[k]: int(row[k]) for k in range(45) if row[k]}
            assert eigen_ok(st, H) and local_ok(graph_of(st, H))
            structs.append(st)
        cl = classes(structs, H)
        print("  isomorphism classes: %d   (%.1f s)" % (len(cl), time.time() - t0))
        recs = []
        for idx, (m, cnt) in enumerate(cl):
            a = aut_order(m, H)
            if name == "I":
                expect = factorial(10) // (126 * a) if factorial(10) % (126 * a) == 0 else None
            else:
                expect = G // a if G % a == 0 else None
            st = {(i, j): m[i][j] for (i, j) in PAIRS if m[i][j]}
            adj = graph_of(st, H)
            rep = psd_report(adj, list(range(NV)))
            status = "PSD-ok" if rep["M1"][0] == "psd" and rep["M2"][0] == "psd" else "PSD-REJECTED"
            print("  class %d: labelled %d, |Aut| %d, expected labelled %s, %s" % (idx, cnt, a, expect, status))
            print("     minus edges: %s" % edges_str(m, 1))
            if any(m[i][j] & 2 for (i, j) in PAIRS):
                print("     plus edges : %s" % edges_str(m, 2))
            for nm in ("M1", "M2"):
                r = rep[nm]
                if r[0] == "psd":
                    print("     %s: PSD exactly, rank %d of 21" % (nm, r[1]))
                else:
                    print("     %s: NOT PSD, integer vector %s gives %d" % (nm, r[1], r[2]))
            if expect != cnt:
                print("     !!! orbit-stabiliser check FAILED")
            recs.append({"case": name, "H": list(H), "m": m, "labelled": cnt, "aut": a, "psd": status,
                         "M1": list(rep["M1"]), "M2": list(rep["M2"]), "check": expect == cnt})
        res[name] = recs
        sys.stdout.flush()
    fn = "structures_%s.json" % "_".join(names)
    json.dump(res, open(fn, "w"))
    print("written", fn)


if __name__ == "__main__":
    main()
