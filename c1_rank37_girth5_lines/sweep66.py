"""Sweep: every (6,6) ball made of two torsion-free components (types 0, 1, 4, 6 of comp66_types.json), every relative
order of the layers, vertex u = 0 of the first component, both square classes of c0.  One line per run."""
import sys, json, itertools, subprocess, time, os
import star66c
types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
free = [i for i, t in enumerate(types) if t["torsion"] == 0]
us = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [0]
out = open(sys.argv[2] if len(sys.argv) > 2 else "sweep66.log", "a")
tot = alive = 0
for i1 in free:
    for i2 in free:
        for r, rho in enumerate(itertools.permutations(range(3))):
            for u in us:
                for c0 in (1, 3):
                    path = "inst_sweep.txt"
                    nc, ni = star66c.write_instance(path, key(types[i1]), key(types[i2]), rho, u, c0, 0, 1, 20000000000)
                    t0 = time.time()
                    res = subprocess.run(["./starc.exe", path], capture_output=True, text=True).stdout.strip().split("\n")[-1]
                    line = f"{i1} {i2} rho={r} u={u} c0={c0} cands={nc} | {res} | {time.time()-t0:.1f}s"
                    out.write(line + "\n"); out.flush(); tot += 1
                    if "solutions 0 timeout 0" not in res: alive += 1; print("NOT DEAD:", line, flush=True)
print(f"runs {tot}, not dead {alive}", flush=True)
