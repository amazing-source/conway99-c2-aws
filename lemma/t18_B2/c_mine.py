# t18_B2 / c_mine.py -- stage C (the ten X_1 neighbours of p) for profile (2,5,0), n_3 = 0.
# THIRD implementation, written in the t18_B2 session; it shares no code with r3_p250.py or r3_verify.py and does not
# read types.json.  Organisation (different from both): "single pairs first, then exact cover".
#
# Input: stage-B triples (tau, F, H) (field "H_stageB" of r3_p250 outputs or "H" of r3_verify B250 outputs) and the
# matching representatives r2_tau_<s>.json (stage 1, double-checked).  Graph B_s re-entered as an edge list.
# Numbering: x_i = i, y_j = 9 + j, p = 18, X_2 vertex k = 19 + k (N n P = DEF[k], N n Q = DEF[tau k]),
#            w_c = 37 + 2c of type (i_c ; j_c) (neighbours x_i, y_j), sigma w_c = 38 + 2c of type (j_c ; i_c).
# Forced facts used (REPORT.md C0; all re-derived there):
#   (C-a) N(p) = A_p u W, A_p = the 4 vertices of the two orbits of F; N(p) induces the 7 mate edges only;
#   (C-b) W = 5 mate pairs of types {i,j}, i != j, pairwise distinct, and x_i has exactly 2 - f_i neighbours in W
#         (f_i = number of vertices of A_p adjacent to x_i);
#   (C-c) K_c = N(w_c) n X_2 is disjoint from A_p, contains no mate pair, |K_c| >= 2, N(sigma w_c) n X_2 = tau K_c;
#   (C-d) every k of X_2 outside A_p has exactly req(k) = 2 - |N(k) n A_p| neighbours in W.
# So S u {p} u X_2 u W (47 vertices) is determined by (types, K_0..K_4), and so is every subset
# S u {p} u X_2 u (some mate pairs of W) with their K_c.
# Steps: C1 type solutions, tested on S u N[p] (33 vertices);
#        C2 for every type (i ; j): all K passing budgets + PSD on the 39 vertices S u {p} u X_2 u {w, sigma w};
#        C3 exact cover of req by one K per pair, with the 41-vertex test for every two pairs, then the 47-vertex test.
# Rejections are exact (count, budget, integer vector with x^T M x < 0 in Python integers, or exact elimination).
# usage: python c_mine.py <s> <part> <nparts> <time limit s> <json files with triples ...>
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1"); os.environ.setdefault("OMP_NUM_THREADS", "1")
import json, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
s = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3]); TL = float(sys.argv[4])
T0 = time.time()
# C_NOPSD=1 : budgets only at every level (does not terminate in practice: first triple > 200 s);
# C_NOPSD=41: PSD kept on 33 and 39 vertices, budgets only on 41 and 47 vertices.
# In both modes every budget-valid 47-vertex graph is classified: rank bound (rankbound.py) and PSD, separately.
NOPSD = os.environ.get("C_NOPSD") in ("1", "41")
PSD_LOW = os.environ.get("C_NOPSD") == "41"
if NOPSD:
    from rankbound import bareiss_det, rank_exact, odd_gram, even_part
pc = int.bit_count
Bm = [[0] * 9 for _ in range(9)]
for e in EDGES[s].split():
    a, b = int(e[0]), int(e[1])
    Bm[a][b] = Bm[b][a] = 1
assert all(sum(r) == 4 for r in Bm)
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if sum(Bm[a][c] * Bm[b][c] for c in range(9)) == 1]
td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
assert [tuple(d) for d in td["DEF"]] == DEF and len(DEF) == 18
REPS = td["reps"]
ST = {"triples": 0, "triples_done": 0, "type_solutions": 0, "type_solutions_ok33": 0, "pair_types_tested": 0,
      "K_budget_ok": 0, "K_psd_ok": 0, "ts_with_all_pairs_alive": 0, "cover_nodes": 0, "pair41_tests": 0,
      "pair41_ok": 0, "full47_tests": 0, "survivors": 0, "psd_cert": 0, "psd_exact_fallback": 0, "rej_budget_np": 0, "K_incremental_budget_missed": 0, "budget_valid_47": 0, "dead_by_rank_bound": 0, "dead_by_odd_rank": 0,
      "dead_by_even_rank": 0, "dead_by_psd": 0, "dead_by_psd_only": 0, "dead_by_rank_only": 0, "pair_types_dead_before_K": 0, "tauF_with_triples": 0}


