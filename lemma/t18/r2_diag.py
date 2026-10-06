# Diagnostic (floating point, exploratory only): where does the E_{-4} violation of a rejected Y-table sit ?
import json, os, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, sys.argv[1])))
res = json.load(open(os.path.join(here, "structures.json")))
si = int(d["name"].split("#")[1])
m = res[0]["survivors"][si]
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(x) for x in td["DEF"]]
np.set_printoptions(precision=2, suppress=True, linewidth=200)
ex = d["rejected_examples"][0]
tau, H, F = ex["tau"], ex["H"], ex["F"]
print("tau:", [(DEF[k], DEF[tau[k]]) for k in range(18) if k < tau[k]])
print("F:", F, " H edges:", [(k, l) for k in range(18) for l in range(k + 1, 18) if (H[k] >> l) & 1])


def block(Hmask, verts=None):
    n = 36
    A = np.zeros((n, n))
    for i in range(9):
        for j in range(9):
            if i != j and m[i][j] & 1:
                A[i, 9 + j] = A[9 + j, i] = 1
    for k in range(18):
        for i in DEF[k]:
            A[18 + k, i] = A[i, 18 + k] = 1
        for j in DEF[tau[k]]:
            A[18 + k, 9 + j] = A[9 + j, 18 + k] = 1
        for l in range(18):
            if (Hmask[k] >> l) & 1:
                A[18 + k, 18 + l] = 1
    return A


# sigma as a permutation of the 36 vertices
sig = list(range(9, 18)) + list(range(9)) + [18 + tau[k] for k in range(18)]
P = np.zeros((36, 36))
for v in range(36):
    P[v, sig[v]] = 1
for label, Hm in (("H = empty", [0] * 18), ("H = mates of F only", [(1 << tau[k]) if (k in F or tau[k] in F) else 0 for k in range(18)]),
                  ("H of the example", H)):
    A = block(Hm)
    M1 = 27 * np.eye(36) - 9 * A + 1
    w, V = np.linalg.eigh(M1)
    v = V[:, 0]
    par = float(v @ P @ v)
    print(f"{label}: min eig {w[0]:.4f}, second {w[1]:.4f}; sigma-parity of eigenvector {par:+.2f}")
    print("    eigenvector on S+ :", v[:9]); print("    on S- :", v[9:18]); print("    on X_2:", v[18:])
    # odd and even parts separately
    odd = (np.eye(36) - P) / 2; even = (np.eye(36) + P) / 2
    for nm, Q in (("odd", odd), ("even", even)):
        ww = np.linalg.eigvalsh(Q @ M1 @ Q)
        nz = ww[np.abs(ww) > 1e-9]
        print(f"    {nm} part: min non-zero eigenvalue {nz.min():.4f}")
