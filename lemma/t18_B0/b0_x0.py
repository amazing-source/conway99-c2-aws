# B0, profile (2,5,0), n_3 = 0.  "X_0-first" route: SECOND, W-FREE way of testing a stage-B triple (tau, F, H).
# It shares no code with r3_p250.py / r4_stageD.py (numpy only; the graph B0 is re-entered as an edge list).
#
# Determined vertex sets used (hand facts: T18_REPORT A8, A14; N3_REPORT by-product):
#   Y37 = S u {p} u X_2  (given by the triple);
#   a vertex z of X_0 \ {p} has no neighbour in S u {p}, is not adjacent to sigma z, and a_2(z) >= 4; a_2(z) <= 8 and
#   a_2(z) <= 4 + t (sum over the 4 orbits of (a_2 - 4) = t = e(X_2));  |N(z) n A_p| <= 2  (z, p have 2 common neighbours);
#   every s in X_2 has exactly need(s) = a_2(s) + 2 - [s in A_p] neighbours in X_0 \ {p};
#   G = A[X_0 \ {p}] is sigma-invariant, without mate edges, with degrees a_2(z) - 4.
# Hence Y39 = Y37 u {z, sigma z} is determined by Z = N(z) n X_2, and Y45 = S u X_0 u X_2 by the four Z's and G.
# X1: all Z passing the budgets on 38 vertices;   X2: unordered pairs {Z, sigma Z} passing budgets + PSD on Y39 and
#     use <= need;   X3: exact covers of need by 4 pairs;   X4: G;   X5: budgets + PSD on Y45.
# Every rejection is exact: a budget violation (integer matrix product) or an integer vector x with x^T M x < 0
# (M = 9(3I-A)+J or 11(4I+A)-2J, exact integer arithmetic).  "kept" never means "proved PSD".
# usage: python b0_x0.py <part> <nparts> <time limit s> [tag]     (input: b0_stageB_reps.json; log: b0_x0_done_<tag>_<part>of<n>.jsonl)
import json, os, sys, itertools, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
part, nparts, tl = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
tag = sys.argv[4] if len(sys.argv) > 4 else "run"
EDGES0 = "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78"
B = np.zeros((9, 9), dtype=np.int64)
for ed in EDGES0.split():
    B[int(ed[0]), int(ed[1])] = B[int(ed[1]), int(ed[0])] = 1
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if (B @ B)[a, b] == 1]
td = json.load(open(os.path.join(HERE, "r2_tau_0.json")))
assert [tuple(d) for d in td["DEF"]] == DEF
reps = td["reps"]
T0 = time.time()
AMBIG = [0]


def budgets_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


def psd_violated(A):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    for M in (27 * I - 9 * A + 1, 44 * I + 11 * A - 2):
        w, V = np.linalg.eigh(M.astype(np.float64))
        if w[0] < -1e-7:
            for col in (0, 1):
                if w[col] > -1e-7:
                    break
                for sc in (9, 40, 300, 5000, 10 ** 5):
                    x = np.rint(sc * V[:, col]).astype(np.int64)
                    if int(x @ (M @ x)) < 0:          # |x_i| <= 10^5, |M_ij| <= 44, n <= 45: no overflow
                        return True
            AMBIG[0] += 1
    return False


class Border:
    """Fast search of integer certificates for the bordered matrices M(Y u {z, sigma z}), Y = Y37 fixed.
    Floats are used only to GUESS a vector; a rejection is accepted only after the exact integer check x^T M x < 0."""
    def __init__(self, A):
        n = A.shape[0]
        I = np.eye(n, dtype=np.int64)
        self.n = n
        self.M = [27 * I - 9 * A + 1, 44 * I + 11 * A - 2]
        self.P = []; self.K = []
        self.usable = True
        for M in self.M:
            w, V = np.linalg.eigh(M.astype(np.float64))
            if w[0] < -1e-7:
                self.usable = False
            pos = w > 1e-6
            self.P.append((V[:, pos] / w[pos]) @ V[:, pos].T)
            self.K.append(V[:, ~pos])

    def certificate(self, A2):
        """A2 = adjacency matrix (integers) of Y u {z, sigma z}, the two new vertices last.
        True iff an integer x with x^T M x < 0 is found, M = 9(3I-A2)+J or 11(4I+A2)-2J built from A2 itself."""
        if not self.usable:
            return False
        n = self.n
        I2 = np.eye(n + 2, dtype=np.int64)
        for m, Mi in enumerate((27 * I2 - 9 * A2 + 1, 44 * I2 + 11 * A2 - 2)):
            assert (Mi[:n, :n] == self.M[m]).all()
            C = Mi[:n, n:].astype(np.float64)
            D = Mi[n:, n:].astype(np.float64)
            PC = self.P[m] @ C
            S = D - C.T @ PC
            Kc = self.K[m].T @ C                            # kernel components of the two columns
            trials = []
            w2, V2 = np.linalg.eigh(S)
            if w2[0] < -1e-6:
                y = V2[:, 0]
                trials.append(np.concatenate((-PC @ y, y)))
            for y in ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, -1.0)):
                y = np.array(y)
                gk = Kc @ y
                g2 = float(gk @ gk)
                if g2 > 1e-8:
                    q0 = float(y @ S @ y)
                    trials.append(np.concatenate((-PC @ y - ((max(q0, 0.0) + 5.0) / g2) * (self.K[m] @ gk), y)))
            for x in trials:
                x = x / np.abs(x).max()
                for sc in (30, 1000, 10 ** 5):               # |x_i| <= 10^5, |M_ij| <= 44, n + 2 <= 39: exact in int64
                    xi = np.rint(sc * x).astype(np.int64)
                    if int(xi @ (Mi @ xi)) < 0:
                        return True
        return False


