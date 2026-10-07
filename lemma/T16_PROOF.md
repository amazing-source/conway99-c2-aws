# T16: no sigma-odd integer (-4)-eigenfunction of squared norm 16 (dual minimum > 8/7)

Index written by the lab session on 2026-10-07 for ONE referee pass (board, hole H5 of `lemma/upstream/AUDIT_ENGINE_RULES.md`).
**The proof text is the dossier of 04/10/2026, in French, kept as received in `lemma/t16/dossier_2026-10-04/`.** It was written by
ChatGPT for the user; it is not rewritten here. This page says what is claimed, where each step is, what is computed, and who
checked what.

## Statement

Gamma = srg(99,14,1,2), sigma an automorphism of order 2 with exactly one fixed vertex p. There is no sigma-odd integer function
phi on the vertices with A phi = -4 phi and sum phi^2 = 16. Equivalently, with Theorem R of `lemma/upstream/AUDIT_REDUCTION.md`:
E(v) = 7 (v,v) - (v,y_1)^2 - (v,y_2)^2 is never 8, so E(v) >= 9 for v outside Z y_1 + Z y_2 (dual minimum of the frame lattice >= 9/7).

## What rests on it

- The engine rule FD_MIN97 of package v10: "norm-3 x with (x,y_1)^2 + (x,y_2)^2 = 13" (E = 21 - 13 = 8), verdict
  "EXCLUDED (dual min 9/7: norm-3 x with Y=13)".
- The quick deferral path uses the engine's own min97_witness test before deferring.
- T18 and T20 do not use it (they exclude the squared norms 18 and 20 directly); the dual-norm rule of `t20_HAND/NOTES.md` H6 needs
  only 8/7.

## Structure of the proof, and where each step is

| Step | Content | Where | Kind |
|---|---|---|---|
| 0 | E(v) >= 8 (no function of squared norm <= 14) | `lemma/upstream/AUDIT_REDUCTION.md` A.5 (redone by the laptop session on 07/10) | hand |
| 1 | Equality E = 8: phi has values 0, +1, -1, eight +1 (the set P) and eight -1 (Q = sigma P) | `LEMME_EGALITE_8_SUR_7_C2.txt` section 2 | hand |
| 2 | The number k of active inner orbits is 0 or 2; P and Q are independent | same, sections 3, 4 | hand |
| 3 | k = 2 is impossible (the matrix B "with two diagonals" does not exist) | same, section 5 | hand |
| 4 | k = 0: B = A[P, Q] is the complement of a cubic graph; two types remain: the complement of the cube Q_3 and the complement of the Wagner graph | `C2_PROLONGEMENT_SUPPORT16_PREUVE_CUBE.txt` sections 7, 8 | hand |
| 5 | Cube complement: impossible, by a double count (at least 10 incidences, at most 8) | same, sections 2-6 | hand |
| 6 | Wagner complement: impossible. Global constraints and the eight "rectangles"; profile B dies by hand (three demands, two partners); profile A by an exhaustive exact enumeration with certificates | `C2_WAGNER_BORNE_9_SUR_7.txt` sections 2-6; programs `ENUMERER_WAGNER_PROFIL_A.py`, `ENUMERER_WAGNER_PROFIL_B.py` (Python standard library), certificates `WAGNER_PROFIL_*_CERTIFICATS.json`, verifier `VERIFIER_WAGNER_CERTIFICATS.py` | hand + computed |
| 7 | Corollary: the equality case 8/7 is impossible | same, section 8 | - |

## Who checked what (not a referee pass)

- Lab session, 04/10 (`lemma/t16/lab_check/VERIF_CUBE_OBSTRUCTION_2026-10-04.md`): steps 4 (the reduction to the two types as used
  there), 5 (every step of the cube double count re-derived by hand), the structural part of step 6, and the derivation of the pair
  criterion Y = 13 with measurements. The active-h lemma (steps 1-3) was re-read the same day.
- An independent agent of the lab session, 04/10 (`lemma/t16/independent_check/`): the two Wagner enumerations redone by another
  program (`crosscheck_stage2.py`, outputs `out_A.txt`, `out_B.txt`, `crosscheck_A.txt`, `crosscheck_B.txt`).
- The laptop session, 07/10: steps 0-2 redone by hand as far as "e = 0, P independent, every vertex of P has 4 neighbours in Q, the
  outside vertices contribute exactly 8 common-neighbour pairs".

## For the referee

Errors only, with file and section references. Points that deserve the closest look: (a) step 4, that the cube and the Wagner graph
are the only cubic graphs left, with the exact hypotheses under which the others are discarded; (b) step 3; (c) step 6: that the
two enumerations are exhaustive for what the text says they cover (section 3 of the Wagner text, "couverture de la réduction"), and
that every rejection in the certificates is an exact integer statement.
