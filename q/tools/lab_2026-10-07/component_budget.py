"""Envelope-level component-budget test (C2, 28/09 night). Sound necessary condition, no y-pairs.
For each irreducible root component R_i of U (simply laced, Coxeter number h_i): sum_{alpha in R_i} (alpha, x)^2 = 2 h_i |P_i x|^2.
The frame identity at every root (sum_f (alpha, f)^2 = 14) summed over R_i gives, for the 51 frame vectors,
      sum_f |P_i f|^2 = 7 rank(R_i),      and on the orthogonal complement of the root span: sum_f |P_perp f|^2 = 7 (24 - rank R).
Each frame vector f (42 of norm 3, 7 of norm 4, 2 of norm 7) has a norm-distribution TYPE t(f) = (|P_1 f|^2, ..., |P_k f|^2, |P_perp f|^2),
read off the actual vectors of U. Test: is there a nonnegative integer choice of 42 norm-3 types, 7 norm-4 types, 2 norm-7 types (with
multiplicity, from the types that occur) meeting every budget exactly?  (MILP, HiGHS; exact data are rationals with denominator | 24.)
Types of norm-4 vectors are restricted to admissible h (|(h, beta)| <= 1 at every new root); norm-7 to vectors with |(y, beta)| <= 3/2
at every new root and Y(alpha) = (alpha, y)^2 <= 6 at every root (trap: 2 - Y/7 >= 8/7 for a single y is necessary since the
other y is orthogonal to... NOT used: only the new-root bound is imposed on y, which is proven).
Usage: python component_budget.py <id> ...  -> JSON line per envelope."""
import sys, os, json, time, numpy as np
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frame_dfs as FD
from scipy.optimize import milp, LinearConstraint, Bounds
LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def components(R, G):
    """split roots (rows, coefficient vectors, one per +- pair) into irreducible components by non-orthogonality"""
    n = len(R); RG = R @ G; P = RG @ R.T
    comp = -np.ones(n, dtype=int); c = 0
    for s in range(n):
        if comp[s] >= 0: continue
        stack = [s]; comp[s] = c
        while stack:
            a = stack.pop()
            for b in np.flatnonzero(P[a] != 0):
                if comp[b] < 0: comp[b] = c; stack.append(b)
        c += 1
    return comp, c


for lid in ["%03d" % int(x) for x in sys.argv[1:]]:
    t0 = time.time()
    rec = json.load(open(os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))
    B, G = FD.setup_lattice(rec["gens"]); Gf = G.astype(float)
    V = FD.short(G, 4); X = FD.one_per_pair(V // 2); nrm = np.einsum("ij,jk,ik->i", X, G, X)
    R = X[nrm == 2]
    if len(R) == 0:
        print(json.dumps({"id": lid, "verdict": "no roots: test empty"})); continue
    comp, k = components(R, G)
    c = FD.solve_mod2(G, np.diag(G)); S2 = FD.short(G, 2, c)
    # projections: P_i x has |P_i x|^2 = sum_{alpha in R_i, +-} (alpha, x)^2 / (2 h_i) ; h_i = |R_i| (both signs) / rank_i
    ranks, hs = [], []
    for i in range(k):
        Ri = R[comp == i]; rk = np.linalg.matrix_rank(Ri.astype(float)); ranks.append(int(rk)); hs.append(F(2 * len(Ri), rk))
    rtot = sum(ranks)
    types = {}
    for norm, name in ((3, "u"), (4, "h")):
        Xn = X[nrm == norm]
        if name == "h":
            Xn = Xn[np.abs(Xn @ G @ S2.T).max(axis=1) <= 2]
        if name == "y":
            Xn = Xn[np.abs(Xn @ G @ S2.T).max(axis=1) <= 3]
        A = Xn @ G @ R.T                                               # (x, alpha) for positive-root reps
        T = set()
        for row in A:
            t = []
            for i in range(k):
                s2 = int((row[comp == i] ** 2).sum()) * 2              # both signs
                t.append(F(s2) / (2 * hs[i]))
            t.append(F(norm) - sum(t))
            T.add(tuple(t))
        types[name] = sorted(T)
    budgets = [7 * rk for rk in ranks] + [7 * (24 - rtot)]
    # MILP: integer counts per (kind, type)
    cols = [(nm, t) for nm in ("u", "h") for t in types[nm]]
    nb = k + 1; den = 24 * 24; ny = 2 * nb                               # y: 2 x nb continuous nonnegative parts, each y sums to 7
    A_eq = np.zeros((nb + 2 + 2, len(cols) + ny)); b_eq = np.zeros(nb + 4)
    for j, (nm, t) in enumerate(cols):
        for i in range(nb): A_eq[i, j] = float(t[i] * den)
        A_eq[nb + ("u", "h").index(nm), j] = 1
    for yy in range(2):
        for i in range(nb):
            A_eq[i, len(cols) + yy * nb + i] = den; A_eq[nb + 2 + yy, len(cols) + yy * nb + i] = 1
    for i in range(nb): b_eq[i] = float(budgets[i] * den)
    b_eq[nb:nb + 2] = [42, 7]; b_eq[nb + 2:] = [7, 7]
    integ = np.r_[np.ones(len(cols)), np.zeros(ny)]
    # v2: the y part of each ROOT component is at most 3 rank_i (Y(alpha) <= 6 at every root: min N* >= 8/7 applied to P_N alpha)
    ub = np.full(len(cols) + ny, np.inf)
    for yy in range(2):
        for i in range(k): ub[len(cols) + yy * nb + i] = 3 * ranks[i]          # per y, <= 3 rank_i is implied by the sum bound; use sum below
    A_ub = np.zeros((k, len(cols) + ny)); b_ub = np.zeros(k)
    for i in range(k):
        A_ub[i, len(cols) + i] = 1; A_ub[i, len(cols) + nb + i] = 1; b_ub[i] = 3 * ranks[i]
    res = milp(np.zeros(len(cols) + ny), constraints=[LinearConstraint(A_eq, b_eq, b_eq), LinearConstraint(A_ub, -np.inf, b_ub)], integrality=integ,
               bounds=Bounds(0, np.inf), options={"time_limit": 60})
    verdict = "EXCLUDED (component budgets infeasible)" if res.status == 2 else ("feasible" if res.status == 0 else "undecided %d" % res.status)
    print(json.dumps({"id": lid, "roots": rec.get("roots"), "components": k, "ranks": ranks, "rank_R": int(rtot),
                      "ntypes": {nm: len(types[nm]) for nm in types}, "verdict": verdict, "secs": round(time.time() - t0, 1)}), flush=True)
