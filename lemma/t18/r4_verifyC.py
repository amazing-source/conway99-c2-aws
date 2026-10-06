# Round 4.  INDEPENDENT second implementation of stage C (W added to S u {p} u X_2) for profile (2,5,0), n_3 = 0.
# It imports nothing from the enumerators (r3_p250.py) and starts from the verifier's own stage-B output
# (r3v_B250_<s>_*.json, produced by r3_verify.py).  Differences with the enumerator:
#   * DUAL order: X_2 orbit by X_2 orbit (which vertices of W does it see), not W pair by W pair;
#   * intermediate test = budgets recounted by matrix products + positive semidefiniteness of the SIGMA-ODD part only
#     (orbit Gram matrix  G = 3I - A[R,R] + A[R, sigma R],  R = one vertex per non-fixed orbit; it is half of
#     (e_v - e_sigma v)^T (3I - A + J/9) (e_v' - e_sigma v'), hence PSD in a real graph); rejection needs an integer
#     vector y with y^T G y < 0, evaluated exactly;
#   * option table: for a vertex w of W of type (i ; j) and an X_2 orbit {k, tau k} the three options
#     w ~ k / w ~ tau k / neither are tested on the 27 determined vertices S u {p} u A_p u {k, tau k} u {w, sigma w};
#   * only COMPLETE configurations (47 vertices) get the full test (both matrices 9(3I-A)+J and 11(4I+A)-2J).
# Since every test is hereditary, the set of complete configurations passing the full test does not depend on the order
# or on the intermediate tests: it must coincide with the survivors of the enumerator.
# usage: python r4_verifyC.py <structure> <part> <nparts> <time limit s>      -> r4v_C_<s>_<part>of<nparts>.json
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
         1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
         2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
