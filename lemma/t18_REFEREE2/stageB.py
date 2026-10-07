# Referee 2: independent stage B of profile (2,5,0) (Computation 8.4), written from sections 6, 7.1, 8.1-8.3 of the text.
# Only budgets (Lemma 6.2) and PSD of M1, M2 (Lemma 6.1) are used, plus the structure: p ~ A_p, mate edges exactly on A_p,
# no edge between the two orbits of A_p (Lemma 8.1 (a)).  (C2 degree cap), (C3), (C4) are NOT used; they are only recorded.
# A rejection is exact: budget = integer count; PSD = integer vector with negative quadratic form (Python integers),
# or else an exact characteristic polynomial.  "Kept" = no exact violation found (float eigenvalue >= -1e-7, or exact).
# usage: python stageB.py <s> [first] [last]      reads my_tau_<s>.json (my own representatives), writes myB_<s>.json
import sys, json, itertools, time
import numpy as np
from common import *
from flint import fmpz_mat

s_ = int(sys.argv[1])
adjB = Bgraph(s_)
js = json.load(open("my_tau_%d.json" % s_))
D = [tuple(u) for u in js["D"]]
REPS = [tuple(t) for t in js["orbit_reps"]]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(REPS)
N = 37
P = 18
ST = dict(tauF=0, tauF_budget23=0, tauF_psd23=0, nodes=0, rej_budget=0, rej_psd_cert=0, rej_psd_charpoly=0,
          psd_tests=0, leaves=0, float_neg_but_exactly_psd=0)
pc = int.bit_count

def exact_neg(M):
    n = len(M)
    cp = fmpz_mat(M).charpoly()
    q = [int(cp[i]) * (-1) ** i for i in range(n + 1)]
    q = [c for c in q if c != 0]
    return sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0)) > 0

def psd_reject(adj, verts):
    """True iff an exact PSD violation of M1 or M2 is found on the induced subgraph on verts."""
    ST["psd_tests"] += 1
    n = len(verts)
    A = np.zeros((n, n))
    for a, u in enumerate(verts):
        m = adj[u]
        for b, v in enumerate(verts):
            if (m >> v) & 1:
                A[a, b] = 1.0
    for which in (1, 2):
        if which == 1:
            M = 27 * np.eye(n) - 9 * A + 1
        else:
            M = 44 * np.eye(n) + 11 * A - 2
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

def budget_all(adj, verts):
    for a in range(len(verts)):
        u = verts[a]
        au = adj[u]
        for b in range(a + 1, len(verts)):
            v = verts[b]
            if pc(au & adj[v]) > (1 if (au >> v) & 1 else 2):
                return False
    return True

def budget_local(adj, touched):
    for u in touched:
        au = adj[u]
        for v in range(N):
            if v != u and pc(au & adj[v]) > (1 if (au >> v) & 1 else 2):
                return False
    return True

