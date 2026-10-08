"""(6,6) balls without type-I 4-cycle, WITH 7-torsion of rank 1 in one or both components (fastg.exe, scalar mode).
  case 01: first component torsion-free, second with torsion rank 1; the torsion vector is unbalanced (lemma I), no residue.
  case 11: both of rank 1; balanced vector phi1 + lambda phi2 (lambda = 1..6), phi1 unbalanced, residue of rank 1 (c0 = 1, 3).
Pairs are taken up to a simultaneous permutation of the layers (and the exchange of the components in case 11).
usage: sweep33t.py case workers"""
import sys, json, time, os
from multiprocessing import Pool
import fastlib
from gen66 import torsion_vectors
from multi import make_ball
from sweep33r import TYPES, KEY, action_table

ID = [(0, 1, 2)] * 2


def lists():
    act = action_table()
    free = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 0]
    one = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 1]
    p01 = sorted({min((act[a][s], act[b][s]) for s in range(6)) for a in free for b in one})
    p11 = sorted({min(tuple(sorted((act[a][s], act[b][s]))) for s in range(6)) for a in one for b in one})
    return p01, p11


def job(j):
    t0 = time.time()
    if j[0] == "01":
        _, a, b = j
        adj, lay, comp = make_ball([KEY[a], KEY[b]], ID)
        t2 = torsion_vectors(adj, comp, 1); assert len(t2) == 1
        res = fastlib.run_torsion([KEY[a], KEY[b]], ID, 0, [], t2[0], 0, tag=f"t01_{a}_{b}")
        return f"01 {a} {b} | {res} | {time.time()-t0:.1f}s"
    _, a, b, lam, c0 = j
    adj, lay, comp = make_ball([KEY[a], KEY[b]], ID)
    t1 = torsion_vectors(adj, comp, 0); t2 = torsion_vectors(adj, comp, 1); assert len(t1) == 1 and len(t2) == 1
    psi = [(x + lam * y) % 7 for x, y in zip(t1[0], t2[0])]
    res = fastlib.run_torsion([KEY[a], KEY[b]], ID, 0, [psi], t1[0], c0, tag=f"t11_{a}_{b}_{lam}_{c0}")
    return f"11 {a} {b} lam={lam} c0={c0} | {res} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    case = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    p01, p11 = lists()
    jobs = [("01", a, b) for a, b in p01] if case == "01" else [("11", a, b, lam, c0) for a, b in p11 for lam in range(1, 7) for c0 in (1, 3)]
    log = f"sweep_33t_{case}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    def name(j): return f"01 {j[1]} {j[2]}" if j[0] == "01" else f"11 {j[1]} {j[2]} lam={j[3]} c0={j[4]}"
    todo = [j for j in jobs if name(j) not in done]
    print(f"case {case}: pairs {len(p01) if case == '01' else len(p11)}, runs {len(jobs)}, to do {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line or "ERR" in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"case {case}: runs {len(todo)}, not dead {bad}", flush=True)
