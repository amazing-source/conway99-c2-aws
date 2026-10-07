# Audit of the reduction "involution => one of the 156 envelopes" (2026-10-07)

Owner of sections A and F: laptop session (LAP). Sections B to E are to be filled by their owners (see section G).
Written without sub-agents, by reading the sources and redoing every step by hand.

**Question audited.** The whole route (C) rests on one implication: *if srg(99,14,1,2) has an automorphism of order 2 with exactly
one fixed vertex, then one of Borcherds' 156 lattices carries a frame*. The exclusions of the 156 are worth nothing if this
implication has a hole. Until today its four steps were "source only, not reread" (`lemma/upstream/README.md`).

## Result in five lines

1. **The implication holds.** Every step is proved below (section A) from the definition of the graph, with two cited theorems:
   the oddity formula for integral quadratic forms, and Borcherds' classification of the unimodular lattices of rank 24.
2. **One upstream input is not needed, and it was the weakest one.** All upstream texts "accept" g in {18, 20} (g = rank mod 7 of
   S - 3I) as an input from C1 / "structures". Its proof chain is long: block-line enumeration (g >= 14), Blichfeldt (g != 8, 10),
   and C1 note 132 (g != 16: 96 classes, LP infeasibility with Farkas certificates, marked "to be reread"). Section A.4 shows that
   the envelope exists **for every g**: the oddity formula alone gives the Witt class of the discriminant form. Theorem R does not
   mention g; section B must confirm that no rule of the engine uses it.
3. **Makhnev-Minakova (2004) is not needed for C2 as stated** (one fixed vertex is the hypothesis). It is needed only for the
   corollary "no involution at all" (every involution has exactly one fixed vertex). It is a published theorem, not reproved here.
4. The bound min N* >= 8/7 is correct (A.5, redone line by line). It is the same kind of statement as T18 / T20: no sigma-odd
   integer (-4)-eigenfunction with sum of squares <= 14.
5. Not covered by this file, and still to be audited by their owners: the rules of the search engine (B), the completeness of the
   enumeration of the pairs (C), the identity of the 156 Gram matrices (D), the provenance of the older exclusions (E).

## A. The reduction theorem, with its proof

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

## B. Rules of the search engine (owner: CDX, with LAB for the file list)

For each pruning rule of `frame_dfs_next.py` (sha 1591aeeac9c0be5c) and of the pair filters: the statement, why it is a consequence
of (R-i)..(R-vii), where the proof is written, who reread it. One line per rule. The skeleton lists: component budget, packing,
per-pair root-class budget, characteristic trap (proved in A.8), swap rule, twin envelope and transfer / deferral, endpoint
confinement, boundary points, symmetry breaking by reflections, Lemma Z (sum of the h in 2U), cells.

_To be filled._

## C. Completeness of the enumeration of the pairs (y_1, y_2) (owner: LAB)

Argument (C1 note 142 item 3): y_1 dominant for W(R) with |(alpha,y_1)| <= 2 (from E(alpha) >= 8); y_2 dominant for the stabiliser
of y_1 (generated by the simple reflections with zero label, Steinberg); then orbits under Gamma, a group of diagram automorphisms
each checked to preserve U. Using a subgroup of Aut(U) is always sound. To state here: (1) for which lattices the producer
`y_pairs_gamma.py` was compared with an independent enumeration, and the result; (2) how the lattices whose roots do not span
(ids 000 to about 016, Golay routes) are enumerated and why that is complete; (3) the swap rule.

**Filled by LAB on 07/10 (sources read: `c1/code/y_pairs.py`, `y_pairs_gamma.py`, `y2_engine.py` of package v10; lab notes 49, 51, 56;
the lab tracker). Status words: OK-REREAD = reread by me today; SOURCE-ONLY = the source exists, not reread; OPEN = not done.**

**(0) The producer's filters follow from Theorem R, and nothing uses g** (OK-REREAD, the statements only). `y_pairs.py` keeps a pair iff:
roots: |(alpha,y)| <= 2 and (alpha,y_1)^2 + (alpha,y_2)^2 in {0,1,2,4,5}; new roots: |(beta,y)| <= 3/2, never both 3/2; norm 3:
|(v,y)| <= 3, never both 3; (y_1,y_2) = 0; and "the exact trap min (y-perp cap U)^* >= 8/7". All are instances of (R-vi) E(v) >= 8
(E = 14 - Y >= 8 for a root gives Y <= 6, and 3, 6 are not sums of two squares; E = 21 - Y >= 8 for norm 3 gives Y <= 13) and of A.8
(new roots; y_1, y_2 are among the 51 vectors of (F)). **No file of the engine or of the producer uses the value of g, the index
[Nmax : N] or the determinant 49** (searched in `frame_dfs_next.py`, `hstage_stream_next.py`, `twin_transfer.py`,
`golay_pairs_job.py`, `y_pairs.py`, `y_pairs_gamma.py`, `y2_engine.py`, `envelope_trap.py`). The only arithmetic mod 7 is in
`twin_transfer.py`: the twin envelope is the other gluing of U cap {y_1,y_2}^perp with the plane, x -> x + ((c-a) y_1 + (d-b) y_2)/7
with (c,d) = R(a,b) mod 7, R = [[2,2],[-2,2]]; it uses only the discriminant group of 7 I_2.

