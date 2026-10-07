# T20 round 3, case I (k = 0): INDEPENDENT verifier.  Imports nothing from eng* / cases* / r3lib / stage1c:
# own model, own enumeration of the configurations of N(p), own budget counts, own PSD test.
#
# Hand part used (report): S+ and S- independent, S disjoint from N[p], x_i ~ y_j iff i ~_B j;  N(p) = seven mate
# pairs, with h2 pairs in X_2 of type {U, V} (U, V disjoint deficient pairs), h1 pairs in X_1 of type {i, k},
# i != k, h0 pairs in X_0; every x_i has exactly two neighbours in N(p); the vertices of X_2 outside N(p) are
# words s with N(s) n S+ = x_U, N(s) n S- = y_V, exactly two neighbours in N(p) (different pairs); every deficient
# unit not used by N(p) [nor by X_3] is N(s) n S+ for exactly one such s.  Caps (upper bounds only):
#   n_3 = 0: a_2(s) <= 5;  a vertex of N(p): at most 4 - h0 (X_2), 8 - h0 (X_1), min(10, 12 - h0) (X_0)
#            neighbours among the words of X_2.
#   n_3 = 2: X_3 = {z, sigma z}, z a word with exactly two neighbours in N(p), a_2(z) <= 1;
#            a_2(s) + 2 a_3(s) <= 4;  a vertex w of N(p) with a3 = a_3(w): at most 3 - h0 - 2 a3 (X_2),
#            7 - h0 - 2 a3 (X_1), min(11 - h0 - 2 a3, (20 - 3 a3) // 2) (X_0) neighbours among the words of X_2.
#
# step 1:  python in_verify.py bases <graph> <h2> <h1> <h0> <out prefix>_<i>of<n>.json part=i/n      (i = 0..n-1)
#          python in_verify.py merge <stage1.json> <out prefix> <n> [<follow prefix>]
#          re-enumerates the configurations of N(p) (n_3 = 0) by another method (rectangles first, tested by a
#          count on the graph S u {p} u pairs; then the X_1 types as a graph with prescribed degrees; full count on
#          35 vertices), reduces them under Aut(B) (own computation); "merge" compares with the stage-1 file.
# step 1, branch n_3 = 2 (X_3 = {z, sigma z} of type (U3 ; V3) in the base, 37 vertices):
#          python in_verify.py basesz <graph> <h2> <h1> <h0> <a,b,c:d,e,f> <out prefix>_<i>of<n>.json part=i/n
#          python in_verify.py mergez <stage1.json> <out prefix> <n> [<follow prefix>]
# step 2:  python in_verify.py follow <stage1.json> <stage2 prefix> <part> <nparts> <out prefix>_<part>of<nparts>.json [first=K] [every=E] [sub=j/m]
#          for the bases of that part: re-traverses the search tree of eng6.  The unit treated at each node is read
#          from the plan stored in the jsonl file (the choice of the unit is not part of the proof); ALL candidates
#          of that unit are regenerated and tested here; the number kept must equal the plan's.
# Exact rejections: a common-neighbour count (int64), or an integer vector x with x^T M x < 0 in Python integers
# (on a sigma-block), or exact rational elimination.  "Kept" is a floating-point decision.
# Nodes that the first program rejected by the rank bound (it wrote no plan below them): this program explores their
# subtree by itself, with the same exact tests and its own choice of the unit, to exhaustion ("free" counters:
# rank_nodes, rank_nodes_closed_by_own_search, free_nodes, free_deepest = largest number of X_2 orbits placed).
# Only if such an exploration hits its cap or finds a complete configuration is the node rejected by an exact rank
# computation done here in rationals (both sigma-blocks of M1 against the bound 22): rank_nodes_closed_by_rank_bound.
# With a plan of the old format (5 fields per line) the same rank computation is used to find WHICH kept children the
# first program left without plan (holes_located_by_own_rank); it rejects nothing.
import sys, json, os, itertools, time
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = 20
TOL = 1e-7
FREE_CAP = 20000          # nodes of an exploration without plan (below a node rejected by rank in the first program)
FREE_SECONDS = 3600.0     # cpu seconds of such an exploration


def load_B(name):
    case, idx = name.split(".")
    rec = json.load(open(os.path.join(HERE, "structures_I.json")))[case][int(idx)]
    assert not rec["H"]
    B = [[1 if (v & 1) else 0 for v in row] for row in rec["m"]]
    for i in range(10):
        assert B[i][i] == 0 and sum(B[i]) == 4 and all(B[i][j] == B[j][i] for j in range(10))
    return B


def support21(B):
    A = np.zeros((21, 21), dtype=np.int64)
    for i in range(10):
        for j in range(10):
            if B[i][j]:
                A[i, 10 + j] = A[10 + j, i] = 1
    phi = np.array([1] * 10 + [-1] * 10 + [0])
    assert (A @ phi == -4 * phi).all()
    return A


def deficient(B):
    u = {}
    for i in range(10):
        for j in range(i + 1, 10):
            c = sum(1 for l in range(10) if B[i][l] and B[j][l])
            if c < 2:
                u[(i, j)] = 2 - c
    assert sum(u.values()) == 30
    return u


def budget_violation(A):
    """exact recount: some pair u != v with more than 2 - A[u,v] common neighbours"""
    X = A @ A + A
    np.fill_diagonal(X, 0)
    return bool((X > 2).any())


def qform(M, x):
    return sum(x[a] * sum(M[a][b] * x[b] for b in range(len(x)) if x[b]) for a in range(len(x)) if x[a])


def exact_psd(Q):
    n = len(Q)
    Bm = [[Fraction(int(t)) for t in row] for row in Q]
    idx = list(range(n))
    while idx:
        if any(Bm[i][i] < 0 for i in idx):
            return False
        piv = next((i for i in idx if Bm[i][i] > 0), None)
        if piv is None:
            return all(Bm[i][j] == 0 for i in idx for j in idx)
        idx.remove(piv)
        for i in idx:
            f = Bm[i][piv] / Bm[piv][piv]
            if f:
                for j in idx:
                    Bm[i][j] -= f * Bm[piv][j]
    return True


NCERT = [0, 0]


