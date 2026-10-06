# Referee check 7 (version b: same model and tests as ref7_p331_ext.py, cover step vectorised, progress lines): profile (3,3,1), steps "45 vertices" and "51 vertices" from my own model, starting from the 39-vertex
# survivors of my own ref6_p331.py.
# 45 = S u X_0 u X_2.  The six vertices of X_0 other than p, z0, sigma z0 (3 orbits; vertices 39..44, mates 39/40, 41/42, 43/44):
#   forced non-edges: to S, to p, to z0, to sigma z0, to the mate;   exactly 2 neighbours in A_p;  a_2(z) >= 4;
#   every s in A_p has exactly 2 neighbours among the six, every s in X_2 \ A_p exactly deg_H(s) + 1;
#   G = A[the six] is sigma-invariant with deg_G(z) = a_2(z) - 4.
# 51 = 45 u W, W = N(p) n X_1 = 3 mate pairs (vertices 45..50): p ~ W, only mate edges inside W, no edge to A_p, to z0, sigma z0,
#   to the six; w = (i ; j), i != j, x_i has 2 - f_i neighbours in W, cell room; exactly 2 neighbours in X_2 \ A_p, not a mate
#   pair; every vertex of X_2 \ A_p has exactly one neighbour in W.
# Counts printed: tables passing the budgets on 45; passing budgets + PSD(both) on 45; budget-valid graphs on 51 built on the
# PSD-passing tables; of which PSD.   PSD is floating point here (threshold -1e-7): a count check, not a proof.
import itertools, sys, time, json, os
M1ONLY = os.environ.get('REF_M1ONLY') == '1'   # test 9(3I-A)+J only (to check the remark that two matrices are needed)
import numpy as np
REP = {"B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
       "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
       "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
name = sys.argv[1]; src = json.load(open(sys.argv[2]))
part, nparts = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)
B = np.zeros((9, 9), dtype=np.int64)
for w in REP[name].split():
    i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
DEF = [tuple(d) for d in src["DEF"]]; reps = [tuple(r) for r in src["reps"]]; n = 18

def psd(A, m, which=3):
    sub = A[:m, :m].astype(float)
    ok1 = np.linalg.eigvalsh(9 * (3 * np.eye(m) - sub) + 1.0)[0] > -1e-7
    if which == 1 or M1ONLY: return ok1
    return ok1 and np.linalg.eigvalsh(11 * (4 * np.eye(m) + sub) - 2.0)[0] > -1e-7
