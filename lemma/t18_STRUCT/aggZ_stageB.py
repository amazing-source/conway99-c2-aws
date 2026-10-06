# Stage-B triples (tau, F, H) of profile (2,5,0): test with the AGGREGATE vertex "Z" = X_0 \ {p}.
# Y = S u {p} u X_2 (37 determined vertices).  In a real graph the 38 vectors  e_v (v in Y)  and  1_Z  have a
# completely determined Gram matrix for the forms 63 E_{-4} = 27I - 9A + J  and  77 E_3 = 44I + 11A - 2J :
#     |N(v) n Z| = 0 for v in S u {p},   = a_2(v) + 2 - [v ~ p] for v in X_2   (report A8),
#     1_Z^T A 1_Z = 2t (p is isolated in X_0), |Z| = 8,  t = e(X_2).
# Necessary: both augmented 38x38 matrices are positive semidefinite.
# A rejection is certified by an integer vector x with x^T M x < 0 (exact Python integers).
# usage: python aggZ_stageB.py <structure 0|1|2> <json files with a list of {tau,F,H} under key H / H_stageB / list>
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
T18 = os.path.join(os.path.dirname(HERE), "t18")
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
s = int(sys.argv[1])
B = np.zeros((9, 9), dtype=np.int64)
for e in EDGES[s].split():
    B[int(e[0]), int(e[1])] = B[int(e[1]), int(e[0])] = 1
C = B @ B
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if C[a, b] == 1]
td = json.load(open(os.path.join(T18, f"r2_tau_{s}.json")))
assert [tuple(d) for d in td["DEF"]] == DEF
reps = td["reps"]

def build(e):
    tau = reps[e["tau"]]; F = e["F"]; H = e["H"]
    n = 37
    A = np.zeros((n, n), dtype=np.int64)
    A[:9, 9:18] = B; A[9:18, :9] = B
    for k in range(18):
        for i in DEF[k]:
            A[i, 19 + k] = A[19 + k, i] = 1
        for j in DEF[tau[k]]:
            A[9 + j, 19 + k] = A[19 + k, 9 + j] = 1
        for l in range(18):
            if (H[k] >> l) & 1:
                A[19 + k, 19 + l] = 1
    mem = sorted(k for o in F for k in (o, tau[o]))
    for k in mem:
        A[18, 19 + k] = A[19 + k, 18] = 1
    assert (A == A.T).all() and not A.diagonal().any()
    for o in F:
        assert A[19 + o, 19 + tau[o]] == 1, "mate edge of A_p missing in H"
    return A, tau, mem

def exact_neg(M, x):
    Mi = [[int(v) for v in r] for r in M]
    xi = [int(v) for v in x]
    n = len(xi)
    return sum(xi[i] * Mi[i][j] * xi[j] for i in range(n) for j in range(n)) < 0

def certificate(M):
    w, V = np.linalg.eigh(M.astype(float))
    if w[0] > -1e-7:
        return None, w[0]
    for col in range(min(3, len(w))):
        if w[col] > -1e-7: break
        for scale in (6, 12, 30, 100, 1000, 10 ** 5):
            x = np.rint(scale * V[:, col]).astype(np.int64)
            if exact_neg(M, x):
                return [int(v) for v in x], w[0]
    return "AMBIGUOUS", w[0]

def augmented(A, mem):
    n = A.shape[0]
    a2 = A[19:37, 19:37].sum(axis=1)
    t = int(a2.sum()) // 2
    nZ = np.zeros(n, dtype=np.int64)
    for k in range(18):
        nZ[19 + k] = a2[k] + 2 - (1 if k in mem else 0)
    assert nZ.sum() == 32 + 2 * t
    I = np.eye(n, dtype=np.int64)
    out = []
    for (c0, c1, cj) in ((27, -9, 1), (44, 11, -2)):
        M = c0 * I + c1 * A + cj
        row = c1 * nZ + cj * 8
        zz = c0 * 8 + c1 * 2 * t + cj * 64
        Mx = np.zeros((n + 1, n + 1), dtype=np.int64)
        Mx[:n, :n] = M; Mx[n, :n] = row; Mx[:n, n] = row; Mx[n, n] = zz
        out.append((M, Mx))
    return t, out

tot = {"triples": 0, "plain_fail": 0, "agg_fail_m4": 0, "agg_fail_3": 0, "agg_fail_any": 0, "ambiguous": 0, "alive": 0}
by_t = {}
alive = []
seen = set()
for fn in sys.argv[2:]:
    d = json.load(open(fn))
    L = d if isinstance(d, list) else (d.get("H") or d.get("H_stageB") or d.get("survivors"))
    for e in L:
        key = (e["tau"], tuple(e["F"]), tuple(e["H"]))
        if key in seen: continue
        seen.add(key)
        A, tau, mem = build(e)
        t, mats = augmented(A, mem)
        tot["triples"] += 1
        bt = by_t.setdefault(t, [0, 0])
        bt[0] += 1
        dead = False
        for idx, (M, Mx) in enumerate(mats):
            c0, _ = certificate(M)
            if c0 is not None:
                tot["plain_fail"] += 1
            c, w0 = certificate(Mx)
            if c == "AMBIGUOUS":
                tot["ambiguous"] += 1
            elif c is not None:
                dead = True
                tot["agg_fail_m4" if idx == 0 else "agg_fail_3"] += 1
        if dead:
            tot["agg_fail_any"] += 1
        else:
            tot["alive"] += 1; bt[1] += 1
            alive.append({"tau": e["tau"], "F": e["F"], "H": e["H"], "t": t})
print("structure B%d:" % s, tot)
print("   by t (triples, alive after the aggregate test):", sorted(by_t.items()))
json.dump(alive, open(os.path.join(HERE, "aggZ_alive_B%d.json" % s), "w"))
