"""Stronger search of an integer-parabola witness for given supports: many restarts, weights up to 3."""
import sys, json, random
import numpy as np
import p3n25_ilp as I, parabola as PA
rng = random.Random(12345)
for sid in map(int, sys.argv[1:]):
    d = I.load("register/supports_open_4581.jsonl", sid)
    adj, R, dv = PA.data(d)
    best = (10 ** 9, None, None)
    for wmax in (2, 3):
        val, w, a = PA.search(R, dv, rng, wmax, restarts=1500)
        if val < best[0]: best = (val, w, a)
        if best[0] < 0: break
    val, w, a = best
    lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
    print(f"support {sid}: min Phi found = {val}  (a = {a});  weights: " + ", ".join(f"{lab(s)}:{int(w[s]):+d}" for s in range(28) if w[s]))
