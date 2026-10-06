# Referee report on T18: the hand part (reductions, models, determined sets)

Agent report of 2026-10-07 (night), saved by the main session. The referee was asked to find errors, re-deriving every hand statement
from the definitions before reading the given proof. Scripts and outputs: this folder (`ref1` ... `ref10`, totals in `ref9_totals.out`),
written from the referee's own model; they import no repo code and read only the `r2_tau_<s>.json` files, for comparison.

## 1. Problems found, most serious first

**No error found that invalidates the proof.** Every load-bearing hand statement came out correct when re-derived from the
definitions. What was found: gaps in the written text, one wrong sentence, and a few unverified side statements.

1. **Gap at the first step (statement level).** The lemma is stated for integer-valued phi, but the T18 documents only treat
   0/+-1-valued phi. The reduction "integer => 0/+-1 with nine +1" is written nowhere for norm 18 (it exists for norm 20,
   `T20_REPORT` A1). It is true, with a four-line proof (section 3). The campaign only uses the 0/+-1 case, so nothing downstream
   changes, but the proof text must contain it if T18 is quoted in integer form.
2. **A9 as written is not a pure hand proof.** It cites "a_3(p) = 0 by A6", and A6's d(a_c) <= 2 came from `rows.py` (computed PSD).
   The repair exists: Theorem N3 uses only A5 and its own Lemmas 1-2, so there is no circularity. The final text must put N3 before
   A8-A9, or use the `VERIF331` variant 2 h_3 + 4 h_0 + n_3 <= 4.
3. **Wrong sentence in A11.** "The violated matrix is 9(3I - A) + J" is false in general. With that matrix alone there are 672 (B1)
   and 887 (B0) survivors on 39 vertices instead of 481 and 383. Ten B1 graphs on 51 vertices pass every budget and 9(3I - A) + J, and
   die only by 11(4I + A) - 2J. The proof text must define both matrices.
4. **A3 omits a case and two justifications**, all trivial: the plus edge between the two active inner vertices is not mentioned
   (impossible: N(p) induces a perfect matching and the mate of a_c is in S-); "M_7 inside {1..6}" needs x_7 = a_c not adjacent to
   y_8 = b_d (same reason); the label 8 silently uses k = 2.
