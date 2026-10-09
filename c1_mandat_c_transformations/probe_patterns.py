"""For each rank: which sets S of short layers (norms 14..2*top) can be the ONLY non-empty ones?  Minimal feasible
supports = exact 'one of these layers is non-empty' statements.  Exact rational LP, truncation 60."""
import itertools, time
from thetalp import Theta
nmax = 60
top = {37: 10, 39: 12, 41: 12, 43: 13}
for r in (37, 39, 41, 43):
    T = Theta(r, nmax); f = T.form; lin = T.lin
    extra = [lin((1, f("a7")), (-1, f("b1"))), lin((-1, f("a7")), (1, f("b1")))] if r == 43 else []
    layers = list(range(7, top[r] + 1)); feas = {}
    t0 = time.time()
    for k in range(0, len(layers) + 1):
        for S in itertools.combinations(layers, k):
            if any(set(m) <= set(S) for m in feas if feas[m]):      # a superset of a feasible support is feasible
                continue
            zero = [T.le_form(f"a{n}", 0) for n in layers if n not in S]
            feas[S] = T.feasible(extra + zero)
    minimal = [S for S in feas if feas[S]]
    print(f"rank {r}: minimal feasible supports among norms {[2*n for n in layers]}: {[[2*n for n in S] for S in minimal]}  [{time.time()-t0:.0f}s]", flush=True)
