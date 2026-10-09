"""S0, line Jacobi form class by class: what do the exact Jacobi equations and the positivity of all pair counts leave?
Data from s0_jac9.py.     usage: s0_jac9b.py [N] [delta3]"""
import sys, pickle, time
from fractions import Fraction as Fr
import exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 32
D = pickle.load(open(f"s0_jac9_N{N}.pkl", "rb")); S = pickle.load(open(f"s0_jac9_sol_N{N}.pkl", "rb"))
EQ, GE, pname, VAR, NV, counts = D["EQ"], D["GE"], D["pname"], D["VAR"], D["NV"], D["counts"]
red, piv, free = S["red"], S["piv"], S["free"]
t0 = time.time()
def aff(const=0): return [Fr(const)] + [Fr(0)] * NV
def add(*fs): return [sum(x) for x in zip(*fs)]
def sc(f, s): return [x * s for x in f]
def subst(f):
    c0 = f[0]; cf = {i: Fr(0) for i in free}
    for i in range(NV):
        x = f[1 + i]
        if x == 0: continue
        if i in piv:
            rw = red[piv.index(i)]; c0 += x * rw[-1]
            for k in free: cf[k] -= x * rw[k]
        else: cf[i] += x
    return c0, [cf[k] for k in free]
G = []; labels = []
def ge(f, lb):
    c0, cf = subst(f)
    if all(x == 0 for x in cf):
        if c0 < 0: print(f"   CONSTANT NEGATIVE: {lb}: {c0}")
        return
    G.append((c0, cf)); labels.append(lb)
for f, lb in GE: ge(f, lb)
cnt = lambda c, num9: counts[(c, num9)]
# known objects: lower bounds on counts and on pair counts
ge(add(cnt(3, 126), aff(-231)), "231 lines"); ge(add(cnt(1, 98), aff(-99)), "99 vertices"); ge(add(cnt(2, 140), aff(-693)), "693 edges")
ge(add(cnt(3, 126), sc(cnt(2, 77), -22), aff(-231)), "22 profile-C vectors per 22-coclique")
# vertex vectors 7Ee_v (class 1, exponent 98/9): line sums 4/3 (7 lines), -2/3 (84 lines), 1/3 (140 lines)
ge(add(VAR[(1, 98, 4)], aff(-99 * 7)), "vertices: s = 4/3"); ge(add(VAR[(1, 98, -2)], aff(-99 * 84)), "vertices: s = -2/3"); ge(add(VAR[(1, 98, 1)], aff(-99 * 140)), "vertices: s = 1/3")
st, sol, it = exact_lp.solve(G)
print(f"S0 with the Jacobi equations, positivity of all pair counts and the known objects: {st}  [{time.time()-t0:.0f}s]", flush=True)
if st == "infeasible":
    for (c0, cf), lb, l in zip(G, labels, sol):
        if l != 0: print(f"      {lb:48s} {float(l):.6g}")
    sys.exit()
def rng(f, hi=10 ** 12):
    c0, cf = subst(f)
    le = lambda X: (Fr(X) - c0, [-v for v in cf]); gE = lambda X: (c0 - Fr(X), list(cf))
    lo_, hi_ = -hi, hi
    if exact_lp.solve(G + [le(lo_)])[0] == "feasible": mn = None
    else:
        while hi_ - lo_ > 1:
            mid = (lo_ + hi_) // 2
            if exact_lp.solve(G + [le(mid)])[0] == "feasible": hi_ = mid
            else: lo_ = mid
        mn = hi_
    lo_, hi_ = -hi, hi
    if exact_lp.solve(G + [gE(hi_)])[0] == "feasible": mx = None
    else:
        while hi_ - lo_ > 1:
            mid = (lo_ + hi_) // 2
            if exact_lp.solve(G + [gE(mid)])[0] == "feasible": lo_ = mid
            else: hi_ = mid
        mx = lo_
    return mn, mx
n = cnt(2, 104); Dl = VAR[(2, 104, -4)]
print("P3/N25 layer (class 2, norm 208/9): count n:", rng(n), flush=True)
print("   sum of delta over the layer minus 3 n (Codex: delta >= 3 for every vector):", rng(add(Dl, sc(n, -3))), flush=True)
print("   9 n minus sum of delta:", rng(add(sc(n, 9), sc(Dl, -1))), flush=True)
for name, f in (("22-cocliques", cnt(2, 77)), ("ghost vertices", add(cnt(1, 98), aff(-99))), ("ghost lines", add(cnt(3, 126), aff(-231))),
                ("class-1 norm 178/9", cnt(1, 89)), ("regular 44-sets", cnt(4, 110)), ("class-4 norm 238/9", cnt(4, 119)),
                ("fractional norm 26, one sign", cnt(3, 117)), ("class-2 norm 40/9 of O", cnt(2, 140))):
    print(f"   {name}: {rng(f)}   [{time.time()-t0:.0f}s]", flush=True)
