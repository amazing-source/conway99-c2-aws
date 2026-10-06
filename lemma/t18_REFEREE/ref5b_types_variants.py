# Variants of the count of W type solutions (to identify which object the reports count as "type solution"):
#   room : the cell (i,j) must have room left by ALL X_2 vertices (my model);  noroom : no cell condition at this stage
#   rep  : the same unordered type may be used by two mate pairs (excluded by hand: 3 common neighbours p, x_i, y_j)
import itertools, sys, json
import numpy as np
REP = {"B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
       "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
       "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
name = sys.argv[1]; src = json.load(open(sys.argv[2]))
B = np.zeros((9, 9), dtype=np.int64)
for w in REP[name].split():
    i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
DEF = [tuple(d) for d in src["DEF"]]; reps = [tuple(r) for r in src["reps"]]; n = 18
def psd(sub):
    sub = sub.astype(float); m = len(sub)
    if np.linalg.eigvalsh(9 * (3 * np.eye(m) - sub) + 1.0)[0] < -1e-7: return False
    return np.linalg.eigvalsh(11 * (4 * np.eye(m) + sub) - 2.0)[0] > -1e-7
def bud(sub):
    C = sub @ sub
    return not ((C > 2 - sub) & (np.eye(len(sub), dtype=np.int64) == 0)).any()
pairs = sorted(set((t[0], tuple(t[1])) for t in src["triples"]))
for room in (True, False):
    for rep in (False, True):
        tot = ok33 = okb = 0
        for ti, F in pairs:
            s = reps[ti]; Ap = [c for a in F for c in (a, s[a])]
            f = [0] * 9
            for c in Ap:
                for i in DEF[c]: f[i] += 1
            need = [2 - x for x in f]
            cov = np.zeros((9, 9), dtype=np.int64)
            for a in range(n):
                for i in DEF[a]:
                    for j in DEF[s[a]]: cov[i, j] += 1
            cells = [(i, j) for i in range(9) for j in range(i + 1, 9) if (not room) or cov[i, j] < 2 - B[i, j]]
            tsols = []
            def rec(k, start, chosen, nd):
                if k == 5:
                    if all(x == 0 for x in nd): tsols.append(tuple(chosen))
                    return
                for t in range(start, len(cells)):
                    i, j = cells[t]
                    if nd[i] == 0 or nd[j] == 0: continue
                    nd[i] -= 1; nd[j] -= 1
                    rec(k + 1, t if rep else t + 1, chosen + [(i, j)], nd)
                    nd[i] += 1; nd[j] += 1
            rec(0, 0, [], need[:])
            tot += len(tsols)
            for ts in tsols:
                A = np.zeros((33, 33), dtype=np.int64)
                A[0:9, 9:18] = B; A[9:18, 0:9] = B
                for q, c in enumerate(Ap):
                    v = 19 + q
                    A[18, v] = A[v, 18] = 1
                    for i in DEF[c]: A[v, i] = A[i, v] = 1
                    for j in DEF[s[c]]: A[v, 9 + j] = A[9 + j, v] = 1
                A[19, 20] = A[20, 19] = 1; A[21, 22] = A[22, 21] = 1
                for c, (i, j) in enumerate(ts):
                    w, sw = 23 + 2 * c, 24 + 2 * c
                    A[w, sw] = A[sw, w] = 1
                    A[18, w] = A[w, 18] = 1; A[18, sw] = A[sw, 18] = 1
                    A[w, i] = A[i, w] = 1; A[w, 9 + j] = A[9 + j, w] = 1
                    A[sw, j] = A[j, sw] = 1; A[sw, 9 + i] = A[9 + i, sw] = 1
                b = bud(A); okb += b
                if b and psd(A): ok33 += 1
        print(f"{name}: cell room={room}, repeated types allowed={rep}: type solutions {tot}; pass budgets on 33: {okb}; pass budgets+PSD on 33: {ok33}")
