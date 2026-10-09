"""General rank 43 (no branch hypothesis), nine-class programme with the full class equalities: 15 parameters.
NATURAL BASIS: the 8 short layers (roots, integral norms 16..24, fractional norms 22, 24) and the 7 bottom quantities of S0
(22-cocliques, ghost vertices, class-4 norm 34/9, ghost lines, class-1 norm 178/9, class-2 norm 190/9, regular 44-sets).
Every layer count is then  constant + integer/rational combination of these 15 non-negative numbers.
Question: how do the short vectors trade against the forced objects of S0 (P3/N25 etc.)?      usage: r43_identity.py [N]"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, mf7
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
t0 = time.time()
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "class equality")
        j += 1
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
res = lambda side: (Z.RHO if side == "T" else Z.SIG)
E = lambda side, c, num9: expr[(side, c, (num9 - res(side)[c]) // 9)]
used = sorted({t for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top for t in e[1]})
nf = len(used); pos = {t: i for i, t in enumerate(used)}
def vec(e, shift=0):
    v = [Fr(0)] * nf
    for t, x in e[1].items(): v[pos[t]] = x
    return [e[0] - shift] + v
nat = [("b1 (roots)", E("X", 0, 63), 0), ("a8", E("X", 0, 72), 0), ("a9", E("X", 0, 81), 0), ("a10", E("X", 0, 90), 0),
       ("a11 integral", E("X", 0, 99), 0), ("a12 integral", E("X", 0, 108), 0), ("f11 (fractional norm 22, one sign)", E("X", 3, 99), 0),
       ("f12 (fractional norm 24, one sign)", E("X", 3, 108), 0),
       ("kappa (22-cocliques)", E("X", 2, 77), 0), ("g_v (ghost vertices)", E("T", 1, 14), 99), ("u (class 4, norm 34/9 of O)", E("T", 4, 17), 0),
       ("g_l (ghost lines)", E("T", 3, 18), 231), ("c1 (class 1, norm 178/9)", E("X", 1, 89), 0), ("w (class 2, norm 190/9)", E("X", 2, 95), 0),
       ("s44 (regular 44-sets)", E("X", 4, 110), 0)]
assert len(nat) == nf == 15, (len(nat), nf)
# natural_i = c_i + sum_j M_ij t_j  ->  t = Minv (natural - c)
rows = [vec(e, sh) for _, e, sh in nat]
aug = [r[1:] + [Fr(int(i == j)) for j in range(nf)] for i, r in enumerate(rows)]
red, piv, _ = mf7.rref(aug)
assert piv == list(range(nf)), "the 15 natural quantities are not independent"
Minv = [r[nf:] for r in red]; c = [r[0] for r in rows]
def natural(e):
    """affine form in the parameters -> (constant, coefficients on the 15 natural quantities)"""
    v = vec(e); co = [sum(v[1 + j] * Minv[j][i] for j in range(nf)) for i in range(nf)]
    return v[0] - sum(co[i] * c[i] for i in range(nf)), co
short = ["b1", "a8", "a9", "a10", "a11", "a12", "f11", "f12", "kappa", "g_v", "u", "g_l", "c1", "w", "s44"]
def show(name, e):
    k0, co = natural(e)
    print(f"{name} = {k0} " + " ".join(f"{'+' if x > 0 else '-'} {abs(x)} {s}" for x, s in zip(co, short) if x != 0))
print(f"general rank 43, truncation {N}  [{time.time()-t0:.0f}s]")
show("P3/N25 layer  Xi_2[104/9]", E("X", 2, 104))
show("class 2, norm 172/9  Xi_2[86/9]", E("X", 2, 86))
show("class 2, norm 226/9  Xi_2[113/9]", E("X", 2, 113))
show("class 1, norm 214/9  Xi_1[107/9]", E("X", 1, 107))
show("class 4, norm 256/9  Xi_4[128/9]", E("X", 4, 128))
show("fractional norm 26, one sign  Xi_3[117/9]", E("X", 3, 117))
show("integral norm 26  Xi_0[117/9]", E("X", 0, 117))
show("integral norm 4 of M  Theta_0[18/9]", E("T", 0, 18))
show("class 2, norm 40/9 of O  Theta_2[20/9]", E("T", 2, 20))
show("class 1, norm 46/9 of O  Theta_1[23/9]", E("T", 1, 23))
