"""Nine-class programme: certified UPPER bounds.  N22 = number of 22-cocliques = L-side class 2 at norm 154/9.
Fano vectors = ordered pairs of 22-cocliques meeting in 15 points (note 192), so a7 <= N22 (N22 - 1)."""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
from z9q import prepare, feasible, form

def maximum(G, f, hi=10 ** 15):
    c0, cf = f
    flo = lambda X: (c0 - Fr(X), dict(cf), "floor")
    if feasible(G, [flo(hi)]): return "unbounded (> 1e15)"
    if not feasible(G, [flo(0)]): return None
    lo = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if feasible(G, [flo(mid)]): lo = mid
        else: hi = mid
    return lo

N = int(sys.argv[2]) if len(sys.argv) > 2 else 32
r = int(sys.argv[1]); t0 = time.time()
Mo, free, G, expr = prepare(r, N)
n22 = form(expr, [(1, ("X", 2, 77))])
print(f"rank {r}: max number of 22-cocliques N22 = {maximum(G, n22)}  [{time.time()-t0:.0f}s]", flush=True)
for name, key in (("fractional norm 22 (class 3)", ("X", 3, 99)), ("regular 44-sets (class 4, norm 220/9)", ("X", 4, 110)),
                  ("class-1 vectors of norm 178/9", ("X", 1, 89)), ("class-1 vectors of O of norm 28/9 (99 + ghosts)", ("T", 1, 14)),
                  ("M class-2 vectors of norm 22/9", ("T", 2, 11)), ("a7", ("X", 0, 63))):
    print(f"   max {name} = {maximum(G, form(expr, [(1, key)]))}  [{time.time()-t0:.0f}s]", flush=True)