def psd_rejected(A, sig):
    """True if M1 = 9(3I-A)+J or M2 = 11(4I+A)-2J is exactly NOT positive semidefinite on this vertex set
    (integer vector on a sigma-block, form evaluated with Python integers; or exact elimination).
    False = kept (floating-point decision)."""
    n = A.shape[0]
    reps = [v for v in range(n) if sig[v] > v]
    fixed = [v for v in range(n) if sig[v] == v]
    D = np.zeros((n, len(reps)), dtype=np.int64)
    E = np.zeros((n, len(fixed) + len(reps)), dtype=np.int64)
    for j, v in enumerate(fixed):
        E[v, j] = 1
    for j, v in enumerate(reps):
        D[v, j] = 1; D[sig[v], j] = -1
        E[v, len(fixed) + j] = 1; E[sig[v], len(fixed) + j] = 1
    I = np.eye(n, dtype=np.int64)
    M1 = 9 * (3 * I - A) + 1
    M2 = 11 * (4 * I + A) - 2
    for M, Bs in ((M1, D), (M2, D), (M1, E), (M2, E)):
        Q = Bs.T @ M @ Bs
        w, V = np.linalg.eigh(Q.astype(np.float64))
        if w[0] < -TOL:
            Ql = Q.tolist()
            v = V[:, 0]
            mx = float(np.abs(v).max())
            for sc in (2, 3, 6, 12, 30, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10):
                x = [int(round(float(t) * sc / mx)) for t in v]
                if any(x) and qform(Ql, x) < 0:
                    NCERT[0] += 1
                    return True
            if not exact_psd(Ql):
                NCERT[1] += 1
                return True
    return False


def exact_rank(Q):
    """rank of an integer matrix, by elimination in exact rationals"""
    M = [[Fraction(int(t)) for t in row] for row in Q]
    rk = 0
    rows, cols = len(M), len(M[0])
    for cidx in range(cols):
        piv = next((r for r in range(rk, rows) if M[r][cidx] != 0), None)
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        for r in range(rk + 1, rows):
            if M[r][cidx] != 0:
                f = M[r][cidx] / M[rk][cidx]
                M[r] = [a - f * b for a, b in zip(M[r], M[rk])]
        rk += 1
        if rk == rows:
            break
    return rk


def rank_bound_violated(A, sig):
    """Rank bound (T18_PROOF.md, Proposition 6.4; a general fact on the graph and sigma, it does not use the theorem
    T18): on a sigma-invariant vertex set the matrices D^T M1 D (odd generators e_v - e_sigma v) and E^T M1 E (even
    generators e_p, e_v + e_sigma v) have rank at most 22.  Exact ranks; tested as soon as there are 23 generators."""
    n = A.shape[0]
    reps = [v for v in range(n) if sig[v] > v]
    fixed = [v for v in range(n) if sig[v] == v]
    if len(reps) + len(fixed) < 23:
        return False
    I = np.eye(n, dtype=np.int64)
    M1 = 9 * (3 * I - A) + 1
    if len(reps) >= 23:
        D = np.zeros((n, len(reps)), dtype=np.int64)
        for j, v in enumerate(reps):
            D[v, j] = 1; D[sig[v], j] = -1
        if exact_rank((D.T @ M1 @ D).tolist()) > 22:
            return True
    E = np.zeros((n, len(fixed) + len(reps)), dtype=np.int64)
    for j, v in enumerate(fixed):
        E[v, j] = 1
    for j, v in enumerate(reps):
        E[v, len(fixed) + j] = 1; E[sig[v], len(fixed) + j] = 1
    return exact_rank((E.T @ M1 @ E).tolist()) > 22


def add_pair(A, t, tp):
    """pair t of N(p) on the vertices 21 + 2t, 22 + 2t"""
    w, sw = 21 + 2 * t, 22 + 2 * t
    for (u, v) in ((w, sw), (w, P), (sw, P)):
        A[u, v] = A[v, u] = 1
    if tp[0] == "A":
        for i in tp[1]:
            A[w, i] = A[i, w] = 1; A[sw, 10 + i] = A[10 + i, sw] = 1
        for i in tp[2]:
            A[w, 10 + i] = A[10 + i, w] = 1; A[sw, i] = A[i, sw] = 1
    elif tp[0] == "W":
        i, k = tp[1], tp[2]
        A[w, i] = A[i, w] = 1; A[w, 10 + k] = A[10 + k, w] = 1
        A[sw, k] = A[k, sw] = 1; A[sw, 10 + i] = A[10 + i, sw] = 1


def sigma(n):
    s = list(range(10, 20)) + list(range(10)) + [20]
    for v in range(21, n, 2):
        s += [v + 1, v]
    return s


# ------------------------------------------------------------------ step 1

def automorphisms(B):
    """own computation: images of 0 and of its neighbours first, then propagation by brute force"""
    out = []
    order = [0]
    while len(order) < 10:
        nxt = max((i for i in range(10) if i not in order), key=lambda i: sum(B[i][j] for j in order))
        order.append(nxt)

    def rec(k, img):
        if k == 10:
            out.append(tuple(img[i] for i in range(10)))
            return
        v = order[k]
        for t in range(10):
            if t in img.values():
                continue
            if all(B[v][u] == B[t][img[u]] for u in order[:k]):
                img[v] = t
                rec(k + 1, img)
                del img[v]
    rec(0, {})
    return out


def cfg_image(cfg, g):
    out = []
    for tp in cfg:
        if tp[0] == "A":
            U = tuple(sorted(g[i] for i in tp[1])); V = tuple(sorted(g[i] for i in tp[2]))
            out.append(("A",) + ((U, V) if U < V else (V, U)))
        else:
            i, k = g[tp[1]], g[tp[2]]
            out.append(("W", min(i, k), max(i, k)))
    return tuple(sorted(out))


