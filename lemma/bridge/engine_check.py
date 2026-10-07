"""Check of the engine-side definitions used by the bridge, on real data: envelope 011 and the 400 historical pairs of the dossier
DOSSIER_WAGNER_2026-10-04 (SOURCE_011_SAMPLE_PAIRS.json, with the 363 exact Y = 13 witnesses of PAIRES_011_TEMOINS_Y13.json).

Uses the package's own lattice_data / min97_witness (scripts/frame_dfs_next.py) and the deferral rule's own witness()
(REPO/q/defer_consumer.py), unchanged. Nothing is written outside this folder (numba cache redirected, no .pyc).

  1. R, X3, X4 of lattice_data are the vectors of U of norm 2, 3, 4 (one per +- pair), G is the Gram matrix of the basis B (exact
     recomputation from B), U is integral and unimodular.
  2. For every pair: y1, y2 in U exactly, norms 7, orthogonal.
  3. E(v) = 7 N(v) - (v,y1)^2 - (v,y2)^2 equals 7 |pi(v)|^2 with pi(v) = v - ((v,y1) y1 + (v,y2) y2)/7 computed in exact rationals
     in ambient coordinates; 7 pi(v) is a vector of U orthogonal to y1, y2.
  4. K = U cap {y1,y2}^perp has determinant 49 (so pi(U) = K*, of index 49 over K, and Z y1 + Z y2 is primitive in U).
  5. Over all vectors of norm <= 4:  E in {1..7} never occurs;  E = 8 <=> (N,Y) in {(3,13),(4,20)};  E = 9 <=> (N,Y) = (2,5);
     E = 10 <=> (N,Y) in {(2,4),(4,18)}.  Coset structure checked at norm 5 on a few pairs:
       #{norm 5, E = 9} = #{roots, Y = 5},   #{norm 5, E = 10} = #{roots, Y = 4} + 2 #{norm 4, Y = 18},   #{norm 4, E = 8} = #{norm 3, Y = 13}.
  6. min97_witness fires on exactly the 363 pairs of the dossier; on the other pairs, Emin and what defer_consumer.witness() answers.
Usage: python engine_check.py"""
import sys, os, json, time, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["NUMBA_CACHE_DIR"] = os.path.join(HERE, "numba_cache"); sys.dont_write_bytecode = True
SP = os.path.dirname(HERE); PKG = os.path.join(SP, "pkgfull"); REPO = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws"
DOS = os.path.join(SP, "dossiers", "DOSSIER_WAGNER_2026-10-04")
from fractions import Fraction as F
import numpy as np
argv0 = sys.argv[:]
sys.argv = ["defer_consumer.py", PKG, "011", "-", os.path.join(HERE, "unused.jsonl"), "0"]
sys.path.insert(0, os.path.join(REPO, "q"))
import defer_consumer as DC                                              # import only: its __main__ block is not run
sys.argv = argv0
FD = DC.FD
sys.path.insert(0, os.path.join(PKG, "external_runs", "c1_96a94fe", "code"))
from envelope_trap import hnf_rows

random.seed(7); OUT = {}; t0 = time.time()
Urec = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "011.json")))
assert Urec == json.load(open(os.path.join(DOS, "SOURCE_U_011.json"))), "U 011 of the package differs from the dossier copy"
L = FD.lattice_data(Urec["gens"], F(1)); G = L["G"]; B = L["B"]
Bq = [[F(x) for x in row] for row in B]
# 1. exact Gram, unimodular, shells
Gex = [[sum(a * b for a, b in zip(u, v)) for v in Bq] for u in Bq]
assert all(Gex[i][j] == int(G[i, j]) for i in range(24) for j in range(24))


def det_int(M):
    M = [[int(x) for x in r] for r in M]; n = len(M); last = 1; sign = 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if M[i][k]), None)
        if p is None: return 0
        if p != k: M[k], M[p] = M[p], M[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n): M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // last
        last = M[k][k]
    return sign * M[-1][-1]


assert det_int(G) == 1
nrm = lambda X: np.einsum("ij,jk,ik->i", X, G, X)
R, X3, X4 = L["R"], L["X3"], L["X4"]
assert (nrm(R) == 2).all() and (nrm(X3) == 3).all() and (nrm(X4) == 4).all()
OUT["lattice 011"] = {"roots (both signs)": 2 * len(R), "norm 3": 2 * len(X3), "norm 4": 2 * len(X4), "new-root pairs": len(L["S2"]),
                      "det G": 1, "odd": bool((np.diag(G) % 2).any()), "roots field of U file": Urec["roots"], "secs lattice_data": L["secs"]}