**(1) Comparison with an independent enumeration: NOT DONE for the stream producer (OPEN).**
- What exists: the lab's own enumerator `scripts/ypairs_c2.py` (second reader of C1's `y_pairs`; reduction by W(R) only, own simple
  roots, own Fincke-Pohst). It was started on 087 on 27/09 and never completed (its output file is truncated); the double-reading
  protocol (b) of lab note 49 was then deferred by the "sweep-first" decision of 27/09 and never resumed. The tracker says so for 087,
  115 and 132 ("pending: independent pair enumeration").
- What was checked instead: every Gamma matrix is verified at load (Gram preserved, simple roots permuted), after the incident of
  27/09 (LLL bases differ between machines: note 51 section 6); the union of the chunks is the single-run list; every pair is checked
  in U exactly by the consumer, and its norms and orthogonality by the engine's pair set-up (and now by the certificates).
- Golay family: two implementations agree on 001 (structures' pipeline and the lab's `golay_gen.py`: identical admissible y set,
  identical 14 y_1 classes, identical pair-class counts), per the header of `golay_pairs_job.py`; not re-run today.
- **Proposal to close this point cheaply:** run `ypairs_c2.py` to the end on two or three small lattices (140: 288 pairs, 141: 319,
  135: 464) and check that every W(R)-dominant pair it finds is Gamma-equivalent to a listed pair, and that the orbit counts agree.
  I try the smallest one on the lab PC (a few minutes); if it is longer it goes to a free machine.

**(2) Lattices whose roots do not span.** SOURCE-ONLY for the argument; what the code does:
- 000 (no root): 141 classes of pairs from C1 (`o24_ypairs.json`), treated class by class (86 by LP certificates, 55 searched).
- 001, 002, 004, 010 (roots a_1^k, Golay frame): pair lists generated in the A_1^24 Golay frame (`golay_gen.py`), reduced by the
  frame's group and the swap filter; blocks of pairs.
- every other lattice, spanning or not, goes through the same producer: y is split into its weight part on each root component
  (dominant labels of level <= 2, a DP over the glue classes) and a part in span(R)^perp cap U enumerated by a shifted Fincke-Pohst
  with exact integer checks (`y2_engine.py`: "rootless part by a small shifted enumeration"; the producer's information line gives
  the rank, e.g. 14 for 003 and 18 for 006). Gamma is then a group of matrices verified to preserve the Gram matrix and the roots:
  a subgroup of Aut(U), which is sound.

**(3) Swap rule** (`hstage_stream_next.py`, FD_SWAP): the frame conditions are symmetric in (y_1, y_2), and the enumeration lists both
orders (y_2 runs over all admissible vectors for each y_1 representative). An Aut(U)-invariant I(y) is computed (sum of
(alpha,y)^2 over the roots, and the sorted pair of the numbers of new roots hit at 3/2 in the two shadow cosets); a pair with
I(y_1) > I(y_2) is SWAP-COVERED: the swapped pair appears as a pair of the y_1-orbit of y_2 and is treated there; pairs with
I(y_1) <= I(y_2) are treated. Sound because I is invariant under Aut(U) (the sort handles automorphisms exchanging the two cosets).
Status: statement and code OK-REREAD on 04/10 with the twin rules; the proof text is Astra's (28/09), SOURCE-ONLY.

## D. The 156 Gram matrices are the 156 lattices (owner: LAB)

`lemma/upstream/README.md` says "recomputed, complete, 156 pairwise non-isometric". To state here: how each lattice is built, which
invariants separate the 156 (in particular the pairs with the same root system: 023/027, 056/058, 120/121), and whether the mass
check was done (sum of 1/|Aut| against SPLAG Table 17.1).

**Filled by LAB on 07/10** (recomputation of 04/10: `scripts/analysis/audit_L1_lattices.py`, `audit_L1_neighbours.py` in the lab;
log in `work/AUDIT_156_PLAN_2026-10-04.md` of the research workspace).

- **How built:** each lattice is given by generators, rational vectors of R^24 with the standard inner product
  (`external_runs/structures_3eceb4d/U/000..155.json`, from the "structures" project). The construction itself is SOURCE-ONLY and is
  not needed: what matters is checked on the data.
- **Recomputed for all 156 (OK-RECOMPUTED):** exact integer determinant 1; odd; no vector of norm 1; the root system recomputed from
  the vectors of norm 2 (components, type from rank and number of roots) equals the label of Borcherds' table, with the same number
  of roots.
- **Separation of the 156:** the root system separates all but seven pairs: 016/017, 023/027, 056/058, 077/079, 082/085, 120/121,
  145/146. For these the two even neighbours (the Niemeier lattices U_0 + each coset of the shadow, recomputed from the data) differ.
  So the 156 data lattices are pairwise non-isometric, and by Borcherds' count they are all the classes.
