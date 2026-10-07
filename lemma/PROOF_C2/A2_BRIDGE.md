# Part A2. Short vectors of the envelope: the energy, the three lemmas as rules, and Corollary Y1

Part of the single proof document `lemma/PROOF_C2/`. Notation and numbering of `A1_REDUCTION.md`: Theorem R, (R-i) to (R-vii).
The detailed, refereed version of this part is `lemma/BRIDGE.md` (referee: `lemma/bridge_REFEREE/REPORT.md`); nothing here goes
beyond it. Status of this file on 2026-10-07: assembled; to be polished with the rest.

## 1. The energy of a vector

Let (U; y_1, y_2; h_c, u_o) be as in Theorem R. For v in U put

    N(v) = (v,v),    Y(v) = (v,y_1)^2 + (v,y_2)^2,    E(v) = 7 N(v) - Y(v).

By (R-v), E(v) = sum_c (v,h_c)^2 + sum_o (v,u_o)^2: E(v) is 7 times the squared norm of the projection of v on the 22-space of
the frame. It is a non-negative integer, it does not change when a multiple of y_1 or y_2 is added to v, and E(v) = 0 exactly
when v is in Z y_1 + Z y_2 ((R-vi)).

By (R-vii), the 49 integers (v,h_c), (v,u_o) are the values of a sigma-odd integer function phi_v on the 99 vertices with
A phi_v = -4 phi_v and sum phi_v^2 = 2 E(v). So:

> **A statement "there is no sigma-odd integer (-4)-eigenfunction with sum of squares 2E" forbids every vector of energy E in every
> envelope.**

Four such statements are available.

| E | sum of squares | statement | where |
|---|---|---|---|
| 1 to 7 | 2 to 14 | no such function | Theorem R, A.5 (hand proof): this is (R-vi), E(v) >= 8 |
| 8 | 16 | no such function | **T16**, `lemma/T16_PROOF.md` |
| 9 | 18 | no such function | **T18**, `lemma/T18_PROOF.md` |
| 10 | 20 | no such function | **T20**, `lemma/T20_PROOF.md` |

Hence, given T16, T18, T20: **E(v) >= 11 for every v of U outside Z y_1 + Z y_2.**

## 2. Which vectors have energy 8, 9, 10: the witness rules

Adding multiples of y_1, y_2 changes (v,y_a) by multiples of 7 and keeps E. So every class has a representative with
|(v,y_1)| <= 3 and |(v,y_2)| <= 3, and for it N = (E + a^2 + b^2) / 7 with a = (v,y_1), b = (v,y_2), a^2 + b^2 <= 18; N is an
integer >= 2 (U has no vector of norm 1). Going through N = 2, 3, 4:

| E | N = 2 (a root) | N = 3 | N = 4 |
|---|---|---|---|
| 8 | a^2 + b^2 = 6: impossible | a^2 + b^2 = 13: {&#124;a&#124;, &#124;b&#124;} = {2, 3} | 20 > 18: impossible |
| 9 | a^2 + b^2 = 5: {&#124;a&#124;, &#124;b&#124;} = {1, 2} | 12: impossible | 19: impossible |
| 10 | a^2 + b^2 = 4: {&#124;a&#124;, &#124;b&#124;} = {0, 2} | 11: impossible | 18: &#124;a&#124; = &#124;b&#124; = 3 |

So the vectors of energy 8, 9, 10 are detected, completely, by four finite tests on the lists of vectors of norm 2, 3, 4 of U:

- **(W8)** a vector of norm 3 with Y = 13;
- **(W9)** a root with Y = 5;
- **(W10)** a root with Y = 4, or a vector of norm 4 with |(x,y_1)| = |(x,y_2)| = 3.

A pair (y_1, y_2) with a witness (W8), (W9) or (W10) hosts no frame, by T16, T18, T20 respectively. A pair without any witness has
E >= 11 everywhere (dual minimum of the lattice orthogonal to y_1, y_2 at least 11/7): the lemmas say nothing about it, and only
the frame search of Part B decides it. (The same table one line further: E = 11 occurs exactly on vectors of norm 3 with
{|a|, |b|} = {1, 3}.)

The three shells are complete lists: their sizes are fixed by the theta series (N_3 = 4096 by shadow theory, N_4 = 98256 - 24 N_2:
`lemma/upstream/theta_odd24.py`), checked on the 156 lattices (`measures/SHELL_COUNTS_2026-10-07.json`).

## 3. Corollary Y1: a root with product 2 kills the normal, whatever the other one

> **Corollary Y1.** Given T18 and T20: in an envelope, every root r satisfies |(r,y_1)| <= 1 and |(r,y_2)| <= 1.

*Proof.* a = (r,y_1), b = (r,y_2) are integers and E(r) = 14 - a^2 - b^2 >= 8 by (R-vi), so a^2 + b^2 <= 6. If |a| = 2 then
b^2 <= 2 and E(r) = 10 - b^2 is 9 or 10: forbidden by T18, resp. T20. Same with a and b exchanged. QED

Read at the level of one normal: **if U has a root r with (r,y_1) = +-2, no frame of U has this y_1, whatever y_2 is.** No y_2 is
enumerated, no swap rule and no search is used. The statement is invariant under Aut(U) and under the sign of y_1, so it applies
to an orbit representative. Certificate: `q/cert_y1.py` (y_1 in ambient coordinates, in U, of norm 7; r in U of norm 2; the
product), checked by the standalone `q/check_cert_y1.py`; a second certificate and checker by another author in
`lemma/t20_CODEX/` (FIXED_Y1_003.md).

Where it is used in Part B: for the y_1 representative 181 of lattice 003, which has no record (its y_2 enumeration never ended);
and as an independent second argument for most y_1 representatives of the lattices re-run on 07/10 (9,143 of 10,802 on the
stream group, 4,073 of 4,334 on the 28 lattices of the old pair-list methods, six of which have no admissible y_1 left at all).

## 4. How Part B uses the rules

- In the sweeps of the 13 last lattices, a pair with a witness (W9) or (W10) that the engine's immediate filters did not already
  exclude is set aside ("deferred") instead of searched. Each deferred pair has a certificate recomputed from the regenerated
  stream: y_1, y_2 in U of norm 7 and orthogonal, the witness vector in U with its norm and its two products
  (`q/cert_stream.py` for the 7,762 stream records; the Golay blocks of 001 and 002 have their own check; in all 5,190,752
  pairs rest on T18 and 2,508,295 on T20).
- (W8) is a filter of the engine itself (version 10: FD_MIN97), together with the characteristic trap (A.8) and the others
  audited in `lemma/upstream/AUDIT_ENGINE_RULES.md`.
- A deferred pair is counted as excluded only by the conversion step, which requires the certificate and the acceptance of T18
  and T20 (`measures/lemmas_accepted_2026-10-07.json`).
