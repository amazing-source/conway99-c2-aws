# Round 3.  Profile (2,5,0) (h_2 = 2, h_1 = 5, h_0 = 0), case n_3 = 0.   Self-contained (numpy only).
#
# Forced (report, A14): A_p = N(p) n X_2 = two adjacent mate pairs, no edge between the two pairs, no neighbour in W;
# W = N(p) n X_1 = five mate pairs w_c = (i_c ; j_c), sigma w_c = (j_c ; i_c), a(w) >= 2, no X_0 neighbour of w except p
# counted in c(w) = a(w) - 1; every vertex s of X_2 outside A_p has exactly 2 - |N(s) n A_p| neighbours in W;
# sum_{A_p} (a - 1) + sum_W (a - 2) = 8;  a <= 4 on X_2;  no X_0 vertex other than p in N(p).
#
# Stage B: all sigma-invariant H = A[X_2] such that S u {p} u X_2 (37 vertices) passes budgets + PSD.
# Stage C: add W (types and X_2-neighbourhoods): S u {p} u X_2 u W (47 vertices), budgets + PSD at every step.
# Every rejection is exact: a pair (u,v) with too many common neighbours, or an integer vector x with x^T M x < 0 for
# M = 9(3I-A)+J or 11(4I+A)-2J restricted to the tested vertex set.  If no such vector is found the node is KEPT.
# PSD certificates are written to r3cert_<tag>_*.jsonl  (one JSON object per line: n, rows, m, x).
# usage: python r3_p250.py <structure> <part> <nparts> <time limit s> [stages: B or BC]
import json, os, sys, itertools, time
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0
STAGES = sys.argv[5] if len(sys.argv) > 5 else "BC"
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
B = [[1 if (m[i][j] & 1) else 0 for j in range(9)] for i in range(9)]
Bn = [set(j for j in range(9) if B[i][j]) for i in range(9)]
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(d) for d in td["DEF"]]
reps = td["reps"]
AT1 = set(); AS1 = set()
for Np, Nm, flag in types[name]:
    if flag and len(Np) == 2:
        AT1.add((tuple(Np), tuple(Nm)))
    if flag and len(Np) == 1:
        AS1.add((Np[0], Nm[0]))
pc = int.bit_count
t0 = time.time()
TAG = f"{si}_{part}of{nparts}"
TOT = {"tau": 0, "tau_done": 0, "F": 0, "F_types_ok": 0, "F_base_ok": 0, "B_nodes": 0, "H_complete": 0, "H_after_counts": 0,
       "type_sols": 0, "type_sols_ok33": 0, "F_W_ok": 0, "C_nb1_tests": 0, "C_nb2_tests": 0, "C_type_solutions": 0, "C_ts_dead_by_counts": 0, "C_forced_tests": 0, "C_nodes": 0, "C_survivors": 0, "H_with_C_survivor": 0,
       "rej_budget": 0, "rej_psd": 0, "psd_tests": 0, "psd_float_neg_no_cert": 0}
P_ = 18
X2 = lambda k: 19 + k
MINY2 = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 14, 6: 20, 7: 26, 8: 32, 9: 42}      # 2 * min sum y_q^2, sum y_q = t, 4 orbits


class CertLog:
    def __init__(self, tag):
        self.tag = tag; self.k = 0; self.f = None; self.size = 0; self.n = 0
    def write(self, rec):
        if self.f is None or self.size > 18_000_000:
            if self.f:
                self.f.close()
            self.f = open(os.path.join(here, f"r3cert_{self.tag}_{self.k}.jsonl"), "w")
            self.k += 1; self.size = 0
        s = json.dumps(rec, separators=(",", ":")) + "\n"
        self.f.write(s); self.size += len(s); self.n += 1
    def close(self):
        if self.f:
            self.f.close()


LOG = CertLog(TAG)
CERTCAP = int(os.environ.get('R3_CERTCAP', '15000'))


