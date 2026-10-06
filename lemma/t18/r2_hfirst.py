# Round 2, profile (3,3,1) (h_2 = 3, h_0 = 1), case n_3 = 0.  "H first".
# By A10 the following vertex set is COMPLETELY determined by (tau, F, H, A_z0):
#     Y1 = S u {p} u X_2 u {z_0, sigma z_0}          (18 + 1 + 18 + 2 = 39 vertices)
#   tau  : matching of the 18 deficient pairs (orbit representatives under Aut(B))
#   F    : the 3 sigma-orbits of X_2 inside N(p); their vertices have no X_2 neighbour except the mate
#   H    : the edges between the other 12 vertices of X_2 (sigma-invariant; per pair of orbits: none / parallel /
#          crossed / both)
#   A_z0 : the 6 neighbours of z_0 in X_2 = one vertex in each of the 6 orbits outside F (A_p, A_z0, A_sigma z0
#          partition X_2); z_0 ~ p, z_0 ~ sigma z_0, and z_0 has no other neighbour in Y1.
# Tests (all exact): common-neighbour budgets |N(u) n N(v)| <= 2 - A_uv on every determined induced subgraph met
# during the construction, and positive semidefiniteness of 9(3I-A)+J and 11(4I+A)-2J (integer certificate for
# each rejection, exact elimination in the doubtful cases).
# usage: python r2_hfirst.py <structure> <part> <nparts> <time limit s>
import json, os, sys, itertools, time
import numpy as np
from enum_S import neg_certificate
from latt import psd_exact

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0
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
pc = lambda x: bin(x).count("1")
t0 = time.time()
# cross-check mode: R2_NOPSD=1 switches the PSD test off (budgets only); output goes to a separate file
NOPSD = os.environ.get("R2_NOPSD") == "1"
TOT = {"tau": 0, "tau_done": 0, "F": 0, "F_after_pairs": 0, "H_nodes": 0, "H_complete": 0, "z0_tested": 0,
       "survivors": 0, "tau_with_survivor": 0, "psd_calls": 0, "exact_calls": 0,
       "rej_budget": 0, "rej_certificate": 0, "rej_exact_elimination_only": 0}
survivors = []
P_ = 18
X2 = lambda k: 19 + k
Z0, Z1 = 37, 38


def graph_ok(rows, L):
    """budgets + exact PSD on the induced subgraph on the vertex list L"""
    mask = 0
    for v in L:
        mask |= 1 << v
    for a in range(len(L)):
        ru = rows[L[a]] & mask
        for b in range(a + 1, len(L)):
            c = pc(ru & rows[L[b]])
            if c > 2 or (c > 1 and (ru >> L[b]) & 1):
                TOT["rej_budget"] += 1
                return False
    if NOPSD:
        return True
    n = len(L)
    A = np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)
    TOT["psd_calls"] += 1
    for Mx in (27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2):
        w = np.linalg.eigvalsh(Mx.astype(float))[0]
        if w > -1e-7:
            continue
        if neg_certificate(Mx.tolist()) is not None:
            TOT["rej_certificate"] += 1
            return False
        TOT["exact_calls"] += 1
        if not psd_exact(Mx.tolist())[0]:
            TOT["rej_exact_elimination_only"] += 1
            return False
    return True


