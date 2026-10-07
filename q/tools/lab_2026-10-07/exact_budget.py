"""Exact (integer) re-check of the component-budget test (component_budget.py) with type tables. Usage: python exact_budget.py <id>..."""
import sys, os, json, numpy as np
from fractions import Fraction as F
from math import lcm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frame_dfs as FD
from component_budget import components
LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def comps(n, parts):
    if parts == 1: yield (n,); return
    for a in range(n + 1):
        for rest in comps(n - a, parts - 1): yield (a,) + rest


for lid in ["%03d" % int(x) for x in sys.argv[1:]]:
    rec = json.load(open(os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))
    B, G = FD.setup_lattice(rec["gens"])
    X = FD.one_per_pair(FD.short(G, 4) // 2); nrm = np.einsum("ij,jk,ik->i", X, G, X); R = X[nrm == 2]
    comp, k = components(R, G); c = FD.solve_mod2(G, np.diag(G)); S2 = FD.short(G, 2, c)
    ranks = [int(np.linalg.matrix_rank(R[comp == i].astype(float))) for i in range(k)]
    hs = [F(2 * int((comp == i).sum()), ranks[i]) for i in range(k)]
    def types(Xn, norm):
        T = {}
        for row in Xn @ G @ R.T:
            t = tuple(F(int((row[comp == i] ** 2).sum()) * 2) / (2 * hs[i]) for i in range(k))
            t = t + (F(norm) - sum(t),)
            T[t] = T.get(t, 0) + 1
        return T
    H4 = X[nrm == 4]; H4 = H4[np.abs(H4 @ G @ S2.T).max(axis=1) <= 2]
    Tu, Th = types(X[nrm == 3], 3), types(H4, 4)
    bud = [F(7 * r) for r in ranks] + [F(7 * (24 - sum(ranks)))]
    print("== %s %s ranks %s budgets %s" % (lid, rec.get("roots"), ranks, [str(b) for b in bud]), flush=True)
    for t, n in Tu.items(): print("   u", [str(v) for v in t], n)
    for t, n in Th.items(): print("   h", [str(v) for v in t], n)
    D = lcm(*[x.denominator for t in list(Tu) + list(Th) for x in t])
    TU = np.array([[int(x * D) for x in t] for t in Tu]); TH = np.array([[int(x * D) for x in t] for t in Th])
    bd = np.array([int(b * D) for b in bud])
    US = np.array([np.array(ns) @ TU for ns in comps(42, len(TU))])
    HSs = np.unique(np.array([np.array(ms) @ TH for ms in comps(7, len(TH))]), axis=0)
    ok = False
    for a in range(0, len(US), 500):
        if ((bd[None, None, :] - US[a:a + 500, None, :] - HSs[None, :, :]) >= 0).all(axis=2).any(): ok = True; break
    print("   EXACT (%d u-sums x %d h-sums): %s" % (len(US), len(HSs), "feasible" if ok else "INFEASIBLE"), flush=True)
