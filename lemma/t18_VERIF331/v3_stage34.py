"""Stages 3 and 4 (independent), in BOTH orders.
usage: python v3_stage34.py <graph> <part> <nparts>
Input: v2_surv_<g>_*.json (survivors on Y1, 39 vertices).
For every survivor:
  X  = all ways to add X_0' (three orbits {q, sigma q}; rows C, graph G') -> Y  = S u X_0 u X_2 (45 vertices)
  Wd = all ways to add W = N(p) n X_1 (three mate pairs; types and X_2-neighbours) -> Y1 u W (45 vertices)
  final = pairs (X, Wd) on Y u W (51 vertices; no edge between X_0' and W).
Each list is filtered by budgets + exact PSD on its own determined set, so
  |X| is the count to compare with "Y-tables passing budgets and PSD" (path A of the first implementation),
  |Wd| is the same thing in the dual order (path B, not in the first implementation),
  final must be empty.
Forced facts used (A8, A10; re-derived by hand in REPORT.md):
  q in X_0': no neighbour in S u {p, z0, sigma z0}; q not~ sigma q; exactly 2 neighbours in A_p; a(q) >= 4;
             deg_{G'}(q) = a(q) - 4;  s in A_p has exactly 2 neighbours in X_0'; s in X_2 \\ A_p has deg_H(s) + 1.
  w in W: neighbours p, sigma w, one x_i, one y_j (i != j), exactly two vertices of X_2 \\ A_p, nothing else in Y;
          every vertex of X_2 \\ A_p has exactly one neighbour in W; a vertex of type (i;j) exists iff m_ij >= 1.
Layout: 0..8 x, 9..17 y, 18 p, 19 z0, 20 sz0, 21..26 A_p, 27..38 X_2 \\ A_p (orbit k = 27+2k, 28+2k).
"""
import sys, json, glob, itertools as it, time
import numpy as np
from vcommon import *

g = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3])
T0 = time.time()
import os
ROWPSD = int(os.environ.get('T18_ROWPSD', '1'))   # 0: no PSD test on the single rows of C (budgets only), to compare raw counts
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
SA = support_adj(B)
SURV = []
for fn in sorted(glob.glob('v2_surv_%d_m%d_*of*.json' % (g, MODE))):
    if 'nopsd' in fn:
        continue
    SURV += json.load(open(fn))['survivors']
SURV.sort(key=lambda s: (s['tau'], s['F'], s['sides'], s['H']))
CNT = dict(configs=0, deg_gt4=0, rows=0, rows_psd=0, C_colsum=0, C_colsum_star=0, CG=0, CG_star=0, CG_budget=0,
           CG_budget_star=0, CG_psd=0, CG_psd_star=0,
           wcand=0, wcand_ok=0, wtriples=0, w_budget=0, w_psd=0, final_pairs=0, final_budget=0, final_psd=0)


def sig(v):
    if v < 9: return v + 9
    if v < 18: return v - 9
    if v == 18: return 18
    if v in (19, 20): return 39 - v
    return v + 1 if v % 2 == 1 else v - 1


def srow(U, V):
    r = np.zeros(18, dtype=np.int64)
    for u in U: r[u] = 1
    for v in V: r[9 + v] = 1
    return r


def build39(s):
    tau = REPS[s['tau']]
    A = np.zeros((39, 39), dtype=np.int64)
    A[:18, :18] = SA
    A[18, 19] = A[18, 20] = A[19, 20] = 1
    for k, f in enumerate(s['F']):
        a, c = tau[f]
        i, j = 21 + 2 * k, 22 + 2 * k
        A[i, :18] = srow(D[a], D[c]); A[j, :18] = srow(D[c], D[a])
        A[i, j] = 1; A[18, i] = A[18, j] = 1
    for k, f in enumerate(s['rest']):
        a, c = tau[f]
        i, j = 27 + 2 * k, 28 + 2 * k
        A[i, :18] = srow(D[a], D[c]); A[j, :18] = srow(D[c], D[a])
        side = s['sides'][k]
        A[19 + side, i] = 1; A[20 - side, j] = 1
    pos = {f: k for k, f in enumerate(s['rest'])}
    for (fa, fb, opt) in s['H']:
        ka, kb = pos[fa], pos[fb]
        assert ka < kb
        ia, ib = 27 + 2 * ka, 27 + 2 * kb
        if opt & 1:
            A[ia, ib] = 1; A[ia + 1, ib + 1] = 1
        if opt & 2:
            A[ia, ib + 1] = 1; A[ia + 1, ib] = 1
    A = np.maximum(A, A.T)
    # sanity: sigma-invariance
    P = [sig(v) for v in range(39)]
    assert (A[np.ix_(P, P)] == A).all()
    return A, tau


