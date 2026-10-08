import sys, json, itertools
from star66 import kmatrix, candidates
from gen66 import make_ball_any, torsion_vectors
types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
i5 = next(i for i, t in enumerate(types) if t["torsion"] == 3)
adj, lay, comp = make_ball_any(key(types[i5]), key(types[i5]), (0, 1, 2)); K = kmatrix(adj, lay)
E1 = torsion_vectors(adj, comp, 0); E2 = torsion_vectors(adj, comp, 1)
for u in [int(x) for x in sys.argv[1:]]:
    cands = candidates(u, adj, lay, comp, K); dem = [K[u][w] for w in range(36)]; dem[u] = 0
    with open(f"u33_{u}.txt", "w") as f:
        f.write(f"{len(cands)} {u}\n" + " ".join(map(str, dem)) + "\n")
        for n in cands:
            a = [sum(p[z] for z in n) % 7 for p in E1]; b = [sum(p[z] for z in n) % 7 for p in E2]
            f.write(" ".join(map(str, n)) + f" {a[0] + 7 * a[1] + 49 * a[2]} {b[0] + 7 * b[1] + 49 * b[2]}\n")
    print("written u =", u, len(cands), flush=True)
