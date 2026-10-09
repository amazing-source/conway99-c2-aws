"""The connected balls of the sample of conn_sample.py (same seed, same keys) that have 7-torsion.
At rank 37 a connected line with torsion space E (dimension t) needs a balanced subspace B with 2 dim B >= t; the
radical of the span has dimension t - dim B and the residue rank 2 dim B - t.
Here: t = 1 only (B = E, residue of rank 1, classes c0 = 1, 3; shadows must be balanced).  Exploration only.
usage: conn_tors.py n seed"""
import sys, random, re, time
import fastlib
from conn_sample import rand_key
from gen66 import nullspace7

if __name__ == "__main__":
    n = int(sys.argv[1]); rnd = random.Random(int(sys.argv[2])); stats = {"generic": 0, "t=1 dead": 0, "t=1 not dead": 0, "t>=2": 0}
    t0 = time.time()
    for k in range(n):
        key = rand_key(rnd); adj = fastlib.build(key)
        H = [[((3 if i == j else 0) - (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
        ns = nullspace7(H); t = len(ns) - 1
        if t == 0: stats["generic"] += 1; continue
        if t >= 2: stats["t>=2"] += 1; print(f"ball {k}: torsion rank {t}, not treated", flush=True); continue
        E = []
        for v in ns:
            m = (sum(v) * pow(36 % 7, -1, 7)) % 7; w = [(x - m) % 7 for x in v]
            if any(w): E.append(w)
        assert len(E) >= 1
        out = []
        for c0 in (1, 3):
            res = fastlib.run_torsion([key], [(0, 1, 2)], 0, [E[0]], None, c0, tag=f"ct{sys.argv[2]}")
            out.append(res)
        ok = all("solutions 0 timeout 0" in r and "ERR" not in r for r in out)
        stats["t=1 dead" if ok else "t=1 not dead"] += 1
        print(f"ball {k}: t=1 | c0=1: {out[0][:90]} | c0=3: {out[1][:90]} | {'DEAD' if ok else 'CHECK'}", flush=True)
    print(f"sample {n} seed {sys.argv[2]}: {stats}; {time.time()-t0:.0f}s", flush=True)
