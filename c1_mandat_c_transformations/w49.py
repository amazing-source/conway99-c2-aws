"""Rank 43: the 49 classes of L1 / sqrt7 M (anisotropic plane over F_7) one by one, exactly.

At rank 43, M is even of rank 44 and determinant 49, with anisotropic discriminant plane.  N_4 = O_K + O_K
(O_K = integers of Q(sqrt -7), Gram [[2,1],[1,4]]) has the opposite discriminant form, so M + N_4 glues to an even
unimodular lattice of rank 48, and for every harmonic polynomial h on the N_4 part (degree m)
        sum over classes d of  Theta_d(tau) theta_{d,h}(tau)   is a modular form of weight 24 + m for SL_2(Z),
where Theta_d is the theta series of the class of M^* = L1/sqrt7 glued to d (exponent = norm in L1 / 14).
The radial averages are the L1 programme; the rest is the class-level information.
Question: which exact linear relations hold among the numbers of vectors of norm 16..26 in the individual classes?"""
import sys, itertools, time
from fractions import Fraction as Fr
from math import factorial
from flint import fmpq, fmpq_mat

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6           # truncation of all q-series (exponent <= N)
MAXDEG = int(sys.argv[2]) if len(sys.argv) > 2 else 10
G2 = [[2, 1], [1, 4]]