def step_bases(name, h2, h1, h0, outfile, part, nparts):
    """All configurations of N(p) whose first rectangle (in the fixed order of the rectangles) has rank = part
    mod nparts.  A configuration passing the budget count on 35 vertices is counted; if it is the smallest image of
    itself under Aut(B) it is a representative: the size of its orbit is added to `osum` and it is tested (PSD)."""
    t0 = time.time()
    B = load_B(name)
    A21 = support21(B)
    defi = deficient(B)
    G = automorphisms(B)
    dl = sorted(defi)
    rects = [(U, V) for U in dl for V in dl if U < V and not set(U) & set(V)]
    sig35 = sigma(35)
    raw = [0, 0, 0]
    res = {"osum": 0, "norb": 0, "npsd": 0}
    kept = []

    def finish(rs, cov):
        need = [2 - c for c in cov]
        if sum(need) != 2 * h1:
            return
        # all simple graphs with degrees `need` on the indices and h1 edges, each once (the edges at the smallest
        # index that still needs one are added in increasing order)
        def wrec(es, nd, li, lk):
            if len(es) == h1:
                if not any(nd):
                    raw[1] += 1
                    A = np.zeros((35, 35), dtype=np.int64)
                    A[:21, :21] = A21
                    cfg = [("A", U, V) for (U, V) in rs] + [("W", i, k) for (i, k) in es]
                    for t, tp in enumerate(cfg):
                        add_pair(A, t, tp)
                    for t in range(len(cfg), 7):
                        add_pair(A, t, ("Z",))
                    if not budget_violation(A):
                        raw[2] += 1
                        c = tuple(sorted(cfg))
                        imgs = set(cfg_image(cfg, g) for g in G)
                        if c == min(imgs):
                            res["norb"] += 1
                            res["osum"] += len(imgs)
                            if psd_rejected(A, sig35):
                                res["npsd"] += 1
                            else:
                                kept.append(c)
                return
            i = next((j for j in range(10) if nd[j]), None)
            if i is None:
                return
            for k in range(i + 1, 10):
                if i == li and k <= lk:
                    continue
                if nd[k]:
                    nd[i] -= 1; nd[k] -= 1
                    wrec(es + [(i, k)], nd, i, k)
                    nd[i] += 1; nd[k] += 1
        wrec([], need, -1, -1)

    def rrec(start, rs, cov):
        if len(rs) == h2:
            finish(rs, cov)
            return
        for a in range(start, len(rects)):
            if not rs and a % nparts != part:
                continue
            U, V = rects[a]
            if any(cov[i] >= 2 for i in U + V):
                continue
            rs2 = rs + [(U, V)]
            raw[0] += 1
            A = np.zeros((21 + 2 * len(rs2), 21 + 2 * len(rs2)), dtype=np.int64)
            A[:21, :21] = A21
            for t, (U_, V_) in enumerate(rs2):
                add_pair(A, t, ("A", U_, V_))
            if budget_violation(A):
                continue
            for i in U + V:
                cov[i] += 1
            rrec(a + 1, rs2, cov)
            for i in U + V:
                cov[i] -= 1
    rrec(0, [], [0] * 10)
    out = {"graph": name, "profile": [h2, h1, h0], "part": part, "nparts": nparts, "aut": len(G), "rects": len(rects),
           "rectangle_sets_tested": raw[0], "right_coverage": raw[1], "passing_budget": raw[2],
           "orbits": res["norb"], "orbit_sizes_sum": res["osum"], "rejected_psd": res["npsd"],
           "kept": [[list(tp) for tp in c] for c in kept],
           "certificates": {"integer_vector": NCERT[0], "exact_elimination": NCERT[1]},
           "seconds": round(time.time() - t0, 1)}
    json.dump(out, open(outfile, "w"))
    print("part %d of %d: rectangle sets tested %d, right coverage %d, passing the budget count %d, representatives "
          "%d (orbit sizes %d), rejected by PSD %d, kept %d   [%.0f s]" % (
              part, nparts, raw[0], raw[1], raw[2], res["norb"], res["osum"], res["npsd"], len(kept), time.time() - t0))


def step_merge(s1file, prefix, nparts, follow_prefix):
    s1 = json.load(open(s1file))
    name = s1["graph"]
    h2, h1, h0 = s1["profile"]
    assert not s1.get("ztype")
    B = load_B(name)
    G = automorphisms(B)
    parts = [json.load(open("%s_%dof%d.json" % (prefix, i, nparts))) for i in range(nparts)]
    for i, p in enumerate(parts):
        assert p["part"] == i and p["nparts"] == nparts and p["graph"] == name and p["profile"] == [h2, h1, h0]
    npass = sum(p["passing_budget"] for p in parts)
    osum = sum(p["orbit_sizes_sum"] for p in parts)
    norb = sum(p["orbits"] for p in parts)
    kept = set()
    for p in parts:
        for c in p["kept"]:
            kept.add(tuple(tuple(tuple(x) if isinstance(x, list) else x for x in tp) for tp in c))
    ref = set()
    for b in s1["bases"]:
        cfg = []
        for tp in b["pairs"]:
            if tp[0] == "A":
                cfg.append(("A", tuple(tp[1]), tuple(tp[2])))
            elif tp[0] == "W":
                cfg.append(("W", tp[1], tp[2]))
        ref.add(min(cfg_image(cfg, g) for g in G))
    print("%s profile (%d,%d,%d), second program, stage 1 (%d parts): |Aut(B)| = %d (first program: %d); rectangle "
          "sets tested %d; configurations with the right coverage %d" % (
              name, h2, h1, h0, nparts, len(G), s1["group_order"], sum(p["rectangle_sets_tested"] for p in parts),
              sum(p["right_coverage"] for p in parts)))
    print("   passing the budget count on 35 vertices: %d (first program: %d); sum of the orbit sizes of the "
          "representatives: %d (must be equal)" % (npass, s1["nconfigs_labelled"], osum))
    print("   orbits under Aut(B): %d (first program: %d); rejected by PSD (exact) %d; kept %d (first program: %d)" % (
        norb, s1["nconfig_orbits"], sum(p["rejected_psd"] for p in parts), len(kept), len(s1["bases"])))
    print("   in the first list only: %d; in this list only: %d" % (len(ref - kept), len(kept - ref)))
    ok1 = (npass == s1["nconfigs_labelled"] == osum and norb == s1["nconfig_orbits"] and kept == ref)
    print("   STAGE 1 AGREES: %s" % ok1)
    if follow_prefix:
        tot = {}
        nb = 0
        inpart = 0
        cert = [0, 0]
        missing = []
        for i in range(nparts):
            fn = "%s_%dof%d.json" % (follow_prefix, i, nparts)
            if not os.path.exists(fn):
                missing.append(i)
                continue
            f = json.load(open(fn))
            if f.get("partial"):
                missing.append(i)
                continue
            nb += f["bases_followed"]
            inpart += f["bases_in_part"]
            cert[0] += f["certificates"]["integer_vector"]; cert[1] += f["certificates"]["exact_elimination"]
            for k, v in f["totals"].items():
                tot[k] = max(tot.get(k, 0), v) if k == "free_deepest" else tot.get(k, 0) + v
        print("   stage 2 re-traversed: bases %d of %d (stage-1 list: %d); parts not finished: %s" % (
            nb, inpart, len(s1["bases"]), missing if missing else "none"))
        print("   totals: %s; certificates: integer vector %d, exact elimination %d" % (tot, cert[0], cert[1]))
        if tot.get("rank_nodes", 0):
            print("   nodes rejected by the rank bound in the first program: %d; closed here by the own search (no "
                  "rank bound): %d, with %d more nodes, deepest node with %d orbits of X_2 placed; closed here by an "
                  "own exact rank computation: %d" % (
                      tot["rank_nodes"], tot.get("rank_nodes_closed_by_own_search", 0), tot.get("free_nodes", 0),
                      tot.get("free_deepest", 0), tot.get("rank_nodes_closed_by_rank_bound", 0)))
        print("   STAGE 2 AGREES AT EVERY NODE, 0 complete, all bases: %s" % (
            not missing and nb == len(s1["bases"]) and tot.get("complete", 1) == 0))