print(json.dumps(OUT["lattice 011"]), flush=True)
RG, X3G, X4G = R @ G, X3 @ G, X4 @ G
Bf = np.array([[float(x) for x in row] for row in B]); Binv = np.linalg.inv(Bf)

pairs = json.load(open(os.path.join(DOS, "SOURCE_011_SAMPLE_PAIRS.json")))
wit = json.load(open(os.path.join(DOS, "PAIRES_011_TEMOINS_Y13.json")))
no_wit = set(wit["pairs_without_found_witness"]); assert len(pairs) == 400 and len(no_wit) == 37


def conv(v):
    q = [F(x) for x in v]; cf = np.rint(np.array([float(x) for x in q]) @ Binv).astype(np.int64)
    assert [sum(int(cf[i]) * Bq[i][j] for i in range(24)) for j in range(24)] == q, "y not in U"
    return cf


def amb(c): return [sum(int(c[i]) * Bq[i][j] for i in range(24)) for j in range(24)]
def dotq(u, v): return sum(a * b for a, b in zip(u, v))


emin_types = collections.Counter(); emin_hist = collections.Counter(); rule = collections.Counter(); low = 0
fired = set(); mism = []; exact_checked = 0; detK = collections.Counter(); table = []
allE = collections.Counter()
for k, pr in enumerate(pairs):
    y1, y2 = conv(pr["y1"]), conv(pr["y2"])
    assert int(y1 @ G @ y1) == 7 and int(y2 @ G @ y2) == 7 and int(y1 @ G @ y2) == 0
    cls = {}
    for nm, XG in ((2, RG), (3, X3G), (4, X4G)):
        a = XG @ y1; b = XG @ y2; Y = a * a + b * b; E = 7 * nm - Y
        assert (E >= 0).all()
        for e, y in zip(E.tolist(), Y.tolist()):
            if 0 < e <= 12: cls[(e, nm, y)] = cls.get((e, nm, y), 0) + 1
    pos = sorted(cls); assert pos
    for (e, nm, y), c_ in cls.items(): allE[(e, nm, y)] += c_
    # 5. the realisations of the small values of E among the vectors of norm <= 4
    assert all(e >= 8 for e, _, _ in pos), ("E in 1..7", k, pos[0]); low += 0
    assert all((nm, y) in ((3, 13), (4, 20)) for e, nm, y in pos if e == 8)
    assert all((nm, y) == (2, 5) for e, nm, y in pos if e == 9)
    assert all((nm, y) in ((2, 4), (4, 18)) for e, nm, y in pos if e == 10)
    assert cls.get((8, 4, 20), 0) == cls.get((8, 3, 13), 0)                # norm-4 (2,4) <-> norm-3 (2,3): same coset of Zy1 + Zy2
    emin = pos[0][0]; emin_hist[emin] += 1
    emin_types[(emin, tuple(sorted((nm, y) for e, nm, y in pos if e == emin)))] += 1
    # 6. the engine's filter and the deferral rule
    x = FD.min97_witness(L, y1, y2)
    if x is not None: fired.add(k); assert int(x @ G @ x) == 3 and int(x @ G @ y1) ** 2 + int(x @ G @ y2) ** 2 == 13
    assert (x is not None) == (emin == 8)
    if (x is None) != (k in no_wit): mism.append(k)
    w = DC.witness(L, y1, y2)
    has5 = (2, 5) in {(nm, y) for e, nm, y in pos if e == 9}; has4 = (2, 4) in {(nm, y) for e, nm, y in pos if e == 10}
    assert (w == DC.DEF18) == has5 and (w == DC.DEF20) == ((not has5) and has4)
    if x is None:
        rule[w if w else "no root with Y in {5,4}"] += 1
        table.append({"pair": k, "Emin": emin, "roots Y=5": cls.get((9, 2, 5), 0), "roots Y=4": cls.get((10, 2, 4), 0),
                      "norm-4 Y=18": cls.get((10, 4, 18), 0), "rule": w, "historical nodes": sum(pr["nodes"]), "historical verdict": pr["verdict"]})
    # 3./4. exact projection and K on a subsample
    if k % 40 == 0 or k in (sorted(no_wit)[:3]):
        Y1, Y2 = amb(y1), amb(y2)
        for X in (R, X3, X4):
            for i in random.sample(range(len(X)), 8):
                v = amb(X[i]); a = dotq(v, Y1); b = dotq(v, Y2)
                pv = [vi - (a * p + b * q) / 7 for vi, p, q in zip(v, Y1, Y2)]
                assert 7 * dotq(pv, pv) == 7 * dotq(v, v) - a * a - b * b and dotq(pv, Y1) == 0 and dotq(pv, Y2) == 0
                c7 = 7 * X[i] - int(a) * y1 - int(b) * y2                 # 7 pi(v) in lattice coordinates: a vector of U
                assert amb(c7) == [7 * t for t in pv]; exact_checked += 1
        M = np.array([G @ y1, G @ y2]).T                                  # 24 x 2: (b_i, y_j)
        rows = [[int(M[i, j]) for j in range(2)] + [int(i == t) for t in range(24)] for i in range(24)]
        Hn = hnf_rows(rows); ker = np.array([r[2:] for r in Hn if not any(r[:2])], dtype=np.int64); assert len(ker) == 22
        assert not (ker @ G @ np.array([y1, y2]).T).any()
        detK[det_int(ker @ G @ ker.T)] += 1
