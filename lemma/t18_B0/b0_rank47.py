# Rank bound applied to stage-C survivors (47 vertices S u {p} u X_2 u W: 23 orbits + p).  Required: odd part of
# 27I-9A+J of rank <= 22 (so the 23 x 23 odd Gram is singular), even part (24 x 24) of rank <= 22.  Exact ranks.
# usage: python b0_rank47.py <structure index> <file with a "survivors" list (rows = 47 bit masks, tau index)> ...
import json, sys
import numpy as np
from b0_rank import parts, violates
s_idx = int(sys.argv[1])
reps = json.load(open(f"r2_tau_{s_idx}.json"))["reps"]
seen = set(); n = dead = 0
for fn in sys.argv[2:]:
    for e in json.load(open(fn))["survivors"]:
        key = tuple(e["rows"])
        if key in seen:
            continue
        seen.add(key)
        tau = reps[e["tau"]]
        A = np.array([[(e["rows"][u] >> v) & 1 for v in range(47)] for u in range(47)], dtype=np.int64)
        sig = list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)]
        for c in range(5):
            sig += [38 + 2 * c, 37 + 2 * c]
        sig = np.array(sig)
        assert (A == A.T).all() and (A[np.ix_(sig, sig)] == A).all()
        res = parts(A, sig)
        d = violates(res)
        n += 1; dead += d
        print(f"matching #{e['tau']}, F = {e['F']}: {res}; violates the rank bound: {d}")
print(f"stage-C survivors examined: {n}; killed by the rank bound: {dead}")
