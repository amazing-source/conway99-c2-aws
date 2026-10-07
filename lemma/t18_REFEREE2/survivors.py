# Referee 2: the four stage-C survivors of B1, rebuilt from Appendix B of T18_PROOF.md only.
# Checks: admissibility of tau, forced numbers (C1)-(C8), budgets, sigma-invariance, exact PSD and ranks of M1, M2,
# det/rank of G_odd, rank of G_even (Computation 8.6), and stage D (Computation 8.8) with exact PSD decisions.
import json, itertools, sys
from common import *
from flint import fmpz_mat, fmpz_poly

s_ = 1
adjB = Bgraph(1)
D = deficient_pairs(adjB)
assert D == [(int(e[0]), int(e[1])) for e in "01 02 03 04 13 16 18 24 27 28 35 37 45 46 56 57 68 78".split()]

def mk_tau(pairs):
    t = [-1] * 18
    for a, b in pairs:
        t[a] = b
        t[b] = a
    assert -1 not in t
    return t

TAU813 = mk_tau([(0, 5), (1, 8), (2, 15), (3, 14), (4, 7), (6, 10), (9, 12), (11, 17), (13, 16)])
TAU975 = mk_tau([(0, 5), (1, 12), (2, 17), (3, 14), (4, 11), (6, 10), (7, 9), (8, 15), (13, 16)])

SURV = [
    dict(name="#813 F=[2,9]", tau=TAU813, Ap=[2, 9, 12, 15], H=[(0, 12), (2, 15), (5, 9), (9, 12)],
         W=[((0, 4), [6, 11, 13]), ((1, 3), [3, 8, 16]), ((1, 6), [6, 7]), ((2, 8), [3, 4, 17]), ((6, 7), [0, 8])],
         tauK=[[10, 16, 17], [1, 13, 14], [4, 10], [7, 11, 14], [1, 5]]),
    dict(name="#813 F=[3,6]", tau=TAU813, Ap=[3, 6, 10, 14], H=[(1, 10), (3, 14), (6, 8), (6, 10)],
         W=[((0, 3), [9, 11, 13]), ((1, 8), [2, 7, 16]), ((2, 4), [2, 5, 17]), ((2, 7), [4, 9]), ((6, 7), [0, 8])],
         tauK=[[12, 16, 17], [4, 13, 15], [0, 11, 15], [7, 12], [1, 5]]),
    dict(name="#975 F=[1,2]", tau=TAU975, Ap=[1, 2, 12, 17], H=[(1, 12), (2, 17)],
         W=[((1, 2), [6, 11, 13]), ((1, 8), [3, 9, 15]), ((3, 4), [5, 8, 13]), ((5, 6), [5, 7, 11]), ((6, 7), [3, 10])],
         tauK=[[4, 10, 16], [7, 8, 14], [0, 15, 16], [0, 4, 9], [6, 14]]),
    dict(name="#975 F=[3,6]", tau=TAU975, Ap=[3, 6, 10, 14], H=[(3, 14), (6, 10)],
         W=[((0, 2), [4, 8, 13]), ((1, 2), [1, 17]), ((3, 4), [5, 7, 8]), ((6, 7), [2, 9, 11]), ((7, 8), [0, 12, 16])],
         tauK=[[11, 15, 16], [2, 12], [0, 9, 15], [4, 7, 17], [1, 5, 13]]),
]

X = lambda i: i
Y = lambda i: 9 + i
P = 18
S_ = lambda k: 19 + k
Wv = lambda c: 37 + 2 * c
sWv = lambda c: 38 + 2 * c

def build(sv):
    tau = sv["tau"]
    n = 47
    nb = [set() for _ in range(n)]
    def E(a, b):
        assert a != b
        nb[a].add(b)
        nb[b].add(a)
    for i in range(9):
        for j in adjB[i]:
            E(X(i), Y(j))
    for k in range(18):
        for i in D[k]:
            E(S_(k), X(i))
        for l in D[tau[k]]:
            E(S_(k), Y(l))
    for k in sv["Ap"]:
        E(P, S_(k))
    for a, b in sv["H"]:
        E(S_(a), S_(b))
    for c, ((i, j), K) in enumerate(sv["W"]):
        E(P, Wv(c)); E(P, sWv(c)); E(Wv(c), sWv(c))
        E(Wv(c), X(i)); E(Wv(c), Y(j)); E(sWv(c), X(j)); E(sWv(c), Y(i))
        for k in K:
            E(Wv(c), S_(k))
            E(sWv(c), S_(tau[k]))
    sig = list(range(n))
    for i in range(9):
        sig[X(i)] = Y(i); sig[Y(i)] = X(i)
    for k in range(18):
        sig[S_(k)] = S_(tau[k])
    for c in range(5):
        sig[Wv(c)] = sWv(c); sig[sWv(c)] = Wv(c)
    return nb, sig

