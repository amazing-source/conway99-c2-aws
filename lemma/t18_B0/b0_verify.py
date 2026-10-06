# Round 3.  INDEPENDENT VERIFIER.  It imports nothing from the other scripts of this folder (numpy only) and re-enters the
# three graphs B0, B1, B2 as explicit edge lists.  Graphs are numpy integer matrices; common-neighbour budgets are recounted
# by integer matrix products; a PSD rejection is accepted only with an integer vector x such that x^T M x < 0 (exact).
#
# Modes
#   stage1 <s>                      re-enumerates the matchings of the deficient pairs with a different algorithm, counts the
#                                   orbits under Aut(B), and checks the representatives stored in r2_tau_<s>.json
#   certs <file.jsonl> ...          re-checks every saved PSD certificate (n, rows, m, x): symmetric 0/1 matrix, zero diagonal,
#                                   the first 18 vertices carry the support graph of some B_s, and x^T M x < 0 exactly
#   B250 <s> <part> <nparts> <tl>   profile (2,5,0): all (tau, F, H) on S u {p} u X_2 (37 vertices), orbits added in the
#                                   REVERSE order of r3_p250.py, no pair prefilter               -> r3v_B250_<s>_<part>of<n>.json
#   C250 <s> <part> <nparts> <tl>   profile (2,5,0): W added in the DUAL order (X_2 orbit by X_2 orbit: which vertices of W
#                                   does it see), starting from the verifier's own B250 output   -> r3v_C250_<s>_<part>of<n>.json
#   compareB <s> <enumerator json files ...>   compares the (tau, F, H) sets of r3_p250.py (stage B) and of B250
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
AMBIG = [0]
T0 = time.time()


def Bmat(s):
    M = np.zeros((9, 9), dtype=np.int64)
    for e in EDGES[s].split():
        a, b = int(e[0]), int(e[1])
        M[a, b] = M[b, a] = 1
    assert (M.sum(0) == 4).all()
    return M


def budgets_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


