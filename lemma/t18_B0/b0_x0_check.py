# B0, profile (2,5,0): INDEPENDENT brute-force re-computation of the X_0-first route (b0_x0.py) on a sample of triples.
# No code shared with b0_x0.py.  Differences:
#   X1  all 2^18 subsets of X_2 are tested (no backtracking);
#   X2  the two matrices are DECIDED exactly (fraction-free integer elimination), not only searched for a certificate;
#   X3  exact covers by plain increasing-index recursion, WITHOUT the two shortcuts of b0_x0.py
#       ("at most one full orbit of X_0 in N(s)", "two orbits share at most 2 neighbours": both are implied by the
#       budgets on the 45 vertices, so the numbers of tables passing the budgets must coincide);
#   X4  G from its own table;   X5  budgets by matrix product, PSD decided exactly.
# Compared with the log of b0_x0.py: x1_Z, x2_pairs_budget, x2_pairs_psd, x5_budget, x5_psd.
# usage: python b0_x0_check.py <tag> <idx> <idx> ...        (idx = position in b0_stageB_reps.json)
import json, os, sys, itertools, time, random
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES0 = "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78"
T0 = time.time()


def exact_psd_int(M):
    """exact decision (Python integers, Bareiss elimination with symmetric pivoting): is the symmetric integer matrix PSD?"""
    A = [[int(x) for x in row] for row in M]
    active = list(range(len(A)))
    prev = 1
    while active:
        piv = None
        for i in active:
            if A[i][i] < 0:
                return False
            if piv is None and A[i][i] > 0:
                piv = i
        if piv is None:
            return all(A[i][j] == 0 for i in active for j in active)
        d = A[piv][piv]
        rest = [i for i in active if i != piv]
        rp = A[piv]
        for i in rest:
            Ai = A[i]; f = Ai[piv]
            for j in rest:
                Ai[j] = (Ai[j] * d - f * rp[j]) // prev          # exact division (Bareiss); signs = signs of the Schur complement
        prev = d
        active = rest
    return True


def exact_psd_frac(M):
    A = [[Fraction(int(x)) for x in row] for row in M]
    active = list(range(len(A)))
    while active:
        piv = None
        for i in active:
            if A[i][i] < 0:
                return False
            if piv is None and A[i][i] > 0:
                piv = i
        if piv is None:
            return all(A[i][j] == 0 for i in active for j in active)
        d = A[piv][piv]
        rest = [i for i in active if i != piv]
        for i in rest:
            f = A[i][piv] / d
            for j in rest:
                A[i][j] -= f * A[piv][j]
        active = rest
    return True


def selftest():
    rng = random.Random(5)
    n_psd = 0
    for trial in range(300):
        n = rng.randint(2, 9)
        r = rng.randint(1, n)
        Gm = [[rng.randint(-3, 3) for _ in range(r)] for _ in range(n)]
        M = [[sum(Gm[i][k] * Gm[j][k] for k in range(r)) for j in range(n)] for i in range(n)]
        if trial % 2:
            i = rng.randrange(n); j = rng.randrange(n)
            M[i][j] -= 1
            if i != j:
                M[j][i] -= 1
        a, b = exact_psd_int(M), exact_psd_frac(M)
        assert a == b, M
        w = np.linalg.eigvalsh(np.array(M, dtype=float))
        if w[0] < -1e-6:
            assert not a
        if w[0] > 1e-6:
            assert a
        n_psd += a
    return n_psd


