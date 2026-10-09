"""Line Jacobi form in S0: feasible region.  Parameters: p = c(2,2) and q = cL(13,2) (both are numbers of pairs, hence integers >= 0):
   p = #{(x, l): x in M of norm 4, <x, h_l> = 2},     q = #{(y, l): y in L1 of norm 26, y(l) = 2}.
Every coefficient c(n, r), cL(N, s) is then A + B p + C q and must be >= 0.   usage: jac_lines2.py"""
import pickle, sys
from fractions import Fraction as Fr
import exact_lp
D = pickle.load(open("jac_lines.pkl", "rb"))
K, CM, CL, a, b = D["K"], D["CM"], D["CL"], D["a"], D["b"]
assert K == 2
f1, f2 = CM[(2, 2)], CL[(13, 2)]
det = f1[1] * f2[2] - f1[2] * f2[1]
assert det != 0, "p and q are not independent"
# t = Minv (pq - const)
def conv(f):
    """affine form in (t1, t2) -> affine form in (p, q)"""
    # t1 = ( f2[2] (p - f1[0]) - f1[2] (q - f2[0]) ) / det ; t2 = ( -f2[1] (p - f1[0]) + f1[1] (q - f2[0]) ) / det
    a1p, a1q, a10 = f2[2] / det, -f1[2] / det, (-f2[2] * f1[0] + f1[2] * f2[0]) / det
    a2p, a2q, a20 = -f2[1] / det, f1[1] / det, (f2[1] * f1[0] - f1[1] * f2[0]) / det
    return [f[0] + f[1] * a10 + f[2] * a20, f[1] * a1p + f[2] * a2p, f[1] * a1q + f[2] * a2q]
M = {k: conv(v) for k, v in CM.items()}; L = {k: conv(v) for k, v in CL.items()}
assert M[(2, 2)] == [0, 1, 0] and L[(13, 2)] == [0, 0, 1]
show = lambda f: f"{f[0]} + ({f[1]}) p + ({f[2]}) q"
print("M side, norm 4:   c(2,0) =", show(M[(2, 0)]), ";  c(2,1) =", show(M[(2, 1)]), ";  c(2,2) = p")
print("L side, norm 26:  cL(13,0) =", show(L[(13, 0)]), ";  cL(13,1) =", show(L[(13, 1)]), ";  cL(13,2) = q")
for n in (3, 4):
    print(f"M side, norm {2*n}:  " + ";  ".join(f"c({n},{r}) = {show(M[(n, r)])}" for r in (0, 1, 2)))
for N in (14, 15, 16):
    print(f"L side, norm {2*N}:  " + ";  ".join(f"cL({N},{s}) = {show(L[(N, s)])}" for s in (0, 1, 2)))
# ---------------- feasibility: all coefficients >= 0
G = []; labels = []
for (n, r), f in sorted(M.items()):
    if b[n] == 0 and f == [0, 0, 0]: continue
    G.append((f[0], [f[1], f[2]])); labels.append(f"c({n},{r})>=0")
for (N, s), f in sorted(L.items()):
    if f == [0, 0, 0]: continue
    G.append((f[0], [f[1], f[2]])); labels.append(f"cL({N},{s})>=0")
const_viol = [(lab, str(c0)) for (c0, cf), lab in zip(G, labels) if cf == [0, 0] and c0 < 0]
if const_viol: print("CONSTANT coefficients negative:", const_viol[:8])
st, sol, it = exact_lp.solve(G)
print(f"\nnon-negativity of all {len(G)} coefficients (truncation {max(n for n, _ in L)}): {st}")
if st == "infeasible":
    print("exact certificate (multipliers):")
    for (c0, cf), lab, l in zip(G, labels, sol):
        if l != 0: print(f"    {lab:16s} = {c0} + ({cf[0]}) p + ({cf[1]}) q      multiplier {l}")
else:
    print("   a feasible point: p =", float(sol[0]), " q =", float(sol[1]))
    def ext(cp, cq):
        """max of cp p + cq q by bisection on the exact feasibility test"""
        lo, hi = -10 ** 12, 10 ** 12
        base = lambda X: (Fr(-X), [Fr(cp), Fr(cq)])
        if exact_lp.solve(G + [base(hi)])[0] == "feasible": return None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if exact_lp.solve(G + [base(mid)])[0] == "feasible": lo = mid
            else: hi = mid
        return lo
    print("   range of p:", -ext(-1, 0), "..", ext(1, 0), "   range of q:", -ext(0, -1), "..", ext(0, 1))
