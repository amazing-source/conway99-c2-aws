# Round 2, stage 2 (case n_3 = 0), adaptation of the Wagner note, sections 3-4.
# For each matching tau of the deficient pairs (r2_tau_<s>.json, orbit representatives under Aut(B)):
#   F : which sigma-orbits of X_2 lie in N(p)            (h_2 = 2, 3 or 4 orbits)
#   C : the sets A_z = N(z) n X_2 for the 8 vertices z of X_0 \ {p} (4 sigma-orbits, h_0 = h_2 - 2 of them in N(p))
#   H : A[X_2],  G : A[X_0]
# and test of the completely determined induced graph on Y = S u X_0 u X_2 (45 vertices):
#       |N_Y(u) n N_Y(v)| <= 2 - A_uv  for every pair.
# Forced numbers used (all proved in the report, Round 2, A8):
#   z in X_0: a_z >= 4, deg_G(z) = a_z - 4;   s in X_2: |N(s) n X_0| = deg_H(s) + 2;
#   sum_{X_0} (a_z - 4)^2 + sum_{X_2} deg_H (deg_H - 1) <= 36;
#   z in X_0 n N(p): z ~ p, z ~ sigma z, a_z >= 6;  p sees exactly the X_2 vertices of F.
# usage: python r2_stage2.py <structure> <part> <nparts> <time limit s>
import json, os, sys, itertools, time
import numpy as np
from enum_S import neg_certificate

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0
# cases h_2 = number of sigma-orbits of X_2 inside N(p): 3 = profile (3,3,1), 2 = profile (2,5,0); h_2 = 4 is excluded (A9)
CASES = [int(c) for c in (sys.argv[5] if len(sys.argv) > 5 else '3')]
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
# optional restriction to the survivors of r2_hfirst.py: env R2_SURV = comma separated json files.
# SURV[tau][F][canonical A_z0] = set of admissible H (tuples of 18 bitmasks)
SURV = None
if os.environ.get('R2_SURV'):
    SURV = {}
    M18 = (1 << 18) - 1
    for f_ in os.environ['R2_SURV'].split(','):
        for s_ in json.load(open(os.path.join(here, f_)))['survivors']:
            rows_ = s_['rows']
            H_ = tuple((rows_[19 + k] >> 19) & M18 for k in range(18))
            A0_ = (rows_[37] >> 19) & M18; A1_ = (rows_[38] >> 19) & M18
            SURV.setdefault(tuple(s_['tau']), {}).setdefault(tuple(s_['F']), {}).setdefault(min(A0_, A1_), set()).add(H_)
curH = [None]
TOT = {"tau": 0, "tau_done": 0, "F": 0, "F_ok_Np": 0, "C": 0, "H": 0, "G": 0, "Y_tables": 0, "tau_with_table": 0,
       "Y_psd_reject": 0, "Y_tables_psd": 0, "tau_with_psd_table": 0}
PSD_HIT = [False]


def psd_ok_rows(rows):
    """exact PSD test of 9(3I-A)+J and 11(4I+A)-2J on the determined graph (integer certificate for a rejection)"""
    n = len(rows)
    A = np.array([[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)], dtype=np.int64)
    for Mx in (27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2):
        if np.linalg.eigvalsh(Mx.astype(float))[0] < -1e-7 and neg_certificate(Mx.tolist()) is not None:
            return False
    return True
timed_out = False
examples = []
rejected = []


