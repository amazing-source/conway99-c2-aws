"""Nine-class programme at a given rank r (no class equality): is a LOW FRACTIONAL OBJECT forced?
objects: 22-cocliques X2[77/9], ghost vertices T1[14/9] - 99, class-1 vectors of L9 of norm 178/9 X1[89/9], regular 44-sets X4[110/9],
class-4 vectors of O of norm 34/9 T4[17/9].  Exact LP: range of each and minimum of their sum, in general and with no integral vector
of norm 14 (and 16).        usage: r_low.py rank [N]"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 32; t0 = time.time()
def build(fix=()):
    Mo = Z.Model(r, N); Mo.geometry()
    for side, c, num9, val in fix: Mo.fix(side, c, num9, val)
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
    addge([(1, E("T", 3, 18))], -231, "231 lines"); addge([(1, E("T", 1, 14))], -99, "99 vertices"); addge([(1, E("T", 2, 20))], -693, "693 edges")
    addge([(1, E("T", 0, 27))], -8316, "8316 differences"); addge([(-1, E("T", 0, 9))], 44, "b1<=44")
    addge([(1, E("T", 0, 18)), (2, E("T", 3, 18)), (-41, E("T", 0, 9))], -462, "b2>=462+41b1")
    addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "22 profile-C vectors of each sign per 22-coclique")
    used = sorted({t for _, cf, _ in G for t in cf})
    def feas(extra=()):
        rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
        return exact_lp.solve(rows)
    return E, comb, feas, len(used), G
def minimum(e, feas, hi=10 ** 9):
    c0, cf = e; lo_, hi_ = -1, hi
    if feas([(Fr(hi) - c0, {t: -v for t, v in cf.items()}, "le")])[0] != "feasible": return None
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([(Fr(mid) - c0, {t: -v for t, v in cf.items()}, "le")])[0] == "feasible": hi_ = mid
        else: lo_ = mid
    return hi_
for name, fix in (("general", ()), ("no integral norm 14", (("X", 0, 63, 0),)), ("no integral norm 14, 16", (("X", 0, 63, 0), ("X", 0, 72, 0)))):
    try: E, comb, feas, nfree, G = build(fix)
    except AssertionError as ex: print(f"rank {r}, {name}: equalities inconsistent ({ex})", flush=True); continue
    viol = [lab for c0, cf, lab in G if not cf and c0 < 0]
    if viol: print(f"rank {r}, {name}: INFEASIBLE by constants {viol[:4]}", flush=True); continue
    st = feas()[0]
    print(f"rank {r}, truncation {N}, {name}: {nfree} free parameters; exact LP {st}  [{time.time()-t0:.0f}s]", flush=True)
    if st != "feasible": continue
    objs = [("22-cocliques", E("X", 2, 77), 0), ("ghost vertices", E("T", 1, 14), -99), ("class 1 norm 178/9", E("X", 1, 89), 0),
            ("regular 44-sets", E("X", 4, 110), 0), ("class 4 norm 34/9 of O", E("T", 4, 17), 0)]
    tot = comb([(1, e) for _, e, _ in objs], sum(s for _, _, s in objs))
    print(f"   minimum of the SUM of the five low objects: {minimum(tot, feas)}  [{time.time()-t0:.0f}s]", flush=True)
    for nm, e, sh in objs: print(f"   minimum of {nm}: {minimum(comb([(1, e)], sh), feas)}", flush=True)
    for nm, e in (("P3/N25 layer X2[104/9]", E("X", 2, 104)), ("class 2 norm 172/9 X2[86/9]", E("X", 2, 86)), ("class 2 norm 190/9 X2[95/9]", E("X", 2, 95)),
                  ("ghost lines T3[18/9]-231", comb([(1, E("T", 3, 18))], -231))):
        print(f"   minimum of {nm}: {minimum(e, feas)}", flush=True)
