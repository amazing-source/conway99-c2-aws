# Part A1. From an automorphism of order 2 to a frame in one of 156 lattices

Part of the single proof document `lemma/PROOF_C2/` (statement: a strongly regular graph with parameters (99, 14, 1, 2) has no
automorphism of order 2). This file is the mathematical reduction, proved by hand; the numbering (R-i) to (R-vii) and A.0 to A.9
is the one every other part cites and must not change.

Status on 2026-10-07: text taken from `lemma/upstream/AUDIT_REDUCTION.md` section A as refereed that day (report
`lemma/t20_CODEX/REFEREE_REDUCTION.md`: no error in A.0 to A.9). To be polished as prose in the next pass; no statement or
proof is to change without a new referee pass.

Cited theorems: the oddity formula for integral quadratic forms (Conway-Sloane, SPLAG ch. 15); the classification of the odd
unimodular lattices of rank 24 without vector of norm 1 (Borcherds; SPLAG ch. 17): 156 classes; for the count N_3 = 4096 used
downstream, shadow theory (Conway-Sloane 1990).

## 1. The reduction theorem, with its proof

Notation: Gamma = srg(99,14,1,2), adjacency matrix A, so A^2 + A - 12 I = 2 J. sigma = an automorphism of order 2 with
Fix(sigma) = {x}.