5. **Stage-1 tests are defined by reference to a document that is not in the repo** ("Wagner note section 3"). The only definition is
   the header of `r2_stage1.py`. Re-derived: (i), (i'), (iii) are valid necessary conditions, and (P) removes nothing.
6. **Some counters do not count what the text says** (all harmless: the omitted conditions are valid and the extra objects die later):
   "(tau, F) passing the N(p) tests ... the 3 pairs of N(p) n X_1 exist" gives 2406 / 7224 / 3510, which are the budget-only counts (a
   real existence test for the W types leaves 1265 / 4096 / 1834); "type solutions 11235" (B2) are counted without the cell-room
   condition (770 with it); stage D "846" for #975 includes the cap a_2(z) <= 4 + t, which A18 does not list (849 without it).
7. **A10 does not state a consequence the 45- and 51-vertex sets need**: the six other X_0 vertices have no neighbour in
   W u {z_0, sigma z_0}. It follows from "exactly 2 in A_p" (their two common neighbours with p are used up).
8. **Stale statements.** Round 3 of `T18_REPORT` presents the four 47-vertex configurations as an open case (P2 kills them);
   `LEMMA_TARGET` section 8 still says B0 is open and B1 stage C has one implementation (see `lemma/t18_B0_VERIFC`); A6 "B0: 6 classes
   of d = 3 types remain, B2: 9" is superseded by N3.
9. **Not verified, not load-bearing.** P6, P7, P8 of `t18_STRUCT` have no written proof; A7 is conditional on H16; the dictionary of
   `LEMMA_TARGET` section 2 (lattice <=> eigenfunction) is outside the graph lemma. No enumeration prunes with P6-P8 or A7.

## 2. Statement-by-statement verdicts

| Statement | Verdict |
|---|---|
| Eigenvalues, multiplicities; 27I - 9A + J = 63 E_{-4}; 44I + 11A - 2J = 77 E_3; both PSD | CORRECT |
| First step: integer phi => 0/+-1, nine at +1 | CORRECT, NOT WRITTEN for T18 (filled in section 3) |
| A0: x ~ sigma x iff x in N(p); N(p) = 7 mate edges, a perfect matching; nobody but p sees both a_c and b_c; iota is a fixed-point-free involution on the 42 outer orbits | CORRECT |
| Section 3 items 1-5 (eigen-equation; k in {0,2}; e <= 2; counting identities; B) | CORRECT |
| A1 parity law | CORRECT |
| A2 (e = 2) | CORRECT |
| A3 (e = 1) | CORRECT, GAP (problem 4) |
| A4 (pattern (ii)) | CORRECT |
| A5: B is 4-regular on 9 vertices, codegrees <= 2, exactly B0, B1, B2 | CORRECT. "4-regular" and "codegree <= 2" by hand; the list by computation (`enum_S.py`, `verify_S.py`, and the referee's own `ref1`) |
| A6 hand bullets (18 - 5d, n_k, w_ij, z_i) | CORRECT; `rows.py` bullets superseded by N3 |
| A7 | NOT VERIFIED (conditional, unused) |
| N3: Lemma 1, Lemma 2, Theorem, by-product | CORRECT; n_3 = 0 is not used before it is proved in the logical order |
| A8 identities, (*), t <= 9 | CORRECT |
| A9 (4 h_0 + n_3 <= 4; profile (4,1,2) dead) | CORRECT, GAP (problem 2) |
| Profile split {(2,5,0), (3,3,1), (4,1,2)} | CORRECT, exhaustive once n_3 = 0 |
| A10 forced structure; 39, 45, 51 determined | CORRECT, GAP (problem 7) |
| A14 a-h; 37 and 47 determined; intermediate 27/29/33-vertex sets | CORRECT |
| B2 report C-a to C-d, legitimacy of budgets on spanning subgraphs | CORRECT |
| A18 (forced numbers of stage D; 48, 49, 55 determined; kernel remark) | CORRECT |
| P1, P2 (rank bound), P3, P4, P5 | CORRECT |
| P6, P7, P8 | NOT VERIFIED (unused) |
| A19b / A21 use of the rank bound | CORRECT |
| B0 reduction modulo the stabiliser of tau | CORRECT in principle; the referee's full run does not use it and agrees |
| A11 sentence on the violated matrix | WRONG (problem 3) |

Specific points:
- **Disconnected graphs.** None exist: a component needs at least 5 vertices. All 1,024,380 labelled 4-regular graphs on 9 vertices
  fall into 16 classes, all connected.
- **What selects 3 of 16.** Only "all codegrees <= 2". The other 13 classes each have a pair with codegree 3 or 4. The three
  survivors have all codegrees in {1,2}, so the 18 deficient pairs are distinct, which the matching model needs.
- **Undetermined adjacency set to non-edge.** Every class pair of the 37-, 39-, 45-, 47-, 49-, 51- and 55-vertex sets was checked.
  Each adjacency is either a listed parameter or forced by one of four facts: N(p) is a perfect matching; v ~ sigma v iff v in N(p);
  the two common neighbours of a vertex with p are used up; an equality case of A9.

## 3. The referee's own proofs

- **First step.** At x with phi(x) = c > 0, -4c = sum_{y ~ x} phi(y). The mate contributes -c if x in N(p), else 0. Any other orbit
  contributes at least -|c_O'|, since being adjacent to both of its vertices gives 0. So sum_{O' != O} |c_O'| >= 3c. The multisets of
  squares summing to 9 are {9}, {4,4,1}, {4,1^5}, {1^9}; the first three give 0 >= 9, 3 >= 6, 5 >= 6.
- **A0.** N(x) n N(sigma x) is sigma-invariant. If it has size 1 it is {p}. If it has size 2 and contains p, the other element is a
  second fixed point. So x ~ sigma x iff x ~ p. For x outside N[p] it is an orbit {z, sigma z}; z in N(p) would put x in
  N(z) n N(sigma z) = {p}.
- **k and e.** At a_c, the sum over its 12 outer neighbours is -3 phi(a_c). So n_c = phi(a_c) mod 2, n_c >= 3 |phi(a_c)|,
  sum n_c = 2(9 - k), giving k in {0,2}. A <= 14 E_0 + 3 (I - E_0) on 1_S gives 2(4e + 36) <= 90.
- **Counting.** Pairs of S+ have 2 C(m,2) - e common neighbours. S+ and S- supply sum (d+^2 + 3 d+ + 6) = Q + 6e + 6m. Hence
  sum_out C(d,2) = m^2 - 7m - 7e - Q, and sum_out d = 10m - 4e.
- **Parity.** sigma pairs the outside vertices other than p with equal d, and d(p) = k, so e = C(k,2) mod 2.
- **e = 2.** Q = 4 forces d <= 1 on 81 vertices carrying 82; Q = 6 makes the sum negative.
- **e = 1, word-word.** If 1 not in M_0, two 5-subsets of {2..8} share >= 3 common neighbours of an edge. Otherwise P, Q are 4-sets
  meeting in {k} and covering {2..8}; each j != k has 0 in M_j, 1 not in M_j, and the two budgets force k not in M_j, so |M_k| <= 2 < 3.
- **e = 1, word-h.** M_0 in {1..6,8} has size 5 and M_7 in {1..6} has size 4; they share >= 2 common neighbours of an edge.
- **e = 1, h-h.** N(p) is a matching.
- **Pattern (ii), e = 0.** 18 - C(2,2) = 17 is odd.
- **B.** d- = 4 and x_i not adjacent to y_i give 4-regular. Non-adjacent x_i, x_j have |B(i) n B(j)| <= 2 common neighbours in S-.
- **Lemma 1 / N3.** Paths z-w-s with s in S+ number 18 - d and also 4d + sum_out d(w). A vertex z with d = 3 has >= 5 neighbours in
  X_0, so does sigma z != z, and |X_0| <= 7, giving >= 3 common neighbours.
- **A8.** Equivalent to psi = (3I - A + J/9) 1_S = 1_S + 2 * 1_{X_0} - 2 * 1_{X_2} being a (-4)-eigenvector; checked class by class.
  sum a_2^2 over outside vertices is 576 - 2t, because each vertex of S has exactly 4 neighbours in X_2.
- **A9.** sum_{w ~ p} a_2(w) = 36 - 2 h_2. Lower bounds are 1, 2, 6 on X_2, X_1, X_0 neighbours (mate; p; p and mate). This gives
  28 + 8 h_0 <= 36, with equality for h_0 = 1.
- **Rank.** tr sigma = 1, tr sigma A = 14, tr sigma J = 99, so tr(sigma E_{-4}) = (27 - 126 + 99)/63 = 0 and
  tr(sigma E_3) = (44 + 154 - 198)/77 = 0. The odd orbit Gram 3I - A[R,R] + A[R, sigma R] is (1/18) D M D^T, of rank <= 22.
- **C-b.** Two W vertices of the same type would be non-adjacent with three common neighbours p, x_i, y_j.
- **C-c.** w adjacent to both s and sigma s would be a common neighbour of them, but those are an iota orbit outside N[p].

## 4. Numerical checks (the referee's own model)

The PSD rejections here use floating-point eigenvalues (threshold -1e-7), so these are model and count checks, not a further exact
proof. Ranks and determinants of the four survivors are exact (flint).

- **Real graphs.** On Paley(9) and the 243-vertex srg(243,22,1,2) with x -> -x: A0, the iota involution, trace(sigma | V) = 0 and
  the rank splits 55+55 / 66+66, the idempotent formulas, and the general counting, parity and path identities all hold.
- **Stage 1.** The stored representative lists equal the referee's, orbit for orbit.

| | B0 | B1 | B2 |
|---|---|---|---|
| Rectangles / usable in N(p) | 99 / 63 | 99 / 63 | 99 / 63 |
| Matchings / orbits | 25514 / 425 | 13799 / 1259 | 9229 / 528 |

- **Profile (2,5,0).** All figures equal the repo's.

| | B0 | B1 | B2 |
|---|---|---|---|
| (tau, F) passing budgets / budgets + PSD | 5545 / 4904 | 12366 / 11509 | 4347 / 3863 |
| Stage-B triples | 5595 | 4977 | 196 |
| Stage C on all triples, survivors | 0 | 4 | 0 |

  The four B1 survivors are #813 F = [2,9], [3,6] and #975 F = [1,2], [3,6]. The B0 run does not use the stabiliser reduction.
  B2 type solutions on 33 vertices: 11235 / 4227 without cell room, as in the repo.
- **The four B1 survivors.** Both matrices are exactly PSD; rank 46 of 47; odd rank 23 with determinant 47684 (#813) and 874944
  (#975); even rank 23 of 24. Both exceed the bound 22. Stage D gives 678 and 849 candidate mate pairs (846 with the cap of problem
  6), none PSD.
- **Profile (3,3,1).** All figures equal the repo's.

| | B0 | B1 | B2 |
|---|---|---|---|
| Survivors on 39 vertices | 383 | 481 | 7 |
| Tables passing budgets on 45 | 8639 | 27203 | 0 |
| Tables passing budgets + PSD on 45 | 23 | 164 | 0 |
| Budget-valid graphs on 51 | 52 | 1839 | - |
| PSD on 51 | 0 | 0 | - |

## 5. Not verified by the referee

- The repo's programs themselves and their exact certificates (only that they agree with the referee's model at every checkpoint).
- The dictionary of `LEMMA_TARGET` section 2, the 04/10 lemma H16, A7, P6-P8, and anything about T20.
