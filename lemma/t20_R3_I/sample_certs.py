# T20 round 3, case I, n_3 = 0: a small sample of rejection records with SMALL-SUPPORT certificates, for reading by hand.
# For a few bases of a stage-1 file (those whose search tree is deepest), the search of eng6 is re-run with its
# certificate option; every PSD rejection of the exact steps is collected with the complete graph concerned
# (base + X_2 orbits placed + the failing candidate).  Rejections of single orbits on the base ("placed = 0") are
# produced separately (eng5.Node.psd_fail on the base).
# For each record the support of the certificate is then reduced: on each of the four sigma-blocks
#   M1 odd  : G = 3I - A[R,R] + A[R,sigma R]                 (x^T M1 x = 18 c^T G c for x = sum c_O (e_v - e_sigma v))
#   M2 odd  : 7I - G                                           (x^T M2 x = 22 c^T (7I - G) c)
#   M1 even : rows/columns p and the orbits, entries of M1 on the vectors e_p, e_v + e_sigma v
#   M2 even : the same with M2
# a minimal set T of coordinates is searched (greedy removal, several orders) such that the principal submatrix on T
# is not positive semidefinite, and an integer vector c on T with negative form is computed (checked in Python
# integers).  The record gives the corresponding vector x on the VERTICES and q = x^T M x < 0, recomputed here
# from the 0/1 adjacency matrix alone, with M = M1 = 27 I - 9 A + J or M = M2 = 44 I + 11 A - 2 J.
# The records kept: for each number of placed orbits (0, 1, 2, 3, 4) the ones with the smallest support.
# usage: python sample_certs.py <stage1.json> <stage2 prefix> <nparts> <out.jsonl> [per_level=2] [bases=4]
import sys, json, os, random
import numpy as np
import eng5, eng6, cases6, r3lib

s1file, prefix, nparts, outfile = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
per_level, nbases = 2, 4
for a in sys.argv[5:]:
    if a.startswith("per_level="):
        per_level = int(a[10:])
    if a.startswith("bases="):
        nbases = int(a[6:])
s1 = json.load(open(s1file))
name = s1["graph"]
m = r3lib.load_B(name)
recs = []
for part in range(nparts):
    for line in open("%s_%dof%d.jsonl" % (prefix, part, nparts)):
        recs.append(json.loads(line))
recs.sort(key=lambda r: (-len(r["visited"]), -sum(r["visited"]), r["i"]))
chosen = [r["i"] for r in recs[:nbases]]
random.seed(20)
BLOCKS = (("M1", "odd"), ("M2", "odd"), ("M1", "even"), ("M2", "even"))


def pform(B, x):
    return sum(x[a] * sum(B[a][b] * x[b] for b in range(len(x)) if x[b]) for a in range(len(x)) if x[a])


def exact_cert(B):
    """integer vector with negative form on the integer matrix B (list of lists), small entries preferred; or None"""
    w, V = np.linalg.eigh(np.array(B, dtype=np.float64))
    if w[0] > -1e-9:
        return None
    v = V[:, 0]
    mx = float(np.abs(v).max())
    best = None
    for sc in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 24, 30, 40, 60, 100, 300, 1000, 10 ** 4, 10 ** 6):
        x = [int(round(float(t) * sc / mx)) for t in v]
        if any(x) and pform(B, x) < 0:
            best = x
            break
    return best


def reduce_support(Bk):
    """minimal T (by inclusion) with Bk[T,T] not PSD; several random removal orders; returns the smallest found"""
    n = Bk.shape[0]
    Bf = Bk.astype(np.float64)
    if np.linalg.eigvalsh(Bf)[0] > -1e-7:
        return None
    best = None
    for trial in range(40):
        T = list(range(n))
        order = list(range(n))
        random.shuffle(order)
        for a in order:
            T2 = [t for t in T if t != a]
            if T2 and np.linalg.eigvalsh(Bf[np.ix_(T2, T2)])[0] < -1e-7:
                T = T2
        if best is None or len(T) < len(best):
            best = T
    return best