> **Theorem R.** If (Gamma, sigma) exists, there are an odd unimodular lattice U of rank 24 without vector of norm 1, and vectors
> y_1, y_2, h_1..h_7, u_1..u_42 of U, such that
> (R-i) (y_a, y_b) = 7 delta_ab, and y_1, y_2 are orthogonal to every h_c and u_o;
> (R-ii) (h_c, h_d) = 4 delta_cd; (u_o, u_o) = 3; (u_o, u_o') is 0 or +-1 for o != o', nonzero for exactly ten o';
> (R-iii) (h_c, u_o) = -C_co, where the 42 columns of C are the vectors e_i + e_j and e_i - e_j (i < j) of Z^7;
> (R-iv) 3 h_c + sum_o C_co u_o = 0 for every c;
> (R-v) for every real v: sum_c (v,h_c)^2 + sum_o (v,u_o)^2 + (v,y_1)^2 + (v,y_2)^2 = 7 (v,v)   **(F)**;
> (R-vi) Z y_1 + Z y_2 is primitive in U; for every v of U outside it, E(v) := 7 (v,v) - (v,y_1)^2 - (v,y_2)^2 >= 8;
> (R-vii) for every v of U, the 49 integers (v,h_c), (v,u_o) are the values of a sigma-odd integer function phi on the vertices
> with A phi = -4 phi and sum phi^2 = 2 E(v).
> By Borcherds' classification U is one of 156 lattices.

### A.0 An automorphism of order 2 fixes exactly one vertex (hand proof, new; the citation of Makhnev-Minakova is no longer needed)

Let sigma be an automorphism of order 2, F its set of fixed vertices, f = |F|. 99 is odd, so f >= 1.
- For p in F, sigma permutes the seven blocks of N(p). A block with one fixed end is fixed pointwise (the other end is the unique
  common neighbour of p and the first). Let s_p = number of blocks fixed pointwise, t_p = number of blocks whose two ends are
  exchanged, 2 r_p = number of blocks sent to another block: **s_p + t_p + 2 r_p = 7**.
- A vertex z at distance 2 from p is determined by its two neighbours a, b in N(p); they lie in different blocks, and the 84 such
  pairs all occur. z is fixed iff {a,b} is invariant: a and b both fixed (2 s_p (s_p - 1) pairs), or b = sigma(a) in another block
  (2 r_p pairs). With p and its 2 s_p fixed neighbours: **f = 1 + 2 s_p^2 + 2 r_p for every p in F**.   (1)
- a_1 := #{v : v ~ sigma v}. For such a v, the unique common neighbour of v and sigma v is a fixed p, and {v, sigma v} is an
  exchanged block of p: a_1 = 2 sum_p t_p. A vertex v in a moved block of p is not adjacent to sigma v; their common neighbours are
  p and one other vertex q, which is fixed; every fixed neighbour of v is a common neighbour of v and sigma v. So v has exactly two
  fixed neighbours, and there are n_2 = 2 sum_p r_p such vertices. All these vertices are non-fixed and distinct:
  **a_1 + n_2 <= 99 - f**.   (2)
- sum_p s_p = 3 x (number of triangles fixed pointwise): **sum_p s_p = 0 mod 3**.   (3)
- The trace of sigma on the (-4)-eigenspace is an integer, and it equals tr(P E_{-4}) = **(3f - a_1 + 11) / 7**.   (4)

By (1), with s + t + 2r = 7, the possible triples (s, r, t) of a fixed vertex are, for each f:
f = 1: (0,0,7). f = 3: (0,1,5), (1,0,6). f = 5: (0,2,3), (1,1,4). f = 7: (0,3,1), (1,2,2). f = 9: (1,3,0), (2,0,5). f = 11: (2,1,3).
f = 13: (2,2,1). f = 19: (3,0,4). f = 21: (3,1,2). f = 23: (3,2,0). f = 33: (4,0,3). f = 35: (4,1,1). f = 51: (5,0,2). f = 53: (5,1,0).
f = 73: (6,0,1). f = 99: the identity. No other value of f is possible.
- f >= 19: a_1 + n_2 = 2 f (t + r) is 152, 126, 92, 198, 140, 204, 106, 146 for f = 19, 21, 23, 33, 35, 51, 53, 73: each exceeds
  99 - f, against (2).
- f = 11, 13: sum s_p = 22, 26, against (3).
- f = 3, 5, 7: let k be the number of fixed vertices with s = 1; by (3) k is a multiple of 3. Then a_1 = 30 + 2k (f = 3 and 5),
  14 + 2k (f = 7), and 3f - a_1 + 11 is -10, -16 (f = 3); -4, -10 (f = 5); 18, 12, 6 (f = 7): never a multiple of 7, against (4).
- f = 9: let k be the number of fixed vertices with s = 2; sum s_p = 9 + k, so k is 0, 3, 6 or 9; a_1 = 10k and
  3f - a_1 + 11 = 38, 8, -22, -52: never a multiple of 7, against (4).
Hence **f = 1**. (Control of formula (1) on H(2,3) = srg(9,4,1,2), two blocks: x -> -x has (s,r,t) = (0,0,2), f = 1; the swap of
coordinates has (0,1,0), f = 3; (x,y) -> (x,-y) has (1,0,1), f = 3. All three are right.)

So Theorem R applies to every automorphism of order 2, and its conclusion reads: **no srg(99,14,1,2) has an automorphism of
order 2**, once the 156 envelopes are excluded.

### A.1 The involution flips the seven blocks (hand proof; uses only Fix = {x})

N(x) is seven disjoint edges ("blocks"), since lambda = 1.
- sigma preserves N(x) and fixes none of its 14 vertices. If sigma exchanged two vertices a, b of different blocks, then a, b are
  not adjacent, their two common neighbours are x and one vertex w, and {x, w} is sigma-invariant, so w is fixed: contradiction.
  Hence sigma exchanges the two ends of every block.
- If u ~ sigma(u), the edge is invariant, its unique common neighbour is fixed, so it is x, and u is in N(x). Hence the 84 other
  vertices ("outer") satisfy u !~ sigma(u). There are 49 orbits of size two: 7 inner, 42 outer.
- An outer u has exactly two neighbours in N(x) (mu = 2 with x), in two different blocks (two ends of one block are adjacent and
  already have x as their unique common neighbour). For two blocks i < j, the four non-adjacent pairs of inner vertices have one
  outer common neighbour each: 4 outer vertices, 2 orbits. So the 42 outer orbits are indexed by the pairs {i,j} with a sign.
- For outer u, N(u) n N(sigma u) has two elements (mu = 2), is sigma-invariant, and does not contain x: it is one orbit {v, sigma v},
  and v is outer (an inner v would put two ends of one block in N(u)).

Source: `conway99-involution/notes/NOTE_involution_case.md` section 2 (a)-(c). Checked: correct.

### A.2 The signed quotient (hand proof)

On the sigma-odd functions (dimension 49, basis d_o = e_o - e_sigma(o) for chosen representatives), A acts by a symmetric integer
matrix S, S_UV = A[u,v] - A[u, sigma v]. J kills odd functions, so **S^2 + S = 12 I**. Diagonal: -1 on the 7 inner orbits, 0 on the 42
outer ones; trace -7, so the eigenvalues are 3 (27 times) and -4 (22 times).
With inner representatives (c,0) and outer representatives chosen by A.1: S = [[-I_7, C], [C^t, T]], the columns of C are e_i + e_j,
e_i - e_j. T has zero diagonal and entries 0, +-1; by A.1 exactly one orbit {v, sigma v} lies in N(u) entirely, so each row of T
has exactly **ten** nonzero entries. The blocks of S^2 + S = 12 I read C C^t = 12 I_7, C T = 0, T^2 + T = 12 I - C^t C.

### A.3 The lattice N and the frame (hand proof)

H := 3I - S satisfies H^2 = 7H and has rank 22. Put u_i := H e_i / sqrt 7. Then (u_i, u_j) = H_ij, so the 49 vectors have Gram H:
norm 4 on the 7 inner ones (call them h_c), norm 3 on the 42 outer ones (u_o), (h_c,h_d) = 0, (h_c,u_o) = -C_co, Gram(u) = 3I - T.
For v in the real span V (= image of H, where Hv = 7v): sum_i (v,u_i)^2 = |Hv|^2 / 7 = 7 (v,v): a tight frame of constant 7.
The vector (3 e_c ; C_c^t) is a 3-eigenvector of S (uses C C^t = 12 I and C T = 0), so it is killed by H: this is (R-iv).
N := the lattice generated by the 49 vectors. With K := Z^49 n V (the integer (-4)-eigenvectors of S):
**N = sqrt7 K^\*** and **N^\* = K / sqrt7** (K^* is the projection of Z^49 on V, which is H Z^49 / 7).
For v in N^*, the integers a_i = (v,u_i) form the vector a = sqrt7 v of K, and sum a_i^2 = 7 (v,v).

### A.4 The discriminant form of N: its Witt class is the anisotropic plane, for every g (hand proof + oddity formula)

Let K' := Z^49 n (3-eigenspace). K and K' are primitive and orthogonal, and 7 Z^49 is inside K + K' (x = Hx/7 + (S+4)x/7).
So Z^49 / (K + K') = F_7^g, det K = 7^g, and g = rank over F_7 of S - 3I. The discriminant group of N is K / 7K^* = F_7^(22-g).

*Oddity of K.* The index 7^g is odd, so over Z_2 the lattice Z^49 is the orthogonal sum of K and K', both unimodular, and the
projection c = H 1 / 7 of the characteristic vector 1 is characteristic in K. Its norm is (147 - s)/7 with s = 1^t S 1.
In the gauge of A.2: s = -7 + 2*42 + (420 - 4M) = 497 - 4M, where M = number of unordered pairs with T = -1.
M is even: 1^t (S^2 + S) 1 = 588 = sum of the squared row sums + s. The 7 inner row sums are odd (squares = 1 mod 8). The outer row
sum r_o is even, and r_o = 2 mod 4 holds for an odd number q of rows (r_o = c_o + 10 - 2 m_o with c_o in {0,2}, sum of c_o/2 = 21,
sum of m_o = 2M). So 588 = 7 + 4q + s mod 8 gives s = 1 mod 8, hence M even, and **(c,c) = 7 (147 - s) = 6 mod 8**.

*Oddity formula* (Conway-Sloane, SPLAG ch. 15): signature + sum over odd p of the p-excess = oddity (mod 8).
For K (positive definite, rank 22, 7-adic Jordan form 1^(e0 (22-g)) 7^(e g)): 22 + 6g + 4 [e = -1] = 6 (mod 8).
So **g is even and e = (-1)^(g/2)**. As det K = 7^g exactly, e0 = e.

*Consequence.* The discriminant form of N is the form of the unit constituent of K: dimension 2m = 22 - g, determinant sign
e0 = (-1)^(g/2) = -(-1)^m. A split (hyperbolic) form of dimension 2m over F_7 has sign (-1/7)^m = (-1)^m. So the form is **not**
split: m >= 1 (g = 22 is impossible), its Witt index is m - 1 and its anisotropic kernel is a plane.
Take a totally isotropic subspace I of dimension m - 1 and let **Nmax** be its preimage in N^*. Then Nmax is an integral lattice,
N < Nmax < N^*, of index 7^(m-1) over N, det Nmax = 49, and its discriminant form I^perp / I is the anisotropic plane over F_7.

This replaces the upstream statement "g is 18 or 20; for g = 18 take an isotropic line": the same construction works for any g.
Sources: `conway99-structures-lab/NOTE_S27_INVOLUTION_GENRE_7ADIQUE.md` section 1 (oddity; states g even, g != 22, e fixed by g),
`.../PREUVES_COMPLETES_REPERE42_7.md` "Unification g18/g20" (the g = 18, 20 construction). Checked: the computation of S27 is
correct; I redid 1^t S 1 mod 8 independently of its gauge formula. Controls of the same formula on real graphs: S27 section 4.

### A.5 min N^\* >= 8/7 (hand proof, redone)

Claim: no nonzero a in Z^49 with S a = -4a and sum a_i^2 <= 7. (Equivalently: no sigma-odd integer (-4)-eigenfunction of A with sum of
squares <= 14.)
- An entry +-2 leaves at most 3 for the other squares, so the other entries have absolute sum <= 3; but row i of S a = -4a asks
  for an off-diagonal sum of absolute value 8 (outer) or 6 (inner). So a has entries 0, +-1 and support m <= 7.
- Lift a to phi on the 99 vertices, P = {phi = 1}, Q = sigma(P) = {phi = -1}, |P| = m, e = edges in P, d_i = degree in P.
  A phi = -4 phi gives deg_Q(i) = d_i + 4. Count the common neighbours of the pairs of P: the total is m(m-1) - e; the vertices of
  P and Q contribute sum (d_i^2 + 3 d_i + 6) = sum d_i^2 + 6e + 6m. So the others contribute D = m(m-7) - 7e - sum d_i^2 >= 0.
  Hence m = 7, e = 0, D = 0.
- B_ij := [i ~ sigma j] on P is symmetric with row sums 4 and B^2 = 2I + 2J (two common neighbours for each pair, all in Q because
  D = 0). Its eigenvalues are 4 and +-sqrt2 with equal multiplicities (rational characteristic polynomial), so trace B = 4: four
  vertices of P are adjacent to their mates. By A.1 they are in N(x). Then x, which is outside P and Q, sees four vertices of P
  and contributes 6 to D = 0. Contradiction.
So min K >= 8 and min N^* >= 8/7.
Source: `.../attaque_globale_27_0803/AUDIT_NORME1_ET_METRIQUES.md`. Checked: correct, every line.

### A.6 The envelope U (hand proof)

J := Z r_1 + Z r_2 with (r_a, r_b) = 7 delta_ab. Its discriminant form (x_1^2 + x_2^2)/7 on F_7^2 is anisotropic (-1 is not a
square mod 7). Nondegenerate forms over F_7 are classified by dimension and determinant, an anisotropic plane has square
determinant, and so does its negative: the discriminant forms of Nmax and J are anti-isometric. Glue along the graph of an
anti-isometry: **U** contains Nmax + J with index 49, is integral, has rank 24 and determinant 49*49/49^2 = 1, and is odd (it
contains vectors of norm 3). Nmax and J are primitive in U (the glue projects injectively to both discriminant groups).
- No vector of norm 1: for v in U with (v,v) = 1, the projection of v on V lies in Nmax^*, which is inside N^*, and has norm <= 1 <
  8/7, so it is 0; then v is in J (primitive), whose minimum is 7.
- y_a := r_a. (F) is the frame identity of A.3 on V plus the orthogonal basis y_1, y_2 of norm 7 of the plane V^perp.
- (R-vi), (R-vii): for v in U, the projection of v on V is in N^*; by A.3 its 49 products form a vector a of K with
  sum a_i^2 = 7 |proj|^2 = E(v), and a = 0 only if v is in J. A.5 gives E(v) >= 8 otherwise. (This is `lemma/BRIDGE.md`.)

U is not unique (choice of I and of the anti-isometry). Only its existence is used.

### A.7 Classification (cited)

Odd unimodular lattices of rank 24 without vector of norm 1: exactly 156 classes (Borcherds, thesis 1984; SPLAG ch. 17,
Table 17.1). The odd Leech lattice (no root, id 000) is one of them. This is a cited theorem. What our files must guarantee is
only that the 156 Gram matrices we use are these 156 lattices: section D.

### A.8 Two consequences used by every exclusion (hand proof)

- **New roots.** Let z be a characteristic vector of U with (z,z) = 8 and beta = z/2. (z,u_o) and (z,y_a) are odd, (z,h_c) is even.
  (F) at beta: 14 = sum (beta,u_o)^2 + sum (beta,h_c)^2 + sum (beta,y_a)^2, with 42 terms >= 1/4, two terms >= 1/4, and each product
  of absolute value 3/2 adds 2. So w(beta) := sum_c (beta,h_c)^2 = 3 - 2 * (number of frame vectors hitting beta at 3/2) is 1 or 3,
  at most one frame vector hits beta at 3/2, and |(beta,h_c)| <= 1. (C1 notes 139 (E), 140 section 2, 142.)
- **Characteristic trap.** For characteristic z of norm 16: E(z) = 112 - Y with Y = (z,y_1)^2 + (z,y_2)^2 = 2 mod 8, and
  E(z) = (42 odd squares) + 4 sum b_c^2 with (z,h_c) = 2 b_c. Mod 8: 6 = 42 + 4 sum b_c^2, so sum b_c^2 is odd, E >= 46, **Y <= 66**.

### A.9 The envelope is indecomposable (hand proof, new; second proof for 153, and for 152)

> **Lemma.** U is not an orthogonal sum L_1 + L_2 of two nonzero lattices.

Proof. Suppose U = L_1 + L_2. Both summands are unimodular without vector of norm 1, so their nonzero vectors have norm >= 2, and
a vector of norm 3 lies in one summand (3 = 3 + 0 only). So each u_o is in L_1 or in L_2.
Take two orbits o, o' sharing exactly one block i. Then (C^t C)_oo' = C_io C_io' = +-1, and the identity T^2 + T = 12 I - C^t C of
A.2 gives sum_o'' T_oo'' T_o''o' + T_oo' = -+1. If u_o is in L_1 and u_o' in L_2, then T_oo' = -(u_o,u_o') = 0 and every term
T_oo'' T_o''o' = (u_o,u_o'')(u_o'',u_o') is 0, because u_o'' lies in one summand: contradiction. So two orbits sharing exactly one
block are in the same summand. The graph "share exactly one block" on the 42 orbits ({i,j}, sign) is connected (({i,j},+) and
({i,j},-) are both adjacent to ({i,k},+)), so all the u_o are in one summand, say L_1. By (R-iv) the h_c are in its real span.
Hence L_2 is orthogonal to the 49 vectors, so it lies in the plane of y_1, y_2 and has rank 1 or 2. A unimodular lattice of rank
1 or 2 is Z or Z^2 and has vectors of norm 1: contradiction. QED

Among the 156, the decomposable lattices are exactly **153** (D12+ + D12+, roots d_12^2) and **152** (E8 + the odd lattice of
rank 16 with roots d_8^2): a unimodular summand without norm 1 has rank 8 (E8), 12 (D12+) or >= 14, and the complement must be
odd or the sum is even. So 153, which rested on one argument reread by C1 only (section E), is excluded by this lemma as well.