# ------------------------------------------------------------------ step 1, branch n_3 = 2

def orbit_counts_batch(A0, sig, R):
    """EXACT (int64).  A0: a sigma-invariant graph without budget violation; R: rows (one per candidate) = the
    neighbourhood, inside A0, of a new vertex s not adjacent to its mate sigma s (whose row is the image under sigma).
    True where A0 + {s, sigma s} has a pair of vertices with more than 2 - [adjacent] common neighbours.  Such a pair
    is: (s, old v): (R A0)_v + R_v > 2;  (s, sigma s): R . (R o sigma) > 2;  two old vertices u, v of N(s) with
    C_uv + A_uv + 1 + [both in N(sigma s)] > 2 (C = A0^2);  the pairs containing sigma s are the images of these."""
    CA = A0 @ A0 + A0
    Q1 = (CA >= 2).astype(np.int64); np.fill_diagonal(Q1, 0)
    Q2 = (CA >= 1).astype(np.int64); np.fill_diagonal(Q2, 0)
    RS = R[:, np.array(sig)]
    bad = ((R @ A0 + R) > 2).any(1)
    bad |= (R * RS).sum(1) > 2
    bad |= ((R @ Q1) * R).sum(1) > 0
    T = R * RS
    bad |= ((T @ Q2) * T).sum(1) > 0
    return bad


def zkey_image(items, g, swap):
    """items: list of (type, zp), type = ("A", U, V) with U < V, ("W", i, k) with i < k, or ("Z",);
    zp = 0 (no neighbour of the pair is adjacent to z), 1 (the first vertex of the pair is: the one adjacent to x_U
    resp. x_i), 2 (the second one).  Image under the relabelling g of the indices; swap = 1 when z and sigma z are
    renamed (g exchanges U3 and V3).  The two vertices of a Z pair are interchangeable: zp is 0 or 1 there."""
    out = []
    for tp, zp in items:
        flip = False
        if tp[0] == "A":
            U = tuple(sorted(g[i] for i in tp[1])); V = tuple(sorted(g[i] for i in tp[2]))
            if U > V:
                U, V = V, U
                flip = True
            tp2 = ("A", U, V)
        elif tp[0] == "W":
            i, k = g[tp[1]], g[tp[2]]
            if i > k:
                i, k = k, i
                flip = True
            tp2 = ("W", i, k)
        else:
            tp2 = ("Z",)
        z2 = zp
        if zp and tp[0] != "Z" and (flip != bool(swap)):
            z2 = 3 - zp
        if tp[0] == "Z" and zp:
            z2 = 1
        out.append((tp2, z2))
    return tuple(sorted(out))


def zgroup(B, U3, V3):
    G = []
    for g in automorphisms(B):
        gu = tuple(sorted(g[i] for i in U3)); gv = tuple(sorted(g[i] for i in V3))
        if (gu, gv) == (U3, V3):
            G.append((g, 0))
        if (gu, gv) == (V3, U3):
            G.append((g, 1))
    return G


def zkey(items, G):
    return min(zkey_image(items, g, sw) for g, sw in G)


