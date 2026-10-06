"""Step 4 in the order of the first implementation, without any PSD pre-filter on W:
for every Y-table (45 vertices) that passed budgets + exact PSD (mode 2: v3_out_<g>_m2_*_norowpsd.json), enumerate ALL
ways to add W = N(p) n X_1 (three mate pairs: types and X_2-neighbours), keep the graphs on 51 vertices that satisfy
every common-neighbour budget, then decide PSD exactly (M1, and M2).
W-orbit candidates are filtered by BUDGETS ONLY on Y u {w, sigma w} (47 vertices); a 51-vertex graph satisfying the
budgets restricts to three such candidates, so nothing is lost.
usage: python v7_step4_direct.py <graph>
"""
import sys, json, glob, itertools as it, time, os
os.environ['T18_MATS'] = '2'
import numpy as np
from collections import Counter
from vcommon import *

g = int(sys.argv[1])
T0 = time.time()
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
SA = support_adj(B)
SURV = []
for fn in sorted(glob.glob('v2_surv_%d_m2_*of*.json' % g)):
    SURV += json.load(open(fn))['survivors']
SURV.sort(key=lambda s: (s['tau'], s['F'], s['sides'], s['H']))
TAB = []
for fn in sorted(glob.glob('v3_out_%d_m2_*of2_norowpsd.json' % g)):
    j = json.load(open(fn))
    assert j['n_surv_input'] == len(SURV) and j['done'] == len(range(int(fn.split('_m2_')[1][0]), len(SURV), 2))
    TAB += j['Y_tables']


def sig(v):
    if v < 9: return v + 9
    if v < 18: return v - 9
    if v == 18: return 18
    if v in (19, 20): return 39 - v
    return v + 1 if v % 2 == 1 else v - 1


def graph45(s, x0):
    tau = REPS[s['tau']]
    A = np.zeros((45, 45), dtype=np.int64)

    def E(a, b):
        A[a, b] = A[b, a] = 1
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
    return A, tau


def add_w(A, tr):
    n = len(A)
    N = np.zeros((n + 2 * len(tr), n + 2 * len(tr)), dtype=np.int64)
    N[:n, :n] = A
    for k, (i, j, s0, s1) in enumerate(tr):
        a, b = n + 2 * k, n + 2 * k + 1
        for v in (18, i, 9 + j, s0, s1, b):
            N[a, v] = N[v, a] = 1
        for v in (18, j, 9 + i, sig(s0), sig(s1)):
            N[b, v] = N[v, b] = 1
    return N


def splits(rem):
    if not rem:
        yield []
        return
    a = rem[0]
    for b in rem[1:]:
        for sp in splits([x for x in rem if x not in (a, b)]):
            yield [(a, b)] + sp


tot = dict(tables=0, cands=0, cands_budget=0, triples=0, budget51=0, psd51=0, type_solutions=0)
per_table = []
for T in TAB:
    s = SURV[T['surv']]
    A, tau = graph45(s, T['x0'])
    assert budgets_ok(A)
    c = np.zeros((9, 9), dtype=np.int64)
    for a, b in tau:
        for u in D[a]:
            for v in D[b]:
                c[u, v] += 1; c[v, u] += 1
    m = 2 - B - c
    cover = [0] * 9
    for f in s['F']:
        a, b = tau[f]
        for u in D[a] + D[b]:
            cover[u] += 1
    r = [2 - x for x in cover]
    assert min(r) >= 0
    good = {}
    seen = set()
    for i in range(9):
        for j in range(9):
            if i == j or not r[i] or not r[j] or m[i, j] < 1:
                continue
            for sa, sb in it.combinations(range(27, 39), 2):
                if sb == sig(sa):
                    continue
                key = min((i, j, sa, sb), (j, i) + tuple(sorted((sig(sa), sig(sb)))))
                if key in seen:
                    continue
                seen.add(key)
                tot['cands'] += 1
                if budgets_ok(add_w(A, [key])):
                    tot['cands_budget'] += 1
                    ko = tuple(sorted(((key[2] - 27) // 2, (key[3] - 27) // 2)))
                    good.setdefault(ko, []).append(key)
    nb51 = 0
    types = set()
    for sp in splits(list(range(6))):
        for tr in it.product(*[good.get(ko, []) for ko in sp]):
            cc = [0] * 9
            used = set()
            for (i, j, s0, s1) in tr:
                used |= {s0, s1, sig(s0), sig(s1)}
                cc[i] += 1; cc[j] += 1
            if len(used) != 12 or cc != r:
                continue
            tot['triples'] += 1
            N = add_w(A, list(tr))
            if not budgets_ok(N):
                continue
            nb51 += 1
            types.add(tuple(sorted(tuple(sorted(t[:2])) for t in tr)))
            if psd_ok(N, exact=True):
                tot['psd51'] += 1
                print('  SURVIVOR on 51 vertices:', T['surv'], tr)
    tot['tables'] += 1
    tot['budget51'] += nb51
    tot['type_solutions'] += len(types)
    per_table.append(nb51)
print('graph B%d: Y-tables %d; W-orbit candidates %d, passing budgets on 47 vertices %d; triples %d; '
      'graphs on 51 vertices passing all budgets %d; of them exactly PSD (M1 and M2) %d'
      % (g, tot['tables'], tot['cands'], tot['cands_budget'], tot['triples'], tot['budget51'], tot['psd51']))
print('  distribution of the number of budget-valid 51-vertex graphs per Y-table:', sorted(Counter(per_table).items()))
print('  type solutions carrying at least one budget-valid graph, summed over tables:', tot['type_solutions'])
print('  PSD decisions:', STAT, ' seconds %.1f' % (time.time() - T0))
