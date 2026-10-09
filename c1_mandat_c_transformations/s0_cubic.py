"""S0 (rank 43): the CUBIC nine-class system (P_3(y) = sum_v y_v^3) with the S0 zeros and the rank-43 class equalities.
Step 1: how many free cubic layer sums remain, and which?"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import z9cubic as ZC, z9theta as Z
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
RHO, SIG = Z.RHO, Z.SIG
def build(N, s0=True, r=43):
    C = ZC.Cubic(r, N); C.zeros()
    if s0:
        C.fix("X", 3, 99); C.fix("X", 3, 108)
        for c in range(1, 5):
            j = 0
            while 7 * (RHO[c] + 9 * j) <= 9 * N:
                num9 = RHO[c] + 9 * j
                a, b = C.var("X", c, 7 * num9), C.var("T", c, num9)
                if a is not None and b is not None: C.rows.append({a: Fr(1), b: Fr(-1)}); C.rhs.append(Fr(0))
                j += 1
    return C
def reduce(C):
    names = C.names
    expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
    xs = [i for i, n in enumerate(names) if n[0] == "x"]
    cl = sorted([i for i, n in enumerate(names) if n[0] != "x"], key=lambda i: -expo(names[i]))
    order = xs + cl; pos = {v: p for p, v in enumerate(order)}; nv = len(names)
    M = fmpq_mat(len(C.rows), nv + 1)
    for i, (row, b) in enumerate(zip(C.rows, C.rhs)):
        for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
        M[i, nv] = fmpq(b.numerator, b.denominator)
    R, rk = M.rref()
    piv = [next(j for j in range(nv + 1) if R[i, j] != 0) for i in range(rk)]
    assert nv not in piv, "inconsistent"
    pset = set(piv); freecols = [p for p in range(nv) if p not in pset]; fidx = {p: t for t, p in enumerate(freecols)}
    expr = {}
    for i, p in enumerate(piv):
        nm = names[order[p]]
        if nm[0] == "x": continue
        expr[nm] = {fidx[q]: -Fr(int(R[i, q].p), int(R[i, q].q)) for q in freecols if R[i, q] != 0}
    for q in freecols:
        nm = names[order[q]]
        if nm[0] != "x": expr[nm] = {fidx[q]: Fr(1)}
    return [names[order[q]] for q in freecols], expr
if __name__ == "__main__":
    t0 = time.time()
    C = build(N); free, expr = reduce(C)
    expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
    top = lambda nm: nm[0] != "x" and expo(nm) > 9 * (N - 9)
    inner = [f for f in free if not top(f)]
    print(f"S0 cubic, N {N}: {len(free)} free, {len(inner)} genuine  [{time.time()-t0:.0f}s]")
    print("genuine free:", [(s, k, f"{expo((s, k, j))}/9") if s != "x" else (s, k, j) for s, k, j in inner])