def run():
    out = []
    t0 = time.time()
    base0 = [0] * N
    for i in range(9):
        for j in adjB[i]:
            base0[i] |= 1 << (9 + j)
            base0[9 + j] |= 1 << i
    for ti in range(lo, hi):
        tau = REPS[ti]
        base = base0[:]
        for k in range(18):
            v = 19 + k
            for i in D[k]:
                base[v] |= 1 << i; base[i] |= 1 << v
            for l in D[tau[k]]:
                base[v] |= 1 << (9 + l); base[9 + l] |= 1 << v
        usable = [a for a in range(18) if a < tau[a] and not (set(D[a]) & set(D[tau[a]]))]
        for F in itertools.combinations(usable, 2):
            ST["tauF"] += 1
            adj = base[:]
            Ap = [F[0], tau[F[0]], F[1], tau[F[1]]]
            for k in Ap:
                adj[P] |= 1 << (19 + k); adj[19 + k] |= 1 << P
            for a in F:
                adj[19 + a] |= 1 << (19 + tau[a]); adj[19 + tau[a]] |= 1 << (19 + a)
            v23 = list(range(19)) + [19 + k for k in Ap]
            sub = [adj[u] & sum(1 << v for v in v23) for u in range(N)]
            if not budget_all(sub, v23):
                continue
            ST["tauF_budget23"] += 1
            if psd_reject(adj, v23):
                continue
            ST["tauF_psd23"] += 1
            if not budget_all(adj, list(range(N))):      # all of X_2 present, no edge of H yet (spanning subgraph)
                ST["rej_budget"] += 1
                continue
            orbs = [(a, tau[a]) for a in range(18) if a < tau[a] and a not in F]     # the 7 orbits of X_2'
            earlier0 = [(F[0], tau[F[0]]), (F[1], tau[F[1]])]

            def place(m, adj):
                if m == len(orbs):
                    ST["leaves"] += 1
                    H = sorted((k, l) for k in range(18) for l in range(k + 1, 18) if (adj[19 + k] >> (19 + l)) & 1)
                    out.append([ti, list(F), H])
                    return
                s, ss = 19 + orbs[m][0], 19 + orbs[m][1]
                earlier = earlier0 + orbs[:m]
                verts = v23 + [19 + k for o in orbs[:m + 1] for k in o]

                def choose(j, adj):
                    if j == len(earlier):
                        ST["nodes"] += 1
                        if psd_reject(adj, verts):
                            return
                        place(m + 1, adj)
                        return
                    a, sa = 19 + earlier[j][0], 19 + earlier[j][1]
                    for opt in range(4):
                        ad = adj
                        if opt:
                            ad = adj[:]
                            if opt & 1:
                                ad[s] |= 1 << a; ad[a] |= 1 << s; ad[ss] |= 1 << sa; ad[sa] |= 1 << ss
                            if opt & 2:
                                ad[s] |= 1 << sa; ad[sa] |= 1 << s; ad[ss] |= 1 << a; ad[a] |= 1 << ss
                            if not budget_local(ad, (s, ss, a, sa)):
                                ST["rej_budget"] += 1
                                continue
                        choose(j + 1, ad)

                choose(0, adj)

            place(0, adj)
        if (ti + 1) % 20 == 0:
            print("  [%ds] tau %d/%d %s" % (time.time() - t0, ti + 1, len(REPS), ST), flush=True)
    return out, time.time() - t0

if __name__ == "__main__":
    out, secs = run()
    print("B%d stage B, matchings %d..%d: %s  (%.0fs)" % (s_, lo, hi, ST, secs))
    # statistics on the leaves
    from collections import Counter
    tdist = Counter(); amax = Counter(); c2 = 0; c3 = 0; c4 = 0
    mm = [0, 2, 4, 6, 8, 14, 20, 26, 32, 42]
    for ti, F, H in out:
        tau = REPS[ti]
        deg = [0] * 18
        for k, l in H:
            deg[k] += 1; deg[l] += 1
        t = len(H)
        tdist[t] += 1; amax[max(deg)] += 1
        Ap = [F[0], tau[F[0]], F[1], tau[F[1]]]
        FL = sum(deg[k] - 1 for k in Ap)
        if max(deg) <= 4: c2 += 1
        if FL % 2 == 0 and FL <= 8: c3 += 1
        if t <= 9 and sum(x * (x - 1) for x in deg) + mm[t] <= 36: c4 += 1
    print("stage-B triples: %d ; matchings carrying them: %d ; pairs (tau,F): %d" %
          (len(out), len(set(o[0] for o in out)), len(set((o[0], tuple(o[1])) for o in out))))
    print("by t:", sorted(tdist.items()), " by largest a_2 on X_2:", sorted(amax.items()))
    print("leaves satisfying the degree cap of (C2): %d, (C3): %d, (C4): %d" % (c2, c3, c4))
    json.dump({"s": s_, "lo": lo, "hi": hi, "stats": ST, "triples": out}, open("myB_%d_%d_%d.json" % (s_, lo, hi), "w"))
