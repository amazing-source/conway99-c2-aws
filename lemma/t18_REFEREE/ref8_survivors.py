# Referee check 8: the four 47-vertex survivors of B1 found by MY stage C (ref5_stageC.py on the control matchings).
#  (a) exact checks: sigma is an automorphism of the 47-vertex graph; all budgets; both matrices exactly PSD (flint charpoly
#      sign test); exact ranks of M1 = 9(3I-A)+J: total, odd part (23 x 23 orbit Gram 3I - A[R,R] + A[R,sR], exact determinant),
#      even part (24 generators).   Rank bound P2: odd <= 22 and even <= 22.
#  (b) stage D, first step (A18): every candidate neighbourhood Z = N(z) n (X_2 u W) of a vertex z of X_0 \ {p}:
#      |Z n (A_p u W)| = 2, |Z n X_2| >= 4, capacities (s in X_2: a_2(s) + 2 - [s in A_p]; w in W: a_2(w) - 2),
#      budgets on the 49 determined vertices Y47 u {z, sigma z}; then PSD on 49 (float; exact not needed for a count check).
import itertools, json, sys
import numpy as np
from flint import fmpz_mat, fmpq_mat, fmpz

mine = json.load(open("ref4_stageB_B1_0of1.json"))
reps = [tuple(r) for r in mine["reps"]]; DEF = [tuple(d) for d in mine["DEF"]]
ctl = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "ref5_stageC_B1_full_control.json"))

def exact_psd(M):
    """M integer symmetric: PSD iff the coefficients of charpoly alternate in sign appropriately:
    p(x) = prod (x - l_i); all l_i >= 0  iff  (-1)^(n-k) * coeff_k >= 0 for all k."""
    n = M.shape[0]
    cp = fmpz_mat(n, n, [int(v) for v in M.flatten()]).charpoly()
    co = [int(c) for c in cp.coeffs()]
    return all(((-1) ** (n - k)) * co[k] >= 0 for k in range(n + 1))
def qrank(M):
    return fmpq_mat(M.shape[0], M.shape[1], [int(v) for v in M.flatten()]).rank()

