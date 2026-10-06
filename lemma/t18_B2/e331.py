# t18_B2 / e331.py -- INDEPENDENT re-computation of profile (3,3,1) (round 2: A10, A11, A12), written in the t18_B2
# session.  It shares no code with r2_hfirst.py / r2_stage2.py / r2_ext2.py and does not read types.json.
#
# Forced structure (REPORT.md, section E0; n_3 = 0):
#   (E-a) A_p = N(p) n X_2 = three mate pairs (U n V empty), each vertex with a_2 = 1: no X_2-neighbour but its mate;
#   (E-b) N(p) n X_0 = {z0, sigma z0}; z0 has no neighbour in S u A_p u W; N(z0) n X_2 = one vertex of each of the six
#         orbits of X_2 outside A_p, sigma z0 sees the other six;
#   (E-c) W = N(p) n X_1 = three mate pairs of distinct types {i,j}, i != j, x_i has 2 - f_i neighbours in W;
#         a vertex of W has no X_0-neighbour but p;
#   (E-d) the six other vertices z of X_0 (three orbits): no neighbour in S u {p, z0, sigma z0} u W, z not~ sigma z,
#         exactly 2 neighbours in A_p, a_2(z) >= 4, deg_G(z) = a_2(z) - 4 with G = A[these six];
#         need(s) = 2 for s in A_p, need(s) = a_2(s) + 1 for the other s of X_2 (neighbours among the six).
# Step 2': all (tau, F, H, orientation of z0) on Y1 = S u {p} u X_2 u {z0, sigma z0} (39 vertices), orbit by orbit.
# Step 3': the three other orbits of X_0 and G: Y = S u X_0 u X_2 (45 vertices).
# Vertex numbering: x_i = i, y_j = 9 + j, p = 18, X_2 vertex k = 19 + k, z0 = 37, sigma z0 = 38, then 39..44.
# Rejections are exact (budget, integer vector with negative quadratic form in Python integers, exact elimination).
# usage: python e331.py <s> <part> <nparts> <time limit>
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
NOPSD1 = os.environ.get("E_NOPSD1") == "1"       # cross-check mode: no PSD test on the 41-vertex sets (budgets only)
pc = int.bit_count
Bm = [[0] * 9 for _ in range(9)]
for e in EDGES[s].split():
    a, b = int(e[0]), int(e[1])
    Bm[a][b] = Bm[b][a] = 1
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if sum(Bm[a][c] * Bm[b][c] for c in range(9)) == 1]
td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
assert [tuple(d) for d in td["DEF"]] == DEF and len(DEF) == 18
REPS = td["reps"]
ST = {"tau": 0, "tau_done": 0, "F": 0, "F_base_ok": 0, "F_W_ok": 0, "H_nodes": 0, "Y1_survivors": 0, "tau_with_Y1": 0,
      "orbits_generated": 0, "orbits_count_ok": 0, "orbits_budget_ok": 0, "orbits_psd_ok": 0, "covers": 0, "G": 0,
      "Y_budget_ok": 0, "Y_kept": 0, "psd_cert": 0, "psd_exact_fallback": 0, "rej_budget_np": 0}
LAST = [0]


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


def to_np(rows, L):
    return np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)


def good(rows, L, psd=True):
    A = to_np(rows, L)
    n = len(L)
    C = A @ A
    np.fill_diagonal(C, 0)
    if (C > 2 - A).any():
        ST["rej_budget_np"] += 1; LAST[0] = 1
        return False
    LAST[0] = 2
    if not psd:
        return True
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * A + 1, 44 * I + 11 * A - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] > -1e-7:
            continue
        Ml = M.tolist()
        for sc in (10, 60, 500, 10 ** 4, 10 ** 6):
            x = [int(round(sc * float(v))) for v in V[:, 0]]
            y = [sum(r[j] * x[j] for j in range(n)) for r in Ml]
            if sum(x[i] * y[i] for i in range(n)) < 0:
                ST["psd_cert"] += 1
                return False
        ST["psd_exact_fallback"] += 1
        if not psd_exact(Ml):
            return False
    return True


def link(rows, u, v):
    rows[u] |= 1 << v; rows[v] |= 1 << u


def add_edge(rows, u, v):
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


Y1_ALL = []
Y_ALL = []


