"""Apply the two lemmas (integer parabola, cap) directly to every support of the register: explicit witnesses, no LP.
usage: lemmas_all.py k nproc out.jsonl"""
import sys, json, random, itertools
import numpy as np
import p3n25_ilp as I, parabola as PA
k, nproc, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
lines = open("register/supports_open_4581.jsonl", encoding="utf-8").read().splitlines()
rng = random.Random(100 + k)
def cap_violation(d):
    adj, r, dZ = I.boundary(d["edges"]); best = None
    for v in range(28):
        for u in range(28):
            if u == v: continue
            X = [x for x in range(28) if (adj[v] >> x) & 1 and x != u and r[u][x] > 0]
            lhs = sum(r[u][x] for x in X)
            if (adj[u] >> v) & 1: rhs = dZ[u] - r[u][v]
            else: rhs = 2 * (dZ[u] - r[u][v]) + min(r[u][v], sum(1 for x in X if r[v][x] == 1))
            if lhs > rhs and (best is None or lhs - rhs > best[0]): best = (lhs - rhs, u, v, X, lhs, rhs)
    return best
with open(out, "w") as fo:
    for pos in range(k, len(lines), nproc):
        d = json.loads(lines[pos])
        adj, R, dv = PA.data(d)
        val, w, a = PA.search(R, dv, rng, 2, restarts=40)
        assert PA.phi(w, a, R, dv) == val
        cv = cap_violation(d)
        rec = {"id": d["id"], "pos": pos, "delta": d["delta"], "parabola": None if val >= 0 else {"phi": val, "a": a, "w": w.tolist()},
               "cap": None if cv is None else {"excess": cv[0], "u": cv[1], "v": cv[2], "X": cv[3], "lhs": cv[4], "rhs": cv[5]}}
        fo.write(json.dumps(rec) + "\n"); fo.flush()
