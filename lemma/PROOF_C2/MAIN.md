# No automorphism of order 2 on a strongly regular graph (99, 14, 1, 2)

Main file of the single proof document `lemma/PROOF_C2/`. It states the theorem, gives the chain of the proof in order with the
file where each link is proved, and says what the proof rests on. Status on 2026-10-07: first assembly; the parts are in place,
the prose is to be polished, then the whole is frozen with a manifest and refereed once more as one text.

## Theorem

> **Let Gamma be a strongly regular graph with parameters (99, 14, 1, 2): 99 vertices, valency 14, two adjacent vertices have
> exactly one common neighbour, two non-adjacent vertices exactly two. Then Gamma has no automorphism of order 2.**

The existence of such a graph is Conway's 99-graph problem; it is not settled here. By earlier work the automorphism group of
such a graph has order 1, 2 or 3 (Makhnev-Minakova 2004, Behbahani-Lam 2011, Crnkovic-Maksimovic 2020, Cesarz-Woldar 2025); the
theorem removes 2.

## The chain

| Step | Statement | Where | Nature |
|---|---|---|---|
| 1 | An automorphism sigma of order 2 fixes exactly one vertex p, and exchanges the two ends of each of the seven edges of N(p) | `A1_REDUCTION.md`, A.0, A.1 | hand |
| 2 | On the sigma-odd functions A acts by a 49 x 49 integer matrix S with S^2 + S = 12 I; H = 3I - S is the Gram matrix of 49 vectors forming a tight frame of rank 22 | A.2, A.3 | hand |
| 3 | The lattice N they generate has a discriminant form over F_7 whose Witt class is the anisotropic plane, for every value of the rank of S - 3I mod 7 | A.4 | hand + oddity formula (cited) |
| 4 | N^* has no nonzero vector of norm < 8/7 | A.5 | hand |
| 5 | **Theorem R**: there is an odd unimodular lattice U of rank 24 without vector of norm 1 containing the frame and two orthogonal vectors y_1, y_2 of norm 7 orthogonal to it, with (R-i) to (R-vii) | A.6 | hand |
| 6 | U is one of 156 lattices | A.7 | cited (Borcherds) |
| 7 | Every vector v of U gives a sigma-odd integer (-4)-eigenfunction of A with sum of squares 2 E(v); the lemmas T16, T18, T20 forbid E = 8, 9, 10; Corollary Y1 | `A2_BRIDGE.md`, `A3_LEMMAS.md`; proofs in `lemma/T16_PROOF.md`, `T18_PROOF.md`, `T20_PROOF.md` | hand + computation (two programs per step) |
| 8 | For each of the 156 lattices, no pair (y_1, y_2) hosts a frame: lattice-level arguments for some, and for the others the complete enumeration of the pairs up to symmetry and, pair by pair, an immediate rule, a witness of step 7 with its certificate, or an exhaustive frame search | `B_LATTICES.md`, `B_TABLE_156.md` | computation, with the audits listed there |
| 9 | Steps 5, 6 and 8 contradict each other: sigma does not exist | - | - |

Steps 1 to 5 use nothing but the definition of the graph and two cited theorems. In particular the fixed-point theorem of
Makhnev-Minakova and the upstream hypothesis "g is 18 or 20" are not used.

## What the proof rests on

1. **Cited theorems.** The oddity formula for integral quadratic forms (Conway-Sloane, SPLAG ch. 15); Borcherds' classification
   of the odd unimodular lattices of rank 24 without vector of norm 1 (156 classes; SPLAG ch. 17); shadow theory for the count of
   vectors of norm 3 (Conway-Sloane 1990). The 156 Gram matrices used were recomputed: unimodular, odd, no norm 1, the root
   systems of the table, pairwise non-isometric (Part B).
2. **The three lemmas** T16, T18, T20: hand arguments and finite enumerations, each computed step with a second program
   (`lemma/ARTIFACTS_T18_T20.md`); refereed by AI sessions.
3. **The sweep of the lattices** (Part B): the enumeration of the pairs by the producer, compared with an independent enumerator
   on four lattices (140, 135, 141, and 064 whose roots do not span: equal lists); the engine, whose rules were audited one by
   one against Theorem R (`lemma/upstream/AUDIT_ENGINE_RULES.md`) with five conditions on the executable, each discharged (Part B
   says how); the records, the certificates of the deferred pairs, and the re-runs of 07/10 for everything whose program could
   not be identified.
4. **Who checked.** Three AI sessions (two Claude sessions and one Codex session), working separately and refereeing each other.
   No human reader has gone through the document; nothing is formalised yet. Every computation can be re-run from the repository:
   programs, commands, expected counts and certificate checkers are public there.

The precise list of reservations, with numbers, is kept without softening in `lemma/FINAL_STATEMENT_DRAFT.md` section 6 and in
Part B; it will be merged here when the text is frozen.

## Still open on the day of this assembly

- Lattice 044: its re-run through the archived engine is in progress (the other 27 lattices of the old pair-list methods are
  done); its line is added when its records are accepted. Its exclusion by the records of 29/09 stands meanwhile.
- T20: reserve G2 of the referee (wording of the verifier's contract).
- The final referee pass on the frozen merged text, and the manifest.
