"""Stage 1 (independent): matchings tau of the 18 deficient pairs.
usage: python v1_stage1.py <graph 0|1|2>
Writes v1_tau_<g>.json : deficient pairs, admissible rectangles, one matching per Aut(B)-orbit (lexicographically
smallest image), orbit sizes.
A rectangle {U,V} (U != V deficient pairs) = sigma-orbit {z, sigma z} of X_2, z ~ x_u (u in U), y_v (v in V).
Tests:
  (i)   lambda = 1 on the edges z-x_u, z-y_v : every row and column of B[U,V] has at most one 1;
  (psd) budgets + exact PSD on S u {p, z, sigma z} (21 vertices), in the status "z not adjacent to p";
        also computed in the status "z ~ p ~ sigma z ~ z" (needs U n V empty) to check the inclusion in <= out.
  (iii) cell budgets: number of X_2 vertices adjacent to x_i and y_j is at most 2 - B_ij (they have no common
        neighbour in S).
"""
import sys, json, itertools as it, time
import numpy as np
from vcommon import *

g = int(sys.argv[1])
T0 = time.time()
B = support_graph(g)
D = deficient_pairs(B)
nb = [set(int(j) for j in np.nonzero(B[i])[0]) for i in range(9)]
# every index lies in exactly 4 deficient pairs
assert all(sum(i in U for U in D) == 4 for i in range(9))
SA = support_adj(B)


def test_i(U, V):
    return all(len(nb[u] & set(V)) <= 1 for u in U) and all(len(nb[v] & set(U)) <= 1 for v in V)


def single(U, V, inside):
    names = ['x%d' % i for i in range(9)] + ['y%d' % i for i in range(9)]
    b = Builder(SA, names)
    b.add('p', [])
    b.add('z', ['x%d' % u for u in U] + ['y%d' % v for v in V] + (['p'] if inside else []))
    b.add('sz', ['x%d' % v for v in V] + ['y%d' % u for u in U] + (['p', 'z'] if inside else []))
    return budgets_ok(b.A), (budgets_ok(b.A) and psd_ok(b.A, exact=True))


rect_i, rect_out, rect_in = [], [], []
bud_out_fail = 0
for a, c in it.combinations(range(18), 2):
    U, V = D[a], D[c]
    if not test_i(U, V):
        continue
    rect_i.append((a, c))
    bo, po = single(U, V, False)
    if not bo:
        bud_out_fail += 1
    if po:
        rect_out.append((a, c))
    if not (set(U) & set(V)):
        bi, pi = single(U, V, True)
        if pi:
            rect_in.append((a, c))
print('graph B%d: deficient pairs' % g, D)
print('rectangles passing (i): %d ; of them budget-failing on 21 vertices (out): %d' % (len(rect_i), bud_out_fail))
print('admissible rectangles, z not adjacent to p (budgets + exact PSD on 21 vertices): %d' % len(rect_out))
print('admissible rectangles, z adjacent to p: %d' % len(rect_in))
print('in-admissible but not out-admissible:', [r for r in rect_in if r not in rect_out])


def matchings(adm):
    adm = set(adm)
    part = {a: [c for c in range(18) if (min(a, c), max(a, c)) in adm] for a in range(18)}
    cap = 2 - B
    cnt = np.zeros((9, 9), dtype=np.int64)
    res = []
    used = [False] * 18
    cur = []

    def cells(a, c):
        U, V = D[a], D[c]
        return [(u, v) for u in U for v in V] + [(v, u) for u in U for v in V]

    def rec():
        try:
            a = used.index(False)
        except ValueError:
            res.append(tuple(cur))
            return
        used[a] = True
        for c in part[a]:
            if used[c]:
                continue
            cl = cells(a, c)
            for (i, j) in cl:
                cnt[i, j] += 1
            if all(cnt[i, j] <= cap[i, j] for (i, j) in cl):
                used[c] = True
                cur.append((a, c))
                rec()
                cur.pop()
                used[c] = False
            for (i, j) in cl:
                cnt[i, j] -= 1
        used[a] = False
    rec()
    return res


aut = automorphisms(B)
print('|Aut(B)| =', len(aut))
pair_index = {U: k for k, U in enumerate(D)}


def act(perm, tau):
    out = []
    for a, c in tau:
        a2 = pair_index[tuple(sorted((perm[D[a][0]], perm[D[a][1]])))]
        c2 = pair_index[tuple(sorted((perm[D[c][0]], perm[D[c][1]])))]
        out.append((min(a2, c2), max(a2, c2)))
    return tuple(sorted(out))


def orbits(ms):
    seen = {}
    for tau in ms:
        can = min(act(pm, tau) for pm in aut)
        seen[can] = seen.get(can, 0) + 1
    return seen


for label, adm in (('(i)+(iii) only', rect_i), ('(i)+(iii)+single-type PSD(out)', rect_out)):
    ms = matchings(adm)
    ob = orbits(ms)
    print('%s: %d matchings, %d orbits under Aut' % (label, len(ms), len(ob)))
    if label.startswith('(i)+(iii)+'):
        reps = sorted(ob)
        json.dump({'graph': g, 'D': D, 'rect_out': rect_out, 'rect_in': rect_in, 'rect_i': rect_i,
                   'n_matchings': len(ms), 'reps': reps, 'orbit_sizes': [ob[r] for r in reps]},
                  open('v1_tau_%d.json' % g, 'w'))
    else:
        json.dump({'graph': g, 'D': D, 'n_matchings': len(ms), 'reps': sorted(ob),
                   'orbit_sizes': [ob[r] for r in sorted(ob)]}, open('v1_tau_%d_nopsd.json' % g, 'w'))
print('seconds %.1f' % (time.time() - T0), STAT)