def zonal(m, d=4):
    out = []
    for i in range(m // 2 + 1):
        den = factorial(i) * factorial(m - 2 * i) * 4 ** i
        for j in range(1, i + 1): den *= (d // 2 + m - 1 - j)
        out.append(Fr((-1) ** i * factorial(m), den))
    return out


# ---------- vectors of O_K^*: (x e1 + y e2)/7 with x + 4y = 0 mod 7; class c = -y mod 7; norm (2x^2+2xy+4y^2)/49
def block(maxnorm):
    out = []; B = int((49 * maxnorm) ** 0.5) + 2
    for x in range(-B, B + 1):
        for y in range(-B, B + 1):
            if (x + 4 * y) % 7: continue
            n49 = 2 * x * x + 2 * x * y + 4 * y * y
            if n49 <= 49 * maxnorm: out.append((x, y, (-y) % 7, n49))
    return out


BL = block(2 * N + 2)
def ip49(u, v):            # 49 * inner product of two vectors given by integer coordinates (x, y) in units of 1/7
    return 2 * u[0] * v[0] + u[0] * v[1] + u[1] * v[0] + 4 * u[1] * v[1]

POLES = [((7, 0), (0, 0)), ((7, 0), (7, 0)), ((7, 0), (0, 7)), ((0, 7), (7, 7)), ((7, 7), (14, -7)), ((14, 7), (7, 21)),
         ((7, -14), (21, 7)), ((21, 7), (-7, 14)), ((7, 28), (14, 7)), ((35, 7), (7, -21))]


def class_series(m, pole):
    """{(c1, c2): {E7: value}}: sum over a in class (c1,c2) of Z_m(a) q^(a^2/2), exponent = E7/7 ... stored by 98*exponent"""
    cz = zonal(m); v2 = Fr(ip49(pole[0], pole[0]) + ip49(pole[1], pole[1]), 49)
    out = {}
    for a1 in BL:
        for a2 in BL:
            n49 = a1[3] + a2[3]
            if n49 > 98 * N: continue
            av = Fr(ip49(a1, pole[0]) + ip49(a2, pole[1]), 49); a2n = Fr(n49, 49)
            val = sum(c * av ** (m - 2 * i) * (v2 * a2n) ** i for i, c in enumerate(cz))
            if val == 0: continue
            d = (a1[2], a2[2]); key = n49                      # exponent a^2/2 = n49/98
            dd = out.setdefault(d, {}); dd[key] = dd.get(key, Fr(0)) + val
    return out


# ---------- level-1 forms
def sigma(n, k): return sum(d ** k for d in range(1, n + 1) if n % d == 0)
E4 = [1] + [240 * sigma(n, 3) for n in range(1, N + 1)]
E6 = [1] + [-504 * sigma(n, 5) for n in range(1, N + 1)]
def mul(f, g): return [sum(f[i] * g[n - i] for i in range(n + 1)) for n in range(N + 1)]
def level1(k):
    out = []
    for b in range(k // 6 + 1):
        if (k - 6 * b) % 4 == 0:
            a = (k - 6 * b) // 4; f = [1] + [0] * N
            for _ in range(a): f = mul(f, E4)
            for _ in range(b): f = mul(f, E6)
            out.append(f)
    return out


# ---------- unknowns: classes d up to sign; exponent of Theta_d = (rho_d + 7 j)/7 with rho_d = -2(c1^2+c2^2) mod 7
reps = []
for c1 in range(7):
    for c2 in range(7):
        d = (c1, c2); nd = ((-c1) % 7, (-c2) % 7)
        if nd < d: continue
        reps.append(d)
rho = {d: (-2 * (d[0] ** 2 + d[1] ** 2)) % 7 for d in reps}
names = []; index = {}
for d in reps:
    j = 0
    while rho[d] + 7 * j <= 7 * N: index[("T", d, j)] = len(names); names.append(("T", d, j)); j += 1
funcs = [(m, p) for m in range(0, MAXDEG + 1, 2) for p in (POLES if m else POLES[:1])]
rows = []; t0 = time.time()
for fi, (m, pole) in enumerate(funcs):
    cs = class_series(m, pole); basis = level1(24 + m)
    xs = []
    for i in range(len(basis)): index[("x", fi, i)] = len(names); names.append(("x", fi, i)); xs.append(index[("x", fi, i)])
    for n in range(N + 1):
        row = {xs[i]: Fr(basis[i][n]) for i in range(len(basis)) if basis[i][n]}
        for d in reps:
            w = 1 if d == (0, 0) else 2
            ser = cs.get(d, {})
            if d != (0, 0):
                # theta_{d,h} + theta_{-d,h} = 2 theta_{d,h} for even m
                pass
            for n49, val in ser.items():
                # exponent of Theta_d: n - n49/98 = (98 n - n49)/98 must be (rho + 7j)/7
                num = 98 * n - n49
                if num < 0 or num % 14: continue
                e7 = num // 14
                if (e7 - rho[d]) % 7 or e7 < rho[d]: continue
                v = index.get(("T", d, (e7 - rho[d]) // 7))
                if v is not None: row[v] = row.get(v, Fr(0)) - w * val
        rows.append(row)
print(f"{len(reps)} classes up to sign, {len(funcs)} functionals, {len(names)} unknowns, {len(rows)} equations  [{time.time()-t0:.0f}s]", flush=True)


def solve(extra):
    nv = len(names)
    cls = sorted([i for i, n in enumerate(names) if n[0] == "T"], key=lambda i: -(rho[names[i][1]] + 7 * names[i][2]))
    order = [i for i, n in enumerate(names) if n[0] == "x"] + cls; pos = {v: p for p, v in enumerate(order)}
    allrows = rows + [r for r, _ in extra]; rhs = [Fr(0)] * len(rows) + [b for _, b in extra]
    M = fmpq_mat(len(allrows), nv + 1)
    for i, (row, b) in enumerate(zip(allrows, rhs)):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
        M[i, nv] = fmpq(b.numerator, b.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv + 1) if R[i, j] != 0) for i in range(rk)]
    free = [p for p in range(nv) if p not in set(piv)]
    return (nv not in piv), [names[order[p]] for p in free], R, piv, order

ok, free, R, piv, order = solve([])
edge = lambda nm: nm[0] == "T" and rho[nm[1]] + 7 * nm[2] > 7 * (N - 2)
print("modularity alone: consistent", ok, "free", len(free), "of which near the truncation edge", sum(1 for f in free if edge(f)))
zeros = [({index[("T", d, 0)]: Fr(1)}, Fr(0)) for d in reps if d != (0, 0)] + [({index[("T", (0, 0), 0)]: Fr(1)}, Fr(1))]
ok, free, R, piv, order = solve(zeros)
inner = [f for f in free if not edge(f)]
print("with the zeros (no vector of norm < 14 outside sqrt7 M) and Theta_0[0] = 1: consistent", ok, "free", len(free), "genuine", len(inner))
print("genuine free parameters:", [(f[1], f"{rho[f[1]] + 7 * f[2]}/7") for f in inner if f[0] == "T"], [f for f in inner if f[0] == "x"])


# ---------- explicit relations: every class variable as an affine function of the genuine free ones
def expressions(R, piv, order, free_names):
    nv = len(names); fpos = {order.index(index[f]): t for t, f in enumerate(free_names)}
    expr = {}
    for i, p in enumerate(piv):
        nm = names[order[p]]
        if nm[0] != "T": continue
        c0 = Fr(int(R[i, nv].p), int(R[i, nv].q)); cf = {}
        for q_, t in fpos.items():
            v = R[i, q_]
            if v != 0: cf[t] = -Fr(int(v.p), int(v.q))
        expr[nm] = (c0, cf)
    for t, f in enumerate(free_names):
        if f[0] == "T": expr[f] = (Fr(0), {t: Fr(1)})
    return expr

if "relations" in sys.argv:
    ok, free, R, piv, order = solve(zeros)
    expr = expressions(R, piv, order, free)
    lab = lambda f: f"n[{f[1][0]},{f[1][1]}]({2 * (rho[f[1]] + 7 * f[2])})" if f[1] != (0, 0) else f"b{f[2]}"
    print("\nnotation: n[c1,c2](norm) = number of vectors of L1 of that norm in the class (c1,c2) (and as many in the opposite class); b_k = vectors of norm 2k of M")
    for d in reps:
        if d == (0, 0): continue
        nm = ("T", d, 1)
        c0, cf = expr[nm]
        if list(cf.items()) == [(free.index(nm), Fr(1))] if nm in free else False: continue
        print(f"{lab(nm)} = {c0}" + "".join(f" {'+' if v > 0 else '-'} {abs(v)} {lab(free[t])}" for t, v in sorted(cf.items()) if not edge(free[t]) or True))
    for k in (2, 3):
        c0, cf = expr[("T", (0, 0), k)]
        print(f"b{k} = {c0}" + "".join(f" {'+' if v > 0 else '-'} {abs(v)} {lab(free[t])}" for t, v in sorted(cf.items())))
