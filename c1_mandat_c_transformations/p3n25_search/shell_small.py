"""smallest parabola witnesses on shells: what do they look like?   usage: shell_small.py id nshells"""
import sys, json, time, random, itertools, collections
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST, shell as SH
sid = int(sys.argv[1]); R = int(sys.argv[2]); d = I.load("register/supports_open_4581.jsonl", sid); rng = random.Random(8)
S = SH.Shell(d, 0); A = S.A
lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if A[s, p]) or "-")
def shrink(Ap, w, a):
    w = np.array(w); changed = True
    while changed:
        changed = False
        for k in rng.sample(list(np.nonzero(w)[0]), int(np.count_nonzero(w))):
            for new in (0, w[k] - np.sign(w[k])):
                w2 = w.copy(); w2[k] = new
                if ST.phi_direct(Ap, w2, a) < 0: w, changed = w2, True; break
    return w
for it in range(R):
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 300; sv.parameters.num_workers = 4; sv.parameters.random_seed = 100 + it
    st = sv.Solve(S.m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print("status", sv.StatusName(st)); break
    Ap = S.adjacency(sv); found = {}
    for k in range(150):
        val, w, a = ST.witness(Ap, rng, restarts=6)
        if val >= 0: continue
        w2 = shrink(Ap, w, a); found[(a, tuple(int(x) for x in w2))] = ST.phi_direct(Ap, w2, a)
    name = lambda k: lab(k) if k < 28 else "z%d(%s)" % (k - 28, "".join("ABC"[p] for p in S.types[k - 28]))
    sizes = collections.Counter(sum(1 for x in w if x) for a, w in found)
    print(f"shell {it}: {len(found)} distinct shrunk witnesses; sizes {sorted(sizes.items())}")
    for (a, w), val in sorted(found.items(), key=lambda kv: sum(1 for x in kv[0][1] if x))[:6]:
        supp = [k for k in range(len(w)) if w[k]]
        deg_in = {k: int(Ap[k].sum()) for k in supp}
        print(f"   a = {a}, Phi = {val}: " + "  ".join(f"{w[k]:+d}{name(k)}[deg {deg_in[k]}]" for k in supp))
        print(f"        edges inside: {[(name(x), name(y)) for x, y in itertools.combinations(supp, 2) if Ap[x, y]]}")
        # where does the excess sit: vertices of S+ with t(t-1) > 0
        t = Ap @ np.array(w); ex = [(name(k), int(t[k])) for k in range(len(w)) if t[k] * (t[k] - 1) > 0]
        tot = 12 * sum(x * x for x in w) + 2 * sum(w) ** 2 - int(np.array(w) @ Ap @ np.array(w)) - 14 * sum(w)
        print(f"        total budget over the 99 vertices: {tot}; used inside S+: {sum(v * (v - 1) for _, v in ex)} by {ex}")
