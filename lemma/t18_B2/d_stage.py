# t18_B2 / d_stage.py -- stage D ("X_0 stage") for profile (2,5,0), n_3 = 0.  SECOND, INDEPENDENT implementation
# (written in the t18_B2 session without reading r4_verifyD.py; it shares no code with r4_stageD.py; numpy + Python ints).
#
# Input : stage-C survivors of r3_p250.py = graphs on S u {p} u X_2 u W (47 vertices, field "rows", bit v of rows[u]).
#         Numbering: x_i = i, y_j = 9 + j, p = 18, X_2 = 19..36, W = 37..46.
# What is rebuilt from the graph itself (nothing is taken from the matching file): the support graph B_s, sigma
# (i <-> 9 + i on the support; on X_2 and on W: the unique vertex with the swapped support neighbourhood), A_p = N(p) n X_2.
#
# Added : the 8 vertices of X_0 \ {p} = 4 sigma-orbits {z, sigma z}.  Forced facts (REPORT.md, section D0):
#   (D-a) z has no neighbour in S, z is not adjacent to p, z is not adjacent to sigma z;
#   (D-b) |N(z) n (A_p u W)| = 2                      (the two common neighbours of z and p lie in N(p) = A_p u W);
#   (D-c) a_2(z) = |N(z) n X_2| >= 4, deg_{A[X_0]}(z) = a_2(z) - 4 <= min(t, 6), all of it inside X_0 \ {p};
#   (D-d) every s in X_2 has exactly need(s) = a_2(s) + 2 - [s in A_p] neighbours in X_0 \ {p};
#         every w in W has exactly need(w) = a_2(w) - 2.
# So S u X_0 u X_2 u W (55 vertices) is completely determined by the four sets Z_q = N(z_q) n (X_2 u W) and by
# G = A[X_0 \ {p}] (sigma-invariant, no edge inside an orbit).
#
# Steps: D1 all orbits {Z, sigma Z} (cliques of the "may share the neighbour z" graph), count filter use <= need,
#           then budgets and PSD on the 49 determined vertices;
#        D2 exact covers of need by 4 orbits;   D3 all G with the prescribed degrees;   D4 budgets + PSD on 55 vertices.
# A rejection is exact: a count, a pair of vertices with too many common neighbours, an integer vector x with
# x^T M x < 0 (Python integers), or an exact fraction-free elimination.  "kept" is never a claim of semidefiniteness,
# except for the final survivors, which are decided exactly.
# Environment: D_NOPSD1=1 skips the PSD test in D1 (cross-check: everything is then decided on 55 vertices).
# usage: python d_stage.py <s> <tag> <json file with a "survivors" list> [more files]
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
NOPSD1 = os.environ.get("D_NOPSD1") == "1"
T0 = time.time()
CERTS = []


def support_matrix(s):
    M = np.zeros((18, 18), dtype=np.int64)
    for e in EDGES[s].split():
        a, b = int(e[0]), int(e[1])
        M[a, 9 + b] = M[9 + b, a] = 1
        M[b, 9 + a] = M[9 + a, b] = 1
    return M


def budget_violation(A):
    """a pair (u, v) with more than 2 - A_uv common neighbours inside the vertex set, or None"""
    C = A @ A
    np.fill_diagonal(C, 0)
    bad = np.argwhere(C > 2 - A)
    return None if len(bad) == 0 else (int(bad[0][0]), int(bad[0][1]))


def psd_exact(M):
    """exact decision for a symmetric integer matrix (fraction-free elimination, symmetric pivoting).  (is_psd, rank)"""
    n = len(M)
    A = [[int(x) for x in r] for r in M]
    alive = list(range(n))
    prev = 1
    rank = 0
    while alive:
        piv = None
        for i in alive:
            if A[i][i] < 0:
                return False, rank
            if A[i][i] > 0 and piv is None:
                piv = i
        if piv is None:
            for i in alive:
                for j in alive:
                    if A[i][j] != 0:
                        return False, rank
            return True, rank
        rank += 1
        alive.remove(piv)
        d = A[piv][piv]
        Ap = A[piv]
        for i in alive:
            Ai = A[i]
            aip = Ai[piv]
            for j in alive:
                Ai[j] = (d * Ai[j] - aip * Ap[j]) // prev          # exact (Sylvester), sign of the Schur complement kept
        prev = d
    return True, rank


