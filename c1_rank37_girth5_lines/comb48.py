"""Profile (4,8), balls left COMB-ALIVE by sweep48tp.py: the sub-cases whose residue has rank rho >= 3 (the whole
balanced space B is made of true relations, every far vertex carries a vector of a non-degenerate space of dimension
rho) were only given a combinatorial test there.  Here they get the rank test of fastrD.exe: the 10 x 10 matrix of a
star must have rank <= rho and zero row sums (rho <= 4).  Tried at vertex 0, then at the other near points until one
has no star; a ball is DEAD when every such sub-case is dead at some vertex.
usage: python comb48.py workers log [log ...]      (logs of sweep48tp.py; the COMB-ALIVE lines are taken)"""
import sys, os, time, json
from multiprocessing import Pool
from gen66 import torsion_vectors
from multi import make_ball, kmatrix
from sweep48 import SMALL, big_key
from sweep48t import subspaces, ID
from sweep48tp import pair_filter
from suborb import torsion_action, orbit_filter
from rankD import run_rankD

VERTS = [0, 1, 4, 5, 8, 9, 12, 13, 20, 21, 28, 29] + [v for v in range(36) if v not in (0, 1, 4, 5, 8, 9, 12, 13, 20, 21, 28, 29)]


def job(a):
    s, b, line = a; t0 = time.time()
    try:
        adj, lay, comp = make_ball([SMALL[s], big_key(line)], ID); K = kmatrix(adj, lay); quota = [2, 4]
        Z = [[(4 if comp[v] == 0 else 5) % 7 for v in range(36)]]
        E = torsion_vectors(adj, comp, 1); t = len(E); mats = torsion_action(adj, lay, comp, E)
        comb = lambda coef: [sum(c * e[v] for c, e in zip(coef, E)) % 7 for v in range(36)]
        n = dead = 0; notes = []
        for beta in range(1, t + 1):
            rho = 2 * beta - t + 1
            if rho < 3: continue
            subs = subspaces(t, beta); rows_list = [rows for _, rows in subs]
            passing, nsh = pair_filter(adj, lay, comp, K, quota, E, rows_list, beta, f"c{s}_{b}_{beta}")
            rep = orbit_filter(mats, rows_list)
            for si, rows in enumerate(rows_list):
                if si not in passing or rep[si] != si: continue
                n += 1
                if rho > 4: notes.append(f"beta={beta} rho={rho}: not treated"); continue
                B = [comb(r) for r in rows]; killed = None; tried = []
                for u in VERTS:
                    res = run_rankD(adj, lay, comp, K, quota, Z, B, rho, u, tag=f"c{s}_{b}_{si}")
                    tried.append(u)
                    if "solutions 0 timeout 0" in res and "ERR" not in res: killed = (u, res); break
                    if "timeout 1" in res or "ERR" in res or "NO OUTPUT" in res: notes.append(f"u={u}: {res[:80]}")
                    if len(tried) >= 12: break
                if killed: dead += 1; notes.append(f"beta={beta} rho={rho} rows={rows}: no star at u={killed[0]} ({killed[1]}) after {tried}")
                else: notes.append(f"beta={beta} rho={rho} rows={rows}: a star of rank <= {rho} at each of {tried}")
        verdict = "DEAD" if n and dead == n else ("NOTHING-TO-DO" if n == 0 else "OPEN")
        return f"48c {s} {b} | t={t} sub-cases of residue rank >= 3: {n} dead {dead} {verdict} | {' ; '.join(notes)} | {time.time()-t0:.1f}s"
    except Exception as ex:
        return f"48c {s} {b} | ERROR {type(ex).__name__}: {ex} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    workers = int(sys.argv[1]); lines = [l for l in open("types_m4_p0.txt").read().split("\n") if l.strip()]
    balls = []
    for f in sys.argv[2:]:
        for l in open(f):
            if "COMB-ALIVE" in l: w = l.split(); balls.append((int(w[1]), int(w[2])))
    balls = sorted(set(balls)); log = "sweep_48c.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [(s, b, lines[b]) for s, b in balls if f"48c {s} {b}" not in done]
    print(f"COMB-ALIVE balls: {len(balls)}; to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo, chunksize=1):
            out.write(line + "\n"); out.flush()
            if " DEAD " not in line: bad += 1; print("NOT DEAD:", line[:400], flush=True)
    print(f"(4,8) rank test of the COMB-ALIVE balls: {len(todo)} balls, not dead {bad}", flush=True)
