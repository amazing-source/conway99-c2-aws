"""Sweeps for the (6,6) balls with 7-torsion (cases 01u, 10u, 11 of gen66.py), 4 workers, one line per run."""
import sys, json, itertools
from multiprocessing import Pool
import gen66

def job(a):
    case, i1, i2, r, u, c0, lam = a
    try:
        return gen66.run(case, i1, i2, r, u, c0, lam, tag=f"sw_{case}_{i1}_{i2}_{r}_{u}_{c0}_{lam}")
    except Exception as ex:
        return f"{case} {i1} {i2} rho={r} u={u} c0={c0} lam={lam} ERROR {type(ex).__name__}: {ex}"

if __name__ == "__main__":
    types = json.load(open("comp66_types.json"))
    free = [i for i, t in enumerate(types) if t["torsion"] == 0]; one = [i for i, t in enumerate(types) if t["torsion"] == 1]
    which = sys.argv[1]
    jobs = []
    if which == "01u":
        jobs = [("01u", a, b, r, 0, 1, 1) for a in free for b in one for r in range(6)]
    elif which == "10u":
        jobs = [("10u", a, b, r, 0, 1, 1) for a in one for b in free for r in range(6)]
    elif which == "11":
        jobs = [("11", a, b, r, 0, c0, lam) for a in one for b in one for r in range(6) for lam in range(1, 7) for c0 in (1, 3)]
    out = open(f"sweep_{which}.log", "a"); bad = 0
    with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as p:
        for line in p.imap_unordered(job, jobs):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"{which}: runs {len(jobs)}, not dead {bad}", flush=True)
