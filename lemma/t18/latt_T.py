# Lattice test on T alone (conditional on H16): does Q(k,n) = 9k^2 + 14k(n.1) + 7 n^T G_T n take a value in 1..8 ?
# Also list ALL vectors with Q <= 8 (exact Fincke-Pohst).
import json, os, datetime
from latt import lattice_test, G_T_of, short_vectors, psd_exact
here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
print(datetime.datetime.now())
for case in res:
    if not case["survivors"]:
        continue
    h = case["h"]
    for idx, m in enumerate(case["survivors"]):
        GT = G_T_of(m, h)
        keep = list(range(1, 9))
        Q = [[0] * 9 for _ in range(9)]
        Q[0][0] = 9
        for a, i in enumerate(keep):
            Q[0][a + 1] = Q[a + 1][0] = 7
            for b, j in enumerate(keep):
                Q[a + 1][b + 1] = 7 * GT[i][j]
        ok, rank = psd_exact(Q)
        sv = short_vectors(Q, 8, limit=1000) if ok and rank == 9 else None
        print(f"{case['name']} #{idx}: PSD {ok}, rank {rank}, vectors with 0 < Q <= 8: "
              f"{None if sv is None else len(sv)}")
        if sv:
            for val, x in sv[:5]:
                n = [0] + x[1:]
                print(f"     Q = {val}  k = {x[0]}  n = {n}")
print(datetime.datetime.now())
