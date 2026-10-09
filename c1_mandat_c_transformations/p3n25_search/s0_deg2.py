"""S0 (rank 43): SECOND MOMENTS class by class (nine classes).

For a trace-free symmetric tensor S on the (-4)-eigenspace and P(y) = y^T S y, the layer sums  Pi_Lam = sum_{y in Lam} P(y)
obey the even nine-class system of degree 2 (weight 28 + m; validated on K_8 + B^18).  With S = (Ee_v)(Ee_v)^T - E/99 this is,
for a vertex v,   Pi_Lam(v) = sum_{y in Lam} ( y_v^2 - |y|^2 / 99 ).
Question: how many free tensors remain in S0, and which exact linear relations hold between the low layers AT EVERY VERTEX?
usage: s0_deg2.py [N]"""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9quartic as ZQ, mf7
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
RHO, SIG = Z.RHO, Z.SIG
t0 = time.time(); top = 9 * (N - 9)
Q = ZQ.Even(43, N, d=2); Q.zeros()
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
free, expr = Q.reduce()
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
lab = lambda f: f"{'Theta' if f[0] == 'T' else 'Xi'}_{f[1]}[{expo(f)}/9]"
inner = [t for t, f in enumerate(free) if f[0] != "x" and expo(f) <= top]
print(f"S0, degree 2, truncation {N}: {len(free)} free, {len(inner)} genuine: {[lab(free[t]) for t in inner]}  [{time.time()-t0:.0f}s]")
E = lambda c, num9: expr[("X", c, (num9 - SIG[c]) // 9)]
low = [(2, 77), (2, 86), (1, 89), (2, 95), (1, 98), (2, 104), (1, 107), (4, 110), (2, 113), (1, 116), (0, 117), (3, 117), (4, 119), (2, 122), (1, 125),
       (0, 126), (3, 126), (4, 128), (2, 131), (1, 134), (0, 135), (3, 135), (2, 140)]
names = {(2, 77): "22-cocliques", (1, 89): "c1 layer", (2, 95): "w layer", (1, 98): "vertices and ghosts", (2, 104): "P3/N25", (4, 110): "44-sets",
         (0, 117): "integral norm 26", (3, 117): "fractional norm 26", (4, 119): "u layer", (0, 126): "integral norm 28 (integral norm 4 of M)",
         (3, 126): "lines and ghost lines", (2, 140): "edges and class-2 norm 40/9 of O", (2, 86): "P1/N23"}
print("layer second moments in terms of the free tensors (same relation at every vertex):")
for c, num9 in low:
    e = E(c, num9)
    assert e[0] == 0
    bad = [t for t in e[1] if t not in inner]
    print(f"   Xi_{c}[{num9}/9] ({names.get((c, num9), '')}) = " + (" ".join(f"{'+' if v > 0 else '-'} {abs(v)} {lab(free[t])}" for t, v in sorted(e[1].items())) or "0") + ("   !! truncation-edge terms" if bad else ""))
import pickle; pickle.dump({"free": free, "inner": inner, "expr": {k: v for k, v in expr.items() if k[0] == "X" and expo(k) <= top}}, open(f"s0_deg2_N{N}.pkl", "wb"))
