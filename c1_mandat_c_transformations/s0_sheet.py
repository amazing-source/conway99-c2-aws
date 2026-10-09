"""Rank 43, Codex's branch (no vector of L1 of norm 16..24), b1 = 2k roots, inside the nine-class programme:
free parameters and exact ranges of the class counts.  usage: s0_sheet.py k"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
k = int(sys.argv[1]); N = 32
Mo = Z.Model(43, N); Mo.geometry()
for n in range(1, N // 7 + 1):
    for c in (0, 3):
        a, b = Mo.var("X", c, 63 * n), Mo.var("T", c, 9 * n)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
Mo.fix("X", 0, 63, 2 * k)                                   # a7 = b1 = 2k
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
E = lambda side, c, num9: expr[(side, c, (num9 - (Z.RHO if side == "T" else Z.SIG)[c]) // 9)]
G = [(e[0], dict(e[1]), str(nm)) for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top]
def comb(terms, const=0):
    c0 = Fr(const); cf = {}
    for coef, e in terms:
        c0 += coef * e[0]
        for t, v in e[1].items(): cf[t] = cf.get(t, Fr(0)) + coef * v
    return c0, {t: v for t, v in cf.items() if v != 0}
def addge(terms, const, label):
    c0, cf = comb(terms, const); G.append((c0, cf, label))
addge([(1, E("T", 3, 18))], -231, "lines"); addge([(1, E("T", 1, 14))], -99, "vertices"); addge([(1, E("T", 2, 20))], -693, "edges")
addge([(1, E("T", 0, 27))], -8316, "differences")
addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "22 profile-C vectors of each sign per 22-coclique")
for c in range(5):
    res = Z.RHO[c]; j = 0
    while 7 * (res + 9 * j) <= top:
        addge([(1, E("X", c, 7 * (res + 9 * j))), (-1, E("T", c, res + 9 * j))], 0, "cross"); j += 1
used = sorted({t for _, cf, _ in G for t in cf})
def feas(extra=()):
    rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
    return exact_lp.solve(rows)[0] == "feasible"
print(f"k = {k} (b1 = {2*k}): {len(used)} free parameters: {[free[t] for t in used]}")
if any((not cf) and c0 < 0 for c0, cf, _ in G) or not feas():
    print("   INFEASIBLE"); sys.exit()
def rng(e, hi=10 ** 10):
    c0, cf = e
    le = lambda X: (Fr(X) - c0, {t: -v for t, v in cf.items()}, "le"); ge = lambda X: (c0 - Fr(X), dict(cf), "ge")
    lo_, hi_ = -1, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([le(mid)]): hi_ = mid
        else: lo_ = mid
    mn = hi_; lo_, hi_ = mn, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([ge(mid)]): lo_ = mid
        else: hi_ = mid
    return mn, lo_
t0 = time.time()
Q = [("norm-4 vectors of M, total b2", comb([(1, E("T", 0, 18)), (2, E("T", 3, 18))])),
     ("   integral ones (class 0)", E("T", 0, 18)),
     ("   fractional of one sign (231 lines + profiles A', B, C)", E("T", 3, 18)),
     ("norm-26 vectors of L1, total a13", comb([(1, E("X", 0, 117)), (2, E("X", 3, 117))])),
     ("   fractional of one sign (Z of size 2, S of size 35)", E("X", 3, 117)),
     ("22-cocliques", E("X", 2, 77)),
     ("regular 44-sets (L class 4, norm 220/9)", E("X", 4, 110)),
     ("L class-1 vectors of norm 178/9", E("X", 1, 89)),
     ("vectors of O of class 1 and norm 28/9 (99 vertices + ghosts)", E("T", 1, 14)),
     ("vectors of O of class 2 and norm 22/9", E("T", 2, 11)),
     ("vectors of O of class 2 and norm 40/9 (693 edges + others)", E("T", 2, 20)),
     ("vectors of O of class 4 and norm 34/9", E("T", 4, 17)),
     ("norm-6 vectors of M of fractional type, one sign", E("T", 3, 27))]
for name, e in Q: print(f"   {name}: {rng(e)}  [{time.time()-t0:.0f}s]", flush=True)
