"""Rank 43, scenario S0 (no root, no vector of L1 of norm 16..24): the 441 classes of L_9 / sqrt7 M_0 = Z/9 x F_7^2.

Degree 0: counts n_Lambda of every class layer Lambda = (class (k,d), norm), affine in 42 free counts.
Degree 1: vector sums S_Lambda = sum of the vectors of the layer, linear in 59 free sums.
NEW INTEGRALITY: every vector of a class (k,d) has all its coordinates = k/9 mod 1, so S_Lambda lies in (k n_Lambda / 9) 1 + Z^99.
A linear relation  D S_Lambda = sum_j (D c_j) S_j  with integers D c_j therefore gives the congruence
        D k_Lambda n_Lambda  =  sum_j D c_j k_j n_j   (mod 9).
Question: are these congruences, together with the integrality of all counts, solvable in integers?"""
import sys, time, io, contextlib, math
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
NTR = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
import a8, mf7
_argv = sys.argv; sys.argv = [sys.argv[0], str(NTR), "0"]
with contextlib.redirect_stdout(io.StringIO()):
    import w49 as W
sys.argv = _argv
N = NTR; t0 = time.time()
def neg(c): return ((-c[0]) % 9, ((-c[1][0]) % 7, (-c[1][1]) % 7))
allc = [(k, (c1, c2)) for k in range(9) for c1 in range(7) for c2 in range(7)]
ZERO = (0, (0, 0))
rho7 = lambda d: (-2 * (d[0] ** 2 + d[1] ** 2)) % 7
EPS = {c: (35 * c[0] ** 2 + 9 * rho7(c[1])) % 63 for c in allc}
kbar = lambda k: min(k, 9 - k)
norm9 = lambda nm: 2 * (EPS[nm[0]] + 63 * nm[1])
A8F = {"even": [(0, "r"), (4, "r"), (6, "r"), (6, "w"), (8, "r"), (8, "w")], "odd": [(3, "r"), (3, "w"), (5, "r"), (5, "w"), (7, "r"), (7, "w"), (9, "r"), (9, "w")]}
N4F = {"odd": [(m, p) for m in (1, 3, 5, 7, 9, 11) for p in range(len(W.POLES))], "even": [(m, p) for m in (0, 2, 4, 6, 8, 10, 12) for p in (range(len(W.POLES)) if m else [0])]}
a8ser = {}; n4ser = {}
def A8(k, m, pole):
    if (k, m, pole) not in a8ser: a8ser[(k, m, pole)] = {49 * E18: v for E18, v in a8.series(k, m, pole, N)}
    return a8ser[(k, m, pole)]
def N4(m, p):
    if (m, p) not in n4ser:
        cs = W.class_series(m, W.POLES[p]); n4ser[(m, p)] = {d: {9 * n49: v for n49, v in s.items()} for d, s in cs.items()}
    return n4ser[(m, p)]
def relations(wt, cusp):
    basis = W.level1(wt)
    Cr = [[Fr(x) for x in f[:N + 1]] for f in basis]
    if cusp:
        red0, piv0, _ = mf7.rref(Cr); Cr = [rw for rw, p in zip(red0, piv0) if p != 0]
        if not Cr: Cr = [[Fr(0)] * (N + 1)]
    red, piv, _ = mf7.rref(Cr) if any(any(x != 0 for x in rw) for rw in Cr) else ([], [], None)
    out = []
    for fcol in [j for j in range(N + 1) if j not in piv]:
        lam = [Fr(0)] * (N + 1); lam[fcol] = Fr(1)
        for rw, p in zip(red, piv): lam[p] = -rw[fcol]
        out.append(lam)
    return out
