"""S0 (rank 43): the LINE JACOBI FORM CLASS BY CLASS (nine classes of L_9).

For y in L_9 of class c and a line l, s = y(l) lies in c/3 + Z.  The translation y -> y + 7E1_l (a vector of class 3, norm 28,
with (7E1_l)(l) = 4) and the symmetry y -> -y give the identifications
      (c, N, s) ~ (c + 3, N + 7(s + 2), s + 4),        (c, N, s) ~ (-c, N, -s)            (N = |y|^2 / 2)
between the numbers  n(c, N, s) = #{(y, l): y of class c, |y|^2 = 2N, y(l) = s}.
A layer (c, N) has only a few values s in (-2, 2] not read off lower layers:
      class 0: 0, +-1, +-2 (3 unknowns);  class 3: -2, -1, 0, 1 (and s = 2 is the class-0 unknown);  classes 1, 2, 4: 4 unknowns;
and the moments   sum 1 = 231 n,  sum s = 0,  sum s^2 = 6 N n,  sum s^3 = cubic sum,  sum s^4 = quartic sum + (72/161) N^2 n.
So for every layer of the classes 1, 2, 3, 4 the QUARTIC sum is determined by the count and the CUBIC sum: one exact linear
equation per layer between the three modular systems (counts: 7 parameters in S0, cubic: 14, quartic: ?).
Discriminating question: is this over-determined exact linear system consistent in S0, and with all n(c, N, s) >= 0 ?
usage: s0_jac9.py [N]"""
import sys, time, math, pickle
from fractions import Fraction as Fr
import z9theta as Z, z9lp, z9quartic as ZQ, s0_cubic as SC, mf7, exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
RHO, SIG = Z.RHO, Z.SIG
t0 = time.time()
top = 9 * (N - 9)
# ---------------- counts in S0
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
# ---------------- cubic in S0
Cs = SC.build(N); qfree3, e3 = SC.reduce(Cs)
# ---------------- quartic in S0
Q = ZQ.Even(43, N); Q.zeros()
Q.fix("X", 0, 63)
for n in range(8, 13): Q.fix("X", 0, 9 * n)
for n in (11, 12): Q.fix("X", 3, 9 * n)
for c in range(5):
    j = 0
    while 7 * (RHO[c] + 9 * j) <= 9 * N:
        num9 = RHO[c] + 9 * j
        a, b = Q.var("X", c, 7 * num9), Q.var("T", c, num9)
        if a is not None and b is not None: Q.rows.append({a: Fr(1), b: Fr(-1)}); Q.rhs.append(Fr(0))
        j += 1
