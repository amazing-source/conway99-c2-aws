import pickle, math
from fractions import Fraction as Fr
import jac_lines2 as J
M, L = J.M, J.L
dens = {}
for side, tab in (("M", M), ("L", L)):
    for key, f in sorted(tab.items()):
        d = math.lcm(*[x.denominator for x in f])
        if d > 1: dens.setdefault(d, []).append((side, key))
print("denominators appearing in the coefficients (as functions of p, q):", {d: len(v) for d, v in dens.items()} or "none: all coefficients are integer combinations")
# tightest constraints: list the edges of the feasible polygon
import itertools
cons = [(f, f"c{key}") for key, f in M.items() if f[1:] != [0, 0]] + [(f, f"cL{key}") for key, f in L.items() if f[1:] != [0, 0]]
def feas(pt): return all(f[0] + f[1] * pt[0] + f[2] * pt[1] >= 0 for f, _ in cons)
verts = []
for (f, a), (g, b) in itertools.combinations(cons, 2):
    det = f[1] * g[2] - f[2] * g[1]
    if det == 0: continue
    p = (-f[0] * g[2] + f[2] * g[0]) / det; q = (-f[1] * g[0] + f[0] * g[1]) / det
    if feas((p, q)): verts.append((float(p), float(q), a, b))
verts.sort()
print("vertices of the feasible polygon (p, q) and the two active constraints:")
for v in verts: print("   p = %.1f, q = %.1f   %s, %s" % v)
