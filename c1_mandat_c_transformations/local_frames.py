"""Pilot 2 (mandate C).  The closed neighbourhood of a vertex x is the one base whose structure is forced, with symmetry
group B_7 (hyperoctahedral).  The 84 second neighbours carry two tight frames, of ranks 30 and 40 (projections on the
(-4)- and 3-eigenvectors vanishing on N[x]); their Gram entries depend only on the B_7-class of the pair and on its
adjacency.  Question to decide: do the RANK-SENSITIVE two-point conditions (Gegenbauer in dimensions 30 and 40, Schur
products of both, traced against the six B_7 idempotents) cut the triangle 0 <= s <= W <= 84 of the local torsion
statistics (W(x), s(x)) of note 90 ?  First-order version (note 90, section 6) and local Krein (note 70) cut nothing.
A cut at W = 84 would mean 'every vertex lies on a prism'."""
import numpy as np, itertools, sys

pts = [(i, e) for i in range(7) for e in (0, 1)]
mate = lambda p: (p[0], 1 - p[1])
lab = [frozenset((p, q)) for p, q in itertools.combinations(pts, 2) if p[0] != q[0]]
n = len(lab); assert n == 84
idx = {l: i for i, l in enumerate(lab)}


def cls(x, y):
    if x == y: return 0
    ym = frozenset(mate(p) for p in y)
    k, k2 = len(x & y), len(x & ym)
    if k == 1 and k2 == 1: return 1          # R_a   : one common label, the others mates       (valence 2)
    if k == 1 and k2 == 0: return 2          # R_sh  : one common label                         (20)
    if k == 0 and k2 == 2: return 3          # R_sigma                                          (1)
    if k == 0 and k2 == 1: return 4          # R_cl  : disjoint labels, one common class        (20)
    if k == 0 and k2 == 0: return 5          # R_dj                                             (40)
    raise ValueError


R = np.zeros((6, n, n))
for i, x in enumerate(lab):
    for j, y in enumerate(lab):
        R[cls(x, y), i, j] = 1
val = [int(R[k][0].sum()) for k in range(6)]
assert val == [1, 2, 20, 1, 20, 40], val
# base B = {x} + 14 points ; C = B x labels incidence ; A_B
C = np.zeros((15, n))
for u, p in enumerate(pts):
    for j, y in enumerate(lab):
        if p in y: C[1 + u, j] = 1
AB = np.zeros((15, 15)); AB[0, 1:] = AB[1:, 0] = 1
for u, p in enumerate(pts): AB[1 + u, 1 + pts.index(mate(p))] = 1
Cp = np.linalg.pinv(C)
PY = np.eye(n) - Cp @ C
M0 = (2 * np.ones((n, 15)) - C.T @ (AB + np.eye(15))) @ Cp.T
cmat = M0 + 3 * PY                         # 7 Pi = cmat - H   (H = adjacency of the second neighbourhood)
c = []
for k in range(6):
    v = cmat[R[k] == 1]; assert np.ptp(v) < 1e-9; c.append(float(v[0]))
print("class constants c_k of 7*Pi30 + H:", np.round(c, 6), " times 8:", np.round(np.array(c) * 8, 6))
print("rank of P_Y:", round(np.trace(PY)))
# idempotents of the scheme
rng = np.random.default_rng(1); Mx = sum(rng.normal() * R[k] for k in range(1, 6))
w, V = np.linalg.eigh(Mx)
groups = []; start = 0
for i in range(1, n + 1):
    if i == n or abs(w[i] - w[start]) > 1e-6:
        groups.append((start, i)); start = i
E = [V[:, a:b] @ V[:, a:b].T for a, b in groups]
dims = [b - a for a, b in groups]
print("idempotent ranks:", dims)
Ek = [[float(E[j][R[k] == 1][0]) for k in range(6)] for j in range(len(E))]
inY = [abs(np.trace(E[j] @ PY) - dims[j]) < 1e-6 for j in range(len(E))]
print("inside Y:", inY)