def matrices(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    return (27 * I - 9 * A + 1, 44 * I + 11 * A - 2)


def psd_rejected(A, stats):
    """True iff one of 9(3I-A)+J, 11(4I+A)-2J is certified NOT positive semidefinite (exactly)"""
    for mi, M in enumerate(matrices(A)):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] > -1e-7:
            continue
        Ml = [[int(x) for x in r] for r in M]
        n = len(Ml)
        for col in range(min(2, n)):
            if w[col] > -1e-7:
                break
            for sc in (10, 60, 500, 10 ** 4, 10 ** 6):
                x = [int(round(sc * float(v))) for v in V[:, col]]
                q = sum(x[i] * sum(Ml[i][j] * x[j] for j in range(n)) for i in range(n))
                if q < 0:
                    stats["psd_cert"] += 1
                    if len(CERTS) < 30000:
                        CERTS.append({"n": n, "rows": [int(sum(1 << b for b in range(n) if A[u, b])) for u in range(n)],
                                      "m": mi, "x": x})
                    return True
        ok, _ = psd_exact(Ml)                                       # float says negative but no vector found: decide exactly
        stats["psd_exact_fallback"] += 1
        if not ok:
            return True
    return False


def analyse(s, e, label):
    rows = e["rows"]
    A = np.array([[(rows[u] >> v) & 1 for v in range(47)] for u in range(47)], dtype=np.int64)
    assert (A == A.T).all() and not A.diagonal().any()
    assert (A[:18, :18] == support_matrix(s)).all(), "support graph"
    X2 = list(range(19, 37)); W = list(range(37, 47))
    assert not A[18, :18].any()
    assert all(A[18, w] for w in W)
    Ap = [v for v in X2 if A[18, v]]
    assert len(Ap) == 4
    # ---- sigma, from the graph
    sig = [9 + i for i in range(9)] + list(range(9)) + [18] + [None] * 28
    nb = lambda v: frozenset(u for u in range(18) if A[v, u])
    where = {}
    for v in X2 + W:
        key = (v >= 37, nb(v))
        assert key not in where
        where[key] = v
    for v in X2 + W:
        assert len(nb(v)) == (2 if v >= 37 else 4)
        sig[v] = where[(v >= 37, frozenset(sig[u] for u in nb(v)))]
    assert all(sig[sig[v]] == v for v in range(47)) and all(sig[v] != v for v in range(47) if v != 18)
    assert (A[np.ix_(sig, sig)] == A).all(), "sigma is not an automorphism of the 47-vertex graph"
    assert all(A[v, sig[v]] == (1 if A[18, v] else 0) for v in X2 + W)
    assert budget_violation(A) is None
    a2 = {v: int(A[v, 19:37].sum()) for v in X2 + W}
    t = sum(a2[v] for v in X2) // 2
    need = {v: a2[v] + 2 - (1 if v in Ap else 0) for v in X2}
    need.update({w: a2[w] - 2 for w in W})
    assert all(x >= 0 for x in need.values())
    assert sum(need[v] for v in X2) == 32 + 2 * t and sum(need[v] for v in Ap + W) == 16
    stats = {"t": t, "orbits_generated": 0, "orbits_count_ok": 0, "orbits_budget_ok": 0, "orbits_psd_ok": 0,
             "covers": 0, "G": 0, "full_budget_ok": 0, "full_psd_kept": 0, "psd_cert": 0, "psd_exact_fallback": 0}
    cn = A @ A
    def comp(u, v):
        return cn[u, v] + 1 <= 2 - A[u, v]
    spec = [v for v in Ap + W if need[v] > 0]
    plain = [v for v in X2 if v not in Ap and need[v] > 0]
    maxdeg = min(t, 6)
    seen = set()
    cands = []
    def record(Z):
        Zs = frozenset(Z)
        sZ = frozenset(sig[v] for v in Z)
        key = frozenset((Zs, sZ))
        if key in seen:
            return
        seen.add(key)
        stats["orbits_generated"] += 1
        use = {}
        for v in list(Zs) + list(sZ):
            use[v] = use.get(v, 0) + 1
        if any(use[v] > need[v] for v in use):
            return
        stats["orbits_count_ok"] += 1
        A49 = np.zeros((49, 49), dtype=np.int64)
        A49[:47, :47] = A
        for v in Zs:
            A49[47, v] = A49[v, 47] = 1
        for v in sZ:
            A49[48, v] = A49[v, 48] = 1
        if budget_violation(A49) is not None:
            return
        stats["orbits_budget_ok"] += 1
        if not NOPSD1 and psd_rejected(A49, stats):
            return
        stats["orbits_psd_ok"] += 1
        cands.append((tuple(sorted(Zs)), tuple(sorted(sZ)), use))
    for u, v in itertools.combinations(spec, 2):
        if not comp(u, v):
            continue
        nA = (1 if u in Ap else 0) + (1 if v in Ap else 0)
        pool = [x for x in plain if comp(x, u) and comp(x, v)]
        def ext(start, R):
            if len(R) + nA >= 4:
                record([u, v] + R)
            if len(R) + nA >= 4 + maxdeg:
                return
            for q in range(start, len(pool)):
                x = pool[q]
                if all(comp(x, y) for y in R):
                    ext(q + 1, R + [x])
        ext(0, [])
    # ---- D2: exact covers of need by 4 distinct orbits
    order = sorted(need, key=lambda v: (sum(1 for c in cands if v in c[2]), v))
    covers = set()
    def cover(chosen, rem):
        if len(chosen) == 4:
            if not any(rem.values()):
                covers.add(frozenset(chosen))
            return
        tgt = next((v for v in order if rem[v] > 0), None)
        if tgt is None:
            return
        for ci, (Z, sZ, use) in enumerate(cands):
            if tgt not in use or ci in chosen:
                continue
            if any(use[v] > rem[v] for v in use):
                continue
            rem2 = dict(rem)
            for v in use:
                rem2[v] -= use[v]
            cover(chosen + [ci], rem2)
    cover([], dict(need))
    stats["covers"] = len(covers)
    survivors = []
    for cov in sorted(tuple(sorted(c)) for c in covers):
        deg = [sum(1 for v in cands[ci][0] if v < 37) - 4 for ci in cov]
        assert sum(deg) == t
        base = np.zeros((55, 55), dtype=np.int64)
        base[:47, :47] = A
        for q, ci in enumerate(cov):
            for v in cands[ci][0]:
                base[47 + 2 * q, v] = base[v, 47 + 2 * q] = 1
            for v in cands[ci][1]:
                base[48 + 2 * q, v] = base[v, 48 + 2 * q] = 1
        pairs = list(itertools.combinations(range(4), 2))
        for st in itertools.product(range(4), repeat=6):
            d = [0, 0, 0, 0]
            for (q, r), x in zip(pairs, st):
                wgt = (x & 1) + (x >> 1)
                d[q] += wgt; d[r] += wgt
            if d != deg:
                continue
            stats["G"] += 1
            A55 = base.copy()
            for (q, r), x in zip(pairs, st):
                if x & 1:                                             # z_q ~ z_r and sigma z_q ~ sigma z_r
                    A55[47 + 2 * q, 47 + 2 * r] = A55[47 + 2 * r, 47 + 2 * q] = 1
                    A55[48 + 2 * q, 48 + 2 * r] = A55[48 + 2 * r, 48 + 2 * q] = 1
                if x & 2:                                             # z_q ~ sigma z_r and sigma z_q ~ z_r
                    A55[47 + 2 * q, 48 + 2 * r] = A55[48 + 2 * r, 47 + 2 * q] = 1
                    A55[48 + 2 * q, 47 + 2 * r] = A55[47 + 2 * r, 48 + 2 * q] = 1
            if budget_violation(A55) is not None:
                continue
            stats["full_budget_ok"] += 1
            if psd_rejected(A55, stats):
                continue
            stats["full_psd_kept"] += 1
            ex = [psd_exact(M.tolist()) for M in matrices(A55)]
            survivors.append({"tau": e.get("tau"), "F": e.get("F"), "types": e.get("types"),
                              "exact_psd": [[bool(a), int(b)] for a, b in ex],
                              "rows": [int(sum(1 << b for b in range(55) if A55[u, b])) for u in range(55)]})
    print(f"{label}: matching #{e.get('tau')}, F = {e.get('F')}, A_p = {Ap}: {stats}   [{time.time() - T0:.0f}s]", flush=True)
    return stats, survivors, [(c[0], c[1]) for c in cands]


