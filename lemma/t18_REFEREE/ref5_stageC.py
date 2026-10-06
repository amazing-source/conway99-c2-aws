# Referee check 5: stage C of profile (2,5,0) from my own model, on the stage-B triples of my own ref4_stageB.py.
# W = N(p) n X_1 = 5 mate pairs w_c = (i_c ; j_c), sigma w_c = (j_c ; i_c), i_c != j_c.  Vertices 37+2c (w_c), 38+2c (sigma w_c).
# Forced (proved by hand): p ~ all of W; inside W only the 5 mate edges; no edge W - A_p (N(p) is a matching);
#   x_i has exactly 2 - f_i neighbours in W (f_i = number of A_p vertices adjacent to x_i);
#   the cell (i,j) must have room: (2 - B_ij) - (number of X_2 vertices adjacent to x_i and y_j) >= 1;
#   K_w = N(w) n X_2 avoids A_p, contains no mate pair, |K_w| >= 2, N(sigma w) n X_2 = tau K_w;
#   every k in X_2 \ A_p has exactly 2 - |N(k) n A_p| neighbours in W.
# Tests: budgets on the partial graph (always legitimate); float PSD of both matrices only on determined sets:
#   S u N[p] (33 vertices) and S u {p} u X_2 u (W pairs whose K is complete).
# usage: python ref5_stageC.py <B0|B1|B2> <stageB json> [mode]   mode = types (count type solutions only) | full
import itertools, sys, time, json
import numpy as np

