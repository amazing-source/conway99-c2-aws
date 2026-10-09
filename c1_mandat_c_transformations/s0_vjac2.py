"""S0: ranges of the seven bottom quantities with the vertex-Jacobi equations and the positivity of all coordinate histograms.
Data from s0_vjac.py.     usage: s0_vjac2.py [N]"""
import sys, pickle, time
from fractions import Fraction as Fr
import exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
D = pickle.load(open(f"s0_vjac_N{N}.pkl", "rb"))
EQ, GE, pname, VAR, NV, red, piv, counts = D["EQ"], D["GE"], D["pname"], D["VAR"], D["NV"], D["red"], D["piv"], D["counts"]
free = [i for i in range(NV) if i not in piv]
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
def build(with_hist=True):
    G = []
    def ge(f):
        c0, cf = subst(f)
        if all(x == 0 for x in cf):
            if c0 < 0: print("   CONSTANT NEGATIVE", c0)
            return
        G.append((c0, cf))
    if with_hist:
        for f, lb in GE: ge(f)
    for key, f in counts.items(): ge(f)
    cnt = lambda c, num9: counts[(c, num9)]
    ge(add(cnt(3, 126), aff(-231))); ge(add(cnt(1, 98), aff(-99))); ge(add(cnt(2, 140), aff(-693)))
    ge(add(cnt(3, 126), sc(cnt(2, 77), -22), aff(-231)))
    return G
cnt = lambda c, num9: counts[(c, num9)]
Q = [("kappa", cnt(2, 77)), ("g_v", add(cnt(1, 98), aff(-99))), ("u", cnt(4, 119)), ("g_l", add(cnt(3, 126), aff(-231))), ("c1", cnt(1, 89)),
     ("w", cnt(2, 95)), ("s44", cnt(4, 110)), ("n (P3/N25)", cnt(2, 104)), ("P1/N23 (class 2, norm 172/9)", cnt(2, 86))]
def rng(G, f, hi=10 ** 9):
    c0, cf = subst(f)
    le = lambda X: (Fr(X) - c0, [-v for v in cf]); gE = lambda X: (c0 - Fr(X), list(cf))
    lo_, hi_ = -1, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if exact_lp.solve(G + [le(mid)])[0] == "feasible": hi_ = mid
        else: lo_ = mid
    mn = hi_; lo_, hi_ = mn, hi
    while hi_ - lo_ > 1:
        mid = (lo_ + hi_) // 2
        if exact_lp.solve(G + [gE(mid)])[0] == "feasible": lo_ = mid
        else: hi_ = mid
    return mn, lo_
for flag in (True,):
    G = build(flag)
    st = exact_lp.solve(G)[0]
    print(f"{'with' if flag else 'without'} the coordinate histograms: {st}, {len(G)} inequalities", flush=True)
    if st != "feasible": continue
    for name, f in Q: print(f"   {name}: {rng(G, f)}   [{time.time()-t0:.0f}s]", flush=True)
