# Referee 2: independent run of profile (3,3,1) (Computation 7.6, steps 1-4), written from sections 6, 7.1-7.4 of the text.
# Structure used: Lemma 7.4 / table of Lemma 7.5, forced numbers (F1), (F3), (F4), (F5), (F6).  NOT used: (F2), (F7).
# Tests: budgets (Lemma 6.2) and PSD of M1, M2 (Lemma 6.1) on determined sets.  Rejections are exact.
# numbering: x_i = i, y_i = 9+i, p = 18, s_k = 19+k, z_0 = 37, sigma z_0 = 38, X_0' = 39..44, W = 45..50
# usage: python p331.py <s> <part> <nparts>
import sys, json, itertools, time
import numpy as np
from collections import Counter
from common import *
from flint import fmpz_mat

s_ = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3])
adjB = Bgraph(s_)
js = json.load(open("my_tau_%d.json" % s_))
D = [tuple(u) for u in js["D"]]
REPS = [tuple(t) for t in js["orbit_reps"]]
P, Z0, SZ0 = 18, 37, 38
pc = int.bit_count
ST = Counter()

def exact_neg(M):
    n = len(M)
    cp = fmpz_mat(M).charpoly()
    q = [int(cp[i]) * (-1) ** i for i in range(n + 1)]
    q = [c for c in q if c != 0]
    return sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0)) > 0

def psd_reject(adj, verts):
    ST["psd_tests"] += 1
    n = len(verts)
    A = np.zeros((n, n))
    for a, u in enumerate(verts):
        m = adj[u]
        for b, v in enumerate(verts):
            if (m >> v) & 1:
                A[a, b] = 1.0
    for which in (1, 2):
        M = (27 * np.eye(n) - 9 * A + 1) if which == 1 else (44 * np.eye(n) + 11 * A - 2)
        w, V = np.linalg.eigh(M)
        if w[0] < -1e-7:
            Mi = [[int(round(x)) for x in row] for row in M]
            v = V[:, 0]
            for scale in (6, 12, 30, 60, 120, 1000):
                x = [int(round(t * scale / max(abs(v)))) for t in v]
                q = sum(x[i] * Mi[i][j] * x[j] for i in range(n) for j in range(n))
                if q < 0:
                    ST["rej_psd_cert_M%d" % which] += 1
                    return True
            if exact_neg(Mi):
                ST["rej_psd_charpoly"] += 1
                return True
            ST["float_neg_but_exactly_psd"] += 1
    return False

def budget_all(adj, verts):
    for a in range(len(verts)):
        u = verts[a]; au = adj[u]
        for b in range(a + 1, len(verts)):
            v = verts[b]
            if pc(au & adj[v]) > (1 if (au >> v) & 1 else 2):
                return False
    return True

def budget_verts(adj, verts, new):
    for u in new:
        au = adj[u]
        for v in verts:
            if v != u and pc(au & adj[v]) > (1 if (au >> v) & 1 else 2):
                return False
        nb = [v for v in verts if (au >> v) & 1]
        for a in range(len(nb)):
            x = adj[nb[a]]
            for b in range(a + 1, len(nb)):
                if pc(x & adj[nb[b]]) > (1 if (x >> nb[b]) & 1 else 2):
                    return False
    return True

