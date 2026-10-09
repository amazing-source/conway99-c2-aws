"""S0 (rank 43, no root, no norm 16..24), nine-class programme: which HYPOTHETICAL divisibility conditions on the sizes
of the L-side class layers are incompatible with the integrality lattice?  (Exploration: says what would have to be proved.)"""
import sys, math
from fractions import Fraction as Fr
import z9theta as Z, z9lp
N = 32
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
        j += 1
Mo.fix("X", 0, 63, 0)
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
exprs = sorted([(nm, e) for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top], key=lambda t: z9lp.expo9(Mo, t[0]))
used = sorted({t for _, e in exprs for t in e[1]}); r = len(used)
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
def radical(nm):
    side, k, j = nm
    if side != "X": return True
    num9 = Z.SIG[k] + 9 * j
    return (num9 % 7 == 0) and ((num9 // 7 - Z.RHO[k]) % 9 == 0)
def run(mult):
    """mult(nm) -> integer m: require count / m to be an integer.  Returns (consistent, index, first failing layer)"""
    t0 = [0] * r; B = [[int(i == j) for j in range(r)] for i in range(r)]; index = 1
    for nm, (c0, cf) in exprs:
        mu = mult(nm); c0_ = c0 / mu; cf_ = {t: v / mu for t, v in cf.items()}
        den = math.lcm(c0_.denominator, *[v.denominator for v in cf_.values()]) if cf_ else c0_.denominator
        if den == 1: continue
        a = [int(cf_.get(t, Fr(0)) * den) for t in used]; b = int(-c0_ * den) % den; m = den
        g = [sum(a[i] * B[i][j] for i in range(r)) % m for j in range(r)]
        c = (b - sum(a[i] * t0[i] for i in range(r))) % m
        for j in range(1, r):
            if g[j] == 0: continue
            G1, x, y = egcd(g[0], g[j]); u0, uj = g[0] // G1, g[j] // G1
            for i in range(r): B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
            g[0], g[j] = G1, 0
        G = math.gcd(g[0], m)
        if c % G: return False, index, nm
        mm = m // G
        if mm > 1:
            s1 = ((c // G) * pow((g[0] // G) % mm, -1, mm)) % mm
            for i in range(r): t0[i] += B[i][0] * s1; B[i][0] *= mm
            index *= mm
    return True, index, None
lab = lambda nm: f"{nm[0]}{nm[1]}[{z9lp.expo9(Mo, nm)}/9]"
print("no hypothesis:", run(lambda nm: 1)[:2])
print("H1 (fractional layers of one sign divisible by 3, non-radical norms):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 3 if (nm[0] == "X" and nm[1] == 3 and not radical(nm)) else 1)]])
print("H2 (classes 1, 2, 4, non-radical norms, divisible by 9):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 9 if (nm[0] == "X" and nm[1] in (1, 2, 4) and not radical(nm)) else 1)]])
print("H2' (classes 1, 2, 4, non-radical norms, divisible by 3):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 3 if (nm[0] == "X" and nm[1] in (1, 2, 4) and not radical(nm)) else 1)]])
# single layers: which single hypothesis 'this layer is divisible by 3' is already inconsistent?
bad = []
for nm, _ in exprs:
    if nm[0] == "X" and nm[1] != 0 and not radical(nm):
        okk, idx, where = run(lambda q, nm=nm: 3 if q == nm else 1)
        if not okk: bad.append(lab(nm))
print("single layers whose divisibility by 3 alone is inconsistent:", bad)
print("H8 (all non-radical layers of the classes 1..4 divisible by 8):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 8 if (nm[0] == "X" and nm[1] != 0 and not radical(nm)) else 1)]])
print("H4 (divisible by 4):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 4 if (nm[0] == "X" and nm[1] != 0 and not radical(nm)) else 1)]])
print("H2x (divisible by 2):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 2 if (nm[0] == "X" and nm[1] != 0 and not radical(nm)) else 1)]])
for kk in (1, 2, 3, 4):
    print(f"   class {kk} alone divisible by 8:", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm, kk=kk: 8 if (nm[0] == "X" and nm[1] == kk and not radical(nm)) else 1)]])
print("H8 on class 0 too (integral vectors per class, non-radical norms):", [(a, b, lab(c) if c else None) for a, b, c in [run(lambda nm: 8 if (nm[0] == "X" and not radical(nm) and not (nm[1] == 0 and nm[2] == 0)) else 1)]])
