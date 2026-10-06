"""Stage 2 (independent): (tau, F, A_{z0}, H) on Y1 = S u {p, z0, sigma z0} u X_2 (39 vertices).
usage: python v2_stage2.py <graph> <part> <nparts> [nopsd]
Order of choices (different from the first implementation, which completes H and then chooses A_{z0}):
  tau (one per Aut(B)-orbit) -> F (3 rectangles inside N(p)) -> W-type solutions must exist ->
  the 6 other orbits of X_2 are added ONE ORBIT AT A TIME, each with its side (which of its two vertices
  is adjacent to z0) and its H-edges to the orbits already placed; budgets + PSD on the current determined set.
Vertex layout: 0..8 x_i, 9..17 y_i, 18 p, 19 z0, 20 sigma z0, 21..26 A_p (3 mate pairs), 27.. the other orbits.
Normalisation: tau = orbit representative; F and H not reduced; A_{z0} up to the swap z0 <-> sigma z0
(the first outside orbit has its first vertex in A_{z0}).
"""
import sys, json, itertools as it, time
import numpy as np
from vcommon import *

g = int(sys.argv[1]); part = int(sys.argv[2]); nparts = int(sys.argv[3])
NOPSD = len(sys.argv) > 4 and sys.argv[4] == 'nopsd'
T0 = time.time()
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
SA = support_adj(B)
CNT = dict(tauF_budget25=0, tauF_psd25=0, tauF_W=0, tauF_single=0, tauF_pair=0, nodes=0, bud_rej=0, psd_rej=0,
           leaves=0, surv=0, wsol_total=0)


def test(A, exact=False):
    if not budgets_ok(A):
        CNT['bud_rej'] += 1
        return False
    if NOPSD:
        return True
    if not psd_ok(A, exact):
        CNT['psd_rej'] += 1
        return False
    return True


def srow(U, V):
    r = np.zeros(18, dtype=np.int64)
    for u in U: r[u] = 1
    for v in V: r[9 + v] = 1
    return r


def base(tau, F):
    """27 vertices: S, p, z0, sz0, A_p."""
    A = np.zeros((27, 27), dtype=np.int64)
    A[:18, :18] = SA
    A[18, 19] = A[19, 18] = A[18, 20] = A[20, 18] = A[19, 20] = A[20, 19] = 1
    for k, f in enumerate(F):
        a, c = tau[f]
        i, j = 21 + 2 * k, 22 + 2 * k
        A[i, :18] = srow(D[a], D[c]); A[j, :18] = srow(D[c], D[a])
        A[:18, i] = A[i, :18]; A[:18, j] = A[j, :18]
        A[i, j] = A[j, i] = 1
        A[i, 18] = A[18, i] = A[j, 18] = A[18, j] = 1
    return A


def add_orbit(A, rect, side, links):
    """links: list of (index of first vertex of an earlier orbit, opt); opt bit0 straight, bit1 cross."""
    n = len(A)
    N = np.zeros((n + 2, n + 2), dtype=np.int64)
    N[:n, :n] = A
    a, c = rect
    N[n, :18] = srow(D[a], D[c]); N[n + 1, :18] = srow(D[c], D[a])
    N[n, 19 + side] = 1; N[n + 1, 20 - side] = 1
    for (m, opt) in links:
        if opt & 1:
            N[n, m] = 1; N[n + 1, m + 1] = 1
        if opt & 2:
            N[n, m + 1] = 1; N[n + 1, m] = 1
    N[:n, n] = N[n, :n]; N[:n, n + 1] = N[n + 1, :n]
    return N


def cell_counts(tau):
    c = np.zeros((9, 9), dtype=np.int64)
    for a, b in tau:
        for u in D[a]:
            for v in D[b]:
                c[u, v] += 1; c[v, u] += 1
    return c


def w_solutions(tau, F, A25):
    """all sets of three unordered types {i,j} for the three mate pairs of N(p) n X_1.
    Necessary: x_i has exactly two neighbours in N(p); a vertex of type (i;j) must exist (m_ij >= 1);
    budgets on S u {p} u A_p u W (31 vertices)."""
    m = 2 - B - cell_counts(tau)
    cover = [0] * 9
    for f in F:
        a, c = tau[f]
        for u in D[a] + D[c]:
            cover[u] += 1
    r = [2 - x for x in cover]
    if min(r) < 0:
        return []
    assert sum(r) == 6
    sols = []
    cand = [(i, j) for i in range(9) for j in range(i + 1, 9) if r[i] and r[j] and m[i, j] >= 1]
    for tr in it.combinations(cand, 3):
        cc = [0] * 9
        for i, j in tr:
            cc[i] += 1; cc[j] += 1
        if cc != r:
            continue
        A = np.zeros((31, 31), dtype=np.int64)
        A[:25, :25] = A25
        for k, (i, j) in enumerate(tr):
            a, b = 25 + 2 * k, 26 + 2 * k
            A[a, i] = A[a, 9 + j] = 1; A[b, j] = A[b, 9 + i] = 1
            A[a, 18] = A[b, 18] = 1
            A[a, b] = 1
        A = np.maximum(A, A.T)
        if budgets_ok(A):
            sols.append(tr)
    return sols