if __name__ == "__main__":
    s = int(sys.argv[1]); tag = sys.argv[2]
    seen = set(); out_stats = []; out_surv = []
    for fn in sys.argv[3:]:
        d = json.load(open(fn if os.path.isabs(fn) else os.path.join(HERE, fn)))
        for e in d["survivors"]:
            key = tuple(e["rows"])
            if key in seen:
                continue
            seen.add(key)
            st, sv, cands = analyse(s, e, f"config {len(seen)}")
            out_stats.append({"tau": e.get("tau"), "F": e.get("F"), "stats": st, "orbit_candidates": cands})
            out_surv += sv
    print(f"d_stage (NOPSD1={NOPSD1}) B{s}: {len(seen)} configurations on 47 vertices examined, "
          f"{len(out_surv)} configurations on 55 vertices left; PSD certificates saved {len(CERTS)}; {time.time() - T0:.0f}s")
    json.dump({"s": s, "nopsd1": NOPSD1, "stats": out_stats, "survivors": out_surv},
              open(os.path.join(HERE, f"d_stage_{tag}.json"), "w"))
    with open(os.path.join(HERE, f"d_stage_cert_{tag}.jsonl"), "w") as f:
        for c in CERTS:
            f.write(json.dumps(c, separators=(",", ":")) + "\n")