def psd_violation(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * A + 1, 44 * I + 11 * A - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -1e-6:
            Mo = M.astype(object)
            for sc in (12, 50, 400, 10 ** 4, 10 ** 6):
                x = np.array([int(round(sc * float(t))) for t in V[:, 0]], dtype=object)
                if int(x @ (Mo @ x)) < 0:
                    return True
            AMBIG[0] += 1
    return False


def ok(A, idx):
    sub = A[np.ix_(idx, idx)]
    return budgets_ok(sub) and not psd_violation(sub)


def support(B, n):
    A = np.zeros((n, n), dtype=np.int64)
    for i in range(9):
        for j in range(9):
            if B[i, j]:
                A[i, 9 + j] = A[9 + j, i] = 1
    return A


def deficient_pairs(B):
    C = B @ B
    return [(a, b) for a in range(9) for b in range(a + 1, 9) if C[a, b] == 1]


def single_type_ok(B, U, V, inner):
    """vertex z seeing U in P and V in Q, its mate seeing V in P and U in Q; inner = (z in N(p))"""
    if inner and set(U) & set(V):
        return False
    A = support(B, 21)
    for i in U:
        A[19, i] = A[i, 19] = 1; A[20, 9 + i] = A[9 + i, 20] = 1
    for j in V:
        A[19, 9 + j] = A[9 + j, 19] = 1; A[20, j] = A[j, 20] = 1
    if inner:
        for u, v in ((19, 20), (18, 19), (18, 20)):
            A[u, v] = A[v, u] = 1
    return ok(A, list(range(21)))


def automorphisms(B):
    res = []
    perm = [-1] * 9
    used = [False] * 9
    def rec(i):
        if i == 9:
            res.append(tuple(perm)); return
        for t in range(9):
            if not used[t] and all(B[i, k] == B[t, perm[k]] for k in range(i)):
                perm[i] = t; used[t] = True
                rec(i + 1)
                used[t] = False; perm[i] = -1
    rec(0)
    return res


def stage1(s):
    B = Bmat(s)
    DEF = deficient_pairs(B)
    n = len(DEF)
    assert n == 18
    adm = [[False] * n for _ in range(n)]
    nadm = 0
    for a in range(n):
        for b in range(a + 1, n):
            U, V = DEF[a], DEF[b]
            if len(set(U) & set(V)) > 1:
                continue
            sub = B[np.ix_(U, V)]
            if (sub.sum(0) > 1).any() or (sub.sum(1) > 1).any():
                continue
            if single_type_ok(B, U, V, False) or single_type_ok(B, U, V, True):
                adm[a][b] = adm[b][a] = True; nadm += 1
    cap = 2 - B
    partner = [-1] * n
    out = []
    def cells_ok():
        cnt = np.zeros((9, 9), dtype=np.int64)
        for a in range(n):
            b = partner[a]
            if b >= 0:
                for i in DEF[a]:
                    for j in DEF[b]:
                        cnt[i, j] += 1
        return bool((cnt <= cap).all())
    def rec():
        a = n - 1
        while a >= 0 and partner[a] >= 0:
            a -= 1
        if a < 0:
            out.append(tuple(partner)); return
        for b in range(a - 1, -1, -1):
            if partner[b] < 0 and adm[a][b]:
                partner[a] = b; partner[b] = a
                if cells_ok():
                    rec()
                partner[a] = -1; partner[b] = -1
    rec()
    auts = automorphisms(B)
    pos = {d: k for k, d in enumerate(DEF)}
    act = [[pos[tuple(sorted((g[a], g[b])))] for (a, b) in DEF] for g in auts]
    def canon(t):
        best = None
        for g in act:
            key = tuple(sorted((min(g[a], g[t[a]]), max(g[a], g[t[a]])) for a in range(n) if a < t[a]))
            if best is None or key < best:
                best = key
        return best
    classes = {}
    for t in out:
        classes.setdefault(canon(t), []).append(t)
    print(f"stage1 B{s}: deficient pairs {n}, admissible rectangles {nadm}, matchings {len(out)}, |Aut| {len(auts)}, "
          f"orbits {len(classes)}, ambiguous PSD {AMBIG[0]}")
    td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
    same_def = [tuple(d) for d in td["DEF"]] == DEF
    mine = set(out)
    reps = [tuple(r) for r in td["reps"]]
    in_mine = all(r in mine for r in reps)
    keys = set(canon(r) for r in reps)
    print(f"   enumerator file r2_tau_{s}.json: same list of deficient pairs: {same_def}; n_tau {td['n_tau']} "
          f"(equal: {td['n_tau'] == len(out)}); {len(reps)} representatives, all are matchings of the verifier: {in_mine}; "
          f"pairwise inequivalent and covering all orbits: {len(keys) == len(reps) == len(classes) and keys == set(classes)}")


def check_certs(files):
    sup = {s: support(Bmat(s), 18) for s in (0, 1, 2)}
    tot = bad = 0
    sizes = {}
    for fn in files:
        nfile = 0
        for line in open(os.path.join(HERE, fn)):
            rec = json.loads(line)
            n, rows, mi, x = rec["n"], rec["rows"], rec["m"], rec["x"]
            A = np.array([[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)], dtype=np.int64)
            good = (A == A.T).all() and not A.diagonal().any() and len(x) == n
            good = good and any((A[:18, :18] == sup[s]).all() for s in sup)
            M = (27 * np.eye(n, dtype=np.int64) - 9 * A + 1) if mi == 0 else (44 * np.eye(n, dtype=np.int64) + 11 * A - 2)
            xo = np.array([int(t) for t in x], dtype=object)
            good = good and int(xo @ (M.astype(object) @ xo)) < 0
            tot += 1; nfile += 1
            sizes[n] = sizes.get(n, 0) + 1
            if not good:
                bad += 1
        print(f"   {fn}: {nfile} certificates")
    print(f"certs: {tot} certificates checked, {bad} invalid; number by size of vertex set: {sorted(sizes.items())}")


def min_y2(t):
    return min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t)


def type_solutions(B, f, cache):
    """sets of 5 distinct unordered pairs {i,j}; vertex i has degree 2 - f_i; single type admissible (own test)"""
    defi = [2 - x for x in f]
    pairs = []
    for i in range(9):
        for j in range(i + 1, 9):
            if (i, j) not in cache:
                cache[(i, j)] = single_type_ok(B, (i,), (j,), True)
            if cache[(i, j)]:
                pairs.append((i, j))
    res = []
    def rec(start, chosen):
        if len(chosen) == 5:
            if not any(defi):
                res.append(tuple(chosen))
            return
        for q in range(start, len(pairs)):
            i, j = pairs[q]
            if defi[i] > 0 and defi[j] > 0:
                defi[i] -= 1; defi[j] -= 1
                chosen.append((i, j))
                rec(q + 1, chosen)
                chosen.pop()
                defi[i] += 1; defi[j] += 1
    rec(0, [])
    return res


