"""Rank 43, odd (degree 1) class-level system.  For a fixed vertex v (or any linear form l on the eigenspace),
   F_d(tau) = sum over y in the class d of l(y) q^(|y|^2/14)     (F_(-d) = -F_d, F_0 = 0)
is a vector-valued cusp form of weight 23; paired with ODD harmonic polynomials h on N_4 (degree m):
   sum_d F_d theta_{d,h}  in  S_(25+m)(SL_2(Z)).
Question: how many free parameters, and do the vector sums of the classes vanish when norms 16..24 are absent?"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "7", "0"]
import w49 as W
N = W.N; MAXDEG = int(sys.argv[2]) if len(sys.argv) > 2 else 11
reps = [d for d in W.reps if d != (0, 0)]; rho = W.rho
names = []; index = {}
for d in reps:
    j = 0
    while rho[d] + 7 * j <= 7 * N: index[("T", d, j)] = len(names); names.append(("T", d, j)); j += 1
funcs = [(m, p) for m in range(1, 12, 2) for p in W.POLES]
rows = []
for fi, (m, pole) in enumerate(funcs):
    cs = W.class_series(m, pole); basis = W.level1(25 + m); xs = []
    for i in range(len(basis)): index[("x", fi, i)] = len(names); names.append(("x", fi, i)); xs.append(index[("x", fi, i)])
    for n in range(N + 1):
        row = {xs[i]: Fr(basis[i][n]) for i in range(len(basis)) if basis[i][n]}
        for d in reps:
            for n49, val in cs.get(d, {}).items():
                num = 98 * n - n49
                if num < 0 or num % 14: continue
                e7 = num // 14
                if (e7 - rho[d]) % 7 or e7 < rho[d]: continue
                v = index.get(("T", d, (e7 - rho[d]) // 7))
                if v is not None: row[v] = row.get(v, Fr(0)) - 2 * val        # class d and class -d contribute equally (odd x odd)
        rows.append(row)
def solve(extra):
    nv = len(names)
    cls = sorted([i for i, n in enumerate(names) if n[0] == "T"], key=lambda i: -(rho[names[i][1]] + 7 * names[i][2]))
    order = [i for i, n in enumerate(names) if n[0] == "x"] + cls; pos = {v: p for p, v in enumerate(order)}
    allrows = rows + extra
    M = fmpq_mat(len(allrows), nv)
    for i, row in enumerate(allrows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv) if R[i, j] != 0) for i in range(rk)]
    return [names[order[p]] for p in range(nv) if p not in set(piv)]
edge = lambda nm: nm[0] == "T" and rho[nm[1]] + 7 * nm[2] > 7 * (N - 2)
free = solve([]); print(f"{len(funcs)} odd functionals; modularity alone: {len(free)} free, {sum(1 for f in free if not edge(f))} genuine")
z1 = [{index[("T", d, 0)]: Fr(1)} for d in reps]
free = solve(z1); g = [f for f in free if not edge(f)]
print(f"with the zeros below norm 14: {len(g)} genuine free:", sorted((2 * (rho[f[1]] + 7 * f[2]), f[1]) for f in g if f[0] == 'T'), [f for f in g if f[0] == 'x'])
z2 = z1 + [{index[("T", d, 1)]: Fr(1)} for d in reps if rho[d] != 6]
free = solve(z2); g = [f for f in free if not edge(f)]
print(f"and no vector of norm 16..24: {len(g)} genuine free:", sorted((2 * (rho[f[1]] + 7 * f[2]), f[1]) for f in g if f[0] == 'T'))