assert not mism, mism
assert fired == set(range(400)) - no_wit
OUT["pairs"] = {"pairs": 400, "norms 7 and orthogonality": "all exact", "min97_witness fires": len(fired), "same set as the dossier's 363 witnesses": True,
                "Emin histogram (norm <= 4 vectors)": {str(e): c for e, c in sorted(emin_hist.items())},
                "realisers of Emin (Emin, [(norm, Y)...]) -> pairs": {str(k_): v for k_, v in sorted(emin_types.items())},
                "E in 1..7 found": 0, "exact projection checks": exact_checked, "det of K = U cap {y1,y2}^perp (sampled pairs)": {str(d): c for d, c in detK.items()},
                "deferral rule on the 37 pairs without Y=13 witness": dict(rule)}
OUT["all (E, norm, Y) classes with 0 < E <= 12 seen on the 400 pairs (counts of +- pairs of vectors)"] = {str(k_): v for k_, v in sorted(allE.items())}
OUT["the 37 pairs without Y=13 witness"] = table
print(json.dumps(OUT["pairs"], indent=1), flush=True)

# coset structure at norm 5 on three pairs (one of each kind if possible)
V5 = FD.one_per_pair(FD.short(G, 5) // 2); n5 = nrm(V5); X5 = V5[n5 == 5]; X5G = X5 @ G
OUT["norm-5 vectors (both signs)"] = 2 * len(X5)
todo = [t["pair"] for t in table if t["rule"] == DC.DEF18][:2] + [t["pair"] for t in table if t["rule"] == DC.DEF20][:2] + sorted(fired)[:1]
cos = []
for k in todo:
    y1, y2 = conv(pairs[k]["y1"]), conv(pairs[k]["y2"])
    def cnt(XG, nm):
        a = XG @ y1; b = XG @ y2; Y = a * a + b * b; return collections.Counter(zip((7 * nm - Y).tolist(), Y.tolist()))
    c2, c3, c4, c5 = cnt(RG, 2), cnt(X3G, 3), cnt(X4G, 4), cnt(X5G, 5)
    e9 = {y: c for (e, y), c in c5.items() if e == 9}; e10 = {y: c for (e, y), c in c5.items() if e == 10}; e8 = {y: c for (e, y), c in c5.items() if e == 8}
    assert set(e9) <= {26} and set(e10) <= {25} and not e8
    assert sum(e9.values()) == c2.get((9, 5), 0)
    assert sum(e10.values()) == c2.get((10, 4), 0) + 2 * c4.get((10, 18), 0)
    assert not any(0 < e < 8 for (e, y) in c5)
    # explicit: every norm-5 v with E = 9 is r +- y_j for a root r with Y = 5
    a = X5G @ y1; b = X5G @ y2; idx = np.flatnonzero(35 - a * a - b * b == 9); roots = {tuple(r) for r in R} | {tuple(-r) for r in R}
    for i in idx:
        sh = (y1 if abs(a[i]) == 5 else y2) * int(np.sign(a[i] if abs(a[i]) == 5 else b[i]))
        r = X5[i] - sh; assert tuple(r) in roots and int(r @ G @ y1) ** 2 + int(r @ G @ y2) ** 2 == 5
    cos.append({"pair": k, "roots Y=5": c2.get((9, 5), 0), "norm 5, E=9": sum(e9.values()), "roots Y=4": c2.get((10, 4), 0), "norm 4, Y=18": c4.get((10, 18), 0),
                "norm 5, E=10": sum(e10.values()), "norm 3, Y=13": c3.get((8, 13), 0), "norm 4, Y=20": c4.get((8, 20), 0)})
OUT["coset structure at norm 5 (counts of +- pairs)"] = cos
print(json.dumps(cos, indent=1))
OUT["secs"] = round(time.time() - t0, 1)
json.dump(OUT, open(os.path.join(HERE, "engine_check.out.json"), "w"), indent=1)
print("ALL CHECKS PASSED in %.1fs" % (time.time() - t0))
