# T20 round 3, case I: STAGE 1 = all configurations of N(p)  (fast version; replaces stage1.py).
#
# A configuration of N(p) ("N-configuration") for the profile (h2, h1, h0) is a SET of
#   h2 pairs  ("A", U, V), U < V disjoint deficient pairs ("rectangle"): w ~ p, sigma w, x_U, y_V; sigma w ~ x_V, y_U
#   h1 pairs  ("W", i, k), i < k:                                           w ~ p, sigma w, x_i, y_k; sigma w ~ x_k, y_i
# (plus h0 pairs "Z" with no neighbour in S) such that
#   (C1) every index 0..9 lies in exactly two of the sets U u V, {i, k};
#   (C2) each rectangle satisfies (R1): an index of U has at most one B-neighbour in V and conversely;
#   (C3) two vertices of N(p) in two different pairs have at most one common neighbour in S.
# (C1) is forced (a vertex x_i outside N[p] has exactly 2 neighbours in N(p), never two mates).  (C2), (C3) are
# budget conditions (exact): (C2) on S u {w, sigma w} (adjacent pair w, x_i resp. w, y_l), (C3) on
# S u {p} u two pairs (two non-adjacent vertices with the common neighbour p).  Units: by (C3) no deficient pair
# is used twice.  n_3 = 2 (option z=...): the rectangles use only the deficient pairs left by z and sigma z
# (m_ij reduced by one for the three pairs of U3 and of V3), and every vertex of every pair must have at most 2
# common neighbours in S with z and with sigma z (budget of a non-adjacent pair; adjacent pairs are tested later).
#
# The N-configurations are enumerated combinatorially (each exactly once: the smallest index covered less than
# twice receives its missing pairs in increasing order); one is kept as a representative iff it is the smallest
# of its images under G (check: the orbit sizes of the representatives add up to the total number); G = Aut(B)  (n_3 = 2: G = the elements of Aut(B) preserving {U3, V3}; an element exchanging U3 and V3
# is composed with the renaming z <-> sigma z, which does not change the unordered types of the pairs of N(p)).
# n_3 = 0: each representative is the base S u N[p] (35 vertices): exact budget count on the whole graph, then
#          exact PSD rejection (integer vector, eng.Tester.reject) or kept (float).
# n_3 = 2: the 35 vertices S u N[p] are tested first (same tests); for each representative left, the 84 choices
#          of N(z) n N(p) = {w1, w2} (two different pairs; then sigma z ~ sigma w1, sigma w2) give the bases
#          S u N[p] u {z, sigma z} (37 vertices): exact budget count (cases6.budget_rows), then exact PSD rejection
#          (eng5.Node.psd_fail: integer vector) or kept.  In the output "zn" = the two vertices (0..13 inside N(p)).
#
# Parallel use: with part=i/n the enumeration is done completely (it is fast) but only the representatives whose
# rank (order of generation) is i mod n are tested; stage1_merge.py puts the n outputs together, in the order of
# the ranks, which gives exactly the output of a run without the option.
#
# usage: python stage1c.py <graph> <h2> <h1> <h0> <outfile.json> [z=a,b,c:d,e,f] [part=i/n]
import sys, json, time, itertools
import numpy as np
import r3lib, eng

name = sys.argv[1]
h2, h1, h0 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
outfile = sys.argv[5]
ztype = None
PART, NPARTS = 0, 1
for a in sys.argv[6:]:
    if a.startswith("part="):
        PART, NPARTS = (int(t) for t in a[5:].split("/"))
    if a.startswith("z="):
        u, v = a[2:].split(":")
        ztype = (tuple(int(t) for t in u.split(",")), tuple(int(t) for t in v.split(",")))
assert h2 + h1 + h0 == 7 and 4 * h2 + 2 * h1 == 20
t0 = time.time()
m = r3lib.load_B(name)
units = r3lib.units_of(m)
group = r3lib.aut_group(m)


def bits(T):
    r = 0
    for i in T:
        r |= 1 << i
    return r


def pc(x):
    return bin(x).count("1")


if ztype:
    U3, V3 = ztype
    for T3 in (U3, V3):
        for pr in itertools.combinations(T3, 2):
            units[pr] -= 1
            assert units[pr] >= 0
            if units[pr] == 0:
                del units[pr]
    G = [g for g in group if set((tuple(sorted(g[i] for i in U3)), tuple(sorted(g[i] for i in V3)))) == {U3, V3}]
    MZ = (bits(U3) | bits(V3) << 10, bits(V3) | bits(U3) << 10)
