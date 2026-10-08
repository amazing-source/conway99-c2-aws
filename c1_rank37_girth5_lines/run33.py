"""Driver for theta33.exe: ball = type 5 + type 5 (torsion rank 3 each), every relative order of the layers, vertex u."""
import sys, json, itertools, subprocess, time
from star66 import kmatrix, candidates
from gen66 import make_ball_any, torsion_vectors

types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
three = [i for i, t in enumerate(types) if t["torsion"] == 3]
u = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for i1 in three:
    for i2 in three:
        for r, rho in enumerate(itertools.permutations(range(3))):
            adj, lay, comp = make_ball_any(key(types[i1]), key(types[i2]), rho)
            K = kmatrix(adj, lay)
            E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
            assert len(E1) == 3 and len(E2) == 3
            cands = candidates(u, adj, lay, comp, K)
            dem = [K[u][w] for w in range(36)]; dem[u] = 0
            path = f"inst33_{r}.txt"
            with open(path, "w") as f:
                f.write(f"{len(cands)} {u}\n" + " ".join(map(str, dem)) + "\n")
                for n in cands:
                    a = [sum(p[z] for z in n) % 7 for p in E1]; b = [sum(p[z] for z in n) % 7 for p in E2]
                    f.write(" ".join(map(str, n)) + f" {a[0] + 7 * a[1] + 49 * a[2]} {b[0] + 7 * b[1] + 49 * b[2]}\n")
            t0 = time.time()
            res = subprocess.run(["./theta33.exe", path], capture_output=True, text=True).stdout.strip()
            print(f"types ({i1},{i2}) rho={r} u={u} candidates={len(cands)}: {res} ({time.time()-t0:.0f}s)", flush=True)
