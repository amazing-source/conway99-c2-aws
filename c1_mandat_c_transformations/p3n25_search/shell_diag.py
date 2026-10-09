"""what do the parabola witnesses on the shell look like?  minimal supports, labels.   usage: shell_diag.py id rounds"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST, shell as SH
sid = int(sys.argv[1]); R = int(sys.argv[2]); d = I.load("register/supports_open_4581.jsonl", sid); rng = random.Random(3)
S = SH.Shell(d, 0); A = S.A
lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if A[s, p]) or "-")
def shrink(Ap, w, a):
    w = np.array(w); val = ST.phi_direct(Ap, w, a); changed = True
    while changed:
        changed = False
        for k in np.nonzero(w)[0]:
            for new in (0, w[k] - np.sign(w[k])):
                w2 = w.copy(); w2[k] = new; v2 = ST.phi_direct(Ap, w2, a)
                if v2 < 0 and (np.count_nonzero(w2) < np.count_nonzero(w) or abs(w2).sum() < abs(w).sum()):
                    w, val, changed = w2, v2, True; break
    return w, val
for it in range(R):
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 200; sv.parameters.num_workers = 8; sv.parameters.random_seed = it
    st = sv.Solve(S.m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print("status", sv.StatusName(st)); break
    Ap = S.adjacency(sv); val, w, a = ST.witness(Ap, rng, restarts=80)
    if val >= 0: print("no witness"); break
    w2, v2 = shrink(Ap, w, a)
    name = lambda k: lab(k) if k < 28 else "z%d(%s; %s)" % (k - 28, "".join("ABC"[p] for p in S.types[k - 28]), ",".join(str(s) for s in range(3, 28) if Ap[k, s]))
    print(f"round {it}: Phi = {val} with {np.count_nonzero(w)} weights; shrunk: Phi = {v2}, a = {a}, {np.count_nonzero(w2)} weights:")
    for k in np.nonzero(w2)[0]: print(f"      {int(w2[k]):+d}  {name(k)}")
    supp = list(np.nonzero(w2)[0]); print("      edges inside:", [(name(x).split('(')[0], name(y).split('(')[0]) for x, y in itertools.combinations(supp, 2) if Ap[x, y]])
    S.add_cut(w2, a)
