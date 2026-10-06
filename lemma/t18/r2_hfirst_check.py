# Cross-checks of r2_hfirst.py.
# (1) Same enumeration with the PSD test switched off (budgets only) on a few matchings: the pairs (tau, F) for which
#     r2_stage2.py found budget-valid Y-tables must reappear here with survivors (the Y-tables contain Y1).
# (2) For every rejected Y-table saved by r2_stage2.py, the sub-configuration Y1 = S u {p} u X_2 u {z_0, sigma z_0}
#     is rebuilt independently and its PSD status recomputed with exact rational elimination (latt.psd_exact).
# (3) psd_exact against integer certificates on the same matrices.
import json, os, sys, runpy
import numpy as np
from latt import psd_exact
from enum_S import neg_certificate
here = os.path.dirname(os.path.abspath(__file__))

# ---- (2), (3)
d = json.load(open(os.path.join(here, "r2_stage2_1_0of400.json")))
res = json.load(open(os.path.join(here, "structures.json")))
m = res[0]["survivors"][1]
td = json.load(open(os.path.join(here, "r2_tau_1.json")))
DEF = [tuple(x) for x in td["DEF"]]
for ex in d.get("rejected_examples", []):
    tau, Az, H, G, F = ex["tau"], ex["Az"], ex["H"], ex["G"], ex["F"]
    n = 45
    A = np.zeros((n, n), dtype=np.int64)
    def add(u, v):
        A[u, v] = 1; A[v, u] = 1
    for i in range(9):
        for j in range(9):
            if i != j and m[i][j] & 1:
                add(i, 9 + j)
    for k in range(18):
        for i in DEF[k]:
            add(27 + k, i)
        for j in DEF[tau[k]]:
            add(27 + k, 9 + j)
        for l in range(18):
            if (H[k] >> l) & 1:
                add(27 + k, 27 + l)
    for q in range(9):
        for k in range(18):
            if (Az[q] >> k) & 1:
                add(18 + q, 27 + k)
        for r in range(9):
            if (G[q] >> r) & 1:
                add(18 + q, 18 + r)
    # which X_0 vertices are p's neighbours (z_0, sigma z_0)
    zin = [q for q in range(1, 9) if A[18, 18 + q]]
    idx = list(range(18)) + [18] + list(range(27, 45)) + [18 + q for q in zin]
    out = []
    for nm, Mx in (("E-4", 27 * np.eye(n, dtype=np.int64) - 9 * A + 1), ("E3", 44 * np.eye(n, dtype=np.int64) + 11 * A - 2)):
        sub = Mx[np.ix_(idx, idx)]
        ex_psd = psd_exact(sub.tolist())[0]
        cert = neg_certificate(sub.tolist())
        out.append((nm, "exact PSD" if ex_psd else "exact NOT PSD", "certificate" if cert is not None else "no certificate",
                    round(float(np.linalg.eigvalsh(sub.astype(float))[0]), 4)))
        assert ex_psd == (cert is None) or abs(out[-1][3]) < 1e-6
    print("rejected Y-table, F =", F, " z_0 pair =", zin, " Y1 (39 vertices):", out)

# ---- (1)
print('(1) is run separately:  R2_NOPSD=1 python r2_hfirst.py 1 0 200 120  -> r2_hfirst_1_0of200_nopsd.json')