def find_neg_vector(M):
    """integer vector x with x^T M x < 0, exact in int64 (|x_i| <= 10^5, |M_ij| <= 44, n <= 55: |x^T M x| < 2*10^15)"""
    w, V = np.linalg.eigh(M.astype(float))
    if w[0] > -1e-7:
        return None
    for col in range(min(3, len(w))):
        if w[col] > -1e-7:
            break
        for scale in (8, 30, 100, 1000, 10 ** 5):
            x = np.rint(scale * V[:, col]).astype(np.int64)
            if int(x @ (M @ x)) < 0:
                return [int(t) for t in x]
    TOT["psd_float_neg_no_cert"] += 1
    return None


def to_matrix(rows, L):
    n = len(L)
    buf = b"".join(rows[u].to_bytes(8, "little") for u in L)
    bits = np.unpackbits(np.frombuffer(buf, dtype=np.uint8).reshape(n, 8), axis=1, bitorder="little")
    return bits[:, L].astype(np.int64)


def graph_ok(rows, L):
    n = len(L)
    A = to_matrix(rows, L)
    C = A @ A
    np.fill_diagonal(C, 0)
    if (C > 2 - A).any():
        TOT["rej_budget"] += 1
        return False
    TOT["psd_tests"] += 1
    for mi, Mx in enumerate((27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2)):
        x = find_neg_vector(Mx)
        if x is not None:
            TOT["rej_psd"] += 1
            if LOG.n < CERTCAP:
                LOG.write({"n": n, "rows": [int(sum(1 << q for q in range(n) if A[u, q])) for u in range(n)], "m": mi, "x": x})
            return False
    return True


def budgets_only(rows, L):
    A = to_matrix(rows, L)
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


SURV = []          # survivors of the last stage run
HLIST = []         # stage B: all (tau, F, H) passing the counting conditions


