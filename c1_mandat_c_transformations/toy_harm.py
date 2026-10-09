"""Validation of the Fricke relation for theta series with a harmonic quartic, on a toy lattice of level 7.
Lambda = H7 + H7 in R^4 (H7: Gram [[2,1],[1,4]]), determinant 49.  Claim (Poisson with a harmonic P of degree 4):
    Theta_{Lambda,P} |_6 W7 = - Theta_{sqrt7 Lambda^#, P}        (weight 2 + 4 = 6, Gamma_0(7)).
Exact arithmetic in Q(sqrt7) is avoided by choosing coordinates where both lattices are rational."""
from fractions import Fraction as Fr
import itertools, mf7
N = 30
# H7 embedded in R^2 with an orthonormal-free trick: work with Gram matrices and coordinates.
G1 = [[2, 1], [1, 4]]
def gram4(): 
    G = [[0]*4 for _ in range(4)]
    for b in range(2):
        for i in range(2):
            for j in range(2): G[2*b+i][2*b+j] = G1[i][j]
    return G
G = gram4()
def inv(M):
    n = len(M); A = [list(map(Fr, r)) + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0); A[c], A[p] = A[p], A[c]
        iv = 1 / A[c][c]; A[c] = [x * iv for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]
Gi = inv(G)                       # Gram of the dual basis; sqrt7*dual has Gram 7*Gi (integral)
# a harmonic quartic on the quadratic space: P(x) = <x,u>^4 - 6|u|^2|x|^2<x,u>^2/(d+4) + 3|u|^4|x|^4/((d+2)(d+4)), d = 4
# vectors are given by coordinates in the basis of Lambda; u is a fixed vector of Lambda tensor Q (coordinates uc).
uc = [Fr(1), Fr(2), Fr(-1), Fr(3)]
def ip(x, y, M): return sum(x[i] * M[i][j] * y[j] for i in range(4) for j in range(4))
u2 = ip(uc, uc, G)
def P(xu, x2): return xu ** 4 - Fr(6) * u2 * x2 * xu ** 2 / 8 + Fr(3) * u2 ** 2 * x2 ** 2 / 48
def theta(coords_to_basis, M, scale):
    """sum over integer coordinate vectors c of P(x) q^(|x|^2/2), x = scale * (sum c_i b_i), b_i with Gram M
    coords_to_basis: matrix expressing b_i in the basis of Lambda (to compute <x,u>)."""
    out = [Fr(0)] * (N + 1); R = 8
    for c in itertools.product(range(-R, R + 1), repeat=4):
        x2 = ip(c, c, M) * scale
        if x2 > 2 * N or x2 % 2: continue
        # <x,u> = sqrt(scale) * sum_i c_i <b_i,u> ; scale is 1 or 7: for scale 7 we get sqrt7 * rational
        xu = sum(c[i] * coords_to_basis[i] for i in range(4))
        out[int(x2) // 2] += P_scaled(xu, x2, scale)
    return out
def P_scaled(xu, x2, scale):
    # x = sqrt(scale)*y, <x,u> = sqrt(scale)*xu : even powers only, so everything is rational
    return scale ** 2 * xu ** 4 - Fr(6) * u2 * x2 * scale * xu ** 2 / 8 + Fr(3) * u2 ** 2 * x2 ** 2 / 48
# Lambda: b_i = basis, <b_i,u> = (G uc)_i
bu = [sum(G[i][j] * uc[j] for j in range(4)) for i in range(4)]
T1 = theta(bu, G, 1)
# dual basis b_i^*: <b_i^*, u> = uc_i ; Gram Gi ; scaled by sqrt7
T2 = theta(uc, Gi, 7)
S = mf7.Space(6)
c1 = S.coords(T1 + [0] * (mf7.N - N)); im = S.expand(S.fricke_coords(c1))
print("Theta_{Lambda,P}      :", [str(x) for x in T1[:6]])
print("Theta_{sqrt7 L^#,P}   :", [str(x) for x in T2[:6]])
print("W7 image of the first :", [str(x) for x in im[:6]])
print("relation  Theta|W7 = -Theta_dual :", all(im[n] == -T2[n] for n in range(N + 1)))