T0 = time.time()
ST = {"triples": 0, "type_solutions": 0, "type_solutions_ok33": 0, "option_tests": 0, "ts_dead_by_options": 0,
      "nodes": 0, "rej_budget": 0, "rej_odd_psd": 0, "complete": 0, "complete_rej_full": 0, "survivors": 0, "ambiguous": 0}


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
    if os.environ.get("R4V_TAUS"):
        keep = set(int(x) for x in os.environ["R4V_TAUS"].split(","))
        items = [e for e in items if e["tau"] in keep]
    single_cache = {}
    ts_cache = {}
    survivors = []
    done = 0
    timed_out = False

    def single_ok(i, j):
        if (i, j) not in single_cache:
            A = np.zeros((21, 21), dtype=np.int64)
            A[:9, 9:18] = B; A[9:18, :9] = B
            for u, v in ((19, 18), (20, 18), (19, 20), (19, i), (19, 9 + j), (20, j), (20, 9 + i)):
                A[u, v] = A[v, u] = 1
            single_cache[(i, j)] = full_ok(A, list(range(21)))
        return single_cache[(i, j)]

    for n_item, e in enumerate(items):
        if n_item % nparts != part:
            continue
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
        sig = list(range(9, 18)) + list(range(9)) + [18] + [19 + tau[k] for k in range(18)] + [37 + (x ^ 1) for x in range(10)]
        sig = np.array(sig)

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
        f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]

        def with_W(A2, ts):
            A3 = A2.copy()
            for c, (i, j) in enumerate(ts):
                w, sw = 37 + 2 * c, 38 + 2 * c
                for u, v in ((w, 18), (sw, 18), (w, sw), (w, i), (w, 9 + j), (sw, j), (sw, 9 + i)):
                    A3[u, v] = A3[v, u] = 1
            return A3

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
                if full_ok(with_W(A, ts), idxp + list(range(37, 47))):
                    good.append(ts)
            ST["type_solutions_ok33"] += len(good)
            ts_cache[key] = good
        non = [k for k in range(18) if k not in mem]
        req = {k: 2 - sum(int(A[19 + k, 19 + q]) for q in mem) for k in non}
        orbs = sorted([(k, tau[k]) for k in non if k < tau[k]], key=lambda o: (-req[o[0]], o))
        opt = {}
        def options(i, j, o):
            """options of the W vertex of type (i ; j) with respect to the orbit o = (k, tau k): '+', '-', '0'"""
            if (i, j, o) not in opt:
                res = set()
                for name in "+-0":
                    ST["option_tests"] += 1
                    A2 = A.copy()
                    for u, v in ((37, 18), (38, 18), (37, 38), (37, i), (37, 9 + j), (38, j), (38, 9 + i)):
                        A2[u, v] = A2[v, u] = 1
                    k, tk = o
                    if name == "+":
                        for u, v in ((37, 19 + k), (38, 19 + tk)):
                            A2[u, v] = A2[v, u] = 1
                    elif name == "-":
                        for u, v in ((37, 19 + tk), (38, 19 + k)):
                            A2[u, v] = A2[v, u] = 1
                    if full_ok(A2, idxp + [19 + k, 19 + tk, 37, 38]):
                        res.add(name)
                opt[(i, j, o)] = res
            return opt[(i, j, o)]

        for ts in ts_cache[key]:
            # cheap necessary conditions from the option tables
            dead = False
            for (i, j) in ts:
                forced = sum(1 for o in orbs if "0" not in options(i, j, o))
                can = sum(1 for o in orbs if options(i, j, o) & {"+", "-"})
                if can < 2 or any(not options(i, j, o) for o in orbs):
                    dead = True; break
            if dead:
                ST["ts_dead_by_options"] += 1
                continue
            A1 = with_W(A, ts)
            def rec(a, A2, idx, degW):
                if a == len(orbs):
                    if min(degW) < 2:
                        return
                    ST["complete"] += 1
                    if full_ok(A2, list(range(47))):
                        ST["survivors"] += 1
                        survivors.append({"tau": ti, "F": F, "H": H, "types": [list(p) for p in ts],
                                          "rows": [int(sum(1 << q for q in range(47) if A2[u, q])) for u in range(47)]})
                    else:
                        ST["complete_rej_full"] += 1
                    return
                o = orbs[a]
                s1, s2 = o
                left = len(orbs) - a - 1
                idx2 = idx + [19 + s1, 19 + s2]
                for sub in itertools.combinations(range(10), req[s1]):
                    if any((x ^ 1) in sub for x in sub):
                        continue
                    good = True
                    for c, (i, j) in enumerate(ts):
                        name = "+" if 2 * c in sub else ("-" if 2 * c + 1 in sub else "0")
                        if name not in options(i, j, o):
                            good = False; break
                    if not good:
                        continue
                    dW = degW[:]
                    for x in sub:
                        dW[x] += 1; dW[x ^ 1] += 1
                    if any(dW[x] + left < 2 for x in range(10)):
                        continue
                    A3 = A2.copy()
                    for x in sub:
                        A3[19 + s1, 37 + x] = A3[37 + x, 19 + s1] = 1
                        A3[19 + s2, 37 + (x ^ 1)] = A3[37 + (x ^ 1), 19 + s2] = 1
                    ST["nodes"] += 1
                    if fast_ok(A3, idx2):
                        rec(a + 1, A3, idx2, dW)
            rec(0, A1, idxp + list(range(37, 47)), [0] * 10)
        done += 1
        if done % 200 == 0:
            print(f"  [{time.time() - T0:.0f}s] done {done}: {ST}", flush=True)
    print(f"verifier stage C, B{s} part {part}/{nparts}: triples in this part {sum(1 for n in range(len(items)) if n % nparts == part)}, "
          f"completed {done}, timed_out {timed_out}, {time.time() - T0:.0f}s")
    print("   ", ST)
    tag = ("_t" + os.environ["R4V_TAUS"].split(",")[0]) if os.environ.get("R4V_TAUS") else ""
    json.dump({"s": s, "part": part, "nparts": nparts, "n_items": len(items), "completed": done, "timed_out": timed_out,
               "stats": ST, "survivors": survivors},
              open(os.path.join(HERE, f"r4v_C_{s}_{part}of{nparts}{tag}.json"), "w"))


if __name__ == "__main__":
    main()
