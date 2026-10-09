"""Pilot (mandate C, 09/10): do the QUARTIC harmonic theta series attached to the vertices and to the lines add
constraints that exclude a rank?

Setting of notes 167-168 of conway99-c1: L1 (even, rank 44, det 7^(r-1)), M = sqrt7 L1^# (even, det 7^(45-r)),
theta_L1 = sum a_n q^n, theta_M = sum b_n q^n in M_22(Gamma_0(7)), theta_L1 | W7 = -7^((23-r)/2) theta_M.

New: for a harmonic quartic P on the (-4)-eigenspace,
    G_L = sum_{y in L1} P(y) q^(y^2/2),  G_M = sum_{x in M} P(x) q^(x^2/2)  are cusp forms of weight 26 on Gamma_0(7),
    G_L | W7 = -7^((23-r)/2) G_M                       (same factor; checked on a toy lattice, toy_harm.py).
Two polynomials, both invariant under relabelling:
    P_V(y) = sum_v y_v^4 - (2/69)|y|^4,        P_T(y) = sum_T y(T)^4 - (18/161)|y|^4.
Exact values on the L1 side (all vectors of norm <= 20 are binary and meet every line at most once, notes 165/171/176):
    norm 2n < 14: none;   14 <= 2n <= 20:  P_V = 2n - (8/69) n^2,   P_T = 6n - (72/161) n^2.
Exact values on the M side: roots (82/483 and 66/161), line vectors, differences of two vertices.
Everything else is bounded by Cauchy-Schwarz.  usage: harm4.py r [nmax] [mode]   mode: base | V | T | VT"""
import sys, json
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
import mf7

r = int(sys.argv[1]); NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 24; MODE = sys.argv[3] if len(sys.argv) > 3 else "VT"
alpha = r - 1
TIGHT = "tight" in sys.argv
F = json.load(open("C:/home/researcher/Desktop/Nouveau/conway99-c1/data/codex_theta7_basis_q84.json"))

