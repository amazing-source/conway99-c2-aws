"""Profile (4,8) without type-I 4-cycle, large component WITH 7-torsion (the balls marked TORSION by sweep48.py).
The small component has no 7-torsion.  Let E be the torsion space of the large component (dimension t) and B the
subspace of its balanced vectors (dimension beta).  True relations = z0 and B; radical of the span = E / B; the
dimension count forces 1 + t <= 2 (1 + beta); the residue has rank rho = 2 beta - t + 1.  Every subspace B is tried:
   rho = 0: no residue;  rho = 1: classes c0 = 1, 3;  rho = 2: forms <1,1> and <1,3>;
   rho >= 3: only the combinatorial test (ten B-balanced shadows through u with sum K e_u, intersections <= 2).
A ball is dead when every sub-case is dead.  One line per ball.
usage: python sweep48t.py workers [part nparts]"""
import sys, os, time, json, itertools, subprocess
from multiprocessing import Pool
from gen66 import Solver, torsion_vectors, nullspace7
from multi import make_ball, kmatrix
from sweep48 import SMALL, REPS, big_key

ID = [(0, 1, 2)] * 2
EXE = os.path.abspath("fastg4.exe")


def subspaces(t, beta):
    """bases (lists of coefficient vectors) of all subspaces of dimension beta of F_7^t, in reduced echelon form"""
    out = []
    for piv in itertools.combinations(range(t), beta):
        free = [(i, c) for i, p in enumerate(piv) for c in range(p + 1, t) if c not in piv]
        for vals in itertools.product(range(7), repeat=len(free)):
            rows = [[0] * t for _ in range(beta)]
            for i, p in enumerate(piv): rows[i][p] = 1
            for (i, c), v in zip(free, vals): rows[i][c] = v
            out.append((piv, rows))
    return out


