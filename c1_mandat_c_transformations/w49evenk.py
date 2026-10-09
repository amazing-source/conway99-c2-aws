"""Rank 43, EVEN class-level system for a harmonic polynomial P of even degree p >= 2 on the eigenspace:
   F_d = sum over y in the class d of P(y) q^(|y|^2/14)   (25 classes up to sign, class 0 = sqrt7 M),  weight 22 + p.
usage: w49evenk.py p [N] [maxdeg] -> free parameters; then the expression of the norm-26 class sums."""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
p = int(sys.argv[1]); Ntr = sys.argv[2] if len(sys.argv) > 2 else "7"; maxdeg = int(sys.argv[3]) if len(sys.argv) > 3 else 12
sys.argv = [sys.argv[0], Ntr, "0"]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import w49 as W
N = W.N; reps = W.reps; rho = W.rho
names = []; index = {}
for d in reps:
    j = 0
    while rho[d] + 7 * j <= 7 * N: index[("T", d, j)] = len(names); names.append(("T", d, j)); j += 1
funcs = [(m, q) for m in range(0, maxdeg + 1, 2) for q in (W.POLES if m else W.POLES[:1])]
rows = []
for fi, (m, pole) in enumerate(funcs):
    cs = W.class_series(m, pole); basis = W.level1(24 + p + m); xs = []
    for i in range(len(basis)): index[("x", fi, i)] = len(names); names.append(("x", fi, i)); xs.append(index[("x", fi, i)])
    for n in range(N + 1):
        row = {xs[i]: Fr(basis[i][n]) for i in range(len(basis)) if basis[i][n]}
        for d in reps:
            w = 1 if d == (0, 0) else 2
            for n49, val in cs.get(d, {}).items():
                num = 98 * n - n49
                if num < 0 or num % 14: continue
                e7 = num // 14
                if (e7 - rho[d]) % 7 or e7 < rho[d]: continue
                v = index.get(("T", d, (e7 - rho[d]) // 7))
                if v is not None: row[v] = row.get(v, Fr(0)) - w * val
        rows.append(row)
def solve(extra):
    nv = len(names)
    cls = sorted([i for i, n in enumerate(names) if n[0] == "T"], key=lambda i: -(rho[names[i][1]] + 7 * names[i][2]))
    order = [i for i, n in enumerate(names) if n[0] == "x"] + cls; pos = {v: q for q, v in enumerate(order)}
    allrows = rows + extra
    M = fmpq_mat(len(allrows), nv)
    for i, row in enumerate(allrows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv) if R[i, j] != 0) for i in range(rk)]
    free = [q for q in range(nv) if q not in set(piv)]
    return [names[order[q]] for q in free], R, piv, order, free
edge = lambda nm: nm[0] == "T" and rho[nm[1]] + 7 * nm[2] > 7 * (N - 2)
lab = lambda f: (f"class0 norm {2 * f[2]} of M" if f[1] == (0, 0) else f"{f[1]} norm {2 * (rho[f[1]] + 7 * f[2])}")
z1 = [{index[("T", d, 0)]: Fr(1)} for d in reps]                         # d != 0: no vector below norm 14; d = 0: P(0) = 0
fr, R, piv, order, fcols = solve(z1); g = [f for f in fr if not edge(f)]
print(f"degree {p} (weight {22 + p}), truncation {N}, {len(funcs)} functionals; with the zeros: {len(g)} genuine free")
print("   ", [lab(f) for f in g if f[0] == 'T'], [f for f in g if f[0] == 'x'])
z2 = z1 + [{index[("T", d, 1)]: Fr(1)} for d in reps if d != (0, 0) and rho[d] != 6]
fr, R, piv, order, fcols = solve(z2); g = [f for f in fr if not edge(f)]
print(f"no vector of norm 16..24: {len(g)} genuine free:", [lab(f) for f in g if f[0] == 'T'], [f for f in g if f[0] == 'x'])
# expressions of the norm-26 class sums and of the next layers of class 0
nv = len(names)
for d in reps:
    if d == (0, 0) or rho[d] != 6: continue
    col = order.index(index[("T", d, 1)])
    if col in piv:
        i = piv.index(col)
        terms = [(names[order[q]], -Fr(int(R[i, q].p), int(R[i, q].q))) for q in fcols if R[i, q] != 0]
        print(f"   sum over class {d} norm 26 =", " + ".join(f"({c}) [{lab(f) if f[0]=='T' else f}]" for f, c in terms) or "0")
# expression of the layers of class 0 (norms 4, 6 of M) in the scenario without norms 16..24
for k in (2, 3):
    col = order.index(index[("T", (0, 0), k)])
    if col in piv:
        i = piv.index(col)
        terms = [(names[order[q]], -Fr(int(R[i, q].p), int(R[i, q].q))) for q in fcols if R[i, q] != 0 and not edge(names[order[q]])]
        print(f"   sum over M, norm {2*k} (class 0) =", " + ".join(f"({c}) [{lab(f) if f[0]=='T' else f}]" for f, c in terms) or "0")
    else: print(f"   class 0 norm {2*k}: free")
# general case (roots and norms 16..24 allowed): the determined quantities in terms of the 24 free tensors
fr, R, piv, order, fcols = solve(z1)
def show_expr(nm, title):
    col = order.index(index[nm])
    if col not in piv: print(f"   {title}: free"); return
    i = piv.index(col)
    terms = [(names[order[q]], -Fr(int(R[i, q].p), int(R[i, q].q))) for q in fcols if R[i, q] != 0 and not edge(names[order[q]])]
    print(f"   {title} =", " ".join(f"{'+' if c > 0 else '-'} {abs(c)} [{lab(f)}]" for f, c in terms))
print("GENERAL CASE at rank 43 (degree", p, "):")
show_expr(("T", (0, 2), 1), "class (0,2) norm 26")
show_expr(("T", (0, 0), 2), "M norm 4")
show_expr(("T", (0, 0), 3), "M norm 6")
