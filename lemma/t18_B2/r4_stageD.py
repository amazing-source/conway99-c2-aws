# Round 4.  Stage D ("X_0 stage") for profile (2,5,0), n_3 = 0.   Self-contained (numpy only).
# Input: the stage-C survivors of r3_p250.py (graphs on S u {p} u X_2 u W, 47 vertices).
# Added: the 8 vertices of X_0 \ {p} = 4 mate pairs {z_q, sigma z_q}.  Forced (report A14, B round 3, A18):
#   z has no neighbour in S u {p}, z is not adjacent to its mate, a_2(z) >= 4, |N(z) n A_p| + |N(z) n W| = 2,
#   deg_{A[X_0]}(z) = a_2(z) - 4;
#   every s in X_2 has exactly a_2(s) + 2 - [s in A_p] neighbours in X_0 \ {p};  every w in W exactly a_2(w) - 2.
# D1: every candidate pair (z, sigma z) is tested on the 49 determined vertices (budgets + exact PSD certificate);
# D2: exact cover of the requirements by 4 pairs;  D3: G = A[X_0 \ {p}] (sigma-invariant, prescribed degrees);
# D4: the 55 determined vertices S u X_0 u X_2 u W are tested (budgets + PSD).
# Vertex numbering: support 0..17, p 18, X_2 19..36, W 37..46, z_q 47+2q, sigma z_q 48+2q.
# usage: python r4_stageD.py <structure> <survivor json files of r3_p250.py ...>
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
s_idx = int(sys.argv[1])
td = json.load(open(os.path.join(HERE, f"r2_tau_{s_idx}.json")))
reps = td["reps"]
T0 = time.time()
CERT = []


def budgets_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


def neg_vector(M):
    """integer x with x^T M x < 0, exact in int64 (n <= 55, |x_i| <= 10^5, |M_ij| <= 44)"""
    w, V = np.linalg.eigh(M.astype(float))
    if w[0] > -1e-7:
        return None, False
    for col in range(min(3, len(w))):
        if w[col] > -1e-7:
            break
        for scale in (8, 30, 100, 1000, 10 ** 5):
            x = np.rint(scale * V[:, col]).astype(np.int64)
            if int(x @ (M @ x)) < 0:
                return x, False
    return None, True


def psd_reject(A, stats, save):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    for mi, M in enumerate((27 * I - 9 * A + 1, 44 * I + 11 * A - 2)):
        x, amb = neg_vector(M)
        if amb:
            stats["ambiguous"] += 1
        if x is not None:
            if save and len(CERT) < 20000:
                CERT.append({"n": n, "rows": [int(sum(1 << q for q in range(n) if A[u, q])) for u in range(n)],
                             "m": mi, "x": [int(t) for t in x]})
            return True
    return False