def geg(m, d, t):                           # Gegenbauer C_m^{(d-2)/2}(t), normalised to 1 at t = 1
    a = (d - 2) / 2.0
    p0, p1 = np.ones_like(t), 2 * a * t
    if m == 0: return p0
    for k in range(2, m + 1):
        p0, p1 = p1, (2 * (k + a - 1) * t * p1 - (k + 2 * a - 2) * p0) / k
    q0, q1 = 1.0, 2 * a
    for k in range(2, m + 1):
        q0, q1 = q1, (2 * (k + a - 1) * q1 - (k + 2 * a - 2) * q0) / k
    return p1 / q1


# Gram values:  7 Pi30 = c_k - h,   7 Pi40 = 7 P_Y - 7 Pi30 = py_k*7 - c_k + h
py = [float(PY[R[k] == 1][0]) for k in range(6)]
def t30(k, h): return (c[k] - h) / c[0]
def t40(k, h): return (7 * py[k] - c[k] + h) / (7 * py[0] - c[0])
print("norms: 7*Pi30_xx =", c[0], " 7*Pi40_xx =", 7 * py[0] - c[0], " -> ranks", 84 * c[0] / 7, 84 * (7 * py[0] - c[0]) / 7)
# ordered-pair counts per class as affine functions (const, coefW, coefs) of (W, s):  adjacent pairs
adj = {1: (168, -2, 0), 2: (0, 2, 0), 3: (0, 0, 1), 4: (0, 2, -2), 5: (840, -2, 1)}
tot = {k: 84 * val[k] for k in range(1, 6)}
ineqs = []                                  # (const, cW, cs) >= 0
MAXM = int(sys.argv[1]) if len(sys.argv) > 1 else 10
for m in range(0, MAXM + 1):
    for q in range(0, MAXM + 1):
        if m == 0 and q == 0: continue
        for j in range(len(E)):
            f = lambda k, h: float(geg(m, 30, np.array(t30(k, h))) * geg(q, 40, np.array(t40(k, h))))
            const = 84 * Ek[j][0] * 1.0     # diagonal: both Gegenbauer are 1 at t = 1
            cW = cs = 0.0
            for k in range(1, 6):
                f1, f0 = f(k, 1), f(k, 0)
                a0, aW, as_ = adj[k]
                const += Ek[j][k] * (a0 * f1 + (tot[k] - a0) * f0)
                cW += Ek[j][k] * aW * (f1 - f0); cs += Ek[j][k] * as_ * (f1 - f0)
            ineqs.append((const, cW, cs, m, q, j))
# feasible region: vertices of {0<=s<=W<=84} cut by the inequalities; report the binding ones
def ok(W, s, tol=1e-7): return all(a + b * W + c_ * s >= -tol for a, b, c_, *_ in ineqs)
viol = [(a + b * 84 + 0 * c_, m, q, j) for a, b, c_, m, q, j in ineqs]
for name, (W, s) in {"untwisted (0,0)": (0, 0), "(84,0)": (84, 0), "(84,84)": (84, 84), "(42,0)": (42, 0), "(42,42)": (42, 42)}.items():
    worst = min((a + b * W + c_ * s, m, q, dims[j]) for a, b, c_, m, q, j in ineqs)
    print(f"{name:18s} feasible: {ok(W, s)}   smallest slack {worst[0]:.6g} at (m,q,dim)={worst[1:]}")
feas = [(W, s) for W in range(0, 85) for s in range(0, W + 1) if ok(W, s)]
print("integer points (W,s) with 0<=s<=W<=84:", 85 * 86 // 2, " feasible:", len(feas))
if feas:
    print("W range:", min(W for W, s in feas), max(W for W, s in feas), " s range:", min(s for W, s in feas), max(s for W, s in feas))
    for W in (0, 14, 28, 42, 56, 70, 84):
        ss = [s for (w_, s) in feas if w_ == W]
        print("  W =", W, " s in", (min(ss), max(ss)) if ss else None)