- One erratum found in the table used for the labels (not in the data): lattice 150 has neighbours E_8^3 / D_10 E_7^2, not
  D_10 E_7^2 / D_16 E_8. No consequence (150 is excluded by packing, computed on the data lattice).
- **Mass check: NOT done** (the orders of the automorphism groups are not computed in the lab). It is not needed for the argument
  above; it would be an independent check of the count 156 itself, which is cited.

## E. Provenance of the exclusions made before v10 (owner: LAB)

93 lattices were excluded before 01/10 by earlier versions of the engine, some by other methods (packing, criterion (E) with Sol's
theta theorems "to be reverified", whole-class LP certificates for 000). One line per method: what it rests on, and whether a
lattice depends on a method that is not reread. The user decided on 07/10 not to re-run the lab-local lattices now (board D6).

**Filled by LAB on 07/10** (lab tracker `finishC_tracker.json`, field "by"; recount of today in `lemma/FINAL_STATEMENT_DRAFT.md`
section 4 and board line D6). 143 lattices are excluded in the lab tracker; the 13 others are the deferral sweep.

| Method | Lattices | Rests on | Reread / recounted |
|---|---|---|---|
| Stream sweep: producer + consumer on all pairs | 91 | section C; the engine rules (section B) | coverage recounted today from the stored records (212,825,691 pairs, complete). Engines of the covering records: v1 (b48cf844) 570 records, v2-v4 (41fbcbff) 1,269, v5-v9 (267d2bb5) 44, v10 (1591aeea) 475; 55 lattices need lab-local records of 28-29/09 (26 without a recorded code version) |
| h-stage sweep on C1's pair lists, 28-29/09 | 13 (044, 072, 096, 097, 105, 106, 108, 116, 119, 120, 121, 127, 130) | C1's Gamma-reduced pair lists; the lab's frame_dfs of that date | lab-local; not recounted |
| frame_dfs with Lemma U+ on the Gamma-reduced pairs, 27/09 | 14 (087, 111, 122-126, 131, 135, 137-141) | the same | lab-local; 124, 126 also done by "structures" with an independent h-stage; not recounted |
| Three h-stage readings on C1's pairs | 2 (115, 132) | C1 h-check, "structures" frame LP with certificates, lab frame_dfs | "pending: independent pair enumeration" in the tracker |
| 000: 141 classes | 1 | 86 whole-class LP certificates (structures, verified twice per the tracker) + 55 classes searched EMPTY | set arithmetic recounted today; certificates and searches not re-run |
| Golay pair blocks | 2 (004, 010) | package v4 / v5 engines | recounted today (416,383 and 3,962 pairs) |
| Packing (C1 `envelope_pack.py`) | 10 (094, 128, 129, 133, 136, 144, 147, 148, 150, 154) | new-root packing bound | "run + argument re-read by C2" (27-28/09); not reread today |
| Criterion (E) of C1 notes/139, AND packing | 3 (117, 134, 142) | two methods each; (E) for 117 "depends on Sol's theta theorems" | packing reread as above |
| "Sol 0836" (D_8^3, D >= 12, E_8), AND packing | 5 (145, 146, 151, 152, 155) | two methods each | "re-read C1 notes/139" + packing |
| **"Sol 0836" D >= 12 only** | **1 (153, d_12^2)** | Sol's argument, reread by C1 (notes/139 s.3) | **rests on this single argument; never reread in the lab** |
| **Component-budget test only** | **1 (143, a_15 a_8)** | lab test at lattice level ("MILP + exact integer enumeration agree", 28/09) | **single method, single author (the lab), "reviewed_by" empty** |

**Lattices resting on one method that nobody outside its author reread: 153 and 143.** Both are large root systems where the
packing bound or a pair sweep would be cheap: the simplest repair is to run the v10 producer and engine on them (they are not in
the v10 job list), or to check whether the packing bound also applies. The 84 lab-local lattices (rows 1-3) are the other weak
point; the user decided on 07/10 not to re-run them now.

## F. External theorems the final statement will cite

| Theorem | Used for | Needed for C2 as stated? |
|---|---|---|
| Oddity formula (Conway-Sloane, SPLAG ch. 15) | A.4 | yes |
| Classification of quadratic forms over F_7; gluing of lattices | A.4, A.6 | yes (textbook) |
| Borcherds: 156 odd unimodular lattices of rank 24 with minimum >= 2 | A.7 | yes |
| Makhnev-Minakova 2004, Theorem 1 (an involution fixes exactly one vertex) | "no involution at all" | no, only for the corollary |
| g in {18, 20} (C1 notes 129, 132; "structures" S27 sections 5-8; Astra dossier 6) | nothing | **no: removed by A.4** |

## G. Who does what

| Section | Owner | State |
|---|---|---|
| A, F | LAP | done 07/10; to be refereed once by CDX (statement R and A.4 first) |
| B | CDX | open |
| C, D, E | LAB | filled 07/10; open points: C (1) independent enumeration never completed (a small check is being tried), E: lattices 153 and 143 rest on a single unreread method |