def process(tau):
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
    base = [0] * 39
    def add(rows, u, v):
        rows[u] |= 1 << v; rows[v] |= 1 << u
    for i in range(9):
        for j in Bn[i]:
            add(base, i, 9 + j)
    for k in range(18):
        for v in range(18):
            if (sup[k] >> v) & 1:
                add(base, X2(k), v)
    found = False
    for Forb in itertools.combinations(elig, 3):
        if time.time() - t0 > tlimit:
            return None
        mem = [k for o in Forb for k in (o, tau[o])]
        if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):
            continue
        f = [sum(1 for k in mem if i in U[k]) for i in range(9)]
        if any(x > 2 for x in f):
            continue
        defi = [2 - x for x in f]
        def x1pairs(chosen):
            if all(d == 0 for d in defi):
                return len(chosen) == 3
            if len(chosen) >= 3:
                return False
            i = next(q for q in range(9) if defi[q] > 0)
            for j in range(9):
                if j == i or defi[j] <= 0 or (i, j) not in AS1:
                    continue
                ok = True
                for k in mem:
                    if (i in U[k]) + (j in V[k]) > 1 or (j in U[k]) + (i in V[k]) > 1:
                        ok = False; break
                if ok:
                    for (a2, b2) in chosen:
                        if (i == a2) + (j == b2) > 1 or (i == b2) + (j == a2) > 1:
                            ok = False; break
                if ok:
                    defi[i] -= 1; defi[j] -= 1
                    chosen.append((i, j))
                    r = x1pairs(chosen)
                    chosen.pop()
                    defi[i] += 1; defi[j] += 1
                    if r:
                        return True
            return False
        if not x1pairs([]):
            continue
        TOT["F"] += 1
        rows0 = base[:]
        for k in mem:
            add(rows0, P_, X2(k))
        for o in Forb:
            add(rows0, X2(o), X2(tau[o]))
        L0 = list(range(18)) + [P_] + [X2(k) for k in mem]
        if not graph_ok(rows0, L0):
            continue
        rest = [o for o in orbs if o not in Forb]                  # 6 orbits
        def states(o, o2):
            st = [0]
            par = edge_allowed(o, o2); cro = edge_allowed(o, tau[o2])
            if par: st.append(1)
            if cro: st.append(2)
            if par and cro: st.append(3)
            return st
        def apply(rows, o, o2, s):
            if s & 1:
                add(rows, X2(o), X2(o2)); add(rows, X2(tau[o]), X2(tau[o2]))
            if s & 2:
                add(rows, X2(o), X2(tau[o2])); add(rows, X2(tau[o]), X2(o2))
        # pair prefilter
        allowed = {}
        dead = False
        for a in range(6):
            La = L0 + [X2(rest[a]), X2(tau[rest[a]])]
            if not graph_ok(rows0, La):
                dead = True; break
            for b in range(a + 1, 6):
                good = []
                for s in states(rest[b], rest[a]):
                    rows = rows0[:]
                    apply(rows, rest[b], rest[a], s)
                    if graph_ok(rows, La + [X2(rest[b]), X2(tau[rest[b]])]):
                        good.append(s)
                if not good:
                    dead = True; break
                allowed[(a, b)] = good
            if dead:
                break
        if dead:
            continue
        TOT["F_after_pairs"] += 1
        Hs = []
        def rec(a, rows, L):
            if time.time() - t0 > tlimit:
                return
            if a == 6:
                Hs.append(rows[:])
                return
            La = L + [X2(rest[a]), X2(tau[rest[a]])]
            for combo in itertools.product(*[allowed[(b, a)] for b in range(a)]):
                TOT["H_nodes"] += 1
                r2 = rows[:]
                for b in range(a):
                    apply(r2, rest[a], rest[b], combo[b])
                # degree caps inside X_2
                if any(pc(r2[X2(k)] >> 19) > 4 for k in (rest[a], tau[rest[a]])):
                    continue
                if graph_ok(r2, La):
                    rec(a + 1, r2, La)
        rec(0, rows0, L0)
        TOT["H_complete"] += len(Hs)
        Lfull = list(range(37))
        for rows in Hs:
            if sum(pc(rows[X2(k)] >> 19) * (pc(rows[X2(k)] >> 19) - 1) for k in range(18)) > 24:
                continue
            # A_z0: one vertex per orbit of `rest`; z_0 named so that it sees rest[0]
            for choice in itertools.product((0, 1), repeat=5):
                Az = [rest[0]] + [rest[q + 1] if choice[q] == 0 else tau[rest[q + 1]] for q in range(5)]
                if any(R[a][b] > 1 for a in Az for b in Az if a != b):
                    continue
                cov = [0] * 18
                for k in Az:
                    for v in range(18):
                        if (sup[k] >> v) & 1:
                            cov[v] += 1
                if max(cov) > 2:
                    continue
                TOT["z0_tested"] += 1
                r2 = rows[:]
                add(r2, Z0, P_); add(r2, Z1, P_); add(r2, Z0, Z1)
                for k in Az:
                    add(r2, Z0, X2(k)); add(r2, Z1, X2(tau[k]))
                if graph_ok(r2, Lfull + [Z0, Z1]):
                    TOT["survivors"] += 1
                    found = True
                    if len(survivors) < int(os.environ.get("R2_CAP", "20")):
                        survivors.append({"tau": list(tau), "F": list(Forb), "rows": r2})
    return found


my = [r for q, r in enumerate(reps) if q % nparts == part]
TOT["tau"] = len(my)
timed_out = False
for tau in my:
    r = process(tau)
    if r is None:
        timed_out = True
        break
    TOT["tau_done"] += 1
    if r:
        TOT["tau_with_survivor"] += 1
    if TOT["tau_done"] % 20 == 0:
        print(f"  [{time.time() - t0:.0f}s] {TOT}", flush=True)
print(f"{name} part {part}/{nparts}: time {time.time() - t0:.1f}s timed_out={timed_out}")
print("  totals:", TOT)
json.dump({"name": name, "part": part, "nparts": nparts, "totals": TOT, "timed_out": timed_out, "survivors": survivors},
          open(os.path.join(here, f"r2_hfirst_{si}_{part}of{nparts}{'_nopsd' if NOPSD else ''}.json"), "w"))
