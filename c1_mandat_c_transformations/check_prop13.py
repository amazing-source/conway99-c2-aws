"""Machine check of the duality steps of Proposition 13 on the Berlekamp-van Lint-Seidel graph srg(243,22,1,2)
(eigenvalues 22, 4, -5; lines of size 3; N N^t = 11 I + A, equal to 6 on the (-5)-eigenspace).
General statement checked:  [E Z^n : E N Z^lines] = #{ x in L / cL : N^t x = 0 mod c },  L = Z^n cap ker(A + 5I), c = 6.
Left side from determinants of Gram matrices, right side from the Smith form of N^t B (B a basis of L)."""
import itertools, math
from flint import fmpz_mat, fmpq_mat, fmpz, fmpq
edges = [tuple(map(int, l.split())) for l in open("C:/home/researcher/Desktop/Nouveau/conway99-c1/data/srg243/bvls243.edges") if l.strip()]
n = 1 + max(max(e) for e in edges); assert n == 243 and len(edges) == 243 * 22 // 2
adj = [set() for _ in range(n)]
for a, b in edges: adj[a].add(b); adj[b].add(a)
lines = sorted({tuple(sorted((a, b, next(iter(adj[a] & adj[b]))))) for a, b in edges})
assert all(len(adj[a] & adj[b]) == 1 for a, b in edges) and len(lines) == 891
A = fmpz_mat(n, n)
for a, b in edges: A[a, b] = 1; A[b, a] = 1
I = fmpz_mat(n, n)
for i in range(n): I[i, i] = 1
# L = integer kernel of A + 5I  (saturated): nullspace then saturation by Hermite form of the transpose
K, nullity = (A + 5 * I).nullspace(); assert nullity == 110
Kb = fmpz_mat([[K[i, j] for i in range(n)] for j in range(nullity)])          # rows span the kernel over Q
# saturate: the lattice Z^n cap rowspace = rows of the primitive part; use LLL after removing content via HNF of transpose
H = Kb.hnf()
# saturation through Smith: Kb = U D V  ->  first 110 rows of V give a basis of the saturation
def saturate(M):
    r, c = M.nrows(), M.ncols()
    # kernel of the kernel: L = (L^perp)^perp, with integer nullspace computed by flint (nullspace gives a basis over Z of
    # a full-rank sublattice of the kernel); we use the standard trick  Z^n cap V = left kernel of a matrix whose columns
    # span V^perp, obtained from HNF with transformation
    Pm, rk = fmpz_mat([[M[i, j] for j in range(c)] for i in range(r)]).nullspace()   # columns: basis of M^perp (not saturated)
    P = fmpz_mat([[Pm[i, j] for i in range(c)] for j in range(rk)])                  # rows span V^perp
    # V = kernel of P; an integer basis of the saturated kernel: take HNF of [P^t | I] trick
    Aug = fmpz_mat(c, rk + c)
    for i in range(c):
        for j in range(rk): Aug[i, j] = P[j, i]
        Aug[i, rk + i] = 1
    Hh = Aug.hnf()
    rows = [[Hh[i, rk + j] for j in range(c)] for i in range(c) if all(Hh[i, j] == 0 for j in range(rk))]
    return fmpz_mat(rows)
B = saturate(Kb); assert B.nrows() == 110
assert all(x == 0 for x in ((A + 5 * I) * B.transpose()).entries())
detL = (B * B.transpose()).det()
print("rank of L:", B.nrows(), " det L =", detL, "=", dict((int(p), int(e)) for p, e in fmpz(detL).factor()))
# lattice E N Z^lines: generators are the projections of the line indicators; work with pairings instead:
# its dual in V is L2 = {y in V : y(T) integer}, so  [L2 : L] = index we want, and  det(L2) = det(L) / index^2.
# L2 = { B^t t / c' ... }: y = B^t u with u rational; conditions: N^t B^t u integral and y in V automatically.
N = fmpz_mat(n, len(lines))
for j, T in enumerate(lines):
    for v in T: N[v, j] = 1
M = (N.transpose() * B.transpose())            # 891 x 110 : u -> line sums of the vector  B^t u
S = M.snf(); d = [int(S[i, i]) for i in range(110)]
assert all(x != 0 for x in d)
# u must satisfy  M u in Z^891 : the lattice of such u is  V diag(1/d_i) Z^110, of index prod d_i over Z^110.
index_direct = math.prod(d)
count_mod6 = math.prod(math.gcd(x, 6) for x in d)
print("invariant factors of N^t B:", sorted(set(d)), " product =", index_direct)
print("[L2 : L] computed directly =", index_direct, "= number of x in L/6L with all line sums = 0 mod 6:", count_mod6, "->", index_direct == count_mod6)
# p-parts and the analogue of step (iv): is ker(N^t mod p) inside L/pL for p = 2, 3 ?
def rank_mod(Mx, p):
    from flint import nmod_mat
    return nmod_mat(Mx.nrows(), Mx.ncols(), [int(x) % p for x in Mx.entries()], p).rank()
for p in (2, 3):
    kerN = n - rank_mod(N.transpose(), p)
    inL = 110 - rank_mod(M, p)
    print(f"p = {p}: dim ker(N^t mod p) = {kerN}, of which inside L/pL: {inL}")
