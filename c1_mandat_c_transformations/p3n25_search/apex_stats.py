"""for supports alive after level 2: number of blocks left for each apex pair (an edge of the support whose triangle leaves it)"""
import sys, json, time, random
import numpy as np
import p3n25_ilp as I, level2 as L2, level2_cert as LC
fn = "register/supports_open_4581.jsonl"
for sid in map(int, sys.argv[1:]):
    d = I.load(fn, sid); t0 = time.time()
    P, wit, alive, cover, full, dead_pairs, dead_points = LC.certificate(d)
    A = P["A"]; r = P["r"]; adj = P["adj"]
    lab = lambda s: ("ABC"[s]) if s < 3 else "n%d[%s]" % (s, "".join("ABC"[p] for p in range(3) if (adj[s] >> p) & 1) or "-")
    ap = sorted(((int(cover[s, t]), int(full[s, t]), lab(s), lab(t)) for s in range(28) for t in range(s + 1, 28) if A[s, t] and r[s][t] == 1))
    na = sorted((int(cover[s, t]) // r[s][t], int(full[s, t]), lab(s), lab(t), r[s][t]) for s in range(28) for t in range(s + 1, 28) if not A[s, t] and r[s][t] >= 1)
    print(f"support {sid} (delta {d['delta']}): {int(alive.sum())}/{len(wit)} blocks; {len(ap)} apex pairs; blocks left per apex pair: {[a[0] for a in ap]}")
    print(f"     smallest: {ap[:3]};   non-adjacent pairs, smallest (left / r): {na[:3]}", flush=True)