def psd_exact(M):
    n = len(M)
    A = [[int(x) for x in r] for r in M]
    alive = list(range(n)); prev = 1
    while alive:
        piv = None
        for i in alive:
            if A[i][i] < 0:
                return False
            if A[i][i] > 0 and piv is None:
                piv = i
        if piv is None:
            return all(A[i][j] == 0 for i in alive for j in alive)
        alive.remove(piv)
        d = A[piv][piv]; Ap = A[piv]
        for i in alive:
            Ai = A[i]; aip = Ai[piv]
            for j in alive:
                Ai[j] = (d * Ai[j] - aip * Ap[j]) // prev
        prev = d
    return True


LAST = [0]          # reason of the last rejection by good(): 1 = budget, 2 = PSD


def to_np(rows, L):
    n = len(L)
    return np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)


def good(rows, L, force_psd=False):
    """budgets (integer matrix product) and PSD on the vertex list L; False only with an exact reason"""
    A = to_np(rows, L)
    n = len(L)
    C = A @ A
    np.fill_diagonal(C, 0)
    if (C > 2 - A).any():
        ST["rej_budget_np"] += 1
        LAST[0] = 1
        return False
    LAST[0] = 2
    if NOPSD and not force_psd:
        return True
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * A + 1, 44 * I + 11 * A - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] > -1e-7:
            continue
        Ml = M.tolist()
        found = False
        for sc in (10, 60, 500, 10 ** 4, 10 ** 6):
            x = [int(round(sc * float(v))) for v in V[:, 0]]
            y = [sum(r[j] * x[j] for j in range(n)) for r in Ml]
            if sum(x[i] * y[i] for i in range(n)) < 0:
                found = True; break
        if found:
            ST["psd_cert"] += 1
            return False
        ST["psd_exact_fallback"] += 1
        if not psd_exact(Ml):
            return False
    return True


def add_edge(rows, u, v):
    """adds u-v; returns False iff some pair now exceeds its common-neighbour budget (only affected pairs are looked at)"""
    rows[u] |= 1 << v; rows[v] |= 1 << u
    if pc(rows[u] & rows[v]) > 1:
        return False
    for a, b in ((u, v), (v, u)):
        m = rows[b] & ~(1 << a)
        while m:
            y = (m & -m).bit_length() - 1
            m &= m - 1
            if pc(rows[a] & rows[y]) > (1 if (rows[a] >> y) & 1 else 2):
                return False
    return True


def link(rows, u, v):
    rows[u] |= 1 << v; rows[v] |= 1 << u


TS_CACHE = {}


