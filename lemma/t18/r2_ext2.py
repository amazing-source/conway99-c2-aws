# Round 2, profile (3,3,1), last step tried: add the 6 vertices W = N(p) n X_1 to a surviving Y-table.
# By A10 (and the remark below) the graph on Y u W (45 + 6 = 51 vertices) is completely determined by
#   - the types (i_c ; j_c) of w_c, c = 1,2,3 (sigma w_c has type (j_c ; i_c)): every P_i must see exactly 2 vertices of N(p);
#   - the 2 neighbours of each w_c in X_2: a(w) = 2, they lie outside A_p, and every vertex s of X_2 outside A_p is adjacent
#     to exactly one vertex of W  (s and p have 2 common neighbours: z_0 or sigma z_0, and one more, which is in W);
#   - w_c ~ p, w_c ~ sigma w_c; no other neighbour of w_c in X_0 (c(w) = 1), none in A_p (N(p) is a matching).
# Tests: common-neighbour budgets and exact PSD (integer certificates) on every induced subgraph met.
# usage: python r2_ext2.py <structure> <json files of r2_stage2.py with "examples" = PSD-surviving Y-tables> ...
import json, os, sys, itertools, time
import numpy as np
from enum_S import neg_certificate
from latt import psd_exact

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si = int(sys.argv[1])
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
Bn = [set(j for j in range(9) if j != i and m[i][j] & 1) for i in range(9)]
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(d) for d in td["DEF"]]
AS1 = set()
for Np, Nm, flag in types[name]:
    if flag and len(Np) == 1:
        AS1.add((Np[0], Nm[0]))
pc = lambda x: bin(x).count("1")
STAT = {"tables": 0, "type_solutions": 0, "nodes": 0, "rej_budget": 0, "rej_certificate": 0, "rej_exact_only": 0, "survivors": 0}


def graph_ok(rows, L):
    mask = 0
    for v in L:
        mask |= 1 << v
    for a in range(len(L)):
        ru = rows[L[a]] & mask
        for b in range(a + 1, len(L)):
            c = pc(ru & rows[L[b]])
            if c > 2 or (c > 1 and (ru >> L[b]) & 1):
                STAT["rej_budget"] += 1
                return False
    n = len(L)
    A = np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)
    for Mx in (27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2):
        if np.linalg.eigvalsh(Mx.astype(float))[0] > -1e-7:
            continue
        if neg_certificate(Mx.tolist()) is not None:
            STAT["rej_certificate"] += 1
            return False
        if not psd_exact(Mx.tolist())[0]:
            STAT["rej_exact_only"] += 1
            return False
    return True


tables = []
for fn in sys.argv[2:]:
    d = json.load(open(os.path.join(here, fn)))
    tables += d["examples"]
    print(fn, ": PSD-surviving Y-tables reported", d["totals"]["Y_tables_psd"], ", saved", len(d["examples"]))
alive_tables = 0
for ex in tables:
    STAT["tables"] += 1
    tau, Az, H, G, F = ex["tau"], ex["Az"], ex["H"], ex["G"], ex["F"]
    U = [set(DEF[k]) for k in range(18)]
    V = [set(DEF[tau[k]]) for k in range(18)]
    rows = [0] * 51
    def add(u, v):
        rows[u] |= 1 << v; rows[v] |= 1 << u
    for i in range(9):
        for j in Bn[i]:
            add(i, 9 + j)
    for k in range(18):
        for i in U[k]:
            add(27 + k, i)
        for j in V[k]:
            add(27 + k, 9 + j)
        for l in range(18):
            if (H[k] >> l) & 1:
                add(27 + k, 27 + l)
    for q in range(9):
        for k in range(18):
            if (Az[q] >> k) & 1:
                add(18 + q, 27 + k)
        for r in range(9):
            if (G[q] >> r) & 1:
                add(18 + q, 18 + r)
    LY = list(range(45))
    assert graph_ok(rows, LY), "the table itself must pass"
    mem = [k for k in range(18) if (Az[0] >> k) & 1]
    outside = [k for k in range(18) if k not in mem]
    f = [sum(1 for k in mem if i in U[k]) for i in range(9)]
    defi = [2 - x for x in f]
    sols = []
    def x1(chosen):
        if all(d == 0 for d in defi):
            if len(chosen) == 3:
                sols.append(tuple(sorted(chosen)))
            return
        if len(chosen) >= 3:
            return
        i = next(q for q in range(9) if defi[q] > 0)
        for j in range(9):
            if j == i or defi[j] <= 0 or (i, j) not in AS1:
                continue
            ok = True
            for k in mem:
                if (i in U[k]) + (j in V[k]) > 1 or (j in U[k]) + (i in V[k]) > 1:
                    ok = False; break
            if ok:
                for (a2, b2) in chosen:
                    if (i == a2) + (j == b2) > 1 or (i == b2) + (j == a2) > 1:
                        ok = False; break
            if ok:
                defi[i] -= 1; defi[j] -= 1
                chosen.append((min(i, j), max(i, j)))
                x1(chosen)
                chosen.pop()
                defi[i] += 1; defi[j] += 1
    x1([])
    sols = sorted(set(sols))
    STAT["type_solutions"] += len(sols)
    table_alive = False
    for sol in sols:
        base = rows[:]
        def addb(rr, u, v):
            rr[u] |= 1 << v; rr[v] |= 1 << u
        for c, (i, j) in enumerate(sol):
            w, sw = 45 + 2 * c, 46 + 2 * c
            addb(base, w, 18); addb(base, sw, 18); addb(base, w, sw)
            addb(base, w, i); addb(base, w, 9 + j); addb(base, sw, j); addb(base, sw, 9 + i)
        def rec(c, rr, L, remaining):
            global alive_tables
            if c == 3:
                STAT["survivors"] += 1
                return True
            w, sw = 45 + 2 * c, 46 + 2 * c
            L2 = L + [w, sw]
            got = False
            for s1, s2 in itertools.combinations(sorted(remaining), 2):
                if s2 == tau[s1]:
                    continue
                STAT["nodes"] += 1
                r2 = rr[:]
                addb(r2, w, 27 + s1); addb(r2, w, 27 + s2); addb(r2, sw, 27 + tau[s1]); addb(r2, sw, 27 + tau[s2])
                if graph_ok(r2, L2):
                    if rec(c + 1, r2, L2, remaining - {s1, s2, tau[s1], tau[s2]}):
                        got = True
            return got
        if rec(0, base, LY, set(outside)):
            table_alive = True
    if table_alive:
        alive_tables += 1
    print(f"table F={F}: type solutions {len(sols)}, alive after adding W: {table_alive}", flush=True)
print("totals:", STAT, " tables still alive:", alive_tables)
