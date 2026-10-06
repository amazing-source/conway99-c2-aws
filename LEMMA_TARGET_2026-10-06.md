# Where the remaining search time goes, and the lemma that would remove it (2026-10-06)

Written from the laptop session of 06/10 while the v10 fleet ran. Everything below is measured on v10 result files of this repo
(branches `run/q-*`) with the package's own `lattice_data()`. Scripts: laptop scratchpad `lemma_scan.py`, `root_rule_test.py`,
`root_cert_test.py` (not in the package).

## 1. Measurement

For a pair (y1, y2) and any v in U put

    Y(v) = (v,y1)^2 + (v,y2)^2,     E(v) = 7 N(v) - Y(v) = 7 x (norm of the projection of v on {y1,y2}^perp).

The v10 filter (min L* >= 9/7) kills a pair as soon as some v has E(v) = 8 (a norm-3 x with Y = 13).
Emin = the smallest positive E(v) over the vectors of U of norm 2, 3 and 4.

Pairs that survive every v10 filter and go to the stage-1 search (field `sample_search` of the result records):

| Lattice | Sampled searched pairs | Emin = 9 (pairs / search nodes) | Emin = 10 (pairs / nodes) | Emin = 11 (pairs / nodes) | Emin >= 12 |
|---|---|---|---|---|---|
| 016 | 20,178 (433 jobs) | 75.7 % / 91.6 % | 23.5 % / 8.3 % | 0.8 % / 0.1 % | none |
| 015 | 100 (2 jobs) | 89 % / 90.1 % | 9 % / 9.1 % | 2 % / 0.9 % | none |
| 014 | 100 (2 jobs) | 68 % / 82.2 % | 32 % / 17.8 % | none | none |
| 011 | 50 (1 job) | 72 % / 63.9 % | 28 % / 36.1 % | none | none |

- Emin = 9 is always realised by a **root r of U with {|(r,y1)|, |(r,y2)|} = {1, 2}** (Y = 5).
- Emin = 10 is realised by a root with {|(r,y1)|, |(r,y2)|} = {0, 2} (Y = 4); 180 of the 4,738 such pairs of 016 by a norm-4 vector with (3, 3).
- Emin = 11 is realised by a norm-3 x with {1, 3} (Y = 10).
- On 016 the v10 filter had already removed 440,625 pairs, and 258,580 were searched. Every searched pair ended EXCLUDED
  (stage 1 empty).
- Time anatomy of a searched pair (60 pairs of 016, laptop, 1 thread): 2.1 s per pair, 81 % in the DFS, 18 % in the setup
  (12 % compat matrix), 315,000 nodes and 5,660 candidate h per pair on average.

**Consequence.** A proof of min L* >= 10/7 would remove 64 to 92 % of the search time of these lattices; min L* >= 11/7 would
remove 99 to 100 %. A stream job that takes an hour today would then take what its cheap filters take.

## 2. The statement to prove, in graph terms