def step12(ti):
    """yield the 39-vertex survivors (F, adjacency, orbs) of matching ti."""
    tau = REPS[ti]
    N = 39
    base = [0] * N
    def E(ad, a, b):
        ad[a] |= 1 << b; ad[b] |= 1 << a
    for i in range(9):
        for j in adjB[i]:
            E(base, i, 9 + j)
    for k in range(18):
        for i in D[k]:
            E(base, 19 + k, i)
        for l in D[tau[k]]:
            E(base, 19 + k, 9 + l)
    usable = [a for a in range(18) if a < tau[a] and not (set(D[a]) & set(D[tau[a]]))]
    res = []
    for F in itertools.combinations(usable, 3):
        adj = base[:]
        Ap = []
        for a in F:
            Ap += [a, tau[a]]
            E(adj, 19 + a, 19 + tau[a])
        for k in Ap:
            E(adj, P, 19 + k)
        v25 = list(range(19)) + [19 + k for k in Ap]
        m25 = sum(1 << v for v in v25)
        if not budget_all([x & m25 for x in adj], v25):
            continue
        ST["tauF_budget25"] += 1
        E(adj, Z0, P); E(adj, SZ0, P); E(adj, Z0, SZ0)
        allv = list(range(N))
        if not budget_all(adj, allv):
            ST["rej_budget"] += 1
            continue
        v27 = v25 + [Z0, SZ0]
        if psd_reject(adj, v27):
            continue
        orbs = [(a, tau[a]) for a in range(18) if a < tau[a] and a not in F]

        def local(ad, touched):
            for u in touched:
                au = ad[u]
                for v in allv:
                    if v != u and pc(au & ad[v]) > (1 if (au >> v) & 1 else 2):
                        return False
            return True

        def place(m, adj):
            if m == len(orbs):
                ST["survivors39"] += 1
                res.append((F, adj, orbs))
                return
            s, ss = 19 + orbs[m][0], 19 + orbs[m][1]
            verts = v27 + [19 + k for o in orbs[:m + 1] for k in o]
            for side in ((0,) if m == 0 else (0, 1)):
                a0 = adj[:]
                if side == 0:
                    E(a0, s, Z0); E(a0, ss, SZ0)
                else:
                    E(a0, s, SZ0); E(a0, ss, Z0)
                if not local(a0, (s, ss, Z0, SZ0)):
                    ST["rej_budget"] += 1
                    continue

                def choose(j, ad):
                    if j == m:
                        ST["nodes2"] += 1
                        if psd_reject(ad, verts):
                            return
                        place(m + 1, ad)
                        return
                    a, sa = 19 + orbs[j][0], 19 + orbs[j][1]
                    for opt in range(4):
                        a2 = ad
                        if opt:
                            a2 = ad[:]
                            if opt & 1:
                                E(a2, s, a); E(a2, ss, sa)
                            if opt & 2:
                                E(a2, s, sa); E(a2, ss, a)
                            if not local(a2, (s, ss, a, sa)):
                                ST["rej_budget"] += 1
                                continue
                        choose(j + 1, a2)
                choose(0, a0)
        place(0, adj)
    return res

