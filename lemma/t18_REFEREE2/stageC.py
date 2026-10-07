# Referee 2: independent stage C of profile (2,5,0) (Computation 8.5), written from sections 8.1, 8.2, 8.4 of the text.
# Input: my own stage-B triples (myB_<s>_*.json).  Tests: (C5), (C7), (C8) of Lemma 8.3, budgets (Lemma 6.2) and
# PSD of M1, M2 (Lemma 6.1) on determined subsets: Y37 u {w, sigma w} (39), Y37 u (placed orbits of W), Y47.
# Rejections are exact (integer count; integer vector with negative form; or exact characteristic polynomial).
# usage: python stageC.py <s> <part> <nparts> <files myB_...json>     writes myC_<s>_<part>of<nparts>.json
import sys, json, itertools, time, glob
import numpy as np
from common import *
from flint import fmpz_mat

s_ = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3])
adjB = Bgraph(s_)
js = json.load(open("my_tau_%d.json" % s_))
D = [tuple(u) for u in js["D"]]
REPS = [tuple(t) for t in js["orbit_reps"]]
TR = []
for fn in sys.argv[4:]:
    for g in sorted(glob.glob(fn)):
        TR += json.load(open(g))["triples"]
TR.sort(key=lambda x: (x[0], x[1], x[2]))
P = 18
pc = int.bit_count
ST = dict(triples=0, dead_counts=0, types_tested=0, K_budget_ok=0, K_psd_ok=0, cover_nodes=0, rej_budget=0,
          rej_psd_cert=0, rej_psd_charpoly=0, float_neg_but_exactly_psd=0, full47_tests=0, survivors=0)

def exact_neg(M):
    n = len(M)
    cp = fmpz_mat(M).charpoly()
    q = [int(cp[i]) * (-1) ** i for i in range(n + 1)]
    q = [c for c in q if c != 0]
    return sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0)) > 0

def psd_reject(adj, verts):
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
                    ST["rej_psd_cert"] += 1
                    return True
            if exact_neg(Mi):
                ST["rej_psd_charpoly"] += 1
                return True
            ST["float_neg_but_exactly_psd"] += 1
    return False

def budget_verts(adj, verts, new):
    """budget for all pairs (u, v), u in new, v in verts; and for all pairs inside N(u), u in new."""
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

