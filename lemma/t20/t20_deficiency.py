# T20: deficient pairs of S+ for the nine survivors.
# m_ij = (1 if x_i ~ x_j else 2) - number of common neighbours of x_i, x_j in S u {p}
#      = number of common neighbours of x_i, x_j outside S u {p}  (they have d >= 2).
import json
from t20_common import *
ref = {}
for fn in ("structures_III_IIb_IIa.json", "structures_I.json"):
    ref.update(json.load(open(fn)))
for case in ("I", "IIa", "III"):
    for idx, rec in enumerate(ref[case]):
        m, H = rec["m"], rec["H"]
        st = {(i, j): m[i][j] for (i, j) in PAIRS if m[i][j]}
        adj = graph_of(st, H)
        pairs = {}
        for i in range(N):
            for j in range(i + 1, N):
                c = bin(adj[i] & adj[j]).count("1")
                need = 1 if (adj[i] >> j) & 1 else 2
                assert c <= need
                if need - c:
                    pairs[(i, j)] = need - c
        tot = sum(pairs.values())
        per = [sum(v for (a, b), v in pairs.items() if t in (a, b)) for t in range(N)]
        print("%s.%d: total deficiency %d; pairs with deficiency 1: %s" % (case, idx, tot,
              " ".join("%d%d" % p for p, v in sorted(pairs.items()) if v == 1)))
        print("      pairs with deficiency 2: %s" % (" ".join("%d%d" % p for p, v in sorted(pairs.items()) if v == 2) or "-"))
        print("      deficiency per vertex x_0..x_9: %s" % per)
