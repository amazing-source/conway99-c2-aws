"""Referee: does BRIDGE.md describe the engine and the deferral rule correctly?  Lattice 011 and the 400 historical pairs.
The engine's lattice_data and defer_consumer.witness are CALLED (they are the objects under test); everything they return is
re-checked here in AMBIENT coordinates with exact integers / Fractions, independently of the Gram matrix G the engine uses.
Nothing is written outside this folder (numba cache redirected, no .pyc)."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["NUMBA_CACHE_DIR"] = os.path.join(HERE, "numba_cache")
os.environ["Q_DEFER_NODES"] = "0"                                       # the quick variant, the one the text warns about
sys.dont_write_bytecode = True
SP = os.path.dirname(HERE); PKG = os.path.join(SP, "pkgfull")
REPO_Q = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\q"
sys.argv = ["defer_consumer.py", PKG, "11", "-", os.path.join(HERE, "unused.jsonl"), "0"]
sys.path.insert(0, REPO_Q)
import numpy as np
from fractions import Fraction as Fr
import defer_consumer as DC
FD = DC.FD
out = {}


def P(*a): print(*a, flush=True)


t0 = time.time()
gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "011.json")))["gens"]
L = FD.lattice_data(gens, Fr(1))
P("lattice_data(011): %.1f s; r = %d, |R| = %d, |X3| = %d, |X4| = %d, |S2| = %d" % (time.time() - t0, L["r"], len(L["R"]), len(L["X3"]), len(L["X4"]), len(L["S2"])))
B = [[Fr(x) for x in row] for row in L["B"]]; G = L["G"]
assert len(B) == 24 and all(len(r) == 24 for r in B)
# --- H2: G = B B^T exactly, integral; det exactly 1; positive definite (exact LDL^T pivots > 0)
Gx = [[sum(a * b for a, b in zip(u, v)) for v in B] for u in B]
assert all(Gx[i][j] == int(G[i, j]) for i in range(24) for j in range(24)), "G is not the Gram matrix of B"
M = [row[:] for row in Gx]; det = Fr(1); piv = []
for c in range(24):
    assert M[c][c] > 0, "not positive definite"                         # no pivoting needed for a PD matrix
    piv.append(M[c][c]); det *= M[c][c]
    for i in range(c + 1, 24):
        f = M[i][c] / M[c][c]
        if f: M[i] = [a - f * b for a, b in zip(M[i], M[c])]
assert det == 1
P("H2: G = B B^T exactly (integers), exact det = %s, all 24 LDL pivots > 0 (positive definite, rank 24)" % det)
# the lattice spanned by B is the lattice spanned by the generators of the file
Binv = None
A_ = [B[i][:] + [Fr(int(i == j)) for j in range(24)] for i in range(24)]
for c in range(24):
    p = next(i for i in range(c, 24) if A_[i][c] != 0); A_[c], A_[p] = A_[p], A_[c]; pv = A_[c][c]; A_[c] = [x / pv for x in A_[c]]
    for i in range(24):
        if i != c and A_[i][c] != 0:
            f = A_[i][c]; A_[i] = [x - f * y for x, y in zip(A_[i], A_[c])]
Binv = [row[24:] for row in A_]


def coeffs(v):                                                           # v (ambient, Fractions) -> coefficients in the basis B, exact
    return [sum(v[j] * Binv[j][i] for j in range(24)) for i in range(24)]


gq = [[Fr(x) for x in g] for g in gens]
assert all(all(x.denominator == 1 for x in coeffs(g)) for g in gq), "a generator is not in Z-span(B)"
# index of span(gens) in span(B) is 1 because span(gens) is an integral lattice containing ... (not needed); check via determinant of an HNF-free argument:
# every basis row is an integer combination of the generators  <=>  the coefficient matrix of the generators has gcd of 24x24 minors 1; test mod several primes
C = [[int(x) for x in coeffs(g)] for g in gq]
def rank_mod(Mx, p):
    Mx = [[x % p for x in r] for r in Mx]; r = 0
    for c in range(24):
        pv = next((i for i in range(r, len(Mx)) if Mx[i][c]), None)
        if pv is None: continue
        Mx[r], Mx[pv] = Mx[pv], Mx[r]; inv = pow(Mx[r][c], p - 2, p); Mx[r] = [x * inv % p for x in Mx[r]]
        for i in range(len(Mx)):
            if i != r and Mx[i][c]: f = Mx[i][c]; Mx[i] = [(a - f * b) % p for a, b in zip(Mx[i], Mx[r])]
        r += 1
    return r
assert all(rank_mod(C, p) == 24 for p in (2, 3, 5, 7, 11, 13)), "generators span a proper sublattice at a small prime"
P("B: every generator of 011.json is an integer combination of B; the generators have full rank mod 2,3,5,7,11,13 in the basis B")

DEN = 1
for row in B:
    for x in row: DEN = DEN * x.denominator // np.gcd(DEN, x.denominator)
DEN = int(DEN)
BD = np.array([[int(x * DEN) for x in row] for row in B], dtype=np.int64)   # DEN * basis (ambient), exact
P("ambient denominators: DEN = %d" % DEN)


def amb(Xc):                                                              # coefficient rows -> DEN * ambient rows (int64, exact: small integers)
    return Xc.astype(np.int64) @ BD


# --- R, X3, X4: norms exactly 2, 3, 4 in ambient coordinates; one per +- pair; integer coefficient vectors
for name, nrm in (("R", 2), ("X3", 3), ("X4", 4)):
    X = L[name]; assert X.dtype == np.int64
    Xa = amb(X); nn = (Xa * Xa).sum(axis=1)
    assert (nn == nrm * DEN * DEN).all(), name
    keys = {tuple(v) for v in X.tolist()}
    assert len(keys) == len(X) and not any(tuple(-a for a in v) in keys for v in keys), "both signs present"
    assert (np.einsum("ij,jk,ik->i", X, G, X) == nrm).all()
P("R (%d), X3 (%d), X4 (%d): integer coefficient rows, ambient norms exactly 2, 3, 4; one vector per +- pair" % (len(L["R"]), len(L["X3"]), len(L["X4"])))
out.update(nR=len(L["R"]), nX3=len(L["X3"]), nX4=len(L["X4"]))

# --- the 400 pairs
pairs = json.load(open(os.path.join(SP, "bridge", "wagner_rerun", "SOURCE_011_SAMPLE_PAIRS.json")))
P("pairs: %d" % len(pairs))
Ra, X3a, X4a = amb(L["R"]), amb(L["X3"]), amb(L["X4"])
cnt = {"T18": 0, "T20": 0, "none": 0}; agree = 0; min97_mine = 0; min97_eng = 0; emin_hist = {}; E17 = 0; shapes = {8: set(), 9: set(), 10: set()}
both = 0; t18_and_y13 = 0; hist_verdicts = {}
D2 = DEN * DEN
for k, rec in enumerate(pairs):
    y1 = [Fr(x) for x in rec["y1"]]; y2 = [Fr(x) for x in rec["y2"]]
    c1, c2 = coeffs(y1), coeffs(y2)
    assert all(x.denominator == 1 for x in c1 + c2), "y not in U"                       # H3
    assert sum(a * a for a in y1) == 7 and sum(a * a for a in y2) == 7 and sum(a * b for a, b in zip(y1, y2)) == 0   # H4
    cf1 = np.array([int(x) for x in c1], dtype=np.int64); cf2 = np.array([int(x) for x in c2], dtype=np.int64)
    y1a = np.array([int(x * DEN) for x in y1], dtype=np.int64); y2a = np.array([int(x * DEN) for x in y2], dtype=np.int64)
    # my Y, ambient: ((DEN r).(DEN y))^2 / DEN^4
    def Yof(Xa):
        a = Xa @ y1a; b = Xa @ y2a
        assert (a % D2 == 0).all() and (b % D2 == 0).all()
        a //= D2; b //= D2
        return a * a + b * b
    YR, Y3, Y4 = Yof(Ra), Yof(X3a), Yof(X4a)
    mine = "T18" if (YR == 5).any() else "T20" if (YR == 4).any() else "none"
    w = DC.witness(L, cf1, cf2)
    theirs = "T18" if w == DC.DEF18 else "T20" if w == DC.DEF20 else "none"
    assert (w is None) == (theirs == "none")
    agree += mine == theirs; cnt[mine] += 1
    both += bool((YR == 5).any() and (YR == 4).any())
    m97 = bool((Y3 == 13).any()); min97_mine += m97
    x = FD.min97_witness(L, cf1, cf2); min97_eng += x is not None
    assert (x is not None) == m97
    t18_and_y13 += (mine == "T18") and m97
    ER, E3, E4 = 14 - YR, 21 - Y3, 28 - Y4
    allE = np.concatenate([ER, E3, E4]); assert allE.min() >= 0
    E17 += int(((allE >= 1) & (allE <= 7)).sum())
    for E in (8, 9, 10):
        for nrm, Y in ((2, YR), (3, Y3), (4, Y4)):
            for yv in np.unique(Y[7 * nrm - Y == E]).tolist(): shapes[E].add((nrm, int(yv)))
    emin = int(allE[allE > 0].min())
    if not m97: emin_hist[emin] = emin_hist.get(emin, 0) + 1; hist_verdicts[rec["verdict"]] = hist_verdicts.get(rec["verdict"], 0) + 1
P("H3/H4 on the 400 pairs (exact, ambient): y1, y2 in U, norms 7, orthogonal")
P("deferral rule: my ambient computation of (r,y1)^2+(r,y2)^2 over the roots agrees with defer_consumer.witness on %d / %d pairs; "
  "T18 %d, T20 %d, none %d; pairs with both a Y=5 and a Y=4 root: %d (labelled T18)" % (agree, len(pairs), cnt["T18"], cnt["T20"], cnt["none"], both))
P("min97 (norm-3 x with Y=13): mine %d, engine %d; among the %d others, minimum positive E over norm<=4: %s; their historical verdicts: %s"
  % (min97_mine, min97_eng, len(pairs) - min97_mine, dict(sorted(emin_hist.items())), hist_verdicts))
P("pairs with a T18 witness that also have a Y=13 witness: %d of %d" % (t18_and_y13, cnt["T18"]))
P("vectors of norm <= 4 with E in 1..7 over all pairs: %d;  (norm, Y) realising E = 8: %s, E = 9: %s, E = 10: %s"
  % (E17, sorted(shapes[8]), sorted(shapes[9]), sorted(shapes[10])))
assert agree == len(pairs)
out.update(pairs=len(pairs), agree=agree, counts=cnt, min97=min97_mine, emin_hist=emin_hist, E_1_7=E17, shapes={k: sorted(v) for k, v in shapes.items()})

# --- the H4 gap of the quick deferral path, shown on a deliberately INVALID pair (norms / orthogonality wrong)
assert DC.BUDGET == 0
rec = next(r for r in pairs if True)
found = None
rng = np.random.default_rng(1)
for rec in pairs:
    c1 = np.array([int(x) for x in coeffs([Fr(x) for x in rec["y1"]])], dtype=np.int64)
    c2 = np.array([int(x) for x in coeffs([Fr(x) for x in rec["y2"]])], dtype=np.int64)
    for r_ in L["R"][:28]:
        for bad1, bad2, why in ((c1 + r_, c2, "y1 + r"), (c1, c2 + r_, "y2 + r"), (c1, c1 + c2 + 0 * r_, "y2 := y1 + y2")):
            n1, n2, ip = int(bad1 @ G @ bad1), int(bad2 @ G @ bad2), int(bad1 @ G @ bad2)
            if (n1, n2, ip) == (7, 7, 0): continue
            if DC.witness(L, bad1, bad2) != DC.DEF18: continue
            if FD.char_trap(L, bad1, bad2) is not None: continue
            found = (bad1, bad2, why, n1, n2, ip); break
        if found: break
    if found: break
if found:
    bad1, bad2, why, n1, n2, ip = found
    r = DC.search(L, bad1, bad2, node_limit=1000)
    P("H4 gap (quick variant, Q_DEFER_NODES=0): invalid pair (%s; norms %d, %d, inner product %d) -> defer_consumer.search returns %r" % (why, n1, n2, ip, r))
    try:
        ps = FD.pair_setup(L, bad1, bad2); P("  engine pair_setup: no assertion?!")
    except AssertionError:
        P("  the engine's pair_setup raises AssertionError on the same pair (the stream consumer would record INVALID if the pair reached it)")
    out["h4_gap_demo"] = {"why": why, "norms": [n1, n2], "ip": ip, "verdict": r.get("verdict")}
else:
    P("no invalid pair with a Y=5 witness and no char trap found in the sample (H4 gap not demonstrated)")
# the same remark for the engine's own immediate filters: they return EXCLUDED before pair_setup
os.environ["FD_MIN97"] = "1"; demo = None
for rec in pairs[:60]:
    c1 = np.array([int(x) for x in coeffs([Fr(x) for x in rec["y1"]])], dtype=np.int64)
    c2 = np.array([int(x) for x in coeffs([Fr(x) for x in rec["y2"]])], dtype=np.int64)
    for r_ in L["R"][:28]:
        bad1 = c1 + r_
        if int(bad1 @ G @ bad1) == 7 and int(bad1 @ G @ c2) == 0: continue
        if FD.char_trap(L, bad1, c2) is not None or FD.min97_witness(L, bad1, c2) is not None:
            try:
                rr = FD.search(L, bad1, c2, node_limit=1000)
                demo = (int(bad1 @ G @ bad1), int(bad1 @ G @ c2), rr.get("verdict")); break
            except AssertionError:
                pass
    if demo: break
os.environ["FD_MIN97"] = "0"
P("engine's own search on an invalid pair (norm(y1) = %s, (y1,y2) = %s): verdict %r (returned before pair_setup's assertions)" % demo if demo else "no demo found for the engine's immediate filters")
out["engine_immediate_demo"] = demo
json.dump(out, open(os.path.join(HERE, "ref_engine.out.json"), "w"), indent=1, default=str)
P("DONE %.1f s" % (time.time() - t0))
