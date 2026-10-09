"""Pairs of components (no type-I 4-cycle) involving the single type of torsion rank 2 (fastg3.exe).
By lemma I and the dimension count the balanced torsion is the graph of an injective linear map between the torsion spaces:
  case 12: (rank 1, rank 2): balanced vector phi + psi, psi any non-zero vector of the rank-2 space (48); radical of
           dimension 2 (the rank-2 space), no residue;
  case 22: (rank 2, rank 2): graph of an isomorphism M (2016); radical of dimension 2; residue of rank 1 (c0 = 1, 3);
  case 23: (rank 2, rank 3): graph of an injective map M, 2 x 3 of rank 2 (114 912 maps, one run per orbit of the
           automorphisms of the ball: 9 726 runs); radical of dimension 3; no residue.
usage: sweepX.py case workers"""
import sys, json, time, os, itertools
from multiprocessing import Pool
import fastlib
from gen66 import torsion_vectors
from multi import make_ball
from sweep33r import TYPES, KEY, action_table

ID = [(0, 1, 2)] * 2
TWO = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 2]
THREE = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 3]
ONE = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 1]


def comb(E, coef):
    return [sum(c * e[v] for c, e in zip(coef, E)) % 7 for v in range(36)]


def rank2(M, a, b):
    from gen66 import nullspace7
    return b - len(nullspace7([list(r) for r in M])) == a


def job(j):
    t0 = time.time(); case = j[0]
    if case == "12":
        _, a, b, coef = j
        adj, lay, comp = make_ball([KEY[a], KEY[b]], ID); E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
        psi = [(x + y) % 7 for x, y in zip(E1[0], comb(E2, coef))]
        res = fastlib.run_torsion3([KEY[a], KEY[b]], ID, 0, [psi], E2, 0, tag=f"x12_{a}_{b}_{coef[0]}{coef[1]}")
        return f"12 {a} {b} psi={coef[0]}{coef[1]} | {res} | {time.time()-t0:.1f}s"
    if case == "22":
        _, a, b, M, c0 = j
        adj, lay, comp = make_ball([KEY[a], KEY[b]], ID); E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
        psis = [[(x + y) % 7 for x, y in zip(E1[k], comb(E2, M[k]))] for k in range(2)]
        res = fastlib.run_torsion3([KEY[a], KEY[b]], ID, 0, psis, E1, c0, tag=f"x22_{''.join(map(str, M[0] + M[1]))}_{c0}")
        return f"22 {a} {b} M={''.join(map(str, M[0] + M[1]))} c0={c0} | {res} | {time.time()-t0:.1f}s"
    _, a, b, M, size = j
    adj, lay, comp = make_ball([KEY[a], KEY[b]], ID); E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
    psis = [[(x + y) % 7 for x, y in zip(E1[k], comb(E2, M[k]))] for k in range(2)]
    res = fastlib.run_torsion3([KEY[a], KEY[b]], ID, 0, psis, E2, 0, tag=f"x23_{''.join(map(str, M[0] + M[1]))}")
    return f"23 {a} {b} M={''.join(map(str, M[0] + M[1]))} | {res} | orbit {size} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    case = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    act = action_table(); jobs = []
    if case == "12":
        pairs = sorted({min((act[a][s], act[b][s]) for s in range(6)) for a in ONE for b in TWO})
        jobs = [("12", a, b, c) for a, b in pairs for c in itertools.product(range(7), repeat=2) if any(c)]
    elif case == "22":
        for M in itertools.product(itertools.product(range(7), repeat=2), repeat=2):
            if (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % 7:
                for c0 in (1, 3): jobs.append(("22", TWO[0], TWO[0], M, c0))
    elif case == "23":
        # one map per orbit of the automorphisms of the ball (orbits23.py); the orbit sizes add up to the 114 912 maps
        from orbits23 import orbit_reps
        maps = [M for M in itertools.product(itertools.product(range(7), repeat=3), repeat=2) if rank2(M, 2, 3)]
        order, reps = orbit_reps([KEY[TWO[0]], KEY[THREE[0]]], maps)
        print(f"case 23: {len(maps)} maps, automorphism group of order {order}, {len(reps)} orbits", flush=True)
        jobs = [("23", TWO[0], THREE[0], M, size) for M, size in reps]
    log = f"sweep_X{case}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    def name(j):
        if j[0] == "12": return f"12 {j[1]} {j[2]} psi={j[3][0]}{j[3][1]}"
        if j[0] == "22": return f"22 {j[1]} {j[2]} M={''.join(map(str, j[3][0] + j[3][1]))} c0={j[4]}"
        return f"23 {j[1]} {j[2]} M={''.join(map(str, j[3][0] + j[3][1]))}"
    todo = [j for j in jobs if name(j) not in done]
    print(f"case {case}: runs {len(jobs)}, to do {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo, chunksize=4):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line or "ERR" in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"case {case}: runs {len(todo)}, not dead {bad}", flush=True)
