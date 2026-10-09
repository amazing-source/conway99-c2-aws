"""Line Jacobi form in S0: PARITY conditions.  For r = 2 the map x -> h_l - x is a fixed-point-free involution of
{(x, l): |x|^2 = 2n, <x,h_l> = 2}, and for r = 0, x -> -x is one (n >= 1).  So c(n,2), c(n,0), cL(N,2), cL(N,0) are EVEN.
With p = 2 p', q = 2 q' : are these parities compatible?"""
import io, contextlib, math
from fractions import Fraction as Fr
with contextlib.redirect_stdout(io.StringIO()):
    import jac_lines2 as J
M, L = J.M, J.L
conds = []
for side, tab in (("c", M), ("cL", L)):
    for (n, r), f in sorted(tab.items()):
        if r in (0, 2): conds.append((f"{side}({n},{r})", f))
# f = A + B p + C q, p = 2p', q = 2q'  ->  A + 2B p' + 2C q' must be even:  A/2 + B p' + C q' integer
bad = [(lab, [str(x) for x in f]) for lab, f in conds if any(x.denominator != 1 for x in f)]
print("non-integer coefficient forms:", bad[:3] or "none")
odd_const = [(lab, int(f[0]), int(f[1]), int(f[2])) for lab, f in conds if int(f[0]) % 2 == 1]
print("forms with an odd constant term:", odd_const[:10] or "none", " (total", len(odd_const), "of", len(conds), ")")
# finer: mod 4 structure etc. via the general congruence solver on (p', q')
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
x0 = [0, 0]; B = [[1, 0], [0, 1]]; idx = 1; ok = True
for lab, f in conds:
    c0 = f[0] / 2; vec = [f[1], f[2]]                         # c0 + vec.(p', q') integer
    den = math.lcm(c0.denominator, *[x.denominator for x in vec])
    if den == 1: continue
    a = [int(x * den) for x in vec]; b_ = int(-c0 * den) % den; m = den
    g = [sum(a[i] * B[i][j] for i in range(2)) % m for j in range(2)]
    c = (b_ - sum(a[i] * x0[i] for i in range(2))) % m
    if g[1]:
        G1, x, y = egcd(g[0], g[1]); u0, u1 = g[0] // G1, g[1] // G1
        for i in range(2): B[i][0], B[i][1] = x * B[i][0] + y * B[i][1], -u1 * B[i][0] + u0 * B[i][1]
        g = [G1, 0]
    G = math.gcd(g[0], m)
    if c % G: print("PARITY INCONSISTENT at", lab, [str(x) for x in f]); ok = False; break
    mm = m // G
    if mm > 1:
        s1 = ((c // G) * pow((g[0] // G) % mm, -1, mm)) % mm
        for i in range(2): x0[i] += B[i][0] * s1; B[i][0] *= mm
        idx *= mm
if ok: print("parities compatible; (p', q') in a coset of index", idx, ": p' =", x0[0], "+", [B[0][0], B[0][1]], " q' =", x0[1], "+", [B[1][0], B[1][1]])
