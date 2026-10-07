# Transcription checks for T20_PROOF (not part of the proof; no search, no solver).
# Rebuilds the nine support structures from the edge lists printed in the text and recomputes the small data
# quoted there (degrees, eigen-equation, budgets on S u {p}, codegrees, automorphisms, triangles, deficient
# units, the numbers r_i of IIa.0, the count 180 of type graphs, the K4 labelling of case III), and checks
# a few arithmetic identities of the hand part by brute force.
import itertools, json, os, sys
from fractions import Fraction

I_GRAPHS = {
    "I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79",
    "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
    "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89",
    "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
    "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79",
    "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89",
}
OTHER = {
    "IIa.0": ("07 08 09 13 15 16 23 24 26 28 29 35 37 39 45 46 48 57 68 79", "23", (0, 1)),
    "III.0": ("07 08 09 15 16 19 24 26 28 34 35 37 48 49 57 58 67 69", "", (0, 1, 2, 3)),
    "III.1": ("07 08 09 15 16 19 24 26 28 34 35 37 48 49 56 57 67 89", "", (0, 1, 2, 3)),
}
DEF = {   # (pairs with m = 2, pairs with m = 1) as printed in the text
    "I.0": ("01 02 18 26 39 45 47 58 67", "03 04 17 19 25 29 34 36 38 59 68 79"),
    "I.1": ("01 02 19", "03 04 17 18 25 26 27 28 34 35 36 38 39 45 46 47 49 57 58 59 67 68 69 78"),
    "I.2": ("01 02 17 26 67", "03 04 18 19 25 29 34 35 36 38 39 45 47 48 49 57 58 59 68 89"),
    "I.3": ("01 02 39 45 47", "03 04 15 16 18 19 26 27 28 29 34 36 38 56 58 59 67 68 78 79"),
    "I.4": ("01 28 39 47 56", "02 03 05 07 14 16 18 19 25 27 29 34 35 38 46 48 57 68 69 79"),
    "I.5": ("05 17 29 38 46", "01 02 06 08 12 16 18 26 28 34 35 37 39 45 47 49 57 59 68 79"),
    "IIa.0": ("45 67", "01 04 05 06 08 16 18 19 29 38 47 49 57 58 69 78"),
    "III.0": ("49 58 67", "07 08 09 14 15 18 25 26 27 34 36 39 47 48 57 59 68 69"),
    "III.1": ("58", "05 06 07 14 18 19 25 26 27 34 38 39 45 46 47 49 59 67 68 69 78 79"),
}
AUT = {"I.0": 16, "I.1": 4, "I.2": 10, "I.3": 4, "I.4": 4, "I.5": 20, "IIa.0": 1, "III.0": 3, "III.1": 4}
TRI = {"I.0": 4, "I.1": 6, "I.2": 5, "I.3": 6, "I.4": 8, "I.5": 10}
COD = {   # codegrees of adjacent / non-adjacent pairs of B, as printed
    "I.0": ({0: 8, 1: 12}, {0: 1, 2: 24}),
    "I.1": ({0: 3, 1: 16, 2: 1}, {1: 8, 2: 17}),
    "I.2": ({0: 5, 1: 15}, {1: 5, 2: 20}),
    "I.3": ({0: 4, 1: 14, 2: 2}, {0: 1, 1: 6, 2: 18}),
    "I.4": ({0: 2, 1: 12, 2: 6}, {0: 3, 1: 8, 2: 14}),
    "I.5": ({1: 10, 2: 10}, {0: 5, 1: 10, 2: 10}),
}


def pairs(s):
    return [(int(t[0]), int(t[1])) for t in s.split()]


def build(minus, plus, inner):
    """adjacency (list of sets) on x_i = i, y_i = 10 + i, p = 20"""
    adj = [set() for _ in range(21)]

    def e(u, v):
        adj[u].add(v); adj[v].add(u)
    for i, j in pairs(minus):
        e(i, 10 + j); e(j, 10 + i)
    for i, j in pairs(plus):
        e(i, j); e(10 + i, 10 + j)
    for i in inner:
        e(i, 10 + i); e(20, i); e(20, 10 + i)
    return adj