Dictionary. It was reconstructed in this session from the norms and the star structure used by the engine (7 vectors of norm 4,
42 of norm 3, rank 22, 12 words per h, 2 h per word); **check it against the project's own notes before building on it.**
The 49 frame vectors h, u are the vectors
f_O = sqrt(7/2) E_{-4}(e_x - e_{sigma x}) of the 49 orbits O = {x, sigma x} of the involution sigma (one fixed vertex, "inf").
Their Gram matrix is 3I - A^ with A^_{OO'} = A_{xy} - A_{x,sigma y} and A^_{OO} = -A_{x,sigma x}:

- norm 4 for the 7 orbits inside N(inf) (x ~ sigma x), norm 3 for the 42 others;
- all inner products of distinct frame vectors are in {0, +-1}; two h are orthogonal;
- each h meets 12 words and each word meets 2 h (mu = 2 with inf);
- Gram^2 = 7 Gram, i.e. sum f f^T = 7 on the 22-dimensional odd part of the (-4)-eigenspace.

For p in L*, c_O = (f_O, p) is an integer vector with Gram c = 7 c, and N(p) = |c|^2 / 7. Extending c to an odd function phi on the
99 vertices (phi(x) = c_O, phi(sigma x) = -c_O, phi(inf) = 0):

> **min L* >= m/7  <=>  every non-zero integer function phi with phi o sigma = -phi and A phi = -4 phi has sum_x phi(x)^2 >= 2m.**

The 04/10 lemma is the case 2m = 18 (no such phi of squared norm 16). The two targets are:

- **T18:** no sigma-odd integer (-4)-eigenfunction of squared norm 18;
- **T20:** none of squared norm 20.

For the campaign only the projections of roots are needed (Emin = 9 and 10 are realised by roots, except 180 pairs of 016), and
for a root r every |(u, r)| <= 1 because U has no norm-1 vector. So the 0/+-1-valued cases of T18 and T20 already remove the
pairs of section 1.

## 3. First reductions for T18 (0/+-1-valued phi, support S = S+ u S-, sigma S+ = S-, |S+| = 9)

For x in S+ write d+(x), d-(x) for its numbers of neighbours in S+ and S-; for z outside S, the same.

1. Eigen-equation: d-(x) = d+(x) + 4 on S+; d+(z) = d-(z) outside S. Conversely any S+ with no two vertices in one orbit and
   e(S+, sigma S+) - 2 e(S+) = 36 gives such a phi (equality in phi^T A phi >= -4 |phi|^2).
2. Active h: a_c = phi on the orbit c inside N(inf). Counting the words of each star (n_c >= 3 |a_c|, n_c = a_c mod 2, each word in
   two stars, n_c <= sum of the other n_d) leaves two patterns only:
   **(i) no active h and 9 words; (ii) two h at +-1 and 7 words.** No h at +-2.
3. e(S+) <= 2: apply A <= 14 E_0 + 3 (I - E_0) to the indicator of S, which gives 2 (4 e(S+) + 36) <= 90.
4. Counting common neighbours (lambda = 1, mu = 2) of the pairs inside S+ and of the cross pairs gives one relation:
   sum over z outside S of C(d(z), 2) = 18 - 7 e(S+) - sum_{x in S+} d+(x)^2.
   So e(S+) = 2 forces two disjoint edges and d(z) <= 1 for every outside z.
5. With e(S+) = 0 and no active h, the orbit graph B (i ~ j iff x_i ~ sigma x_j) is 4-regular on 9 vertices, any two vertices have
   at most 2 common neighbours, and every eigenvalue of B other than 4 lies in [-3, 3]. The Paley graph K3 x K3 passes all of this,
   so these counts alone do not finish: this is the analogue of the cube and Wagner complements of the 04/10 proof.

None of this is a proof of T18. It is the starting point.

## 4. What does not work

- **Rule R9a** (provable from section 3, item 2): delete the candidate h with |(h, r)| = 2 for a root r with E(r) = 9.
  Measured on 60 searched pairs of 016: 0 candidates removed, same nodes, same time. No candidate h meets such a root at +-2.
- **Local certificate around r**: the 9 frame vectors meeting r must have pairwise products in {0, +-1} and row sums 7 - N.
  Measured on searched pairs of 016:
  - only 16 to 50 words meet r, but 1,060 to 1,230 of the 5,800 candidate h do, so pattern (ii) stays wide open;
  - nine-word search (pattern (i)) with the exact row sums and a budget of 3,000,000 nodes, 10 pairs: no configuration in 9 pairs
    (3 searches complete, 6 stopped by the budget), 24 configurations in the tenth (not complete). About 100 s per pair in Python,
    against 2 s for the frame search itself.
  - So pattern (i) is often dead locally, pattern (ii) is not, and the test is slower than what it would replace. The obstruction
    is not local to r.
- Enforcing "exactly 0 or 2 of the 7 h meet r" inside the DFS would need a new point type in the numba kernels (coverage in
  {0, 2}); about 20 % of the candidates meet r, so the expected pruning is modest. Not tried.

So the gain needs T18 and T20 themselves, or the frame search as it is.

## 5. T18 reduced to three explicit graphs (06/10, evening)

Full report, scripts and outputs: `lemma/t18/` (start with `T18_REPORT.md`). The hand proofs below were re-read line by line in the
main session; the enumerations were run by two independent programs (`enum_S.py`, `verify_S.py`).

Notation of section 3; e = e(S+), k = number of active h = number of neighbours of inf in S+, Q = sum_{x in S+} d+(x)^2.

- **Counting identity (general form, |S+| = m):** sum over z outside S of C(d(z),2) = m^2 - 7m - 7e - Q, and
  sum over z outside S of d(z) = 10m - 4e.
- **Parity law (any m): e = C(k,2) mod 2.** sigma pairs the outside vertices other than inf and d(sigma z) = d(z), so the sum of
  C(d(z),2) over them is even; d(inf) = k; m^2 - 7m is even and Q = 2e = 0 mod 2.
- **e = 2 is impossible:** it forces Q = 4 and sum C(d,2) = 0, so d(z) <= 1 outside S, but sum d(z) = 82 over 81 vertices.
- **e = 1 is impossible** (word-word edge and word-h edge, both by lambda = 1 / mu = 2 counting on the sets
  M_j = {i != j : x_j ~ sigma x_i}; see A3 of the report).
- **Pattern (ii) is impossible:** k = 2 forces e odd, hence e = 1.
- **What is left:** S+ independent, no active h, and x_i ~ sigma x_j iff i ~ j in a 4-regular graph B on 9 vertices whose pairs
  of vertices have at most 2 common neighbours. There are exactly three such graphs:

  | | Edges of B | Automorphisms | Spectrum |
  |---|---|---|---|
  | B0 = K3 x K3 (Paley 9) | 01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78 | 72 | 4, 1^4, (-2)^4 |
  | B1 | 01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78 | 12 | 4, 2, 1^2, (-1)^2, (-2)^3 |
  | B2 = C9(1,2) | 01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78 | 18 | 4, (-2)^2, roots of t^3 - 3t - 1 twice |

- Proved about the three survivors: every outside vertex has d <= 3; d(a_c) <= 2; B1 admits no outside vertex with d = 3.
- **Not proved:** that the three graphs are impossible. For each of them a consistent assignment of neighbourhoods in S to all the
  other vertices exists, so the obstruction, if there is one, lies in the adjacency among the vertices outside S. This is the same
  point the 04/10 proof reached with the cube and Wagner complements; the argument that closed those two is the first thing to try
  on B0, B1 and B2 (the file `VERIF_CUBE_OBSTRUCTION_2026-10-04.md` is on the lab PC, not in this repo).

T20 has not been attacked. The parity law and the two counting identities apply to it as they stand (m = 10).
