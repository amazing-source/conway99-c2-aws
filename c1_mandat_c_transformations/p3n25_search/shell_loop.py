"""long cut loop on the shell: several shrunk parabola witnesses per shell found.   usage: shell_loop.py id tau rounds solve_tl workers"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST, shell as SH
sid, tau, R, TL, NW = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
d = I.load("register/supports_open_4581.jsonl", sid); rng = random.Random(3)
S = SH.Shell(d, tau); assert S.ok
def shrink(Ap, w, a):
    w = np.array(w); changed = True
    while changed:
        changed = False
        for k in rng.sample(list(np.nonzero(w)[0]), int(np.count_nonzero(w))):
            for new in (0, w[k] - np.sign(w[k])):
                w2 = w.copy(); w2[k] = new
                if ST.phi_direct(Ap, w2, a) < 0: w, changed = w2, True; break
    return w
t0 = time.time(); log = open(f"shell_loop_{sid}_{tau}.log", "a"); ncut = 0
for it in range(R):
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = TL; sv.parameters.num_workers = NW; sv.parameters.random_seed = it
    ts = time.time(); st = sv.Solve(S.m); name = sv.StatusName(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"round {it}: {name} after {ncut} cuts  [solve {time.time()-ts:.0f}s, total {time.time()-t0:.0f}s]", file=log, flush=True); break
    Ap = S.adjacency(sv); found = {}
    for k in range(10):
        val, w, a = ST.witness(Ap, rng, restarts=30)
        if val >= 0: continue
        w2 = shrink(Ap, w, a); found[(a, tuple(int(x) for x in w2))] = 1
    if not found:
        np.save(f"shell_alive_{sid}_{tau}.npy", Ap)
        print(f"round {it}: shell WITHOUT witness after {ncut} cuts  [total {time.time()-t0:.0f}s]", file=log, flush=True); break
    for (a, w2) in found: S.add_cut(list(w2), a); ncut += 1
    print(f"round {it}: {len(found)} cuts (sizes {sorted(sum(1 for x in w if x) for a, w in found)}), total {ncut}  [solve {time.time()-ts:.0f}s, total {time.time()-t0:.0f}s]", file=log, flush=True)
json.dump(S.cuts, open(f"shell_cuts_{sid}_{tau}.json", "w"))