def step_bases_z(name, h2, h1, h0, U3, V3, outfile, part, nparts):
    """Branch n_3 = 2.  All configurations of N(p) whose first rectangle has rank = part mod nparts, tested by exact
    counts on S u {p, z, sigma z} u pairs with z not yet attached (a spanning subgraph of the true graph: the
    counts are upper bounds there).  A configuration passing the count on the 37 vertices is treated if it is the
    smallest of its images under G_z (elements of Aut(B) preserving {U3, V3}).  Then every choice of N(z) n N(p) =
    two vertices of two different pairs (84 choices): exact count on the complete 37-vertex graph, the hand filter
    a_2(z) <= 1 (not two vertices of A pairs), exact PSD test.  The kept bases are written as canonical keys."""
    t0 = time.time()
    B = load_B(name)
    A21 = support21(B)
    defi = deficient(B)
    G = zgroup(B, U3, V3)
    dl = sorted(defi)
    rects = [(U, V) for U in dl for V in dl if U < V and not set(U) & set(V)]
    nb = 37
    sig37 = sigma(37)
    ZV, SZV = 35, 36

    def start(n):
        A = np.zeros((n, n), dtype=np.int64)
        A[:21, :21] = A21
        return A

    def put_z(A, zv, szv):
        for i in U3:
            A[zv, i] = A[i, zv] = 1; A[szv, 10 + i] = A[10 + i, szv] = 1
        for i in V3:
            A[zv, 10 + i] = A[10 + i, zv] = 1; A[szv, i] = A[i, szv] = 1
    chk = start(23)
    put_z(chk, 21, 22)
    assert not budget_violation(chk), "the type of z fails the count on S u {p, z, sigma z}"
    res = {"rect_sets": 0, "coverage": 0, "pass37": 0, "reps": 0, "osum": 0, "attach": 0, "att_budget": 0,
           "att_hand_a2z": 0, "att_psd": 0, "kept": 0, "batches": 0, "recounts": 0}
    sig35 = sigma(35)
    ATT = [(a_, b_) for a_ in range(14) for b_ in range(a_ + 1, 14) if a_ // 2 != b_ // 2]
    ZROW = np.zeros(35, dtype=np.int64)
    for i in U3:
        ZROW[i] = 1
    for i in V3:
        ZROW[10 + i] = 1
    keys = {}

    def cfg_only_image(cfg, g):
        return tuple(sorted(tp for tp, zp in zkey_image([(tp, 0) for tp in cfg], g, 0)))

    def treat(cfg):
        c = tuple(sorted(cfg))
        imgs = set(cfg_only_image(cfg, g) for g, sw in G)
        if c != min(imgs):
            return
        res["reps"] += 1
        res["osum"] += len(imgs)
        full = list(c) + [("Z",)] * h0
        A35 = start(35)
        for t, tp in enumerate(full):
            add_pair(A35, t, tp)
        A = start(37)
        A[:35, :35] = A35
        put_z(A, ZV, SZV)
        isA = [tp[0] == "A" for tp in full]
        R = np.zeros((len(ATT), 35), dtype=np.int64)
        for q, (a_, b_) in enumerate(ATT):
            R[q, :] = ZROW
            R[q, 21 + a_] = 1
            R[q, 21 + b_] = 1
        bad = orbit_counts_batch(A35, sig35, R)
        res["attach"] += len(ATT)
        res["att_budget"] += int(bad.sum())
        res["batches"] += 1
        check = [int(q) for q in np.flatnonzero(~bad)]
        if res["batches"] % 20 == 0:
            check += [res["batches"] % len(ATT), (7 * res["batches"]) % len(ATT)]
        for q in sorted(set(check)):              # explicit recount on the complete 37-vertex graph
            a_, b_ = ATT[q]
            A2 = A.copy()
            for w in (21 + a_, 21 + b_):
                A2[ZV, w] = A2[w, ZV] = 1
                A2[SZV, sig37[w]] = A2[sig37[w], SZV] = 1
            assert budget_violation(A2) == bool(bad[q]), "batch count differs from the explicit recount"
            res["recounts"] += 1
            if bad[q]:
                continue
            if isA[a_ // 2] and isA[b_ // 2]:
                res["att_hand_a2z"] += 1          # hand: a_2(z) <= 1
                continue
            if psd_rejected(A2, sig37):
                res["att_psd"] += 1
                continue
            res["kept"] += 1
            items = [(tp, (1 + (a_ % 2) if a_ // 2 == t else 1 + (b_ % 2) if b_ // 2 == t else 0))
                     for t, tp in enumerate(full)]
            k = zkey(items, G)
            keys[k] = keys.get(k, 0) + 1

    def finish(rs, cov):
        need = [2 - c for c in cov]
        if sum(need) != 2 * h1:
            return

        def wrec(es, nd, li, lk):
            if len(es) == h1:
                if not any(nd):
                    res["coverage"] += 1
                    cfg = [("A", U, V) for (U, V) in rs] + [("W", i, k) for (i, k) in es]
                    A = start(37)
                    for t, tp in enumerate(cfg):
                        add_pair(A, t, tp)
                    for t in range(len(cfg), 7):
                        add_pair(A, t, ("Z",))
                    put_z(A, ZV, SZV)
                    if not budget_violation(A):
                        res["pass37"] += 1
                        treat(cfg)
                return
            i = next((j for j in range(10) if nd[j]), None)
            if i is None:
                return
            for k in range(i + 1, 10):
                if i == li and k <= lk:
                    continue
                if nd[k]:
                    nd[i] -= 1; nd[k] -= 1
                    wrec(es + [(i, k)], nd, i, k)
                    nd[i] += 1; nd[k] += 1
        wrec([], need, -1, -1)

    def rrec(startidx, rs, cov):
        if len(rs) == h2:
            finish(rs, cov)
            return
        for a in range(startidx, len(rects)):
            if not rs and a % nparts != part:
                continue
            U, V = rects[a]
            if any(cov[i] >= 2 for i in U + V):
                continue
            rs2 = rs + [(U, V)]
            res["rect_sets"] += 1
            n = 23 + 2 * len(rs2)
            A = start(n)
            for t, (U_, V_) in enumerate(rs2):
                add_pair(A, t, ("A", U_, V_))
            put_z(A, n - 2, n - 1)
            if budget_violation(A):
                continue
            for i in U + V:
                cov[i] += 1
            rrec(a + 1, rs2, cov)
            for i in U + V:
                cov[i] -= 1
    rrec(0, [], [0] * 10)
    out = {"graph": name, "profile": [h2, h1, h0], "ztype": [list(U3), list(V3)], "part": part, "nparts": nparts,
           "group_order": len(G), "counts": res, "keys": [[repr(k), v] for k, v in sorted(keys.items())],
           "certificates": {"integer_vector": NCERT[0], "exact_elimination": NCERT[1]},
           "seconds": round(time.time() - t0, 1)}
    json.dump(out, open(outfile, "w"))
    print("part %d of %d: %s   [%.0f s]" % (part, nparts, res, time.time() - t0))


def step_merge_z(s1file, prefix, nparts, follow_prefix):
    s1 = json.load(open(s1file))
    name = s1["graph"]
    h2, h1, h0 = s1["profile"]
    U3, V3 = (tuple(t) for t in s1["ztype"])
    B = load_B(name)
    G = zgroup(B, U3, V3)
    parts = [json.load(open("%s_%dof%d.json" % (prefix, i, nparts))) for i in range(nparts)]
    tot = {}
    mine = set()
    for i, p in enumerate(parts):
        assert p["part"] == i and p["nparts"] == nparts and p["graph"] == name and p["profile"] == [h2, h1, h0]
        assert tuple(tuple(t) for t in p["ztype"]) == (U3, V3)
        for k, v in p["counts"].items():
            tot[k] = tot.get(k, 0) + v
        mine |= set(k for k, v in p["keys"])
    ref = set()
    for b in s1["bases"]:
        items = []
        for t, tp in enumerate(b["pairs"]):
            zp = 0
            for a_ in b["zn"]:
                if a_ // 2 == t:
                    zp = 1 + (a_ % 2)
            if tp[0] == "A":
                items.append((("A", tuple(tp[1]), tuple(tp[2])), zp))
            elif tp[0] == "W":
                items.append((("W", tp[1], tp[2]), zp))
            else:
                items.append((("Z",), zp))
        ref.add(repr(zkey(items, G)))
    print("%s profile (%d,%d,%d) z = %s ; %s, second program, stage 1 (%d parts): |G_z| with the exchange = %d (first "
          "program, without it: %d)" % (name, h2, h1, h0, U3, V3, nparts, len(G), s1["group_order"]))
    print("   rectangle sets tested %d; right coverage %d; passing the count on 37 vertices (z not attached) %d; "
          "representatives %d (orbit sizes %d, must equal the previous number)" % (
              tot["rect_sets"], tot["coverage"], tot["pass37"], tot["reps"], tot["osum"]))
    print("   attachments of z tested %d: rejected by the count %d, by the hand filter a_2(z) <= 1: %d, by PSD (exact) "
          "%d, kept %d" % (tot["attach"], tot["att_budget"], tot["att_hand_a2z"], tot["att_psd"], tot["kept"]))
    print("   kept bases as classes (canonical keys): this program %d, first program %d (from %d bases); in the first "
          "list only: %d; in this list only: %d" % (len(mine), len(ref), len(s1["bases"]), len(ref - mine), len(mine - ref)))
    ok1 = (mine == ref and tot["osum"] == tot["pass37"])
    print("   STAGE 1 AGREES: %s" % ok1)
    if follow_prefix:
        ftot = {}
        nbf = 0
        cert = [0, 0]
        missing = []
        for i in range(nparts):
            fn = "%s_%dof%d.json" % (follow_prefix, i, nparts)
            if not os.path.exists(fn):
                missing.append(i)
                continue
            f = json.load(open(fn))
            if f.get("partial"):
                missing.append(i)
                continue
            nbf += f["bases_followed"]
            cert[0] += f["certificates"]["integer_vector"]; cert[1] += f["certificates"]["exact_elimination"]
            for k, v in f["totals"].items():
                ftot[k] = max(ftot.get(k, 0), v) if k == "free_deepest" else ftot.get(k, 0) + v
        print("   stage 2 re-traversed: bases %d (stage-1 list: %d); parts not finished: %s" % (
            nbf, len(s1["bases"]), missing if missing else "none"))
        print("   totals: %s; certificates: integer vector %d, exact elimination %d" % (ftot, cert[0], cert[1]))
        if ftot.get("rank_nodes", 0):
            print("   nodes rejected by the rank bound in the first program: %d; closed here by the own search (no "
                  "rank bound): %d, with %d more nodes, deepest node with %d orbits of X_2 placed; closed here by an "
                  "own exact rank computation: %d" % (
                      ftot["rank_nodes"], ftot.get("rank_nodes_closed_by_own_search", 0), ftot.get("free_nodes", 0),
                      ftot.get("free_deepest", 0), ftot.get("rank_nodes_closed_by_rank_bound", 0)))
        print("   STAGE 2 AGREES AT EVERY NODE, 0 complete, all bases: %s" % (
            not missing and nbf == len(s1["bases"]) and ftot.get("complete", 0 if not s1["bases"] else 1) == 0))


# ------------------------------------------------------------------ step 2

def follow(B, A21, defi, rec, plan, ztype):
    pairs = rec["pairs"]
    h0 = sum(1 for tp in pairs if tp[0] == "Z")
    nb = 37 if ztype else 35
    A0 = np.zeros((nb, nb), dtype=np.int64)
    A0[:21, :21] = A21
    units = dict(defi)

    def use(X):
        units[X] -= 1
        assert units[X] >= 0
        if units[X] == 0:
            del units[X]
    Ap = set()
    kind = {}
    for t, tp in enumerate(pairs):
        add_pair(A0, t, tp)
        kind[21 + 2 * t] = kind[22 + 2 * t] = tp[0]
        if tp[0] == "A":
            use(tuple(tp[1])); use(tuple(tp[2]))
            Ap |= {21 + 2 * t, 22 + 2 * t}
    SIG = sigma(nb)
    Z = ()
    if ztype:
        # own layout: z = 35, sigma z = 36 (the first program puts them at 21, 22)
        U3, V3 = ztype
        for i in U3:
            A0[35, i] = A0[i, 35] = 1; A0[36, 10 + i] = A0[10 + i, 36] = 1
        for i in V3:
            A0[35, 10 + i] = A0[10 + i, 35] = 1; A0[36, i] = A0[i, 36] = 1
        for T3 in (U3, V3):
            for pr in itertools.combinations(T3, 2):
                use(pr)
        for a in rec["zn"]:
            w = 21 + a
            A0[35, w] = A0[w, 35] = 1
            A0[36, SIG[w]] = A0[SIG[w], 36] = 1
        Z = (35, 36)
    assert not budget_violation(A0)
    NPV = list(range(21, 35))
    cap = {}
    for w in NPV:
        a3 = int(A0[w, 35] + A0[w, 36]) if ztype else 0
        if not ztype:
            cap[w] = {"A": 4 - h0, "W": 8 - h0, "Z": min(10, 12 - h0)}[kind[w]]
        else:
            cap[w] = {"A": 3 - h0 - 2 * a3, "W": 7 - h0 - 2 * a3, "Z": min(11 - h0 - 2 * a3, (20 - 3 * a3) // 2)}[kind[w]]
    for v in Z:
        cap[v] = 1 - sum(int(A0[v, w]) for w in Ap)
    stat = {"nodes": 0, "cands": 0, "budget": 0, "psd": 0, "kept": 0, "complete": 0, "impossible": 0,
            "rank_nodes": 0, "rank_nodes_closed_by_own_search": 0, "rank_nodes_closed_by_rank_bound": 0,
            "holes_located_by_own_rank": 0, "free_nodes": 0, "free_cands": 0, "free_budget": 0, "free_psd": 0,
            "free_deepest": 0, "free_complete": 0, "free_capped": 0}
    if any(c < 0 for c in cap.values()):
        stat["impossible"] = 1
        assert rec.get("impossible"), "the first program did not flag this base as impossible"
        return stat, 0
    smax = 4 if ztype else 5
    # all N0 in the order of the first program: (w1, w2) increasing, then no z / z / sigma z
    n0all = []
    for a in range(14):
        for b in range(a + 1, 14):
            if a // 2 == b // 2:
                continue
            for zc in ((),) + tuple((v,) for v in Z):
                n0all.append((21 + a, 21 + b) + zc)
    norb = sum(units.values()) // 2
    plan = iter(plan)
    paircache = {}
    singlecache = {}

    def row0(o):
        U, V, N0 = o
        r = np.zeros(nb, dtype=np.int64)
        for i in U:
            r[i] = 1
        for i in V:
            r[10 + i] = 1
        for w in N0:
            r[w] = 1
        return r

    def extend(A, sig, row):
        n = A.shape[0]
        Bm = np.zeros((n + 2, n + 2), dtype=np.int64)
        Bm[:n, :n] = A
        rs = row[np.array(sig)]
        Bm[n, :n] = row; Bm[:n, n] = row
        Bm[n + 1, :n] = rs; Bm[:n, n + 1] = rs
        return Bm, sig + [n + 1, n]

    # single orbits on the base: exact common-neighbour counts (int64), for all (V, N0) of a unit at once.
    # For a new word s with neighbourhood row r (and sigma s with row r o sigma), a pair with too many common
    # neighbours in base + {s, sigma s} is one of: (s, old v): (r A0)_v + r_v > 2;  (s, sigma s): r . (r o sigma) > 2;
    # (old u, old v) both in N(s): C0_uv + A0_uv + 1 + [both in N(sigma s)] > 2  (C0 = A0^2); the pairs containing
    # sigma s are the images of these.  Each batch is compared with the explicit recount on a sample of its rows.
    C0A = A0 @ A0 + A0
    Q1 = (C0A >= 2).astype(np.int64); np.fill_diagonal(Q1, 0)
    Q2 = (C0A >= 1).astype(np.int64); np.fill_diagonal(Q2, 0)
    SIGA = np.array(SIG)
    batched = set()
    allunits = sorted(units)

    def batch_singles(U0):
        keys = [(U0, V, N0) for V in allunits if V != U0 for N0 in n0all]
        R = np.array([row0(o) for o in keys], dtype=np.int64)
        RS = R[:, SIGA]
        bad = ((R @ A0 + R) > 2).any(1)
        bad |= (R * RS).sum(1) > 2
        bad |= ((R @ Q1) * R).sum(1) > 0
        T = R * RS
        bad |= ((T @ Q2) * T).sum(1) > 0
        for o, b in zip(keys, bad.tolist()):
            singlecache[o] = not b
        step = max(1, len(keys) // 12)
        for a in list(range(0, len(keys), step)) + np.flatnonzero(~bad)[:6].tolist():
            Bm, _ = extend(A0, SIG, R[a])
            assert budget_violation(Bm) == bool(bad[a]), "batch count differs from the explicit recount"
            stat["recount_checks"] = stat.get("recount_checks", 0) + 1
        batched.add(U0)

    def single_budget_ok(o):
        if o[0] not in batched:
            batch_singles(o[0])
        return singlecache[o]

    def pair_budget_ok(o1, o2, pat):
        key = (o1, o2, pat)
        r = paircache.get(key)
        if r is None:
            Bm, sg = extend(A0, SIG, row0(o1))
            row = np.zeros(nb + 2, dtype=np.int64)
            row[:nb] = row0(o2)
            if pat & 1:
                row[nb] = 1
            if pat & 2:
                row[nb + 1] = 1
            B2, _ = extend(Bm, sg, row)
            r = not budget_violation(B2)
            paircache[key] = r
        return r

    def gen_cands(U0, orbs, caps, degs, cnt, remaining, st):
        """all candidates (V, N0, cap, patterns to the earlier orbits) of the unit U0 at a node, in the order of the
        first program; the ones left out are rejected exactly (caps of the hand part, or a count on the base plus
        one or two orbits)"""
        t = len(orbs)
        rem2 = dict(remaining)
        rem2[U0] -= 1
        if rem2[U0] == 0:
            del rem2[U0]
        cands = []
        for V in sorted(rem2):
            if V == U0:
                continue
            for N0 in n0all:
                zc = N0[2:]
                tg = smax - 2 * len(zc) - sum(1 for w in N0[:2] if w in Ap)
                if tg < 0:
                    continue
                if any(cnt[w] >= cap[w] for w in N0) or any(cnt[SIG[w]] >= cap[SIG[w]] for w in N0):
                    continue
                onew = (U0, V, N0)
                if not single_budget_ok(onew):
                    st["budget"] += 1            # exact: a count on the base plus this orbit
                    continue
                allowed = []
                ok = True
                for i in range(t):
                    room = caps[i] - degs[i]
                    pats = [pat for pat in (0, 1, 2, 3)
                            if (pat & 1) + (pat >> 1) <= min(room, tg) and pair_budget_ok(orbs[i], onew, pat)]
                    if not pats:
                        ok = False
                        break
                    allowed.append(pats)
                if not ok:
                    st["budget"] += 1            # exact: counts on the base plus two orbits, or the caps
                    continue
                for choice in itertools.product(*allowed):
                    used = sum((pat & 1) + (pat >> 1) for pat in choice)
                    if used <= tg:
                        cands.append((V, N0, tg, choice, used))
        return cands

    def test_cands(A, sig, U0, cands, st):
        """every candidate is rejected exactly (budget count on the whole graph, or PSD certificate) or kept"""
        good = []
        n = A.shape[0]
        for (V, N0, tg, choice, used) in cands:
            row = np.zeros(n, dtype=np.int64)
            row[:nb] = row0((U0, V, N0))
            for i, pat in enumerate(choice):
                if pat & 1:
                    row[nb + 2 * i] = 1
                if pat & 2:
                    row[nb + 2 * i + 1] = 1
            Bm, sg = extend(A, sig, row)
            if budget_violation(Bm):
                st["budget"] += 1
            elif psd_rejected(Bm, sg):
                st["psd"] += 1
            else:
                good.append((V, N0, tg, choice, used, Bm, sg))
        return good

    def child_state(U0, V, N0, tg, choice, used, orbs, caps, degs, cnt, remaining):
        rem3 = dict(remaining)
        for X in (U0, V):
            rem3[X] -= 1
            if rem3[X] == 0:
                del rem3[X]
        c2 = dict(cnt)
        for w in N0:
            c2[w] += 1; c2[SIG[w]] += 1
        d2 = [degs[i] + (pat & 1) + (pat >> 1) for i, pat in enumerate(choice)]
        return orbs + [(U0, V, N0)], caps + [tg], d2 + [used], c2, rem3

    def free(A, sig, orbs, caps, degs, cnt, remaining, fs):
        """exploration WITHOUT plan (below a node that the first program rejected by the rank bound): the unit with
        the fewest candidates is treated (any choice is valid: some vertex of X_2 not yet placed realises it); no rank
        test here."""
        t = len(orbs)
        fs["deepest"] = max(fs["deepest"], t)
        if t == norb:
            fs["complete"] += 1
            return
        if fs["nodes"] >= FREE_CAP or time.process_time() - fs["t0"] > FREE_SECONDS:
            fs["capped"] = True
            return
        fs["nodes"] += 1
        best = None
        for U0 in sorted(remaining):
            cands = gen_cands(U0, orbs, caps, degs, cnt, remaining, fs)
            if best is None or len(cands) < len(best[1]):
                best = (U0, cands)
            if not cands:
                break
        U0, cands = best
        fs["cands"] += len(cands)
        good = test_cands(A, sig, U0, cands, fs)
        fs["kept"] += len(good)
        for (V, N0, tg, choice, used, Bm, sg) in good:
            if fs["capped"]:
                return
            free(Bm, sg, *child_state(U0, V, N0, tg, choice, used, orbs, caps, degs, cnt, remaining), fs)

    def dfs(A, sig, orbs, caps, degs, cnt, remaining):
        t = len(orbs)
        if t == norb:
            stat["complete"] += 1
            return
        pl = next(plan)
        assert pl[0] == t, "plan out of step"
        U0 = (pl[1], pl[2])
        assert U0 in remaining
        stat["nodes"] += 1
        cands = gen_cands(U0, orbs, caps, degs, cnt, remaining, stat)
        stat["cands"] += len(cands)
        good = test_cands(A, sig, U0, cands, stat)
        assert len(good) == pl[4], "DISAGREEMENT with the plan at depth %d: kept %d, plan %d" % (t, len(good), pl[4])
        stat["kept"] += len(good)
        # children that the first program rejected by the rank bound: it wrote no plan below them.  New plans list
        # their positions (6th field).  For an old plan (5 fields) the position is found with an own exact rank
        # computation; this only says where the plan has a hole, it rejects nothing.
        holes = set(pl[5]) if len(pl) > 5 else None
        for pos, (V, N0, tg, choice, used, Bm, sg) in enumerate(good):
            if holes is not None:
                hole = pos in holes
            else:
                hole = rank_bound_violated(Bm, sg)
                stat["holes_located_by_own_rank"] += int(hole)
            state = child_state(U0, V, N0, tg, choice, used, orbs, caps, degs, cnt, remaining)
            if hole:
                stat["rank_nodes"] += 1
                fs = {"nodes": 0, "cands": 0, "budget": 0, "psd": 0, "kept": 0, "complete": 0, "deepest": 0,
                      "capped": False, "t0": time.process_time()}
                free(Bm, sg, *state, fs)
                stat["free_nodes"] += fs["nodes"]
                stat["free_cands"] += fs["cands"]
                stat["free_budget"] += fs["budget"]
                stat["free_psd"] += fs["psd"]
                stat["free_deepest"] = max(stat["free_deepest"], fs["deepest"])
                stat["free_complete"] += fs["complete"]
                stat["free_capped"] += int(fs["capped"])
                if not fs["capped"] and fs["complete"] == 0:
                    stat["rank_nodes_closed_by_own_search"] += 1      # no rank bound needed for this node
                else:
                    # the own search did not close the node: exact rank of both sigma-blocks of M1 against 22
                    assert rank_bound_violated(Bm, sg), "node rejected by rank in the first program, not closed here"
                    stat["rank_nodes_closed_by_rank_bound"] += 1
                continue
            dfs(Bm, sg, *state)

    dfs(A0, list(SIG), [], [], [], {w: 0 for w in NPV + list(Z)}, units)
    left = sum(1 for _ in plan)
    return stat, left


def step_follow(s1file, prefix, part, nparts, outfile, first, every, sub=(0, 1), only=None):
    s1 = json.load(open(s1file))
    name = s1["graph"]
    ztype = tuple(tuple(t) for t in s1["ztype"]) if s1.get("ztype") else None
    B = load_B(name)
    A21 = support21(B)
    defi = deficient(B)
    recs = {}
    for line in open("%s_%dof%d.jsonl" % (prefix, part, nparts)):
        r = json.loads(line)
        if not r.get("timeout") and not r.get("error"):
            recs[r["i"]] = r
    todo = sorted(recs)
    if every > 1:
        todo = [i for i in todo if (i // nparts) % every == 0]
    todo = todo[sub[0]::sub[1]]          # sub=j/m: the bases of rank j mod m of this part (to share a part)
    if only is not None:
        todo = [i for i in todo if i in only]
    if first:
        todo = todo[:first]
    tot = {}
    nb = 0
    t0 = time.process_time()
    for i in todo:
        r = recs[i]
        base = dict(s1["bases"][i])
        if r.get("impossible"):
            base["impossible"] = True
        st, left = follow(B, A21, defi, base, r.get("plan", []), ztype)
        assert left == 0, "plan lines left"
        assert st["complete"] == r["complete"]
        if not r.get("impossible"):
            assert st["nodes"] == sum(r["visited"]) and st["kept"] == sum(r["kept"]), (i, st, r["visited"], r["kept"])
            assert st["rank_nodes"] == sum(r["rej_rank"]), (i, st["rank_nodes"], r["rej_rank"])
        for k, v in st.items():
            tot[k] = max(tot.get(k, 0), v) if k == "free_deepest" else tot.get(k, 0) + v
        nb += 1
        if nb % 50 == 0:
            json.dump({"partial": True, "bases": nb, "totals": tot}, open(outfile, "w"))
    out = {"stage1": s1file, "prefix": prefix, "part": part, "nparts": nparts, "first": first, "every": every,
           "sub": list(sub), "indices_sha1": __import__("hashlib").sha1(repr(todo).encode()).hexdigest(),
           "bases_followed": nb, "bases_in_part": len(recs), "totals": tot,
           "certificates": {"integer_vector": NCERT[0], "exact_elimination": NCERT[1]},
           "cpu": round(time.process_time() - t0, 1)}
    json.dump(out, open(outfile, "w"))
    print(json.dumps(out))


if sys.argv[1] == "bases":
    # python in_verify.py bases <graph> <h2> <h1> <h0> <out.json> [part=i/n]
    part, nparts = 0, 1
    for a in sys.argv[7:]:
        if a.startswith("part="):
            part, nparts = (int(t) for t in a[5:].split("/"))
    step_bases(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], part, nparts)
elif sys.argv[1] == "basesz":
    # python in_verify.py basesz <graph> <h2> <h1> <h0> <a,b,c:d,e,f> <out.json> [part=i/n]
    part, nparts = 0, 1
    for a in sys.argv[8:]:
        if a.startswith("part="):
            part, nparts = (int(t) for t in a[5:].split("/"))
    u_, v_ = sys.argv[6].split(":")
    step_bases_z(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
                 tuple(int(t) for t in u_.split(",")), tuple(int(t) for t in v_.split(",")), sys.argv[7], part, nparts)
elif sys.argv[1] == "mergez":
    # python in_verify.py mergez <stage1.json> <basesz prefix> <nparts> [<follow prefix>]
    step_merge_z(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None)
elif sys.argv[1] == "merge":
    # python in_verify.py merge <stage1.json> <bases prefix> <nparts> [<follow prefix>]
    step_merge(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None)
else:
    first = 0
    every = 1
    sub = (0, 1)
    only = None
    for a in sys.argv[7:]:
        if a.startswith("first="):
            first = int(a[6:])
        if a.startswith("every="):
            every = int(a[6:])
        if a.startswith("sub="):
            sub = tuple(int(t) for t in a[4:].split("/"))
        if a.startswith("only="):
            only = set(int(t) for t in a[5:].split(","))
    step_follow(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], first, every, sub, only)