def stage_D(e, label):
    rows = e["rows"]
    A47 = np.array([[(rows[u] >> v) & 1 for v in range(47)] for u in range(47)], dtype=np.int64)
    tau = reps[e["tau"]]
    mem = set(k for o in e["F"] for k in (o, tau[o]))
    a2 = [int(A47[19 + u, 19:37].sum()) for u in range(28)]          # items: X_2 vertex k = item k, W vertex x = item 18 + x
    t = sum(a2[:18]) // 2
    need = [a2[u] + 2 - (1 if u in mem else 0) if u < 18 else a2[u] - 2 for u in range(28)]
    sig = [tau[u] if u < 18 else 18 + ((u - 18) ^ 1) for u in range(28)]
    cn = A47 @ A47
    stats = {"t": t, "gen_nodes": 0, "cand_raw": 0, "cand_budget_ok": 0, "cand_psd_ok": 0, "covers": 0, "G": 0,
             "full_budget_ok": 0, "full_psd_ok": 0, "ambiguous": 0}
    assert sum(need[:18]) == 32 + 2 * t and all(x >= 0 for x in need)
    pair_ok = [[(u != v) and cn[19 + u, 19 + v] + 1 <= 2 - A47[19 + u, 19 + v] for v in range(28)] for u in range(28)]
    cands = []                                                      # (Z tuple, sigma Z tuple)
    def consider(Z):
        stats["cand_raw"] += 1
        sZ = tuple(sorted(sig[u] for u in Z))
        Zt = tuple(Z)
        if Zt > sZ:
            return                                                  # the mate will be generated as its own candidate
        use = [0] * 28
        for u in Zt:
            use[u] += 1
        for u in sZ:
            use[u] += 1
        if any(use[u] > need[u] for u in range(28)) or len(set(Zt) & set(sZ)) > 2:
            return
        A = np.zeros((49, 49), dtype=np.int64)
        A[:47, :47] = A47
        for u in Zt:
            A[47, 19 + u] = A[19 + u, 47] = 1
        for u in sZ:
            A[48, 19 + u] = A[19 + u, 48] = 1
        if not budgets_ok(A):
            return
        stats["cand_budget_ok"] += 1
        if psd_reject(A, stats, True):
            return
        stats["cand_psd_ok"] += 1
        cands.append((Zt, sZ, use))
    def gen(start, Z, cnt, nx2, nspec):
        stats["gen_nodes"] += 1
        if nx2 >= 4 and nspec == 2:
            consider(Z)
        for u in range(start, 28):
            if need[u] < 1:
                continue
            spec = (u >= 18) or (u in mem)
            if spec and nspec >= 2:
                continue
            if u < 18 and nx2 >= 4 + t:
                continue
            if any(not pair_ok[u][v] for v in Z):
                continue
            cnt2 = cnt + A47[19 + u]
            if (cnt2 > 2).any():
                continue
            gen(u + 1, Z + [u], cnt2, nx2 + (1 if u < 18 else 0), nspec + (1 if spec else 0))
    gen(0, [], np.zeros(47, dtype=np.int64), 0, 0)
    # ---- D2: exact covers by 4 mate pairs
    by_item = {u: [] for u in range(28)}
    for ci, (Zt, sZ, use) in enumerate(cands):
        for u in range(28):
            if use[u]:
                by_item[u].append(ci)
    covers = set()
    def cover(chosen, rem):
        if len(chosen) == 4:
            if not any(rem):
                covers.add(frozenset(chosen))
            return
        try:
            u = next(q for q in range(28) if rem[q] > 0)
        except StopIteration:
            return
        for ci in by_item[u]:
            if ci in chosen:
                continue
            Zt, sZ, use = cands[ci]
            if any(use[q] > rem[q] for q in range(28)):
                continue
            ok = True
            for cj in chosen:
                Z2, sZ2, _ = cands[cj]
                for a in (Zt, sZ):
                    for b in (Z2, sZ2):
                        if len(set(a) & set(b)) > 2:
                            ok = False
            if ok:
                cover(chosen + [ci], [rem[q] - use[q] for q in range(28)])
    cover([], need[:])
    stats["covers"] = len(covers)
    survivors = []
    for cov in covers:
        cl = sorted(cov)
        deg = [sum(1 for u in cands[ci][0] if u < 18) - 4 for ci in cl]
        base = np.zeros((55, 55), dtype=np.int64)
        base[:47, :47] = A47
        for q, ci in enumerate(cl):
            Zt, sZ, _ = cands[ci]
            for u in Zt:
                base[47 + 2 * q, 19 + u] = base[19 + u, 47 + 2 * q] = 1
            for u in sZ:
                base[48 + 2 * q, 19 + u] = base[19 + u, 48 + 2 * q] = 1
        pairs = list(itertools.combinations(range(4), 2))
        for st in itertools.product((0, 1, 2, 3), repeat=6):
            d = [0] * 4
            for (q, r), x in zip(pairs, st):
                w = (0, 1, 1, 2)[x]
                d[q] += w; d[r] += w
            if d != deg:
                continue
            stats["G"] += 1
            A = base.copy()
            for (q, r), x in zip(pairs, st):
                if x & 1:
                    for u, v in ((47 + 2 * q, 47 + 2 * r), (48 + 2 * q, 48 + 2 * r)):
                        A[u, v] = A[v, u] = 1
                if x & 2:
                    for u, v in ((47 + 2 * q, 48 + 2 * r), (48 + 2 * q, 47 + 2 * r)):
                        A[u, v] = A[v, u] = 1
            if not budgets_ok(A):
                continue
            stats["full_budget_ok"] += 1
            if psd_reject(A, stats, True):
                continue
            stats["full_psd_ok"] += 1
            survivors.append({"tau": e["tau"], "F": e["F"], "types": e["types"],
                              "rows": [int(sum(1 << q for q in range(55) if A[u, q])) for u in range(55)]})
    print(f"{label}: matching #{e['tau']}, F = {e['F']}: {stats}   [{time.time() - T0:.0f}s]", flush=True)
    return stats, survivors, [(c[0], c[1]) for c in cands]


if __name__ == "__main__":
    seen = set()
    allsurv = []; allstats = []
    for fn in sys.argv[2:]:
        d = json.load(open(os.path.join(HERE, fn)))
        for e in d["survivors"]:
            key = tuple(e["rows"])
            if key in seen:
                continue
            seen.add(key)
            st, sv, cands = stage_D(e, f"survivor {len(seen)}")
            allstats.append({"tau": e["tau"], "F": e["F"], "stats": st, "candidates": cands})
            allsurv += sv
    print(f"stage D: {len(seen)} configurations on 47 vertices examined, {len(allsurv)} configurations on 55 vertices left; "
          f"certificates saved {len(CERT)}")
    tag = os.environ.get("R4_TAG", f"B{s_idx}")
    json.dump({"stats": allstats, "survivors": allsurv}, open(os.path.join(HERE, f"r4_stageD_{tag}.json"), "w"))
    with open(os.path.join(HERE, f"r4cert_stageD_{tag}.jsonl"), "w") as f:
        for c in CERT:
            f.write(json.dumps(c, separators=(",", ":")) + "\n")
