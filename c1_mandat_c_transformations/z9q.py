"""Forced numbers in the nine-class programme, to compare with the L1 programme (380 / 2367 / 234 / 165, b2 >= 913)."""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp

def prepare(r, N, drop=()):
    Mo, free, G = z9lp.build(r, N)
    G = [g for g in G if g[2] not in drop]
    # expressions of the class variables again (same elimination order as in build)
    free2, expr = z9lp.reduce(Mo)
    assert free2 == free
    return Mo, free, G, expr

def dense(G, extra, nfree):
    used = sorted({t for _, cf, _ in list(G) + list(extra) for t in cf}); remap = {t: i for i, t in enumerate(used)}
    return [(c0, [Fr(0)] * len(used)) for c0, _, _ in []] or [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in list(G) + list(extra)]

def feasible(G, extra=()):
    return exact_lp.solve(dense(G, extra, None))[0] == "feasible"

def form(expr, terms):
    c0 = Fr(0); cf = {}
    for coef, (side, k, num9) in terms:
        res = (Z.RHO if side == "T" else Z.SIG)[k]
        e = expr[(side, k, (num9 - res) // 9)]
        c0 += coef * e[0]
        for t, v in e[1].items(): cf[t] = cf.get(t, Fr(0)) + coef * v
    return c0, cf

def minimum(G, f, hi=10 ** 13):
    c0, cf = f
    cap = lambda X: (Fr(X) - c0, {t: -v for t, v in cf.items()}, "cap")
    if not feasible(G, [cap(hi)]): return None
    if feasible(G, [cap(0)]): return 0
    lo = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if feasible(G, [cap(mid)]): hi = mid
        else: lo = mid
    return hi

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    t0 = time.time()
    Mo, free, G, expr = prepare(35, N)
    print("rank 35 with all constraints:", "feasible" if feasible(G) else "INFEASIBLE", f"[{time.time()-t0:.0f}s]", flush=True)
    G2 = [g for g in G if g[2] != "a7<=990"]
    print("rank 35 without the Fano packing bound a7 <= 990:", "feasible" if feasible(G2) else "INFEASIBLE", flush=True)
    top = {37: 10, 39: 12, 41: 12, 43: 13}
    for r in (37, 39, 41, 43):
        Mo, free, G, expr = prepare(r, N)
        a = lambda n: [(1, ("X", 0, 9 * n)), (2, ("X", 3, 9 * n))]
        tot = form(expr, sum((a(n) for n in range(7, top[r] + 1)), []))
        b2 = form(expr, [(1, ("T", 0, 18)), (2, ("T", 3, 18))])
        print(f"rank {r}: min sum a7..a{top[r]} = {minimum(G, tot)}; min b2 = {minimum(G, b2)}; "
              f"min class-1 vectors of norm 28/9 = {minimum(G, form(expr, [(1, ('T', 1, 14))]))}; "
              f"min fractional norm 22 (class 3) = {minimum(G, form(expr, [(1, ('X', 3, 99))]))}  [{time.time()-t0:.0f}s]", flush=True)
