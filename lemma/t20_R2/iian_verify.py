# T20 round 2, case IIa.0: INDEPENDENT verifier (imports nothing from r2c / eng* / cases; own model, own tests).
#
# Hand part used (report, case II): n_3 = 0; N(p) = {x_0, y_0, x_1, y_1} u W, W = five mate pairs w = (i ; k),
# sigma w = (k ; i), i != k words, the five unordered types {i, k} distinct, x_i (word) has exactly
# 2 - r_i neighbours in W (r_i = number of neighbours of x_i among x_0, y_0, x_1, y_1); no vertex of X_2 other than
# p... is adjacent to p; a vertex s of X_2 minus p has type (U ; V), |U| = |V| = 2, exactly 2 - r(s) neighbours in W
# (never two mates), at most 3 - q(s) neighbours in X_2 minus p (q(s) = number of its neighbours among
# x_2, x_3, y_2, y_3); a vertex w of W has at most 4 - q(w) neighbours in X_2 minus p; every deficient unit of S+
# is N(s) n S+ of exactly one s of X_2 minus p.
#
# step 1:  python iian_verify.py types              -> the type sets of N(p) passing budgets and PSD on S u N[p]
# step 2:  python iian_verify.py follow a b <dir> <tag>   -> for the type sets a..b-1 (indices in iia_w.json, which
#          step 1 compares with its own list): re-traverses the search tree of eng5.py.  The unit treated at each
#          node is read from the plan file (the choice of the unit is not part of the proof); all candidates of
#          that unit are regenerated and tested here; the number kept must equal the plan's.
# Exact rejections: a common-neighbour count, or an integer vector x with x^T M x < 0 in Python integers.
import sys, json, os, itertools, time
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rec = json.load(open(os.path.join(HERE, "structures_III_IIb_IIa.json")))["IIa"][0]
MM, INNER = rec["m"], set(rec["H"])
assert INNER == {0, 1}
PLUS = {i for i in range(10) for j in range(10) if i != j and MM[i][j] & 2}
assert PLUS == {2, 3}
P = 20
TOL = 1e-7


def support():
    A = np.zeros((21, 21), dtype=np.int64)
    for i in range(10):
        for j in range(10):
            if i == j:
                continue
            if MM[i][j] & 1:
                A[i, 10 + j] = A[10 + j, i] = 1
            if MM[i][j] & 2:
                A[i, j] = A[j, i] = 1
                A[10 + i, 10 + j] = A[10 + j, 10 + i] = 1
    for i in INNER:
        A[i, 10 + i] = A[10 + i, i] = 1
        A[P, i] = A[i, P] = 1
        A[P, 10 + i] = A[10 + i, P] = 1
    phi = np.array([1] * 10 + [-1] * 10 + [0])
    assert ((A @ phi)[:20] == -4 * phi[:20]).all()
    return A


A21 = support()


def budget_violation(A):
    """exact recount: some pair u != v with more than 2 - A[u,v] common neighbours"""
    C = A @ A
    X = C + A
    np.fill_diagonal(X, 0)
    return bool((X > 2).any())


def qform(M, x):
    return sum(x[a] * sum(M[a][b] * x[b] for b in range(len(x)) if x[b]) for a in range(len(x)) if x[a])


def exact_psd(Q):
    n = len(Q)
    B = [[Fraction(int(t)) for t in row] for row in Q]
    idx = list(range(n))
    while idx:
        if any(B[i][i] < 0 for i in idx):
            return False
        piv = next((i for i in idx if B[i][i] > 0), None)
        if piv is None:
            return all(B[i][j] == 0 for i in idx for j in idx)
        idx.remove(piv)
        for i in idx:
            f = B[i][piv] / B[piv][piv]
            if f:
                for j in idx:
                    B[i][j] -= f * B[piv][j]
    return True


NCERT = [0, 0]          # certificates found / exact eliminations


def psd_rejected(A, sig):
    """True if M1 = 9(3I-A)+J or M2 = 11(4I+A)-2J is exactly NOT positive semidefinite on this vertex set
    (integer certificate, checked with Python integers on a sigma-block; or exact elimination).  False = kept
    (floating-point decision)."""
    n = A.shape[0]
    reps = [v for v in range(n) if sig[v] > v]
    fixed = [v for v in range(n) if sig[v] == v]
    D = np.zeros((n, len(reps)), dtype=np.int64)
    E = np.zeros((n, len(fixed) + len(reps)), dtype=np.int64)
    for j, v in enumerate(fixed):
        E[v, j] = 1
    for j, v in enumerate(reps):
        D[v, j] = 1; D[sig[v], j] = -1
        E[v, len(fixed) + j] = 1; E[sig[v], len(fixed) + j] = 1
    I = np.eye(n, dtype=np.int64)
    M1 = 9 * (3 * I - A) + 1
    M2 = 11 * (4 * I + A) - 2
    for M, B in ((M1, D), (M2, D), (M1, E), (M2, E)):
        Q = B.T @ M @ B
        w, V = np.linalg.eigh(Q.astype(np.float64))
        if w[0] < -TOL:
            Ql = Q.tolist()
            v = V[:, 0]
            mx = float(np.abs(v).max())
            for sc in (2, 3, 6, 12, 30, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10):
                x = [int(round(float(t) * sc / mx)) for t in v]
                if any(x) and qform(Ql, x) < 0:
                    NCERT[0] += 1
                    return True
            if not exact_psd(Ql):
                NCERT[1] += 1
                return True
    return False