else:
    G = list(group)
    MZ = ()

upairs = sorted(units)
types = []          # (key, mask of w, mask of sigma w, indices)
for U in upairs:
    for V in upairs:
        if U < V and not set(U) & set(V):
            if all(sum(m[i][l] for l in V) <= 1 for i in U) and all(sum(m[l][i] for i in U) <= 1 for l in V):
                mw = bits(U) | bits(V) << 10
                ms = bits(V) | bits(U) << 10
                if all(pc(mw & z) <= 2 and pc(ms & z) <= 2 for z in MZ):
                    types.append((("A", U, V), mw, ms, U + V))
nrect = len(types)
for i in range(10):
    for k in range(i + 1, 10):
        mw = 1 << i | 1 << (10 + k)
        ms = 1 << k | 1 << (10 + i)
        types.append((("W", i, k), mw, ms, (i, k)))
types.sort()
nt = len(types)
compat = [[False] * nt for _ in range(nt)]
for a in range(nt):
    for b in range(nt):
        if a != b:
            compat[a][b] = pc(types[a][1] & types[b][1]) <= 1 and pc(types[a][1] & types[b][2]) <= 1
by_index = {i: [a for a in range(nt) if i in types[a][3]] for i in range(10)}
isA = [types[a][0][0] == "A" for a in range(nt)]

tindex = {types[a][0]: a for a in range(nt)}
# action of G on the type indices
gmap = []
for g in G:
    mp = []
    for a in range(nt):
        tp = types[a][0]
        if tp[0] == "A":
            U = tuple(sorted(g[i] for i in tp[1])); V = tuple(sorted(g[i] for i in tp[2]))
            if U > V:
                U, V = V, U
            mp.append(tindex[("A", U, V)])      # KeyError here would mean that the type set is not G-invariant
        else:
            i, k = g[tp[1]], g[tp[2]]
            if i > k:
                i, k = k, i
            mp.append(tindex[("W", i, k)])
    gmap.append(mp)

reps = []
repidx = []
nrep = [0]
cov = [0] * 10
nodes = [0]
total = [0]
osum = [0]


def leaf(chosen):
    """an N-configuration (generated exactly once).  It is kept as a representative iff it is the smallest
    image of itself under G; osum adds the sizes of the orbits of the representatives (must equal the total)."""
    total[0] += 1
    c = tuple(sorted(chosen))
    imgs = set()
    for mp in gmap:
        im = tuple(sorted([mp[a] for a in c]))
        if im < c:
            return
        imgs.add(im)
    if nrep[0] % NPARTS == PART:
        reps.append(c)
        repidx.append(nrep[0])
    nrep[0] += 1
    osum[0] += len(imgs)


def rec(chosen, nA, nW, cur_i, last):
    nodes[0] += 1
    i = next((j for j in range(10) if cov[j] < 2), None)
    if i is None:
        if nA == h2 and nW == h1:
            leaf(chosen)
        return
    for a in by_index[i]:
        if i == cur_i and a <= last:
            continue
        if isA[a]:
            if nA >= h2:
                continue
        elif nW >= h1:
            continue
        idx = types[a][3]
        if any(cov[j] >= 2 for j in idx):
            continue
        ca = compat[a]
        if not all(ca[b] for b in chosen):
            continue
        for j in idx:
            cov[j] += 1
        chosen.append(a)
        rec(chosen, nA + isA[a], nW + (not isA[a]), i, a)
        chosen.pop()
        for j in idx:
            cov[j] -= 1


rec([], 0, 0, -1, -1)
t1 = time.time()
assert osum[0] == total[0], "orbit sizes of the representatives do not add up to the number of N-configurations"
t2 = time.time()
nconf = total[0]

stats = eng.Counter()
tester = eng.Tester(stats)
sig35 = r3lib.sigma_of(35)
cnt = {"tested": 0, "budget": 0, "psd": 0, "kept": 0, "n35_tested": 0, "n35_budget": 0, "n35_psd": 0}
bases = []
bases_ri = []