def load_setup(s):
    B = Bmat(s)
    DEF = deficient_pairs(B)
    td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
    assert [tuple(d) for d in td["DEF"]] == DEF
    return B, DEF, [tuple(r) for r in td["reps"]]


def base37(B, DEF, tau, n=37):
    A = support(B, n)
    for k in range(18):
        for i in DEF[k]:
            A[19 + k, i] = A[i, 19 + k] = 1
        for j in DEF[tau[k]]:
            A[19 + k, 9 + j] = A[9 + j, 19 + k] = 1
    return A


def B250(s, part, nparts, tl):
    B, DEF, reps = load_setup(s)
    stc = {}
    out = []
    stats = {"tau": 0, "F_tested": 0, "F_base_ok": 0, "F_types_ok": 0, "nodes": 0, "H": 0}
    timed_out = False
    KEEP = set(int(x) for x in os.environ["R3V_TAUS"].split(",")) if os.environ.get("R3V_TAUS") else None
    tagx = ("_t" + os.environ["R3V_TAUS"].split(",")[0]) if KEEP is not None else ""
    DONE_TAUS = []
    for ti in range(len(reps)):
        if KEEP is not None:
            if ti not in KEEP:
                continue
        elif ti % nparts != part:
            continue
        if time.time() - T0 > tl:
            timed_out = True; break
        tau = reps[ti]
        stats["tau"] += 1
        DONE_TAUS.append(ti)
        A = base37(B, DEF, tau)
        orbits = [(k, tau[k]) for k in range(18) if k < tau[k]]
        for F in itertools.combinations(orbits, 2):
            mem = [k for o in F for k in o]
            if any(set(DEF[k]) & set(DEF[tau[k]]) for k in mem):
                continue
            stats["F_tested"] += 1
            A0 = A.copy()
            for k in mem:
                A0[18, 19 + k] = A0[19 + k, 18] = 1
            for (a, b) in F:
                A0[19 + a, 19 + b] = A0[19 + b, 19 + a] = 1
            idx0 = list(range(19)) + [19 + k for k in mem]
            if not ok(A0, idx0):
                continue
            stats["F_base_ok"] += 1
            f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
            if max(f) > 2 or not type_solutions(B, f, stc):
                continue
            stats["F_types_ok"] += 1
            rest = sorted([o for o in orbits if o not in F], reverse=True)
            def add_orbit(a, Acur, idx, fl):
                if a == len(rest):
                    H = [int(sum(1 << l for l in range(18) if Acur[19 + k, 19 + l])) for k in range(18)]
                    out.append({"tau": ti, "F": sorted(o[0] for o in F), "H": H})
                    return
                s1, s2 = rest[a]
                prev = list(F) + rest[:a]
                idx2 = idx + [19 + s1, 19 + s2]
                def choose(b, A2, deg, fl2):
                    if b == len(prev):
                        stats["nodes"] += 1
                        if ok(A2, idx2):
                            add_orbit(a + 1, A2, idx2, fl2)
                        return
                    q1, q2 = prev[b]
                    isF = prev[b] in F
                    for st in (0, 1, 2, 3):
                        w = (0, 1, 1, 2)[st]
                        if deg + w > 4 or (isF and fl2 + w > 4):
                            continue
                        A3 = A2
                        if st:
                            A3 = A2.copy()
                            if st & 1:
                                A3[19 + s1, 19 + q1] = A3[19 + q1, 19 + s1] = 1
                                A3[19 + s2, 19 + q2] = A3[19 + q2, 19 + s2] = 1
                            if st & 2:
                                A3[19 + s1, 19 + q2] = A3[19 + q2, 19 + s1] = 1
                                A3[19 + s2, 19 + q1] = A3[19 + q1, 19 + s2] = 1
                            if A3[19 + q1, 19:37].sum() > 4 or A3[19 + q2, 19:37].sum() > 4:
                                continue
                            if not budgets_ok(A3[np.ix_(idx2, idx2)]):
                                continue
                        choose(b + 1, A3, deg + w, fl2 + (w if isF else 0))
                choose(0, Acur, 0, fl)
            add_orbit(0, A0, idx0, 0)
    stats["H"] = len(out)
    print(f"B250 B{s} part {part}/{nparts}: {stats}, timed_out {timed_out}, ambiguous PSD {AMBIG[0]}, {time.time() - T0:.0f}s")
    json.dump({"s": s, "part": part, "nparts": nparts, "stats": stats, "timed_out": timed_out, "H": out,
               "taus_started": DONE_TAUS},
              open(os.path.join(HERE, f"r3v_B250_{s}_{part}of{nparts}{tagx}.json"), "w"))


