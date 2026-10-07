# Referee 2: properties of B0,B1,B2 and stage 1 (Computation 7.3), from the text only.
import sys, json, itertools, math
from common import *

def charpoly_int(adj):
    import sympy
    n = len(adj)
    M = sympy.Matrix(n, n, lambda i, j: 1 if j in adj[i] else 0)
    x = sympy.symbols('x')
    return sympy.factor(M.charpoly(x).as_expr())

def stage1(s, save=None):
    adj = Bgraph(s)
    assert all(len(a) == 4 for a in adj)
    cod = {(i, j): codeg(adj, i, j) for i in range(9) for j in range(i + 1, 9)}
    adjpairs = [(i, j) for (i, j) in cod if j in adj[i]]
    nonadj = [(i, j) for (i, j) in cod if j not in adj[i]]
    tri = sum(1 for i in range(9) for j in range(i + 1, 9) for k in range(j + 1, 9)
              if j in adj[i] and k in adj[i] and k in adj[j])
    aut = automorphisms(adj)
    print("=== B%d ===" % s)
    print("codegree values:", sorted(set(cod.values())))
    print("adjacent pairs with codeg 1 / 2:", sum(1 for e in adjpairs if cod[e] == 1), sum(1 for e in adjpairs if cod[e] == 2))
    print("non-adjacent pairs with codeg 1 / 2:", sum(1 for e in nonadj if cod[e] == 1), sum(1 for e in nonadj if cod[e] == 2))
    print("triangles:", tri, " |Aut|:", len(aut))
    print("charpoly:", charpoly_int(adj))
    D = deficient_pairs(adj)
    docD = [(int(e[0]), int(e[1])) for e in DOC_DEF[s].split()]
    print("deficient pairs (18?):", len(D), " equal to the list printed in the document:", D == docD)
    idx = {U: k for k, U in enumerate(D)}

    # (R1)
    def R1(U, V):
        for i in U:
            if len(adj[i] & set(V)) > 1:
                return False
        for l in V:
            if len(adj[l] & set(U)) > 1:
                return False
        return True

    rect = [[False] * 18 for _ in range(18)]
    nrect = nus = 0
    for a in range(18):
        for b in range(a + 1, 18):
            if R1(D[a], D[b]):
                rect[a][b] = rect[b][a] = True
                nrect += 1
                if not (set(D[a]) & set(D[b])):
                    nus += 1
    print("admissible rectangles:", nrect, " usable in N(p):", nus)

    # matchings with (R2), incremental: cell[i][l] = number of U with i in U, l in tau U
    cap = [[2 - (1 if l in adj[i] else 0) for l in range(9)] for i in range(9)]
    cell = [[0] * 9 for _ in range(9)]
    tau = [-1] * 18
    sols = []

    def add(a, b, sgn):
        # s_a of type (D[a]; D[b]); s_b of type (D[b]; D[a])
        ok = True
        for i in D[a]:
            for l in D[b]:
                cell[i][l] += sgn
                if cell[i][l] > cap[i][l]:
                    ok = False
        for i in D[b]:
            for l in D[a]:
                cell[i][l] += sgn
                if cell[i][l] > cap[i][l]:
                    ok = False
        return ok

    def rec():
        try:
            a = tau.index(-1)
        except ValueError:
            sols.append(tuple(tau))
            return
        for b in range(a + 1, 18):
            if tau[b] == -1 and rect[a][b]:
                ok = add(a, b, +1)
                if ok:
                    tau[a] = b
                    tau[b] = a
                    rec()
                    tau[a] = tau[b] = -1
                add(a, b, -1)

    rec()
    print("admissible matchings:", len(sols))
    # also: count without (R2) (perfect matchings of the rectangle graph), for information
    # orbits under Aut(B)
    perms = []
    for g in aut:
        pd = []
        for U in D:
            V = tuple(sorted((g[U[0]], g[U[1]])))
            pd.append(idx[V])
        perms.append(pd)
    def canon(t):
        best = None
        for pd in perms:
            im = [0] * 18
            for a in range(18):
                im[pd[a]] = pd[t[a]]
            im = tuple(im)
            if best is None or im < best:
                best = im
        return best
    orb = {}
    for t in sols:
        c = canon(t)
        orb.setdefault(c, []).append(t)
    print("orbits under Aut(B):", len(orb))
    # Burnside cross-check
    solset = set(sols)
    fix = 0
    for pd in perms:
        for t in sols:
            im = [0] * 18
            for a in range(18):
                im[pd[a]] = pd[t[a]]
            if tuple(im) == t:
                fix += 1
    print("Burnside: sum of fixed points / |Aut| =", fix, "/", len(aut), "=", fix / len(aut))
    # closure
    closed = all(canon(t) in orb for t in sols)
    # compare with the stored representatives
    try:
        path = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma\t18\r2_tau_%d.json" % s
        js = json.load(open(path))
        reps = js["reps"] if isinstance(js, dict) else js
        reps = [tuple(r) for r in reps]
        allin = all(r in solset for r in reps)
        cs = set(canon(r) for r in reps)
        print("stored reps r2_tau_%d.json: %d entries; all admissible: %s; distinct orbits: %d; cover all my orbits: %s"
              % (s, len(reps), allin, len(cs), cs == set(orb.keys())))
        if isinstance(js, dict):
            print("   keys of the json:", sorted(js.keys()))
            if "pairs" in js or "def" in js or "deficient" in js:
                pass
    except Exception as ex:
        print("could not compare with r2_tau:", repr(ex))
        reps = None
    if save:
        json.dump({"D": D, "orbit_reps": sorted(orb.keys()), "nsols": len(sols)}, open(save % s, "w"))
    return adj, D, sols, orb, aut

if __name__ == "__main__":
    for s in (0, 1, 2):
        stage1(s, save="my_tau_%d.json")