def check_structure(name, minus, plus, inner):
    adj = build(minus, plus, inner)
    # sigma-invariance is built in; eigen-equation (E)
    phi = [1] * 10 + [-1] * 10 + [0]
    for v in range(20):
        assert sum(phi[w] for w in adj[v]) == -4 * phi[v], (name, v)
    assert sum(phi[w] for w in adj[20]) == 0
    # budgets (L) on the 21 vertices
    for u in range(21):
        for v in range(u + 1, 21):
            c = len(adj[u] & adj[v])
            assert c <= (1 if v in adj[u] else 2), (name, u, v, c)
    # deficient units: pairs of S+ with need = 2 - [adjacent] - (common neighbours in S u {p})
    need = {}
    for i in range(10):
        for j in range(i + 1, 10):
            n = (1 if j in adj[i] else 2) - len(adj[i] & adj[j])
            assert n >= 0
            if n:
                need[(i, j)] = n
    m2 = sorted(k for k, v in need.items() if v == 2)
    m1 = sorted(k for k, v in need.items() if v == 1)
    assert m2 == sorted(pairs(DEF[name][0])), (name, m2)
    assert m1 == sorted(pairs(DEF[name][1])), (name, m1)
    return adj, need


def automorphisms(minus, plus, inner):
    """permutations of the ten orbits preserving the minus graph, the plus graph and the set of inner orbits"""
    M = [[0] * 10 for _ in range(10)]
    for i, j in pairs(minus):
        M[i][j] |= 1; M[j][i] |= 1
    for i, j in pairs(plus):
        M[i][j] |= 2; M[j][i] |= 2
    inn = set(inner)
    out = []
    g = [-1] * 10
    used = [False] * 10

    def rec(k):
        if k == 10:
            out.append(tuple(g)); return
        for t in range(10):
            if used[t] or ((k in inn) != (t in inn)):
                continue
            if all(M[k][a] == M[t][g[a]] for a in range(k)):
                g[k] = t; used[t] = True
                rec(k + 1)
                used[t] = False; g[k] = -1
    rec(0)
    return out


print("1. the nine structures")
tot_need = {}
for name, minus in I_GRAPHS.items():
    adj, need = check_structure(name, minus, "", ())
    B = [[0] * 10 for _ in range(10)]
    for i, j in pairs(minus):
        B[i][j] = B[j][i] = 1
    assert all(sum(r) == 4 for r in B)
    ca, cn = {}, {}
    for i in range(10):
        for j in range(i + 1, 10):
            c = sum(B[i][l] * B[j][l] for l in range(10))
            assert c <= 2
            d = ca if B[i][j] else cn
            d[c] = d.get(c, 0) + 1
            # the number of common neighbours of x_i, x_j inside S is the codegree
            assert need.get((i, j), 0) == 2 - c
    assert (ca, cn) == COD[name], (name, ca, cn)
    tri = sum(1 for a in range(10) for b in range(a + 1, 10) for c in range(b + 1, 10) if B[a][b] and B[b][c] and B[a][c])
    assert tri == TRI[name], (name, tri)
    na = len(automorphisms(minus, "", ()))
    assert na == AUT[name], (name, na)
    assert sum(need.values()) == 30
    # independence number 3 (remark only)
    alpha = max(len(c) for r in range(1, 6) for c in itertools.combinations(range(10), r)
                if all(not B[a][b] for a in c for b in c))
    print("   %s: 4-regular, codegrees <= 2, adjacent %s non-adjacent %s, triangles %d, |Aut| %d, units 30, independence number %d"
          % (name, ca, cn, tri, na, alpha))
for name, (minus, plus, inner) in OTHER.items():
    adj, need = check_structure(name, minus, plus, inner)
    na = len(automorphisms(minus, plus, inner))
    assert na == AUT[name], (name, na)
    print("   %s: (E) and (L) hold on S u {p}; units %d; |Aut| %d" % (name, sum(need.values()), na))
    tot_need[name] = sum(need.values())
assert tot_need == {"IIa.0": 20, "III.0": 24, "III.1": 24}

print("2. IIa.0: the numbers r_i and the 180 type graphs")
minus, plus, inner = OTHER["IIa.0"]
adj = build(minus, plus, inner)
r = {i: len(adj[i] & {0, 10, 1, 11}) for i in range(2, 10)}
assert r == {2: 0, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}, r
assert 3 in adj[2] and 13 in adj[2] and 12 in adj[3]            # the quad x_2 x_3 y_2 y_3
assert adj[2] & adj[3] == {19}                                    # triangle x_2 x_3 y_9
deg = {i: 2 - r[i] for i in r}
edges = list(itertools.combinations(range(2, 10), 2))
cnt = 0
for es in itertools.combinations(edges, 5):
    d = {i: 0 for i in range(2, 10)}
    for a, b in es:
        d[a] += 1; d[b] += 1
    if d == deg:
        cnt += 1
assert cnt == 180
print("   r =", r, "; simple graphs on {2..9} with degrees 2 - r_i:", cnt)

