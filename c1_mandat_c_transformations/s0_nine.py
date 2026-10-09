"""Rank 43, scenario S0 (no root, no vector of L1 of norm 16..24) inside the nine-class programme:
how are the 1000 norm-4 vectors of M and the 2632 norm-26 vectors of L1 split between integral and fractional type?
T3[2] = fractional norm-4 vectors of M of one sign (>= 231 lines), T0[2] = integral ones;  X3[13], X0[13] same for norm 26."""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
N = 32
Mo = Z.Model(43, N); Mo.geometry()
for n in range(1, N // 7 + 1):
    for k in (0, 3):
        a, b = Mo.var("X", k, 63 * n), Mo.var("T", k, 9 * n)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
for n in range(7, 13): Mo.fix("X", 0, 9 * n, 0)          # no integral vector of norm 14..24
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)              # no fractional vector of norm 22, 24
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
E = lambda side, k, num9: expr[(side, k, (num9 - (Z.RHO if side == "T" else Z.SIG)[k]) // 9)]
G = []
for nm, e in expr.items():
    if z9lp.expo9(Mo, nm) <= top: G.append((e[0], dict(e[1]), str(nm)))
def addge(terms, const, label):
    c0 = Fr(const); cf = {}
    for coef, e in terms:
        c0 += coef * e[0]
        for t, v in e[1].items(): cf[t] = cf.get(t, Fr(0)) + coef * v
    G.append((c0, {t: v for t, v in cf.items() if v != 0}, label))
addge([(1, E("T", 3, 18))], -231, "231 lines"); addge([(1, E("T", 1, 14))], -99, "99 vertices"); addge([(1, E("T", 2, 20))], -693, "693 edges")
addge([(1, E("T", 0, 27))], -8316, "8316 differences")
for k in range(5):
    res = Z.RHO[k]; j = 0
    while 7 * (res + 9 * j) <= top:
        addge([(1, E("X", k, 7 * (res + 9 * j))), (-1, E("T", k, res + 9 * j))], 0, "cross"); j += 1
used = sorted({t for _, cf, _ in G for t in cf})
print(f"S0 in the nine-class programme: {len(used)} free parameters in {len(G)} inequalities", flush=True)
triv = [lab for c0, cf, lab in G if not cf and c0 < 0]
print("violated constant inequalities:", triv[:5])
def feas(extra=()):
    rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
    return exact_lp.solve(rows)[0] == "feasible"
print("feasible:", feas(), flush=True)
def rng(e, hi=10 ** 9):
    c0, cf = e
    def le(X): return (Fr(X) - c0, {t: -v for t, v in cf.items()}, "le")
    def ge(X): return (c0 - Fr(X), dict(cf), "ge")
    lo_, hi_ = -1, hi
    while hi_ - lo_ > 1:                      # minimum
        mid = (lo_ + hi_) // 2
        if feas([le(mid)]): hi_ = mid
        else: lo_ = mid
    mn = hi_; lo_, hi_ = mn, hi
    while hi_ - lo_ > 1:                      # maximum
        mid = (lo_ + hi_) // 2
        if feas([ge(mid)]): lo_ = mid
        else: hi_ = mid
    return mn, lo_
t0 = time.time()
for name, e in (("b2 = T0[2] + 2 T3[2]", (E("T", 0, 18)[0] + 2 * E("T", 3, 18)[0], {t: E("T", 0, 18)[1].get(t, 0) + 2 * E("T", 3, 18)[1].get(t, 0) for t in set(E("T", 0, 18)[1]) | set(E("T", 3, 18)[1])})),
                ("fractional norm-4 vectors of M of one sign, T3[2]", E("T", 3, 18)),
                ("fractional norm-26 vectors of L1 of one sign, X3[13]", E("X", 3, 117)),
                ("22-cocliques (L class 2, norm 154/9)", E("X", 2, 77)),
                ("class-1 vectors of O of norm 28/9", E("T", 1, 14))):
    print(f"   {name}: range {rng(e)}  [{time.time()-t0:.0f}s]", flush=True)
