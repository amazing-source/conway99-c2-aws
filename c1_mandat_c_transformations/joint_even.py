"""Rank 43: the 441 classes of L_9 / sqrt7 M_0 = Z/9 x F_7^2 together, degree 0 (numbers of vectors per class and norm).
 sum over classes (k,d) of  n_(k,d)(tau) theta^A8_{k,m1}(tau) theta^N4_{d,m2}(tau)  in  M_(28 + m1 + m2)(SL_2(Z)),   m1 + m2 even.
Question (scenario S0): how many free parameters; are the counts equally distributed over the 8 classes d of a circle?
usage: joint_even.py [N] [S0]"""
import sys, time, io, contextlib
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
NTR = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
S0 = "S0" in sys.argv
import a8, mf7
_argv = sys.argv; sys.argv = [sys.argv[0], str(NTR), "0"]
with contextlib.redirect_stdout(io.StringIO()):
    import w49 as W
sys.argv = _argv
N = NTR; t0 = time.time()
def neg(c): return ((-c[0]) % 9, ((-c[1][0]) % 7, (-c[1][1]) % 7))
allc = [(k, (c1, c2)) for k in range(9) for c1 in range(7) for c2 in range(7)]
reps = [c for c in allc if c <= neg(c)]; assert len(reps) == 221
rho7 = lambda d: (-2 * (d[0] ** 2 + d[1] ** 2)) % 7
eps = {c: (35 * c[0] ** 2 + 9 * rho7(c[1])) % 63 for c in reps}
names = []; index = {}
for c in reps:
    j = 0
    while eps[c] + 63 * j <= 63 * N: index[(c, j)] = len(names); names.append((c, j)); j += 1
norm9 = lambda nm: 2 * (eps[nm[0]] + 63 * nm[1])
kbar = lambda k: min(k, 9 - k)
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
def relations(wt):
    basis = W.level1(wt)
    Cr = [[Fr(x) for x in f[:N + 1]] for f in basis]
    red, piv, _ = mf7.rref(Cr)
    out = []
    for fcol in [j for j in range(N + 1) if j not in piv]:
        lam = [Fr(0)] * (N + 1); lam[fcol] = Fr(1)
        for rw, p in zip(red, piv): lam[p] = -rw[fcol]
        out.append(lam)
    return out
rows = []
funcs = [(f1, f2) for f1 in A8F["even"] for f2 in N4F["even"]] + [(f1, f2) for f1 in A8F["odd"] for f2 in N4F["odd"]]
for (m1, p1), (m2, p2) in funcs:
    rel = relations(28 + m1 + m2)
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
                    if num < eps[c] or (num - eps[c]) % 63: continue
                    u = index.get((c, (num - eps[c]) // 63))
                    if u is not None: coef[n][u] = coef[n].get(u, Fr(0)) + w * v1 * v2
    for lam in rel:
        row = {}
        for n in range(N + 1):
            if lam[n] == 0: continue
            for u, v in coef[n].items(): row[u] = row.get(u, Fr(0)) + lam[n] * v
        row = {u: v for u, v in row.items() if v != 0}
        if row: rows.append(row)
print(f"221 classes up to sign, {len(names)} unknown counts, {len(funcs)} functionals, {len(rows)} modular equations  [{time.time()-t0:.0f}s]", flush=True)
ZERO = (0, (0, 0))
def zero_general(nm):
    c, j = nm; k = kbar(c[0]); nu9 = norm9(nm)
    if c == ZERO: return False
    if k == 0: return nu9 < 14 * 9
    return nu9 < {3: 22 * 9, 1: 178, 2: 154, 4: 220}[k]
def zero_S0(nm):
    c, j = nm; k = kbar(c[0]); nu9 = norm9(nm)
    if c == ZERO: return nu9 == 14 * 9
    if k == 0: return 16 * 9 <= nu9 <= 24 * 9
    if k == 3: return nu9 < 26 * 9
    return False
def solve(zero):
    nv = len(names)
    order = sorted(range(nv), key=lambda i: -norm9(names[i])); pos = {v: p for p, v in enumerate(order)}
    extra = [({i: Fr(1)}, Fr(0)) for i, nm in enumerate(names) if zero(nm)] + [({index[(ZERO, 0)]: Fr(1)}, Fr(1))]
    M = fmpq_mat(len(rows) + len(extra), nv + 1)
    for i, row in enumerate(rows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    for i, (row, b) in enumerate(extra):
        for j, c in row.items(): M[len(rows) + i, pos[j]] = fmpq(c.numerator, c.denominator)
        M[len(rows) + i, nv] = fmpq(b.numerator, b.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv + 1) if R[i, j] != 0) for i in range(rk)]
    assert nv not in piv, "inconsistent"
    return [names[order[p]] for p in range(nv) if p not in set(piv)], R, piv, order
edge = lambda nm: norm9(nm) > 9 * 14 * (N - 2)
for label, zero in (("rank 43, proved zeros", zero_general),) + ((("S0", lambda nm: zero_general(nm) or zero_S0(nm)),) if S0 else ()):
    free, R, piv, order = solve(zero); g = [f for f in free if not edge(f)]
    byk = {}
    for (c, j) in g: byk.setdefault((kbar(c[0]), norm9((c, j)), c[1] == (0, 0)), []).append(c)
    print(f"{label}: {len(g)} genuine free counts  [{time.time()-t0:.0f}s]")
    for (k, nu9, rad), cl in sorted(byk.items()):
        print(f"     k = {k}, L-norm {nu9}/9 = {nu9/9:.2f}{' (radical class)' if rad else ''}: {len(cl)} free classes")
