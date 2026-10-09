"""Orbits of the subspaces of the torsion space E of the large component under the automorphisms of a (4,8) ball
(they preserve each component; the layers may be permuted, by the same permutation in both components).
An automorphism sends a graph in which B is balanced to a graph in which g(B) is balanced, so one subspace per orbit
is enough.  In coordinates on the basis E: a row of coefficients c becomes c.R(g), with g.E[k] = sum_j R[k][j] E[j]."""
import itertools
from orbits23 import component_maps, coords


def echelon(rows):
    M = [[x % 7 for x in r] for r in rows]; r = 0; t = len(M[0])
    for c in range(t):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; iv = pow(M[r][c], -1, 7); M[r] = [(x * iv) % 7 for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[r])]
        r += 1
    return tuple(tuple(x) for x in M[:r])


def torsion_action(adj, lay, comp, E):
    """matrices R(g) on E for the automorphisms of the ball (first component must follow the same layer permutation)"""
    mats = []
    for sigma in itertools.permutations(range(3)):
        if not component_maps(adj, lay, comp, 0, sigma): continue
        for g in component_maps(adj, lay, comp, 1, sigma):
            inv = {w: v for v, w in g.items()}
            R = [coords(E, [e[inv[v]] if v in inv else 0 for v in range(36)]) for e in E]
            mats.append(R)
    return mats


def orbit_filter(mats, rows_list):
    """rep[i] = index of the representative of the orbit of subspace i (the smallest index of the orbit)"""
    canon = {echelon(rows): i for i, rows in enumerate(rows_list)}
    assert len(canon) == len(rows_list)
    rep = {}
    for i, rows in enumerate(rows_list):
        if i in rep: continue
        orb = set()
        for R in mats:
            img = echelon([[sum(c * R[k][j] for k, c in enumerate(r)) % 7 for j in range(len(R))] for r in rows])
            orb.add(canon[img])
        assert i in orb and min(orb) == i
        for j in orb: rep[j] = i
    assert len(rep) == len(rows_list)
    return rep
