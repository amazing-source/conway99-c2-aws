"""Nine-class programme, degree 1 (vector sums).  For a linear form l on the eigenspace:
   M side:  T_k = sum over x in O of class k of l(sqrt7 x) q^(x^2/2),   L side:  X_c = sum over y in L_9 of class c of l(y) q^(y^2/2)
(odd in the class).  With an odd zonal harmonic Z_m of A_8:  g_m = 2 sum_k T_k theta_{k,m} in S_(27+m)(Gamma_0(7)),
   2 sum_c X_c(tau) theta_{c,m}(7 tau) = - 7^((18 - r - m)/2) g_m | W_7.
Question at rank 43, scenario S0: are all the class layers centred (vector sum zero)?        usage: z9lin.py r [S0]"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, a8
import z9theta as Z
RHO, SIG = Z.RHO, Z.SIG
r = int(sys.argv[1]); S0 = "S0" in sys.argv; N = 32
FUNCS = [(3, "r"), (3, "w"), (5, "r"), (5, "w"), (7, "r"), (7, "w"), (9, "r"), (9, "w")]
names = []; index = {}; rows = []
def add(nm): index[nm] = len(names); names.append(nm)
for side, res in (("T", RHO), ("X", SIG)):
    for k in range(1, 5):
        j = 0
        while res[k] + 9 * j <= 9 * N: add((side, k, j)); j += 1
def var(side, k, num9):
    res = (RHO if side == "T" else SIG)[k]
    if num9 < res or (num9 - res) % 9: return None
    return index.get((side, k, (num9 - res) // 9))
for f in FUNCS:
    S, V = Z.space(27 + f[0])
    for i in range(len(S.ser)): add(("x", f, i))
for f in FUNCS:
    m, pole = f; S, V = Z.space(27 + m); c7 = Fr(7) ** ((18 - r - m) // 2)
    th = {k: dict(a8.series(k, m, pole, N)) for k in range(1, 5)}
    for n in range(N + 1):
        row = {index[("x", f, i)]: Fr(S.ser[i][n]) for i in range(len(S.ser)) if S.ser[i][n]}
        for k in range(1, 5):
            for E18, val in th[k].items():
                v = var("T", k, 9 * n - E18 // 2)
                if v is not None: row[v] = row.get(v, Fr(0)) - 2 * val
        rows.append(row)
        row = {index[("x", f, i)]: -c7 * Fr(V[i][n]) for i in range(len(S.ser)) if V[i][n]}
        for c in range(1, 5):
            for E18, val in th[c].items():
                v = var("X", c, 9 * n - 7 * E18 // 2)
                if v is not None: row[v] = row.get(v, Fr(0)) - 2 * val
        rows.append(row)
def fix(side, k, num9):
    v = var(side, k, num9)
    if v is not None: rows.append({v: Fr(1)})
def solve():
    expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
    xs = [i for i, n in enumerate(names) if n[0] == "x"]
    cl = sorted([i for i, n in enumerate(names) if n[0] != "x"], key=lambda i: -expo(names[i]))
    order = xs + cl; pos = {v: p for p, v in enumerate(order)}; nv = len(names)
    M = fmpq_mat(len(rows), nv)
    for i, row in enumerate(rows):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
    R, rk = M.rref()
    piv = set(next(j for j in range(nv) if R[i, j] != 0) for i in range(rk))
    free = [names[order[p]] for p in range(nv) if p not in piv]
    top = lambda nm: nm[0] != "x" and expo(nm) > 9 * (N - 9)
    return [f for f in free if not top(f)]
g = solve(); print(f"rank {r}: modularity alone, genuine free: {len(g)}")
for n in range(0, 11): fix("X", 3, 9 * n)
for num9 in range(8, 89, 9): fix("X", 1, num9)
for num9 in range(5, 77, 9): fix("X", 2, num9)
for num9 in range(2, 110, 9): fix("X", 4, num9)
fix("T", 3, 0); fix("T", 3, 9); fix("T", 1, 5); fix("T", 2, 2); fix("T", 4, 8)
lab = lambda f: f"{f[0]}{f[1]}[{(RHO if f[0]=='T' else SIG)[f[1]] + 9*f[2]}/9]"
g = solve(); print(f"with the proved zeros: {len(g)} genuine free: {[lab(f) for f in g if f[0] != 'x']}")
if r == 43:
    for c in range(1, 5):
        j = 0
        while 7 * (RHO[c] + 9 * j) <= 9 * N:
            a, b = var("X", c, 7 * (RHO[c] + 9 * j)), var("T", c, RHO[c] + 9 * j)
            if a is not None and b is not None: rows.append({a: Fr(1), b: Fr(-1)})
            j += 1
    g = solve(); print(f"rank 43 class equalities: {len(g)} genuine free: {[lab(f) for f in g if f[0] != 'x']}")
    if S0:
        fix("X", 3, 99); fix("X", 3, 108)
        g = solve(); print(f"S0 (no fractional vector of norm 22, 24): {len(g)} genuine free: {[lab(f) for f in g if f[0] != 'x']}")
