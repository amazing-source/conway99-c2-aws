"""S0 (rank 43) in NATURAL coordinates: the seven bottom quantities
     kappa (22-cocliques), g_v (ghost vertices), u (class 4, norm 34/9 of O), g_l (ghost lines), c1 (class 1, norm 178/9),
     w (class 2, norm 190/9), s44 (regular 44-sets).
Every layer count is constant + rational combination of these seven non-negative integers.
Step 1: the identities of the low layers.  Step 2: the congruences (integrality of all counts) in these coordinates.
Step 3: the admissible integer points (all counts non-negative integers, g_l >= 22 kappa).     usage: s0_natural.py [N] [enum]"""
import sys, time, math, itertools
from fractions import Fraction as Fr
import z9theta as Z, z9lp, mf7
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 32
t0 = time.time()
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "class equality")
        j += 1
Mo.fix("X", 0, 63, 0)
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
res = lambda side: (Z.RHO if side == "T" else Z.SIG)
E = lambda side, c, num9: expr[(side, c, (num9 - res(side)[c]) // 9)]
layers = {nm: e for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top}
used = sorted({t for e in layers.values() for t in e[1]}); nf = len(used); pos = {t: i for i, t in enumerate(used)}
def vec(e, shift=0):
    v = [Fr(0)] * nf
    for t, x in e[1].items(): v[pos[t]] = x
    return [e[0] - shift] + v
names = ["kappa", "g_v", "u", "g_l", "c1", "w", "s44"]
nat = [(E("X", 2, 77), 0), (E("T", 1, 14), 99), (E("T", 4, 17), 0), (E("T", 3, 18), 231), (E("X", 1, 89), 0), (E("X", 2, 95), 0), (E("X", 4, 110), 0)]
assert nf == 7
rows = [vec(e, sh) for e, sh in nat]
red, piv, _ = mf7.rref([r[1:] + [Fr(int(i == j)) for j in range(nf)] for i, r in enumerate(rows)])
assert piv == list(range(nf))
Minv = [r[nf:] for r in red]; c0s = [r[0] for r in rows]
def natural(e):
    v = vec(e); co = [sum(v[1 + j] * Minv[j][i] for j in range(nf)) for i in range(nf)]
    return [v[0] - sum(co[i] * c0s[i] for i in range(nf))] + co
NAT = {nm: natural(e) for nm, e in layers.items()}
lab = lambda nm: f"{'Theta' if nm[0] == 'T' else 'Xi'}_{nm[1]}[{z9lp.expo9(Mo, nm)}/9]"
def show(nm):
    f = NAT[nm]
    return f"{lab(nm)} = {f[0]} " + " ".join(f"{'+' if x > 0 else '-'} {abs(x)} {s}" for x, s in zip(f[1:], names) if x != 0)
order = sorted(layers, key=lambda nm: (z9lp.expo9(Mo, nm) * (7 if nm[0] == "T" else 1), nm[0]))
print(f"S0, truncation {N}: identities of the lowest layers in natural coordinates  [{time.time()-t0:.0f}s]")
seen = 0
for nm in order:
    f = NAT[nm]
    if all(x == 0 for x in f): continue
    if nm[0] == "T": continue                           # the M-side layers are L-side layers (class equality)
    if z9lp.expo9(Mo, nm) > 140: break
    print("  ", show(nm)); seen += 1
# ---------------- congruences
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
r = nf; x0 = [0] * r; B = [[int(i == j) for j in range(r)] for i in range(r)]; idx = 1; ok = True
for nm in order:
    f = NAT[nm]
    den = math.lcm(*[x.denominator for x in f])
    if den == 1: continue
    a = [int(x * den) for x in f[1:]]; b = int(-f[0] * den) % den; mm_ = den
    g = [sum(a[i] * B[i][j] for i in range(r)) % mm_ for j in range(r)]
    cc = (b - sum(a[i] * x0[i] for i in range(r))) % mm_
    for j in range(1, r):
        if g[j] == 0: continue
        G1, x, y = egcd(g[0], g[j]); u0, uj = g[0] // G1, g[j] // G1
        for i in range(r): B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
        g[0], g[j] = G1, 0
    G = math.gcd(g[0], mm_)
    if cc % G: print("CONGRUENCES INCONSISTENT at", lab(nm)); ok = False; break
    m2 = mm_ // G
    if m2 > 1:
        s1 = ((cc // G) * pow((g[0] // G) % m2, -1, m2)) % m2
        for i in range(r): x0[i] += B[i][0] * s1; B[i][0] *= m2
        idx *= m2
print(f"integrality of all counts: " + (f"coset of a lattice of index {idx} in Z^7" if ok else "impossible"))
dens = sorted({math.lcm(*[x.denominator for x in f]) for f in NAT.values()})
print("denominators occurring:", dens)
import pickle
pickle.dump({"NAT": {nm: f for nm, f in NAT.items()}, "names": names, "x0": x0, "B": B, "idx": idx, "expo": {nm: z9lp.expo9(Mo, nm) for nm in NAT}}, open("s0_natural.pkl", "wb"))