def step34(ti, F, adj39, orbs):
    tau = REPS[ti]
    Ap = []
    for a in F:
        Ap += [a, tau[a]]
    X2mask = sum(1 << (19 + k) for k in range(18))
    hdeg = {k: pc(adj39[19 + k] & X2mask) for o in orbs for k in o}
    col = {k: 2 for k in Ap}
    for k in hdeg:
        col[k] = hdeg[k] + 1
    Y1 = list(range(39))
    # ---- candidate rows: R subset of X_2, exactly 2 in A_p (different orbits), >= 2 in X_2'
    rows = set()
    q, sq = 39, 40
    verts = Y1 + [q, sq]
    for (fa, fb) in itertools.combinations(F, 2):
        for a in (fa, tau[fa]):
            for b in (fb, tau[fb]):
                ad = adj39[:] + [0, 0]
                for k in (a, b):
                    ad[q] |= 1 << (19 + k); ad[19 + k] |= 1 << q
                    ad[sq] |= 1 << (19 + tau[k]); ad[19 + tau[k]] |= 1 << sq
                if not budget_verts(ad, verts, [q, sq]):
                    continue
                def rec(m, ad, R):
                    if m == len(orbs):
                        if len(R) >= 4:
                            rows.add(frozenset(R))
                        return
                    u, v = orbs[m]
                    for opt in range(4):
                        a2 = ad; R2 = R
                        if opt:
                            a2 = ad[:]
                            ks = ([u] if opt & 1 else []) + ([v] if opt & 2 else [])
                            for k in ks:
                                a2[q] |= 1 << (19 + k); a2[19 + k] |= 1 << q
                                a2[sq] |= 1 << (19 + tau[k]); a2[19 + tau[k]] |= 1 << sq
                            if not budget_verts(a2, verts, [q, sq]):
                                continue
                            R2 = R + ks
                        rec(m + 1, a2, R2)
                rec(0, ad, [a, b])
    ST["rows"] += len(rows)
    rorb = sorted(set(tuple(sorted([tuple(sorted(R)), tuple(sorted(tau[k] for k in R))])) for R in rows))
    # ---- three row orbits with the right column sums (F3)
    cnt = [[(1 if k in ro[0] else 0) + (1 if k in ro[1] else 0) for k in range(18)] for ro in rorb]
    target = [col[k] for k in range(18)]
    out_tables = []
    def cov(start, chosen, cur):
        if len(chosen) == 3:
            if cur == target:
                ST["covers"] += 1
                tables(chosen)
            return
        for r in range(start, len(rorb)):
            c2 = [cur[k] + cnt[r][k] for k in range(18)]
            if any(c2[k] > target[k] for k in range(18)):
                continue
            cov(r + 1, chosen + [r], c2)
    def tables(chosen):
        R = []
        for r in chosen:
            R += [rorb[r][0], rorb[r][1]]         # vertices 39..44: q_a = 39+2a, sigma q_a = 40+2a
        deg = [len(R[2 * a]) - 4 for a in range(3)]
        for opts in itertools.product(range(4), repeat=3):
            d = [0, 0, 0]
            prs = [(0, 1), (0, 2), (1, 2)]
            for (a, b), o in zip(prs, opts):
                c = (o & 1) + ((o >> 1) & 1)
                d[a] += c; d[b] += c
            if d != deg:
                continue
            ST["tables_F3F4"] += 1
            ad = adj39[:] + [0] * 6
            for a in range(6):
                for k in R[a]:
                    ad[39 + a] |= 1 << (19 + k); ad[19 + k] |= 1 << (39 + a)
            for (a, b), o in zip(prs, opts):
                if o & 1:
                    for (u, v) in ((39 + 2 * a, 39 + 2 * b), (40 + 2 * a, 40 + 2 * b)):
                        ad[u] |= 1 << v; ad[v] |= 1 << u
                if o & 2:
                    for (u, v) in ((39 + 2 * a, 40 + 2 * b), (40 + 2 * a, 39 + 2 * b)):
                        ad[u] |= 1 << v; ad[v] |= 1 << u
            Y = list(range(45))
            if not budget_verts(ad, Y, list(range(39, 45))):
                continue
            ST["tables_budget45"] += 1
            if psd_reject(ad, Y):
                continue
            ST["tables_psd45"] += 1
            out_tables.append(ad)
    cov(0, [], [0] * 18)
    # ---- step 4
    Apmask = sum(1 << (19 + k) for k in Ap)
    f = [pc(adj39[i] & Apmask) for i in range(9)]
    need0 = [2 - x for x in f]
    X2p = [k for o in orbs for k in o]
    for ad45 in out_tables:
        def types(c, need, chosen, last):
            if c == 3:
                if not any(need):
                    ST["type_solutions"] += 1
                    addW(0, ad45[:] + [0] * 6, chosen, set())
                return
            try:
                i = next(x for x in range(9) if need[x] > 0)
            except StopIteration:
                return
            for j in range(i + 1, 9):
                if need[j] == 0 or (last is not None and last[0] == i and j <= last[1]):
                    continue
                need[i] -= 1; need[j] -= 1
                types(c + 1, need, chosen + [(i, j)], (i, j))
                need[i] += 1; need[j] += 1
        def addW(c, ad, chosen, used):
            if c == 3:
                if len(used) != 12:
                    return
                ST["graphs51_budget"] += 1
                if not psd_reject(ad, list(range(51))):
                    ST["graphs51_psd"] += 1
                return
            i, j = chosen[c]
            w, sw = 45 + 2 * c, 46 + 2 * c
            verts = list(range(45 + 2 * (c + 1)))
            for k, l in itertools.combinations(X2p, 2):
                if l == tau[k] or k in used or l in used:
                    continue
                a2 = ad[:]
                def E(a, b):
                    a2[a] |= 1 << b; a2[b] |= 1 << a
                E(w, P); E(sw, P); E(w, sw); E(w, i); E(w, 9 + j); E(sw, j); E(sw, 9 + i)
                E(w, 19 + k); E(w, 19 + l); E(sw, 19 + tau[k]); E(sw, 19 + tau[l])
                if not budget_verts(a2, verts, [w, sw]):
                    continue
                addW(c + 1, a2, chosen, used | {k, l, tau[k], tau[l]})
        types(0, need0[:], [], None)

if __name__ == "__main__":
    t0 = time.time()
    carriers_tau = set(); carriers_F = set(); tau_tab = set()
    for ti in range(len(REPS)):
        if ti % nparts != part:
            continue
        for (F, adj39, orbs) in step12(ti):
            carriers_tau.add(ti); carriers_F.add((ti, F))
            before = ST["tables_psd45"]
            step34(ti, F, adj39, orbs)
            if ST["tables_psd45"] > before:
                tau_tab.add(ti)
        if (ti // nparts) % 40 == 0:
            print("  [%ds] tau %d/%d %s" % (time.time() - t0, ti, len(REPS), dict(ST)), flush=True)
    print("B%d profile (3,3,1) part %d/%d: %s  (%.0fs)" % (s_, part, nparts, dict(ST), time.time() - t0))
    print("matchings carrying 39-vertex survivors: %d ; pairs (tau,F): %d ; matchings carrying PSD tables: %d"
          % (len(carriers_tau), len(carriers_F), len(tau_tab)))
    json.dump({"s": s_, "part": part, "nparts": nparts, "stats": dict(ST), "carriers_tau": sorted(carriers_tau),
               "carriers_F": sorted([t, list(F)] for t, F in carriers_F), "tau_tab": sorted(tau_tab)},
              open("my331_%d_%dof%d.json" % (s_, part, nparts), "w"))