def build35(cfg):
    """S u N[p]: x_i = i, y_i = 10 + i, p = 20, pair t = (21 + 2t, 22 + 2t)"""
    A = r3lib.support(m, 14)
    for t in range(7):
        w, sw = 21 + 2 * t, 22 + 2 * t
        A[w, sw] = A[sw, w] = 1
        A[w, 20] = A[20, w] = 1
        A[sw, 20] = A[20, sw] = 1
        if t < len(cfg):
            tp = types[cfg[t]][0]
            if tp[0] == "A":
                for i in tp[1]:
                    A[w, i] = A[i, w] = 1; A[sw, 10 + i] = A[10 + i, sw] = 1
                for i in tp[2]:
                    A[w, 10 + i] = A[10 + i, w] = 1; A[sw, i] = A[i, sw] = 1
            else:
                i, k = tp[1], tp[2]
                A[w, i] = A[i, w] = 1; A[w, 10 + k] = A[10 + k, w] = 1
                A[sw, k] = A[k, sw] = 1; A[sw, 10 + i] = A[10 + i, sw] = 1
    return A


if ztype:
    import eng5, cases6
    zpairs = [(a_, b_) for a_ in range(14) for b_ in range(a_ + 1, 14) if a_ // 2 != b_ // 2]
    assert len(zpairs) == 84
    ZR = np.zeros((84, 35), dtype=np.int64)
    for q, (a_, b_) in enumerate(zpairs):
        for i in U3:
            ZR[q, i] = 1
        for i in V3:
            ZR[q, 10 + i] = 1
        ZR[q, 21 + a_] = 1
        ZR[q, 21 + b_] = 1
    sigarr35 = np.array(sig35)
for ri, c in zip(repidx, reps):
    pairs = [list(types[a][0]) for a in c] + [["Z"]] * h0
    A = build35(c)
    cnt["n35_tested"] += 1
    if r3lib.budget_viol(A):
        cnt["n35_budget"] += 1
        continue
    if tester.reject(A, sig35) is not None:
        cnt["n35_psd"] += 1
        continue
    if not ztype:
        bases.append({"pairs": pairs})
        bases_ri.append(ri)
        continue
    # n_3 = 2: the orbit {z, sigma z} is added to the 35 vertices with N(z) n N(p) = {w1, w2} (84 choices)
    CA = A @ A + A
    W1 = (CA >= 2).astype(np.int64); np.fill_diagonal(W1, 0)
    W2 = (CA >= 1).astype(np.int64); np.fill_diagonal(W2, 0)
    bad = cases6.budget_rows(A, W1, W2, sigarr35, ZR)
    cnt["tested"] += 84
    cnt["budget"] += int(bad.sum())
    node = None
    for q in range(84):
        if bad[q]:
            continue
        if node is None:
            node = eng5.Node(A, sig35)
            node.prepare()
        if node.psd_fail(ZR[q], 0, stats) is not None:
            cnt["psd"] += 1
            continue
        cnt["kept"] += 1
        bases.append({"pairs": pairs, "zn": list(zpairs[q])})
        bases_ri.append(ri)
if not ztype:
    cnt["tested"], cnt["budget"], cnt["psd"], cnt["kept"] = cnt["n35_tested"], cnt["n35_budget"], cnt["n35_psd"], len(bases)
out = {"graph": name, "profile": [h2, h1, h0], "ztype": ztype, "group_order": len(G), "rects": nrect,
       "nconfigs_labelled": nconf, "nconfig_orbits": nrep[0], "enum_nodes": nodes[0],
       "part": PART, "nparts": NPARTS, "bases_rank": bases_ri,
       "tested": cnt["tested"], "rejected_budget": cnt["budget"], "rejected_psd_exact": cnt["psd"],
       "kept": cnt["kept"], "n35": [cnt["n35_tested"], cnt["n35_budget"], cnt["n35_psd"]], "stats": stats.c, "seconds": time.time() - t0, "bases": bases}
json.dump(out, open(outfile, "w"))
print("%s profile (%d,%d,%d)%s: |G| = %d; rectangles %d; N-configurations %d (enumeration nodes %d), orbits under G %d" % (
    name, h2, h1, h0, (" z = %s ; %s" % ztype) if ztype else "", len(G), nrect, nconf, nodes[0], nrep[0]))
if NPARTS > 1:
    print("   PART %d of %d: only the representatives of rank = %d mod %d are tested here" % (PART, NPARTS, PART, NPARTS))
if ztype:
    print("   on the 35 vertices S u N[p]: tested %d, rejected by budgets %d, by PSD (exact) %d" % (
        cnt["n35_tested"], cnt["n35_budget"], cnt["n35_psd"]))
print("   bases tested %d: rejected by budgets %d, by PSD (exact) %d, kept %d   stats %s   [enum %.0f s, orbits %.0f s, tests %.0f s]" % (
    cnt["tested"], cnt["budget"], cnt["psd"], cnt["kept"], stats.c, t1 - t0, t2 - t1, time.time() - t2))