for ti, F, pk in ctl["survivors"]:
    s = reps[ti]
    A = np.unpackbits(np.array(pk, dtype=np.uint8))[:47 * 47].reshape(47, 47).astype(np.int64)
    assert (A == A.T).all() and not A.diagonal().any()
    sig = list(range(9, 18)) + list(range(0, 9)) + [18] + [19 + s[a] for a in range(18)] + [38, 37, 40, 39, 42, 41, 44, 43, 46, 45]
    sig = np.array(sig)
    assert (A[np.ix_(sig, sig)] == A).all(), "sigma is not an automorphism"
    C = A @ A; np.fill_diagonal(C, 0)
    assert not (C > 2 - A).any()
    Ap = [c for a in F for c in (a, s[a])]
    assert sorted(np.nonzero(A[18])[0].tolist()) == sorted([19 + c for c in Ap] + list(range(37, 47)))
    I = np.eye(47, dtype=np.int64); J = np.ones((47, 47), dtype=np.int64)
    M1 = 9 * (3 * I - A) + J; M2 = 11 * (4 * I + A) - 2 * J
    p1, p2 = exact_psd(M1), exact_psd(M2)
    R = [v for v in range(47) if v < sig[v]]
    assert len(R) == 23
    Godd = 3 * np.eye(23, dtype=np.int64) - A[np.ix_(R, R)] + A[np.ix_(R, sig[R])]
    det = int(fmpz_mat(23, 23, [int(v) for v in Godd.flatten()]).det())
    Dm = np.zeros((23, 47), dtype=np.int64); Dp = np.zeros((24, 47), dtype=np.int64)
    for t, v in enumerate(R):
        Dm[t, v] = 1; Dm[t, sig[v]] = -1; Dp[t, v] = 1; Dp[t, sig[v]] = 1
    Dp[23, 18] = 1
    assert (Dm @ M1 @ Dm.T == 18 * Godd).all()
    H = A[19:37, 19:37]; t_e = int(H.sum()) // 2
    a2W = [int(A[w, 19:37].sum()) for w in range(37, 47)]
    print(f"survivor matching {ti} F={tuple(F)}: t={t_e}; a_2 on W = {a2W}; M1 exactly PSD: {p1}; M2 exactly PSD: {p2}; "
          f"rank M1 = {qrank(M1)} of 47, odd part rank {qrank(Dm @ M1 @ Dm.T)} of 23 (det of odd orbit Gram = {det}), "
          f"even part rank {qrank(Dp @ M1 @ Dp.T)} of 24;  rank M2 = {qrank(M2)}, odd {qrank(Dm @ M2 @ Dm.T)}, even {qrank(Dp @ M2 @ Dp.T)}")
    # ---- stage D first step
    a2 = A[:, 19:37].sum(1)
    cap = {}
    for c in range(18): cap[19 + c] = int(a2[19 + c]) + 2 - (1 if c in Ap else 0)
    for w in range(37, 47): cap[w] = int(a2[w]) - 2
    NP = [19 + c for c in Ap] + list(range(37, 47))
    others = [19 + c for c in range(18) if c not in Ap]
    A49 = np.zeros((49, 49), dtype=np.int64); A49[:47, :47] = A
    found = {}; raw = 0
    def bud(M):
        C = M @ M; np.fill_diagonal(C, 0)
        return not (C > 2 - M).any()
    for u, v in itertools.combinations(NP, 2):
        Z0 = [u, v]
        M0 = A49.copy(); cov = dict.fromkeys(cap, 0); ok = True
        for q in Z0:
            M0[47, q] = M0[q, 47] = 1; M0[48, sig[q]] = M0[sig[q], 48] = 1
            cov[q] += 1; cov[int(sig[q])] += 1
        if any(cov[q] > cap[q] for q in cov) or not bud(M0): continue
        nx2 = sum(1 for q in Z0 if q < 37)
        def rec(i, M, cov, Z, nx2):
            global raw
            if i == len(others):
                if nx2 >= 4:
                    raw += 1
                    key = min(tuple(sorted(Z)), tuple(sorted(int(sig[q]) for q in Z)))
                    found[key] = M
                return
            rec(i + 1, M, cov, Z, nx2)
            q = others[i]
            if cov[q] + 1 <= cap[q] and cov[int(sig[q])] + 1 <= cap[int(sig[q])]:
                M2_ = M.copy()
                M2_[47, q] = M2_[q, 47] = 1; M2_[48, sig[q]] = M2_[sig[q], 48] = 1
                if bud(M2_):
                    cov2 = dict(cov); cov2[q] += 1; cov2[int(sig[q])] += 1
                    rec(i + 1, M2_, cov2, Z + [q], nx2 + 1)
        rec(0, M0, cov, Z0, nx2)
    from collections import Counter
    dist = Counter(sum(1 for q in key if q < 37) for key in found)
    print(f"   distribution of a_2(z) = |Z n X_2| over the unordered pairs: {dict(sorted(dist.items()))};  t = {t_e}, so "
          f"sum over the 4 orbits of (a_2(z) - 4) = t forces a_2(z) <= {4 + t_e}: pairs with a_2(z) <= 4 + t: "
          f"{sum(v for k, v in dist.items() if k <= 4 + t_e)}")
    npsd = 0; npsd48 = 0
    for key, M in found.items():
        Mf = M.astype(float)
        e1 = np.linalg.eigvalsh(9 * (3 * np.eye(49) - Mf) + 1.0)[0]
        e2 = np.linalg.eigvalsh(11 * (4 * np.eye(49) + Mf) - 2.0)[0]
        if e1 > -1e-7 and e2 > -1e-7: npsd += 1
        Mg = Mf[:48, :48]
        if np.linalg.eigvalsh(9 * (3 * np.eye(48) - Mg) + 1.0)[0] > -1e-7 and np.linalg.eigvalsh(11 * (4 * np.eye(48) + Mg) - 2.0)[0] > -1e-7: npsd48 += 1
    print(f"   stage D: oriented sets Z passing capacities + budgets on 49: {raw}; unordered mate pairs {{Z, sigma Z}}: {len(found)}; "
          f"of which PSD on 49: {npsd}; PSD already on the 48 vertices Y47 u {{z}}: {npsd48}")