def process(ti, tau):
    U = [set(DEF[k]) for k in range(18)]
    V = [set(DEF[tau[k]]) for k in range(18)]
    sup = [sum(1 << i for i in U[k]) | sum(1 << (9 + j) for j in V[k]) for k in range(18)]
    R = [[pc(sup[k] & sup[l]) for l in range(18)] for k in range(18)]
    orbs = [k for k in range(18) if k < tau[k]]
    elig = [k for k in orbs if not (U[k] & V[k]) and (DEF[k], DEF[tau[k]]) in AT1]
    def free_at(k, v):
        return not (V[k] & Bn[v]) if v < 9 else not (U[k] & Bn[v - 9])
    def edge_allowed(a, b):
        if b == a or b == tau[a] or R[a][b] > 1:
            return False
        if R[a][b] == 1:
            v = (sup[a] & sup[b]).bit_length() - 1
            return free_at(a, v) and free_at(b, v)
        return True
    def add(rows, u, v):
        rows[u] |= 1 << v; rows[v] |= 1 << u
    base = [0] * 55
    for i in range(9):
        for j in Bn[i]:
            add(base, i, 9 + j)
    for k in range(18):
        for v in range(18):
            if (sup[k] >> v) & 1:
                add(base, X2(k), v)
    def apply(rows, o, o2, s):
        if s & 1:
            add(rows, X2(o), X2(o2)); add(rows, X2(tau[o]), X2(tau[o2]))
        if s & 2:
            add(rows, X2(o), X2(tau[o2])); add(rows, X2(tau[o]), X2(o2))
    def states(o, o2):
        st = [0]
        par = edge_allowed(o, o2); cro = edge_allowed(o, tau[o2])
        if par: st.append(1)
        if cro: st.append(2)
        if par and cro: st.append(3)
        return st
    LS = list(range(18))
    pair_cache = {}
    def pair_states(o, o2, fo, fo2):
        """states between orbits o, o2 passing budgets + PSD on S u o u o2 (22 vertices); fo, fo2 = mate-adjacent flags"""
        key = (o, o2, fo, fo2) if o < o2 else (o2, o, fo2, fo)
        if key in pair_cache:
            return pair_cache[key]
        a, b, fa, fb = key
        good = []
        for s in states(a, b):
            rows = base[:]
            if fa: add(rows, X2(a), X2(tau[a]))
            if fb: add(rows, X2(b), X2(tau[b]))
            apply(rows, a, b, s)
            if graph_ok(rows, LS + [X2(a), X2(tau[a]), X2(b), X2(tau[b])]):
                good.append(s)
        pair_cache[key] = good
        return good
    weight = (0, 1, 1, 2)
    found_any = False
    for Forb in itertools.combinations(elig, 2):
        if time.time() - t0 > tlimit:
            return None
        mem = [k for o in Forb for k in (o, tau[o])]
        if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):
            continue
        f = [sum(1 for k in mem if i in U[k]) for i in range(9)]
        if any(x > 2 for x in f):
            continue
        TOT["F"] += 1
        # ---- W types: 5 unordered pairs {i,j}, admissible single type adjacent to p, degrees = deficits, no repeated pair
        defi = [2 - x for x in f]
        cand_pairs = [(i, j) for i in range(9) for j in range(i + 1, 9) if (i, j) in AS1 and (j, i) in AS1]
        type_sols = []
        def tsol(start, chosen):
            if len(chosen) == 5:
                if all(d == 0 for d in defi):
                    type_sols.append(tuple(chosen))
                return
            for q in range(start, len(cand_pairs)):
                i, j = cand_pairs[q]
                if defi[i] > 0 and defi[j] > 0:
                    defi[i] -= 1; defi[j] -= 1
                    chosen.append((i, j))
                    tsol(q + 1, chosen)
                    chosen.pop()
                    defi[i] += 1; defi[j] += 1
        tsol(0, [])
        if not type_sols:
            continue
        TOT["F_types_ok"] += 1
        rows0 = base[:]
        for k in mem:
            add(rows0, P_, X2(k))
        for o in Forb:
            add(rows0, X2(o), X2(tau[o]))
        L0 = LS + [P_] + [X2(k) for k in mem]
        if not graph_ok(rows0, L0):
            continue
        TOT["F_base_ok"] += 1
        # ---- W prefilters that do not depend on H: single mate pairs (25 vertices), then S u N[p] (33 vertices)
        def wrows(rw, c, i, j):
            w, sw = 37 + 2 * c, 38 + 2 * c
            add(rw, w, P_); add(rw, sw, P_); add(rw, w, sw)
            add(rw, w, i); add(rw, w, 9 + j); add(rw, sw, j); add(rw, sw, 9 + i)
        ts_box = [None]
        def lazy_type_sols():
            if ts_box[0] is None:
                single_ok = {}
                for (i, j) in sorted(set(pr for ts in type_sols for pr in ts)):
                    rw = rows0[:]; wrows(rw, 0, i, j)
                    single_ok[(i, j)] = graph_ok(rw, L0 + [37, 38])
                ts_ok = []
                for ts in type_sols:
                    if not all(single_ok[pr] for pr in ts):
                        continue
                    rw = rows0[:]
                    for c, (i, j) in enumerate(ts):
                        wrows(rw, c, i, j)
                    if graph_ok(rw, L0 + list(range(37, 47))):
                        ts_ok.append(ts)
                TOT["type_sols"] += len(type_sols); TOT["type_sols_ok33"] += len(ts_ok)
                if ts_ok:
                    TOT["F_W_ok"] += 1
                ts_box[0] = ts_ok
            return ts_box[0]
        rest = [o for o in orbs if o not in Forb]                    # 7 orbits
        prev_all = list(Forb)
        Hs = []
        # depth-first: orbit by orbit; for each new orbit, states to the two F orbits and to the earlier orbits,
        # chosen one at a time with the (monotone) budget test; PSD once the orbit is complete.
        def rec(a, rows, L, flinks):
            if time.time() - t0 > tlimit:
                return
            if a == len(rest):
                Hs.append(rows[:])
                return
            o = rest[a]
            La = L + [X2(o), X2(tau[o])]
            prev = list(Forb) + rest[:a]
            def choose(b, r2, deg, fl):
                if b == len(prev):
                    TOT["B_nodes"] += 1
                    if graph_ok(r2, La):
                        rec(a + 1, r2, La, fl)
                    return
                o2 = prev[b]
                isF = o2 in Forb
                for s in pair_states(o, o2, False, isF):
                    w = weight[s]
                    if deg + w > 4:
                        continue
                    if isF and fl + w > 4:
                        continue
                    if s == 0:
                        choose(b + 1, r2, deg, fl)
                        continue
                    # degree cap on the other side
                    if pc(r2[X2(o2)] >> 19) + w > 4 or pc(r2[X2(tau[o2])] >> 19) + w > 4:
                        continue
                    r3 = r2[:]
                    apply(r3, o, o2, s)
                    if budgets_only(r3, La):
                        choose(b + 1, r3, deg + w, fl + (w if isF else 0))
            choose(0, rows, 0, flinks)
        rec(0, rows0, L0, 0)
        TOT["H_complete"] += len(Hs)
        L37 = list(range(37))
        for rows in Hs:
            degs = [pc(rows[X2(k)] >> 19) for k in range(18)]
            t = sum(degs) // 2
            D = sum(d * (d - 1) for d in degs)
            fl = sum(degs[k] - 1 for k in mem)
            if t > 9 or fl > 8 or D + MINY2[t] > 36:
                continue
            TOT["H_after_counts"] += 1
            HLIST.append({"tau": ti, "F": list(Forb), "H": [(rows[X2(k)] >> 19) & ((1 << 18) - 1) for k in range(18)]})
            if "C" not in STAGES:
                SURV.append({"tau": ti, "F": list(Forb), "H": [(rows[X2(k)] >> 19) & ((1 << 18) - 1) for k in range(18)]})
                found_any = True
                continue
            # ---------------- stage C: the five mate pairs of W
            req = [0] * 18
            for k in range(18):
                if k not in mem:
                    req[k] = 2 - sum(1 for q in mem if (rows[X2(k)] >> X2(q)) & 1)
            slack = 4 - fl // 2
            Hgot = False
            nb1_cache = {}; nb2_cache = {}; first_cache = {}
            def nb1(i, j):
                if (i, j) not in nb1_cache:
                    good = []
                    for k in range(18):
                        if req[k] > 0 and req[tau[k]] > 0:
                            TOT["C_nb1_tests"] += 1
                            rw = rows[:]; wrows(rw, 0, i, j)
                            add(rw, 37, X2(k)); add(rw, 38, X2(tau[k]))
                            if graph_ok(rw, L0 + [X2(k), X2(tau[k]), 37, 38]):
                                good.append(k)
                    nb1_cache[(i, j)] = good
                return nb1_cache[(i, j)]
            forced_cache = {}
            def forced(i, j):
                if (i, j) not in forced_cache:
                    fo = []
                    for k in range(18):
                        if k < tau[k] and k not in mem:
                            TOT["C_forced_tests"] += 1
                            rw = rows[:]; wrows(rw, 0, i, j)
                            if not graph_ok(rw, L0 + [X2(k), X2(tau[k]), 37, 38]):
                                fo.append(k)
                    forced_cache[(i, j)] = fo
                return forced_cache[(i, j)]
            def nb2(i, j, k, k2):
                key = (i, j, min(k, k2), max(k, k2))
                if key not in nb2_cache:
                    TOT["C_nb2_tests"] += 1
                    rw = rows[:]; wrows(rw, 0, i, j)
                    add(rw, 37, X2(k)); add(rw, 38, X2(tau[k])); add(rw, 37, X2(k2)); add(rw, 38, X2(tau[k2]))
                    nb2_cache[key] = graph_ok(rw, L0 + [X2(k), X2(tau[k]), X2(k2), X2(tau[k2]), 37, 38])
                return nb2_cache[key]
            for ts in lazy_type_sols():
                TOT["C_type_solutions"] += 1
                rw = rows[:]
                for c, (i, j) in enumerate(ts):
                    wrows(rw, c, i, j)
                if any(len(nb1(i, j)) < 2 for (i, j) in ts):
                    TOT["C_ts_dead_by_counts"] += 1
                    continue
                dead = False
                for (i, j) in ts:
                    fo = forced(i, j)
                    if len(fo) > 2 + slack or any((k not in nb1(i, j)) and (tau[k] not in nb1(i, j)) for k in fo):
                        dead = True; break
                for k in range(18):
                    if dead:
                        break
                    if req[k] > 0:
                        # w_c may see k iff k in nb1(type c); sigma w_c may see k iff tau k in nb1(type c); not both
                        avail = sum(1 for (i, j) in ts if (k in nb1(i, j)) or (tau[k] in nb1(i, j)))
                        if avail < req[k]:
                            dead = True; break
                if dead:
                    TOT["C_ts_dead_by_counts"] += 1
                    continue
                def recW(c, r2, L, rq, sl):
                    nonlocal Hgot
                    if time.time() - t0 > tlimit:
                        return
                    if c == 5:
                        if any(rq):
                            return
                        TOT["C_survivors"] += 1
                        Hgot = True
                        SURV.append({"tau": ti, "F": list(Forb), "types": [list(x) for x in ts],
                                     "rows": r2[:47]})
                        return
                    w, sw = 37 + 2 * c, 38 + 2 * c
                    Lc = L + [w, sw]
                    remaining_pairs = 5 - c - 1
                    ti_, tj_ = ts[c]
                    cands = [k for k in nb1(ti_, tj_) if rq[k] > 0 and rq[tau[k]] > 0]
                    def pick(start, r3, chosen, rq2):
                        size = len(chosen)
                        if size >= 2 and all((k in chosen) or (tau[k] in chosen) for k in forced(ti_, tj_)):
                            # remaining requirement must be coverable by the remaining pairs
                            remsum = sum(rq2)
                            if remsum >= 4 * remaining_pairs and remsum <= 4 * remaining_pairs + 2 * (sl - (size - 2)):
                                if c == 0:
                                    ck = (ts[0], tuple(sorted(chosen)))
                                    if ck not in first_cache:
                                        TOT["C_nodes"] += 1
                                        first_cache[ck] = graph_ok(r3, Lc)
                                    okc = first_cache[ck]
                                else:
                                    TOT["C_nodes"] += 1
                                    okc = graph_ok(r3, Lc)
                                if okc:
                                    recW(c + 1, r3, Lc, rq2, sl - (size - 2))
                        if size >= 2 + sl:
                            return
                        for q in range(start, len(cands)):
                            k = cands[q]
                            if rq2[k] <= 0 or rq2[tau[k]] <= 0 or tau[k] in chosen or k in chosen:
                                continue
                            if not all(nb2(ti_, tj_, k, k0) for k0 in chosen):
                                continue
                            r4 = r3[:]
                            add(r4, w, X2(k)); add(r4, sw, X2(tau[k]))
                            if not budgets_only(r4, Lc):
                                continue
                            rq3 = rq2[:]
                            rq3[k] -= 1; rq3[tau[k]] -= 1
                            pick(q + 1, r4, chosen + [k], rq3)
                    pick(0, r2, [], rq)
                recW(0, rw, L37, req, slack)
            if Hgot:
                TOT["H_with_C_survivor"] += 1
                found_any = True
    return found_any


