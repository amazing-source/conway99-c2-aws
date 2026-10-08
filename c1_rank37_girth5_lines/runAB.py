"""Pairs of components without type-I 4-cycle whose torsion ranks are (2,2) or (2,3): the balanced torsion is the graph
of an injective map (lemma I + dimension count); combinatorial test of every map at several vertices (thetaAB.exe),
intersecting the surviving maps.  Prints the number of maps left after each vertex."""
import sys, json, subprocess, itertools, os
from star66 import kmatrix
from multi import make_ball, candidates
from gen66 import torsion_vectors
from sweep33r import TYPES, KEY, action_table

act = action_table()
two = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 2]
three = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 3]
pairs = sorted({min((act[a][s], act[b][s]) for s in range(6)) for a in two for b in two + three})
print("types of torsion rank 2:", two, " rank 3:", three, " pairs (first of rank 2):", pairs, flush=True)
for a, b in pairs:
    ra, rb = TYPES[a]["torsion"], TYPES[b]["torsion"]
    adj, lay, comp = make_ball([KEY[a], KEY[b]], [(0, 1, 2)] * 2); K = kmatrix(adj, lay)
    E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
    assert len(E1) == ra and len(E2) == rb
    cur = None
    for u in [0, 1, 6, 12, 18, 19, 24, 30, 2, 7, 13, 20, 25, 31]:
        cands = candidates(u, adj, lay, comp, K, [3, 3]); dem = [K[u][w] for w in range(36)]; dem[u] = 0
        inst = f"ab_{a}_{b}_{u}.txt"
        with open(inst, "w") as f:
            f.write(f"{len(cands)} {u}\n" + " ".join(map(str, dem)) + "\n")
            for n in cands:
                x = [sum(p[z] for z in n) % 7 for p in E1] + [0, 0, 0]; y = [sum(p[z] for z in n) % 7 for p in E2] + [0, 0, 0]
                f.write(" ".join(map(str, n)) + f" {x[0] + 7 * x[1] + 49 * x[2]} {y[0] + 7 * y[1] + 49 * y[2]}\n")
        out = f"ab_{a}_{b}_after{u}.txt"
        cmd = ["./thetaAB.exe", inst, str(ra), str(rb), out] + ([cur] if cur else [])
        res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        left = sum(1 for _ in open(out))
        print(f"pair ({a},{b}) ranks ({ra},{rb}) u={u}: {res}; maps left {left}", flush=True)
        os.remove(inst); cur = out
        if left == 0: break
