# Round 4.  INDEPENDENT second implementation of stage C (W added to S u {p} u X_2), profile (2,5,0), n_3 = 0.
# Third attempt (r3_verify.py C250 and r4_verifyC.py, both in the dual order, were far too slow).
# It imports nothing from the enumerator r3_p250.py and starts from the verifier's own stage-B output r3v_B250_<s>_*.json.
# Method:
#   (1) for a W vertex w of type (i ; j) and each X_2 orbit {k, tau k} outside A_p, the options
#       '+' (w ~ k), '-' (w ~ tau k), '0' (neither) are tested on the 27 determined vertices
#       S u {p} u A_p u {k, tau k} u {w, sigma w};
#   (2) FS(i ; j) = all sets N = N(w) n X_2 (one allowed option per orbit, |N| >= 2, |N| <= 2 + slack) such that the 39
#       determined vertices S u {p} u X_2 u {w, sigma w} pass;
#   (3) for every type solution (5 pairs of types) choose N_c in FS(type_c), exact cover of the requirements
#       (every s in X_2 \ A_p has exactly 2 - |N(s) n A_p| neighbours in W), tested after each pair;
#   (4) complete configurations (47 vertices) get the FULL test.
# Intermediate test = budgets recounted by matrix products + PSD of the sigma-odd orbit matrix
#       G = 3I - A[R,R] + A[R, sigma R]   (R = one vertex per non-fixed orbit),
# a necessary condition (half of (e_v - e_sv)^T (3I - A + J/9) (e_v' - e_sv')); a rejection needs an integer vector y
# with y^T G y < 0, evaluated exactly in int64.  The full test uses both matrices 9(3I-A)+J and 11(4I+A)-2J.
# All tests are hereditary, so the set of complete configurations passing the full test is independent of the order and
# of the intermediate tests: it must equal the survivor set of the enumerator.
# usage: python r4_verifyC2.py <structure> <part> <nparts> <time limit s>     -> r4v_C2_<s>_<part>of<nparts>[_skipN].json
# env: R4V_TAUS (restrict to these matchings), R4V_SKIP (skip the first N triples of the part: resume after a time-out)
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
T0 = time.time()
FULL = os.environ.get("R4V_FULL") == "1"
ST = {"triples": 0, "type_solutions": 0, "type_solutions_ok33": 0, "option_tests": 0, "FS_candidates": 0, "FS_partial_budget_cut": 0, "FS_kept": 0,
      "ts_dead_empty_FS": 0, "nodes": 0, "rej_budget": 0, "rej_odd_psd": 0, "complete": 0, "complete_rej_full": 0,
      "survivors": 0, "ambiguous": 0}


def exact_neg(M, V, cols=1):
    for col in range(cols):
        for sc in (8, 30, 100, 1000, 10 ** 5):
            y = np.rint(sc * V[:, col]).astype(np.int64)
            if int(y @ (M @ y)) < 0:
                return True
    return False


def full_ok(A, idx):
    sub = A[np.ix_(idx, idx)]
    C = sub @ sub
    np.fill_diagonal(C, 0)
    if (C > 2 - sub).any():
        return False
    n = len(idx)
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * sub + 1, 44 * I + 11 * sub - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -1e-7:
            if exact_neg(M, V, 2):
                return False
            ST["ambiguous"] += 1
    return True


