# Referee 2: number of pairs (tau, F) (no budget violation on S u {p} u A_p) admitting a set of types for W, under
#   variant A: (F5)/(C5) only;  variant B: + cell room (C6);  variant C: + no A_p vertex of type (U;V) with i in U, j in V
#   (w of type (i;j) and such a vertex would have the 3 common neighbours p, x_i, y_j).
import json, itertools
from common import *
def base(adjB):
    nb = [set() for _ in range(19)]
    for i in range(9):
        for j in adjB[i]:
            nb[i].add(9 + j); nb[9 + j].add(i)
    return nb
for s in (0, 1, 2):
    adjB = Bgraph(s)
    js = json.load(open("my_tau_%d.json" % s))
    D = [tuple(u) for u in js["D"]]; reps = [tuple(t) for t in js["orbit_reps"]]
    nb0 = base(adjB)
    for nF in (3, 2):
        cnt = {"A": 0, "B": 0, "C": 0}; tot = 0
        for tau in reps:
            usable = [a for a in range(18) if a < tau[a] and not (set(D[a]) & set(D[tau[a]]))]
            cell = [[sum(1 for a in range(18) if i in D[a] and j in D[tau[a]]) for j in range(9)] for i in range(9)]
            for F in itertools.combinations(usable, nF):
                Ap = []
                for a in F: Ap += [a, tau[a]]
                nb = [set(x) for x in nb0] + [set() for _ in Ap]
                for q, a in enumerate(Ap):
                    v = 19 + q
                    for i in D[a]: nb[v].add(i); nb[i].add(v)
                    for l in D[tau[a]]: nb[v].add(9 + l); nb[9 + l].add(v)
                    nb[v].add(18); nb[18].add(v)
                for q in range(0, len(Ap), 2):
                    nb[19 + q].add(20 + q); nb[20 + q].add(19 + q)
                if not budget_ok(nb): continue
                tot += 1
                f = [0] * 9
                for a in Ap:
                    for i in D[a]: f[i] += 1
                if max(f) > 2: continue
                norb = 3 if nF == 3 else 5
                for var in "ABC":
                    def okcell(i, j):
                        if var == "A": return True
                        if cell[i][j] > 1 - (1 if j in adjB[i] else 0): return False
                        if cell[j][i] > 1 - (1 if j in adjB[i] else 0): return False
                        if var == "C":
                            for a in Ap:
                                U, V = D[a], D[tau[a]]
                                if (i in U and j in V) or (j in U and i in V): return False
                        return True
                    cand = [(i, j) for i in range(9) for j in range(i + 1, 9) if f[i] < 2 and f[j] < 2 and okcell(i, j)]
                    need = [2 - x for x in f]
                    def rec(start, left):
                        if left == 0: return not any(need)
                        for q in range(start, len(cand)):
                            i, j = cand[q]
                            if need[i] > 0 and need[j] > 0:
                                need[i] -= 1; need[j] -= 1
                                r = rec(q + 1, left - 1)
                                need[i] += 1; need[j] += 1
                                if r: return True
                        return False
                    if rec(0, norb): cnt[var] += 1
        print("B%d |F|=%d: budget-valid pairs (tau,F) %d; with a type solution: (F5) only %d; + cell room %d; + no A_p vertex in the cell %d" % (s, nF, tot, cnt["A"], cnt["B"], cnt["C"]))