WORDS = [i for i in range(10) if i not in INNER]


def type_sets():
    need = {i: 2 - int(A21[i, 0] + A21[i, 10] + A21[i, 1] + A21[i, 11]) for i in WORDS}
    pairs = list(itertools.combinations(WORDS, 2))
    out = []
    for comb in itertools.combinations(pairs, 5):
        deg = {i: 0 for i in WORDS}
        for (i, k) in comb:
            deg[i] += 1; deg[k] += 1
        if deg == need:
            out.append(comb)
    return out


def base31(ts):
    A = np.zeros((31, 31), dtype=np.int64)
    A[:21, :21] = A21
    for t, (i, k) in enumerate(ts):
        w, sw = 21 + 2 * t, 22 + 2 * t
        for (u, v) in ((w, sw), (w, P), (sw, P), (w, i), (w, 10 + k), (sw, k), (sw, 10 + i)):
            A[u, v] = A[v, u] = 1
    return A


SIG31 = list(range(10, 20)) + list(range(10)) + [20] + [22, 21, 24, 23, 26, 25, 28, 27, 30, 29]


def units_of():
    u = {}
    for i in range(10):
        for j in range(i + 1, 10):
            c = int((A21[i] * A21[j]).sum())
            d = (1 if A21[i, j] else 2) - c
            assert d >= 0
            if d:
                u[(i, j)] = d
    assert sum(u.values()) == 20
    return u


def step_types():
    ts = type_sets()
    nb = npsd = 0
    good = []
    for comb in ts:
        A = base31(comb)
        if budget_violation(A):
            nb += 1
        elif psd_rejected(A, SIG31):
            npsd += 1
        else:
            good.append([list(t) for t in comb])
    print("type sets with the right degrees: %d; rejected by budgets %d, by PSD (exact) %d, kept %d" % (
        len(ts), nb, npsd, len(good)))
    ref = json.load(open(os.path.join(HERE, "iia_w.json")))
    same = sorted(map(lambda g: sorted(map(tuple, g)), good)) == sorted(map(lambda g: sorted(map(tuple, g)), ref))
    print("identical to the list of the first program (iia_w.json, %d sets): %s" % (len(ref), same))
    print("certificates: integer vector %d, exact elimination %d" % (NCERT[0], NCERT[1]))


