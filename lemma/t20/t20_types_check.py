# T20: independent re-count of the outside types of B4 that pass the graph rule (L)  (no shared code with
# t20_survivors.py / t20_common.py; Python sets; no sigma quotient, no PSD).
# Reads only the edge data of the nine survivors from the json files.
# For d in (4, 3): number of ORDERED pairs (Np, Nm) of d-subsets of the 10 orbits such that the graph on
# S u {p, z, sigma z} with N(z) = {x_i : i in Np} u {y_j : j in Nm} (+ sigma z, p if z is inner) and the mirrored
# neighbourhood for sigma z satisfies: adjacent pairs <= 1 common neighbour, non-adjacent pairs <= 2.
# classes under sigma = (ordered + symmetric) / 2, symmetric = number of types with Np = Nm.
import json, sys, time
from itertools import combinations

ref = {}
for fn in ("structures_III_IIb_IIa.json", "structures_I.json"):
    ref.update(json.load(open(fn)))
T0 = time.time()
for d in (4, 3):
    for case in ("I", "IIa", "III"):
        for idx, rec in enumerate(ref[case]):
            m, H = rec["m"], rec["H"]
            nb = [set() for _ in range(23)]

            def add(u, v, nb=nb):
                nb[u].add(v); nb[v].add(u)
            for i in range(10):
                for j in range(i + 1, 10):
                    if m[i][j] & 1:
                        add(i, 10 + j); add(j, 10 + i)
                    if m[i][j] & 2:
                        add(i, j); add(10 + i, 10 + j)
            for i in H:
                add(i, 10 + i); add(20, i); add(20, 10 + i)
            base = [set(s) for s in nb]
            res = []
            for inner in (False, True):
                ordered = 0
                sym = 0
                for Np in combinations(range(10), d):
                    for Nm in combinations(range(10), d):
                        g = [set(s) for s in base]
                        for i in Np:
                            g[21].add(i); g[i].add(21); g[22].add(10 + i); g[10 + i].add(22)
                        for j in Nm:
                            g[21].add(10 + j); g[10 + j].add(21); g[22].add(j); g[j].add(22)
                        if inner:
                            g[21].add(22); g[22].add(21)
                            g[21].add(20); g[20].add(21); g[22].add(20); g[20].add(22)
                        ok = True
                        # only pairs involving z, sigma z or one of their neighbours can be violated newly; test all pairs anyway
                        for u in range(23):
                            gu = g[u]
                            for v in range(u + 1, 23):
                                c = len(gu & g[v])
                                if c > 2 or (c == 2 and v in gu):
                                    ok = False
                                    break
                            if not ok:
                                break
                        if ok:
                            ordered += 1
                            if Np == Nm:
                                sym += 1
                res.append((ordered, sym, (ordered + sym) // 2))
            print("d=%d %s.%d : z not in N(p): ordered %d, symmetric %d, classes %d | z in N(p): ordered %d, symmetric %d, classes %d   [%.0f s]" % (
                d, case, idx, res[0][0], res[0][1], res[0][2], res[1][0], res[1][1], res[1][2], time.time() - T0))
            sys.stdout.flush()