REP = {
 "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
 "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
 "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}
name = sys.argv[1]; src = json.load(open(sys.argv[2])); mode = sys.argv[3] if len(sys.argv) > 3 else "full"
TLIM = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
TAG = sys.argv[5] if len(sys.argv) > 5 else "all"
B = np.zeros((9, 9), dtype=np.int64)
for w in REP[name].split():
    i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
DEF = [tuple(d) for d in src["DEF"]]
reps = [tuple(r) for r in src["reps"]]
n = 18; NV = 47
OFF = 1 - np.eye(NV, dtype=np.int64)

def psd(A, idxs):
    sub = A[np.ix_(idxs, idxs)].astype(float); m = len(idxs)
    if np.linalg.eigvalsh(9 * (3 * np.eye(m) - sub) + 1.0)[0] < -1e-7: return False
    return np.linalg.eigvalsh(11 * (4 * np.eye(m) + sub) - 2.0)[0] > -1e-7
def budget_ok(A):
    C = A @ A
    return not ((C > 2 - A) & (OFF == 1)).any()
def budget_sub(A, idxs):
    sub = A[np.ix_(idxs, idxs)]; C = sub @ sub
    return not ((C > 2 - sub) & (np.eye(len(idxs), dtype=np.int64) == 0)).any()

stats = dict(triples=0, pairs_tauF=0, type_solutions=0, type_ok33=0, triple_type=0, nodes=0, rej_budget=0, rej_psd=0, survivors=0)
surv = []
bypair = {}
for tr in src["triples"]:
    ti, F, Hpk = tr[0], tuple(tr[1]), tr[2]
    H = np.unpackbits(np.array(Hpk, dtype=np.uint8))[:324].reshape(18, 18).astype(np.int64)
    bypair.setdefault((ti, F), []).append(H)
t0 = time.time(); timed_out = False
PART, NPARTS = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (0, 1)
done_pairs = []
for pi, ((ti, F), Hs) in enumerate(sorted(bypair.items())):
    if pi % NPARTS != PART: continue
    if stats["pairs_tauF"] and stats["pairs_tauF"] % 20 == 0:
        print(f"   progress: {stats['pairs_tauF']} pairs, {stats['triples']} triples, survivors {stats['survivors']}, {time.time()-t0:.0f}s", flush=True)
    if time.time() - t0 > TLIM:
        timed_out = True; print("TIME LIMIT before pair", ti, F, flush=True); break
    s = reps[ti]
    stats["pairs_tauF"] += 1
    Ap = [c for a in F for c in (a, s[a])]
    f = [0] * 9
    for c in Ap:
        for i in DEF[c]: f[i] += 1
    need = [2 - x for x in f]
    assert min(need) >= 0 and sum(need) == 10
    cov = np.zeros((9, 9), dtype=np.int64)
    for a in range(n):
        for i in DEF[a]:
            for j in DEF[s[a]]: cov[i, j] += 1
    cells = [(i, j) for i in range(9) for j in range(i + 1, 9) if cov[i, j] < 2 - B[i, j]]
    assert (cov == cov.T).all()
    tsols = []
    def rec(k, start, chosen, nd):
        if k == 5:
            if all(x == 0 for x in nd): tsols.append(tuple(chosen))
            return
        for t in range(start, len(cells)):
            i, j = cells[t]
            if nd[i] == 0 or nd[j] == 0: continue
            nd[i] -= 1; nd[j] -= 1
            rec(k + 1, t + 1, chosen + [(i, j)], nd)
            nd[i] += 1; nd[j] += 1
    rec(0, 0, [], need[:])
    stats["type_solutions"] += len(tsols)
    # base matrix on 47 vertices without H and without W - X_2 edges
    A0 = np.zeros((NV, NV), dtype=np.int64)
    A0[0:9, 9:18] = B; A0[9:18, 0:9] = B
    for a in range(n):
        for i in DEF[a]: A0[19 + a, i] = A0[i, 19 + a] = 1
        for j in DEF[s[a]]: A0[19 + a, 9 + j] = A0[9 + j, 19 + a] = 1
    for c in Ap: A0[18, 19 + c] = A0[19 + c, 18] = 1
    good_types = []
    for ts in tsols:
        A = A0.copy()
        for c, (i, j) in enumerate(ts):
            w, sw = 37 + 2 * c, 38 + 2 * c
            A[w, sw] = A[sw, w] = 1
            A[18, w] = A[w, 18] = 1; A[18, sw] = A[sw, 18] = 1
            A[w, i] = A[i, w] = 1; A[w, 9 + j] = A[9 + j, w] = 1          # w = (i ; j)
            A[sw, j] = A[j, sw] = 1; A[sw, 9 + i] = A[9 + i, sw] = 1      # sigma w = (j ; i)
        idx33 = list(range(19)) + [19 + c for c in Ap] + list(range(37, 47))
        # mate edges of A_p are needed on the 33-vertex set
        A33 = A.copy()
        for a in F: A33[19 + a, 19 + s[a]] = A33[19 + s[a], 19 + a] = 1
        if budget_sub(A33, idx33) and psd(A33, idx33):
            good_types.append((ts, A))
    stats["type_ok33"] += len(good_types)
    if mode == "types": continue
    orbs_rest = [a for a in range(n) if a < s[a] and a not in F]
    for H in Hs:
        stats["triples"] += 1
        reqk = {}
        for a in orbs_rest:
            r = 2 - int(sum(H[a, c] for c in Ap))
            r2 = 2 - int(sum(H[s[a], c] for c in Ap))
            assert r == r2 and r >= 0
            reqk[a] = r
        for ts, Abase in good_types:
            stats["triple_type"] += 1
            A = Abase.copy()
            A[19:37, 19:37] = H
            if not budget_ok(A):
                stats["rej_budget"] += 1; continue
            # search: W pair by W pair; inside a pair, orbit by orbit: w ~ a, w ~ tau a, or none
            def pairlevel(c, A, rem):
                if c == 5:
                    if any(rem[a] for a in orbs_rest): return
                    stats["survivors"] += 1
                    surv.append((ti, F, [int(x) for x in np.packbits(A.astype(np.uint8)).tolist()]))
                    return
                later = 4 - c
                w, sw = 37 + 2 * c, 38 + 2 * c
                def orblevel(q, A, rem, size):
                    stats["nodes"] += 1
                    if q == len(orbs_rest):
                        if size < 2: return
                        # feasibility: remaining requirements must fit in the later pairs
                        if any(rem[a] > later for a in orbs_rest): return
                        idxs = list(range(37)) + list(range(37, 39 + 2 * c))
                        if not psd(A, idxs):
                            stats["rej_psd"] += 1; return
                        pairlevel(c + 1, A, rem)
                        return
                    a = orbs_rest[q]
                    if rem[a] <= later:                       # option: no edge to this orbit
                        orblevel(q + 1, A, rem, size)
                    if rem[a] > 0:
                        for k in (a, s[a]):
                            A2 = A.copy()
                            A2[w, 19 + k] = A2[19 + k, w] = 1
                            A2[sw, 19 + s[k]] = A2[19 + s[k], sw] = 1
                            if budget_ok(A2):
                                rem2 = dict(rem); rem2[a] -= 1
                                orblevel(q + 1, A2, rem2, size + 1)
                            else:
                                stats["rej_budget"] += 1
                orblevel(0, A, rem, 0)
            pairlevel(0, A, dict(reqk))
el = time.time() - t0
print(f"{name} [{mode}] from {sys.argv[2]}: {stats}  time {el:.0f}s timed_out={timed_out}", flush=True)
if mode != "types":
    for ti, F, _ in surv: print("   SURVIVOR on 47 vertices: matching index", ti, "F =", F)
    json.dump({"stats": stats, "survivors": surv, "timed_out": timed_out, "part": [PART, NPARTS], "n_pairs_total": len(bypair)}, open(f"ref5_stageC_{name}_{mode}_{TAG}_{PART}of{NPARTS}.json", "w"))