def mats(nb):
    n = len(nb)
    A = [[1 if j in nb[i] else 0 for j in range(n)] for i in range(n)]
    M1 = [[(27 if i == j else 0) - 9 * A[i][j] + 1 for j in range(n)] for i in range(n)]
    M2 = [[(44 if i == j else 0) + 11 * A[i][j] - 2 for j in range(n)] for i in range(n)]
    return A, M1, M2

def neg_count_and_rank(M):
    """exact: (number of negative eigenvalues, rank) of an integer symmetric matrix, via the characteristic
    polynomial (all roots real: Descartes' rule of signs is exact)."""
    n = len(M)
    cp = fmpz_mat(M).charpoly()
    co = [int(cp[i]) for i in range(n + 1)]
    # multiplicity of 0
    z = 0
    while co[z] == 0:
        z += 1
    rank = n - z
    # negative roots of p(x) = positive roots of p(-x)
    q = [co[i] * (-1) ** i for i in range(n + 1)]
    q = [c for c in q if c != 0]
    neg = sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0))
    return neg, rank

def check_R(adjB, D, tau):
    idx = {U: k for k, U in enumerate(D)}
    for a in range(18):
        b = tau[a]
        if b == a or tau[b] != a:
            return False
        U, V = D[a], D[b]
        for i in U:
            if len(adjB[i] & set(V)) > 1:
                return False
        for l in V:
            if len(adjB[l] & set(U)) > 1:
                return False
    for i in range(9):
        for l in range(9):
            c = sum(1 for a in range(18) if i in D[a] and l in D[tau[a]])
            if c > 2 - (1 if l in adjB[i] else 0):
                return False
    return True