GTABLE = {}
_pairs4 = list(itertools.combinations(range(4), 2))
for _st in itertools.product((0, 1, 2, 3), repeat=6):
    _d = [0] * 4
    for (_q, _r), _x in zip(_pairs4, _st):
        _w = (0, 1, 1, 2)[_x]
        _d[_q] += _w; _d[_r] += _w
    GTABLE.setdefault(tuple(_d), []).append(_st)
FAST = os.environ.get("B0_X0_SLOW") is None


def do_triple(e):
    tau = reps[e["tau"]]
    F = e["F"]; H = e["H"]
    mem = set(k for o in F for k in (o, tau[o]))
    A = np.zeros((37, 37), dtype=np.int64)
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
    assert (A == A.T).all() and all(A[19 + k, 19 + tau[k]] == (1 if k in mem else 0) for k in range(18))
    assert budgets_ok(A)
    a2 = [int(A[19 + k, 19:].sum()) for k in range(18)]
    t = sum(a2) // 2
    need = [a2[k] + 2 - (1 if k in mem else 0) for k in range(18)]
    assert sum(need) == 32 + 2 * t
    cn = A @ A
    rows = [A[19 + k] for k in range(18)]
    bad = [[(k != l) and (cn[19 + k, 19 + l] + A[19 + k, 19 + l] >= 2) for l in range(18)] for k in range(18)]
    amax = min(8, 4 + t)
    st = {"t": t, "x1_nodes": 0, "x1_Z": 0, "x2_pairs_budget": 0, "x2_fast_cert": 0, "x2_pairs_psd": 0, "x3_covers": 0, "x4_G": 0,
          "x5_budget": 0, "x5_psd": 0}
    Zs = []
    def gen(start, Z, cnt, nap):
        st["x1_nodes"] += 1
        if len(Z) >= 4:
            # exact 38-vertex condition: |Z n N(v)| <= 2 - [v in Z]
            if all(cnt[19 + k] <= 1 for k in Z):
                Zs.append(tuple(Z))
        if len(Z) == amax:
            return
        for u in range(start, 18):
            if need[u] < 1 or (u in mem and nap >= 2):
                continue
            if any(bad[u][v] for v in Z):
                continue
            c2 = cnt + rows[u]
            if (c2 > 2).any():
                continue
            gen(u + 1, Z + [u], c2, nap + (1 if u in mem else 0))
    gen(0, [], np.zeros(37, dtype=np.int64), 0)
    st["x1_Z"] = len(Zs)
    Zset = set(Zs)
    cands = []
    border = Border(A) if FAST else None
    for Z in Zs:
        sZ = tuple(sorted(tau[k] for k in Z))
        if Z > sZ or sZ not in Zset:
            continue
        use = [0] * 18
        for k in Z:
            use[k] += 1
        for k in sZ:
            use[k] += 1
        if any(use[k] > need[k] for k in range(18)):
            continue
        A2 = np.zeros((39, 39), dtype=np.int64)
        A2[:37, :37] = A
        for k in Z:
            A2[37, 19 + k] = A2[19 + k, 37] = 1
        for k in sZ:
            A2[38, 19 + k] = A2[19 + k, 38] = 1
        if not budgets_ok(A2):
            continue
        st["x2_pairs_budget"] += 1
        if FAST and border.certificate(A2):
            st["x2_fast_cert"] += 1
            continue
        if psd_violated(A2):
            continue
        st["x2_pairs_psd"] += 1
        cands.append((Z, sZ, use))
    # ---- exact covers by 4 mate pairs
    covers = []
    if len(cands) >= 4:
        by_item = [[ci for ci, c in enumerate(cands) if c[2][k]] for k in range(18)]
        compat = {}
        def comp(ci, cj):
            key = (ci, cj) if ci < cj else (cj, ci)
            if key not in compat:
                compat[key] = not any(len(set(a) & set(b)) > 2 for a in cands[ci][:2] for b in cands[cj][:2])
            return compat[key]
        visited = set()
        def cover(chosen, rem, dbl):
            key = tuple(sorted(chosen))
            if key in visited:
                return
            visited.add(key)
            if len(chosen) == 4:
                if not any(rem):
                    covers.append(key)
                return
            k0 = next((k for k in range(18) if rem[k] > 0), None)
            if k0 is None:
                return
            if sum(rem) < 8 * (4 - len(chosen)):          # each remaining pair uses at least 2 * 4 incidences
                return
            for ci in by_item[k0]:
                if ci in chosen:
                    continue
                Z, sZ, use = cands[ci]
                if any(use[k] > rem[k] for k in range(18)):
                    continue
                if any(use[k] == 2 and dbl[k] for k in range(18)):   # N(s) contains at most one full sigma-orbit of X_0
                    continue
                if not all(comp(ci, cj) for cj in chosen):
                    continue
                cover(chosen + [ci], [rem[k] - use[k] for k in range(18)], [dbl[k] or use[k] == 2 for k in range(18)])
        cover([], need[:], [False] * 18)
    covers = sorted(set(tuple(sorted(c)) for c in covers))
    st["x3_covers"] = len(covers)
    alive = []
    pairs = list(itertools.combinations(range(4), 2))
    for cov in covers:
        deg = [len(cands[ci][0]) - 4 for ci in cov]
        base = np.zeros((45, 45), dtype=np.int64)
        base[:37, :37] = A
        for q, ci in enumerate(cov):
            Z, sZ, _ = cands[ci]
            for k in Z:
                base[37 + 2 * q, 19 + k] = base[19 + k, 37 + 2 * q] = 1
            for k in sZ:
                base[38 + 2 * q, 19 + k] = base[19 + k, 38 + 2 * q] = 1
        for stt in GTABLE.get(tuple(deg), []):
            st["x4_G"] += 1
            A5 = base.copy()
            for (q, r), x in zip(pairs, stt):
                if x & 1:
                    for u, v in ((37 + 2 * q, 37 + 2 * r), (38 + 2 * q, 38 + 2 * r)):
                        A5[u, v] = A5[v, u] = 1
                if x & 2:
                    for u, v in ((37 + 2 * q, 38 + 2 * r), (38 + 2 * q, 37 + 2 * r)):
                        A5[u, v] = A5[v, u] = 1
            if not budgets_ok(A5):
                continue
            st["x5_budget"] += 1
            if psd_violated(A5):
                continue
            st["x5_psd"] += 1
            alive.append({"Z": [list(cands[ci][0]) for ci in cov], "G": list(stt)})
    return st, alive


