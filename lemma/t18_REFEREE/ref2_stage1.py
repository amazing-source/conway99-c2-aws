# Referee check 2: stage 1 (matchings tau of the 18 deficient pairs) recounted from my own model.
# Only constraints that I proved by hand are used:
#   (R1) a vertex v of X_2 with N+(v) = x_U, N-(v) = y_V:  |U n V| <= 1 ; every a in U has at most one B-neighbour in V and
#        every c in V at most one B-neighbour in U (v ~ x_a adjacent => exactly one common neighbour).
#   (R2) for every ordered cell (i, j): number of X_2 vertices v with i in N+(v), j in N-(v)  <=  1 if i ~_B j, else 2.
# No PSD test, no file of the repo is read.  Then:
#   - pairs (tau, F), |F| = 3 (profile (3,3,1)) and |F| = 2 (profile (2,5,0)) passing ALL common-neighbour budgets on the
#     determined set S u {p} u A_p, with and without the existence of a type solution for W.
import itertools, sys, time
import numpy as np
from collections import Counter

REP = {
 "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
 "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
 "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}

def run(name):
    B = [[0] * 9 for _ in range(9)]
    for w in REP[name].split():
        i, j = int(w[0]), int(w[1]); B[i][j] = B[j][i] = 1
    assert all(sum(r) == 4 for r in B)
    Bn = [set(j for j in range(9) if B[i][j]) for i in range(9)]
    cod = lambda a, b: len(Bn[a] & Bn[b])
    assert all(cod(a, b) in (1, 2) for a in range(9) for b in range(a + 1, 9))
    DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if cod(a, b) == 1]
    n = len(DEF); assert n == 18
    # each index lies in exactly 4 deficient pairs (x_i has 4 neighbours in X_2)
    assert all(sum(1 for d in DEF if i in d) == 4 for i in range(9))

    def r1(U, V):
        if len(set(U) & set(V)) > 1: return False
        if any(sum(B[i][j] for j in V) > 1 for i in U): return False
        if any(sum(B[i][j] for i in U) > 1 for j in V): return False
        return True
    OK = [[a != b and r1(DEF[a], DEF[b]) for b in range(n)] for a in range(n)]
    assert all(OK[a][b] == OK[b][a] for a in range(n) for b in range(n))
    nrect = sum(OK[a][b] for a in range(n) for b in range(a + 1, n))
    ninNp = sum(OK[a][b] and not (set(DEF[a]) & set(DEF[b])) for a in range(n) for b in range(a + 1, n))
    print(f"{name}: deficient pairs {n}; rectangles passing (R1): {nrect}; of which U n V empty (usable in N(p)): {ninNp}")

    req = [[2 - B[i][j] for j in range(9)] for i in range(9)]
    cover = [[0] * 9 for _ in range(9)]
    tau = [-1] * n
    sols = []
    def put(a, b, s):
        U, V = DEF[a], DEF[b]
        for i in U:
            for j in V:
                cover[i][j] += s      # vertex (U;V)
                cover[j][i] += s      # its mate (V;U)
    def okc(a, b):
        U, V = DEF[a], DEF[b]
        return all(cover[i][j] <= req[i][j] and cover[j][i] <= req[j][i] for i in U for j in V)
    def rec():
        # last free index first (a different order from r2_stage1.py)
        a = -1
        for k in range(n - 1, -1, -1):
            if tau[k] == -1:
                a = k; break
        if a < 0:
            sols.append(tuple(tau)); return
        for b in range(a):
            if tau[b] == -1 and OK[a][b]:
                put(a, b, 1)
                if okc(a, b):
                    tau[a] = b; tau[b] = a
                    rec()
                    tau[a] = -1; tau[b] = -1
                put(a, b, -1)
    t0 = time.time(); rec()
    print(f"   matchings tau passing (R1)+(R2): {len(sols)}  ({time.time()-t0:.1f}s)")
    # Aut(B) and orbits
    auts = [p for p in itertools.permutations(range(9))
            if all(B[p[i]][p[j]] == B[i][j] for i in range(9) for j in range(i + 1, 9))]
    idx = {d: k for k, d in enumerate(DEF)}
    gd = [[idx[tuple(sorted((p[a], p[b])))] for (a, b) in DEF] for p in auts]
    seen = set(); reps = []
    for s in sols:
        if s in seen: continue
        reps.append(s)
        for g in gd:
            img = [0] * n
            for a in range(n): img[g[a]] = g[s[a]]
            seen.add(tuple(img))
    assert seen == set(sols)
    print(f"   |Aut(B)| = {len(auts)}; orbits of matchings: {len(reps)}")
    # how many matchings contain a rectangle with U n V != empty for every orbit etc. (information)
    # ---- pairs (tau, F) ----
    def budgets_Ap(s, F):
        """All common-neighbour budgets on S u {p} u A_p (edges: B between S+ and S-, p - A_p, mates in A_p, A_p - S by tau).
        Returns True iff no pair exceeds 2 - A_uv.  Brute force on the explicit graph."""
        V = []            # vertices: ('x',i) ('y',i) ('p',) ('v',a)
        verts = [('x', i) for i in range(9)] + [('y', i) for i in range(9)] + [('p',)]
        for a in F:
            verts += [('v', a), ('v', s[a])]
        pos = {v: k for k, v in enumerate(verts)}
        m = len(verts)
        A = [[0] * m for _ in range(m)]
        def e(u, v):
            A[pos[u]][pos[v]] = A[pos[v]][pos[u]] = 1
        for i in range(9):
            for j in range(9):
                if B[i][j]: e(('x', i), ('y', j))
        for a in F:
            for c in (a, s[a]):
                e(('p',), ('v', c))
                for i in DEF[c]: e(('v', c), ('x', i))
                for j in DEF[s[c]]: e(('v', c), ('y', j))
            e(('v', a), ('v', s[a]))
        for u in range(m):
            for v in range(u + 1, m):
                c = sum(A[u][k] & A[v][k] for k in range(m))
                if c > 2 - A[u][v]: return False
        LASTA[0] = np.array(A, dtype=float)
        return True
    LASTA = [None]
    def psd_both():
        A = LASTA[0]; m = len(A)
        M1 = 9 * (3 * np.eye(m) - A) + np.ones((m, m))
        M2 = 11 * (4 * np.eye(m) + A) - 2 * np.ones((m, m))
        return np.linalg.eigvalsh(M1)[0] > -1e-7, np.linalg.eigvalsh(M2)[0] > -1e-7
    def w_types_exist(s, F):
        """Existence of the mate pairs of W = N(p) n X_1 with types (i;j),(j;i), i != j:
        x_i has exactly 2 - f_i neighbours in W; the cell (i,j) must have room (req - cover by ALL X_2 >= number used);
        a W vertex and an A_p vertex share p, so they share at most one support neighbour; same for two W vertices of
        different pairs; two W pairs cannot have the same unordered type."""
        f = [0] * 9
        Ap = []
        for a in F:
            for c in (a, s[a]):
                Ap.append((set(DEF[c]), set(DEF[s[c]])))
                for i in DEF[c]: f[i] += 1
        need = [2 - x for x in f]
        if min(need) < 0: return False
        cov = [[0] * 9 for _ in range(9)]
        for a in range(n):
            for i in DEF[a]:
                for j in DEF[s[a]]:
                    cov[i][j] += 1
        npairs = sum(need) // 2
        if sum(need) % 2: return False
        cells = [(i, j) for i in range(9) for j in range(i + 1, 9)
                 if cov[i][j] < req[i][j] and cov[j][i] < req[j][i]
                 and all(not (i in U and j in V) and not (j in U and i in V) for U, V in Ap)]
        def rec2(k, start, chosen, nd):
            if k == npairs:
                return all(x == 0 for x in nd)
            for t in range(start, len(cells)):
                i, j = cells[t]
                if nd[i] == 0 or nd[j] == 0: continue
                # two W vertices of different pairs share p: at most one more common neighbour
                bad = False
                for (a, b) in chosen:
                    # w=(i;j), sw=(j;i) against w'=(a;b), sw'=(b;a)
                    if (i == a and j == b) or (i == b and j == a): bad = True   # same unordered type (excluded by hand)
                if bad: continue
                nd[i] -= 1; nd[j] -= 1
                if rec2(k + 1, t + 1, chosen + [(i, j)], nd):
                    nd[i] += 1; nd[j] += 1
                    return True
                nd[i] += 1; nd[j] += 1
            return False
        return rec2(0, 0, [], need[:])
    for h2 in (3, 2):
        cnt_b = 0; cnt_bw = 0; taus_b = 0; cnt_p1 = 0; cnt_p12 = 0; cnt_p12w = 0
        for s in reps:
            orbs = [a for a in range(n) if a < s[a]]
            usable = [a for a in orbs if not (set(DEF[a]) & set(DEF[s[a]]))]
            hit = False
            for F in itertools.combinations(usable, h2):
                if budgets_Ap(s, F):
                    cnt_b += 1; hit = True
                    p1, p2 = psd_both()
                    cnt_p1 += p1; cnt_p12 += (p1 and p2)
                    we = w_types_exist(s, F)
                    if we: cnt_bw += 1
                    cnt_p12w += (p1 and p2 and we)
            taus_b += hit
        print(f"   |F| = {h2}: pairs (tau rep, F) passing all budgets on S u p u A_p: {cnt_b} (in {taus_b} matchings); "
              f"and admitting a type solution for W: {cnt_bw}; budgets + PSD(M1): {cnt_p1}; budgets + PSD(M1,M2): {cnt_p12}; "
              f"budgets + PSD(M1,M2) + W types: {cnt_p12w}")

for nm in (sys.argv[1:] or ["B2", "B1", "B0"]):
    run(nm)
