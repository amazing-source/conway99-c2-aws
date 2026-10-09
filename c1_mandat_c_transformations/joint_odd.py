"""Rank 43: the 441 classes of L_9 / sqrt7 M_0 = Z/9 x F_7^2 together, degree 1 (vector sums of the class layers).

M_0 = {sqrt7 E psi : 9 | sum psi} is even of rank 44 with discriminant group Z/9 x F_7^2 at rank 43; A_8 + N_4 (N_4 = O_K + O_K)
carries the opposite discriminant form, so M_0 + A_8 + N_4 glues to an even unimodular lattice of rank 56, and for a linear
form l on the eigenspace, zonal harmonics h1 on A_8 (degree m1) and h2 on N_4 (degree m2), m1 + m2 odd,
     sum over classes (k,d) of  F_(k,d)(tau) theta^A8_{k,m1}(tau) theta^N4_{d,m2}(tau)   is a cusp form of weight 29 + m1 + m2 for SL_2(Z),
where F_(k,d) = sum over y in L_9 of class (k,d) of l(y) q^(|y|^2/14).
Question (scenario S0: no root, no vector of L1 of norm 16..24): which class layers are forced to be centred?
usage: joint_odd.py [N] [S0]"""
import sys, time, io, contextlib
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
NTR = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
S0 = "S0" in sys.argv
import a8
_argv = sys.argv; sys.argv = [sys.argv[0], str(NTR), "0"]
with contextlib.redirect_stdout(io.StringIO()):
    import w49 as W
sys.argv = _argv
N = NTR
t0 = time.time()
# ---------- classes (k, d) up to sign, excluding (0, (0,0))
def neg(c): return ((-c[0]) % 9, ((-c[1][0]) % 7, (-c[1][1]) % 7))
allc = [(k, (c1, c2)) for k in range(9) for c1 in range(7) for c2 in range(7)]
reps = [c for c in allc if c < neg(c)]
assert len(reps) == 220
rho7 = lambda d: (-2 * (d[0] ** 2 + d[1] ** 2)) % 7
eps = {c: (35 * c[0] ** 2 + 9 * rho7(c[1])) % 63 for c in reps}             # exponent of F_c = (eps + 63 j)/63
names = []; index = {}
for c in reps:
    j = 0
    while eps[c] + 63 * j <= 63 * N: index[(c, j)] = len(names); names.append((c, j)); j += 1
norm9 = lambda nm: 2 * (eps[nm[0]] + 63 * nm[1])                              # L-norm times 9
print(f"{len(reps)} classes up to sign, {len(names)} unknown vector sums (exponent <= {N})", flush=True)

# ---------- theta factors
A8F = {"even": [(0, "r"), (4, "r"), (6, "r"), (6, "w"), (8, "r"), (8, "w")], "odd": [(3, "r"), (3, "w"), (5, "r"), (5, "w"), (7, "r"), (7, "w"), (9, "r"), (9, "w")]}
N4F = {"odd": [(m, p) for m in (1, 3, 5, 7, 9, 11) for p in range(len(W.POLES))], "even": [(m, p) for m in (0, 2, 4, 6, 8, 10, 12) for p in (range(len(W.POLES)) if m else [0])]}
a8ser = {}
def A8(k, m, pole):
    key = (k, m, pole)
    if key not in a8ser: a8ser[key] = {49 * E18: v for E18, v in a8.series(k, m, pole, N)}        # exponent in units 1/882
    return a8ser[key]
n4ser = {}
def N4(m, p):
    if (m, p) not in n4ser:
        cs = W.class_series(m, W.POLES[p]); n4ser[(m, p)] = {d: {9 * n49: v for n49, v in s.items()} for d, s in cs.items()}
    return n4ser[(m, p)]

def cusp_relations(wt):
    """functionals (lam_1..lam_N) vanishing on the q-expansions (coefficients 1..N) of S_wt(SL_2(Z))"""
    basis = [f for f in W.level1(wt)]
    # cusp forms: combinations with zero constant term
    M = fmpq_mat(len(basis), 1 + N, [x for f in basis for x in f[:N + 1]])
    # nullspace of the map lam -> (sum_n lam_n f[n]) restricted to cusp forms: solve over the space spanned by cusp forms
    R, rk = M.rref()
    cusp = [[R[i, n] for n in range(1, N + 1)] for i in range(rk) if R[i, 0] == 0]
    # nullspace of the cusp rows (functionals lam with lam . f = 0 for every cusp form f), by hand
    Cr = [[Fr(int(x.p), int(x.q)) for x in row] for row in cusp]
    import mf7
    red, piv, _ = mf7.rref(Cr) if Cr else ([], [], None)
    freec = [j for j in range(N) if j not in piv]
    out = []
    for fcol in freec:
        lam = [Fr(0)] * N; lam[fcol] = Fr(1)
        for rw, p in zip(red, piv): lam[p] = -rw[fcol]
        out.append(lam)
    return out