def do_triple(ti, F, H):
    tau = REPS[ti]
    n = 47
    adj = [0] * n
    def E(a, b):
        adj[a] |= 1 << b; adj[b] |= 1 << a
    for i in range(9):
        for j in adjB[i]:
            E(i, 9 + j)
    for k in range(18):
        for i in D[k]:
            E(19 + k, i)
        for l in D[tau[k]]:
            E(19 + k, 9 + l)
    Ap = [F[0], tau[F[0]], F[1], tau[F[1]]]
    for k in Ap:
        E(P, 19 + k)
    for k, l in H:
        E(19 + k, 19 + l)
    Y37 = list(range(37))
    Apmask = sum(1 << (19 + k) for k in Ap)
    f = [pc(adj[i] & Apmask) for i in range(9)]
    if max(f) > 2:
        ST["dead_counts"] += 1; return []
    need = [2 - x for x in f]
    X2mask = sum(1 << (19 + k) for k in range(18))
    FL = sum(pc(adj[19 + k] & X2mask) - 1 for k in Ap)
    if FL % 2 or FL > 8:
        ST["dead_counts"] += 1; return []
    slack = 4 - FL // 2
    orbs = [(a, tau[a]) for a in range(18) if a < tau[a] and a not in F]
    req = {k: 2 - pc(adj[19 + k] & Apmask) for o in orbs for k in o}
    if min(req.values()) < 0:
        ST["dead_counts"] += 1; return []
    # ---- all K for every type (i ; j), i < j
    Klist = {}
    for i in range(9):
        for j in range(i + 1, 9):
            if need[i] == 0 or need[j] == 0:
                continue
            ST["types_tested"] += 1
            w, sw = 37, 38
            ad = adj[:37] + [0, 0]
            def E2(a, b):
                ad[a] |= 1 << b; ad[b] |= 1 << a
            E2(w, P); E2(sw, P); E2(w, sw); E2(w, i); E2(w, 9 + j); E2(sw, j); E2(sw, 9 + i)
            verts = Y37 + [w, sw]
            if not budget_verts(ad, verts, [w, sw]):
                ST["rej_budget"] += 1
                Klist[(i, j)] = []
                continue
            res = []
            def rec(m, ad, K):
                if m == len(orbs):
                    if len(K) >= 2:
                        ST["K_budget_ok"] += 1
                        if not psd_reject(ad, verts):
                            ST["K_psd_ok"] += 1
                            res.append(tuple(K))
                    return
                rec(m + 1, ad, K)
                if len(K) >= 2 + slack:
                    return
                a, b = orbs[m]
                if req[a] < 1:
                    return
                for (k, sk) in ((a, b), (b, a)):
                    a2 = ad[:]
                    a2[w] |= 1 << (19 + k); a2[19 + k] |= 1 << w
                    a2[sw] |= 1 << (19 + sk); a2[19 + sk] |= 1 << sw
                    if budget_verts(a2, verts, [w, sw]):
                        rec(m + 1, a2, K + [k])
                    else:
                        ST["rej_budget"] += 1
            rec(0, ad, [])
            Klist[(i, j)] = res
    # ---- exact cover by 5 types
    surv = []
    def cover(c, ad, need, cov, chosen, last):
        ST["cover_nodes"] += 1
        if c == 5:
            if any(need) or any(cov[k] != req[k] for k in req):
                return
            ST["full47_tests"] += 1
            surv.append([list(x) for x in chosen])
            return
        try:
            i = next(q for q in range(9) if need[q] > 0)
        except StopIteration:
            return
        for j in range(i + 1, 9):
            if need[j] == 0 or (last is not None and last[0] == i and j <= last[1]):
                continue
            for K in Klist.get((i, j), []):
                ok = True
                for k in K:
                    if cov[k] + 1 > req[k] or cov[tau[k]] + 1 > req[tau[k]]:
                        ok = False; break
                if not ok:
                    continue
                w, sw = 37 + 2 * c, 38 + 2 * c
                a2 = ad[:]
                def E3(a, b):
                    a2[a] |= 1 << b; a2[b] |= 1 << a
                E3(w, P); E3(sw, P); E3(w, sw); E3(w, i); E3(w, 9 + j); E3(sw, j); E3(sw, 9 + i)
                for k in K:
                    E3(w, 19 + k); E3(sw, 19 + tau[k])
                verts = list(range(37 + 2 * (c + 1)))
                if not budget_verts(a2, verts, [w, sw]):
                    ST["rej_budget"] += 1
                    continue
                if c >= 1 and psd_reject(a2, verts):
                    continue
                need[i] -= 1; need[j] -= 1
                for k in K:
                    cov[k] += 1; cov[tau[k]] += 1
                cover(c + 1, a2, need, cov, chosen + [((i, j), K)], (i, j))
                for k in K:
                    cov[k] -= 1; cov[tau[k]] -= 1
                need[i] += 1; need[j] += 1
    cover(0, adj[:], need[:], {k: 0 for k in req}, [], None)
    return surv

if __name__ == "__main__":
    t0 = time.time()
    OUT = []
    for idx, (ti, F, H) in enumerate(TR):
        if idx % nparts != part:
            continue
        ST["triples"] += 1
        for sv in do_triple(ti, F, H):
            ST["survivors"] += 1
            OUT.append({"tau_index_mine": ti, "tau": list(REPS[ti]), "F": F, "H": H, "W": sv})
        if ST["triples"] % 20 == 0:
            print("  [%ds] %s" % (time.time() - t0, ST), flush=True)
    print("B%d stage C part %d/%d: triples in the input %d; %s  (%.0fs)" % (s_, part, nparts, len(TR), ST, time.time() - t0))
    print("stage-C survivors:", len(OUT))
    for o in OUT:
        print("   my matching #%d, F = %s, t = %d, types and K: %s" % (o["tau_index_mine"], o["F"], len(o["H"]), o["W"]))
    json.dump({"s": s_, "part": part, "nparts": nparts, "stats": ST, "survivors": OUT},
              open("myC_%d_%dof%d.json" % (s_, part, nparts), "w"))
