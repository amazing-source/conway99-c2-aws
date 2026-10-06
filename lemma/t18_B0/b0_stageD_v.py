# B0, profile (2,5,0): INDEPENDENT check of the first step of stage D (the "X_0 step").
# It shares no code with r4_stageD.py.  Different algorithm: no backtracking; all subsets are enumerated by brute force
# (91 pairs of N(p) x 2^14 subsets of X_2 \ A_p), budgets by integer matrix products, PSD decided EXACTLY (rational
# elimination), with an integer certificate x (x^T M x < 0) for every rejection.
#
# Input: stage-C survivors (graphs on the 47 vertices S u {p} u X_2 u W; numbering: x_i = i, y_i = 9+i, p = 18,
#        X_2 = 19..36, W = 37..46 with mates 37+2c, 38+2c).
# A vertex z of X_0 \ {p} (8 such vertices must exist: |X_0| = 9) satisfies, by hand (T18_REPORT A8, A14):
#   no neighbour in S u {p};  z not adjacent to sigma z;  a_2(z) >= 4;  exactly 2 neighbours in N(p) = A_p u W.
# So with Z = N(z) n (X_2 u W), the graph on the 47 vertices + z + sigma z is completely determined by Z
# (N(sigma z) = sigma Z).  We list every Z passing the common-neighbour budgets on 48 vertices, then every unordered
# pair {Z, sigma Z} passing them on 49 vertices, then test the two matrices 9(3I-A)+J and 11(4I+A)-2J on the 49 vertices.
# If no pair survives, the configuration on 47 vertices cannot be completed (X_0 \ {p} would be empty).
# The additional filters of r4_stageD.py (use <= need, a_2(z) <= 4 + t) are applied only to produce a comparable count.
# usage: python b0_stageD_v.py <out tag> <survivor file (.json with "survivors" or .jsonl of stage C logs)> ...
import json, os, sys, itertools, time
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES0 = "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78"
T0 = time.time()


def exact_psd(M):
    """exact decision: is the symmetric integer matrix M positive semidefinite?  (rational Schur complements)"""
    n = len(M)
    A = [[Fraction(int(x)) for x in row] for row in M]
    active = list(range(n))
    while active:
        piv = None
        for i in active:
            if A[i][i] < 0:
                return False
            if piv is None and A[i][i] > 0:
                piv = i
        if piv is None:                       # zero diagonal: PSD iff the block is zero
            return all(A[i][j] == 0 for i in active for j in active)
        d = A[piv][piv]
        rest = [i for i in active if i != piv]
        rowp = A[piv]
        for i in rest:
            if A[i][piv] != 0:
                f = A[i][piv] / d
                Ai = A[i]
                for j in rest:
                    if rowp[j] != 0:
                        Ai[j] -= f * rowp[j]
        active = rest
    return True


def neg_certificate(M):
    """integer x with x^T M x < 0 (checked with Python integers), or None"""
    w, V = np.linalg.eigh(M.astype(np.float64))
    Mo = [[int(v) for v in row] for row in M]
    n = len(Mo)
    for col in range(min(2, n)):
        if w[col] > -1e-9:
            break
        for sc in (10, 60, 500, 10 ** 4, 10 ** 6):
            x = [int(round(sc * float(t))) for t in V[:, col]]
            q = sum(x[i] * Mo[i][j] * x[j] for i in range(n) for j in range(n))
            if q < 0:
                return x
    return None


def psd_status(A):
    """returns ('psd', None) or ('neg', (matrix index, certificate or None))  -- always an exact decision"""
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    for mi, M in enumerate((27 * I - 9 * A + 1, 44 * I + 11 * A - 2)):
        x = neg_certificate(M)
        if x is not None:
            return "neg", (mi, x)
        if not exact_psd(M.tolist()):
            return "neg", (mi, None)
    return "psd", None


def budgets_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