def follow(wi, ts, plan_path):
    A0 = base31(ts)
    assert not budget_violation(A0)
    W = list(range(21, 31))
    capW = {w: 4 - int(A0[w, 2] + A0[w, 3] + A0[w, 12] + A0[w, 13]) for w in W}
    wopts = {0: [()], 1: [(w,) for w in W],
             2: [(a, b) for a in W for b in W if a < b and (a - 21) // 2 != (b - 21) // 2]}
    plan = iter(open(plan_path))
    stat = {"nodes": 0, "cands": 0, "budget": 0, "psd": 0, "kept": 0, "complete": 0, "cand_mismatch": 0}
    paircache = {}

    def row31(o):
        U, V, NW = o
        r = np.zeros(31, dtype=np.int64)
        for i in U:
            r[i] = 1
        for i in V:
            r[10 + i] = 1
        for w in NW:
            r[w] = 1
        return r

    def extend(A, sig, row):
        n = A.shape[0]
        B = np.zeros((n + 2, n + 2), dtype=np.int64)
        B[:n, :n] = A
        rs = row[np.array(sig)]
        B[n, :n] = row; B[:n, n] = row
        B[n + 1, :n] = rs; B[:n, n + 1] = rs
        return B, sig + [n + 1, n]

    def pair_budget_ok(o1, o2, pat):
        key = (o1, o2, pat)
        r = paircache.get(key)
        if r is None:
            B, sg = extend(A0, SIG31, row31(o1))
            row = np.zeros(33, dtype=np.int64)
            row[:31] = row31(o2)
            if pat & 1:
                row[31] = 1
            if pat & 2:
                row[32] = 1
            B2, _ = extend(B, sg, row)
            r = not budget_violation(B2)
            paircache[key] = r
        return r

    def dfs(A, sig, orbs, caps, degs, cntW, remaining):
        t = len(orbs)
        if t == 10:
            stat["complete"] += 1
            return
        pl = [int(v) for v in next(plan).split()]
        assert pl[0] == t, "plan out of step"
        U0 = (pl[1], pl[2])
        assert U0 in remaining
        stat["nodes"] += 1
        rem2 = dict(remaining)
        rem2[U0] -= 1
        if rem2[U0] == 0:
            del rem2[U0]
        cands = []
        for V in sorted(rem2):
            if V == U0:
                continue
            r = sum(1 for i in U0 if i in INNER) + sum(1 for i in V if i in INNER)
            q = sum(1 for i in U0 if i in PLUS) + sum(1 for i in V if i in PLUS)
            if r > 2 or q > 3:
                continue
            cap = 3 - q
            for NW in wopts[2 - r]:
                if any(cntW[w] >= capW[w] for w in NW) or any(cntW[SIG31[w]] >= capW[SIG31[w]] for w in NW):
                    continue
                onew = (U0, V, NW)
                allowed = []
                ok = True
                for i in range(t):
                    room = caps[i] - degs[i]
                    pats = [pat for pat in (0, 1, 2, 3)
                            if (pat & 1) + (pat >> 1) <= min(room, cap) and pair_budget_ok(orbs[i], onew, pat)]
                    if not pats:
                        ok = False
                        break
                    allowed.append(pats)
                if not ok:
                    continue
                for choice in itertools.product(*allowed):
                    used = sum((pat & 1) + (pat >> 1) for pat in choice)
                    if used <= cap:
                        cands.append((V, NW, cap, choice, used))
        stat["cands"] += len(cands)
        if len(cands) != pl[3]:
            stat["cand_mismatch"] += 1
        good = []
        n = A.shape[0]
        for (V, NW, cap, choice, used) in cands:
            row = np.zeros(n, dtype=np.int64)
            row[:31] = row31((U0, V, NW))
            for i, pat in enumerate(choice):
                if pat & 1:
                    row[31 + 2 * i] = 1
                if pat & 2:
                    row[32 + 2 * i] = 1
            B, sg = extend(A, sig, row)
            if budget_violation(B):
                stat["budget"] += 1
            elif psd_rejected(B, sg):
                stat["psd"] += 1
            else:
                good.append((V, NW, cap, choice, used, B, sg))
        assert len(good) == pl[4], "DISAGREEMENT with the plan at depth %d: kept %d, plan %d" % (t, len(good), pl[4])
        stat["kept"] += len(good)
        for (V, NW, cap, choice, used, B, sg) in good:
            rem3 = dict(remaining)
            for X in (U0, V):
                rem3[X] -= 1
                if rem3[X] == 0:
                    del rem3[X]
            c2 = dict(cntW)
            for w in NW:
                c2[w] += 1; c2[SIG31[w]] += 1
            d2 = [degs[i] + (pat & 1) + (pat >> 1) for i, pat in enumerate(choice)]
            dfs(B, sg, orbs + [(U0, V, NW)], caps + [cap], d2 + [used], c2, rem3)

    dfs(A0, list(SIG31), [], [], [], {w: 0 for w in W}, units_of())
    left = sum(1 for _ in plan)
    return stat, left


if sys.argv[1] == "types":
    step_types()
else:
    a, b, d, tag = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    ref = json.load(open(os.path.join(HERE, "iia_w.json")))
    tot = {}
    res = []
    for wi in range(a, min(b, len(ref))):
        ts = [tuple(t) for t in ref[wi]]
        t0 = time.process_time()
        st, left = follow(wi, ts, os.path.join(d, "%s_w%d_0of1.plan" % (tag, wi)))
        st["plan_lines_left"] = left
        st["wset"] = wi
        st["cpu"] = round(time.process_time() - t0, 1)
        res.append(st)
        print("WSET %d: nodes %d candidates %d rejected budgets %d PSD %d kept %d complete %d | plan lines left %d, "
              "candidate-count mismatches %d | cpu %.1f s" % (wi, st["nodes"], st["cands"], st["budget"], st["psd"],
                                                             st["kept"], st["complete"], left, st["cand_mismatch"], st["cpu"]))
        sys.stdout.flush()
        json.dump(res, open("iian_verify_%d_%d.json" % (a, b), "w"))
    print("TOTAL over the type sets %d..%d: nodes %d, candidates %d, budget %d, PSD %d, kept %d, complete %d" % (
        a, b - 1, sum(r["nodes"] for r in res), sum(r["cands"] for r in res), sum(r["budget"] for r in res),
        sum(r["psd"] for r in res), sum(r["kept"] for r in res), sum(r["complete"] for r in res)))
    print("certificates: integer vector %d, exact elimination %d" % (NCERT[0], NCERT[1]))