def C250(s, part, nparts, tl, files):
    B, DEF, reps = load_setup(s)
    items = []
    for fn in files:
        d = json.load(open(os.path.join(HERE, fn)))
        # B0: the first file stopped after matchings 0..417, the second covers 418..424 (b0_compareB.py checks the union)
        assert (not d["timed_out"]) or os.environ.get("B0_ALLOW_PARTIAL")
        items += d["H"]
    items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
    tagx = ""
    if os.environ.get("R3V_TAUS"):
        keep = set(int(x) for x in os.environ["R3V_TAUS"].split(","))
        items = [e for e in items if e["tau"] in keep]
        tagx = "_t" + os.environ["R3V_TAUS"].split(",")[0]
    if os.environ.get("R3V_SKIP") or os.environ.get("R3V_TAKE"):
        sk = int(os.environ.get("R3V_SKIP", "0")); tk = int(os.environ.get("R3V_TAKE", "1000000"))
        items = items[sk:sk + tk]
        tagx += f"_skip{sk}"
    MY = {t: 2 * min_y2(t) for t in range(10)}
    stc = {}
    stats = {"H_in": len(items), "H_mine": 0, "H_after_counts": 0, "type_solutions": 0, "type_solutions_ok33": 0,
             "allow_tests": 0, "nodes": 0, "survivors": 0}
    ts_cache = {}
    survivors = []
    timed_out = False
    for n_item, e in enumerate(items):
        if n_item % nparts != part:
            continue
        if time.time() - T0 > tl:
            timed_out = True; break
        stats["H_mine"] += 1
        ti, F, H = e["tau"], e["F"], e["H"]
        tau = reps[ti]
        mem = [k for o in F for k in (o, tau[o])]
        degs = [bin(h).count("1") for h in H]
        t = sum(degs) // 2
        fl = sum(degs[k] - 1 for k in mem)
        if t > 9 or fl > 8 or sum(d * (d - 1) for d in degs) + MY[t] > 36:
            continue
        stats["H_after_counts"] += 1
        A = base37(B, DEF, tau, 47)
        for k in range(18):
            for l in range(18):
                if (H[k] >> l) & 1:
                    A[19 + k, 19 + l] = 1
        for k in mem:
            A[18, 19 + k] = A[19 + k, 18] = 1
        f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
        idxp = list(range(19)) + [19 + k for k in mem]
        def with_W(A2, ts):
            A3 = A2.copy()
            for c, (i, j) in enumerate(ts):
                w, sw = 37 + 2 * c, 38 + 2 * c
                for u, v in ((w, 18), (sw, 18), (w, sw), (w, i), (w, 9 + j), (sw, j), (sw, 9 + i)):
                    A3[u, v] = A3[v, u] = 1
            return A3
        key = (ti, tuple(F))
        if key not in ts_cache:
            good = []
            for ts in type_solutions(B, f, stc):
                stats["type_solutions"] += 1
                if ok(with_W(A, ts), idxp + list(range(37, 47))):
                    good.append(ts)
            stats["type_solutions_ok33"] += len(good)
            ts_cache[key] = good
        non = [k for k in range(18) if k not in mem]
        req = {k: 2 - sum(int(A[19 + k, 19 + q]) for q in mem) for k in non}
        orbs = sorted([(k, tau[k]) for k in non if k < tau[k]], key=lambda o: (-req[o[0]], o))
        allow = {}
        def allowed(i, j, k):
            """may the vertex of W of type (i ; j) be adjacent to the X_2 vertex k ?  (27 determined vertices)"""
            if (i, j, k) not in allow:
                stats["allow_tests"] += 1
                A2 = A.copy()
                for u, v in ((37, 18), (38, 18), (37, 38), (37, i), (37, 9 + j), (38, j), (38, 9 + i),
                             (37, 19 + k), (38, 19 + tau[k])):
                    A2[u, v] = A2[v, u] = 1
                allow[(i, j, k)] = ok(A2, idxp + [19 + k, 19 + tau[k], 37, 38])
            return allow[(i, j, k)]
        for ts in ts_cache[key]:
            A1 = with_W(A, ts)
            wtype = {}
            for c, (i, j) in enumerate(ts):
                wtype[2 * c] = (i, j); wtype[2 * c + 1] = (j, i)
            def rec(a, A2, idx):
                if a == len(orbs):
                    if all(A2[37 + x, 19:37].sum() >= 2 for x in range(10)):
                        stats["survivors"] += 1
                        survivors.append({"tau": ti, "F": F, "H": H, "types": [list(p) for p in ts]})
                    return
                s1, s2 = orbs[a]
                idx2 = idx + [19 + s1, 19 + s2]
                cand = [x for x in range(10) if allowed(wtype[x][0], wtype[x][1], s1)]
                for sub in itertools.combinations(cand, req[s1]):
                    if any((x ^ 1) in sub for x in sub):
                        continue
                    A3 = A2.copy()
                    for x in sub:
                        A3[19 + s1, 37 + x] = A3[37 + x, 19 + s1] = 1
                        A3[19 + s2, 37 + (x ^ 1)] = A3[37 + (x ^ 1), 19 + s2] = 1
                    stats["nodes"] += 1
                    if ok(A3, idx2):
                        rec(a + 1, A3, idx2)
            rec(0, A1, idxp + list(range(37, 47)))
    print(f"C250 B{s} part {part}/{nparts}: {stats}, timed_out {timed_out}, ambiguous PSD {AMBIG[0]}, {time.time() - T0:.0f}s")
    json.dump({"s": s, "part": part, "nparts": nparts, "stats": stats, "timed_out": timed_out, "survivors": survivors},
              open(os.path.join(HERE, f"r3v_C250_{s}_{part}of{nparts}{tagx}.json"), "w"))