def main():
    try:
        reps = json.load(open(r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma\t18\r2_tau_1.json"))["reps"]
        print("tau #813 of r2_tau_1.json equals Appendix B:", list(reps[813]) == TAU813,
              "; tau #975:", list(reps[975]) == TAU975)
    except Exception as ex:
        print("r2_tau_1.json not compared:", ex)
    for sv in SURV:
        print("=====", sv["name"], "=====")
        tau = sv["tau"]
        print("tau admissible (R1),(R2):", check_R(adjB, D, tau))
        # printed tau K
        for c, ((i, j), K) in enumerate(sv["W"]):
            assert sorted(tau[k] for k in K) == sorted(sv["tauK"][c]), ("tau K misprint", c)
        print("printed 'tau K' columns consistent with tau: True")
        Ap = set(sv["Ap"])
        assert all(tau[k] in Ap for k in Ap)
        # C1: usable
        print("(C1) rectangles of F usable (disjoint):", all(not (set(D[k]) & set(D[tau[k]])) for k in Ap))
        nb, sig = build(sv)
        n = 47
        print("degrees ok / sigma is an automorphism of the 47-vertex graph:",
              all(sig[sig[v]] == v for v in range(n)) and
              all({sig[u] for u in nb[v]} == nb[sig[v]] for v in range(n)))
        print("budget violations on 47 vertices:", len(budget_violations(nb)))
        X2 = [S_(k) for k in range(18)]
        X2p = [S_(k) for k in range(18) if k not in Ap]
        Wl = [Wv(c) for c in range(5)] + [sWv(c) for c in range(5)]
        a2 = {v: len(nb[v] & set(X2)) for v in range(n)}
        t = sum(a2[v] for v in X2) // 2
        print("t =", t, "; a_2 on A_p:", [a2[S_(k)] for k in sorted(Ap)], "; a_2 on w_c:", [a2[Wv(c)] for c in range(5)])
        # C2
        c2 = all(((S_(tau[k]) in nb[S_(k)]) == (k in Ap)) for k in range(18)) and max(a2[v] for v in X2) <= 4
        FL = sum(a2[S_(k)] - 1 for k in Ap)
        m = [0, 2, 4, 6, 8, 14, 20, 26, 32, 42]
        c4 = t <= 9 and sum(a2[v] * (a2[v] - 1) for v in X2) + m[t] <= 36
        f = [len(nb[X(i)] & {S_(k) for k in Ap}) for i in range(9)]
        types = [frozenset(ij) for ij, K in sv["W"]]
        c5 = len(set(types)) == 5 and all(len(ty) == 2 for ty in types) and \
            all(sum(1 for ty in types if i in ty) == 2 - f[i] for i in range(9))
        c6 = True
        for (i, j), K in sv["W"]:
            for (a, b) in ((i, j), (j, i)):
                cnt = sum(1 for k in range(18) if a in D[k] and b in D[tau[k]])
                if cnt > 1 - (1 if b in adjB[a] else 0):
                    c6 = False
        slack = 4 - FL // 2
        c7 = all(set(K) <= set(range(18)) - Ap and not any(tau[k] in K for k in K) and 2 <= len(K) <= 2 + slack
                 for ij, K in sv["W"]) and sum(len(K) - 2 for ij, K in sv["W"]) == slack
        c8 = True
        for k in range(18):
            if k in Ap:
                continue
            req = 2 - len(nb[S_(k)] & {S_(a) for a in Ap})
            cnt = sum(1 for ij, K in sv["W"] if k in K) + sum(1 for ij, K in sv["W"] if tau[k] in K)
            if cnt != req:
                c8 = False
        print("(C2) %s (C3) FL=%d even,<=8: %s (C4) %s (C5) %s (C6) %s (C7) %s (C8) %s"
              % (c2, FL, FL % 2 == 0 and FL <= 8, c4, c5, c6, c7, c8))
        # Corollary 2.2 on the 47 vertices: every vertex outside N[p] of S and X2' has exactly 2 neighbours in N(p)
        Np = nb[P]
        print("every vertex of S u X_2' has exactly 2 neighbours in N(p) (Cor 2.2):",
              all(len(nb[v] & Np) == 2 for v in list(range(18)) + X2p))
        A, M1, M2 = mats(nb)
        n1, r1 = neg_count_and_rank(M1)
        n2, r2 = neg_count_and_rank(M2)
        print("M1[Y47]: negative eigenvalues %d, rank %d ; M2[Y47]: negative eigenvalues %d, rank %d" % (n1, r1, n2, r2))
        # kernel remark
        kv = [0] * n
        kv[P] = 4
        for v in Np:
            kv[v] = 1
        print("M1 * (4 e_p + 1_N(p)) == 0:", all(sum(M1[i][j] * kv[j] for j in range(n)) == 0 for i in range(n)))
        # rank bound
        R = [X(i) for i in range(9)] + [S_(k) for k in range(18) if k < tau[k]] + [Wv(c) for c in range(5)]
        assert len(R) == 23
        Godd = [[(3 if x == y else 0) - A[x][y] + A[x][sig[y]] for y in R] for x in R]
        Gm = fmpz_mat(Godd)
        # cross-check the definition against u^T M1 u = 18 G_odd
        ok = True
        for a, x in enumerate(R):
            for b, y in enumerate(R):
                val = M1[x][y] - M1[x][sig[y]] - M1[sig[x]][y] + M1[sig[x]][sig[y]]
                if val != 18 * Godd[a][b]:
                    ok = False
        print("u^T M1 u == 18 G_odd entrywise:", ok)
        print("det G_odd =", int(Gm.det()), " rank G_odd =", Gm.rank())
        gens = [[x, sig[x]] for x in R] + [[P]]
        Geven = [[sum(M1[a][b] for a in g for b in h) for h in gens] for g in gens]
        # explicit formula of Prop 6.4 (b)
        okf = True
        for a, x in enumerate(R):
            for b, y in enumerate(R):
                if a == b:
                    ex = 58 - 18 * A[x][sig[x]]
                else:
                    ex = 4 - 18 * (A[x][y] + A[x][sig[y]])
                if ex != Geven[a][b]:
                    okf = False
            if Geven[23][a] != 2 - 18 * A[P][x]:
                okf = False
        if Geven[23][23] != 28:
            okf = False
        print("explicit entries of G_even as in Prop 6.4(b):", okf, " rank G_even =", fmpz_mat(Geven).rank())

        # ---------------- stage D ----------------
        cand = X2 + Wl
        need = {}
        for k in range(18):
            v = S_(k)
            need[v] = a2[v] + 2 - (1 if k in Ap else 0)
        for w in Wl:
            need[w] = a2[w] - 2
        ApW = {S_(k) for k in Ap} | set(Wl)
        X2set = set(X2)
        results = {}
        for cap in ("with (D3) upper bound", "without upper bound"):
            found = []
            hi = 4 + t if cap.startswith("with (") else 99
            cnt = [0] * n          # |Z n N(u)|
            Z = []
            inZ = [False] * n

            def rec(pos, nApW, nX2):
                if pos == len(cand):
                    if nApW == 2 and 4 <= nX2 <= hi:
                        found.append(frozenset(Z))
                    return
                v = cand[pos]
                # exclude v
                rec(pos + 1, nApW, nX2)
                # include v
                if need[v] < 1:
                    return
                if v in ApW and nApW >= 2:
                    return
                if v in X2set and nX2 >= hi:
                    return
                # (D4): v in Z and v in sigma Z (i.e. sigma v in Z)
                if inZ[sig[v]] and (need[v] < 2):
                    return
                # budget for the pair (z, u): |Z n N(u)| <= 2 - [u in Z]
                if cnt[v] > 1:
                    return
                okk = True
                for u in nb[v]:
                    if cnt[u] + 1 > (1 if inZ[u] else 2):
                        okk = False
                        break
                if not okk:
                    return
                for u in nb[v]:
                    cnt[u] += 1
                inZ[v] = True
                Z.append(v)
                rec(pos + 1, nApW + (1 if v in ApW else 0), nX2 + (1 if v in X2set else 0))
                Z.pop()
                inZ[v] = False
                for u in nb[v]:
                    cnt[u] -= 1

            rec(0, 0, 0)
            # full budget test on the 49 vertices
            good = []
            for Zs in found:
                sZ = frozenset(sig[v] for v in Zs)
                nb49 = [set(x) for x in nb] + [set(Zs), set(sZ)]
                for v in Zs:
                    nb49[v].add(47)
                for v in sZ:
                    nb49[v].add(48)
                if budget_ok(nb49):
                    good.append(Zs)
            pairs = set(frozenset((Zs, frozenset(sig[v] for v in Zs))) for Zs in good)
            results[cap] = (len(found), len(good), len(pairs), good)
            print("stage D, %s: %d sets Z pass the z-only tests, %d pass the budget on 49 vertices, %d unordered pairs {Z, sigma Z}; Z = sigma Z occurs: %s"
                  % (cap, len(found), len(good), len(pairs), any(len(pr) == 1 for pr in pairs)))
        good = results["without upper bound"][3]
        # exact PSD decision for every oriented Z (48 and 49 vertices), both matrices
        bad48 = bad49 = 0
        which49 = {"M1": 0, "M2 only": 0}
        for Zs in good:
            sZ = frozenset(sig[v] for v in Zs)
            nb49 = [set(x) for x in nb] + [set(Zs), set(sZ)]
            for v in Zs:
                nb49[v].add(47)
            for v in sZ:
                nb49[v].add(48)
            A9, M19, M29 = mats(nb49)
            neg1, _ = neg_count_and_rank(M19)
            neg2 = 0
            if neg1 == 0:
                neg2, _ = neg_count_and_rank(M29)
            if neg1 + neg2 == 0:
                bad49 += 1
            else:
                which49["M1" if neg1 else "M2 only"] += 1
            M18 = [row[:48] for row in M19[:48]]
            M28 = [row[:48] for row in M29[:48]]
            n18, _ = neg_count_and_rank(M18)
            n28 = 0
            if n18 == 0:
                n28, _ = neg_count_and_rank(M28)
            if n18 + n28 == 0:
                bad48 += 1
        print("stage D (all oriented Z without the upper bound, %d sets): exactly PSD on 49 vertices: %d ; exactly PSD on 48 vertices (Y47 u {z}): %d ; rejected on 49 by %s"
              % (len(good), bad49, bad48, which49))

if __name__ == "__main__":
    main()
