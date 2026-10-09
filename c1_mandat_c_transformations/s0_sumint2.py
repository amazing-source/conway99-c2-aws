"""S0: sub-branches of the coupled count / vector-sum congruences (data from s0_sumint.py).
A free layer that is EMPTY, or made only of vertices / lines (whose vectors sum to zero), has vector sum exactly 0:
its coordinate k n / 9 + t is 0, which fixes t.  Question: which sub-branches of S0 survive?
usage: s0_sumint2.py [N]"""
import sys, math, pickle, itertools
from fractions import Fraction as Fr
import z9theta as Z
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
D = pickle.load(open(f"s0_sumint_N{N}.pkl", "rb"))
conds, gen, cused = D["conds"], D["gen"], D["cused"]
RHO, SIG = Z.RHO, Z.SIG
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
lab = lambda f: f"{f[0]}{f[1]}[{expo(f)}/9]"
nc, J = len(cused), len(gen); r = nc + J
names = [("n", f) for f in cused] + [("t", f) for f in gen]
ix = {nm: i for i, nm in enumerate(names)}
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
def test(fixed):
    """fixed: {unknown index: integer value}.  Returns (consistent, index, first failing condition)"""
    keep = [i for i in range(r) if i not in fixed]; q = len(keep)
    x0 = [0] * q; B = [[int(i == j) for j in range(q)] for i in range(q)]; idx = 1
    order = sorted(conds, key=lambda t: (expo(t[2][1]), t[2][0] != "count"))
    for c0, vec, labl in order:
        c0 = c0 + sum(vec[i] * v for i, v in fixed.items()); v2 = [vec[i] for i in keep]
        den = math.lcm(c0.denominator, *[x.denominator for x in v2]) if v2 else c0.denominator
        if den == 1: continue
        a = [int(x * den) for x in v2]; b = int(-c0 * den) % den; m = den
        g = [sum(a[i] * B[i][j] for i in range(q)) % m for j in range(q)]
        c = (b - sum(a[i] * x0[i] for i in range(q))) % m
        for j in range(1, q):
            if g[j] == 0: continue
            G1, x, y = egcd(g[0], g[j]); u0, uj = g[0] // G1, g[j] // G1
            for i in range(q): B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
            g[0], g[j] = G1, 0
        G = math.gcd(g[0], m) if q else m
        if c % G: return False, idx, labl
        mm = m // G
        if mm > 1:
            s1 = ((c // G) * pow((g[0] // G) % mm, -1, mm)) % mm
            for i in range(q): x0[i] += B[i][0] * s1; B[i][0] *= mm
            idx *= mm
    return True, idx, None
def branch(desc, counts):
    """counts: {layer: value} for free layers whose content is known to sum to zero (value = number of vectors)"""
    fixed = {}
    for f, val in counts.items():
        fixed[ix[("n", f)]] = val
        k = f[1]
        assert (k * val) % 9 == 0, (f, val)
        fixed[ix[("t", f)]] = -(k * val) // 9                       # coordinate of the sum = k n/9 + t = 0
    ok, idx, where = test(fixed)
    print(f"{desc}: " + ("consistent" if ok else f"INCONSISTENT at the {where[0]} condition of {lab(where[1])}"), flush=True)
    return ok
T = lambda k, num9: ("T", k, (num9 - RHO[k]) // 9)
print("no hypothesis:", test({})[:2])
co, gv, u, gl = T(2, 11), T(1, 14), T(4, 17), T(3, 18)
branch("no 22-coclique", {co: 0})
branch("no ghost vertex", {gv: 99})
branch("no class-4 vector of O of norm 34/9", {u: 0})
branch("no ghost line", {gl: 231})
branch("no ghost vertex, no ghost line", {gv: 99, gl: 231})
branch("no coclique, no ghost vertex, no ghost line", {co: 0, gv: 99, gl: 231})
branch("PURE: no coclique, no ghost vertex, no class-4 norm 34/9, no ghost line", {co: 0, gv: 99, u: 0, gl: 231})