def run_tauF(ti, tau, F, out):
    A27 = base(tau, F)
    # S u {p} u A_p : indices 0..18 and 21..26
    idx25 = list(range(19)) + list(range(21, 27))
    A25 = A27[np.ix_(idx25, idx25)]
    if not budgets_ok(A25):
        return
    CNT['tauF_budget25'] += 1
    ws = w_solutions(tau, F, A25)
    # the W-type test is recorded with each survivor (field nW) but NOT used to prune here,
    # so that the 39-vertex survivor set is defined by budgets + PSD on Y1 alone.
    if ws:
        CNT['tauF_W'] += 1
        CNT['wsol_total'] += len(ws)
    if not test(A27):
        return
    CNT['tauF_psd25'] += 1
    rest = [k for k in range(9) if k not in F]
    rects = [tau[k] for k in rest]
    # single-orbit tests (side irrelevant by the swap z0 <-> sigma z0)
    for r in rects:
        if not test(add_orbit(A27, r, 0, [])):
            return
    CNT['tauF_single'] += 1
    # pair tables: T[(k,l)][rel side][opt]
    T = {}
    for k in range(6):
        for l in range(k + 1, 6):
            Ak = add_orbit(A27, rects[k], 0, [])
            tab = [[False] * 4 for _ in range(2)]
            anyok = False
            for rel in range(2):
                for opt in range(4):
                    ok = test(add_orbit(Ak, rects[l], rel, [(27, opt)]))
                    tab[rel][opt] = ok
                    anyok |= ok
            if not anyok:
                return
            T[(k, l)] = tab
    CNT['tauF_pair'] += 1
    sides = [0] * 6
    opts = {}

    def rec(k, A):
        CNT['nodes'] += 1
        if k == 6:
            CNT['leaves'] += 1
            if NOPSD or psd_ok(A, exact=True):
                CNT['surv'] += 1
                H = sorted((rest[a], rest[b], opts[(a, b)]) for (a, b) in opts if opts[(a, b)])
                out.append({'tau': ti, 'F': list(F), 'rest': rest, 'sides': list(sides), 'H': H, 'nW': len(ws)})
            else:
                CNT['psd_rej'] += 1
            return
        for side in ((0,) if k == 0 else (0, 1)):
            doms = [[o for o in range(4) if T[(l, k)][sides[l] ^ side][o]] for l in range(k)]
            if any(not d for d in doms):
                continue
            sides[k] = side
            for combo in it.product(*doms):
                N = add_orbit(A, rects[k], side, [(27 + 2 * l, combo[l]) for l in range(k)])
                if not test(N):
                    continue
                for l in range(k):
                    opts[(l, k)] = combo[l]
                rec(k + 1, N)
            for l in range(k):
                opts.pop((l, k), None)
    rec(0, A27)


out = []
done = []
for ti in range(part, len(REPS), nparts):
    tau = REPS[ti]
    for F in it.combinations(range(9), 3):
        if any(set(D[tau[f][0]]) & set(D[tau[f][1]]) for f in F):
            continue
        run_tauF(ti, tau, F, out)
    done.append(ti)
    if time.time() - T0 > 520:
        print('TIME LIMIT: stopped after matching index', ti)
        break
tag = '%d_m%d_%dof%d%s' % (g, MODE, part, nparts, '_nopsd' if NOPSD else '')
json.dump({'graph': g, 'part': part, 'nparts': nparts, 'done': done, 'n_reps': len(REPS), 'counts': CNT,
           'stat': STAT, 'survivors': out, 'seconds': time.time() - T0}, open('v2_surv_%s.json' % tag, 'w'))
print('PSD matrices used: %d' % MODE)
print('graph B%d part %d/%d: matchings done %d (of %d in this part)' % (g, part, nparts, len(done), len(range(part, len(REPS), nparts))))
print(CNT)
print('survivors on 39 vertices: %d, in %d matchings, %d pairs (tau,F)' % (
    len(out), len({s['tau'] for s in out}), len({(s['tau'], tuple(s['F'])) for s in out})))
ow = [s for s in out if s['nW']]
print('  of which with at least one W-type solution: %d, in %d matchings, %d pairs (tau,F)' % (
    len(ow), len({s['tau'] for s in ow}), len({(s['tau'], tuple(s['F'])) for s in ow})))
print(STAT, 'seconds %.1f' % (time.time() - T0))
