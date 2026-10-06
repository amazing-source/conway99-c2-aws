# Sanity checks on example Y-tables saved by r2_stage2.py:
#  - rebuild Y independently, re-check the common-neighbour budgets;
#  - check the forced identity: u = 3*1_S - 1_{X_0} + 1_{X_2} is in the kernel of 9(3I-A)+J restricted to Y
#    (this must hold for every valid table, so it tests the construction, not the obstruction);
#  - report which of the two PSD matrices is violated, with an exact integer certificate, and on which sub-blocks.
import json, os, sys
import numpy as np
from enum_S import neg_certificate
here = os.path.dirname(os.path.abspath(__file__))
fn = sys.argv[1]
d = json.load(open(os.path.join(here, fn)))
res = json.load(open(os.path.join(here, "structures.json")))
si = int(d["name"].split("#")[1])
m = res[0]["survivors"][si]
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(x) for x in td["DEF"]]
for ex in (d.get("rejected_examples", []) + d["examples"])[:3]:
    tau, Az, H, G = ex["tau"], ex["Az"], ex["H"], ex["G"]
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
    C2 = A @ A
    bad = [(u, v) for u in range(n) for v in range(u + 1, n) if C2[u, v] > 2 - A[u, v]]
    u = np.array([3] * 18 + [-1] * 9 + [1] * 18, dtype=np.int64)
    M1 = 27 * np.eye(n, dtype=np.int64) - 9 * A + 1
    M2 = 44 * np.eye(n, dtype=np.int64) + 11 * A - 2
    print("example: F =", ex["F"], " sizes a_z =", [bin(a).count("1") for a in Az],
          " e(H) =", sum(bin(h).count("1") for h in H) // 2, " e(G) =", sum(bin(g).count("1") for g in G) // 2)
    print("   budget violations:", len(bad), "  M1 u == 0:", bool((M1 @ u == 0).all()))
    for nm, Mx in (("9(3I-A)+J", M1), ("11(4I+A)-2J", M2)):
        w = np.linalg.eigvalsh(Mx.astype(float))
        cert = neg_certificate(Mx.tolist())
        q = None if cert is None else int(sum(cert[a] * int(Mx[a, b]) * cert[b] for a in range(n) for b in range(n)))
        print(f"   {nm}: min eigenvalue (float) {w[0]:.4f}; exact certificate value v^T M v = {q}")
    # sub-blocks
    blocks = {"S u X_2": list(range(18)) + list(range(27, 45)), "S u X_0": list(range(27)),
              "X_0 u X_2": list(range(18, 45)), "S u X_2 u {p}": list(range(18)) + [18] + list(range(27, 45))}
    for nm, idx in blocks.items():
        r = []
        for Mx in (M1, M2):
            sub = Mx[np.ix_(idx, idx)]
            r.append(round(float(np.linalg.eigvalsh(sub.astype(float))[0]), 4))
        print(f"   block {nm}: min eigenvalues {r}")
