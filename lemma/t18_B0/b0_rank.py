# RANK BOUND (coordinator, hand proof; re-derived in REPORT.md): 27I - 9A + J = 63 E_{-4} has rank 44 and its sigma-odd and
# sigma-even parts have rank 22 each (trace(sigma) = 1, trace(sigma A) = 14, trace(sigma J) = 99 give trace(sigma E_{-4}) = 0).
# So for a sigma-invariant completely determined vertex set Y:
#   rank of the odd part  (Gram of the vectors e_x - e_{sigma x}, one per orbit != {p})          <= 22,
#   rank of the even part (Gram of the vectors e_x + e_{sigma x}, plus e_p if p is in Y)          <= 22.
# Likewise 44I + 11A - 2J = 77 E_3 (rank 54 = 27 + 27): odd part <= 27, even part <= 27.
# Exact ranks by rational elimination.  This file applies the bound to the tables on 45 vertices S u X_0 u X_2 left by the
# X_0-first route (22 orbits + p: the even part of 63 E_{-4} is 23 x 23 and must be singular).
import json, glob, itertools, os
from fractions import Fraction
import numpy as np

EDGES0 = "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78"


def rank_exact(M):
    A = [[Fraction(int(x)) for x in row] for row in M]
    n = len(A); r = 0
    for c in range(n):
        piv = next((i for i in range(r, n) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(r + 1, n):
            if A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def parts(A, sig):
    """exact ranks of the sigma-odd and sigma-even parts of 27I-9A+J and 44I+11A-2J on the vertex set of A"""
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    orbs = [(v, int(sig[v])) for v in range(n) if v < sig[v]]
    fixed = [v for v in range(n) if sig[v] == v]
    O = np.zeros((len(orbs), n), dtype=np.int64); E = np.zeros((len(orbs) + len(fixed), n), dtype=np.int64)
    for q, (u, v) in enumerate(orbs):
        O[q, u] = 1; O[q, v] = -1; E[q, u] = 1; E[q, v] = 1
    for q, v in enumerate(fixed):
        E[len(orbs) + q, v] = 1
    out = {}
    for name, M in (("E-4", 27 * I - 9 * A + 1), ("E3", 44 * I + 11 * A - 2)):
        out[name] = {"odd_dim": len(orbs), "odd_rank": rank_exact((O @ M @ O.T).tolist()),
                     "even_dim": E.shape[0], "even_rank": rank_exact((E @ M @ E.T).tolist())}
    return out


def violates(res):
    return (res["E-4"]["odd_rank"] > 22 or res["E-4"]["even_rank"] > 22 or res["E3"]["odd_rank"] > 27 or res["E3"]["even_rank"] > 27)


if __name__ == "__main__":
    from b0_x0_check import exact_psd_int
    B = np.zeros((9, 9), dtype=np.int64)
    for ed in EDGES0.split():
        B[int(ed[0]), int(ed[1])] = B[int(ed[1]), int(ed[0])] = 1
    td = json.load(open("r2_tau_0.json")); DEF = td["DEF"]; reps = td["reps"]
    R = json.load(open("b0_stageB_reps.json"))
    pairs = list(itertools.combinations(range(4), 2))
    n_tab = n_dead = n_psd = 0
    for f in sorted(glob.glob("b0_x0_done_*.jsonl")):
        for l in open(f):
            if not l.strip():
                continue
            d = json.loads(l)
            for tab in d["alive"]:
                e = R[d["idx"]]; tau = reps[e["tau"]]
                A = np.zeros((45, 45), dtype=np.int64)
                A[:9, 9:18] = B; A[9:18, :9] = B
                for k in range(18):
                    for i in DEF[k]:
                        A[19 + k, i] = A[i, 19 + k] = 1
                    for j in DEF[tau[k]]:
                        A[19 + k, 9 + j] = A[9 + j, 19 + k] = 1
                    for l2 in range(18):
                        if (e["H"][k] >> l2) & 1:
                            A[19 + k, 19 + l2] = 1
                for o in e["F"]:
                    for k in (o, tau[o]):
                        A[18, 19 + k] = A[19 + k, 18] = 1
                for q, Z in enumerate(tab["Z"]):
                    for k in Z:
                        A[37 + 2 * q, 19 + k] = A[19 + k, 37 + 2 * q] = 1
                        A[38 + 2 * q, 19 + tau[k]] = A[19 + tau[k], 38 + 2 * q] = 1
                for (q, r), x in zip(pairs, tab["G"]):
                    if x & 1:
                        for u, v in ((37 + 2 * q, 37 + 2 * r), (38 + 2 * q, 38 + 2 * r)):
                            A[u, v] = A[v, u] = 1
                    if x & 2:
                        for u, v in ((37 + 2 * q, 38 + 2 * r), (38 + 2 * q, 37 + 2 * r)):
                            A[u, v] = A[v, u] = 1
                sig = list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)]
                for q in range(4):
                    sig += [38 + 2 * q, 37 + 2 * q]
                sig = np.array(sig)
                assert (A == A.T).all() and (A[np.ix_(sig, sig)] == A).all()
                C = A @ A; np.fill_diagonal(C, 0)
                budgets = not (C > 2 - A).any()
                I = np.eye(45, dtype=np.int64)
                psd = exact_psd_int((27 * I - 9 * A + 1).tolist()) and exact_psd_int((44 * I + 11 * A - 2).tolist())
                res = parts(A, sig)
                dead = violates(res)
                n_tab += 1; n_dead += dead; n_psd += psd
                print(f"idx {d['idx']} (matching #{d['tau']}, F = {d['F']}), a_2 on X_0 minus p: {[len(Z) for Z in tab['Z']]}: budgets {budgets}, "
                      f"both matrices exactly PSD: {psd}; ranks {res}; violates the rank bound: {dead}")
    print(f"tables on 45 vertices left by the X_0-first route: {n_tab}; exactly PSD with all budgets: {n_psd}; killed by the rank bound: {n_dead}")