if __name__ == "__main__":
    R = json.load(open(os.path.join(HERE, os.environ.get("B0_REPS", "b0_stageB_reps.json"))))
    done = set()
    for fn in os.listdir(HERE):
        if fn.startswith("b0_x0_done_") and fn.endswith(".jsonl"):
            for line in open(os.path.join(HERE, fn)):
                if line.strip():
                    done.add(json.loads(line)["idx"])
    mine = [i for i in range(len(R)) if i % nparts == part and i not in done]
    if os.environ.get("B0_TAKE"):
        mine = mine[:int(os.environ["B0_TAKE"])]
    log = open(os.path.join(HERE, f"b0_x0_done_{tag}_{part}of{nparts}.jsonl"), "a")
    tot = {}
    n_done = 0; n_alive = 0; timed_out = False
    for i in mine:
        if time.time() - T0 > tl:
            timed_out = True
            break
        st, alive = do_triple(R[i])
        for k, v in st.items():
            if k != "t":
                tot[k] = tot.get(k, 0) + v
        n_done += 1; n_alive += bool(alive)
        log.write(json.dumps({"idx": i, "tau": R[i]["tau"], "F": R[i]["F"], "stats": st, "alive": alive}, separators=(",", ":")) + chr(10))
        log.flush()
        if n_done % 50 == 0:
            print(f"  [{time.time() - T0:.0f}s] {n_done} triples, {n_alive} with a Y45 table left; {tot}", flush=True)
    print(f"X_0-first, part {part}/{nparts}, tag {tag}: {n_done} of {len(mine)} triples done, timed_out {timed_out}, "
          f"triples with a table on 45 vertices left: {n_alive}; ambiguous PSD {AMBIG[0]}; {time.time() - T0:.0f}s")
    print("  totals:", tot)