def step3(ti, F, rows39, tau, mem):
    """the three other orbits of X_0 (vertices 39..44) and G"""
    X2 = list(range(19, 37))
    Ap = [19 + k for k in mem]
    A = to_np(rows39, list(range(39)))
    cn = A @ A
    a2 = {v: pc((rows39[v] >> 19) & ((1 << 18) - 1)) for v in X2}
    t = sum(a2.values()) // 2
    need = {v: (2 if v in Ap else a2[v] + 1) for v in X2}
    assert sum(need.values()) == 18 + 2 * t
    sig = {19 + k: 19 + tau[k] for k in range(18)}
    maxdeg = min(4, t - 3)
    if maxdeg < 0:
        return
    def comp(u, v):
        return cn[u, v] + 1 <= 2 - A[u, v]
    plain = [v for v in X2 if v not in Ap]
    seen = set(); cands = []
    def record(Z):
        Zs = frozenset(Z); sZ = frozenset(sig[v] for v in Z)
        key = frozenset((Zs, sZ))
        if key in seen:
            return
        seen.add(key)
        ST["orbits_generated"] += 1
        use = {}
        for v in list(Zs) + list(sZ):
            use[v] = use.get(v, 0) + 1
        if any(use[v] > need[v] for v in use):
            return
        ST["orbits_count_ok"] += 1
        r = rows39[:] + [0, 0]
        for v in Zs:
            link(r, 39, v)
        for v in sZ:
            link(r, 40, v)
        if not good(r, list(range(41)), psd=False):
            return
        ST["orbits_budget_ok"] += 1
        if not NOPSD1 and not good(r, list(range(41))):
            return
        ST["orbits_psd_ok"] += 1
        cands.append((tuple(sorted(Zs)), tuple(sorted(sZ)), use))
    for u, v in itertools.combinations(Ap, 2):
        if not comp(u, v):
            continue
        pool = [x for x in plain if comp(x, u) and comp(x, v)]
        def ext(start, R):
            if len(R) >= 2:
                record([u, v] + R)
            if len(R) >= 2 + maxdeg:
                return
            for q in range(start, len(pool)):
                x = pool[q]
                if all(comp(x, y) for y in R):
                    ext(q + 1, R + [x])
        ext(0, [])
    covers = set()
    order = sorted(need, key=lambda v: (sum(1 for c in cands if v in c[2]), v))
    def cover(chosen, rem):
        if len(chosen) == 3:
            if not any(rem.values()):
                covers.add(frozenset(chosen))
            return
        tgt = next((v for v in order if rem[v] > 0), None)
        if tgt is None:
            return
        for ci, (Z, sZ, use) in enumerate(cands):
            if tgt not in use or ci in chosen or any(use[v] > rem[v] for v in use):
                continue
            rem2 = dict(rem)
            for v in use:
                rem2[v] -= use[v]
            cover(chosen + [ci], rem2)
    cover([], dict(need))
    ST["covers"] += len(covers)
    for cov in sorted(tuple(sorted(c)) for c in covers):
        deg = [len(cands[ci][0]) - 4 for ci in cov]
        base = rows39[:] + [0] * 6
        for q, ci in enumerate(cov):
            for v in cands[ci][0]:
                link(base, 39 + 2 * q, v)
            for v in cands[ci][1]:
                link(base, 40 + 2 * q, v)
        prs = [(0, 1), (0, 2), (1, 2)]
        for st in itertools.product(range(4), repeat=3):
            d = [0, 0, 0]
            for (q, r_), x in zip(prs, st):
                wgt = (x & 1) + (x >> 1)
                d[q] += wgt; d[r_] += wgt
            if d != deg:
                continue
            ST["G"] += 1
            r = base[:]
            for (q, r_), x in zip(prs, st):
                if x & 1:
                    link(r, 39 + 2 * q, 39 + 2 * r_); link(r, 40 + 2 * q, 40 + 2 * r_)
                if x & 2:
                    link(r, 39 + 2 * q, 40 + 2 * r_); link(r, 40 + 2 * q, 39 + 2 * r_)
            if not good(r, list(range(45)), psd=False):
                continue
            ST["Y_budget_ok"] += 1
            if not good(r, list(range(45))):
                continue
            ST["Y_kept"] += 1
            Y_ALL.append({"tau": ti, "F": list(F), "rows": r})


