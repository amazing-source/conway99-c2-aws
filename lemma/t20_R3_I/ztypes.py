# T20 round 3, case I, n_3 = 2: the possible types (U3 ; V3) of the word z of X_3, up to Aut(B) and the exchange
# z <-> sigma z.  Test: exact budget count on the 23 vertices S u {p, z, sigma z} (z, sigma z not adjacent to p
# nor to each other).  Also prints, for information, rho = number of B-edges between U3 and V3 and |U3 n V3|.
import itertools, json
import numpy as np
import r3lib
res = {}
for name in r3lib.GRAPHS:
    m = r3lib.load_B(name)
    A21 = r3lib.support(m)
    G = r3lib.aut_group(m)
    triples = list(itertools.combinations(range(10), 3))
    ok = []
    for U in triples:
        for V in triples:
            if U == V:
                continue
            A = np.zeros((23, 23), dtype=np.int64)
            A[:21, :21] = A21
            for i in U:
                A[21, i] = A[i, 21] = 1; A[22, 10 + i] = A[10 + i, 22] = 1
            for i in V:
                A[21, 10 + i] = A[10 + i, 21] = 1; A[22, i] = A[i, 22] = 1
            if not r3lib.budget_viol(A):
                ok.append((U, V))
    okset = set(ok)
    seen = set(); reps = []
    for t in sorted(okset):
        if t in seen:
            continue
        orb = set()
        for g in G:
            gu = tuple(sorted(g[i] for i in t[0])); gv = tuple(sorted(g[i] for i in t[1]))
            orb.add((gu, gv)); orb.add((gv, gu))
        assert orb <= okset
        seen |= orb
        r = min(orb)
        rho = sum(m[i][l] for i in r[0] for l in r[1])
        reps.append({"U": r[0], "V": r[1], "orbit": len(orb), "rho": rho, "cap": len(set(r[0]) & set(r[1]))})
    print("%s: |Aut| = %d; ordered types (U3;V3) passing the budgets on 23 vertices: %d (= %d classes under sigma); classes under Aut(B) x <sigma>: %d" % (
        name, len(G), len(ok), len(ok) // 2, len(reps)))
    for r in reps:
        print("    z = %s ; %s   orbit %d  rho %d  |U3 n V3| %d" % (r["U"], r["V"], r["orbit"], r["rho"], r["cap"]))
    res[name] = reps
json.dump(res, open("ztypes.json", "w"))