print("3. case III: the words are the edges of K4")
lab = {4: {2, 3}, 5: {1, 3}, 6: {1, 2}, 7: {0, 3}, 8: {0, 2}, 9: {0, 1}}
for name in ("III.0", "III.1"):
    minus, plus, inner = OTHER[name]
    adj = build(minus, plus, inner)
    for j in range(4, 10):
        assert {c for c in range(4) if 10 + c in adj[j]} == lab[j]
        assert not ({0, 1, 2, 3} & adj[j])
    W = {j: sorted(l for l in range(4, 10) if 10 + l in adj[j]) for j in range(4, 10)}
    assert all(len(v) == 2 for v in W.values())
    # rule: for a word j and c in j, at most one W-neighbour of j contains c
    for j in range(4, 10):
        for c in lab[j]:
            assert sum(1 for l in W[j] if c in lab[l]) <= 1
    # shape of W
    seen, comps = set(), []
    for j in range(4, 10):
        if j in seen:
            continue
        comp, stack = [], [j]
        while stack:
            a = stack.pop()
            if a in seen:
                continue
            seen.add(a); comp.append(a); stack += W[a]
        comps.append(sorted(comp))
    print("   %s: word-word graph components %s" % (name, comps))

print("4. arithmetic of the hand part")
# multisets of non-zero kappa with sum of squares 10
ms = set()
for a in range(0, 2):
    for b in range(0, 3):
        for c in range(0, 11):
            if 9 * a + 4 * b + c == 10:
                ms.add((a, b, c))
assert ms == {(1, 0, 1), (0, 2, 2), (0, 1, 6), (0, 0, 10)}, ms
# counting identities, m = 10:  C(d,2) + C(d+4,2) = d^2 + 3d + 6
for d in range(0, 6):
    assert d * (d - 1) // 2 + (d + 4) * (d + 3) // 2 == d * d + 3 * d + 6
# (Q0), n_3 = 0, as a polynomial identity in t and in the three sums of squares
# sum_out a_2^2 = 1440 - 2t;  sums of a_2: 2t (X_0, 9 vertices), 300 - 4t (X_1, 40), 2t (X_2, 30)
for t in range(0, 60):
    lhs = (1440 - 2 * t) - 12 * (2 * t) + 36 * 9 - 9 * (300 - 4 * t) + 20 * 40 - 5 * (2 * t) + 6 * 30
    assert lhs == 44
# (Q2), n_3 = 2
for t in range(0, 60):
    for al in (0, 1):
        for eps in (0, 1):
            S_sq = 2 * (4 * eps + 16 * (6 - 2 * eps) + 36 * (4 + eps))
            out_sq = (24 * 14 + 24 * 23 * 2 - 2 * t) - S_sq - 2 * al * al
            lhs = out_sq - 10 * (2 * t + 4 * al) + 25 * 7 - 7 * (240 - 4 * t - 6 * al) + 12 * 46 - 3 * (2 * t) + 2 * 24
            assert lhs == 55 - 16 * eps, (t, al, eps, lhs)
# identity (1) of the edge bound:  108 - 8s, and (4): 16 (9 - s)
for s in range(0, 10):
    assert 44 + 2 * (72 - 4 * s) - 2 * 40 == 108 - 8 * s
    assert 108 - 8 * s - 4 * (2 * s) + 4 * 9 == 16 * (9 - s)
# cells of profile (4,2,1): all solutions of Lemma 9.13
sols = set()
for sZ in range(0, 3):
    for sW in range(0, 7):
        for c in (0, 1):
            for AA in range(0, 13):
                for AW in range(0, 17):
                    for WW in range(0, 3 - c):
                        for WZ in range(0, 5):
                            for AZ in range(0, 9):
                                if AZ + WZ == 8 + sZ and AW + 2 * WW + WZ == 8 + sW and 2 * AA + AW + AZ == 6 - sZ - sW:
                                    sols.add((sZ, sW, AA, AW, WW, WZ, AZ, c))
exp = {(0, 0, 0, 1, 2, 3, 5, 0), (0, 0, 0, 2, 1, 4, 4, 0), (0, 0, 0, 2, 1, 4, 4, 1), (0, 0, 1, 0, 2, 4, 4, 0),
       (0, 1, 0, 1, 2, 4, 4, 0), (1, 0, 0, 0, 2, 4, 5, 0)}
assert sols == exp, sorted(sols)
print("   multisets of values, C(d,2) + C(d+4,2), (Q0), (Q2), the edge-bound identities and the six cell solutions: OK")

print("5. the two matrices on the eigenvalues, and the traces of Lemma 6.3")
for (A, J) in ((14, 99), (3, 0), (-4, 0)):
    print("   A = %3d: M1 = %d, M2 = %d" % (A, 27 - 9 * A + J, 44 + 11 * A - 2 * J))
assert Fraction(27 * 1 - 9 * 14 + 99, 63) == 0 and Fraction(44 * 1 + 11 * 14 - 2 * 99, 77) == 0
print("ALL CHECKS PASSED")
