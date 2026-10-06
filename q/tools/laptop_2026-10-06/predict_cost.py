"""Can the cost of a one-y1 stream job be predicted from its y1 representative alone? (laptop, read-only)
For each y1 of plan.json: I(y1) = sum over the roots r (one per +- pair) of (r,y1)^2, and the SWAP rule searches a pair only when
I(y1) <= I(y2), so a low I(y1) should mean many searched pairs. Compared with the measured wall time of the v10 jobs of 016."""
import sys, os, json, statistics as st
S, PKG, LID = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
from fractions import Fraction as F
import frame_dfs_next as FD
plan = json.load(open(os.path.join(PKG, "data", "finishC", "stream", LID, "plan.json")))
gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % LID)))["gens"]
L = FD.lattice_data(gens, F(1)); G = L["G"]; Y = np.array(plan["y1_reps"], dtype=np.int64)
nrm = np.einsum("ij,jk,ik->i", Y, G, Y)
print("lattice %s: %d y1 reps; norms in the engine basis: %s" % (LID, len(Y), sorted(set(nrm.tolist()))[:6]))
if set(nrm.tolist()) != {7}:
    sys.exit("the plan's coordinates are not in the engine's basis: cannot use them directly")
RG = L["R"] @ G; I = ((Y @ RG.T) ** 2).sum(axis=1)
co = (L["S2"] @ G @ L["S2"].T)[0] % 4 == 0
hits = np.abs(Y @ (L["S2"] @ G).T) == 3
inv = [(int(I[i]),) + tuple(sorted((int(hits[i][co].sum()), int(hits[i][~co].sum())))) for i in range(len(Y))]
print("I(y1) values and counts:", dict(sorted({v: int((I == v).sum()) for v in set(I.tolist())}.items())))
print("is the list sorted by decreasing I?", bool((np.diff(I) <= 0).all()), "| by decreasing full invariant?", all(inv[i] >= inv[i + 1] for i in range(len(inv) - 1)))
if os.path.exists(os.path.join(S, "rows%s.json" % LID)):
    rows = {int(k): v for k, v in json.load(open(os.path.join(S, "rows%s.json" % LID))).items()}
    by = {}
    for k, (npairs, wall, srch, trap) in rows.items():
        by.setdefault(inv[k], []).append((wall / 60, npairs, k))
    print("%-16s %5s %9s %9s %9s %9s   k range" % ("invariant of y1", "jobs", "med min", "max min", "med pairs", "total h"))
    for key in sorted(by, reverse=True):
        v = by[key]
        print("%-16s %5d %9.1f %9.1f %9d %9.1f   %d-%d" % (str(key), len(v), st.median(x[0] for x in v), max(x[0] for x in v), st.median(x[1] for x in v), sum(x[0] for x in v) / 60, min(x[2] for x in v), max(x[2] for x in v)))