def budget(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()

st = dict(configs39=0, cand_Z=0, cand_orbits=0, covers=0, tables45_budget=0, tables45_psd=0, tables45_psd_M1only=0,
          type_solutions=0, graphs51_budget=0, graphs51_psd=0, graphs51_psd_M1only=0, nodes51=0)
t0 = time.time()
for ci, (ti, F, pk) in enumerate(src["surv39"]):
    if ci % nparts != part: continue
    st["configs39"] += 1
    s = reps[ti]
    A39 = np.unpackbits(np.array(pk, dtype=np.uint8))[:45 * 45].reshape(45, 45).astype(np.int64)
    Ap = [c for a in F for c in (a, s[a])]
    nonAp = [c for c in range(18) if c not in Ap]
    H = A39[19:37, 19:37]; degH = H.sum(1)
    assert all(degH[c] == 1 for c in Ap)
    need = np.array([2 if c in Ap else int(degH[c]) + 1 for c in range(18)])
    Az0 = [c for c in nonAp if A39[37, 19 + c]]; sAz0 = [c for c in nonAp if A39[38, 19 + c]]
    assert len(Az0) == 6 and len(sAz0) == 6 and not set(Az0) & set(sAz0)
    # ---- candidate neighbourhoods Z of one vertex z (41 determined vertices: the 39 + z + sigma z, placed at 39, 40)
    cands = {}
    for ap2 in itertools.combinations(Ap, 2):
        for r1 in range(0, 3):
            for z1 in itertools.combinations(Az0, r1):
                for r2 in range(0, 3):
                    if r1 + r2 < 2: continue
                    for z2 in itertools.combinations(sAz0, r2):
                        Z = tuple(sorted(ap2 + z1 + z2))
                        st["cand_Z"] += 1
                        cov = np.zeros(18, dtype=np.int64)
                        for c in Z:
                            cov[c] += 1; cov[s[c]] += 1
                        if (cov > need).any(): continue
                        A = A39.copy()
                        for c in Z:
                            A[39, 19 + c] = A[19 + c, 39] = 1
                            A[40, 19 + s[c]] = A[19 + s[c], 40] = 1
                        if not budget(A): continue
                        tZ = tuple(sorted(s[c] for c in Z))
                        key = min(Z, tZ)
                        assert Z != tZ
                        cands[key] = cov
    keys = sorted(cands)
    st["cand_orbits"] += len(keys)
    bycov = {}
    for k in keys: bycov.setdefault(tuple(cands[k]), []).append(k)
    # ---- exact covers by 3 distinct orbits
    covers = []
    if keys:
        COV = np.array([cands[k] for k in keys])
        for a in range(len(keys) - 1):
            rem = need - COV[a]
            if (rem < 0).any(): continue
            okb = np.nonzero((COV[a + 1:] <= rem).all(1))[0] + a + 1          # vectorised over the second orbit
            for b in okb:
                r = rem - COV[b]
                for k3 in bycov.get(tuple(int(x) for x in r), []):
                    if k3 > keys[b]: covers.append((keys[a], keys[b], k3))
    if st["configs39"] % 20 == 0:
        print(f"   progress: {st['configs39']} configs, cand orbits {st['cand_orbits']}, covers {st['covers'] + len(covers)}, "
              f"tables45_budget {st['tables45_budget']}, {time.time()-t0:.0f}s", flush=True)
    st["covers"] += len(covers)
    tables = []
    for cov3 in covers:
        # orientation: the stored key is Z of the representative (vertex 39+2q); its mate (40+2q) sees tau Z.
        A = A39.copy()
        for q, Z in enumerate(cov3):
            for c in Z:
                A[39 + 2 * q, 19 + c] = A[19 + c, 39 + 2 * q] = 1
                A[40 + 2 * q, 19 + s[c]] = A[19 + s[c], 40 + 2 * q] = 1
        if not budget(A): continue
        a2 = [len(cov3[q // 2]) for q in range(6)]
        pairs = [(0, 1), (0, 2), (1, 2)]
        for gb in itertools.product((0, 1), repeat=6):
            A2 = A.copy()
            for t, (u, v) in enumerate(pairs):
                if gb[2 * t]:
                    A2[39 + 2 * u, 39 + 2 * v] = A2[39 + 2 * v, 39 + 2 * u] = 1
                    A2[40 + 2 * u, 40 + 2 * v] = A2[40 + 2 * v, 40 + 2 * u] = 1
                if gb[2 * t + 1]:
                    A2[39 + 2 * u, 40 + 2 * v] = A2[40 + 2 * v, 39 + 2 * u] = 1
                    A2[40 + 2 * u, 39 + 2 * v] = A2[39 + 2 * v, 40 + 2 * u] = 1
            dg = A2[39:45, 39:45].sum(1)
            if any(int(dg[q]) != a2[q] - 4 for q in range(6)): continue
            if not budget(A2): continue
            st["tables45_budget"] += 1
            if psd(A2, 45, 1): st["tables45_psd_M1only"] += 1
            if psd(A2, 45):
                st["tables45_psd"] += 1
                tables.append(A2)
    # ---- 51 vertices
    f = [0] * 9
    for c in Ap:
        for i in DEF[c]: f[i] += 1
    needw = [2 - x for x in f]
    assert min(needw) >= 0 and sum(needw) == 6
    cov2 = np.zeros((9, 9), dtype=np.int64)
    for a in range(n):
        for i in DEF[a]:
            for j in DEF[s[a]]: cov2[i, j] += 1
    cells = [(i, j) for i in range(9) for j in range(i + 1, 9) if cov2[i, j] < 2 - B[i, j]]
    tsols = []
    def rec(k, start, chosen, nd):
        if k == 3:
            if all(x == 0 for x in nd): tsols.append(tuple(chosen))
            return
        for t in range(start, len(cells)):
            i, j = cells[t]
            if nd[i] == 0 or nd[j] == 0: continue
            nd[i] -= 1; nd[j] -= 1
            rec(k + 1, t + 1, chosen + [(i, j)], nd)
            nd[i] += 1; nd[j] += 1
    rec(0, 0, [], needw[:])
    orbs_rest = [c for c in nonAp if c < s[c]]
    for T in tables:
        st["type_solutions"] += len(tsols)
        for ts in tsols:
            A = np.zeros((51, 51), dtype=np.int64); A[:45, :45] = T
            for c, (i, j) in enumerate(ts):
                w, sw = 45 + 2 * c, 46 + 2 * c
                A[w, sw] = A[sw, w] = 1
                A[18, w] = A[w, 18] = 1; A[18, sw] = A[sw, 18] = 1
                A[w, i] = A[i, w] = 1; A[w, 9 + j] = A[9 + j, w] = 1
                A[sw, j] = A[j, sw] = 1; A[sw, 9 + i] = A[9 + i, sw] = 1
            if not budget(A): continue
            def lvl(q, A, cap):
                st["nodes51"] += 1
                if q == 6:
                    st["graphs51_budget"] += 1
                    if psd(A, 51, 1): st["graphs51_psd_M1only"] += 1
                    if psd(A, 51): st["graphs51_psd"] += 1
                    return
                a = orbs_rest[q]
                for c in range(3):
                    if cap[c] == 0: continue
                    for k in (a, s[a]):
                        A2 = A.copy()
                        w, sw = 45 + 2 * c, 46 + 2 * c
                        A2[w, 19 + k] = A2[19 + k, w] = 1
                        A2[sw, 19 + s[k]] = A2[19 + s[k], sw] = 1
                        if budget(A2):
                            cap2 = cap[:]; cap2[c] -= 1
                            lvl(q + 1, A2, cap2)
            lvl(0, A, [2, 2, 2])
print(f"{name} part {part}/{nparts} from {sys.argv[2]}: {st}  time {time.time()-t0:.0f}s", flush=True)
