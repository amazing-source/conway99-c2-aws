# Referee 2: (1) is types.json (d = 1, 2) exactly the list given by budgets alone on the 21 vertices S u {p, w, sigma w}?
#            (2) recount of line 1 of section 7.5 and of the first two rows of the table of Computation 8.4,
#                on MY orbit representatives (my_tau_<s>.json written by stage1.py).
import json, itertools, sys
from common import *
from flint import fmpz_mat

def neg_count(M):
    n = len(M)
    cp = fmpz_mat(M).charpoly()
    co = [int(cp[i]) for i in range(n + 1)]
    q = [co[i] * (-1) ** i for i in range(n + 1)]
    q = [c for c in q if c != 0]
    return sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0))

def base(adjB):
    nb = [set() for _ in range(19)]
    for i in range(9):
        for j in adjB[i]:
            nb[i].add(9 + j)
            nb[9 + j].add(i)
    return nb

def types_budget_only(adjB):
    nb0 = base(adjB)
    out = {}
    for d in range(0, 4):
        for Np in itertools.combinations(range(9), d):
            for Nm in itertools.combinations(range(9), d):
                for flag in (0, 1):
                    N = set(Np) | {9 + j for j in Nm}
                    sN = {9 + i for i in Np} | set(Nm)
                    if flag:
                        N.add(18); sN.add(18)
                    nb = [set(x) for x in nb0] + [set(N), set(sN)]
                    for v in N:
                        nb[v].add(19)
                    for v in sN:
                        nb[v].add(20)
                    if flag:
                        nb[19].add(20); nb[20].add(19)
                    if budget_ok(nb):
                        out.setdefault((d, flag), set()).add((Np, Nm, flag))
    return out

def main():
    T = json.load(open(r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma\t18\types.json"))
    for s in (0, 1, 2):
        adjB = Bgraph(s)
        mine = types_budget_only(adjB)
        theirs = {}
        for a, b, f in T["(i) e=0 #%d" % s]:
            theirs.setdefault((len(a), f), set()).add((tuple(a), tuple(b), f))
        print("B%d: types.json vs 'no budget violation on the 21 vertices S u {p, w, sigma w}':" % s)
        for key in sorted(set(mine) | set(theirs)):
            m = mine.get(key, set()); t = theirs.get(key, set())
            print("   (d, flag) = %s: budgets only %d, types.json %d, equal sets: %s, types.json subset of budgets-only: %s"
                  % (key, len(m), len(t), m == t, t <= m))
        # -------- recounts on my representatives
        js = json.load(open("my_tau_%d.json" % s))
        D = [tuple(u) for u in js["D"]]
        reps = [tuple(t) for t in js["orbit_reps"]]
        nb0 = base(adjB)
        for nF in (3, 2):
            cnt_budget = cnt_psd = cnt_types = 0
            nmatch = set()
            for ti, tau in enumerate(reps):
                usable = [a for a in range(18) if a < tau[a] and not (set(D[a]) & set(D[tau[a]]))]
                for F in itertools.combinations(usable, nF):
                    Ap = []
                    for a in F:
                        Ap += [a, tau[a]]
                    n = 19 + len(Ap)
                    nb = [set(x) for x in nb0] + [set() for _ in Ap]
                    for q, a in enumerate(Ap):
                        v = 19 + q
                        for i in D[a]:
                            nb[v].add(i); nb[i].add(v)
                        for l in D[tau[a]]:
                            nb[v].add(9 + l); nb[9 + l].add(v)
                        nb[v].add(18); nb[18].add(v)
                    for q in range(0, len(Ap), 2):
                        nb[19 + q].add(20 + q); nb[20 + q].add(19 + q)
                    if not budget_ok(nb):
                        continue
                    cnt_budget += 1
                    nmatch.add(ti)
                    # type solutions for W, with cell room (C5)+(C6) / (F5) + cell room
                    f = [0] * 9
                    for a in Ap:
                        for i in D[a]:
                            f[i] += 1
                    def room(i, j):
                        c = sum(1 for a in range(18) if i in D[a] and j in D[tau[a]])
                        return c <= 1 - (1 if j in adjB[i] else 0)
                    if max(f) <= 2:
                        need = [2 - x for x in f]
                        cand = [(i, j) for i in range(9) for j in range(i + 1, 9)
                                if need[i] > 0 and need[j] > 0 and room(i, j) and room(j, i)]
                        norb = 3 if nF == 3 else 5
                        found = False
                        def rec(start, left, need):
                            nonlocal found
                            if found:
                                return
                            if left == 0:
                                if not any(need):
                                    found = True
                                return
                            for q in range(start, len(cand)):
                                i, j = cand[q]
                                if need[i] > 0 and need[j] > 0:
                                    need[i] -= 1; need[j] -= 1
                                    rec(q + 1, left - 1, need)
                                    need[i] += 1; need[j] += 1
                        rec(0, norb, need)
                        if found:
                            cnt_types += 1
                    if nF == 2:
                        A = [[1 if j in nb[i] else 0 for j in range(n)] for i in range(n)]
                        M1 = [[(27 if i == j else 0) - 9 * A[i][j] + 1 for j in range(n)] for i in range(n)]
                        if neg_count(M1) == 0:
                            M2 = [[(44 if i == j else 0) + 11 * A[i][j] - 2 for j in range(n)] for i in range(n)]
                            if neg_count(M2) == 0:
                                cnt_psd += 1
            print("   |F| = %d: pairs (tau, F) with no budget violation on S u {p} u A_p: %d (in %d matchings); admitting a type solution with cell room: %d%s"
                  % (nF, cnt_budget, len(nmatch), cnt_types,
                     ("; exactly PSD (M1 and M2) on the 23 vertices: %d" % cnt_psd) if nF == 2 else ""))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
