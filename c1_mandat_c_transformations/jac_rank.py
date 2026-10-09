"""LINE JACOBI PROGRAMME at a given rank r (no branch hypothesis).

phi(tau, z) = sum over the 231 lines l and x in M of q^(|x|^2/2) zeta^<x,h_l>  is a Jacobi form of weight 22 and index 2 on
Gamma_0(7); its Taylor coefficients are 231 theta_M (weight 22), 0 (weight 24: sum_l h_l h_l^T = 21 E) and the quartic series
G_M of weight 26; same on the dual side with theta_L1 and G_L, G_M = -7^((r-23)/2) G_L | W_7.
    c(n, r)  = #{(x, l): x in M,  |x|^2 = 2n, <x,h_l> = r}      depends only on (8n - r^2, r mod 4),
    cL(N, s) = #{(y, l): y in L1, |y|^2 = 2N, y(l) = s}          depends only on (8N - 7 s^2, s mod 4).
All of them are affine in the 7 coordinates of theta and the coordinates of G, and are numbers of pairs: >= 0.
NEW with respect to section 9 (harm4.py): the line sums are INTEGERS, so the quartic sum of a layer is tied to its distribution
on {0, +-1, +-2, ...} (not only bounded by Cauchy-Schwarz), and the values |r| >= 3 are read off lower layers.
Discriminating question: is some rank in {37, 39, 41, 43} infeasible?        usage: jac_rank.py r [NMAX] [options]"""
import sys, math, time
from fractions import Fraction as Fr
import mf7, thetalp, exact_lp
R = int(sys.argv[1]); NMAX = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 30
OPT = set(sys.argv[2:])
t0 = time.time()
T = thetalp.Theta(R, nmax=NMAX, standard=False)
S = mf7.Space(26); D = len(S.ser)
fac = -Fr(7) ** ((R - 23) // 2)
def coefL(n): return [Fr(S.ser[i][n]) for i in range(D)]
def coefM(n): return [fac * sum(S.W[i][j] * S.ser[j][n] for j in range(D)) for i in range(D)]
rows = [coefL(n) for n in range(0, 7)] + [coefM(0)]
red, piv, _ = mf7.rref(rows)
ns = []
for fcol in [j for j in range(D) if j not in piv]:
    v = [Fr(0)] * D; v[fcol] = Fr(1)
    for rw, p in zip(red, piv): v[p] = -rw[fcol]
    ns.append(v)
K = len(ns)                                   # free coordinates of G
NV = 7 + K + 1                                # c1..c7, u1..uK, P
iP = 7 + K
def aff(const=0): return [Fr(const)] + [Fr(0)] * NV
def add(*fs): return [sum(x) for x in zip(*fs)]
def sc(f, s): return [x * s for x in f]
def lift(f8): return list(f8) + [Fr(0)] * (K + 1)
def gform(vals):
    f = aff();
    for k in range(K): f[1 + 7 + k] = Fr(vals[k])
    return f
A = [lift(T.a[n]) for n in range(NMAX + 1)]; Bm = [lift(T.b[n]) for n in range(NMAX + 1)]
GL = [gform([sum(x * y for x, y in zip(coefL(n), v)) for v in ns]) for n in range(NMAX + 1)]
GM = [gform([sum(x * y for x, y in zip(coefM(n), v)) for v in ns]) for n in range(NMAX + 1)]
Pv = aff(); Pv[1 + iP] = Fr(1)
print(f"rank {R}, truncation {NMAX}: 7 theta coordinates, {K} quartic coordinates, 1 prism variable  [{time.time()-t0:.0f}s]", flush=True)
# ---------------- M side
CM = {}
def cM(n, r):
    lam = -((r + 1) // 4); rp = r + 4 * lam; n2 = n + lam * r + 2 * lam * lam
    if rp == -1: rp = 1
    if n2 < 0 or (n2 == 0 and rp != 0): return aff(0)
    if n2 == 0: return aff(231)
    return CM[(n2, rp)]
for n in range(1, NMAX + 1):
    rmax = math.isqrt(8 * n)
    R0 = sc(Bm[n], 231); R2 = sc(Bm[n], 42 * n); R4 = add(sc(GM[n], 49), sc(Bm[n], Fr(504, 23) * n * n))
    for r in range(3, rmax + 1):
        v = cM(n, r); R0 = add(R0, sc(v, -2)); R2 = add(R2, sc(v, -2 * r * r)); R4 = add(R4, sc(v, -2 * r ** 4))
    c2 = sc(add(R4, sc(R2, -1)), Fr(1, 24))
    c1 = sc(add(R2, sc(c2, -8)), Fr(1, 2))
    c0 = add(R0, sc(c1, -2), sc(c2, -2))
    CM[(n, 0)], CM[(n, 1)], CM[(n, 2)] = c0, c1, c2
# ---------------- L side
CL = {}
def cLf(N, s):
    lam = -((s + 1) // 4); sp = s + 4 * lam; N2 = N + 7 * lam * (s + 2 * lam)
    if sp == -1: sp = 1
    if N2 < 0 or (N2 == 0 and sp != 0): return aff(0)
    if N2 == 0: return aff(231)
    return CL[(N2, sp)]
for Nn in range(1, NMAX + 1):
    smax = math.isqrt(8 * Nn // 7)
    R0 = sc(A[Nn], 231); R2 = sc(A[Nn], 6 * Nn); R4 = add(GL[Nn], sc(A[Nn], Fr(72, 161) * Nn * Nn))
    for s in range(3, smax + 1):
        v = cLf(Nn, s); R0 = add(R0, sc(v, -2)); R2 = add(R2, sc(v, -2 * s * s)); R4 = add(R4, sc(v, -2 * s ** 4))
    c2 = sc(add(R4, sc(R2, -1)), Fr(1, 24))
    c1 = sc(add(R2, sc(c2, -8)), Fr(1, 2))
    c0 = add(R0, sc(c1, -2), sc(c2, -2))
    CL[(Nn, 0)], CL[(Nn, 1)], CL[(Nn, 2)] = c0, c1, c2
# ---------------- constraints
EQ, GE = [], []
def ge(f, lab): GE.append((f, lab))
def eq(f, lab): EQ.append((f, lab))
for N in range(1, 7):
    for s in (0, 1, 2): eq(CL[(N, s)], f"cL({N},{s})=0 (no vector of norm < 14)")
for N in range(7, 11): eq(CL[(N, 2)], f"cL({N},2)=0 (vectors of norm <= 20 meet every line at most once)")
for (n, r), f in CM.items(): ge(f, f"c({n},{r})>=0")
for (N, s), f in CL.items():
    if N >= 7: ge(f, f"cL({N},{s})>=0")
for n in range(1, NMAX // 7 + 1):
    for s in (0, 1, 2): ge(add(CL[(7 * n, s)], sc(CM[(n, s)], -1)), f"cL({7*n},{s})>=c({n},{s})")
    if R == 43:
        for s in (0, 1, 2): ge(add(CM[(n, s)], sc(CL[(7 * n, s)], -1)), f"rank 43: cL({7*n},{s})<=c({n},{s})")
# the 462 line vectors themselves (P = number of prisms): contributions to the layer n = 2
ge(Pv, "P>=0"); ge(add(aff(852), sc(Pv, -1)), "P<=852")
ge(add(CM[(2, 2)], sc(Pv, -2)), "c(2,2)>=2P"); ge(add(CM[(2, 1)], aff(-15708), sc(Pv, 8)), "c(2,1)>=15708-8P")
ge(add(CM[(2, 0)], aff(-74844), sc(Pv, -12)), "c(2,0)>=74844+12P")
# standard degree-0 bounds
ge(add(aff(990), sc(A[7], -1)), "a7<=990"); ge(add(aff(55440), sc(A[7], -7), sc(A[8], -8)), "7a7+8a8<=55440")
ge(add(aff(44), sc(Bm[1], -1)), "b1<=44"); ge(add(Bm[2], aff(-462), sc(Bm[1], -41)), "b2>=462+41b1")
ge(add(Bm[3], aff(-45964)), "b3>=45964"); ge(add(Bm[4], aff(-2729034)), "b4>=2729034"); ge(add(Bm[5], aff(-18001368)), "b5>=18001368")
for n in range(7, NMAX + 1): ge(A[n], f"a{n}>=0")
for n in range(1, NMAX + 1): ge(Bm[n], f"b{n}>=0")
# optional hypotheses  hyp:a8=0  hyp:b1=0  hyp:a9<=100  hyp:P=0 ; objectives  min:a7  max:b2  (bisection on exact feasibility)
import re as _re
def _form(name):
    if name == "P": return Pv
    k = int(name[1:]); return A[k] if name[0] == "a" else Bm[k]
for arg in sys.argv:
    m_ = _re.fullmatch(r"hyp:([abP]\d*)(<=|>=|=)(\d+)", arg)
    if not m_: continue
    f_, op_, v_ = _form(m_.group(1)), m_.group(2), int(m_.group(3))
    if op_ == "=": eq(add(f_, aff(-v_)), arg)
    if op_ == "<=": ge(add(aff(v_), sc(f_, -1)), arg)
    if op_ == ">=": ge(add(f_, aff(-v_)), arg)
if "nojacobi" in OPT:
    GE = [(f, lab) for f, lab in GE if not lab.startswith(("c(", "cL(", "rank 43"))]
    EQ = [(f, lab) for f, lab in EQ if not lab.startswith("cL(") or "no vector" in lab]
# ---------------- eliminate the equalities exactly
rowsE = [f[1:] + [-f[0]] for f, _ in EQ]
redE, pivE, _ = mf7.rref(rowsE)
for rw in redE:
    if all(x == 0 for x in rw[:-1]) and rw[-1] != 0: print("EQUALITIES INCONSISTENT"); sys.exit()
free = [i for i in range(NV) if i not in pivE]
def subst(f):
    c0 = f[0]; cf = {i: Fr(0) for i in free}
    for i in range(NV):
        x = f[1 + i]
        if x == 0: continue
        if i in pivE:
            rw = redE[pivE.index(i)]; c0 += x * rw[-1]
            for k in free: cf[k] -= x * rw[k]
        else: cf[i] += x
    return c0, [cf[k] for k in free]
G = []; labels = []
for f, lab in GE:
    c0, cf = subst(f)
    if all(x == 0 for x in cf):
        if c0 < 0: print(f"CONSTANT VIOLATION: {lab}: {c0}")
        continue
    G.append((c0, cf)); labels.append(lab)
print(f"{len(EQ)} equalities (rank {len(pivE)}), {len(free)} free variables, {len(G)} inequalities  [{time.time()-t0:.0f}s]", flush=True)
st, sol, it = exact_lp.solve(G)
print(f"RANK {R}: line Jacobi programme, truncation {NMAX}: {st}  ({it} pivots)  [{time.time()-t0:.0f}s]", flush=True)
if st == "feasible":
    def weighted(spec):
        f = aff()
        for term in spec.split("+"):
            m_ = _re.fullmatch(r"(\d*)\*?([abP]\d*)", term); f = add(f, sc(_form(m_.group(2)), int(m_.group(1) or 1)))
        return f
    for arg in sys.argv:
        m_ = _re.fullmatch(r"(min|max):(.+)", arg)
        if not m_: continue
        c0, cf = subst(weighted(m_.group(2))); sgn = 1 if m_.group(1) == "min" else -1
        cap = lambda X: (Fr(X) - sgn * c0, [-sgn * x for x in cf])            # sgn * value <= X
        lo, hi = -10 ** 13, 10 ** 13
        if exact_lp.solve(G + [cap(lo)])[0] == "feasible": print(f"   {arg}: unbounded"); continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if exact_lp.solve(G + [cap(mid)])[0] == "feasible": hi = mid
            else: lo = mid
        print(f"   {arg} = {sgn * hi}   [{time.time()-t0:.0f}s]", flush=True)
if st == "infeasible":
    print("exact certificate:")
    for (c0, cf), lab, l in zip(G, labels, sol):
        if l != 0: print(f"    {lab:44s} {float(l):.6g}")