def check_survivor(e, label, out):
    rows = e["rows"]
    A = np.array([[(rows[u] >> v) & 1 for v in range(47)] for u in range(47)], dtype=np.int64)
    # ---- independent structural checks of the input
    assert (A == A.T).all() and not A.diagonal().any()
    B = np.zeros((9, 9), dtype=np.int64)
    for ed in EDGES0.split():
        B[int(ed[0]), int(ed[1])] = B[int(ed[1]), int(ed[0])] = 1
    assert (A[:9, 9:18] == B).all() and not A[:9, :9].any() and not A[9:18, 9:18].any() and not A[18, :18].any()
    typ = [(tuple(np.flatnonzero(A[v, :9])), tuple(np.flatnonzero(A[v, 9:18]))) for v in range(19, 47)]
    assert all(len(t[0]) == 2 and len(t[1]) == 2 for t in typ[:18]) and all(len(t[0]) == 1 and len(t[1]) == 1 for t in typ[18:])
    sig = list(range(9, 18)) + list(range(9)) + [18]
    for k in range(18):
        mates = [l for l in range(18) if typ[l] == (typ[k][1], typ[k][0])]
        assert len(mates) == 1 and mates[0] != k
        sig.append(19 + mates[0])
    for c in range(5):
        sig += [38 + 2 * c, 37 + 2 * c]
        assert typ[18 + 2 * c] == (typ[19 + 2 * c][1], typ[19 + 2 * c][0]) and A[37 + 2 * c, 38 + 2 * c]
    sig = np.array(sig)
    assert (A[np.ix_(sig, sig)] == A).all(), "not sigma-invariant"
    assert budgets_ok(A), "input violates a budget"
    st0, _ = psd_status(A)
    Ap = [v for v in range(19, 37) if A[18, v]]
    assert len(Ap) == 4 and all(A[18, v] for v in range(37, 47)) and A[18].sum() == 14
    a2 = A[:, 19:37].sum(1)
    t = int(a2[19:37].sum()) // 2
    need = {v: int(a2[v]) + 2 - (1 if v in Ap else 0) for v in range(19, 37)}
    need.update({v: int(a2[v]) - 2 for v in range(37, 47)})
    special = Ap + list(range(37, 47))
    plain = [v for v in range(19, 37) if v not in Ap]
    cn = A @ A
    badm = ((cn + A) >= 2)                       # u, v cannot both be neighbours of a new vertex
    np.fill_diagonal(badm, False)
    badm = badm.astype(np.int64)
    masks = np.arange(1 << 14)
    PL = ((masks[:, None] >> np.arange(14)) & 1).astype(np.int64)
    cnt_plain = PL @ A[plain, :]
    size_plain = PL.sum(1)
    ok_plain = ((PL @ badm[np.ix_(plain, plain)]) * PL).sum(1) == 0
    member0 = np.zeros((1 << 14, 47), dtype=np.int64)
    member0[:, plain] = PL
    Zs = []
    for s1, s2 in itertools.combinations(special, 2):
        if badm[s1, s2]:
            continue
        nx2 = size_plain + (1 if s1 < 37 else 0) + (1 if s2 < 37 else 0)
        cnt = cnt_plain + A[s1] + A[s2]
        member = member0.copy()
        member[:, s1] = 1; member[:, s2] = 1
        good = ok_plain & (nx2 >= 4) & (cnt <= 2 - member).all(1)
        good &= (PL @ badm[plain, s1] == 0) & (PL @ badm[plain, s2] == 0)
        for mk in np.flatnonzero(good):
            Zs.append(tuple(sorted([plain[q] for q in range(14) if (mk >> q) & 1] + [s1, s2])))
    Zset = set(Zs)
    assert len(Zset) == len(Zs)
    st = {"t": t, "input_psd_exact": st0, "Z_48_budget_ok": len(Zs), "pairs_49_budget_ok": 0, "pairs_49_budget_ok_and_need": 0,
          "pairs_49_psd_ok": 0, "pairs_49_psd_ok_and_need": 0, "rejected_with_certificate": 0, "rejected_exact_only": 0}
    seen = set(); alive = []
    for Z in Zs:
        sZ = tuple(sorted(int(sig[v]) for v in Z))
        key = (Z, sZ) if Z <= sZ else (sZ, Z)
        if key in seen:
            continue
        seen.add(key)
        if sZ not in Zset:                         # sigma z would violate a budget on 48 vertices
            continue
        A2 = np.zeros((49, 49), dtype=np.int64)
        A2[:47, :47] = A
        for v in Z:
            A2[47, v] = A2[v, 47] = 1
        for v in sZ:
            A2[48, v] = A2[v, 48] = 1
        if not budgets_ok(A2):
            continue
        st["pairs_49_budget_ok"] += 1
        use = {}
        for v in Z + sZ:
            use[v] = use.get(v, 0) + 1
        nd = all(use[v] <= need[v] for v in use) and sum(1 for v in Z if v < 37) <= 4 + t
        st["pairs_49_budget_ok_and_need"] += nd
        res, cert = psd_status(A2)
        if res == "psd":
            st["pairs_49_psd_ok"] += 1
            st["pairs_49_psd_ok_and_need"] += nd
            alive.append({"Z": [int(v) for v in Z], "sZ": [int(v) for v in sZ], "need_ok": bool(nd)})
        elif cert[1] is not None:
            st["rejected_with_certificate"] += 1
        else:
            st["rejected_exact_only"] += 1
    print(f"{label}: matching #{e['tau']}, F = {e['F']}: {st}   [{time.time() - T0:.0f}s]", flush=True)
    out.append({"tau": e["tau"], "F": e["F"], "types": e.get("types"), "rows": rows, "stats": st, "alive": alive})
    return st


if __name__ == "__main__":
    tag = sys.argv[1]
    survivors = []
    for fn in sys.argv[2:]:
        path = os.path.join(HERE, fn)
        if fn.endswith(".jsonl"):
            for line in open(path):
                if line.strip():
                    survivors += json.loads(line)["survivors"]
        else:
            survivors += json.load(open(path))["survivors"]
    uniq = {}
    for e in survivors:
        uniq.setdefault(tuple(e["rows"]), e)
    out = []
    tot_alive = 0
    for n_, e in enumerate(uniq.values()):
        st = check_survivor(e, f"survivor {n_ + 1}/{len(uniq)}", out)
        tot_alive += st["pairs_49_psd_ok"]
    print(f"independent stage-D check: {len(uniq)} configurations on 47 vertices; total number of pairs (z, sigma z) alive on "
          f"49 vertices: {tot_alive}; configurations with no possible pair: {sum(1 for o in out if not o['alive'])}")
    json.dump(out, open(os.path.join(HERE, f"b0_stageD_v_{tag}.json"), "w"))
