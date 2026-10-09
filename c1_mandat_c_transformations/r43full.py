"""Rank 43 in the nine-class programme with the FULL class equality.
At rank 43 the quotient L_9 / sqrt7 O is the anisotropic plane, so for EVERY class k (not only 0 and 3) a vector of L_9
of class k whose exponent is 7e (e a legal exponent of the class k of O) lies in sqrt7 O:   Xi_k[7e] = Theta_k[e].
usage: r43full.py general | branch k        (branch = no vector of L1 of norm 16..24, b1 = 2k)"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
mode = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 0; N = 32
Mo = Z.Model(43, N); Mo.geometry()
neq = 0
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, f"rank 43: X{c}[{7*num9}/9] = T{c}[{num9}/9]"); neq += 1
        j += 1
if mode == "branch":
    Mo.fix("X", 0, 63, 2 * k)
    for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
    for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
try: free, expr = z9lp.reduce(Mo)
except AssertionError as e:
    print(f"{mode} {k}: the EQUALITIES are inconsistent ({e})"); sys.exit()
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
addge([(1, E("T", 0, 27)), (2, E("T", 3, 27))], -45964, "b3"); addge([(1, E("T", 0, 36)), (2, E("T", 3, 36))], -2729034, "b4")
addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "22 profile-C vectors of each sign per 22-coclique")
used = sorted({t for _, cf, _ in G for t in cf})
def feas(extra=()):
    rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]
    return exact_lp.solve(rows)
print(f"{mode} {k if mode == 'branch' else ''}: {neq} class equalities, {len(used)} free parameters: {[free[t] for t in used]}", flush=True)
viol = [(lab, str(c0)) for c0, cf, lab in G if not cf and c0 < 0]
if viol: print("   INFEASIBLE: constant inequalities violated:", viol[:6]); sys.exit()
st, sol, it = feas()
print("   exact LP:", st, flush=True)
if st == "infeasible":
    for (c0, cf, lab), l in zip(G, sol):
        if l != 0: print(f"      {lab:60s} {float(l):.6g}")
    sys.exit()
def rng(e, hi=10 ** 10):
    c0, cf = e
    le = lambda X: (Fr(X) - c0, {t: -v for t, v in cf.items()}, "le"); ge = lambda X: (c0 - Fr(X), dict(cf), "ge")
    lo_, hi_ = -1, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([le(mid)])[0] == "feasible": hi_ = mid
        else: lo_ = mid
    mn = hi_; lo_, hi_ = mn, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if feas([ge(mid)])[0] == "feasible": lo_ = mid
        else: hi_ = mid
    return mn, lo_
t0 = time.time()
Q = [("b2", comb([(1, E("T", 0, 18)), (2, E("T", 3, 18))])), ("integral norm-4 vectors of M", E("T", 0, 18)),
     ("fractional norm-4 vectors of M, one sign", E("T", 3, 18)), ("fractional norm-26 vectors of L1, one sign", E("X", 3, 117)),
     ("22-cocliques", E("X", 2, 77)), ("class-1 vectors of O of norm 28/9", E("T", 1, 14)),
     ("class-2 vectors of O of norm 40/9", E("T", 2, 20)), ("class-4 vectors of O of norm 34/9", E("T", 4, 17))]
for name, e in Q: print(f"   {name}: {rng(e)}  [{time.time()-t0:.0f}s]", flush=True)
if mode == "branch" and "cert" in sys.argv:
    def cert(e, X, sense):
        c0, cf = e
        extra = [(Fr(X) - c0, {t: -v for t, v in cf.items()}, f"hypothesis <= {X}")] if sense == "le" else [(c0 - Fr(X), dict(cf), f"hypothesis >= {X}")]
        st, sol, it = feas(extra)
        print(f"   certificate for {extra[0][2]}: {st}")
        if st == "infeasible":
            for (c0_, cf_, lab), l in zip(list(G) + extra, sol):
                if l != 0: print(f"        {lab:62s} {float(l):.6g}")
    print("class-2 vectors of O of norm 40/9:"); cert(E("T", 2, 20), 5671, "le")
    print("class-1 vectors of O of norm 28/9:"); cert(E("T", 1, 14), 122, "ge")
    print("fractional norm-4 vectors of one sign:"); cert(E("T", 3, 18), 328, "ge")
    print("fractional norm-26 of one sign:"); cert(E("X", 3, 117), 159, "le")
    # exact expressions of a few L-side first coefficients in the 7 parameters
    labf = {t: free[t] for t in used}
    def show(name, e):
        c0, cf = e
        print(f"   {name} = {c0} " + " ".join(f"{'+' if v > 0 else '-'} {abs(v)}*{labf[t][0]}{labf[t][1]}[{(Z.RHO if labf[t][0]=='T' else Z.SIG)[labf[t][1]] + 9*labf[t][2]}/9]" for t, v in sorted(cf.items())))
    show("fractional norm 26, one sign  X3[13]", E("X", 3, 117))
    show("22-cocliques  X2[77/9]", E("X", 2, 77))
    show("L class-1 norm 178/9  X1[89/9]", E("X", 1, 89))
    show("regular 44-sets  X4[110/9]", E("X", 4, 110))
    show("integral norm 4 of M  T0[2]", E("T", 0, 18))
    show("L class 2, norm 172/9  X2[86/9]", E("X", 2, 86))
    show("L class 1, norm 196/9  X1[98/9]", E("X", 1, 98))
