"""Post-analysis of the 39-vertex survivors: degrees in H, t = e(X_2), counting condition (*) of A8.
usage: python v2_analyse.py <graph>"""
import sys, json, glob, itertools as it
from collections import Counter
g = int(sys.argv[1])
S = []
for fn in sorted(glob.glob('v2_surv_%d_m1_*of*.json' % g)):
    if 'nopsd' in fn: continue
    S += json.load(open(fn))['survivors']
def info(s):
    pos = {f: k for k, f in enumerate(s['rest'])}
    deg = [0] * 12
    e = 0
    for fa, fb, o in s['H']:
        for bit in (1, 2):
            if o & bit:
                e += 2
                for k in (pos[fa], pos[fb]):
                    deg[2 * k] += 1; deg[2 * k + 1] += 1
    t = 3 + e
    sx2 = sum(d * (d - 1) for d in deg)
    y = t - 3
    mn = min(sum(v * v for v in c) for c in it.product(range(y + 1), repeat=3) if sum(c) == y)
    return max(deg), t, sx2 + 2 * mn
rows = [info(s) for s in S]
print('graph B%d: survivors on 39 vertices (budgets + PSD on Y1 only): %d' % (g, len(S)))
print('  distribution of (max deg_H on X_2 minus A_p, t):', sorted(Counter((r[0], r[1]) for r in rows).items()))
a = [s for s, r in zip(S, rows) if r[0] <= 4]
b = [s for s, r in zip(S, rows) if r[0] <= 4 and r[2] <= 24]
c = [s for s, r in zip(S, rows) if r[0] <= 4 and r[2] <= 24 and s['nW']]
d = [s for s, r in zip(S, rows) if s['nW']]
for name, L in (('deg_H <= 4', a), ('deg_H <= 4 and (*) [sum_X2 a(a-1) + 2 min sum y^2 <= 24]', b),
                ('the same and a W-type solution exists', c), ('W-type solution exists (no counting filter)', d)):
    print('  %s: %d, in %d matchings, %d pairs (tau,F)' % (name, len(L), len({s['tau'] for s in L}),
          len({(s['tau'], tuple(s['F'])) for s in L})))
print('  number of distinct (tau,F,H) [A_z0 forgotten]:', len({(s['tau'], tuple(s['F']), tuple(map(tuple, s['H']))) for s in S}))