def process(tau):
    global timed_out
    U = [set(DEF[k]) for k in range(18)]
    V = [set(DEF[tau[k]]) for k in range(18)]
    sup = [sum(1 << i for i in U[k]) | sum(1 << (9 + j) for j in V[k]) for k in range(18)]
    R = [[pc(sup[k] & sup[l]) for l in range(18)] for k in range(18)]
    tmask = lambda A: sum(1 << tau[k] for k in range(18) if (A >> k) & 1)
    comp = [sum(1 << l for l in range(18) if l != k and R[k][l] <= 1) for k in range(18)]
    elig = [k for k in range(18) if k < tau[k] and not (U[k] & V[k]) and (DEF[k], DEF[tau[k]]) in AT1]
    # free at a support vertex: no triangle {s, P_i, Q_j} through that support vertex
    def free_at(k, v):
        if v < 9:
            return not (V[k] & Bn[v])
        return not (U[k] & Bn[v - 9])
    found_any = False
    # all subsets of X_2 (size 4..9) that are pairwise non-concurrent and cover every support vertex at most twice
    ALLSETS = []
    supl = [[v for v in range(18) if (sup[k] >> v) & 1] for k in range(18)]
    def gen(start, A, size, covs, allowed):
        if size >= 4:
            ALLSETS.append((A, size, tmask(A)))
        if size == 9:
            return
        for k in range(start, 18):
            if not (allowed >> k) & 1:
                continue
            if any(covs[v] >= 2 for v in supl[k]):
                continue
            for v in supl[k]:
                covs[v] += 1
            gen(k + 1, A | (1 << k), size + 1, covs, allowed & comp[k])
            for v in supl[k]:
                covs[v] -= 1
    gen(0, 0, 0, [0] * 18, (1 << 18) - 1)
    TOT["sets"] = TOT.get("sets", 0) + len(ALLSETS)
    for h2 in CASES:
        h0 = h2 - 2; h1 = 7 - h2 - h0
        for Forb in itertools.combinations(elig, h2):
            if time.time() - t0 > tlimit:
                timed_out = True
                return found_any
            if SURV is not None and tuple(Forb) not in SURV.get(tuple(tau), {}):
                continue
            mem = [k for o in Forb for k in (o, tau[o])]
            if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):
                continue
            f = [sum(1 for k in mem if i in U[k]) for i in range(9)]
            if any(x > 2 for x in f):
                continue
            TOT["F"] += 1
            # ---- the h1 pairs of N(p) inside X_1 must exist (types (i;j), mate (j;i))
            defi = [2 - x for x in f]
            def x1pairs(chosen):
                if all(d == 0 for d in defi):
                    return len(chosen) == h1
                if len(chosen) >= h1:
                    return False
                i = next(q for q in range(9) if defi[q] > 0)
                for j in range(9):
                    if j == i or defi[j] <= 0 or (i, j) not in AS1:
                        continue
                    for (a, b) in ((i, j), (j, i)):
                        ok = True
                        for k in mem:
                            if (a in U[k]) + (b in V[k]) > 1 or (b in U[k]) + (a in V[k]) > 1:
                                ok = False; break
                        if ok:
                            for (a2, b2) in chosen:
                                if (a == a2) + (b == b2) > 1 or (a == b2) + (b == a2) > 1:
                                    ok = False; break
                        if ok:
                            defi[i] -= 1; defi[j] -= 1
                            chosen.append((a, b))
                            r = x1pairs(chosen)
                            chosen.pop()
                            defi[i] += 1; defi[j] += 1
                            if r:
                                return True
                return False
            if not x1pairs([]):
                continue
            TOT["F_ok_Np"] += 1
            Ap = sum(1 << k for k in mem)
            budget0 = 36 - (2 * h2 - 4) ** 2
            # ---- candidate sets for the vertices of X_0 \ {p}
            amax = 4
            while 2 * (amax + 1 - 4) ** 2 <= budget0:
                amax += 1
            amax = min(amax, 9)
            cands_out = []; cands_in = []
            for A, size, tA in ALLSETS:
                if size > amax:
                    continue
                inter_p = A & Ap
                okp = True
                if pc(inter_p) > 2:
                    okp = False
                elif pc(inter_p) == 2:
                    a, b = [k for k in range(18) if (inter_p >> k) & 1]
                    if b == tau[a] or R[a][b] != 0:
                        okp = False
                # profile (3,3,1) (A10): every z outside N[p] sees exactly 2 vertices of A_p, the z in N(p) has a = 6
                if okp and pc(A & tA) <= 2 and (h2 != 3 or pc(inter_p) == 2):
                    cands_out.append(A)
                if size >= 6 and inter_p == 0 and (A & tA) == 0 and (h2 != 3 or size == 6):
                    cands_in.append(A)
            TOT['cands_out'] = TOT.get('cands_out', 0) + len(cands_out)
            TOT['cands_in'] = TOT.get('cands_in', 0) + len(cands_in)
            req = [3 if (h2 == 3 and (Ap >> k) & 1) else 2 for k in range(18)]
            cap = [3 if (h2 == 3 and (Ap >> k) & 1) else 6 for k in range(18)]
            # ---- choose the 4 orbits of X_0 \ {p}
            cov = [1 if (Ap >> k) & 1 else 0 for k in range(18)]
            pairc = [[0] * 18 for _ in range(18)]          # number of X_0 vertices seeing both k and l
            for a in mem:
                for b in mem:
                    if a != b:
                        pairc[a][b] = 1
            chosen = []                                    # list of (A, is_in)
            seenC = set()
            def add_set(A, sgn):
                ks = [k for k in range(18) if (A >> k) & 1]
                for k in ks:
                    cov[k] += sgn
                for a in ks:
                    for b in ks:
                        if a != b:
                            pairc[a][b] += sgn
            def pair_ok(A):
                ks = [k for k in range(18) if (A >> k) & 1]
                for x in range(len(ks)):
                    for y in range(x + 1, len(ks)):
                        if pairc[ks[x]][ks[y]] > 2 - R[ks[x]][ks[y]]:
                            return False
                return all(cov[k] <= cap[k] for k in ks)
            def orbit_rec(n_in, budget):
                if timed_out:
                    return
                if len(chosen) == 4:
                    if n_in != h0 or any(cov[k] < req[k] for k in range(18)):
                        return
                    key = frozenset((min(A, tmask(A)), isin) for A, isin in chosen)
                    if key in seenC:
                        return
                    seenC.add(key)
                    degH = [c - 2 for c in cov]
                    if budget - sum(d * (d - 1) for d in degH) < 0:
                        return
                    if any(degH[k] < 1 for k in mem) or any(d > 4 for d in degH):
                        return
                    TOT["C"] += 1
                    finish(degH)
                    return
                r = 4 - len(chosen)
                deficit = sum(max(0, req[k] - cov[k]) for k in range(18))
                # each remaining orbit covers 2a incidences, with 2 (a-4)^2 <= budget
                am = 4
                while 2 * (am + 1 - 4) ** 2 <= budget and am < 9:
                    am += 1
                if deficit > r * 2 * am:
                    return
                low = [k for k in range(18) if cov[k] < req[k]]
                if n_in < h0:
                    pool = [(A, 1) for A in cands_in if A <= tmask(A)]
                    if SURV is not None:
                        pool = [(A, 1) for A, _ in pool if A in SURV[tuple(tau)][tuple(Forb)]]
                elif low:
                    k0 = low[0]
                    pool = [(A, 0) for A in cands_out if (A >> k0) & 1]
                else:
                    last = max((min(A, tmask(A)) for A, _ in chosen), default=-1)
                    pool = [(A, 0) for A in cands_out if A <= tmask(A)]
                for A, isin in pool:
                    a = pc(A)
                    cost = 2 * (a - 4) ** 2
                    if cost > budget:
                        continue
                    if (h0 - n_in - isin) > r - 1:
                        continue
                    tA = tmask(A)
                    ok = True
                    for A2, isin2 in chosen:
                        tA2 = tmask(A2)
                        if pc(A & A2) > 2 or pc(A & tA2) > 2:
                            ok = False; break
                    if not ok:
                        continue
                    add_set(A, 1); add_set(tA, 1)
                    if pair_ok(A) and pair_ok(tA):
                        chosen.append((A, isin))
                        if SURV is not None and isin:
                            oldc, oldr = cap[:], req[:]
                            curH[0] = SURV[tuple(tau)][tuple(Forb)][A]
                            for k in range(18):
                                ds = [pc(h_[k]) for h_ in curH[0]]
                                cap[k] = max(ds) + 2; req[k] = min(ds) + 2
                        orbit_rec(n_in + isin, budget - cost)
                        if SURV is not None and isin:
                            cap[:] = oldc; req[:] = oldr
                        chosen.pop()
                    add_set(tA, -1); add_set(A, -1)

            def finish(degH):
                nonlocal found_any
                # X_0 vertices: 0 = p, 1+2q = z_q, 2+2q = sigma z_q ; sets
                Az = [Ap]
                isin = [False]
                for A, ii in chosen:
                    Az.append(A); Az.append(tmask(A)); isin.append(bool(ii)); isin.append(bool(ii))
                degG = [pc(Az[q]) - 4 for q in range(9)]
                # ---- H : sigma-invariant graphs on X_2 with degrees degH; k ~ tau k iff the orbit is in F
                Hs = []
                rem = degH[:]
                adjH = [0] * 18
                inF = [False] * 18
                for k in mem:
                    inF[k] = True
                for k in mem:
                    rem[k] -= 1
                    adjH[k] |= 1 << tau[k]
                # partner bookkeeping: at most one partner per shared support vertex is checked by the Y test
                def edge_allowed(a, b):
                    if b == a or b == tau[a] or R[a][b] > 1:
                        return False
                    if R[a][b] == 1:
                        v = (sup[a] & sup[b]).bit_length() - 1
                        if not (free_at(a, v) and free_at(b, v)):
                            return False
                    return True
                def recH(a):
                    while a < 18 and rem[a] == 0:
                        a += 1
                    if a == 18:
                        Hs.append(adjH[:])
                        return
                    for b in range(18):
                        if b == a or rem[b] <= 0 or (adjH[a] >> b) & 1 or not edge_allowed(a, b):
                            continue
                        ta, tb = tau[a], tau[b]
                        # edge {a,b} and its image {ta,tb}
                        if {ta, tb} == {a, b}:
                            continue
                        need = {}
                        for x in (a, b, ta, tb):
                            need[x] = need.get(x, 0) + 1
                        if any(rem[x] < c for x, c in need.items()):
                            continue
                        if b < a and rem[b] > 0:
                            pass
                        adjH[a] |= 1 << b; adjH[b] |= 1 << a; adjH[ta] |= 1 << tb; adjH[tb] |= 1 << ta
                        for x, c in need.items():
                            rem[x] -= c
                        recH(a)
                        for x, c in need.items():
                            rem[x] += c
                        adjH[a] &= ~(1 << b); adjH[b] &= ~(1 << a); adjH[ta] &= ~(1 << tb); adjH[tb] &= ~(1 << ta)
                recH(0)
                Hset = set(tuple(h) for h in Hs)
                if SURV is not None:
                    Hset &= curH[0]
                TOT["H"] += len(Hset)
                if not Hset:
                    return
                # ---- G : sigma-invariant graphs on X_0 with degrees degG
                sg = lambda q: 0 if q == 0 else (q + 1 if q % 2 == 1 else q - 1)
                Gs = []
                remG = degG[:]
                adjG = [0] * 9
                for q in range(1, 9):
                    if isin[q]:
                        adjG[0] |= 1 << q; adjG[q] |= 1; remG[0] -= 1; remG[q] -= 1
                        if q % 2 == 1:
                            adjG[q] |= 1 << (q + 1); adjG[q + 1] |= 1 << q; remG[q] -= 1; remG[q + 1] -= 1
                if remG[0] != 0 or any(x < 0 for x in remG):
                    return
                def recG(a):
                    while a < 9 and remG[a] == 0:
                        a += 1
                    if a == 9:
                        Gs.append(adjG[:])
                        return
                    for b in range(1, 9):
                        if b == a or b == sg(a) or remG[b] <= 0 or (adjG[a] >> b) & 1:
                            continue
                        if pc(Az[a] & Az[b]) > 1:
                            continue
                        ta, tb = sg(a), sg(b)
                        need = {}
                        for x in (a, b, ta, tb):
                            need[x] = need.get(x, 0) + 1
                        if any(remG[x] < c for x, c in need.items()):
                            continue
                        adjG[a] |= 1 << b; adjG[b] |= 1 << a; adjG[ta] |= 1 << tb; adjG[tb] |= 1 << ta
                        for x, c in need.items():
                            remG[x] -= c
                        recG(a)
                        for x, c in need.items():
                            remG[x] += c
                        adjG[a] &= ~(1 << b); adjG[b] &= ~(1 << a); adjG[ta] &= ~(1 << tb); adjG[tb] &= ~(1 << ta)
                recG(1)
                Gset = set(tuple(g) for g in Gs)
                TOT["G"] += len(Gset)
                # ---- Y test.  vertex numbering: support 0..17, X_0 18..26, X_2 27..44
                base = [0] * 45
                for i in range(9):
                    for j in Bn[i]:
                        base[i] |= 1 << (9 + j); base[9 + j] |= 1 << i
                for k in range(18):
                    for v in range(18):
                        if (sup[k] >> v) & 1:
                            base[27 + k] |= 1 << v; base[v] |= 1 << (27 + k)
                for q in range(9):
                    for k in range(18):
                        if (Az[q] >> k) & 1:
                            base[18 + q] |= 1 << (27 + k); base[27 + k] |= 1 << (18 + q)
                for h in Hset:
                    rows1 = base[:]
                    for k in range(18):
                        rows1[27 + k] |= h[k] << 27
                    for g in Gset:
                        rows = rows1[:]
                        for q in range(9):
                            rows[18 + q] |= g[q] << 18
                        ok = True
                        for u in range(45):
                            ru = rows[u]
                            for v in range(u + 1, 45):
                                c = pc(ru & rows[v])
                                if c > 2 or (c > 1 and (ru >> v) & 1):
                                    ok = False; break
                            if not ok:
                                break
                        if ok:
                            TOT["Y_tables"] += 1
                            found_any = True
                            if psd_ok_rows(rows):
                                TOT["Y_tables_psd"] += 1
                                PSD_HIT[0] = True
                            else:
                                TOT["Y_psd_reject"] += 1
                                if len(rejected) < 3:
                                    rejected.append({"tau": list(tau), "F": list(Forb), "Az": Az, "H": list(h), "G": list(g)})
                                continue
                            if len(examples) < 100000:
                                examples.append({"tau": list(tau), "F": list(Forb), "Az": Az, "H": list(h), "G": list(g)})
            orbit_rec(0, budget0)
    return found_any