def do_tau(ti):
    tau = REPS[ti]
    orbs = [k for k in range(18) if k < tau[k]]
    base = [0] * 39
    for i in range(9):
        for j in range(9):
            if Bm[i][j]:
                link(base, i, 9 + j)
    for k in range(18):
        for i in DEF[k]:
            link(base, 19 + k, i)
        for j in DEF[tau[k]]:
            link(base, 19 + k, 9 + j)
    elig = [o for o in orbs if not (set(DEF[o]) & set(DEF[tau[o]]))]
    found = False
    for F in itertools.combinations(elig, 3):
        ST["F"] += 1
        mem = [k for o in F for k in (o, tau[o])]
        rows = base[:]
        for k in mem:
            link(rows, 18, 19 + k)
        for o in F:
            link(rows, 19 + o, 19 + tau[o])
        L0 = list(range(19)) + [19 + k for k in mem]
        if not good(rows, L0):
            continue
        ST["F_base_ok"] += 1
        f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
        if max(f) > 2:
            continue
        link(rows, 37, 18); link(rows, 38, 18); link(rows, 37, 38)
        # (E-c): some type solution for W must pass on S u N[p] (33 vertices; W temporarily at 39..44 of a longer list)
        defi = [2 - x for x in f]
        allp = [(i, j) for i in range(9) for j in range(i + 1, 9)]
        w_ok = False
        for ts in itertools.combinations(allp, 3):
            dg = [0] * 9
            for i, j in ts:
                dg[i] += 1; dg[j] += 1
            if dg != defi:
                continue
            r = rows[:] + [0] * 6
            for c, (i, j) in enumerate(ts):
                w, sw = 39 + 2 * c, 40 + 2 * c
                link(r, w, 18); link(r, sw, 18); link(r, w, sw)
                link(r, w, i); link(r, w, 9 + j); link(r, sw, j); link(r, sw, 9 + i)
            if good(r, L0 + [37, 38] + list(range(39, 45))):
                w_ok = True
                break
        if not w_ok:
            continue
        ST["F_W_ok"] += 1
        non = [o for o in orbs if o not in F]
        def rec(a, r, L):
            if a == 6:
                ST["Y1_survivors"] += 1
                Y1_ALL.append({"tau": ti, "F": list(F), "rows": r[:39]})
                step3(ti, F, r[:39], tau, mem)
                return True
            k1, k2 = non[a], tau[non[a]]
            La = L + [19 + k1, 19 + k2]
            got = False
            for (u, v) in (((k1, k2),) if a == 0 else ((k1, k2), (k2, k1))):       # z0 ~ u, sigma z0 ~ v
                r1 = r[:]
                if not (add_edge(r1, 37, 19 + u) and add_edge(r1, 38, 19 + v)):
                    continue
                def choose(b, r2):
                    nonlocal got
                    if b == a:
                        ST["H_nodes"] += 1
                        if good(r2, La):
                            if rec(a + 1, r2, La):
                                got = True
                        return
                    q1, q2 = non[b], tau[non[b]]
                    for st in range(4):
                        r3 = r2[:]
                        okk = True
                        if st & 1:
                            okk = okk and add_edge(r3, 19 + k1, 19 + q1) and add_edge(r3, 19 + k2, 19 + q2)
                        if okk and (st & 2):
                            okk = okk and add_edge(r3, 19 + k1, 19 + q2) and add_edge(r3, 19 + k2, 19 + q1)
                        if not okk:
                            continue
                        if any(pc((r3[19 + x] >> 19) & ((1 << 18) - 1)) > 4 for x in (k1, k2, q1, q2)):
                            continue
                        choose(b + 1, r3)
                choose(0, r1)
            return got
        if rec(0, rows, L0 + [37, 38]):
            found = True
    return found


timed_out = False
alive = []
for ti in range(len(REPS)):
    if ti % nparts != part:
        continue
    ST["tau"] += 1
    if time.time() - T0 > TL:
        timed_out = True
        break
    if do_tau(ti):
        alive.append(ti); ST["tau_with_Y1"] += 1
    ST["tau_done"] += 1
    if ST["tau_done"] % 50 == 0:
        print(f"  [{time.time() - T0:.0f}s] {ST}", flush=True)
print(f"e331 B{s} part {part}/{nparts}: timed_out {timed_out}, {time.time() - T0:.0f}s")
print("  totals:", ST)
print(f"  Y1 configurations (39 vertices): {len(Y1_ALL)} in matchings {alive};  Y configurations (45 vertices) kept: {len(Y_ALL)}")
json.dump({"s": s, "part": part, "nparts": nparts, "totals": ST, "timed_out": timed_out, "Y1": Y1_ALL, "Y": Y_ALL},
          open(os.path.join(HERE, f"e331_{s}_{part}of{nparts}{'_nopsd1' if NOPSD1 else ''}.json"), "w"))
