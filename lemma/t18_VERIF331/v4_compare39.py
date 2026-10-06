"""Set comparison on Y1 (39 vertices): my survivors (v2_surv_<g>_m2_*.json) against the stored survivors of the
first implementation (t18/r2_hfirst_<g>_*.json, OUTPUT files only; read after my own counts were produced).
usage: python v4_compare39.py <graph>
Both programs take one matching per Aut(B)-orbit but not the same representative, so every configuration is
brought to a canonical form under Aut(B):  (tau, A_p, H = A[X_2], {A_z0, sigma A_z0}) with the X_2 vertices named
by the index of their deficient pair U.  Multisets of canonical forms are compared.
Layout of the other implementation, deduced from the data and asserted below: 0..8 x_i, 9..17 y_i, 18 p,
19 + a = the X_2 vertex whose U is deficient pair number a, 37 and 38 = z0, sigma z0.
"""
import sys, json, glob, os
from collections import Counter
from vcommon import *

g = int(sys.argv[1])
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
aut = automorphisms(B)
pidx = {U: k for k, U in enumerate(D)}
gact = [[pidx[tuple(sorted((pm[D[a][0]], pm[D[a][1]])))] for a in range(18)] for pm in aut]


def canon(taupairs, Ap, H, Az):
    """taupairs: set of frozenset({a,c}); Ap: set of a; H: set of frozenset({a,b}); Az: set of a."""
    partner = {}
    for pr in taupairs:
        a, c = tuple(pr)
        partner[a] = c; partner[c] = a
    best = None
    for ga in gact:
        t = tuple(sorted(tuple(sorted((ga[a], ga[c]))) for a, c in map(tuple, taupairs)))
        ap = tuple(sorted(ga[a] for a in Ap))
        h = tuple(sorted(tuple(sorted((ga[a], ga[b]))) for a, b in map(tuple, H)))
        z1 = tuple(sorted(ga[a] for a in Az))
        z2 = tuple(sorted(ga[partner[a]] for a in Az))
        key = (t, ap, h, min(z1, z2))
        if best is None or key < best:
            best = key
    return best


# ---- mine
mine = Counter()
nm = 0
for fn in sorted(glob.glob('v2_surv_%d_m2_*of*.json' % g)):
    for s in json.load(open(fn))['survivors']:
        tau = REPS[s['tau']]
        tp = {frozenset(r) for r in tau}
        Ap = set()
        H = set()
        for f in s['F']:
            Ap |= set(tau[f]); H.add(frozenset(tau[f]))
        Az = set()
        for k, f in enumerate(s['rest']):
            Az.add(tau[f][0] if s['sides'][k] == 0 else tau[f][1])
        for fa, fb, o in s['H']:
            a0, a1 = tau[fa]; b0, b1 = tau[fb]
            if o & 1:
                H.add(frozenset((a0, b0))); H.add(frozenset((a1, b1)))
            if o & 2:
                H.add(frozenset((a0, b1))); H.add(frozenset((a1, b0)))
        mine[canon(tp, Ap, H, Az)] += 1
        nm += 1

# ---- theirs
theirs = Counter()
nt = 0
TD = os.path.join('..', 't18')
files = [f for f in sorted(glob.glob(os.path.join(TD, 'r2_hfirst_%d_*.json' % g))) if 'nopsd' not in f and 'of200' not in f]
for fn in files:
    j = json.load(open(fn))
    for s in j['survivors']:
        tau = s['tau']; rows = s['rows']
        assert len(rows) == 39 and all(tau[tau[a]] == a and tau[a] != a for a in range(18))
        adj = lambda u, v: rows[u] >> v & 1
        assert all(adj(u, v) == adj(v, u) for u in range(39) for v in range(39))
        # layout assertions
        for i in range(9):
            for j2 in range(9):
                assert adj(i, 9 + j2) == B[i, j2] and adj(i, j2) == 0 and adj(9 + i, 9 + j2) == 0
        for a in range(18):
            U, V = D[a], D[tau[a]]
            assert [i for i in range(9) if adj(19 + a, i)] == list(U)
            assert [i for i in range(9) if adj(19 + a, 9 + i)] == list(V)
        for v in (18, 37, 38):
            assert not any(adj(v, u) for u in range(18))
        assert adj(18, 37) and adj(18, 38) and adj(37, 38)
        Ap = {a for a in range(18) if adj(18, 19 + a)}
        assert len(Ap) == 6 and all(tau[a] in Ap for a in Ap)
        Az = {a for a in range(18) if adj(37, 19 + a)}
        Az2 = {a for a in range(18) if adj(38, 19 + a)}
        assert len(Az) == 6 and Az2 == {tau[a] for a in Az} and not (Az & Az2) and not (Az & Ap)
        tp = {frozenset((a, tau[a])) for a in range(18)}
        H = {frozenset((a, b)) for a in range(18) for b in range(a + 1, 18) if adj(19 + a, 19 + b)}
        theirs[canon(tp, Ap, H, Az)] += 1
        nt += 1
print('graph B%d: mine %d configurations (%d canonical forms), first implementation %d (%d canonical forms), files %s'
      % (g, nm, len(mine), nt, len(theirs), [os.path.basename(f) for f in files]))
print('  multisets identical:', mine == theirs)
if mine != theirs:
    only_m = mine - theirs; only_t = theirs - mine
    print('  only mine: %d, only theirs: %d' % (sum(only_m.values()), sum(only_t.values())))
    for k in list(only_m)[:2]: print('   mine only:', k)
    for k in list(only_t)[:2]: print('   theirs only:', k)