def main():
    s = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3]); tl = float(sys.argv[4])
    B = np.zeros((9, 9), dtype=np.int64)
    for e in EDGES[s].split():
        B[int(e[0]), int(e[1])] = B[int(e[1]), int(e[0])] = 1
    C2 = B @ B
    DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if C2[a, b] == 1]
    td = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))
    assert [tuple(d) for d in td["DEF"]] == DEF
    reps = td["reps"]
    items = []
    for fn in sorted(os.listdir(HERE)):
        if fn.startswith(f"r3v_B250_{s}_") and fn.endswith(".json"):
            d = json.load(open(os.path.join(HERE, fn)))
            assert not d["timed_out"]
            items += d["H"]
    items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
    tag = ""
    if os.environ.get("R4V_TAUS"):
        keep = set(int(x) for x in os.environ["R4V_TAUS"].split(","))
        items = [e for e in items if e["tau"] in keep]
        tag += "_t" + os.environ["R4V_TAUS"].split(",")[0]
    mine = [e for n_item, e in enumerate(items) if n_item % nparts == part]
    idx_list = None
    if os.environ.get("R4V_IDX"):
        idx_list = [int(x) for x in os.environ["R4V_IDX"].split(",")]
        mine = [items[q] for q in idx_list]
        tag += f"_idx{idx_list[0]}"
    skip = int(os.environ.get("R4V_SKIP", "0"))
    if skip:
        tag += f"_skip{skip}"
    if FULL:
        tag += "_full"
    single_cache = {}
    ts_cache = {}
    survivors = []
    done = 0
    timed_out = False
    outname = None
    def dump():
        json.dump({"s": s, "part": part, "nparts": nparts, "n_items": len(items), "in_part": len(mine), "skip": skip,
                   "idx_list": idx_list, "completed": done, "timed_out": timed_out, "stats": ST, "survivors": survivors},
                  open(os.path.join(HERE, outname), "w"))

    def single_ok(i, j):
        if (i, j) not in single_cache:
            A = np.zeros((21, 21), dtype=np.int64)
            A[:9, 9:18] = B; A[9:18, :9] = B
            for u, v in ((19, 18), (20, 18), (19, 20), (19, i), (19, 9 + j), (20, j), (20, 9 + i)):
                A[u, v] = A[v, u] = 1
            single_cache[(i, j)] = full_ok(A, list(range(21)))
        return single_cache[(i, j)]

    outname = f"r4v_C2_{s}_{part}of{nparts}{tag}.json"
    for e in mine[skip:]:
        if done:
            dump()
        if time.time() - T0 > tl:
            timed_out = True
            break
        ST["triples"] += 1
        ti, F, H = e["tau"], e["F"], e["H"]
        tau = reps[ti]
        mem = [k for o in F for k in (o, tau[o])]
        A = np.zeros((47, 47), dtype=np.int64)
        A[:9, 9:18] = B; A[9:18, :9] = B
        for k in range(18):
            for i in DEF[k]:
                A[19 + k, i] = A[i, 19 + k] = 1
            for j in DEF[tau[k]]:
                A[19 + k, 9 + j] = A[9 + j, 19 + k] = 1
            for l in range(18):
                if (H[k] >> l) & 1:
                    A[19 + k, 19 + l] = 1
        for k in mem:
            A[18, 19 + k] = A[19 + k, 18] = 1
        sig = np.array(list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)]
                       + [37 + (x ^ 1) for x in range(10)])

        def fast_ok(A2, idx):
            sub = A2[np.ix_(idx, idx)]
            Cn = sub @ sub
            np.fill_diagonal(Cn, 0)
            if (Cn > 2 - sub).any():
                ST["rej_budget"] += 1
                return False
            R = [v for v in idx if v < sig[v]]
            G = 3 * np.eye(len(R), dtype=np.int64) - A2[np.ix_(R, R)] + A2[np.ix_(R, sig[R])]
            w, V = np.linalg.eigh(G.astype(np.float64))
            if w[0] < -1e-7:
                if exact_neg(G, V):
                    ST["rej_odd_psd"] += 1
                    return False
                ST["ambiguous"] += 1
            return True

        idxp = list(range(19)) + [19 + k for k in mem]
        idx37 = list(range(37))
        f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]

        def put_W(A2, c, i, j):
            w, sw = 37 + 2 * c, 38 + 2 * c
            for u, v in ((w, 18), (sw, 18), (w, sw), (w, i), (w, 9 + j), (sw, j), (sw, 9 + i)):
                A2[u, v] = A2[v, u] = 1

        key = (ti, tuple(F))
        if key not in ts_cache:
            defi = [2 - x for x in f]
            pairs = [(i, j) for i in range(9) for j in range(i + 1, 9) if single_ok(i, j)]
            sols = []
            def rec_t(start, chosen):
                if len(chosen) == 5:
                    if not any(defi):
                        sols.append(tuple(chosen))
                    return
                for q in range(start, len(pairs)):
                    i, j = pairs[q]
                    if defi[i] > 0 and defi[j] > 0:
                        defi[i] -= 1; defi[j] -= 1
                        chosen.append((i, j))
                        rec_t(q + 1, chosen)
                        chosen.pop()
                        defi[i] += 1; defi[j] += 1
            rec_t(0, [])
            good = []
            for ts in sols:
                ST["type_solutions"] += 1
                A3 = A.copy()
                for c, (i, j) in enumerate(ts):
                    put_W(A3, c, i, j)
                if full_ok(A3, idxp + list(range(37, 47))):
                    good.append(ts)
            ST["type_solutions_ok33"] += len(good)
            ts_cache[key] = good
        if not ts_cache[key]:
            done += 1
            continue
        non = [k for k in range(18) if k not in mem]
        req = {k: 2 - sum(int(A[19 + k, 19 + q]) for q in mem) for k in non}
        orbs = [(k, tau[k]) for k in non if k < tau[k]]
        degs = [int(A[19 + k, 19:37].sum()) for k in range(18)]
        slack = 4 - sum(degs[k] - 1 for k in mem) // 2
        fs_cache = {}

        def FS(i, j):
            if (i, j) in fs_cache:
                return fs_cache[(i, j)]
            opts = []
            for (k, tk) in orbs:
                res = []
                for name in "0+-":
                    if name != "0" and req[k] < 1:
                        continue
                    ST["option_tests"] += 1
                    A2 = A.copy()
                    put_W(A2, 0, i, j)
                    if name == "+":
                        for u, v in ((37, 19 + k), (38, 19 + tk)):
                            A2[u, v] = A2[v, u] = 1
                    elif name == "-":
                        for u, v in ((37, 19 + tk), (38, 19 + k)):
                            A2[u, v] = A2[v, u] = 1
                    if fast_ok(A2, idxp + [19 + k, 19 + tk, 37, 38]):
                        res.append(name)
                opts.append(res)
            out = []
            if all(opts):
                def rec_n(a, N):
                    if a == len(orbs):
                        if len(N) >= 2:
                            ST["FS_candidates"] += 1
                            A2 = A.copy()
                            put_W(A2, 0, i, j)
                            for k in N:
                                A2[37, 19 + k] = A2[19 + k, 37] = 1
                                A2[38, 19 + tau[k]] = A2[19 + tau[k], 38] = 1
                            if fast_ok(A2, idx37 + [37, 38]):
                                out.append(tuple(N))
                        return
                    k, tk = orbs[a]
                    remaining = len(orbs) - a - 1
                    for name in opts[a]:
                        if name == "0":
                            if len(N) + remaining >= 2:
                                rec_n(a + 1, N)
                        elif len(N) < 2 + slack:
                            N2 = N + [k if name == "+" else tk]
                            A2 = A.copy()
                            put_W(A2, 0, i, j)
                            for q in N2:
                                A2[37, 19 + q] = A2[19 + q, 37] = 1
                                A2[38, 19 + tau[q]] = A2[19 + tau[q], 38] = 1
                            sub = A2[:39, :39]
                            Cn = sub @ sub
                            np.fill_diagonal(Cn, 0)
                            if (Cn > 2 - sub).any():
                                ST["FS_partial_budget_cut"] += 1
                                continue
                            rec_n(a + 1, N2)
                rec_n(0, [])
            ST["FS_kept"] += len(out)
            fs_cache[(i, j)] = out
            return out

        for ts in ts_cache[key]:
            dead = False
            for c in sorted(range(5), key=lambda c: ts[c] not in fs_cache):
                if not FS(*ts[c]):
                    dead = True; break
            if dead:
                ST["ts_dead_empty_FS"] += 1
                continue
            lists = [FS(i, j) for (i, j) in ts]
            A1 = A.copy()
            for c, (i, j) in enumerate(ts):
                put_W(A1, c, i, j)
            def rec(c, A2, rem):
                if c == 5:
                    if any(rem.values()):
                        return
                    ST["complete"] += 1
                    if full_ok(A2, list(range(47))):
                        ST["survivors"] += 1
                        survivors.append({"tau": ti, "F": F, "H": H, "types": [list(p) for p in ts],
                                          "rows": [int(sum(1 << q for q in range(47) if A2[u, q])) for u in range(47)]})
                    else:
                        ST["complete_rej_full"] += 1
                    return
                for N in lists[c]:
                    if any(rem[k] < 1 or rem[tau[k]] < 1 for k in N):
                        continue
                    rem2 = dict(rem)
                    for k in N:
                        rem2[k] -= 1; rem2[tau[k]] -= 1
                    # the remaining pairs must be able to absorb what is left
                    left = sum(rem2.values())
                    if left < 4 * (4 - c) or left > 2 * (2 + slack) * (4 - c):
                        continue
                    A3 = A2.copy()
                    w, sw = 37 + 2 * c, 38 + 2 * c
                    for k in N:
                        A3[w, 19 + k] = A3[19 + k, w] = 1
                        A3[sw, 19 + tau[k]] = A3[19 + tau[k], sw] = 1
                    ST["nodes"] += 1
                    if (full_ok(A3, idx37 + list(range(37, 39 + 2 * c))) if FULL else fast_ok(A3, idx37 + list(range(37, 39 + 2 * c)))):
                        rec(c + 1, A3, rem2)
            rec(0, A1, dict(req))
        done += 1
        if done % 250 == 0:
            print(f"  [{time.time() - T0:.0f}s] done {done}: {ST}", flush=True)
    print(f"verifier stage C (v2), B{s} part {part}/{nparts}: triples in this part {len(mine)}, skipped {skip}, "
          f"completed now {done}, timed_out {timed_out}, {time.time() - T0:.0f}s")
    print("   ", ST)
    dump()


if __name__ == "__main__":
    main()