def do_triple(ti, F, H):
    tau = REPS[ti]
    assert all(tau[tau[k]] == k and tau[k] != k for k in range(18))
    rows = [0] * 47
    for i in range(9):
        for j in range(9):
            if Bm[i][j]:
                link(rows, i, 9 + j)
    for k in range(18):
        for i in DEF[k]:
            link(rows, 19 + k, i)
        for j in DEF[tau[k]]:
            link(rows, 19 + k, 9 + j)
    mem = sorted(k for o in F for k in (o, tau[o]))
    assert len(set(mem)) == 4
    for k in range(18):
        for l in range(18):
            if (H[k] >> l) & 1:
                assert (H[l] >> k) & 1 and k != l
                rows[19 + k] |= 1 << (19 + l)
    for k in range(18):                                              # H is sigma-invariant, mate edges exactly on A_p
        assert sum(1 << tau[l] for l in range(18) if (H[k] >> l) & 1) == H[tau[k]]
        assert ((H[k] >> tau[k]) & 1) == (1 if k in mem else 0)
    for k in mem:
        link(rows, 18, 19 + k)
    L37 = list(range(37))
    A = to_np(rows, L37); C = A @ A; np.fill_diagonal(C, 0)
    assert not (C > 2 - A).any(), "stage-B triple violates a budget"
    non = [k for k in range(18) if k not in mem]
    req = [0] * 18
    for k in non:
        req[k] = 2 - sum(1 for q in mem if (H[k] >> q) & 1)
        assert req[k] >= 0
    FL = sum(pc(H[k]) - 1 for k in mem)
    assert sum(req) == 28 - FL and FL % 2 == 0
    slack = 4 - FL // 2
    if slack < 0:
        return []
    f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
    if max(f) > 2:
        return []
    # ---- C1: type solutions
    defi = [2 - x for x in f]
    allp = [(i, j) for i in range(9) for j in range(i + 1, 9)]
    tsols = []
    def rec_ts(start, chosen):
        if len(chosen) == 5:
            if not any(defi):
                tsols.append(tuple(chosen))
            return
        for q in range(start, len(allp)):
            i, j = allp[q]
            if defi[i] and defi[j]:
                defi[i] -= 1; defi[j] -= 1
                chosen.append((i, j))
                rec_ts(q + 1, chosen)
                chosen.pop()
                defi[i] += 1; defi[j] += 1
    rec_ts(0, [])
    first_time = (ti, tuple(F)) not in TS_CACHE
    if first_time:
        ST["type_solutions"] += len(tsols); ST["tauF_with_triples"] += 1
    def put_pair(r, c, i, j):
        w, sw = 37 + 2 * c, 38 + 2 * c
        link(r, w, 18); link(r, sw, 18); link(r, w, sw)
        link(r, w, i); link(r, w, 9 + j); link(r, sw, j); link(r, sw, 9 + i)
    L19p = list(range(19)) + [19 + k for k in mem]
    if first_time:
        ok33 = []
        for ts in tsols:
            r = rows[:]
            for c, (i, j) in enumerate(ts):
                put_pair(r, c, i, j)
            if good(r, L19p + list(range(37, 47)), force_psd=PSD_LOW):
                ok33.append(ts)
        ST["type_solutions_ok33"] += len(ok33)
        TS_CACHE[(ti, tuple(F))] = ok33
    ok33 = TS_CACHE[(ti, tuple(F))]
    if not ok33:
        return []
    # ---- C2: single pairs
    orbs = [(k, tau[k]) for k in non if k < tau[k] and req[k] > 0]
    SP = {}
    for (i, j) in sorted(set(t for ts in ok33 for t in ts)):
        ST["pair_types_tested"] += 1
        r0 = rows[:]
        put_pair(r0, 0, i, j)
        A0 = to_np(r0, L37 + [37, 38]); C0 = A0 @ A0; np.fill_diagonal(C0, 0)
        if (C0 > 2 - A0).any():                                      # e.g. x_i, y_j already have two common neighbours in X_2
            ST["pair_types_dead_before_K"] += 1                      # (spanning subgraph of the true graph: budgets only)
            SP[(i, j)] = []
            continue
        res = []
        def rec(a, r, K):
            if a == len(orbs):
                if 2 <= len(K) <= 2 + slack:
                    ST["K_budget_ok"] += 1
                    if good(r, L37 + [37, 38], force_psd=PSD_LOW):
                        ST["K_psd_ok"] += 1
                        res.append(frozenset(K))
                    elif LAST[0] == 1:
                        ST["K_incremental_budget_missed"] += 1
                return
            if len(K) + (len(orbs) - a) < 2:
                return
            rec(a + 1, r, K)
            if len(K) >= 2 + slack:
                return
            k1, k2 = orbs[a]
            for x, y in ((k1, k2), (k2, k1)):                       # w ~ x and sigma w ~ y = tau x
                r2 = r[:]
                if add_edge(r2, 37, 19 + x) and add_edge(r2, 38, 19 + y):
                    rec(a + 1, r2, K + [x])
        rec(0, r0, [])
        SP[(i, j)] = res
    # ---- C3: exact cover
    surv = []
    memo41 = {}
    def pair41(t1, K1, t2, K2):
        key = (t1, K1, t2, K2) if (t1, sorted(K1)) <= (t2, sorted(K2)) else (t2, K2, t1, K1)
        if key not in memo41:
            ST["pair41_tests"] += 1
            r = rows[:]
            for c, (tt, KK) in enumerate(((key[0], key[1]), (key[2], key[3]))):
                put_pair(r, c, tt[0], tt[1])
                for k in KK:
                    link(r, 37 + 2 * c, 19 + k); link(r, 38 + 2 * c, 19 + tau[k])
            memo41[key] = good(r, L37 + [37, 38, 39, 40])
            if memo41[key]:
                ST["pair41_ok"] += 1
        return memo41[key]
    for ts in ok33:
        if any(not SP[t] for t in ts):
            continue
        ST["ts_with_all_pairs_alive"] += 1
        order = sorted(range(5), key=lambda c: len(SP[ts[c]]))
        def cov(a, chosen, rq):
            ST["cover_nodes"] += 1
            if a == 5:
                if any(rq):
                    return
                ST["full47_tests"] += 1
                r = rows[:]
                for c in range(5):
                    put_pair(r, c, ts[c][0], ts[c][1])
                    for k in chosen[c]:
                        link(r, 37 + 2 * c, 19 + k); link(r, 38 + 2 * c, 19 + tau[k])
                if good(r, list(range(47))):
                    if NOPSD:                                        # budget-valid on 47 vertices: classify
                        ST["budget_valid_47"] += 1
                        sig = [9 + i for i in range(9)] + list(range(9)) + [18] + [19 + tau[k] for k in range(18)]                               + [37 + (c ^ 1) for c in range(10)]
                        orb = list(range(9)) + [19 + k for k in range(18) if k < tau[k]] + [37 + 2 * c for c in range(5)]
                        det = bareiss_det(odd_gram(r, orb, sig))
                        erank = rank_exact(even_part(r, orb, sig, fixed=18))
                        psd_ok = good(r, list(range(47)), force_psd=True)
                        dead_rank = (det != 0) or (erank > 22)
                        ST["dead_by_odd_rank"] += det != 0
                        ST["dead_by_even_rank"] += erank > 22
                        ST["dead_by_rank_bound"] += dead_rank
                        ST["dead_by_psd"] += not psd_ok
                        ST["dead_by_psd_only"] += (not psd_ok) and not dead_rank
                        ST["dead_by_rank_only"] += dead_rank and psd_ok
                        if psd_ok and not dead_rank:
                            ST["survivors"] += 1
                            surv.append({"tau": ti, "F": list(F), "H": list(H), "types": [list(t) for t in ts], "rows": r})
                        return
                    ST["survivors"] += 1
                    surv.append({"tau": ti, "F": list(F), "H": list(H), "types": [list(t) for t in ts], "rows": r})
                return
            c = order[a]
            left = 5 - a - 1
            for K in SP[ts[c]]:
                if any(rq[k] < 1 or rq[tau[k]] < 1 for k in K):
                    continue
                rq2 = rq[:]
                for k in K:
                    rq2[k] -= 1; rq2[tau[k]] -= 1
                tot = sum(rq2)
                if tot < 4 * left or (left == 0 and tot != 0):
                    continue
                if all(pair41(ts[c], K, ts[c2], K2) for c2, K2 in chosen.items()):
                    chosen[c] = K
                    cov(a + 1, chosen, rq2)
                    del chosen[c]
        cov(0, {}, req[:])
    return surv


