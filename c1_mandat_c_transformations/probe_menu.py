"""Menu: for each rank, the number of short vectors of L1 that the exact theta programme forces, layer by layer."""
import time
from thetalp import Theta
nmax = 60
top = {37: 10, 39: 12, 41: 12, 43: 13}
for r in (37, 39, 41, 43):
    T = Theta(r, nmax); f = T.form; lin = T.lin
    extra = [lin((1, f("a7")), (-1, f("b1"))), lin((-1, f("a7")), (1, f("b1")))] if r == 43 else []
    m = top[r]; names = [f"a{k}" for k in range(7, m + 1)]
    tot = T.minimum(lin(*[(1, f(n)) for n in names]), extra)
    alone = {}
    for n in names:
        others = [T.le_form(o, 0) for o in names if o != n]
        alone[n] = T.minimum(f(n), extra + others)
    print(f"rank {r}: min sum a7..a{m} = {tot}; each layer alone: {alone}", flush=True)
    # M side: forced numbers beyond the known vectors
    print(f"         min b2 = {T.minimum(f('b2'), extra)}, min b3 = {T.minimum(f('b3'), extra)}, min b4 = {T.minimum(f('b4'), extra)}, max b1 = {T.maximum(f('b1'), extra)}", flush=True)