my = [(q, r) for q, r in enumerate(reps) if q % nparts == part]
if os.environ.get("R3_IDX"):
    my = [(int(i), reps[int(i)]) for i in os.environ["R3_IDX"].split(",")]
    TAG = TAG + "_idx" + os.environ["R3_IDX"].split(",")[0]
    LOG.tag = TAG
TOT["tau"] = len(my)
timed_out = False
tau_alive = []
for ti, tau in my:
    r = process(ti, tau)
    if r is None:
        timed_out = True
        break
    TOT["tau_done"] += 1
    if r:
        tau_alive.append(ti)
    if TOT["tau_done"] % 10 == 0:
        print(f"  [{time.time() - t0:.0f}s] {TOT}", flush=True)
LOG.close()
print(f"{name} profile (2,5,0) stages {STAGES} part {part}/{nparts}: time {time.time() - t0:.1f}s timed_out={timed_out}")
print("  totals:", TOT)
print("  PSD certificates written:", LOG.n, " survivors of the last stage:", len(SURV), " in matchings:", len(tau_alive))
json.dump({"name": name, "profile": "250", "stages": STAGES, "part": part, "nparts": nparts, "totals": TOT,
           "timed_out": timed_out, "tau_alive": tau_alive, "survivors": SURV[:200000], "n_cert": LOG.n,
           "H_stageB": HLIST},
          open(os.path.join(here, f"r3_p250_{TAG}_{STAGES}.json"), "w"))