def labels(n):
    lab = {}
    for i in range(10):
        lab[i] = "x%d" % i
        lab[10 + i] = "y%d" % i
    lab[20] = "p"
    for t in range(7):
        lab[21 + 2 * t] = "w%d" % t
        lab[22 + 2 * t] = "sw%d" % t
    for j in range((n - 35) // 2):
        lab[35 + 2 * j] = "s%d" % j
        lab[36 + 2 * j] = "ss%d" % j
    return lab


def make_record(bi, A, sig, engine_block):
    """A: complete graph (numpy int64), last two vertices = the failing candidate and its mate"""
    n = A.shape[0]
    assert not r3lib.budget_viol(A), "the failing graph has a budget violation (not expected for a PSD rejection)"
    node = eng5.Node(A.copy(), list(sig))
    node.prepare()
    reps, fixed = node.reps, node.fixed
    best = None
    for bidx, (mat, par) in enumerate(BLOCKS):
        Bk = node.blocks[bidx].B
        T = reduce_support(Bk)
        if T is None:
            continue
        sub = Bk[np.ix_(T, T)].tolist()
        c = exact_cert(sub)
        if c is None:
            continue
        if best is None or len(T) < len(best[2]):
            best = (mat, par, T, c, sub)
    assert best is not None
    mat, par, T, c, sub = best
    coords = reps if par == "odd" else fixed + reps
    x = [0] * n
    for t, ct in zip(T, c):
        v = coords[t]
        if par == "odd":
            x[v] += ct; x[sig[v]] -= ct
        else:
            x[v] += ct
            if sig[v] != v:
                x[sig[v]] += ct
    Al = A.tolist()
    sx = sum(x)
    q = 0
    for a in range(n):
        if x[a]:
            sa = sum(x[b] for b in range(n) if Al[a][b])
            q += x[a] * ((27 * x[a] - 9 * sa + sx) if mat == "M1" else (44 * x[a] + 11 * sa - 2 * sx))
    assert q < 0
    qb = pform(sub, c)
    assert qb < 0
    lab = labels(n)
    norb = (n - 35) // 2
    orbits = []
    for j in range(norb):
        s = 35 + 2 * j
        row = Al[s]
        orbits.append({"s": s, "sigma_s": s + 1, "U": [i for i in range(10) if row[i]],
                       "V": [i for i in range(10) if row[10 + i]],
                       "nbrs_in_Np": [lab[v] for v in range(21, 35) if row[v]],
                       "nbrs_in_earlier_orbits": [lab[v] for v in range(35, s) if row[v]]})
    pairs = []
    for t, tp in enumerate(s1["bases"][bi]["pairs"]):
        w = 21 + 2 * t
        pairs.append({"pair": t, "kind": {"A": "X_2", "W": "X_1", "Z": "X_0"}[tp[0]], "w": w, "sigma_w": w + 1,
                      "w_nbrs_in_S": [lab[v] for v in range(20) if Al[w][v]],
                      "sigma_w_nbrs_in_S": [lab[v] for v in range(20) if Al[w + 1][v]]})
    return {"graph": name, "profile": s1["profile"], "base_index": bi, "placed": norb - 1,
            "n_vertices": n, "pairs_of_Np": pairs, "X2_orbits_placed": orbits[:-1], "failing_candidate": orbits[-1],
            "sigma": list(sig), "adjacency": ["".join(map(str, r)) for r in Al],
            "matrix": mat, "block": par, "support_size": len(T),
            "support": [lab[coords[t]] for t in T], "block_matrix_on_support": sub, "c": c, "block_form": qb,
            "x": x, "q": q, "engine_rejected_on": engine_block}


cands = {}
for bi in chosen:
    prob = cases6.CaseIN6(name, s1["bases"][bi])
    tag = "tmp_sample_certs_b%d" % bi
    out = eng6.run(prob, 0, 1, 3600, 99, tag, save_certs=10 ** 6, files=True)
    assert not out["timeout"] and not out["survivors"]
    for line in open("%s_certs_0of1.jsonl" % tag):
        cr = json.loads(line)
        A = np.array([[int(ch) for ch in row] for row in cr["A"]], dtype=np.int64)
        lev = (A.shape[0] - 35) // 2 - 1
        cands.setdefault(lev, []).append((bi, A, cr["sig"], cr["block"]))
    for suf in ("_certs_0of1.jsonl", "_0of1.json", "_0of1.log"):
        if os.path.exists(tag + suf):
            os.remove(tag + suf)
    # single orbits on the base (placed = 0): the float-rejected ones, certified exactly
    root = eng5.Node(prob.AB.copy(), prob.sig)
    root.prepare()
    st = eng5.Counter()
    ul = sorted(prob.units)
    k = 0
    for U in ul:
        for V in ul:
            if U == V:
                continue
            for N0, tgt in prob.options(U, V):
                row = np.zeros(35, dtype=np.int64)
                for i in U:
                    row[i] = 1
                for i in V:
                    row[10 + i] = 1
                for w in N0:
                    row[w] = 1
                r = root.psd_fail(row, 0, st)
                if r is not None:
                    k += 1
                    if k % 7 == 0:                         # a spread sample of the single-orbit rejections
                        ch = root.child(row, 0)
                        cands.setdefault(0, []).append((bi, ch.A, ch.sig, r[0]))
out_records = []
summary = {}
for lev in sorted(cands):
    lst = cands[lev]
    random.shuffle(lst)
    made = [make_record(bi, A, sig, blk) for (bi, A, sig, blk) in lst[:90]]
    made.sort(key=lambda r: (r["support_size"], max(abs(t) for t in r["c"]), r["base_index"]))
    pick = []
    seen = set()
    for r in made:                                         # the smallest supports; no two records with the same support
        key = (r["base_index"], tuple(r["support"]), r["matrix"], r["block"])
        if len(pick) < per_level and key not in seen:
            pick.append(r); seen.add(key)
    out_records += pick
    summary[lev] = {"rejections_collected": len(lst), "examined": len(made),
                    "support_sizes_examined": sorted(r["support_size"] for r in made),
                    "kept": [r["support_size"] for r in pick]}
header = {"README": (
    "T20 round 3, case I (k = 0), n_3 = 0, graph %s, profile %s: sample of EXACT rejection records, one JSON object per "
    "line after this one.  Vertices: 0..9 = x_0..x_9 (S+), 10..19 = y_0..y_9 (S-, y_i = sigma x_i), 20 = p (fixed by "
    "sigma), 21 + 2t and 22 + 2t = the two vertices w_t, sigma w_t of the pair t of N(p) (t = 0..6), 35 + 2j and 36 + 2j "
    "= s_j, sigma s_j, the j-th orbit of X_2 outside N(p) in the order of placement; the LAST orbit is the failing "
    "candidate.  x_i ~ y_j iff B_ij = 1 (B below).  'adjacency' = the complete induced graph on these n vertices (row "
    "strings); 'sigma' = the involution as a list.  The graph has no pair of vertices with too many common neighbours "
    "(the candidate passed the budget counts); it is rejected because M = M1 = 27 I - 9 A + J (if 'matrix' = 'M1') or "
    "M = M2 = 44 I + 11 A - 2 J ('M2'), restricted to these n vertices, is not positive semidefinite: 'x' is an integer "
    "vector on the n vertices with x^T M x = 'q' < 0 (recomputed from 'adjacency' alone, Python integers).  The "
    "certificate was reduced to a small set of sigma-orbits: 'support' = their names (x_i = orbit {x_i, y_i}, w_t = "
    "pair t of N(p), s_j = X_2 orbit j, p), 'block' = 'odd' (x = sum c_O (e_v - e_sigma v); then x^T M1 x = 18 c^T G c "
    "with G = 3I - A[R,R] + A[R,sigma R] the Gram matrix of the frame vectors, and x^T M2 x = 22 c^T (7I - G) c) or "
    "'even' (x = c_p e_p + sum c_O (e_v + e_sigma v)); 'block_matrix_on_support' = that block restricted to the "
    "support, 'c' the integer vector, 'block_form' = c^T (block) c < 0.  The support is minimal by inclusion (removing "
    "any orbit leaves a positive semidefinite submatrix, floating-point check), not proved minimum.  'placed' = number "
    "of X_2 orbits placed before the failing candidate (0 = a single orbit on the base S u N[p]).  'pairs_of_Np': kind "
    "X_2 / X_1 / X_0 = d(w) = 2 / 1 / 0.  'engine_rejected_on' = the block on which the search engine found its own "
    "(dense) certificate." % (name, tuple(s1["profile"]))),
    "B": m, "stage1_file": os.path.basename(s1file), "bases_sampled": chosen, "per_level_summary": summary}
with open(outfile, "w", newline="\n") as f:
    f.write(json.dumps(header) + "\n")
    for r in out_records:
        f.write(json.dumps(r, separators=(",", ":")) + "\n")
print("bases sampled:", chosen)
for lev in sorted(summary):
    print("placed %d: PSD rejections collected %d, examined %d, minimal supports found %s, kept %s" % (
        lev, summary[lev]["rejections_collected"], summary[lev]["examined"], summary[lev]["support_sizes_examined"],
        summary[lev]["kept"]))
print("records written:", len(out_records), "file size", os.path.getsize(outfile), "bytes")
