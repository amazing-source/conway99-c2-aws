# t18_B2 / rank_B1_survivors.py -- independent recomputation of the numbers of lemma/t18_STRUCT/REPORT.md section 2:
# odd Gram determinant and even rank for the four B1 stage-C survivors (read from the c_mine control output of this folder).
import json, os
from rankbound import bareiss_det, rank_exact, odd_gram, even_part
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "c_mine_1_0of1_t813.json")))
reps_tau = json.load(open(os.path.join(HERE, "r2_tau_1.json")))["reps"]
for e in d["survivors"]:
    rows = e["rows"]; tau = reps_tau[e["tau"]]
    sig = [9 + i for i in range(9)] + list(range(9)) + [18] + [19 + tau[k] for k in range(18)] + [37 + (c ^ 1) for c in range(10)]
    assert all((rows[sig[u]] >> sig[v]) & 1 == (rows[u] >> v) & 1 for u in range(47) for v in range(47))
    orb = list(range(9)) + [19 + k for k in range(18) if k < tau[k]] + [37 + 2 * c for c in range(5)]
    G = odd_gram(rows, orb, sig)
    E = even_part(rows, orb, sig, fixed=18)
    print(f"B1 matching #{e['tau']}, F = {e['F']}: odd Gram 23 x 23: det = {bareiss_det(G)}, rank {rank_exact(G)} (bound 22); "
          f"even part 24 x 24: rank {rank_exact(E)} (bound 22)")