def extend(A, newrows):
    """newrows: list of neighbour lists (indices in the growing matrix, may refer to earlier new vertices)."""
    n = len(A); k = len(newrows)
    N = np.zeros((n + k, n + k), dtype=np.int64)
    N[:n, :n] = A
    for t, nb in enumerate(newrows):
        for v in nb:
            N[n + t, v] = N[v, n + t] = 1
    return N


def x0_part(A39):
    """all (rows, G') for X_0' : returns list of lists of 6 neighbour lists (q1, sq1, q2, sq2, q3, sq3),
    indices relative to a matrix whose first 39 vertices are Y1 and whose next 6 are these."""
    degH = A39[21:39, 21:39].sum(axis=1)
    if degH.max() > 4:
        CNT['deg_gt4'] += 1      # a <= 4 on X_2 (A8): no completion
        return []
    dem = {}
    for v in range(21, 27): dem[v] = 2
    for v in range(27, 39): dem[v] = int(degH[v - 21]) + 1
    X2 = list(range(21, 39))
    rows = set()

    def ok(R):
        return budgets_ok(extend(A39, [list(R), [sig(v) for v in R]]))

    def rec(pos, R):
        # R is budget-feasible as a partial row
        nap = sum(1 for v in R if v < 27)
        if nap == 2 and len(R) >= 4:
            m1 = tuple(sorted(R)); m2 = tuple(sorted(sig(v) for v in R))
            rows.add(min(m1, m2))
        for t in range(pos, 18):
            v = X2[t]
            if v < 27 and nap == 2:
                continue
            if sig(v) in R and dem[v] < 2:
                continue
            R2 = R + [v]
            if ok(R2):
                rec(t + 1, R2)
    rec(0, [])
    rows = sorted(rows)
    CNT['rows'] += len(rows)
    good = []
    for R in rows:
        if not ROWPSD or psd_ok(extend(A39, [list(R), [sig(v) for v in R]])):
            good.append(R)
    CNT['rows_psd'] += len(good)

    def contrib(R):
        c = [0] * 18
        for v in R:
            c[v - 21] += 1; c[sig(v) - 21] += 1
        return tuple(c)
    con = [contrib(R) for R in good]
    demv = tuple(dem[v] for v in X2)
    byc = {}
    for k, c in enumerate(con):
        byc.setdefault(c, []).append(k)
    res = []
    n = len(good)
    for a in range(n):
        for b in range(a + 1, n):
            need = tuple(demv[t] - con[a][t] - con[b][t] for t in range(18))
            if min(need) < 0:
                continue
            for c in byc.get(need, ()):
                if c <= b:
                    continue
                CNT['C_colsum'] += 1
                tri = (good[a], good[b], good[c])
                deg = [len(R) - 4 for R in tri]
                # counting identity (*) of A8 with p, z0, sigma z0 contributing 12:
                #   sum_{X_2} a(a-1) + sum_{X_0'} (a-4)^2 <= 24   (recorded, not used to prune)
                star = int((degH * (degH - 1)).sum()) + 2 * sum(d * d for d in deg) <= 24
                CNT['C_colsum_star'] += star
                for o01, o02, o12 in it.product(range(4), repeat=3):
                    pc = lambda o: (o & 1) + (o >> 1)
                    if pc(o01) + pc(o02) != deg[0] or pc(o01) + pc(o12) != deg[1] or pc(o02) + pc(o12) != deg[2]:
                        continue
                    CNT['CG'] += 1
                    CNT['CG_star'] += star
                    nb = []
                    for R in tri:
                        nb.append(list(R)); nb.append([sig(v) for v in R])
                    for (ka, kb, o) in ((0, 1, o01), (0, 2, o02), (1, 2, o12)):
                        ia, ib = 39 + 2 * ka, 39 + 2 * kb
                        if o & 1:
                            nb[2 * kb].append(ia); nb[2 * kb + 1].append(ia + 1)
                        if o & 2:
                            nb[2 * kb].append(ia + 1); nb[2 * kb + 1].append(ia)
                    N = extend(A39, nb)
                    if not budgets_ok(N):
                        continue
                    CNT['CG_budget'] += 1
                    CNT['CG_budget_star'] += star
                    if not psd_ok(N, exact=True):
                        continue
                    CNT['CG_psd'] += 1
                    CNT['CG_psd_star'] += star
                    res.append(nb)
    return res