# ---------- degree 0: a_n, b_n as affine functions of the free coordinates c_1..c_7 (vector index 0 = constant)
NV0 = 8
cs = [[Fr(0)] * NV0 for _ in range(15)]
cs[0][0] = Fr(7) ** (25 - alpha // 2)
for j in range(1, 8): cs[j][j] = Fr(1)
for n in range(7):
    j = 14 - n
    tot = [sum(cs[k][t] * F[k][n] for k in range(j + 1, 15)) for t in range(NV0)]
    cs[j] = [Fr(int(n == 0 and t == 0)) - tot[t] for t in range(NV0)]
ds = [[x * Fr(7) ** (alpha // 2 + 3 - 2 * i) for x in cs[14 - i]] for i in range(15)]
def expansion(co, n): return [sum(co[j][t] * F[j][n] for j in range(15)) for t in range(NV0)]
a = [expansion(cs, n) for n in range(NMAX + 1)]; b = [expansion(ds, n) for n in range(NMAX + 1)]
assert a[0] == [1] + [0] * 7 and b[0] == [1] + [0] * 7 and all(a[n] == [0] * 8 for n in range(1, 7))

# ---------- variables of the LP: c_1..c_7, P (prisms), 17 coordinates of G_L^V, 17 of G_L^T
S26 = mf7.Space(26); D = len(S26.mons)
names = [f"c{j}" for j in range(1, 8)] + ["P"] + [f"gV{i}" for i in range(D)] + [f"gT{i}" for i in range(D)]
NV = len(names); iP = 7; oV = 8; oT = 8 + D
def lift(v8):
    """affine form in (1, c1..c7) -> affine form in (1, all variables)"""
    return [v8[0]] + list(v8[1:]) + [Fr(0)] * (NV - 7)
def unit(i, cf=Fr(1)):
    v = [Fr(0)] * (NV + 1); v[1 + i] = cf; return v
def add(*vs): return [sum(x) for x in zip(*vs)]
def sc(v, s): return [x * s for x in v]
A = [lift(x) for x in a]; Bm = [lift(x) for x in b]; Pv = unit(iP)
const = lambda x: [Fr(x)] + [Fr(0)] * NV

EQ, GE = [], []          # affine forms: EQ: form == 0 ; GE: form >= 0
def ge(f, label): GE.append((f, label))
def eq(f, label): EQ.append((f, label))

for n in range(7, NMAX + 1): ge(A[n], f"a{n}>=0")
for n in range(1, NMAX + 1): ge(Bm[n], f"b{n}>=0")
ge(add(const(990), sc(A[7], -1)), "a7<=990")
ge(add(const(55440), sc(A[7], -7), sc(A[8], -8)), "7a7+8a8<=55440")
ge(add(const(44), sc(Bm[1], -1)), "b1<=44")
ge(add(Bm[2], const(-462), sc(Bm[1], -41)), "b2>=462+41b1")
if r >= 37: ge(add(Bm[3], const(-45964)), "b3>=45964")
else: ge(add(Bm[3], const(-24948)), "b3>=24948")
ge(add(Bm[4], const(-2729034)), "b4>=2729034")
ge(add(Bm[5], const(-18001368)), "b5>=18001368")
for k in range(1, NMAX // 7 + 1): ge(add(A[7 * k], sc(Bm[k], -1)), f"a{7*k}>=b{k}")
ge(Pv, "P>=0"); ge(add(const(852), sc(Pv, -1)), "P<=852")
# optional extra hypotheses from the command line:  hyp:P=0  hyp:a7=0  hyp:b1=0  hyp:b2<=1100  hyp:a8=0 ...
import re as _re
def _form(name):
    if name == "P": return Pv
    k = int(name[1:]); return A[k] if name[0] == "a" else Bm[k]
for arg in sys.argv:
    m_ = _re.fullmatch(r"hyp:([abP]\d*)(<=|>=|=)(\d+)", arg)
    if not m_: continue
    f_, op_, v_ = _form(m_.group(1)), m_.group(2), int(m_.group(3))
    if op_ in ("<=", "="): ge(add(const(v_), sc(f_, -1)), arg + " (upper)")
    if op_ in (">=", "="): ge(add(f_, const(-v_)), arg + " (lower)")


NATQ = {}
def quartic(off, tag, lamL, rootM, known, loM, hiM, loL, hiL):
    """adds the constraints of one quartic series.  known[n] = (count, affine form of the exact sum over the known vectors)"""
    gco = [unit(off + i) for i in range(D)]                       # coordinates of G_L as affine forms
    def coefL(n): return add(*[sc(gco[i], Fr(S26.ser[i][n])) for i in range(D)])
    # G_M = -7^((r-23)/2) * (G_L | W7)
    fr = [add(*[sc(gco[i], S26.W[i][j]) for i in range(D)]) for j in range(D)]
    fac = -Fr(7) ** Fr(r - 23, 2) if (r - 23) % 2 == 0 else None
    def coefM(n): return sc(add(*[sc(fr[j], Fr(S26.ser[j][n])) for j in range(D)]), fac)
    NATQ[tag] = [coefL(n) for n in range(11, 16)]
    eq(coefL(0), f"{tag}: cusp at infinity"); eq(coefM(0), f"{tag}: cusp at 0")
    for n in range(1, 7): eq(coefL(n), f"{tag}: g{n}=0")
    for n in range(7, 11): eq(add(coefL(n), sc(A[n], -lamL(n))), f"{tag}: g{n}=lam*a{n}")
    eq(add(coefM(1), sc(Bm[1], -rootM)), f"{tag}: m1=root*b1")
    for n in range(2, NMAX + 1):
        cnt, exact = known.get(n, (0, const(0)))
        rest = add(Bm[n], const(-cnt))                           # number of other vectors of norm 2n, >= 0
        ge(add(coefM(n), sc(exact, -1), sc(rest, -loM(n))), f"{tag}: m{n} lower")
        ge(add(sc(coefM(n), -1), exact, sc(rest, hiM(n))), f"{tag}: m{n} upper")
    for n in range(11, NMAX + 1):
        ge(add(coefL(n), sc(A[n], -loL(n))), f"{tag}: g{n} lower")
        ge(add(sc(coefL(n), -1), sc(A[n], hiL(n))), f"{tag}: g{n} upper")

if "V" in MODE:
    quartic(oV, "V", lambda n: 2 * n - Fr(8, 69) * n * n, Fr(82, 483),
            {2: (462, const(462 * Fr(-124, 1127))), 3: (8316, const(8316 * Fr(3102, 1127))), 4: (1386, const(1386 * Fr(30712, 3381)))},
            lambda n: (Fr(4, 99) - Fr(8, 69)) * n * n, lambda n: (Fr(16, 9) - Fr(8, 69)) * n * n,
            lambda n: ({11: Fr(22, 3), 12: Fr(32, 3), 13: Fr(14)}.get(n, Fr(4, 99) * n * n) if TIGHT else Fr(4, 99) * n * n) - Fr(8, 69) * n * n,
            lambda n: ({11: Fr(34), 12: Fr(96), 13: Fr(98)}.get(n, Fr(16, 9) * n * n) if TIGHT else Fr(16, 9) * n * n) - Fr(8, 69) * n * n)
else:
    for i in range(D): eq(unit(oV + i), "V unused")
if "T" in MODE:
    # line vectors: sum of S_4 over the 462 vectors = 149688 + 48 P ; P_T = (S_4 - (504/23) n^2)/49
    linesum = sc(add(const(Fr(149688) - 462 * Fr(504, 23) * 4), sc(Pv, 48)), Fr(1, 49))
    quartic(oT, "T", lambda n: 6 * n - Fr(72, 161) * n * n, Fr(66, 161),
            {2: (462, linesum), 3: (8316, const(8316 * Fr(-534, 1127))), 4: (1386, const(1386 * Fr(-888, 1127)))},
            lambda n: (Fr(1764, 231) - Fr(504, 23)) * n * n / 49, lambda n: (336 - Fr(504, 23)) * n * n / 49,
            lambda n: (Fr(36, 231) - Fr(72, 161)) * n * n,
            lambda n: ((24 * n if (TIGHT and 11 <= n <= 13) else Fr(48, 7) * n * n)) - Fr(72, 161) * n * n)
else:
    for i in range(D): eq(unit(oT + i), "T unused")

# ---------- exact elimination of the equalities, then an exact change to natural variables, then a scaled LP
rows = [f[1:] + [-f[0]] for f, _ in EQ]                           # sum coef*x = -const
red, piv, _ = mf7.rref(rows)
for rw in red: assert any(x != 0 for x in rw[:-1]), "inconsistent equalities: " + str(rw[-1])
free = [i for i in range(NV) if i not in piv]
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
# natural variables: a_7..a_13, P, and four L-side coefficients (among g_11..g_15) of each quartic series
nat = [(f"a{n}", A[n]) for n in range(7, 14)] + [("P", Pv)]
cand = [(f"g{tag}{11+i}", f) for tag in sorted(NATQ) for i, f in enumerate(NATQ[tag])]
chosen = []; matrows = []
for nm, f in nat + cand:
    c0, cf = subst(f)
    if len(mf7.rref(matrows + [cf])[0]) == len(matrows) + 1: chosen.append((nm, c0)); matrows.append(cf)
assert len(chosen) == len(free), (len(chosen), len(free))
nf = len(free)
aug = [list(matrows[i]) + [Fr(int(i == j)) for j in range(nf)] for i in range(nf)]
inv = [rw[nf:] for rw in mf7.rref(aug)[0]]                         # free = inv * (nat - c0nat)
c0nat = [c for _, c in chosen]
def to_nat(c0, cf):
    w = [sum(cf[i] * inv[i][k] for i in range(nf)) for k in range(nf)]
    return c0 - sum(w[k] * c0nat[k] for k in range(nf)), w
G = [to_nat(*subst(f)) for f, _ in GE]
print(f"rank {r}: {NV} variables, {len(EQ)} equalities of rank {len(red)}, {nf} free: {[n for n, _ in chosen]}; {len(GE)} inequalities, nmax {NMAX}, mode {MODE}")
# each natural variable is rescaled by a typical magnitude so that the floating LP is well conditioned
mag = [max([abs(float(g[1][k])) for g in G]) for k in range(nf)]
Ain, bin_ = [], []
import math
# geometric column scaling
col = []
for k in range(nf):
    v = [abs(float(g[1][k])) for g in G if g[1][k] != 0]
    col.append(math.exp(sum(math.log(x) for x in v) / len(v)) if v else 1.0)
for c0, cf in G:
    cfs = [float(x) / col[k] for k, x in enumerate(cf)]
    s = max([abs(x) for x in cfs] + [abs(float(c0)), 1e-300])
    Ain.append([-x / s for x in cfs] + [1.0]); bin_.append(float(c0) / s)
res = linprog([0.0] * nf + [-1.0], A_ub=np.array(Ain), b_ub=np.array(bin_), bounds=[(None, None)] * nf + [(None, 1.0)], method="highs")
print("LP status:", res.status, " max margin t =", None if res.x is None else res.x[-1])
if res.x is not None:
    t = res.x[-1]
    print("=> FEASIBLE relaxation" if t > 1e-9 else ("=> INFEASIBLE (numerically; needs an exact certificate)" if t < -1e-9 else "=> on the boundary"))
    lam = -res.ineqlin.marginals; idx = np.argsort(-lam)[:16]
    print("active constraints:", [(GE[i][1], round(float(lam[i]), 4)) for i in idx if lam[i] > 1e-9])
    if t > 1e-9:
        xs = [res.x[k] / col[k] for k in range(nf)]
        print("a point:", {chosen[k][0]: f"{xs[k]:.6g}" for k in range(nf)})
        # exact evaluation of a few quantities at the floating point (indicative only)
        def val(f):
            c0, cf = to_nat(*subst(f)); return float(c0) + sum(float(cf[k]) * xs[k] for k in range(nf))
        print("b1..b5:", [f"{val(Bm[n]):.6g}" for n in range(1, 6)], " a7..a10:", [f"{val(A[n]):.6g}" for n in range(7, 11)])

if len(sys.argv) > 4 and sys.argv[4] == "dump":
    for (c0, cf), (f, lab) in zip(G, GE):
        if lab in ("b1>=0", "b2>=0", "a7>=0", "b1<=44", "a7<=990", "V: m2 lower", "V: m2 upper", "V: g11 lower", "V: g11 upper", "T: m2 lower", "T: m2 upper"):
            print(f"{lab:16s} const {float(c0): .4e} | " + " ".join(f"{chosen[k][0]}:{float(cf[k]): .3e}" for k in range(nf) if cf[k] != 0))

if "exact" in sys.argv:
    import exact_lp, time
    t0 = time.time()
    status, sol, it = exact_lp.solve(G)
    print(f"EXACT rational LP: {status} after {it} pivots, {time.time()-t0:.1f}s")
    if status == "infeasible":
        act = [(GE[i][1], sol[i]) for i in range(len(G)) if sol[i] != 0]
        print("exact Farkas certificate, verified (sum lam*coef = 0, sum lam*const = -1); constraints used:")
        for lab, l in act: print(f"   {lab:22s} multiplier {float(l):.6g}")
    else:
        def val(f):
            c0, cf = to_nat(*subst(f)); return c0 + sum(cf[k] * sol[k] for k in range(nf))
        print("exact feasible point (checked on every inequality):")
        print("   " + ", ".join(f"{chosen[k][0]}={float(sol[k]):.6g}" for k in range(nf)))
        print("   b1..b5 = " + ", ".join(f"{float(val(Bm[n])):.8g}" for n in range(1, 6)) + " ; a7..a13 = " + ", ".join(f"{float(val(A[n])):.8g}" for n in range(7, 14)))
