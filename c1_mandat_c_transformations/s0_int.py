"""Rank 43, scenario S0 (no root, no vector of L1 of norm 16..24), nine-class programme with all class equalities:
every class count is an affine function of 7 integer parameters, with denominators.  INTEGRALITY test:
is there an integer parameter vector making every count a non-negative integer?
Step 1: the lattice of parameter vectors satisfying all the congruences (exact).  Step 2: its points in the polytope."""
import sys, time, math
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
        j += 1
Mo.fix("X", 0, 63, 0)
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
exprs = [(nm, e) for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top]
used = sorted({t for _, e in exprs for t in e[1]}); r = len(used)
print("parameters:", [free[t] for t in used])
# ---- step 1: congruences  c0 + sum cf_i t_i in Z
def egcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
t0 = [0] * r; B = [[int(i == j) for j in range(r)] for i in range(r)]       # columns of B = basis
index = 1; ok = True
for nm, (c0, cf) in exprs:
    den = math.lcm(c0.denominator, *[v.denominator for v in cf.values()]) if cf else c0.denominator
    if den == 1: continue
    a = [int(cf.get(t, Fr(0)) * den) for t in used]; b = int(-c0 * den) % den; m = den
    # congruence a.t = b mod m with t = t0 + B s
    g = [sum(a[i] * B[i][j] for i in range(r)) % m for j in range(r)]
    c = (b - sum(a[i] * t0[i] for i in range(r))) % m
    # unimodular column operations on (g; B) to bring g to (G1, 0, ..., 0)
    for j in range(1, r):
        if g[j] == 0: continue
        G1, x, y = egcd(g[0], g[j])
        u0, uj = g[0] // G1, g[j] // G1
        for i in range(r):
            B[i][0], B[i][j] = x * B[i][0] + y * B[i][j], -uj * B[i][0] + u0 * B[i][j]
        g[0], g[j] = G1, 0
    G = math.gcd(g[0], m)
    if c % G:
        print(f"CONGRUENCES INCONSISTENT at {nm}: {a} . t = {b} mod {m}"); ok = False; break
    mm = m // G
    if mm > 1:
        inv = pow((g[0] // G) % mm, -1, mm) if mm > 1 else 0
        s1 = ((c // G) * inv) % mm
        for i in range(r): t0[i] += B[i][0] * s1; B[i][0] *= mm
        index *= mm
if ok:
    print(f"the congruences are consistent; admissible parameter vectors form a coset of a lattice of index {index} = {dict((p, e) for p, e in __import__('sympy').factorint(index).items()) if False else index}")
    import json
    json.dump({"t0": t0, "B": B, "index": index}, open("s0_int_lattice.json", "w"))

# ---- step 2: integer points of the polytope in the admissible coset
if ok:
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds, linprog
    # inequalities c0 + cf.t >= lb  for every count (lb = known lower bounds)
    E = lambda side, c, num9: expr[(side, c, (num9 - (Z.RHO if side == "T" else Z.SIG)[c]) // 9)]
    LB = {("T", 3, 2): 231, ("T", 1, 1): 99, ("T", 2, 2): 693}
    rows = []
    for nm, (c0, cf) in exprs:
        rows.append((c0 - LB.get(nm, 0), [cf.get(t, Fr(0)) for t in used], str(nm)))
    e1, e2 = E("T", 3, 18), E("X", 2, 77)                                   # 22 profile-C vectors of each sign per coclique
    rows.append((e1[0] - 22 * e2[0] - 231, [e1[1].get(t, Fr(0)) - 22 * e2[1].get(t, Fr(0)) for t in used], "profile C"))
    # LLL-reduce the lattice basis (columns of B) with a diagonal weighting ~ the widths of the polytope
    def lll(cols, delta=Fr(3, 4)):
        n = len(cols); b = [list(map(Fr, c)) for c in cols]
        def gs():
            bs = []; mu = [[Fr(0)] * n for _ in range(n)]
            for i in range(n):
                v = b[i][:]
                for j in range(i):
                    mu[i][j] = sum(x * y for x, y in zip(b[i], bs[j])) / sum(y * y for y in bs[j])
                    v = [x - mu[i][j] * y for x, y in zip(v, bs[j])]
                bs.append(v)
            return bs, mu
        k = 1
        while k < n:
            bs, mu = gs()
            for j in range(k - 1, -1, -1):
                q = round(mu[k][j])
                if q: b[k] = [x - q * y for x, y in zip(b[k], b[j])]; bs, mu = gs()
            if sum(x * x for x in bs[k]) >= (delta - mu[k][k - 1] ** 2) * sum(x * x for x in bs[k - 1]): k += 1
            else: b[k], b[k - 1] = b[k - 1], b[k]; k = max(k - 1, 1)
        return [[int(x) for x in v] for v in b]
    cols = lll([[B[i][j] for i in range(r)] for j in range(r)])
    Bm = np.array(cols, dtype=object).T                                         # r x r, columns = reduced basis
    # constraints in s:  c0 + cf.(t0 + B s) >= 0
    A_s = []; b_s = []
    for c0, cf, lab in rows:
        w = [sum(cf[i] * Bm[i][j] for i in range(r)) for j in range(r)]; const = c0 + sum(cf[i] * t0[i] for i in range(r))
        sc = max([abs(x) for x in w] + [abs(const), Fr(1)])
        A_s.append([float(x / sc) for x in w]); b_s.append(float(-const / sc))
    A_s = np.array(A_s); b_s = np.array(b_s)
    res = milp(c=np.zeros(r), constraints=LinearConstraint(A_s, lb=b_s, ub=np.inf), integrality=np.ones(r), bounds=Bounds(-1e9, 1e9), options={"time_limit": 200})
    print("MILP status:", res.status, res.message)
    if res.x is not None:
        s = [int(round(v)) for v in res.x]; t = [t0[i] + sum(int(Bm[i][j]) * s[j] for j in range(r)) for i in range(r)]
        vals = [(lab, c0 + sum(cf[i] * t[i] for i in range(r))) for c0, cf, lab in rows]
        good = all(v >= 0 for _, v in vals) and all((c0 + sum(cf.get(used[i], Fr(0)) * t[i] for i in range(r))).denominator == 1 for _, (c0, cf) in exprs)
        print("integer parameter vector:", dict(zip([str(free[u]) for u in used], t)))
        print("exact check (all counts non-negative integers, lower bounds respected):", good)
        if not good: print("   failing:", [(lab, str(v)) for lab, v in vals if v < 0][:5])
