"""General rank 43 (no branch hypothesis) in the nine-class programme with the full class equalities:
which low layers of L_9 are FORCED non-empty?  For each layer: exact LP test of 'layer = 0', then the exact minimum.
usage: r43gen_layers.py [N]"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
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
addge([(1, E("T", 0, 18)), (2, E("T", 3, 18)), (-41, E("T", 0, 9))], -462, "b2>=462+41b1")
addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "22 profile-C vectors per 22-coclique")
used = sorted({t for _, cf, _ in G for t in cf})
def feas(extra=()):
    rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
    return exact_lp.solve(rows)
print(f"general rank 43, N {N}: {len(used)} free parameters: {[free[t] for t in used]}  [{time.time()-t0:.0f}s]", flush=True)
st, sol, it = feas(); print("   exact LP:", st, f"[{time.time()-t0:.0f}s]", flush=True)
def minimum(e, hi=10 ** 9):
    c0, cf = e
    le = lambda X: (Fr(X) - c0, {t: -v for t, v in cf.items()}, "le")
    if feas([le(0)])[0] == "feasible": return 0
    lo_, hi_ = 0, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([le(mid)])[0] == "feasible": hi_ = mid
        else: lo_ = mid
    return hi_
todo = [("X", 2, 104), ("X", 2, 113), ("X", 2, 122), ("X", 1, 107), ("X", 1, 116), ("X", 4, 128), ("X", 3, 117), ("X", 2, 86), ("X", 2, 95),
        ("X", 1, 89), ("X", 4, 110), ("X", 3, 99), ("X", 3, 108), ("T", 2, 20), ("T", 0, 18)]
for side, c, num9 in todo:
    nrm = 2 * num9 * (7 if side == "T" else 1)
    print(f"   {side}{c}[{num9}/9] (L-norm {nrm}/9 = {nrm/9:.2f}): minimum {minimum(E(side, c, num9))}   [{time.time()-t0:.0f}s]", flush=True)
