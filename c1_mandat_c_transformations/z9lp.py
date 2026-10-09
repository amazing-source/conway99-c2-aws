"""Nine-class (Z/9-refined) theta programme with positivity: exact elimination (flint), then LP.

Discriminating question: with the proved zeros of the five classes, positivity of every class on both sides and the
proved counts (99 vertices in class 1, 693 edges in class 2, 231 lines in class 3, known bounds on a_n, b_n), is some
rank in {37, 39, 41, 43} infeasible?        usage: z9lp.py r [N] [exact]"""
import sys, time, math
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import numpy as np
from scipy.optimize import linprog
import z9theta as Z


def expo9(Mo, name):
    side, k, j = name
    return (Z.RHO if side == "T" else Z.SIG)[k] + 9 * j


def reduce(Mo):
    """exact elimination with the form coordinates first and the class variables by decreasing exponent:
    returns (free names, {name: (c0, {free index: coef})}) for all class variables"""
    names = Mo.names
    xs = [i for i, n in enumerate(names) if n[0] == "x"]
    cl = sorted([i for i, n in enumerate(names) if n[0] != "x"], key=lambda i: -expo9(Mo, names[i]))
    order = xs + cl; pos = {v: p for p, v in enumerate(order)}; nv = len(names)
    M = fmpq_mat(len(Mo.rows), nv + 1)
    for i, (row, b) in enumerate(zip(Mo.rows, Mo.rhs)):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
        M[i, nv] = fmpq(b.numerator, b.denominator)
    R, rk = M.rref()
    piv = []
    for i in range(rk):
        j = next(j for j in range(nv + 1) if R[i, j] != 0); piv.append(j)
    assert nv not in piv, "inconsistent equalities"
    pset = set(piv); freecols = [p for p in range(nv) if p not in pset]
    fidx = {p: t for t, p in enumerate(freecols)}
    expr = {}
    for i, p in enumerate(piv):
        nm = names[order[p]]
        if nm[0] == "x": continue
        c0 = Fr(int(R[i, nv].p), int(R[i, nv].q)); cf = {}
        for q_ in freecols:
            v = R[i, q_]
            if v != 0: cf[fidx[q_]] = -Fr(int(v.p), int(v.q))
        expr[nm] = (c0, cf)
    for q_ in freecols:
        nm = names[order[q_]]
        if nm[0] != "x": expr[nm] = (Fr(0), {fidx[q_]: Fr(1)})
    return [names[order[q_]] for q_ in freecols], expr


def build(r, N, margin=9):
    Mo = Z.Model(r, N); Mo.geometry()
    # rank 43: every vector of L1 of norm divisible by 14 lies in sqrt7 M, class by class
    if r == 43:
        for n in range(1, N // 7 + 1):
            for k in (0, 3):
                a, b = Mo.var("X", k, 63 * n), Mo.var("T", k, 9 * n)
                if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, f"rank43 class {k} n {n}")
    free, expr = reduce(Mo)
    top = 9 * (N - margin)                                   # inequalities only where the truncation is harmless
    V = lambda side, k, num9: expr.get((side, k, (num9 - (Z.RHO if side == "T" else Z.SIG)[k]) // 9))
    G = []                                                   # (c0, {free: coef}, label):  c0 + cf.f >= 0
    def add(terms, const, label):
        c0 = Fr(const); cf = {}
        for coef, e in terms:
            if e is None: return
            c0 += coef * e[0]
            for t, v in e[1].items(): cf[t] = cf.get(t, Fr(0)) + coef * v
        G.append((c0, {t: v for t, v in cf.items() if v != 0}, label))
    for nm, e in expr.items():
        if expo9(Mo, nm) <= top: add([(1, e)], 0, f"{nm}>=0")
    T = lambda k, num9: V("T", k, num9); X = lambda k, num9: V("X", k, num9)
    add([(-1, T(0, 9))], 44, "b1<=44")
    add([(1, T(3, 18))], -231, "class 3: 231 lines")
    add([(1, T(0, 18)), (2, T(3, 18)), (-41, T(0, 9))], -462, "b2>=462+41b1")
    add([(1, T(0, 27))], -8316, "class 0: 8316 differences of non-adjacent vertices")
    add([(1, T(0, 27)), (2, T(3, 27))], -45964, "b3>=45964")
    add([(1, T(0, 36)), (2, T(3, 36))], -2729034, "b4>=2729034")
    add([(1, T(0, 45)), (2, T(3, 45))], -18001368, "b5>=18001368")
    add([(1, T(1, 14))], -99, "class 1: 99 vertices")
    add([(1, T(2, 20))], -693, "class 2: 693 edges")
    add([(-1, X(0, 63))], 990, "a7<=990")
    add([(-7, X(0, 63)), (-8, X(0, 72))], 55440, "7a7+8a8<=55440")
    for k in range(5):                                       # sqrt7 (vector of O of class k) is a vector of L_9 of class k
        res = Z.RHO[k]; j = 0
        while 7 * (res + 9 * j) <= top:
            add([(1, X(k, 7 * (res + 9 * j))), (-1, T(k, res + 9 * j))], 0, f"X{k}[7e]>=T{k}[e], e={res+9*j}/9"); j += 1
    return Mo, free, G


def float_lp(G, nf):
    col = []
    for t in range(nf):
        v = [abs(float(cf[t])) for _, cf, _ in G if t in cf]
        col.append(math.exp(sum(math.log(x) for x in v) / len(v)) if v else 1.0)
    A, b = [], []
    for c0, cf, _ in G:
        rowv = [0.0] * nf
        for t, v in cf.items(): rowv[t] = float(v) / col[t]
        s = max([abs(x) for x in rowv] + [abs(float(c0)), 1e-300])
        A.append([-x / s for x in rowv] + [1.0]); b.append(float(c0) / s)
    res = linprog([0.0] * nf + [-1.0], A_ub=np.array(A), b_ub=np.array(b), bounds=[(None, None)] * nf + [(None, 1.0)], method="highs")
    return res


if __name__ == "__main__":
    r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    t0 = time.time(); Mo, free, G = build(r, N)
    used = sorted({t for _, cf, _ in G for t in cf}); remap = {t: i for i, t in enumerate(used)}
    G = [(c0, {remap[t]: v for t, v in cf.items()}, lab) for c0, cf, lab in G]
    nf = len(used)
    print(f"rank {r}, N {N}: {len(free)} free after elimination, {nf} appear in the {len(G)} inequalities  [{time.time()-t0:.0f}s]")
    print("free variables used:", [free[t] for t in used])
    triv = [(lab, c0) for c0, cf, lab in G if not cf and c0 < 0]
    if triv: print("VIOLATED CONSTANT INEQUALITIES (exact):", triv[:10])
    res = float_lp(G, nf)
    print("float LP status", res.status, "margin", None if res.x is None else res.x[-1])
    if "exact" in sys.argv:
        import exact_lp
        Gd = [(c0, [cf.get(t, Fr(0)) for t in range(nf)]) for c0, cf, _ in G]
        t1 = time.time(); status, sol, it = exact_lp.solve(Gd)
        print(f"EXACT: {status} after {it} pivots [{time.time()-t1:.0f}s]")
        if status == "infeasible":
            for (c0, cf, lab), l in zip(G, sol):
                if l != 0: print(f"   {lab:55s} {float(l):.6g}")
