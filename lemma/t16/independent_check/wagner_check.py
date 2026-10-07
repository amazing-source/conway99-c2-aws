#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Independent exhaustive check of the 'Wagner complement' configuration for a
hypothetical srg(99,14,1,2) with an involution sigma fixing exactly one vertex p.
Written from the task statement only (no other implementation consulted).

Stage 1: all sigma-invariant induced subgraphs on Y = P u Q u X0 u X2 (35 vertices)
         satisfying the given facts and |N_Y(i) n N_Y(j)| <= (1 if A_ij else 2).
Stage 2: for every stage-1 survivor, add T = the 4 X1-neighbours of x and sigma(T),
         and test the srg conditions that are decidable on Y u T u sigma(T).

Usage: python wagner_check.py [A|B|both]
Memory: a few MB.  Single process.
"""
import itertools
import sys
import time
from itertools import combinations

import numpy as np

T0 = time.time()


def log(*a):
    print(" ".join(str(x) for x in a), flush=True)


def popcount(m):
    return bin(m).count("1")


# ---------------------------------------------------------------- basic data
ROW = [frozenset((i + d) % 8 for d in (2, 3, 5, 6)) for i in range(8)]
B = [[1 if j in ROW[i] else 0 for j in range(8)] for i in range(8)]
assert all(B[i][j] == B[j][i] for i in range(8) for j in range(8))
assert all(B[i][i] == 0 for i in range(8))

INTER = {}
for i in range(8):
    for j in range(i + 1, 8):
        INTER[(i, j)] = len(ROW[i] & ROW[j])
DEF = [pr for pr, s in sorted(INTER.items()) if s == 1]  # deficient pairs
DEFIDX = {pr: k for k, pr in enumerate(DEF)}

# automorphisms of B (= automorphisms of the Wagner graph)
AUT = [pi for pi in itertools.permutations(range(8))
       if all(B[pi[i]][pi[j]] == B[i][j] for i in range(8) for j in range(8))]


def map_def(pi, d):
    a, b = DEF[d]
    return DEFIDX[tuple(sorted((pi[a], pi[b])))]


# ---------------------------------------------------------------- vertex layout
# P_i = i, Q_j = 8+j, p = 16, X0\{p}: orbit k -> (17+2k, 18+2k), X2: orbit m -> (27+2m, 28+2m)
def P(i): return i
def Q(j): return 8 + j
PV = 16
def W(k, s=0): return 17 + 2 * k + s
def Z(m, s=0): return 27 + 2 * m + s


NY = 35
SIG = list(range(NY))
for i in range(8):
    SIG[P(i)], SIG[Q(i)] = Q(i), P(i)
for k in range(5):
    SIG[W(k)], SIG[W(k, 1)] = W(k, 1), W(k)
for m in range(4):
    SIG[Z(m)], SIG[Z(m, 1)] = Z(m, 1), Z(m)
X0 = list(range(16, 27))
X0NP = list(range(17, 27))
X2 = list(range(27, 35))


def sig_mask(m):
    """sigma on 8-bit X2 masks; bit b <-> vertex 27+b; bits 2k <-> 2k+1."""
    return ((m & 0x55) << 1) | ((m & 0xAA) >> 1)


# ---------------------------------------------------------------- profiles
# X0 orbit a-values (non-p orbits, sorted); profile multisets given in the task.
PROFILES = {
    "A": dict(x0orbits=[3, 3, 3, 3, 4], X0=[2] + [3] * 8 + [4] * 2, X1max_a=2),
    "B": dict(x0orbits=[2, 3, 3, 4, 4], X0=[2] * 3 + [3] * 4 + [4] * 4, X1max_a=1),
}
for pn, pr in PROFILES.items():
    exp = sorted([2] + [a for a in pr["x0orbits"] for _ in (0, 1)])
    assert exp == sorted(pr["X0"]), pn
    # X0-X2 edge count from both sides: sum a over X0 = sum c over X2 = 6*4 + 2*5 = 34
    assert sum(pr["X0"]) == 34, pn


# ---------------------------------------------------------------- matchings
def perfect_matchings(items):
    if not items:
        yield ()
        return
    a = items[0]
    for k in range(1, len(items)):
        rest = items[1:k] + items[k + 1:]
        for m in perfect_matchings(rest):
            yield ((a, items[k]),) + m


MATCHINGS = list(perfect_matchings(list(range(8))))


def match_key(M, mxy=None):
    """Canonical key of (matching, xy-orbit) under Aut(B).  P<->Q swap acts trivially here."""
    best = None
    for pi in AUT:
        pairs = []
        xy = ()
        for m, (a, b) in enumerate(M):
            e = tuple(sorted((map_def(pi, a), map_def(pi, b))))
            pairs.append(e)
            if m == mxy:
                xy = e
        key = (tuple(sorted(pairs)), xy)
        if best is None or key < best:
            best = key
    return best


def base_matrix(M, mxy=None):
    A = np.zeros((NY, NY), dtype=np.int64)
    for i in range(8):
        for j in range(8):
            if B[i][j]:
                A[P(i), Q(j)] = A[Q(j), P(i)] = 1
    for m, (a, b) in enumerate(M):
        U, V = DEF[a], DEF[b]
        z, zs = Z(m), Z(m, 1)
        for u in U:
            A[z, P(u)] = A[P(u), z] = 1
            A[zs, Q(u)] = A[Q(u), zs] = 1
        for v in V:
            A[z, Q(v)] = A[Q(v), z] = 1
            A[zs, P(v)] = A[P(v), zs] = 1
    if mxy is not None:
        x, y = Z(mxy), Z(mxy, 1)
        A[x, y] = A[y, x] = 1
        A[PV, x] = A[x, PV] = 1
        A[PV, y] = A[y, PV] = 1
    return A


def violations(A, verts, unknown_pairs=()):
    """pairs in verts with common-neighbour count (inside verts) above the bound.
    bound 1 if adjacent, 2 otherwise; pairs listed in unknown_pairs get bound 2."""
    sub = A[np.ix_(verts, verts)]
    C = sub @ sub
    bound = 2 - sub
    idx = {v: n for n, v in enumerate(verts)}
    for (u, v) in unknown_pairs:
        bound[idx[u], idx[v]] = bound[idx[v], idx[u]] = 2
    np.fill_diagonal(C, 0)
    bad = np.argwhere(np.triu(C > bound, 1))
    return [(verts[i], verts[j], int(C[i, j])) for i, j in bad]


def le_ok(A):
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > (2 - A)).any()


# ---------------------------------------------------------------- incidence search
CANDS = {}
for a in (2, 3, 4):
    CANDS[a] = sorted(m for m in range(256) if popcount(m) == a and m <= sig_mask(m))
BITS = [[b for b in range(8) if m >> b & 1] for m in range(256)]
BITPAIRS = [list(combinations(BITS[m], 2)) for m in range(256)]


ALLM = {a: [m for m in range(256) if popcount(m) == a] for a in (2, 3, 4)}


def incidence_search(A0, avals, mxy, use_rep=True, use_order=True):
    """Enumerate sigma-invariant X0\\{p} -> X2 incidences, normalised by
    (rep of each X0 orbit has mask <= sigma(mask)) and (masks nondecreasing among
    orbits with equal a).  Constraints used (all necessary):
      * every X2 vertex has exactly 4 neighbours in X0\\{p} (c_z = a_z + 4, p ~ x,y only);
      * two X0 vertices share <= 2 X2-neighbours;
      * X2-X2 pairs: common neighbours in P u Q u X2 u {p} u (placed X0) <= bound.
    """
    C0 = A0 @ A0
    base = [[int(C0[27 + b1, 27 + b2]) for b2 in range(8)] for b1 in range(8)]
    bnd = [[1 if A0[27 + b1, 27 + b2] else 2 for b2 in range(8)] for b1 in range(8)]
    pmask = (1 << (2 * mxy)) | (1 << (2 * mxy + 1))
    out = []
    n = len(avals)

    def rec(k, placed, cnt, col, chosen):
        if k == n:
            if all(c == 4 for c in col):
                out.append(tuple(chosen))
            return
        a = avals[k]
        for S in (CANDS[a] if use_rep else ALLM[a]):
            if use_order and k > 0 and avals[k - 1] == a and S < chosen[-1]:
                continue
            Ss = sig_mask(S)
            if popcount(S & Ss) > 2:
                continue
            if any(popcount(S & T) > 2 or popcount(Ss & T) > 2 for T in placed):
                continue
            ncol = [col[m] + popcount(S & (3 << (2 * m))) for m in range(4)]
            if max(ncol) > 4:
                continue
            ncnt = [row[:] for row in cnt]
            ok = True
            for MM in (S, Ss):
                for b1, b2 in BITPAIRS[MM]:
                    ncnt[b1][b2] += 1
                    ncnt[b2][b1] += 1
                    if ncnt[b1][b2] > bnd[b1][b2]:
                        ok = False
            if not ok:
                continue
            rec(k + 1, placed + [S, Ss], ncnt, ncol, chosen + [S])

    rec(0, [pmask], base, [0] * 4, [])
    return out


def incidence_search_raw(A0, avals, mxy):
    """Same constraints, NO normalisation (any mask for any orbit, any order).
    Implemented separately (set-based, no incremental counters) for validation."""
    pmask = (1 << (2 * mxy)) | (1 << (2 * mxy + 1))
    C0 = A0 @ A0
    out = []
    n = len(avals)
    allm = {a: [m for m in range(256) if popcount(m) == a] for a in set(avals)}

    def x2pair_ok(masks_all):
        for b1 in range(8):
            for b2 in range(b1 + 1, 8):
                # C0 already contains p's contribution, so skip masks_all[0] (= p)
                c = int(C0[27 + b1, 27 + b2]) + sum(1 for T in masks_all[1:] if (T >> b1 & 1) and (T >> b2 & 1))
                if c > (1 if A0[27 + b1, 27 + b2] else 2):
                    return False
        return True

    def rec(k, chosen):
        masks_all = [pmask] + [f(S) for S in chosen for f in (lambda s: s, sig_mask)]
        for i in range(len(masks_all)):
            for j in range(i + 1, len(masks_all)):
                if popcount(masks_all[i] & masks_all[j]) > 2:
                    return
        cols = [sum(1 for T in masks_all[1:] if T >> b & 1) for b in range(8)]
        if max(cols) > 4:
            return
        if not x2pair_ok(masks_all):
            return
        if k == n:
            if all(c == 4 for c in cols):
                out.append(tuple(chosen))
            return
        for S in allm[avals[k]]:
            rec(k + 1, chosen + [S])

    rec(0, [])
    return out


def normal_form(masks, avals):
    reps = [min(S, sig_mask(S)) for S in masks]
    res = []
    i = 0
    while i < len(avals):
        j = i
        while j < len(avals) and avals[j] == avals[i]:
            j += 1
        res += sorted(reps[i:j])
        i = j
    return tuple(res)


def validate(profile, mode, lo=0, hi=10 ** 9):
    """mode 'rep'  : rep normalisation off, ordering on;
       mode 'order': rep on, ordering off;
       mode 'both' : both off (only on L3 pairs whose Aut(B)-class has solutions, one per class).
    Normal forms of the unnormalised solutions must equal the normalised solution set."""
    avals = PROFILES[profile]["x0orbits"]
    flags = {"rep": (False, True), "order": (True, False), "both": (False, False)}[mode]
    seen = 0
    tot_raw = tot_norm = 0
    done_cls = set()
    l3idx = -1
    for M in MATCHINGS:
        for mxy in range(4):
            A3 = base_matrix(M, mxy)
            if violations(A3, list(range(17)) + X2):
                continue
            l3idx += 1
            if not (lo <= l3idx < hi):
                continue
            norm = set(incidence_search(A3, avals, mxy))
            if mode == "both":
                k = match_key(M, mxy)
                if not norm or k in done_cls:
                    continue
                done_cls.add(k)
            seen += 1
            raw = incidence_search(A3, avals, mxy, *flags)
            nf = set(normal_form(m, avals) for m in raw)
            tot_raw += len(raw)
            tot_norm += len(norm)
            if nf != norm:
                log("MISMATCH", M, mxy, len(nf), len(norm))
                return False
            log("  ok pair", seen, "raw", len(raw), "norm", len(norm), "t=%.0fs" % (time.time() - T0))
    log("validate %s mode=%s: %d L3 pairs, unnormalised incidences %d, normalised %d, normal forms agree" % (
        profile, mode, seen, tot_raw, tot_norm))
    return True


def internal_sets(avals):
    """sigma-invariant graphs on X0\\{p} with deg(w_k) = a_k - 2 and no w~sigma(w) edge,
    as sets of edge-orbits (k,l,t): t=0 -> {w_k,w_l},{sw_k,sw_l}; t=1 -> {w_k,sw_l},{sw_k,w_l}."""
    deg = [a - 2 for a in avals]
    tot = sum(deg)
    assert tot % 2 == 0
    EO = [(k, l, t) for k in range(5) for l in range(k + 1, 5) for t in (0, 1)]
    res = []
    for comb in combinations(EO, tot // 2):
        d = [0] * 5
        for (k, l, t) in comb:
            d[k] += 1
            d[l] += 1
        if d == deg:
            res.append(comb)
    return res


def eo_edges(eo):
    k, l, t = eo
    return [(W(k), W(l, t)), (W(k, 1), W(l, 1 - t))]


def build_full(A0, masks, comb):
    A = A0.copy()
    for k, S in enumerate(masks):
        Ss = sig_mask(S)
        for b in BITS[S]:
            A[W(k), 27 + b] = A[27 + b, W(k)] = 1
        for b in BITS[Ss]:
            A[W(k, 1), 27 + b] = A[27 + b, W(k, 1)] = 1
    for eo in comb:
        for (u, v) in eo_edges(eo):
            A[u, v] = A[v, u] = 1
    return A


# ---------------------------------------------------------------- fact verification
def verify_facts(A, profile):
    """Re-check every given fact directly on a 35x35 matrix (independent of construction)."""
    pr = PROFILES[profile]
    errs = []
    if not (A == A.T).all(): errs.append("asym")
    if A.diagonal().any(): errs.append("loop")
    S = np.array(SIG)
    if not (A[np.ix_(S, S)] == A).all(): errs.append("sigma")
    for i in range(8):
        for j in range(8):
            if A[P(i), P(j)] or A[Q(i), Q(j)]: errs.append("PQindep")
            if A[P(i), Q(j)] != B[i][j]: errs.append("B")
    PQ = list(range(16))
    if A[np.ix_(PQ, X0)].any(): errs.append("PQ-X0")
    for v in PQ:
        if A[v, X2].sum() != 2: errs.append("PQ-X2deg")
    seenP = []
    for z in X2:
        pp = tuple(i for i in range(8) if A[z, P(i)])
        qq = tuple(j for j in range(8) if A[z, Q(j)])
        if pp not in DEFIDX or qq not in DEFIDX: errs.append("X2pairs")
        seenP.append(pp)
        # d-value: equal numbers in P and Q
    if sorted(seenP) != sorted(DEF): errs.append("defonce")
    for v in range(16, 35):
        if A[v, 0:8].sum() != A[v, 8:16].sum(): errs.append("dval")
    x2e = [(u, v) for u in X2 for v in X2 if u < v and A[u, v]]
    if len(x2e) != 1: errs.append("X2edges")
    else:
        x, y = x2e[0]
        if SIG[x] != y or not A[PV, x] or not A[PV, y]: errs.append("xy")
    aX0 = sorted(int(A[w, X2].sum()) for w in X0)
    if aX0 != sorted(pr["X0"]): errs.append("aX0")
    aX2 = sorted(int(A[z, X2].sum()) for z in X2)
    if aX2 != [0] * 6 + [1] * 2: errs.append("aX2")
    for w in X0:
        a = int(A[w, X2].sum())
        if A[w, X0].sum() != a - 2: errs.append("cX0")
    for z in X2:
        a = int(A[z, X2].sum())
        if A[z, X0].sum() != a + 4: errs.append("cX2")
    if A[PV, X0].sum() != 0 or A[PV, X2].sum() != 2: errs.append("p")
    for w in X0NP:
        if A[w, SIG[w]]: errs.append("w-sw")
    if not le_ok(A): errs.append("lambda/mu")
    return errs


# ---------------------------------------------------------------- canonical form
SWAPS = (0, 1)  # set to (0,) to drop the P<->Q swap from the symmetry group


def canon(A):
    """Canonical key under: Aut(B) x {P<->Q swap} on indices, plus any sigma-commuting
    relabelling of X0\\{p} and X2.  X2 vertices are labelled by their (unique) P-pair."""
    best = None
    for pi in AUT:
        for s in SWAPS:
            newlab = {}
            for i in range(8):
                if s == 0:
                    newlab[P(i)], newlab[Q(i)] = P(pi[i]), Q(pi[i])
                else:
                    newlab[P(i)], newlab[Q(i)] = Q(pi[i]), P(pi[i])
            x2lab = {}
            qdata = [None] * 8
            for z in X2:
                nb = [newlab[u] for u in range(16) if A[z, u]]
                pp = tuple(sorted(v for v in nb if v < 8))
                qq = tuple(sorted(v - 8 for v in nb if v >= 8))
                li = DEFIDX[pp]
                x2lab[z] = li
                qdata[li] = DEFIDX[qq]
            xy = tuple(sorted(x2lab[z] for z in X2 if A[z, X2].sum()))
            masks = {w: sum(1 << x2lab[z] for z in X2 if A[w, z]) for w in X0NP}
            ws = sorted(X0NP, key=lambda w: masks[w])
            groups = [list(g) for _, g in itertools.groupby(ws, key=lambda w: masks[w])]
            for perms in itertools.product(*[itertools.permutations(g) for g in groups]):
                order = [w for g in perms for w in g]
                pos = {w: n for n, w in enumerate(order)}
                adj = tuple(int(A[order[i], order[j]]) for i in range(10) for j in range(i + 1, 10))
                mates = tuple(pos[SIG[w]] for w in order)
                key = (tuple(qdata), xy, tuple(masks[w] for w in order), adj, mates)
                if best is None or key < best:
                    best = key
    return best


# ---------------------------------------------------------------- stage 2
NT = 43
SIG43 = SIG + [39, 40, 41, 42, 35, 36, 37, 38]


def x0_assign(sizes, r, X0list):
    """all tuples of sets S_t (|S_t| = sizes[t]) from X0list with column counts == r[w]."""
    need = {w: r[w] for w in X0list}
    out = []

    def rec(t, need, acc):
        if t == len(sizes):
            if all(v == 0 for v in need.values()):
                out.append(tuple(acc))
            return
        avail = [w for w in X0list if need[w] > 0]
        for S in combinations(avail, sizes[t]):
            nn = dict(need)
            for w in S:
                nn[w] -= 1
            # feasibility: remaining demand must equal remaining capacity
            if sum(nn.values()) != sum(sizes[t + 1:]):
                continue
            rec(t + 1, nn, acc + [S])

    rec(0, need, [])
    return out


def vkind(v, xv):
    if v < 8: return "P"
    if v < 16: return "Q"
    if v == PV: return "p"
    if v < 27: return "X0"
    if v == xv: return "x"
    if v == SIG[xv]: return "y"
    if v < 35: return "X2"
    if v < 39: return "t"
    return "st"


def stage2(A, xv, profile, verbose=True):
    """Return (status, details, survivors) for adding T = N(x) n X1 (4 vertices) and sigma(T)."""
    maxa = PROFILES[profile]["X1max_a"]
    y = SIG[xv]
    NXY = [v for v in range(NY) if A[xv, v]]
    assert len(NXY) == 10
    r = {}
    for v in range(NY):
        if v == xv:
            continue
        target = 1 if A[xv, v] else 2
        known = int(sum(A[v, u] for u in NXY))
        r[v] = target - known  # = #{t in T : t ~ v}, exactly
    stats = {}
    if min(r.values()) < 0:
        return "dead:negative r", {"r": r}, []
    sP = sum(r[P(i)] for i in range(8))
    sQ = sum(r[Q(j)] for j in range(8))
    X2o = [z for z in X2 if z != xv]
    n2 = sum(r[z] for z in X2o)          # = sum_t (a_t - 1)
    s0 = sum(r[w] for w in X0)           # = sum_t c_t = sum_t (a_t + 1) = (4 + n2) + 4
    det = dict(sP=sP, sQ=sQ, n2=n2, s0=s0, r_y=r[y], r_p=r[PV],
               rP=[r[P(i)] for i in range(8)], rQ=[r[Q(j)] for j in range(8)],
               rX0={w: r[w] for w in X0 if r[w]}, rX2={z: r[z] for z in X2o if r[z]})
    if sP != 4:
        return "dead:sum r(P) != 4", det, []
    if sQ != 4:
        return "dead:sum r(Q) != 4", det, []
    # n2 = number of t with a_t = 2 (each a_t in {1,..,maxa}; in A at most one t has a=2)
    if n2 > (1 if maxa >= 2 else 0):
        return "dead:n2 too large", det, []
    if s0 != 8 + n2:
        return "dead:sum r(X0) != 8+n2", det, []
    if any(r[z] > 1 for z in X2o):
        return "dead:r(z)>1 on X2", det, []
    Pm = sorted(i for i in range(8) for _ in range(r[P(i)]))
    Qm = [j for j in range(8) for _ in range(r[Q(j)])]
    z2 = [z for z in X2o if r[z] > 0]
    qperms = sorted(set(itertools.permutations(Qm)))
    a2choices = list(range(4)) if n2 == 1 else [None]
    n_assign = n_tint = n_E = n_full = 0
    reasons = {}

    def bump(k):
        reasons[k] = reasons.get(k, 0) + 1

    survivors = []
    tpairs = list(combinations(range(4), 2))
    for qp in qperms:
        for a2 in a2choices:
            at = [2 if i == a2 else 1 for i in range(4)]
            sizes = [a + 1 for a in at]
            for S0s in x0_assign(sizes, r, X0):
                n_assign += 1
                M = np.zeros((NT, NT), dtype=np.int64)
                M[:NY, :NY] = A
                for i in range(4):
                    t, ts = 35 + i, 39 + i
                    nb = [P(Pm[i]), Q(qp[i]), xv] + ([z2[0]] if i == a2 else []) + list(S0s[i])
                    for v in nb:
                        M[t, v] = M[v, t] = 1
                        M[ts, SIG[v]] = M[SIG[v], ts] = 1
                mt = [int(M[35 + i, NXY].sum()) for i in range(4)]
                if max(mt) > 1:
                    bump("A1: some t has >=2 nbrs in N_Y(x)")
                    continue
                if sum(1 for v in mt if v == 0) % 2:
                    bump("A2: odd number of t unmatched inside N_Y(x)")
                    continue
                tint_found = False
                pre_E = n_E
                for tm in range(64):
                    deg = [0] * 4
                    for b, (i, j) in enumerate(tpairs):
                        if tm >> b & 1:
                            deg[i] += 1
                            deg[j] += 1
                    if any(mt[i] + deg[i] != 1 for i in range(4)):
                        continue  # lambda=1 inside N(x): exactly one neighbour each
                    n_tint += 1
                    tint_found = True
                    M1 = M.copy()
                    for b, (i, j) in enumerate(tpairs):
                        if tm >> b & 1:
                            M1[35 + i, 35 + j] = M1[35 + j, 35 + i] = 1
                            M1[39 + i, 39 + j] = M1[39 + j, 39 + i] = 1
                    ms = [int(M1[39 + j, NXY].sum()) for j in range(4)]
                    for em in range(64):
                        cnt = ms[:]
                        for b, (i, j) in enumerate(tpairs):
                            if em >> b & 1:
                                cnt[i] += 1  # t_j ~ s t_i
                                cnt[j] += 1  # t_i ~ s t_j
                        if any(c != 2 for c in cnt):
                            continue  # |N(x) n N(s t_j)| = 2 exactly (s t_j not ~ x)
                        n_E += 1
                        M2 = M1.copy()
                        for b, (i, j) in enumerate(tpairs):
                            if em >> b & 1:
                                M2[35 + i, 39 + j] = M2[39 + j, 35 + i] = 1
                                M2[35 + j, 39 + i] = M2[39 + i, 35 + j] = 1
                        # full checks
                        S = np.array(SIG43)
                        assert (M2[np.ix_(S, S)] == M2).all()
                        C = M2 @ M2
                        np.fill_diagonal(C, 0)
                        badm = np.triu(C > (2 - M2), 1)
                        if badm.any():
                            kinds = sorted(set(
                                "-".join(sorted((vkind(u, xv), vkind(v, xv)))) + ("(adj)" if M2[u, v] else "(non)")
                                for u, v in np.argwhere(badm)))
                            bump("F1: <= violated on " + ",".join(kinds))
                            continue
                        exact_ok = True
                        for c in (xv, y):
                            for v in range(NT):
                                if v != c and C[c, v] != (1 if M2[c, v] else 2):
                                    exact_ok = False
                        if not exact_ok:
                            bump("F2: exact count with x or y fails")
                            continue
                        if M2[xv].sum() != 14 or M2[y].sum() != 14:
                            bump("F3: degree of x/y")
                            continue
                        n_full += 1
                        survivors.append(M2)
                if not tint_found:
                    bump("A3: no T-internal graph gives a perfect matching on N(x)")
                elif n_E == pre_E:
                    bump("A4: no T-sigma(T) edge set gives |N(x) n N(s t)| = 2")
    det.update(n_assign=n_assign, n_tint=n_tint, n_E=n_E, n_full=n_full,
               qperms=len(qperms), a2choices=len(a2choices), reasons=reasons)
    return ("SURVIVES" if survivors else "dead:exhausted"), det, survivors


# ---------------------------------------------------------------- driver
def describe(A):
    lines = []
    names = {}
    for i in range(8):
        names[P(i)] = "P%d" % i
        names[Q(i)] = "Q%d" % i
    names[PV] = "p"
    for k in range(5):
        names[W(k)] = "w%d" % k
        names[W(k, 1)] = "sw%d" % k
    for m in range(4):
        names[Z(m)] = "z%d" % m
        names[Z(m, 1)] = "sz%d" % m
    for v in range(16, NY):
        nb = [names[u] for u in range(NY) if A[v, u]]
        lines.append("  %-4s: %s" % (names[v], " ".join(nb)))
    return "\n".join(lines)


def run_profile(profile, do_stage2=True):
    pr = PROFILES[profile]
    avals = pr["x0orbits"]
    log("=" * 70)
    log("PROFILE", profile, " X0 non-p orbit a-values:", avals)
    ISETS = internal_sets(avals)
    log("sigma-invariant X0-internal graphs with prescribed degrees (labelled):", len(ISETS))

    # level counts on matchings
    L1 = L2 = 0
    L3pairs = []
    for M in MATCHINGS:
        A = base_matrix(M)
        PQ = list(range(16))
        # L1: P-Q pairs only (common nbrs of P_i,Q_j lie in X2 only)
        C = A @ A
        ok1 = all(C[P(i), Q(j)] <= (1 if B[i][j] else 2) for i in range(8) for j in range(8))
        if not ok1:
            continue
        L1 += 1
        verts = list(range(16)) + X2
        unk = [(u, v) for u in X2 for v in X2 if u < v]
        if violations(A, verts, unk):
            continue
        L2 += 1
        for mxy in range(4):
            A3 = base_matrix(M, mxy)
            if violations(A3, list(range(17)) + X2):
                continue
            L3pairs.append((M, mxy))
    if profile == "A":
        mk = set(match_key(M) for M in MATCHINGS)
        log("perfect matchings of the 8 deficient pairs:", len(MATCHINGS),
            " Aut(B)-classes:", len(mk))
    log("matchings passing P-Q common-neighbour bound (L1):", L1)
    log("matchings passing all bounds on P u Q u X2 (X2-X2 adjacency unknown) (L2):", L2)
    log("(matching, xy-orbit) pairs passing bounds on P u Q u X2 u {p} (L3):", len(L3pairs),
        " Aut(B)-classes:", len(set(match_key(M, mxy) for M, mxy in L3pairs)))

    n_inc = 0
    n_inc_pairs = 0
    n_int_tested = 0
    n_valid = 0
    canon_store = {}
    per_pair = []
    for (M, mxy) in L3pairs:
        A0 = base_matrix(M, mxy)
        incs = incidence_search(A0, avals, mxy)
        n_inc += len(incs)
        nv_here = 0
        if incs:
            n_inc_pairs += 1
        for masks in incs:
            for comb in ISETS:
                # quick necessary filter: adjacent X0 vertices share <= 1 X2-neighbour
                bad = False
                for eo in comb:
                    for (u, v) in eo_edges(eo):
                        mu = masks[(u - 17) // 2] if (u - 17) % 2 == 0 else sig_mask(masks[(u - 17) // 2])
                        mv = masks[(v - 17) // 2] if (v - 17) % 2 == 0 else sig_mask(masks[(v - 17) // 2])
                        if popcount(mu & mv) > 1:
                            bad = True
                if bad:
                    continue
                n_int_tested += 1
                A = build_full(A0, masks, comb)
                if not le_ok(A):
                    continue
                errs = verify_facts(A, profile)
                assert not errs, errs
                n_valid += 1
                nv_here += 1
                key = canon(A)
                if key not in canon_store:
                    canon_store[key] = (A, M, mxy, masks, comb)
        per_pair.append((M, mxy, len(incs), nv_here))
    log("normalised X0-X2 incidences (summed over L3 pairs):", n_inc,
        " L3 pairs with >=1 incidence:", n_inc_pairs)
    log("(incidence, X0-internal graph) combos passing quick filter:", n_int_tested)
    log("valid Y configurations (labelled, X0-normalised):", n_valid)
    log("valid Y configurations up to isomorphism:", len(canon_store))
    log("  [time %.1fs]" % (time.time() - T0))
    # per Aut(B)-class of (matching, xy): counts
    cls = {}
    for (M, mxy, ninc, nv) in per_pair:
        k = match_key(M, mxy)
        c = cls.setdefault(k, [0, 0, 0])
        c[0] += 1
        c[1] += ninc
        c[2] += nv
    log("per Aut(B)-class of (matching, xy): [#labelled pairs, #incidences, #valid configs]")
    for k in sorted(cls):
        if cls[k][1] or cls[k][2]:
            log("  ", k, cls[k])

    with open("stage1_configs_%s.txt" % profile, "w") as fh:
        fh.write("Profile %s: %d stage-1 configurations up to isomorphism.\n" % (profile, len(canon_store)))
        fh.write("Layout: P0-7, Q0-7 (Q_j = sigma P_j), p, X0 orbits (wk, swk), X2 orbits (zm, szm);\n")
        fh.write("zm sees P_U, Q_V; szm sees P_V, Q_U.  Adjacency lists of p, X0, X2 restricted to Y.\n\n")
        for n, (key, (A, M, mxy, masks, comb)) in enumerate(sorted(canon_store.items())):
            fh.write("config #%d  matching(U,V) per X2 orbit: %s  xy-orbit: %d\n" % (
                n, [(DEF[a], DEF[b]) for a, b in M], mxy))
            fh.write(describe(A) + "\n\n")
    if not do_stage2:
        return canon_store
    # stage 2
    log("-" * 70)
    log("STAGE 2 (profile %s): adding T = N(x) n X1 and sigma(T)" % profile)
    total_surv = 0
    for n, (key, (A, M, mxy, masks, comb)) in enumerate(sorted(canon_store.items())):
        log("config #%d: matching %s (as DEF pairs %s), xy-orbit %d, masks %s, X0-internal %s" % (
            n, M, [(DEF[a], DEF[b]) for a, b in M], mxy, [format(m, "08b")[::-1] for m in masks], comb))
        res = []
        for side in (0, 1):
            st, det, surv = stage2(A, Z(mxy, side), profile)
            res.append((st, det, surv))
            log("   x = %s: %s | %s" % ("z%d" % mxy if side == 0 else "sz%d" % mxy, st,
                                       {k: det[k] for k in det if k not in ("rX0", "rX2")}))
        if res[0][0] != res[1][0]:
            log("   WARNING: x/y asymmetry in stage-2 status")
        if res[0][2]:
            total_surv += 1
            log("   SURVIVING stage-2 configuration(s):", len(res[0][2]))
            log(describe(A))
    log("profile %s: stage-1 iso classes = %d, stage-2 survivors = %d" % (profile, len(canon_store), total_surv))
    return canon_store


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which.startswith("validate"):
        pfl = sys.argv[2]
        rng = [int(v) for v in sys.argv[4:6]] if len(sys.argv) > 5 else []
        validate(pfl, sys.argv[3], *rng)
        log("total time %.1fs" % (time.time() - T0))
        return
    log("ROW:", [sorted(r) for r in ROW])
    log("|row_i n row_j| by difference:", {d: INTER[(0, d)] for d in range(1, 8)})
    log("deficient pairs:", DEF)
    log("|Aut(B)| =", len(AUT))
    profs = ["A", "B"] if which == "both" else [which]
    for pfl in profs:
        run_profile(pfl)
    log("total time %.1fs" % (time.time() - T0))


if __name__ == "__main__":
    main()