def run_case(adj, lay, comp, K, quota, sol, Q, M0, Z, u, extra_T, phis, C0, C1, comb, tag):
    assert 36 - sol.rank == len(Z) + len(extra_T) + len(phis)
    T = Z + extra_T; betas = []
    for k in range(len(phis)):
        rows = [p[:] for p in phis] + [x[:] for x in T]; rhs = [int(i == k) for i in range(len(phis))] + [0] * len(T)
        A = [r + [b] for r, b in zip(rows, rhs)]; piv = []; rr = 0
        for c in range(36):
            p = next((i for i in range(rr, len(A)) if A[i][c] % 7), None)
            if p is None: continue
            A[rr], A[p] = A[p], A[rr]; iv = pow(A[rr][c], -1, 7); A[rr] = [(x * iv) % 7 for x in A[rr]]
            for i in range(len(A)):
                if i != rr and A[i][c] % 7:
                    f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[rr])]
            piv.append(c); rr += 1
        assert rr == len(rows)
        beta = [0] * 36
        for i, c in enumerate(piv): beta[c] = A[i][36]
        betas.append(beta)
    cross = [z for z in adj[u] if lay[z] != lay[u]]; mate = next(z for z in adj[u] if lay[z] == lay[u])
    als = []
    for beta in betas:
        bl = sum(beta[z] * (2 * (1 if lay[z] == lay[u] else 0) + 2) for z in range(36))
        als.append((-(4 * beta[u] + bl + beta[mate] + sum(beta[z] for z in cross))) % 7)
    als += [0] * (3 - len(als))
    path = f"fg4_{tag}_{os.getpid()}.txt"      # the process id keeps two runs from sharing a file
    with open(path, "w") as f:
        f.write(f"{u} {C0} {C1} {comb} 2 {len(extra_T)} {len(phis)} {als[0]} {als[1]} {als[2]} 1 2000000000\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, M0, Q):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for tv in extra_T + phis + betas: f.write(" ".join(map(str, tv)) + "\n")
    r = subprocess.run([EXE, path], capture_output=True, text=True)
    os.remove(path)
    out = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else "NO OUTPUT"
    if r.stderr.strip(): out += " ERR " + r.stderr.strip()
    return out


def job(a):
    s, b, line = a
    t0 = time.time()
    try:
        keys = [SMALL[s], big_key(line)]
        adj, lay, comp = make_ball(keys, ID); K = kmatrix(adj, lay); quota = [2, 4]
        Z = [[(4 if comp[v] == 0 else 5) % 7 for v in range(36)]]          # 4 * 1_C1 - 2 * 1_C2 mod 7
        M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
        sol = Solver(M0); Q = [[0] * 36 for _ in range(36)]
        for i, c in enumerate(sol.piv): Q[c] = sol.E[i][:]
        E = torsion_vectors(adj, comp, 1); t = len(E)
        assert not torsion_vectors(adj, comp, 0)
        comb = lambda coef: [sum(c * e[v] for c, e in zip(coef, E)) % 7 for v in range(36)]
        n = dead = calive = alive = 0; notes = []
        for beta in range(0, t + 1):
            if 1 + t > 2 * (1 + beta): continue
            rho = 2 * beta - t + 1
            for piv, rows in subspaces(t, beta):
                extra = [comb(r) for r in rows]
                phis = [comb([int(i == c) for i in range(t)]) for c in range(t) if c not in piv]
                forms = [(0, 0)] if rho == 0 else [(1, 0), (3, 0)] if rho == 1 else [(1, 1), (1, 3)] if rho == 2 else [(0, 0)]
                for (C0, C1) in forms:
                    n += 1
                    res = run_case(adj, lay, comp, K, quota, sol, Q, M0, Z, 0, extra, phis, C0, C1, 1 if rho >= 3 else 0, f"{s}_{b}_{n}")
                    if "solutions 0 timeout 0" in res and "ERR" not in res: dead += 1
                    elif rho >= 3: calive += 1; notes.append(f"beta={beta} piv={piv} rows={rows} comb")
                    else: alive += 1; notes.append(f"beta={beta} rows={rows} form=({C0},{C1}): {res}")
        verdict = "DEAD" if dead == n else ("COMB-ALIVE" if alive == 0 else "ALIVE")
        return f"48t {s} {b} | t={t} sub-cases {n} dead {dead} comb-alive {calive} alive {alive} {verdict} {' ; '.join(notes[:3])} | {time.time()-t0:.1f}s"
    except Exception as ex:
        return f"48t {s} {b} | ERROR {type(ex).__name__}: {ex} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    part = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nparts = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    lines = [l for l in open("types_m4_p0.txt").read().split("\n") if l.strip()]
    tors = json.load(open("tors_m4.json"))                     # [(index of the large type, torsion rank)]
    if len(sys.argv) > 4: tors = [x for x in tors if x[1] == int(sys.argv[4])]
    jobs = [(s, b, lines[b]) for s in REPS for (b, t) in tors]
    if os.path.exists("reps48.txt"):       # one ball per isomorphism class (reps48.py)
        keep = {tuple(map(int, l.split()[:2])) for l in open("reps48.txt") if l.strip()}
        jobs = [j for j in jobs if (j[0], j[1]) in keep]
        print(f"restricted to the representatives of reps48.txt ({len(keep)} balls in all)", flush=True)
    jobs = [j for i, j in enumerate(jobs) if i % nparts == part]
    log = f"sweep_48t_part{part}of{nparts}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [j for j in jobs if f"48t {j[0]} {j[1]}" not in done]
    print(f"torsion balls in this part: {len(jobs)}; to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0; n = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo, chunksize=2):
            out.write(line + "\n"); out.flush(); n += 1
            if " DEAD " not in line: bad += 1; print("NOT DEAD:", line[:300], flush=True)
    print(f"(4,8) torsion part {part}/{nparts}: balls {len(todo)}, not dead {bad}", flush=True)