def compareB(s, enum_files):
    MY = {t: 2 * min_y2(t) for t in range(10)}
    B, DEF, reps = load_setup(s)
    mine = set(); mine_all = 0
    for fn in sorted(os.listdir(HERE)):
        if fn.startswith(f"r3v_B250_{s}_") and fn.endswith(".json"):
            d = json.load(open(os.path.join(HERE, fn)))
            assert not d["timed_out"], fn
            for e in d["H"]:
                mine_all += 1
                tau = reps[e["tau"]]
                mem = [k for o in e["F"] for k in (o, tau[o])]
                degs = [bin(h).count("1") for h in e["H"]]
                t = sum(degs) // 2
                if t <= 9 and sum(degs[k] - 1 for k in mem) <= 8 and sum(x * (x - 1) for x in degs) + MY[t] <= 36:
                    mine.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
    theirs = set()
    for fn in enum_files:
        d = json.load(open(os.path.join(HERE, fn)))
        assert not d["timed_out"], fn
        for e in d["H_stageB"]:
            theirs.add((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
    print(f"compareB B{s}: verifier H (all / after the counting conditions) = {mine_all} / {len(mine)}; "
          f"enumerator = {len(theirs)}; identical sets: {mine == theirs}; only verifier {len(mine - theirs)}, "
          f"only enumerator {len(theirs - mine)}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stage1":
        stage1(int(sys.argv[2]))
    elif mode == "certs":
        check_certs(sys.argv[2:])
    elif mode == "B250":
        B250(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
    elif mode == "C250":
        s = int(sys.argv[2])
        files = sorted(fn for fn in os.listdir(HERE) if fn.startswith(f"r3v_B250_{s}_") and fn.endswith(".json"))
        C250(s, int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), files)
    elif mode == "compareB":
        compareB(int(sys.argv[2]), sys.argv[3:])
