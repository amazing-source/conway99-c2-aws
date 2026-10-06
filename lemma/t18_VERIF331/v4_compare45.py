"""Set comparison on Y = S u X_0 u X_2 (45 vertices): my Y-tables passing budgets + exact PSD
(v3_out_<g>_m2_*_norowpsd.json) against the tables stored by the first implementation
(t18/r2_stage2_<g>_*surv*.json, field "examples"; OUTPUT files only, read after my own counts were produced).
usage: python v4_compare45.py <graph>
Canonical form under Aut(B): X_2 vertices named by the index of their deficient pair; p, z0, sigma z0 as in
v4_compare39; the six vertices of X_0' named by their neighbourhood in X_2 (rows are pairwise distinct).
Format of the other implementation, deduced from the data and asserted: Az[k] = neighbours in X_2 of the k-th
vertex of X_0 (bit a = deficient pair a), k = 0: p, 1: z0, 2: sigma z0, 3..8: X_0'; H[a] = row of A[X_2];
G[k] = row of A[X_0].
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


def canon(partner, Ap, H, Az, rows, gedges):
    """rows: list of 6 frozensets of a; gedges: set of frozenset({row index, row index})."""
    best = None
    for ga in gact:
        t = tuple(sorted({tuple(sorted((ga[a], ga[partner[a]]))) for a in range(18)}))
        ap = tuple(sorted(ga[a] for a in Ap))
        h = tuple(sorted(tuple(sorted((ga[a], ga[b]))) for a, b in map(tuple, H)))
        z1 = tuple(sorted(ga[a] for a in Az))
        z2 = tuple(sorted(ga[partner[a]] for a in Az))
        rr = [tuple(sorted(ga[a] for a in R)) for R in rows]
        assert len(set(rr)) == 6
        ge = tuple(sorted(tuple(sorted((rr[i], rr[j]))) for i, j in map(tuple, gedges)))
        key = (t, ap, h, min(z1, z2), tuple(sorted(rr)), ge)
        if best is None or key < best:
            best = key
    return best


# ---- mine
SURV = []
for fn in sorted(glob.glob('v2_surv_%d_m2_*of*.json' % g)):
    SURV += json.load(open(fn))['survivors']
SURV.sort(key=lambda s: (s['tau'], s['F'], s['sides'], s['H']))
mine = Counter(); nm = 0
for fn in sorted(glob.glob('v3_out_%d_m2_*of2_norowpsd.json' % g)):
    j = json.load(open(fn))
    assert j['n_surv_input'] == len(SURV)
    for T in j['Y_tables']:
        s = SURV[T['surv']]
        tau = REPS[s['tau']]
        partner = {}
        for a, c in tau:
            partner[a] = c; partner[c] = a
        name = {}
        Ap = set(); H = set()
        for k, f in enumerate(s['F']):
            name[21 + 2 * k], name[22 + 2 * k] = tau[f]
            Ap |= set(tau[f]); H.add(frozenset(tau[f]))
        Az = set()
        for k, f in enumerate(s['rest']):
            name[27 + 2 * k], name[28 + 2 * k] = tau[f]
            Az.add(tau[f][0] if s['sides'][k] == 0 else tau[f][1])
        for fa, fb, o in s['H']:
            a0, a1 = tau[fa]; b0, b1 = tau[fb]
            if o & 1:
                H.add(frozenset((a0, b0))); H.add(frozenset((a1, b1)))
            if o & 2:
                H.add(frozenset((a0, b1))); H.add(frozenset((a1, b0)))
        rows = [frozenset(name[v] for v in nb if v < 39) for nb in T['x0']]
        ge = {frozenset((k, v - 39)) for k, nb in enumerate(T['x0']) for v in nb if v >= 39}
        mine[canon(partner, Ap, H, Az, rows, ge)] += 1
        nm += 1

# ---- theirs
TD = os.path.join('..', 't18')
theirs = Counter(); nt = 0; declared = 0
files = sorted(glob.glob(os.path.join(TD, 'r2_stage2_%d_*surv*.json' % g)))
for fn in files:
    j = json.load(open(fn))
    declared += j['totals']['Y_tables_psd']
    for e in j.get('examples', []):
        tau = e['tau']
        partner = {a: tau[a] for a in range(18)}
        bits = lambda m, n: {a for a in range(n) if m >> a & 1}
        Azs = [bits(m, 18) for m in e['Az']]
        Gs = [bits(m, 9) for m in e['G']]
        Ap = Azs[0]
        assert len(Ap) == 6 and all(tau[a] in Ap for a in Ap) and Gs[0] == {1, 2} and Gs[1] == {0, 2} and Gs[2] == {0, 1}
        Az = Azs[1]
        assert Azs[2] == {tau[a] for a in Az} and len(Az) == 6 and not (Az & Ap) and not (Az & Azs[2])
        H = {frozenset((a, b)) for a in range(18) for b in bits(e['H'][a], 18)}
        assert all(len(h) == 2 for h in H)
        rows = [frozenset(Azs[k]) for k in range(3, 9)]
        ge = {frozenset((k - 3, l - 3)) for k in range(3, 9) for l in Gs[k]}
        assert all(len(x) == 2 and min(x) >= 0 for x in ge)
        theirs[canon(partner, Ap, H, Az, rows, ge)] += 1
        nt += 1
print('graph B%d: mine %d Y-tables (%d canonical forms); first implementation: %d stored, %d declared, files %s'
      % (g, nm, len(mine), nt, declared, [os.path.basename(f) for f in files]))
print('  multisets identical:', mine == theirs)
if mine != theirs:
    only_m = mine - theirs; only_t = theirs - mine
    print('  only mine: %d, only theirs: %d' % (sum(only_m.values()), sum(only_t.values())))
