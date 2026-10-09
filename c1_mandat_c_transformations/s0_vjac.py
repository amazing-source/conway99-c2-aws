"""S0 (rank 43): the VERTEX JACOBI FORM class by class.

For y in L_9 of class c and a vertex v, write Y = 9 y_v (an integer = c mod 9).  The translation y -> y + 7Ee_v (class 1, norm 196/9,
coordinate 28/9 at v) and the symmetry y -> -y give, for  N(c, e, Y) = #{(y, v): y of class c, |y|^2/2 = e, 9 y_v = Y}:
        N(c, e, Y) = N(c + 1, e + (98 + 7Y)/9, Y + 28) = N(-c, e, -Y).
There are 15 classes of pairs: the reduced values are Y in {0, +-9} (class 0), {-8, 1, 10} (class 1), {-7, 2, 11} (class 2),
{-6, 3, 12} (class 3), {-14, -5, 4, 13} (class 4).  With the moments  sum 1 = 99 n,  sum Y = 0,  sum Y^2 = 81 |y|^2 n,
sum Y^3 = 729 x (cubic sum of the layer), every layer of the classes 1, 2, 3 gives ONE EXACT LINEAR EQUATION: its cubic sum
P_3 = sum_v y_v^3 is determined by its count and by lower layers.  The cubic sums obey the cubic modular system (14 free in S0).
Discriminating question: is the resulting over-determined linear system consistent, and what does it leave of the 7 parameters?
usage: s0_vjac.py [N]"""
import sys, time, math, pickle
from fractions import Fraction as Fr
import z9theta as Z, z9lp, s0_cubic as SC, mf7, exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
RHO, SIG = Z.RHO, Z.SIG
t0 = time.time(); top = 9 * (N - 9)
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (RHO[c] + 9 * j) <= 9 * N:
        num9 = RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "rank43")
        j += 1