items = []
for fn in sys.argv[5:]:
    d = json.load(open(fn if os.path.isabs(fn) else os.path.join(HERE, fn)))
    assert not d["timed_out"], fn
    for e in d.get("H_stageB", d.get("H", [])):
        items.append((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
items = sorted(set(items))
TAGX = ""
if os.environ.get("C_TAUS"):                                         # restrict to some matchings (positive control on B1)
    keep = set(int(x) for x in os.environ["C_TAUS"].split(","))
    items = [it for it in items if it[0] in keep]
    TAGX = "_t" + os.environ["C_TAUS"].split(",")[0]
ST["triples"] = len(items)
mine = [it for q, it in enumerate(items) if q % nparts == part]
survivors = []; done = []; timed_out = False
for (ti, F, H) in mine:
    if time.time() - T0 > TL:
        timed_out = True
        break
    survivors += do_triple(ti, F, H)
    done.append([ti, list(F)])
    ST["triples_done"] += 1
    if ST["triples_done"] % 10 == 0:
        print(f"  [{time.time() - T0:.0f}s] {ST}", flush=True)
print(f"c_mine B{s} part {part}/{nparts}: {len(mine)} triples in this part, done {ST['triples_done']}, timed_out {timed_out}, "
      f"{time.time() - T0:.0f}s")
print("  totals:", ST)
print("  survivors on 47 vertices:", len(survivors))
json.dump({"s": s, "part": part, "nparts": nparts, "totals": ST, "timed_out": timed_out, "done": done,
           "survivors": survivors}, open(os.path.join(HERE, f"c_mine_{s}_{part}of{nparts}{TAGX}{('_nopsd' + os.environ['C_NOPSD']) if NOPSD else ''}.json"), "w"))
