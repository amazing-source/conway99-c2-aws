"""which rules make a positive star-less?  the star model with each group of rules switched off in turn.   usage: star_why.py"""
import sys, json, time, itertools, collections
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I
def model(d, p, off=()):
    A = np.zeros((28, 28), dtype=np.int64)
    for x, y in d["edges"]: A[x, y] = A[y, x] = 1
    C = A @ A; r = np.where(A == 1, 1, 2) - C; np.fill_diagonal(r, 0)
    Np = [x for x in range(3, 28) if A[p, x]]; U = [x for x in Np if not any(A[x, y] for y in Np)]; u = len(U)
    partner = {}
    for i in range(u, 6, 2): partner[i] = i + 1; partner[i + 1] = i
    others = [s for s in range(28) if s != p]; m = cp_model.CpModel(); a = {}
    for z in range(6):
        for s in others:
            a[z, s] = m.NewBoolVar("")
            if r[p, s] == 0: m.Add(a[z, s] == 0)
    for i, x in enumerate(U):
        for z in range(6): m.Add(a[z, x] == (1 if z == i else 0))
    for z in range(6):
        m.Add(sum(a[z, s] for s in others if s >= 3) - sum(a[z, s] for s in others if s < 3) == 5)
        if "r" not in off:
            for s, t in itertools.combinations(others, 2):
                if r[s, t] <= 0: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
        for s in others:
            ns = sum(a[z, t] for t in others if A[s, t]) + int(A[s, p]); pz = partner.get(z)
            pt = (a[pz, s] if (pz is not None and "partner" not in off) else 0)
            if "in" not in off: m.Add(ns <= 1).OnlyEnforceIf(a[z, s])
            if "out" not in off: m.Add(ns + pt <= 2).OnlyEnforceIf(a[z, s].Not())
    for s in others: m.Add(sum(a[z, s] for z in range(6)) == int(r[p, s]))
    if "share" not in off:
        for z, z2 in itertools.combinations(range(6), 2):
            prods = []
            for s in others:
                if r[p, s] >= 2:
                    b = m.NewBoolVar(""); m.AddMultiplicationEquality(b, [a[z, s], a[z2, s]]); prods.append(b)
            m.Add(sum(prods) <= (0 if partner.get(z) == z2 else 1))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 60; sv.parameters.num_workers = 4
    return sv.StatusName(sv.Solve(m)), u, r, A, Np, U
if __name__ == "__main__":
    rs = {json.loads(l)["id"]: json.loads(l) for l in open("star_all.jsonl")}
    ids = json.load(open("star_extra_ids.json")); tab = collections.Counter(); n = 0
    for sid in ids:
        x = next(q for q in rs[sid]["pos"] if q["status"] == "no star")
        if x["cuts"]: continue
        d = I.load("register/supports_open_4581.jsonl", sid); p = x["p"]; n += 1
        res = {g: model(d, p, (g,))[0] for g in ("r", "in", "out", "partner", "share")}
        key = tuple(g for g in res if res[g] != "INFEASIBLE"); tab[key] += 1
        if n <= 6:
            st, u, r, A, Np, U = model(d, p)
            others = [q for q in range(3) if q != p]
            print(f"support {sid} p={p}: u={u}, r(p,q)={[int(r[p, q]) for q in others]}, rho histogram {sorted(collections.Counter(int(r[p, s]) for s in range(3, 28) if not A[p, s]).items())}; relaxations that give a star: {key}")
    print(n, "star-less positives without cut; needed rule groups (relaxing any ONE of these gives a star):")
    for k, v in sorted(tab.items(), key=lambda kv: -kv[1]): print("   ", v, k)
