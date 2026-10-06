"""The configurations on 51 vertices that survive budgets + exact PSD of M1 = 9(3I-A)+J ALONE (mode 1).
For each: rebuild the 51-vertex graph from scratch, re-check symmetry, sigma-invariance, the support graph, all
budgets, exact PSD of M1 (characteristic polynomial), then test M2 = 11(4I+A)-2J exactly and print an integer
vector x with x^T M2 x < 0.  Also reports the smallest determined subset among Y1 (39), Y (45), Y1 u W (45), Y u W (51)
on which M2 already fails.
usage: python v6_m1_final.py <graph>      (reads v2_surv_<g>_m1_*.json and v3_out_<g>_m1_*.json)
"""
import sys, json, glob, os
os.environ['T18_MATS'] = '1'
import numpy as np
from vcommon import *

g = int(sys.argv[1])
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
SA = support_adj(B)
SURV = []
for fn in sorted(glob.glob('v2_surv_%d_m1_*of*.json' % g)):
    SURV += json.load(open(fn))['survivors']
SURV.sort(key=lambda s: (s['tau'], s['F'], s['sides'], s['H']))
FIN = []
for fn in sorted(glob.glob('v3_out_%d_m1_*of*.json' % g)):
    if 'norowpsd' in fn:
        continue
    j = json.load(open(fn))
    assert j['n_surv_input'] == len(SURV)
    FIN += j['final']


def sig(v):
    if v < 9: return v + 9
    if v < 18: return v - 9
    if v == 18: return 18
    if v in (19, 20): return 39 - v
    return v + 1 if v % 2 == 1 else v - 1


def graph51(s, x0, w):
    tau = REPS[s['tau']]
    A = np.zeros((51, 51), dtype=np.int64)
    E = lambda a, b: A.__setitem__((a, b), 1) or A.__setitem__((b, a), 1)
    for i in range(9):
        for j in range(9):
            if B[i, j]: E(i, 9 + j)
    E(18, 19); E(18, 20); E(19, 20)
    orb = [(21 + 2 * k, tau[f]) for k, f in enumerate(s['F'])] + [(27 + 2 * k, tau[f]) for k, f in enumerate(s['rest'])]
    for v, (a, c) in orb:
        for u in D[a]: E(v, u); E(v + 1, 9 + u)
        for u in D[c]: E(v, 9 + u); E(v + 1, u)
    for k in range(3):
        E(21 + 2 * k, 22 + 2 * k); E(18, 21 + 2 * k); E(18, 22 + 2 * k)
    for k in range(6):
        side = s['sides'][k]
        E(19 + side, 27 + 2 * k); E(20 - side, 28 + 2 * k)
    pos = {f: k for k, f in enumerate(s['rest'])}
    for fa, fb, o in s['H']:
        ia, ib = 27 + 2 * pos[fa], 27 + 2 * pos[fb]
        if o & 1: E(ia, ib); E(ia + 1, ib + 1)
        if o & 2: E(ia, ib + 1); E(ia + 1, ib)
    for k, nb in enumerate(x0):
        for v in nb: E(39 + k, v)
    for k, (i, j, s0, s1) in enumerate(w):
        a, b = 45 + 2 * k, 46 + 2 * k
        for v in (18, i, 9 + j, s0, s1, b): E(a, v)
        for v in (18, j, 9 + i, sig(s0), sig(s1)): E(b, v)
    return A


def sig51(v):
    if v < 39: return sig(v)
    return v + 1 if v % 2 == 1 else v - 1


def neg_vector(M):
    w, V = np.linalg.eigh(M.astype(np.float64))
    v = V[:, 0] / np.abs(V[:, 0]).max()
    for k in (3, 6, 12, 30, 100, 1000, 20000):
        x = [int(t) for t in np.rint(v * k)]
        q = sum(x[a] * int(M[a, b]) * x[b] for a in range(len(x)) for b in range(len(x)))
        if q < 0:
            return x, q
    return None, None


print('graph B%d: %d configurations on 51 vertices pass budgets + exact PSD of M1 alone' % (g, len(FIN)))
SETS = {'Y1 (39)': list(range(39)), 'Y (45)': list(range(45)), 'Y1 u W (45)': list(range(39)) + list(range(45, 51)),
        'Y u W (51)': list(range(51))}
for n, f in enumerate(FIN):
    s = SURV[f['surv']]
    A = graph51(s, f['x0'], [tuple(t) for t in f['w']])
    assert (A == A.T).all() and not A.diagonal().any()
    P = [sig51(v) for v in range(51)]
    assert (A[np.ix_(P, P)] == A).all(), 'not sigma-invariant'
    assert (A[:18, :18] == SA).all()
    assert budgets_ok(A)
    m1 = exact_psd_charpoly(gram(A))
    res = {}
    for name, idx in SETS.items():
        res[name] = exact_psd_charpoly(gram2(A[np.ix_(idx, idx)]))
    x, q = neg_vector(gram2(A))
    deg = A.sum(axis=1)
    print(' #%d matching %d F=%s t=%d: budgets ok, sigma-invariant, M1 exactly PSD: %s (rank deficiency allowed); '
          'M2 exactly PSD on %s' % (n, s['tau'], s['F'], int(A[21:39, 21:39].sum()) // 2, m1, res))
    print('    integer vector with x^T M2 x = %s on the 51 vertices: %s' % (q, x))
    print('    degrees inside the 51 vertices: min %d max %d' % (deg.min(), deg.max()))
json.dump([{'tau_pairs': REPS[SURV[f['surv']]['tau']], 'config39': SURV[f['surv']], 'x0': f['x0'], 'w': f['w'],
            'rows51': [int(sum(int(A_) << k for k, A_ in enumerate(row))) for row in
                       graph51(SURV[f['surv']], f['x0'], [tuple(t) for t in f['w']])]} for f in FIN],
          open('v6_m1_final_%d.json' % g, 'w'))