def w_part(A39, s, tau):
    """all ways to add W: list of lists of 6 neighbour lists (w1, sw1, w2, sw2, w3, sw3), indices < 39 or
    'M' for the mate (resolved by the caller through an offset)."""
    c = np.zeros((9, 9), dtype=np.int64)
    for a, b in tau:
        for u in D[a]:
            for v in D[b]:
                c[u, v] += 1; c[v, u] += 1
    m = 2 - B - c
    assert m.min() >= 0
    cover = [0] * 9
    for f in s['F']:
        a, b = tau[f]
        for u in D[a] + D[b]:
            cover[u] += 1
    r = [2 - x for x in cover]
    if min(r) < 0:
        return []
    cands = {}
    for i in range(9):
        for j in range(9):
            if i == j or not r[i] or not r[j] or m[i, j] < 1:
                continue
            for sa, sb in it.combinations(range(27, 39), 2):
                if sb == sig(sa):
                    continue
                key1 = (i, j, sa, sb)
                key2 = (j, i) + tuple(sorted((sig(sa), sig(sb))))
                key = min(key1, key2)
                if key in cands:
                    continue
                CNT['wcand'] += 1
                i0, j0, s0, s1 = key
                # w = 39, sw = 40
                nb = [[18, i0, 9 + j0, s0, s1], [18, j0, 9 + i0, sig(s0), sig(s1), 39]]
                N = extend(A39, nb)
                cands[key] = budgets_ok(N) and psd_ok(N)
    good = sorted(k for k, v in cands.items() if v)
    CNT['wcand_ok'] += len(good)
    res = []
    # the three W-orbits split the six orbits of X_2 \ A_p into three pairs of orbits
    by = {}
    for key in good:
        ko = tuple(sorted(((key[2] - 27) // 2, (key[3] - 27) // 2)))
        by.setdefault(ko, []).append(key)
    seen = set()

    def splits(rem):
        if not rem:
            yield []
            return
        a = rem[0]
        for b in rem[1:]:
            rest = [x for x in rem if x not in (a, b)]
            for sp in splits(rest):
                yield [(a, b)] + sp
    for sp in splits(list(range(6))):
        for tr in it.product(*[by.get(ko, []) for ko in sp]):
            cc = [0] * 9
            used = set()
            for (i, j, s0, s1) in tr:
                used |= {s0, s1, sig(s0), sig(s1)}
                cc[i] += 1; cc[j] += 1
            if len(used) != 12 or cc != r:
                continue
            tr = tuple(sorted(tr))
            assert tr not in seen
            seen.add(tr)
            CNT['wtriples'] += 1
            res.append(tr)
    return res


def w_rows(tr, off):
    nb = []
    for k, (i, j, s0, s1) in enumerate(tr):
        nb.append([18, i, 9 + j, s0, s1])
        nb.append([18, j, 9 + i, sig(s0), sig(s1), off + 2 * k])
    return nb


out_x, out_w, out_final = [], [], []
done = 0
for si in range(part, len(SURV), nparts):
    s = SURV[si]
    A39, tau = build39(s)
    assert budgets_ok(A39)
    CNT['configs'] += 1
    X = x0_part(A39)
    Wt = w_part(A39, s, tau)
    Wd = []
    for tr in Wt:
        N = extend(A39, w_rows(tr, 39))
        if not budgets_ok(N):
            continue
        CNT['w_budget'] += 1
        if not psd_ok(N, exact=True):
            continue
        CNT['w_psd'] += 1
        Wd.append(tr)
    for nb in X:
        out_x.append({'surv': si, 'x0': nb})
    for tr in Wd:
        out_w.append({'surv': si, 'w': tr})
    for nb in X:
        for tr in Wd:
            CNT['final_pairs'] += 1
            N = extend(A39, nb + w_rows(tr, 45))
            if not budgets_ok(N):
                continue
            CNT['final_budget'] += 1
            if not psd_ok(N, exact=True):
                continue
            CNT['final_psd'] += 1
            out_final.append({'surv': si, 'x0': nb, 'w': tr})
    done += 1
    if time.time() - T0 > 520:
        print('TIME LIMIT after survivor index', si)
        break
tag = '%d_m%d_%dof%d%s' % (g, MODE, part, nparts, '' if ROWPSD else '_norowpsd')
json.dump({'graph': g, 'n_surv_input': len(SURV), 'done': done, 'counts': CNT, 'stat': STAT,
           'Y_tables': out_x, 'W_tables': out_w, 'final': out_final, 'seconds': time.time() - T0},
          open('v3_out_%s.json' % tag, 'w'))
print('PSD matrices used: %d ; PSD on single rows of C: %d' % (MODE, ROWPSD))
print('graph B%d part %d/%d: survivors input %d, processed %d' % (g, part, nparts, len(SURV), done))
print(CNT)
print('Y-tables (45 vertices, X_0 added) passing budgets + exact PSD: %d, in %d configurations, %d matchings' % (
    len(out_x), len({o['surv'] for o in out_x}), len({SURV[o['surv']]['tau'] for o in out_x})))
print('dual order: Y1 u W (45 vertices) passing budgets + exact PSD: %d, in %d configurations' % (
    len(out_w), len({o['surv'] for o in out_w})))
print('FINAL on 51 vertices: %d' % len(out_final))
print(STAT, 'seconds %.1f' % (time.time() - T0))