def zero_rule(nm):
    """proved zeros at rank 43 and the zeros of S0"""
    c, j = nm; k = kbar(c[0]); nu9 = norm9(nm)
    if c == ZERO: return nu9 == 14 * 9                               # S0: no root
    if k == 0: return nu9 < 14 * 9 or 16 * 9 <= nu9 <= 24 * 9
    if k == 3: return nu9 < 26 * 9
    return nu9 < {1: 178, 2: 154, 4: 220}[k]

def system(parity):
    """parity 0: counts (classes up to sign incl. the zero class), parity 1: vector sums (odd)."""
    reps = [c for c in allc if (c <= neg(c) if parity == 0 else c < neg(c))]
    names = []; index = {}
    for c in reps:
        j = 0
        while EPS[c] + 63 * j <= 63 * N: index[(c, j)] = len(names); names.append((c, j)); j += 1
    if parity == 0: funcs = [(f1, f2) for f1 in A8F["even"] for f2 in N4F["even"]] + [(f1, f2) for f1 in A8F["odd"] for f2 in N4F["odd"]]
    else: funcs = [(f1, f2) for f1 in A8F["even"] for f2 in N4F["odd"]] + [(f1, f2) for f1 in A8F["odd"] for f2 in N4F["even"]]
    rows = []
    for (m1, p1), (m2, p2) in funcs:
        rel = relations(28 + parity + m1 + m2, cusp=(parity == 1))
        if not rel: continue
        s2 = N4(m2, p2); coef = [dict() for _ in range(N + 1)]
        for c in reps:
            k, d = c; w = 1 if c == neg(c) else 2
            th1 = A8(k, m1, p1); th2 = s2.get(d, {})
            if not th1 or not th2: continue
            for e1, v1 in th1.items():
                for e2, v2 in th2.items():
                    e = e1 + e2
                    if e > 882 * N: continue
                    for n in range(N + 1):
                        rest = 882 * n - e
                        if rest < 0 or rest % 14: continue
                        num = rest // 14
                        if num < EPS[c] or (num - EPS[c]) % 63: continue
                        u = index.get((c, (num - EPS[c]) // 63))
                        if u is not None: coef[n][u] = coef[n].get(u, Fr(0)) + w * v1 * v2
        for lam in rel:
            row = {}
            for n in range(N + 1):
                if lam[n] == 0: continue
                for u, v in coef[n].items(): row[u] = row.get(u, Fr(0)) + lam[n] * v
            row = {u: v for u, v in row.items() if v != 0}
            if row: rows.append(row)
    nv = len(names)
    order = sorted(range(nv), key=lambda i: -norm9(names[i])); pos = {v: p for p, v in enumerate(order)}
    extra = [({i: Fr(1)}, Fr(0)) for i, nm in enumerate(names) if zero_rule(nm)]
    if parity == 0: extra.append(({index[(ZERO, 0)]: Fr(1)}, Fr(1)))
    M = fmpq_mat(len(rows) + len(extra), nv + 1)
    for i, row in enumerate(rows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    for i, (row, b) in enumerate(extra):
        for j, c in row.items(): M[len(rows) + i, pos[j]] = fmpq(c.numerator, c.denominator)
        M[len(rows) + i, nv] = fmpq(b.numerator, b.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv + 1) if R[i, j] != 0) for i in range(rk)]
    assert nv not in piv, "inconsistent"
    pset = set(piv); freecols = [p for p in range(nv) if p not in pset]
    expr = {}
    for i, p in enumerate(piv):
        nm = names[order[p]]
        c0 = Fr(int(R[i, nv].p), int(R[i, nv].q))
        cf = {names[order[q]]: -Fr(int(R[i, q].p), int(R[i, q].q)) for q in freecols if R[i, q] != 0}
        expr[nm] = (c0, cf)
    for q in freecols: expr[names[order[q]]] = (Fr(0), {names[order[q]]: Fr(1)})
    return expr, [names[order[q]] for q in freecols]

edge = lambda nm: norm9(nm) > 9 * 14 * (N - 2)
cnt, cfree = system(0); print(f"counts: {sum(1 for f in cfree if not edge(f))} genuine free  [{time.time()-t0:.0f}s]", flush=True)
vs, vfree = system(1); print(f"vector sums: {sum(1 for f in vfree if not edge(f))} genuine free  [{time.time()-t0:.0f}s]", flush=True)
params = [f for f in cfree if not edge(f)]; pidx = {f: i for i, f in enumerate(params)}; r = len(params)

def count_expr(nm):
    """count of the layer nm as (const, vector over params); None if it involves truncation-edge unknowns"""
    c = nm[0]; rep = c if c <= neg(c) else neg(c)
    e = cnt.get((rep, nm[1]))
    if e is None: return None
    if any(f not in pidx for f in e[1]): return None
    v = [Fr(0)] * r
    for f, x in e[1].items(): v[pidx[f]] = x
    return e[0], v

# ---------- congruences
cong = []                # (const, vec, modulus, label):  const + vec.t  = 0  (mod modulus), all rationals scaled later
for nm, (c0, cf) in cnt.items():
    if edge(nm) or any(f not in pidx for f in cf): continue
    v = [Fr(0)] * r
    for f, x in cf.items(): v[pidx[f]] = x
    cong.append((c0, v, 1, ("count", nm)))
nvec = 0
for nm, (c0, cf) in vs.items():
    if edge(nm) or any(edge(f) for f in cf) or (len(cf) == 1 and nm in cf): continue
    D = math.lcm(*[x.denominator for x in cf.values()]) if cf else 1
    terms = [(Fr(D * nm[0][0]), nm)] + [(-D * x * f[0][0], f) for f, x in cf.items()]          # sum of (integer coefficient * k) * n  = 0 mod 9
    const = Fr(0); vec = [Fr(0)] * r; ok = True
    for coef, layer in terms:
        e = count_expr(layer)
        if e is None: ok = False; break
        const += coef * e[0]; vec = [a + coef * b for a, b in zip(vec, e[1])]
    if ok: cong.append((const / 9, [x / 9 for x in vec], 1, ("vector sum", nm))); nvec += 1
print(f"{len(cong) - nvec} integrality conditions on counts, {nvec} congruences from vector sums; {r} integer parameters", flush=True)

def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
def lattice(conds):
    t0_ = [0] * r; B = [[int(i == j) for j in range(r)] for i in range(r)]; idx = 1
    for c0, vec, _, lab in conds:
        den = math.lcm(c0.denominator, *[x.denominator for x in vec])
        if den == 1: continue
        a = [int(x * den) for x in vec]; b = int(-c0 * den) % den; m = den
        g = [sum(a[i] * B[i][j] for i in range(r)) % m for j in range(r)]
        c = (b - sum(a[i] * t0_[i] for i in range(r))) % m
        for j in range(1, r):
            if g[j] == 0: continue
            G1, x, y = egcd(g[0], g[j]); u0, uj = g[0] // G1, g[j] // G1
            for i in range(r): B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
            g[0], g[j] = G1, 0
        G = math.gcd(g[0], m)
        if c % G: return False, idx, lab
        mm = m // G
        if mm > 1:
            s1 = ((c // G) * pow((g[0] // G) % mm, -1, mm)) % mm
            for i in range(r): t0_[i] += B[i][0] * s1; B[i][0] *= mm
            idx *= mm
    return True, idx, None
key = lambda t: norm9(t[3][1])
only_counts = sorted([c for c in cong if c[3][0] == "count"], key=key)
print("integrality of the counts alone:", lattice(only_counts)[:2], flush=True)
allc_ = sorted(cong, key=key)
ok, idx, where = lattice(allc_)
print("with the vector-sum congruences:", "CONSISTENT, index " + str(idx) if ok else f"INCONSISTENT at {where[0]} of class {where[1][0]}, L-norm {norm9(where[1])}/9 (lattice index before: {idx})")
