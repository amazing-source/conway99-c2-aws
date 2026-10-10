"""Nine-class programme at rank r with no integral vector of norm 14: how many integral vectors of norms 16, 18, 20 (and 22, 24) are
forced?  Exact LP: minimum and maximum of a8, a9, a10, a11, a12 (numbers of integral vectors of L1 of norm 2n, both signs), and the
minimum of a8 + a9 + a10.        usage: r_short.py rank [N] [paths]      (paths: adds the row of the 8316 induced 2-paths, norm 6 of M, class of sum 3)"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 32; t0 = time.time()
Mo = Z.Model(r, N); Mo.geometry(); Mo.fix("X", 0, 63, 0); Mo.fix("T", 0, 9, 0)        # a7 = 0, hence b1 = 0 (sqrt7 M is inside L1)
free, expr = z9lp.reduce(Mo); top = 9 * (N - 9)
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
addge([(1, E("T", 3, 18))], -231, "231 lines"); addge([(1, E("T", 1, 14))], -99, "99 vertices"); addge([(1, E("T", 2, 20))], -693, "693 edges")
addge([(1, E("T", 0, 27))], -8316, "8316 differences"); addge([(-1, E("T", 0, 9))], 44, "b1<=44")
if "paths" in sys.argv: addge([(1, E("T", 3, 27))], -8316, "8316 induced 2-paths e_u + e_v + e_w (sum +3, norm 6 of M)")
addge([(1, E("T", 0, 18)), (2, E("T", 3, 18)), (-41, E("T", 0, 9))], -462, "b2>=462+41b1")
addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "22 profile-C vectors of each sign per 22-coclique")
for n in (2, 3):                                                                      # sqrt7 M inside L1: Theta_c[9n/9] <= Xi_c[63n/9]
    addge([(1, E("X", 0, 63 * n)), (-1, E("T", 0, 9 * n))], 0, f"sqrt7 M in L1, integral, norm {2*n} of M")
    addge([(1, E("X", 3, 63 * n)), (-1, E("T", 3, 9 * n))], 0, f"sqrt7 M in L1, fractional, norm {2*n} of M")
used = sorted({t for _, cf, _ in G for t in cf})
def feas(extra=()):
    rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
    return exact_lp.solve(rows)[0] == "feasible"
print(f"rank {r}, truncation {N}, a7 = b1 = 0, containment rows: {len(used)} free parameters; feasible: {feas()}  [{time.time()-t0:.0f}s]", flush=True)
def mn(e, hi=10 ** 7, extra=()):
    c0, cf = e; lo_, hi_ = -1, hi
    if not feas(list(extra) + [(Fr(hi) - c0, {t: -v for t, v in cf.items()}, "le")]): return None
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas(list(extra) + [(Fr(mid) - c0, {t: -v for t, v in cf.items()}, "le")]): hi_ = mid
        else: lo_ = mid
    return hi_
a = {n: E("X", 0, 9 * n) for n in (8, 9, 10, 11, 12)}
zero = lambda e: (-e[0], {t: -v for t, v in e[1].items()}, "= 0")
print(f"   minimum of a8 + a9 + a10 (integral norms 16, 18, 20, both signs): {mn(comb([(1, a[8]), (1, a[9]), (1, a[10])]))}  [{time.time()-t0:.0f}s]", flush=True)
for n in (8, 9, 10): print(f"   minimum of a{n} (norm {2*n}): {mn(a[n])}  [{time.time()-t0:.0f}s]", flush=True)
print(f"   minimum of a9 + a10 when a8 = 0: {mn(comb([(1, a[9]), (1, a[10])]), extra=[zero(a[8])])}  [{time.time()-t0:.0f}s]", flush=True)
print(f"   minimum of a10 when a8 = a9 = 0: {mn(a[10], extra=[zero(a[8]), zero(a[9])])}  [{time.time()-t0:.0f}s]", flush=True)
print(f"   minimum of a8 when a9 = a10 = 0: {mn(a[8], extra=[zero(a[9]), zero(a[10])])}  [{time.time()-t0:.0f}s]", flush=True)
print("done", flush=True)
