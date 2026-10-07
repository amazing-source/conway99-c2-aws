# Part A3. The three eigenfunction lemmas T16, T18, T20: statements and what each rests on

Part of the single proof document `lemma/PROOF_C2/`. The three proofs are separate files and stay so; this part states them in
one form and says, for each, what is proved by hand, what is computed, by how many programs, and who refereed it.
Status of this file on 2026-10-07: assembled; to be polished with the rest.

## 1. The common statement

Gamma is a strongly regular graph with parameters (99, 14, 1, 2), A its adjacency matrix, sigma an automorphism of order 2. By
A.0 of Part A1, sigma fixes exactly one vertex p.

> **T(2E).** There is no function phi on the 99 vertices with integer values such that
> phi(sigma x) = -phi(x) for every x,   A phi = -4 phi,   and   sum_x phi(x)^2 = 2E.

| Name | E | sum of squares | Proof text | Size of the support |
|---|---|---|---|---|
| (in Theorem R, A.5) | 1 to 7 | 2 to 14 | `A1_REDUCTION.md`, A.5 | at most 7 + 7 |
| **T16** | 8 | 16 | `lemma/T16_PROOF.md` | 8 + 8 |
| **T18** | 9 | 18 | `lemma/T18_PROOF.md` | 9 + 9 |
| **T20** | 10 | 20 | `lemma/T20_PROOF.md` | 10 + 10 |

The four proofs have the same skeleton. (i) The values of phi are 0, +1, -1 (larger values are excluded by hand from the row
equations). (ii) With S+ = {phi = 1}, S- = sigma S+, the equation gives, for every vertex of S+, (neighbours in S-) =
(neighbours in S+) + 4, and a count of common neighbours bounds the edges inside S+. (iii) The bipartite graph between S+ and S-
is one of finitely many "support structures", which are enumerated. (iv) Each structure is excluded, by hand where possible,
otherwise by an exhaustive search over the vertices outside the support in which every rejection is exact: a count of common
neighbours (lambda = 1, mu = 2), or an integer vector on which one of the two matrices 9(3I - A) + J and 11(4I + A) - 2J, which
are positive semidefinite on the whole graph, takes a negative value.

For E <= 7 step (ii) alone gives a contradiction (A.5). The work grows quickly with E.

## 2. T16

- **Hand part.** Values 0, +-1; S+ is independent with 8 vertices; the number k of support vertices adjacent to p is 0 or 2, and
  k = 2 is excluded; for k = 0 the complement of the bipartite graph is a triangle-free cubic graph on 8 vertices, i.e. the cube
  or the Wagner graph.
- **Computed part.** For the two graphs, two "profiles" of the neighbourhood of p; the configurations are enumerated and each is
  refuted by an explicit obstruction (240 obstructions for one profile, 32 witnesses for the other).
- **Checks.** The dossier of 04/10, the lab's own check, an independent enumeration (`lemma/t16/`). Referee report
  `lemma/t20_CODEX/REFEREE_T16_PROOF.md`: no blocking mathematical error; one defect in the dossier's verifier (a test W <= set(V)
  was missing in `check_B`); with the test added every witness and obstruction passes again.
- **Where it is used.** Rule (W8) of Part A2, i.e. the engine's filter "dual minimum 9/7" (FD_MIN97) in version 10.

## 3. T18

- **Text.** `lemma/T18_PROOF.md`, version 2 (version 1 and the change log are in `lemma/t18_PROOF/`).
- **Hand part.** Values 0, +-1; the support structures; the classes of outside vertices by their number of neighbours in S+;
  a five-line theorem removing the vertices with three neighbours; the profiles of the neighbourhood of p.
- **Computed part.** The remaining profiles, by exhaustive searches with exact rejections; one family is closed by the rank bound
  (the sigma-odd part of 9(3I - A) + J has rank at most 22).
- **Checks.** Two independent referees (`lemma/t18_REFEREE/`, `lemma/t18_REFEREE2/`), no error; every computation re-done by at
  least three programs, one of them written from the text alone.
- **Where it is used.** Rule (W9) of Part A2, Corollary Y1, and the conversion of 5,190,752 deferred pairs.

## 4. T20

- **Text.** `lemma/T20_PROOF.md` (Theorem 10.2), with the specification `lemma/t20_R3_I/SPEC_ROUTE_B_N3.txt` for its last case.
- **Hand part.** Values 0, +-1; k (support vertices adjacent to p, counted in orbits) is 0, 2 or 4; nine support configurations
  (III.0, III.1 for k = 4; IIa.0 for k = 2; I.0 to I.5 for k = 0); for k = 0: the number n_3 of outside vertices with three
  neighbours in S+ is 0 or 2, and the neighbourhood of p has one of two profiles.
- **Computed part.** III.0, III.1, IIa.0; case I with n_3 = 0 (twelve cases: 615,405 bases, 15.8 million nodes, no complete
  configuration); case I with n_3 = 2 (fifty cases: 64,528 bases, 86,968 nodes, no node with four added orbits).
- **Checks.** Every computed step has a second program; for III.1 the second verification shares the model file and part of the
  enumeration skeleton with the first; in the searches the second program re-traverses the tree of the first with the same
  choice of branching unit and its own tests. Referee reports `lemma/t20_CODEX/REFEREE_T20_PROOF.md` (two passes and an addendum
  on the last case): no blocking error. Open: reserve G2 (the exact wording of what the verifier guarantees). Where every run
  lives: `lemma/ARTIFACTS_T18_T20.md`.
- **Where it is used.** Rule (W10) of Part A2, Corollary Y1, and the conversion of 2,508,295 deferred pairs.

## 5. What the three lemmas do not give

They forbid E = 8, 9, 10. A pair (y_1, y_2) all of whose vectors have E >= 11 passes all of them; such pairs exist in the swept
lattices in large numbers (for instance 2,652 pairs among the 28 small lattices of section B.6, and thousands in lattice 003),
and they are excluded only by the frame search of Part B. A lemma T22 would move that boundary by one step; none is claimed.

All three lemmas were proved and checked by AI sessions (two Claude sessions and one Codex session, the latter also as referee);
no human reader has gone through them and nothing is formalised. Part of the formalisation plan is to state them as named
hypotheses of the final theorem first.
