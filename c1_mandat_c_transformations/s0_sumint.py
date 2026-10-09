"""S0 (rank 43): EXACT integrality of the VECTOR SUMS of the class layers, coupled with the integrality of the counts.

For a layer Lam (class k, n_Lam vectors, all with coordinates = k/9 mod 1), the coordinate at a fixed vertex v of the vector
sum S_Lam lies in  k n_Lam / 9 + Z.  The degree-1 modular system gives S_Lam = sum_j c_(Lam,j) S_j  (j: free layers).
Writing  (S_j)_v = k_j n_j / 9 + t_j  with t_j in Z, every determined layer gives the exact condition
        sum_j c_(Lam,j) (k_j n_j / 9 + t_j)  -  k_Lam n_Lam / 9   in Z,
the counts n being affine in the 7 integer count parameters tau.  Unknown integer vector (tau, t).
Question: is this system of linear congruences solvable?            usage: s0_sumint.py [N]"""
import sys, time, math, pickle
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, a8, z9theta as Z, z9lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
RHO, SIG = Z.RHO, Z.SIG
t0 = time.time()
# ---------------- counts in S0
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (RHO[c] + 9 * j) <= 9 * N:
        num9 = RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
        j += 1
Mo.fix("X", 0, 63, 0)
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
cfree, cexpr = z9lp.reduce(Mo)
top = 9 * (N - 9)
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
cex = {nm: e for nm, e in cexpr.items() if expo(nm) <= top}
cused = sorted({t for e in cex.values() for t in e[1]}); nc = len(cused); cpos = {t: i for i, t in enumerate(cused)}
lab = lambda f: f"{f[0]}{f[1]}[{expo(f)}/9]"
print("count parameters:", [lab(cfree[t]) for t in cused], f"[{time.time()-t0:.0f}s]", flush=True)
# ---------------- vector sums in S0 (degree-1 system of z9lin.py)
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
    m, pole = f; S, V = Z.space(27 + m); c7 = Fr(7) ** ((18 - 43 - m) // 2)
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
for n in range(0, 13): fix("X", 3, 9 * n)                       # includes the S0 zeros (norms 22, 24)
for num9 in range(8, 89, 9): fix("X", 1, num9)
for num9 in range(5, 77, 9): fix("X", 2, num9)
for num9 in range(2, 110, 9): fix("X", 4, num9)
fix("T", 3, 0); fix("T", 3, 9); fix("T", 1, 5); fix("T", 2, 2); fix("T", 4, 8)
for c in range(1, 5):
    j = 0
    while 7 * (RHO[c] + 9 * j) <= 9 * N:
        a, b = var("X", c, 7 * (RHO[c] + 9 * j)), var("T", c, RHO[c] + 9 * j)
        if a is not None and b is not None: rows.append({a: Fr(1), b: Fr(-1)})
        j += 1
xs = [i for i, n in enumerate(names) if n[0] == "x"]
cl = sorted([i for i, n in enumerate(names) if n[0] != "x"], key=lambda i: -expo(names[i]))
order = xs + cl; pos = {v: p for p, v in enumerate(order)}; nv = len(names)
M = fmpq_mat(len(rows), nv)
for i, row in enumerate(rows):
    for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
R, rk = M.rref()
piv = [next(j for j in range(nv) if R[i, j] != 0) for i in range(rk)]
pset = set(piv); freecols = [p for p in range(nv) if p not in pset]
assert all(names[order[q]][0] != "x" for q in freecols), "a form coordinate is free"
vexpr = {}
for i, p in enumerate(piv):
    nm = names[order[p]]
    if nm[0] == "x": continue
    vexpr[nm] = {names[order[q]]: -Fr(int(R[i, q].p), int(R[i, q].q)) for q in freecols if R[i, q] != 0}
vfree = [names[order[q]] for q in freecols]
gen = [f for f in vfree if expo(f) <= top]
print(f"vector sums: {len(gen)} genuine free layers: {[lab(f) for f in gen]}  [{time.time()-t0:.0f}s]", flush=True)
J = len(gen); jpos = {f: i for i, f in enumerate(gen)}
# ---------------- congruences in the unknown integer vector (tau, t)
r = nc + J
def count_aff(nm):
    e = cex.get(nm)
    if e is None: return None
    v = [Fr(0)] * r
    for t, x in e[1].items(): v[cpos[t]] = x
    return e[0], v
conds = []
for nm, e in cex.items():
    if nm[0] == "x": continue
    ca = count_aff(nm); conds.append((ca[0], ca[1], ("count", nm)))
nsum = 0
for nm, cf in vexpr.items():
    if expo(nm) > top or any(f not in jpos for f in cf): continue
    k = nm[1]; ca = count_aff(nm)
    if ca is None: continue
    const = -Fr(k, 9) * ca[0]; vec = [-Fr(k, 9) * x for x in ca[1]]
    ok = True
    for f, c in cf.items():
        cj = count_aff(f)
        if cj is None: ok = False; break
        const += c * Fr(f[1], 9) * cj[0]
        vec = [a + c * Fr(f[1], 9) * b for a, b in zip(vec, cj[1])]
        vec[nc + jpos[f]] += c
    if ok: conds.append((const, vec, ("sum", nm))); nsum += 1
print(f"{len(conds) - nsum} count conditions, {nsum} vector-sum conditions, {r} integer unknowns ({nc} count parameters + {J} integer parts)", flush=True)
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
def lattice(conds):
    x0 = [0] * r; B = [[int(i == j) for j in range(r)] for i in range(r)]; idx = 1
    for c0, vec, labl in conds:
        den = math.lcm(c0.denominator, *[x.denominator for x in vec])
        if den == 1: continue
        a = [int(x * den) for x in vec]; b = int(-c0 * den) % den; m = den
        g = [sum(a[i] * B[i][j] for i in range(r)) % m for j in range(r)]
        c = (b - sum(a[i] * x0[i] for i in range(r))) % m
        for j in range(1, r):
            if g[j] == 0: continue
            G1, x, y = egcd(g[0], g[j]); u0, uj = g[0] // G1, g[j] // G1
            for i in range(r): B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
            g[0], g[j] = G1, 0
        G = math.gcd(g[0], m)
        if c % G: return False, idx, labl, x0, B
        mm = m // G
        if mm > 1:
            s1 = ((c // G) * pow((g[0] // G) % mm, -1, mm)) % mm
            for i in range(r): x0[i] += B[i][0] * s1; B[i][0] *= mm
            idx *= mm
    return True, idx, None, x0, B
key = lambda t: expo(t[2][1])
cc = sorted([c for c in conds if c[2][0] == "count"], key=key)
ok, idx, where, x0, B = lattice(cc); print("counts alone:", ok, idx, flush=True)
ok, idx, where, x0, B = lattice(sorted(conds, key=lambda t: (key(t), t[2][0] != "count")))
print("counts and vector sums together:", "CONSISTENT, index " + str(idx) if ok else f"INCONSISTENT at the {where[0]} condition of the layer {lab(where[1])} (index reached before: {idx})")
pickle.dump({"conds": conds, "gen": gen, "cused": [cfree[t] for t in cused], "x0": x0, "B": B, "ok": ok, "idx": idx}, open(f"s0_sumint_N{N}.pkl", "wb"))
