"""Same sub-cases as sweep48t.py (profile (4,8), large component with 7-torsion), with the PAIR LEMMA as a first filter:
a subspace B of balanced torsion vectors must leave, for every pair of near points with K_ab = c > 0, at least c
admissible B-balanced 6-sets containing the pair (pairt.exe; purely combinatorial).  The subspaces that fail are dead
without any search; the others go to fastg4.exe exactly as in sweep48t.py.  One line per ball:
   48t s b | t=.. sub-cases N pair-dead P orbit-dup O dead D comb-alive .. alive .. VERDICT | group, time
(N = all sub-cases, P = those removed by the pair lemma, O = those not searched because an automorphism of the ball
sends them to a searched one (suborb.py), D = all those established dead; DEAD means D = N).
usage: python sweep48tp.py workers [part nparts] [T]"""
import sys, os, time, json, subprocess
from multiprocessing import Pool
from gen66 import Solver, torsion_vectors
from multi import make_ball, kmatrix
from sweep48 import SMALL, REPS, big_key
from sweep48t import subspaces, run_case, ID
from suborb import torsion_action, orbit_filter

PAIR = os.path.abspath("pairt.exe")


def pair_filter(adj, lay, comp, K, quota, E, rows_list, d, tag):
    """indices of the subspaces (given by d rows of coefficients on E) that pass the pair test, and the number of admissible sets"""
    path = f"pt_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{len(E)} {len(rows_list)} {d} {len(quota)}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for row in K: f.write(" ".join(map(str, row)) + "\n")
        for e in E: f.write(" ".join(map(str, e)) + "\n")
        for rows in rows_list:
            for r in rows: f.write(" ".join(map(str, r)) + "\n")
    r = subprocess.run([PAIR, path], capture_output=True, text=True)
    os.remove(path)
    head, tail = r.stdout.strip().split(":")
    w = head.split(); assert w[0] == "shadows" and int(w[3]) == len(rows_list)
    passing = [int(x) for x in tail.split()]; assert len(passing) == int(w[5])
    return set(passing), int(w[1])


def job(a):
    s, b, line = a
    t0 = time.time()
    try:
        keys = [SMALL[s], big_key(line)]
        adj, lay, comp = make_ball(keys, ID); K = kmatrix(adj, lay); quota = [2, 4]
        Z = [[(4 if comp[v] == 0 else 5) % 7 for v in range(36)]]
        M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
        sol = Solver(M0); Q = [[0] * 36 for _ in range(36)]
        for i, c in enumerate(sol.piv): Q[c] = sol.E[i][:]
        E = torsion_vectors(adj, comp, 1); t = len(E)
        assert not torsion_vectors(adj, comp, 0)
        mats = torsion_action(adj, lay, comp, E)                 # automorphisms of the ball acting on E
        comb = lambda coef: [sum(c * e[v] for c, e in zip(coef, E)) % 7 for v in range(36)]
        n = dead = pdead = odup = calive = alive = 0; notes = []; nsh = -1
        for beta in range(0, t + 1):
            if 1 + t > 2 * (1 + beta): continue
            rho = 2 * beta - t + 1
            subs = subspaces(t, beta); rows_list = [rows for _, rows in subs]
            if beta >= 1:
                passing, nsh = pair_filter(adj, lay, comp, K, quota, E, rows_list, beta, f"{s}_{b}_{beta}")
                rep = orbit_filter(mats, rows_list)
                # the pair test is invariant under the automorphisms: a free check of both
                assert all((i in passing) == (rep[i] in passing) for i in range(len(subs))), "pair test not constant on an orbit"
            else:
                passing = set(range(len(subs))); rep = {i: i for i in range(len(subs))}
            forms = [(0, 0)] if rho == 0 else [(1, 0), (3, 0)] if rho == 1 else [(1, 1), (1, 3)] if rho == 2 else [(0, 0)]
            verdict_of = {}                                      # (representative, form) -> True if dead
            for si, (piv, rows) in enumerate(subs):              # representatives come first in their orbit (smallest index)
                if si not in passing:
                    n += len(forms); dead += len(forms); pdead += len(forms); continue
                if rep[si] != si:
                    for fm in forms:
                        n += 1; odup += 1
                        if verdict_of[(rep[si], fm)]: dead += 1
                    continue
                extra = [comb(r) for r in rows]
                phis = [comb([int(i == c) for i in range(t)]) for c in range(t) if c not in piv]
                for (C0, C1) in forms:
                    n += 1
                    res = run_case(adj, lay, comp, K, quota, sol, Q, M0, Z, 0, extra, phis, C0, C1, 1 if rho >= 3 else 0, f"{s}_{b}_{n}")
                    ok = "solutions 0 timeout 0" in res and "ERR" not in res
                    verdict_of[(si, (C0, C1))] = ok
                    if ok: dead += 1
                    elif rho >= 3: calive += 1; notes.append(f"beta={beta} piv={piv} rows={rows} comb")
                    else: alive += 1; notes.append(f"beta={beta} rows={rows} form=({C0},{C1}): {res}")
        verdict = "DEAD" if dead == n else ("COMB-ALIVE" if alive == 0 else "ALIVE")
        return (f"48t {s} {b} | t={t} sub-cases {n} pair-dead {pdead} orbit-dup {odup} dead {dead} comb-alive {calive} alive {alive} {verdict} "
                f"{' ; '.join(notes[:3])} | group {len(mats)} admissible sets {nsh} | {time.time()-t0:.1f}s")
    except Exception as ex:
        return f"48t {s} {b} | ERROR {type(ex).__name__}: {ex} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    part = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nparts = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    lines = [l for l in open("types_m4_p0.txt").read().split("\n") if l.strip()]
    tors = json.load(open("tors_m4.json"))                     # [(index of the large type, torsion rank)]
    T = sys.argv[4] if len(sys.argv) > 4 else "all"
    if T != "all": tors = [x for x in tors if x[1] == int(T)]
    jobs = [(s, b, lines[b]) for s in REPS for (b, t) in tors]
    if os.path.exists("reps48.txt"):       # one ball per isomorphism class (reps48.py)
        keep = {tuple(map(int, l.split()[:2])) for l in open("reps48.txt") if l.strip()}
        jobs = [j for j in jobs if (j[0], j[1]) in keep]
        print(f"restricted to the representatives of reps48.txt ({len(keep)} balls in all)", flush=True)
    jobs = [j for i, j in enumerate(jobs) if i % nparts == part]
    log = f"sweep_48tp_T{T}_part{part}of{nparts}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [j for j in jobs if f"48t {j[0]} {j[1]}" not in done]
    print(f"torsion balls in this part: {len(jobs)}; to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0; n = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo, chunksize=1):
            out.write(line + "\n"); out.flush(); n += 1
            if " DEAD " not in line: bad += 1; print("NOT DEAD:", line[:300], flush=True)
    print(f"(4,8) torsion with pair lemma, T={T}, part {part}/{nparts}: balls {len(todo)}, not dead {bad}", flush=True)