rows = []
funcs = [(f1, f2) for f1 in A8F["even"] for f2 in N4F["odd"]] + [(f1, f2) for f1 in A8F["odd"] for f2 in N4F["even"]]
for (m1, p1), (m2, p2) in funcs:
    rel = cusp_relations(29 + m1 + m2)
    if not rel: continue
    s2 = N4(m2, p2)
    coef = [dict() for _ in range(N + 1)]                         # coef[n][unknown] : coefficient of the unknown in the q^n coefficient
    for c in reps:
        k, d = c
        th1 = A8(k, m1, p1); th2 = s2.get(d, {})
        if not th1 or not th2: continue
        prod = {}
        for e1, v1 in th1.items():
            for e2, v2 in th2.items():
                e = e1 + e2
                if e <= 882 * N: prod[e] = prod.get(e, Fr(0)) + v1 * v2
        for e, v in prod.items():
            for n in range(N + 1):
                rest = 882 * n - e                                # = 14 (eps + 63 j)
                if rest < 0 or rest % 14: continue
                num = rest // 14
                if num < eps[c] or (num - eps[c]) % 63: continue
                u = index.get((c, (num - eps[c]) // 63))
                if u is not None: coef[n][u] = coef[n].get(u, Fr(0)) + 2 * v
    assert not coef[0], "a constant term appeared"
    for lam in rel:
        row = {}
        for n in range(1, N + 1):
            if lam[n - 1] == 0: continue
            for u, v in coef[n].items(): row[u] = row.get(u, Fr(0)) + lam[n - 1] * v
        row = {u: v for u, v in row.items() if v != 0}
        if row: rows.append(row)
print(f"{len(funcs)} functionals, {len(rows)} modular equations  [{time.time()-t0:.0f}s]", flush=True)

def kbar(k): return min(k, 9 - k)
def zero_general(nm):
    c, j = nm; k = kbar(c[0]); nu9 = norm9(nm)                    # L-norm * 9
    if k == 0: return nu9 < 14 * 9                                # d != 0 here (class (0,0) is not a representative)
    return nu9 < {3: 22 * 9, 1: 178, 2: 154, 4: 220}[k]
def zero_S0(nm):
    c, j = nm; k = kbar(c[0]); nu9 = norm9(nm)
    if k == 0: return 16 * 9 <= nu9 <= 24 * 9
    if k == 3: return nu9 < 26 * 9
    return False

def solve(zero):
    nv = len(names)
    order = sorted(range(nv), key=lambda i: -norm9(names[i])); pos = {v: p for p, v in enumerate(order)}
    extra = [{i: Fr(1)} for i, nm in enumerate(names) if zero(nm)]
    allrows = rows + extra
    M = fmpq_mat(len(allrows), nv)
    for i, row in enumerate(allrows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    R, rk = M.rref()
    piv = set(next(j for j in range(nv) if R[i, j] != 0) for i in range(rk))
    return [names[order[p]] for p in range(nv) if p not in piv]

edge = lambda nm: norm9(nm) > 9 * 14 * (N - 2)
for label, zero in (("rank 43, proved zeros", zero_general),) + ((("S0", lambda nm: zero_general(nm) or zero_S0(nm)),) if S0 else ()):
    free = solve(zero); g = [f for f in free if not edge(f)]
    byk = {}
    for (c, j) in g: byk.setdefault((kbar(c[0]), norm9((c, j))), []).append(c)
    print(f"{label}: {len(g)} genuine free vector sums  [{time.time()-t0:.0f}s]")
    for (k, nu9), cl in sorted(byk.items()):
        print(f"     class type k = {k}, L-norm {nu9}/9 = {nu9/9:.2f}: {len(cl)} free classes (of this type and norm)")

# ---------- dependence of the fractional (k = 3) and integral (k = 0) layers on the free sums, in S0
if S0:
    zero = lambda nm: zero_general(nm) or zero_S0(nm)
    nv = len(names)
    order = sorted(range(nv), key=lambda i: -norm9(names[i])); pos = {v: p for p, v in enumerate(order)}
    allrows = rows + [{i: Fr(1)} for i, nm in enumerate(names) if zero(nm)]
    M = fmpq_mat(len(allrows), nv)
    for i, row in enumerate(allrows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv) if R[i, j] != 0) for i in range(rk)]
    freecols = [p for p in range(nv) if p not in set(piv)]
    dep = {}
    for i, p in enumerate(piv):
        nm = names[order[p]]
        if edge(nm): continue
        deps = [names[order[q]] for q in freecols if R[i, q] != 0 and not edge(names[order[q]])]
        dep[nm] = deps
    for k in (3, 0):
        for nu in (26, 28, 30, 32, 34, 36, 38, 40):
            sel = [(nm, d) for nm, d in dep.items() if kbar(nm[0][0]) == k and norm9(nm) == 9 * nu]
            if not sel: continue
            nz = sum(1 for _, d in sel if d)
            types = sorted({(kbar(f[0][0]), norm9(f)) for _, d in sel for f in d})
            print(f"class type k = {k}, L-norm {nu}: {len(sel)} determined classes, {nz} of them depend on free sums; free layers involved: {[(a, f'{b}/9') for a, b in types]}")