Mo.fix("X", 0, 63, 0)
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)
cfree, cexpr = z9lp.reduce(Mo)
Cs = SC.build(N); qfree3, e3 = SC.reduce(Cs)
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
lab = lambda f: f"{f[0]}{f[1]}[{expo(f)}/9]"
layers = sorted([(SIG[c] + 9 * j, c) for c in range(5) for j in range(0, N + 1) if SIG[c] + 9 * j <= top])
key = lambda c, num9: ("X", c, (num9 - SIG[c]) // 9)
used0, used3 = set(), set()
for num9, c in layers:
    used0 |= set(cexpr[key(c, num9)][1])
    if c: used3 |= set(e3[key(c, num9)])
P0, P3 = sorted(used0), sorted(used3)
NV = len(P0) + len(P3)
pos0 = {t: 1 + i for i, t in enumerate(P0)}; pos3 = {t: 1 + len(P0) + i for i, t in enumerate(P3)}
pname = ["1"] + ["n:" + lab(cfree[t]) for t in P0] + ["c:" + lab(qfree3[t]) for t in P3]
print(f"S0, truncation {N}: {len(P0)} count parameters, {len(P3)} cubic parameters  [{time.time()-t0:.0f}s]", flush=True)
def aff(const=0): return [Fr(const)] + [Fr(0)] * NV
def add(*fs): return [sum(x) for x in zip(*fs)]
def sc(f, s): return [x * s for x in f]
def count_form(c, num9):
    c0, cf = cexpr[key(c, num9)]; f = aff(c0)
    for t, v in cf.items(): f[pos0[t]] = v
    return f
def cubic_form(c, num9):
    f = aff()
    if c == 0: return f
    for t, v in e3[key(c, num9)].items(): f[pos3[t]] = v
    return f
exists = {(c, num9) for num9, c in layers}
RED = {0: (0, 9), 1: (-8, 1, 10), 2: (-7, 2, 11), 3: (-6, 3, 12), 4: (-14, -5, 4, 13)}
VAR = {}
def canon(k, num9, Y):
    while True:
        k %= 9
        if k > 4: k, Y = 9 - k, -Y
        if k == 0 and Y < 0: Y = -Y
        if Y in RED[k]: return k, num9, Y
        if Y > 13: k, num9, Y = k - 1, num9 + 98 - 7 * Y, Y - 28
        elif Y < -13: k, num9, Y = k + 1, num9 + 98 + 7 * Y, Y + 28
        else: raise ValueError((k, num9, Y))
def value(k, num9, Y):
    kr, nr, Yr = canon(k, num9, Y)
    if nr < 0: return aff(0)
    if nr == 0: return aff(99) if (kr == 0 and Yr == 0) else aff(0)
    if (kr, nr) not in exists:
        if nr > top: raise KeyError((kr, nr, Yr))
        return aff(0)
    return VAR[(kr, nr, Yr)]
EQ = []; GE = []; nlay = 0
INV = {}
def vinv(vals):
    if vals not in INV:
        d = len(vals)
        rows = [[Fr(s) ** p for s in vals] + [Fr(int(p == q)) for q in range(d)] for p in range(d)]
        red, piv, _ = mf7.rref(rows); assert piv == list(range(d))
        INV[vals] = [r[d:] for r in red]
    return INV[vals]
for num9, c in layers:
    n = count_form(c, num9); C = cubic_form(c, num9)
    if c == 0 and num9 == 0:
        VAR[(0, 0, 0)] = aff(99); VAR[(0, 0, 9)] = aff(0); continue
    Ymax = math.isqrt(72 * num9 // 9)                      # Y^2 <= 81 * (4/9) * |y|^2 = 36 * 2 num9 / 9 = 8 num9
    R = [sc(n, 99), aff(0), sc(n, 18 * num9), sc(C, 729)]
    allvals = [Y for Y in range(-Ymax, Ymax + 1) if (Y - c) % 9 == 0]
    red_here = [Y for Y in allvals if (Y in RED[c]) or (c == 0 and -Y in RED[0])]
    empty = all(x == 0 for x in n)
    if empty:
        assert all(x == 0 for x in C), (c, num9)
        for Y in allvals:
            if Y in red_here:
                kr, nr, Yr = canon(c, num9, Y)
                if (kr, nr, Yr) in VAR and any(x != 0 for x in VAR[(kr, nr, Yr)]): EQ.append((VAR[(kr, nr, Yr)], f"empty layer class {c}, {num9}/9, Y = {Y}"))
                VAR.setdefault((kr, nr, Yr), aff(0))
            else:
                v = value(c, num9, Y)
                if any(x != 0 for x in v): EQ.append((v, f"empty layer class {c}, {num9}/9, Y = {Y}"))
        for Y in RED[c]: VAR.setdefault((c, num9, Y), aff(0))
        continue
    for Y in allvals:
        if Y in red_here: continue
        v = value(c, num9, Y)
        for p in range(4): R[p] = add(R[p], sc(v, -Fr(Y) ** p))
    if c == 0:
        n9 = sc(R[2], Fr(1, 162)); n0 = add(R[0], sc(n9, -2))
        VAR[(0, num9, 9)], VAR[(0, num9, 0)] = n9, n0
        new = [(0, n0), (9, n9)]
        for p in (1, 3):
            if any(x != 0 for x in R[p]): EQ.append((R[p], f"class 0, {num9}/9, odd moment {p}"))
    else:
        vals = tuple(Y for Y in RED[c] if Y * Y <= 8 * num9)
        d = len(vals); inv = vinv(vals)
        sol = [add(*[sc(R[p], inv[i][p]) for p in range(d)]) for i in range(d)]
        for Y, f in zip(vals, sol): VAR[(c, num9, Y)] = f
        for Y in RED[c]:
            if Y not in vals: VAR[(c, num9, Y)] = aff(0)
        for p in range(d, 4):
            lhs = add(*([sc(f, Fr(Y) ** p) for Y, f in zip(vals, sol)] + [sc(R[p], -1)]))
            if any(x != 0 for x in lhs): EQ.append((lhs, f"class {c}, exponent {num9}/9, moment {p}"))
        new = list(zip(vals, sol))
    for Y, f in new: GE.append((f, f"N({c}; {num9}/9; Y = {Y}) >= 0"))
    nlay += 1
print(f"{nlay} non-empty layers, {len(EQ)} vertex-Jacobi equations, {len(GE)} pair counts  [{time.time()-t0:.0f}s]", flush=True)
rows = [f[1:] + [-f[0]] for f, _ in EQ]
red, piv, _ = mf7.rref(rows) if rows else ([], [], None)
bad = [rw for rw in red if all(x == 0 for x in rw[:-1]) and rw[-1] != 0]
print(f"rank {len(piv)} in {NV} parameters: " + ("INCONSISTENT" if bad else "consistent"), flush=True)
pickle.dump({"EQ": EQ, "GE": GE, "pname": pname, "VAR": VAR, "NV": NV, "red": red, "piv": piv,
             "counts": {(c, num9): count_form(c, num9) for num9, c in layers}}, open(f"s0_vjac_N{N}.pkl", "wb"))
if bad:
    # show the first inconsistent equation in the order of the layers
    acc = []
    for f, lb in EQ:
        acc.append(f[1:] + [-f[0]]); r2, p2, _ = mf7.rref(acc)
        if any(all(x == 0 for x in rw[:-1]) and rw[-1] != 0 for rw in r2): print("   first contradiction when adding:", lb); break
    sys.exit()
free = [i for i in range(NV) if i not in piv]
print(f"   remaining free parameters ({len(free)}):", [pname[1 + i] for i in free], flush=True)
# what is left of the count parameters?  rank of the equations after eliminating the cubic parameters
nc = len(P0)
only = [rw for rw in red if all(x == 0 for x in rw[nc:-1])]
print(f"   equations involving the count parameters only: {len(only)}")
for rw in only: print("      ", " + ".join(f"({rw[i]}) {pname[1+i]}" for i in range(nc) if rw[i] != 0), "=", rw[-1])
def subst(f):
    c0 = f[0]; cf = {i: Fr(0) for i in free}
    for i in range(NV):
        x = f[1 + i]
        if x == 0: continue
        if i in piv:
            rw = red[piv.index(i)]; c0 += x * rw[-1]
            for k2 in free: cf[k2] -= x * rw[k2]
        else: cf[i] += x
    return c0, [cf[k2] for k2 in free]
G = []; labels = []
for f, lb in GE:
    c0, cf = subst(f)
    if all(x == 0 for x in cf):
        if c0 < 0: print(f"   CONSTANT NEGATIVE: {lb}: {c0}")
        continue
    G.append((c0, cf)); labels.append(lb)
st, sol, it = exact_lp.solve(G)
print(f"non-negativity of the {len(G)} pair counts: {st}  [{time.time()-t0:.0f}s]", flush=True)
if st == "infeasible":
    for (c0, cf), lb, l in zip(G, labels, sol):
        if l != 0: print(f"      {lb:44s} {float(l):.6g}")
