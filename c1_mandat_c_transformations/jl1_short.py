"""Rank 43, no root in M (b1 = 0): LEVEL-1 Jacobi form of the lift of ONE short vector of L1.

U = M + N_4 glued is even unimodular of rank 48.  A vector y of L1 of norm 2k (k = 8..13) lifts to v = (y/sqrt7, b), b minimal in the
partner class of N_4^#, and |v|^2 = 4 (for k = 13 only in the four classes whose partner has minimum 2/7).  phi_v lies in J_{24,2}(SL_2(Z))
(dimension 6).  theta_U = 1 + 4 q + A2 q^2 + ... has one unknown A2; the products of v with the 4 roots of N_4 are known from b;
one parameter t = c(2,2) = #{u of norm 4: <u, v> = 2} is left.
Question: for which (A2, t) are all c(n, r) >= 0, for each type of short vector?     usage: jl1_short.py [NMAX]"""
import sys, itertools
from fractions import Fraction as Fr
from collections import Counter
import jl1, exact_lp
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 14
k, m = 24, 2
# ---------------- N_4^# model (as in jl1_p3n25.py)
def okdual(maxn49):
    out = []; Bd = int((maxn49 / 2) ** 0.5) + 3
    for x in range(-Bd, Bd + 1):
        for y in range(-Bd, Bd + 1):
            if (x - 3 * y) % 7: continue
            n49 = 2 * x * x + 2 * x * y + 4 * y * y
            if n49 <= maxn49: out.append((x, y, n49))
    return out
OK = okdual(49 * 3)
def ip49(u, v): return 2 * u[0] * v[0] + u[0] * v[1] + u[1] * v[0] + 4 * u[1] * v[1]
roots = [((7, 0, 98), (0, 0, 0)), ((-7, 0, 98), (0, 0, 0)), ((0, 0, 0), (7, 0, 98)), ((0, 0, 0), (-7, 0, 98))]
def nip(b, c): return Fr(ip49(b[0], c[0]) + ip49(b[1], c[1]), 49)
types = {}                                              # norm of b (x7) -> set of root distributions
for u1 in OK:
    for u2 in OK:
        n7 = Fr(u1[2] + u2[2], 7)
        if n7 not in (2, 4, 6, 8, 10, 12): continue      # |b|^2 = n7 / 7
        # keep only vectors that are minimal in their class: class = (y1 mod 7, y2 mod 7)
        cls = ((-u1[1]) % 7, (-u2[1]) % 7)
        types.setdefault((n7, cls), []).append((u1, u2))
classmin = {}
for (n7, cls), lst in types.items():
    if cls not in classmin or n7 < classmin[cls][0]: classmin[cls] = (n7, lst)
dist_by_k = {}
for cls, (n7, lst) in classmin.items():
    if cls == (0, 0): continue
    kk = (28 - n7) // 2                                  # |y|^2 / 7 + n7 / 7 = 4  ->  |y|^2 = 28 - n7 = 2k
    for b in lst:
        d = Counter(int(nip(b, r)) for r in roots)
        dist_by_k.setdefault(int(kk), set()).add((d[0], d[1], d[2]))
print("norm of the short vector -> possible (number of roots with product 0, +1, +2) for its lift:")
for kk in sorted(dist_by_k): print(f"   norm {2*kk}: {sorted(dist_by_k[kk])}")
# ---------------- Jacobi form with parameters A2, x (S26), y1, y2 (S28)
B = jl1.basis(24); S26 = jl1.cusp(26); S28 = jl1.cusp(28)
red, piv = jl1.rref([[B[0][n], B[1][n], B[2][n]] + [[1, 0], [4, 0], [0, 1]][n] for n in range(3)])
th = [[sum(red[i][3] * B[i][n] for i in range(3)), sum(red[i][4] * B[i][n] for i in range(3))] for n in range(jl1.NQ + 1)]
xi = [[[Fr(th[n][0]), Fr(th[n][1]), 0, 0, 0] for n in range(jl1.NQ + 1)],
      [[0, 0, Fr(S26[0][n]), 0, 0] for n in range(jl1.NQ + 1)],
      [[0, 0, 0, Fr(S28[0][n]), Fr(S28[1][n])] for n in range(jl1.NQ + 1)]]
xi = [[[Fr(v) for v in f] for f in row] for row in xi]
C = jl1.solve_coeffs(k, m, xi, NMAX)
def analyse(c1, c2):
    """root distribution c(1,1) = c1, c(1,2) = c2; returns the coefficient forms in (1, A2, t)"""
    rows = []
    for r, val in ((1, c1), (2, c2)):
        f = C[(1, r)]; rows.append([f[2], f[3], f[4], val - f[0], -f[1], 0])
    f = C[(2, 2)]; rows.append([f[2], f[3], f[4], -f[0], -f[1], 1])
    red, piv = jl1.rref(rows)
    assert piv[:3] == [0, 1, 2]
    sol = [red[i][3:] for i in range(3)]
    T = {}
    for key, f in C.items():
        if key == "constraints": continue
        out = [f[0], f[1], Fr(0)]
        for i in range(3):
            if f[2 + i] != 0: out = [o + f[2 + i] * s for o, s in zip(out, sol[i])]
        T[key] = out
    return T
seen = set()
for kk in sorted(dist_by_k):
    for (c0, c1, c2) in sorted(dist_by_k[kk]):
        if (c1, c2) in seen: continue
        seen.add((c1, c2))
        T = analyse(c1, c2)
        print(f"\nroot products ({c0} zero, {c1} of +1, {c2} of +2):   [types: " + ", ".join(f"norm {2*q}" for q in sorted(dist_by_k) if any(d[1:] == (c1, c2) for d in dist_by_k[q])) + "]")
        for n in (2, 3):
            for r in range(3): print(f"   c({n},{r}) = {T[(n, r)][0]} + ({T[(n, r)][1]}) A2 + ({T[(n, r)][2]}) t")
        G = [(f[0], [f[1], f[2]]) for key, f in T.items() if key[0] >= 2 and f[1:] != [0, 0]]
        st, sol, it = exact_lp.solve(G)
        print(f"   non-negativity up to n = {NMAX}: {st}")
        if st == "feasible":
            def ext(cA, ct):
                lo, hi = -10 ** 9, 10 ** 9
                if exact_lp.solve(G + [(Fr(-hi), [Fr(cA), Fr(ct)])])[0] == "feasible": return None
                while hi - lo > 1:
                    mid = (lo + hi) // 2
                    if exact_lp.solve(G + [(Fr(-mid), [Fr(cA), Fr(ct)])])[0] == "feasible": lo = mid
                    else: hi = mid
                return lo
            mA = ext(-1, 0); MA = ext(1, 0); mt = ext(0, -1); Mt = ext(0, 1)
            print(f"   range of A2 = a_2(U): {None if mA is None else -mA} .. {MA};   range of t: {None if mt is None else -mt} .. {Mt}")