qfree4, e4 = Q.reduce()
assert qfree4 is not None
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
lab = lambda f: f"{f[0]}{f[1]}[{expo(f)}/9]"
# ---------------- parameters actually used by the layers below the safe exponent
layers = sorted([(SIG[c] + 9 * j, c) for c in range(5) for j in range(0, N + 1) if SIG[c] + 9 * j <= top])
key = lambda c, num9: ("X", c, (num9 - SIG[c]) // 9)
used0, used3, used4 = set(), set(), set()
for num9, c in layers:
    used0 |= set(cexpr[key(c, num9)][1])
    if c: used3 |= set(e3[key(c, num9)])
    used4 |= set(e4[key(c, num9)][1])
P0, P3, P4 = sorted(used0), sorted(used3), sorted(used4)
NV = len(P0) + len(P3) + len(P4)
pos0 = {t: 1 + i for i, t in enumerate(P0)}; pos3 = {t: 1 + len(P0) + i for i, t in enumerate(P3)}; pos4 = {t: 1 + len(P0) + len(P3) + i for i, t in enumerate(P4)}
pname = ["1"] + ["n:" + lab(cfree[t]) for t in P0] + ["c:" + lab(qfree3[t]) for t in P3] + ["q:" + lab(qfree4[t]) for t in P4]
print(f"S0, truncation {N}: parameters: {len(P0)} counts, {len(P3)} cubic sums, {len(P4)} quartic sums  [{time.time()-t0:.0f}s]", flush=True)
print("   cubic :", [lab(qfree3[t]) for t in P3]); print("   quartic:", [lab(qfree4[t]) for t in P4], flush=True)
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
def quartic_form(c, num9):
    c0, cf = e4[key(c, num9)]; f = aff(c0)
    for t, v in cf.items(): f[pos4[t]] = v
    return f
exists = {(c, num9) for num9, c in layers}
VAR = {}                                              # canonical (c, num9, s3) -> affine form
def canon(k, num9, s3):
    """canonical representative of the class of (k, num9, s3) with s in (-2, 2]; returns None if the count is 0, 'zero' for the zero vector"""
    k %= 9
    lam = -((s3 + 5) // 12)                           # s3 + 12 lam in (-6, 6]
    s3r = s3 + 12 * lam; kr = (k + 3 * lam) % 9; nr = num9 + 21 * lam * (s3 + 6 * lam)
    assert -6 < s3r <= 6
    if kr > 4:
        kr, s3r = 9 - kr, -s3r                        # mirror; s3r may now be -6 (only for kr = 3)
    elif kr == 0 and s3r < 0: s3r = -s3r
    if kr == 3 and s3r == 6: kr = 0                   # (3, N, 2) ~ (0, N, 2)
    return kr, nr, s3r
def value(k, num9, s3):
    kr, nr, s3r = canon(k, num9, s3)
    if nr < 0: return aff(0)
    if nr == 0: return aff(231) if (kr == 0 and s3r == 0) else aff(0)
    if (kr, nr) not in exists:
        if nr > top: raise KeyError((kr, nr, s3r))
        return aff(0)                                 # not a legal exponent of the class: no vector
    return VAR[(kr, nr, s3r)]
EQ = []; GE = []
VAND = {}
def vinv(svals):
    """inverse of the 4x4 moment matrix (rows: powers 0..3) for the four values svals"""
    if svals not in VAND:
        rows = [[Fr(s) ** p for s in svals] + [Fr(int(p == q)) for q in range(4)] for p in range(4)]
        red, piv, _ = mf7.rref(rows); assert piv == [0, 1, 2, 3]
        VAND[svals] = [r[4:] for r in red]
    return VAND[svals]
nlay = 0
for num9, c in layers:
    Nn = Fr(num9, 9); n = count_form(c, num9); C = cubic_form(c, num9); Qf = quartic_form(c, num9)
    smax = math.isqrt(8 * num9 // 7)                                  # |s3| <= sqrt(8 num9 / 7)
    R = [sc(n, 231), aff(0), sc(n, 6 * Nn), C, add(Qf, sc(n, Fr(72, 161) * Nn * Nn))]
    if c == 0: red_vals = [0, 3, -3, 6, -6]
    elif c == 3: red_vals = [-6, -3, 0, 3, 6]
    elif c in (1, 4): red_vals = [-5, -2, 1, 4]
    else: red_vals = [-4, -1, 2, 5]
    if c == 0 and num9 == 0:
        VAR[(0, 0, 0)] = aff(231); continue
    if all(x == 0 for x in n):
        # provably empty layer: no pair at all, so every class met by this layer is empty as well
        assert all(x == 0 for x in C) and all(x == 0 for x in Qf), (c, num9)
        for s3 in range(-smax, smax + 1):
            if (s3 - c) % 3: continue
            if s3 in red_vals:
                kr, nr, s3r = canon(c, num9, s3)
                if (kr, nr, s3r) not in VAR: VAR[(kr, nr, s3r)] = aff(0)
                elif any(x != 0 for x in VAR[(kr, nr, s3r)]): EQ.append((VAR[(kr, nr, s3r)], f"empty layer: class {c}, exponent {num9}/9, s = {Fr(s3, 3)}"))
            else:
                v = value(c, num9, s3)
                if any(x != 0 for x in v): EQ.append((v, f"empty layer: class {c}, exponent {num9}/9, s = {Fr(s3, 3)}"))
        for s3 in red_vals:
            kr, nr, s3r = canon(c, num9, s3)
            VAR.setdefault((kr, nr, s3r), aff(0))
        continue
    for s3 in range(-smax, smax + 1):
        if (s3 - c) % 3 or s3 in red_vals: continue
        v = value(c, num9, s3); s = Fr(s3, 3)
        for p in range(5): R[p] = add(R[p], sc(v, -s ** p))
    if c == 0:
        u2 = sc(add(R[4], sc(R[2], -1)), Fr(1, 24)); u1 = sc(add(R[2], sc(u2, -8)), Fr(1, 2)); u0 = add(R[0], sc(u1, -2), sc(u2, -2))
        VAR[(0, num9, 0)], VAR[(0, num9, 3)], VAR[(0, num9, 6)] = u0, u1, u2
        new = [(0, u0), (3, u1), (6, u2)]
    elif c == 3:
        u2 = VAR[(0, num9, 6)]                                        # s = 2 is shared with the class 0
        for p in range(5): R[p] = add(R[p], sc(u2, -Fr(2) ** p))
        inv = vinv((-2, -1, 0, 1))
        sol = [add(*[sc(R[p], inv[i][p]) for p in range(4)]) for i in range(4)]
        for s3, f in zip((-6, -3, 0, 3), sol): VAR[(3, num9, s3)] = f
        EQ.append((add(*([sc(f, Fr(s) ** 4) for s, f in zip((-2, -1, 0, 1), sol)] + [sc(R[4], -1)])), f"class 3, exponent {num9}/9"))
        new = list(zip((-6, -3, 0, 3), sol))
    else:
        svals = tuple(Fr(x, 3) for x in red_vals); inv = vinv(svals)
        sol = [add(*[sc(R[p], inv[i][p]) for p in range(4)]) for i in range(4)]
        for s3, f in zip(red_vals, sol): VAR[(c, num9, s3)] = f
        EQ.append((add(*([sc(f, s ** 4) for s, f in zip(svals, sol)] + [sc(R[4], -1)])), f"class {c}, exponent {num9}/9"))
        new = list(zip(red_vals, sol))
    for s3, f in new: GE.append((f, f"n({c}; {num9}/9; s = {Fr(s3, 3)}) >= 0"))
    nlay += 1
print(f"{nlay} layers, {len(EQ)} Jacobi equations, {len(GE)} pair counts  [{time.time()-t0:.0f}s]", flush=True)
pickle.dump({"EQ": EQ, "GE": GE, "pname": pname, "VAR": VAR, "NV": NV, "nP": (len(P0), len(P3), len(P4)),
             "counts": {(c, num9): count_form(c, num9) for num9, c in layers}}, open(f"s0_jac9_N{N}.pkl", "wb"))
# ---------------- the linear system
rows = [f[1:] + [-f[0]] for f, _ in EQ if any(x != 0 for x in f)]
triv = len(EQ) - len(rows)
red, piv, _ = mf7.rref(rows) if rows else ([], [], None)
bad = [rw for rw in red if all(x == 0 for x in rw[:-1]) and rw[-1] != 0]
print(f"Jacobi equations: {len(rows)} non-trivial ({triv} trivial), rank {len(piv)} in {NV} parameters: " + ("INCONSISTENT" if bad else "consistent"), flush=True)
if bad: sys.exit()
free = [i for i in range(NV) if i not in piv]
print(f"   remaining free parameters ({len(free)}):", [pname[1 + i] for i in free], flush=True)
def subst(f):
    c0 = f[0]; cf = {i: Fr(0) for i in free}
    for i in range(NV):
        x = f[1 + i]
        if x == 0: continue
        if i in piv:
            rw = red[piv.index(i)]; c0 += x * rw[-1]
            for k in free: cf[k] -= x * rw[k]
        else: cf[i] += x
    return c0, [cf[k] for k in free]
pickle.dump({"red": red, "piv": piv, "free": free}, open(f"s0_jac9_sol_N{N}.pkl", "wb"))
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