if SURV is not None:
    reps = [r for r in reps if tuple(r) in SURV]
my = [r for q, r in enumerate(reps) if q % nparts == part]
TAG = ''
if os.environ.get('R2_IDX'):
    my = [reps[int(i)] for i in os.environ['R2_IDX'].split(',')]
    TAG = '_idx' + os.environ['R2_IDX'].split(',')[0]
TOT["tau"] = len(my)
per_tau = []
for tau in my:
    if time.time() - t0 > tlimit:
        timed_out = True
        break
    before = dict(TOT)
    PSD_HIT[0] = False
    fa = process(tau)
    if timed_out:
        break
    TOT["tau_done"] += 1
    if fa:
        TOT["tau_with_table"] += 1
    if PSD_HIT[0]:
        TOT["tau_with_psd_table"] += 1
    per_tau.append({k: TOT[k] - before[k] for k in ("F", "F_ok_Np", "C", "H", "G", "Y_tables", "Y_tables_psd")})
    per_tau[-1]["rep_index"] = reps.index(tau)
    per_tau[-1]["seconds"] = round(time.time() - t0, 1)
    if TOT["tau_done"] % 10 == 0:
        print(f"  [{time.time() - t0:.0f}s] {TOT}", flush=True)
print(f"{name} part {part}/{nparts}: time {time.time() - t0:.1f}s timed_out={timed_out}")
print("  totals:", TOT)
json.dump({"name": name, "part": part, "nparts": nparts, "totals": TOT, "timed_out": timed_out,
           "per_tau": per_tau, "examples": examples, "rejected_examples": rejected},
          open(os.path.join(here, f"r2_stage2_{si}_{part}of{nparts}{'_surv' if SURV is not None else ''}{TAG}.json"), "w"))