def psd_exact(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    return exact_psd_int((27 * I - 9 * A + 1).tolist()) and exact_psd_int((44 * I + 11 * A - 2).tolist())


def budgets_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


GT = {}
PR = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
for code in range(4 ** 6):
    stt = [(code >> (2 * q)) & 3 for q in range(6)]
    dg = [0, 0, 0, 0]
    for (a, b), x in zip(PR, stt):
        wgt = (x & 1) + (x >> 1)
        dg[a] += wgt; dg[b] += wgt
    GT.setdefault(tuple(dg), []).append(stt)


def check(idx, e, reps, DEF, B):
    tau = reps[e["tau"]]
    H = e["H"]
    A = np.zeros((37, 37), dtype=np.int64)
    for i in range(9):
        for j in range(9):
            if B[i][j]:
                A[i, 9 + j] = A[9 + j, i] = 1
    for k in range(18):
        U, V = DEF[k], DEF[tau[k]]
        for i in U:
            A[19 + k, i] = A[i, 19 + k] = 1
        for j in V:
            A[19 + k, 9 + j] = A[9 + j, 19 + k] = 1
        for l in range(18):
            if (H[k] >> l) & 1:
                A[19 + k, 19 + l] = A[19 + l, 19 + k] = 1
    Ap = sorted(k for o in e["F"] for k in (o, tau[o]))
    for k in Ap:
        A[18, 19 + k] = A[19 + k, 18] = 1
    sig = np.array(list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)])
    assert (A[np.ix_(sig, sig)] == A).all() and budgets_ok(A)
    a2 = A[19:, 19:].sum(1)
    t = int(a2.sum()) // 2
    need = np.array([int(a2[k]) + 2 - (1 if k in Ap else 0) for k in range(18)])
    amax = min(8, 4 + t)
    cn = A @ A
    badm = ((cn[19:, 19:] + A[19:, 19:]) >= 2).astype(np.int16)
    np.fill_diagonal(badm, 0)
    masks = np.arange(1 << 18, dtype=np.int64)
    PL = ((masks[:, None] >> np.arange(18)) & 1).astype(np.int16)
    size = PL.sum(1)
    cnt = PL @ A[19:, :].astype(np.int16)
    member = np.zeros((1 << 18, 37), dtype=np.int16)
    member[:, 19:] = PL
    good = (size >= 4) & (size <= amax) & (PL[:, Ap].sum(1) <= 2) & (cnt <= 2 - member).all(1)
    good &= ((PL @ badm) * PL).sum(1) == 0
    del cnt, member
    Zs = [tuple(k for k in range(18) if (int(mk) >> k) & 1) for mk in np.flatnonzero(good)]
    Zset = set(Zs)
    res = {"idx": idx, "t": t, "x1_Z": len(Zs), "x2_pairs_budget": 0, "x2_pairs_psd_exact": 0, "covers_no_shortcut": 0,
           "G_no_shortcut": 0, "x5_budget": 0, "x5_psd_exact": 0}
    cands = []
    for Z in Zs:
        sZ = tuple(sorted(tau[k] for k in Z))
        if sZ < Z or sZ not in Zset:
            continue
        use = np.zeros(18, dtype=np.int64)
        for k in Z:
            use[k] += 1
        for k in sZ:
            use[k] += 1
        if (use > need).any():
            continue
        A2 = np.zeros((39, 39), dtype=np.int64)
        A2[:37, :37] = A
        A2[37, [19 + k for k in Z]] = 1; A2[38, [19 + k for k in sZ]] = 1
        A2[:37, 37] = A2[37, :37]; A2[:37, 38] = A2[38, :37]
        if not budgets_ok(A2):
            continue
        res["x2_pairs_budget"] += 1
        if psd_exact(A2):
            res["x2_pairs_psd_exact"] += 1
            cands.append((Z, sZ, use))
    n = len(cands)
    uses = [c[2] for c in cands]
    covers = []
    def rec(start, chosen, rem):
        if len(chosen) == 4:
            if not rem.any():
                covers.append(tuple(chosen))
            return
        left = 4 - len(chosen)
        tot = int(rem.sum())
        if tot < 8 * left or tot > 16 * left:
            return
        for ci in range(start, n - left + 1):
            if (uses[ci] <= rem).all():
                rec(ci + 1, chosen + [ci], rem - uses[ci])
    rec(0, [], need.copy())
    res["covers_no_shortcut"] = len(covers)
    for cov in covers:
        base = np.zeros((45, 45), dtype=np.int64)
        base[:37, :37] = A
        for q, ci in enumerate(cov):
            Z, sZ, _ = cands[ci]
            for k in Z:
                base[37 + 2 * q, 19 + k] = base[19 + k, 37 + 2 * q] = 1
            for k in sZ:
                base[38 + 2 * q, 19 + k] = base[19 + k, 38 + 2 * q] = 1
        deg = tuple(len(cands[ci][0]) - 4 for ci in cov)
        for stt in GT.get(deg, []):
            res["G_no_shortcut"] += 1
            A5 = base.copy()
            for (a, b), x in zip(PR, stt):
                if x & 1:
                    A5[37 + 2 * a, 37 + 2 * b] = A5[37 + 2 * b, 37 + 2 * a] = 1
                    A5[38 + 2 * a, 38 + 2 * b] = A5[38 + 2 * b, 38 + 2 * a] = 1
                if x & 2:
                    A5[37 + 2 * a, 38 + 2 * b] = A5[38 + 2 * b, 37 + 2 * a] = 1
                    A5[38 + 2 * a, 37 + 2 * b] = A5[37 + 2 * b, 38 + 2 * a] = 1
            if not budgets_ok(A5):
                continue
            res["x5_budget"] += 1
            if psd_exact(A5):
                res["x5_psd_exact"] += 1
    return res


if __name__ == "__main__":
    tag = sys.argv[1]
    idxs = [int(x) for x in sys.argv[2:]]
    print("self-test of the exact PSD decision (300 random matrices, integer vs rational elimination): passed,",
          selftest(), "PSD cases", flush=True)
    B = [[0] * 9 for _ in range(9)]
    for ed in EDGES0.split():
        B[int(ed[0])][int(ed[1])] = B[int(ed[1])][int(ed[0])] = 1
    td = json.load(open(os.path.join(HERE, "r2_tau_0.json")))
    DEF = [tuple(d) for d in td["DEF"]]; reps = td["reps"]
    assert DEF == [(a, b) for a in range(9) for b in range(a + 1, 9) if B[a][b]]       # deficient pairs = edges of K3 x K3
    R = json.load(open(os.path.join(HERE, "b0_stageB_reps.json")))
    logged = {}
    for fn in os.listdir(HERE):
        if fn.startswith("b0_x0_done_") and fn.endswith(".jsonl"):
            for line in open(os.path.join(HERE, fn)):
                if line.strip():
                    d = json.loads(line); logged[d["idx"]] = d
    out = []; n_same = 0
    for idx in idxs:
        res = check(idx, R[idx], reps, DEF, B)
        lg = logged.get(idx)
        same = None
        if lg is not None:
            s = lg["stats"]
            same = (s["x1_Z"] == res["x1_Z"] and s["x2_pairs_budget"] == res["x2_pairs_budget"] and
                    s["x2_pairs_psd"] == res["x2_pairs_psd_exact"] and s["x5_budget"] == res["x5_budget"] and
                    s["x5_psd"] == res["x5_psd_exact"] and len(lg["alive"]) == res["x5_psd_exact"])
            n_same += bool(same)
        res["agrees_with_b0_x0"] = same
        out.append(res)
        print(f"[{time.time() - T0:.0f}s] {res}", flush=True)
    print(f"checked {len(out)} triples; agreement with the log of b0_x0.py on {n_same}; "
          f"tables on 45 vertices exactly PSD: {sum(r['x5_psd_exact'] for r in out)}")
    json.dump(out, open(os.path.join(HERE, f"b0_x0_check_{tag}.json"), "w"))
