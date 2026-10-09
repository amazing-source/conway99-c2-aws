"""Pilot 1 (mandate C).  Question: what is the exact algebraic shape of the only known non-trivial exact move in the
family srg(v,k,1,2), the triangle flip BvLS -> twisted 243 (note 159)?  Spectrum of D = A' - A, commutation, D^2."""
import numpy as np, sys, collections
R = "C:/home/researcher/Desktop/Nouveau/conway99-c1/data/srg243/"


def load(p, n=243):
    M = np.zeros((n, n), dtype=np.int64)
    for l in open(p):
        if l.strip():
            i, j = map(int, l.split()); M[i, j] = M[j, i] = 1
    return M


A = load(R + "bvls243.edges"); B = load(R + "twin243_switched.edges")
n = 243; I = np.eye(n, dtype=np.int64); J = np.ones((n, n), dtype=np.int64)
for X in (A, B):
    assert (X @ X + X == 20 * I + 2 * J).all()
D = B - A
print("nonzero entries of D:", int((D != 0).sum()), " +1:", int((D == 1).sum()), " -1:", int((D == -1).sum()))
rows = (D != 0).sum(1)
print("row supports:", dict(collections.Counter(rows.tolist())))
ball = [i for i in range(n) if rows[i] == 0]; far = [i for i in range(n) if rows[i] != 0]
print("unchanged rows:", len(ball), "changed:", len(far))
T = [i for i in ball if all(A[i, f] == 0 for f in far)]
print("triangle:", T)
assert (A @ D + D @ A + D @ D + D == 0).all()
print("A commutes with A':", bool((A @ B == B @ A).all()))
D2 = D @ D
print("D^2 commutes with A:", bool((D2 @ A == A @ D2).all()), " with A':", bool((D2 @ B == B @ D2).all()))
ev = np.linalg.eigvalsh(D.astype(float))
c = collections.Counter(np.round(ev, 6).tolist())
print("spectrum of D:", sorted(c.items()))
print("rank of D:", int(np.linalg.matrix_rank(D.astype(float))))
# principal angles: eigenvalues are 9 sin(theta)
print("sin^2 values:", sorted(collections.Counter(np.round((ev / 9) ** 2, 6).tolist()).items()))
# entries of D^2 by relation in A (restricted to far)
Df = D[np.ix_(far, far)]; Af = A[np.ix_(far, far)]; Bf = B[np.ix_(far, far)]
D2f = Df @ Df
print("values of D^2 on far x far:", dict(collections.Counter(D2f.flatten().tolist())))
# minimal polynomial test
for cst in (9, 27, 36, 45, 81):
    print("D^3 == %d D ?" % cst, bool((D2 @ D == cst * D).all()))
np.save("far243.npy", np.array(far)); np.save("T243.npy", np.array(T))
