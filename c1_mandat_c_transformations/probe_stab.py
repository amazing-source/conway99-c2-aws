"""Stability in the truncation of the forced numbers (every value is a valid lower bound at any truncation)."""
import time
from thetalp import Theta
for nmax in (40, 60, 84):
    t0 = time.time()
    T = Theta(37, nmax); f = T.form; lin = T.lin
    m37 = T.minimum(lin((1, f("a7")), (1, f("a8")), (1, f("a9")), (1, f("a10"))))
    T = Theta(43, nmax); f = T.form; lin = T.lin
    eq = [lin((1, f("a7")), (-1, f("b1"))), lin((-1, f("a7")), (1, f("b1")))]
    m43 = T.minimum(f("b2"), eq); m43b = T.minimum(f("b2"), eq + [T.le_form("b1", 0)])
    out = {}
    for r in (39, 41):
        Tr = Theta(r, nmax)
        out[r] = (Tr.minimum(Tr.form("b2")), Tr.feasible([Tr.le_form(f"a{k}", 0) for k in range(7, 12)]))
    print(f"nmax {nmax}: rank 37 min(a7+a8+a9+a10) = {m37}; rank 43 min b2 = {m43} (b1 = 0: {m43b}); ranks 39, 41 (min b2, a7..a11 = 0 feasible): {out}  [{time.time()-t0:.0f}s]", flush=True)
