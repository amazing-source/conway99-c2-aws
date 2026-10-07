# Route (C): the final statement and what it rests on — DRAFT of 2026-10-07, 12:50 UTC

Lab session (Claude). Board line D5 of `lemma/T20_BOARD.md` (compute repo). This is a recheck by an AI session, not a human
referee and not a formal proof.

> **Not yet true on the day of writing.** Four things are still missing; nothing below may be quoted as a result before they are
> in (section 5): the end of the n_3 = 2 computation of T20 and its second program, the referee pass on `T20_PROOF.md`, the
> certificate run of the deferred pairs, and one stream job (003:181:182).

## 1. Statements

**Statement A (route C).** No strongly regular graph with parameters (99, 14, 1, 2) has an automorphism of order 2 with exactly
one fixed vertex. In the terms of `MODEL.md` section 6: EX is false.

**Statement B.** With F0 ("every involution of a srg(99,14,1,2) fixes exactly one vertex"), no such graph has an involution.

Scope: A and B say nothing about a graph without involution.

Direction used: a real graph with such an involution gives the frame data (direct direction of `MODEL.md` section 5 and Part I
of the proof skeleton). T4 and the reconstruction direction are not used for statement A.

## 2. The chain

| Step | Content | Where | Status on 07/10 |
|---|---|---|---|
| R1 | Graph with a one-fixed-point involution => signed orbit matrix, 49 frame vectors (7 of norm 4, 42 of norm 3) of rank 22 with Gram 3I - S, tight with constant 7 | `lemma/upstream/PROOF_SKELETON_C2.md` Part I; re-proved from the definitions in `lemma/BRIDGE.md` section 4 | BRIDGE: written and refereed by the laptop session's agents. By me: the Gram and the dual-lattice dictionary re-derived for the Y = 13 check of 04/10. Rest: SOURCE-ONLY |
| R2 | The frame lies in an odd unimodular lattice U of rank 24 without vector of norm 1, orthogonal to two orthogonal vectors y1, y2 of norm 7 | upstream notes, not in this workspace | SOURCE-ONLY. This is the one external assumption of the whole campaign |
| R3 | There are 156 such lattices | Borcherds' table; lattice data `external_runs/structures_3eceb4d/U/*.json` | OK-RECOMPUTED 04/10 (determinant, parity, minimum, root systems; one erratum on neighbours, no consequence) |
| R4 | For each lattice, the pairs (y1, y2) up to Aut(U) x signs, swap and twin rules | C1 producers `y_pairs.py`, `y_pairs_gamma.py`, Golay generators, O24 classes | SOURCE-ONLY. Twin rule: checked conservative (04/10). Completeness of the enumeration: NOT re-derived (audit item L4) |
| R5 | Each pair is excluded by one of: characteristic-vector trap; pair set-up; dual minimum 9/7 (norm-3 x with Y = 13); exact search (stage 1, stage 2); swap coverage; twin transfer / deferral; lemmas T18 / T20 through a witness root | engine `frame_dfs_next.py` (v10 sha 1591aeea) and earlier versions; `q/defer_consumer.py` | Y = 13 rule: OK-REREAD + independent agent (04/10). Search engine: calibrations between versions; code not re-read line by line (audit item L2). Deferral rule: second computation = certificates (R8) |
| R6 | T18: no sigma-odd integer (-4)-eigenfunction of squared norm 18 | `lemma/T18_PROOF.md` | proved and refereed twice per the laptop session; every computation by at least three programs. Not re-read by me |
| R7 | T20: the same for squared norm 20 | `lemma/T20_PROOF.md` | see section 3 |
| R8 | Bridge: a root r of U with (r,y1)^2 + (r,y2)^2 = 5, resp. 4, gives an eigenfunction of squared norm 18, resp. 20; needs y1, y2 in U of norm 7 and orthogonal | `lemma/BRIDGE.md`; certificates `q/cert_stream.py`, `cert_golay.py` | bridge refereed (laptop); same computation as my Y = 13 check. Certificates: Golay 001 / 002 done (17,983 pairs, 0 invalid); stream: running (7,762 records, 7,681,064 pairs) |
| R9 | Coverage: every lattice has every pair accounted for | lab tracker and records | section 4 |

## 3. T20 on 07/10, 12:50 UTC

| Part | Status | Programs |
|---|---|---|
| Reduction to nine support configurations | hand + computed | two |
| k = 4: III.0, III.1; k = 2: IIa.0 | excluded, computed | two each (III.1: second program complete on 07/10) |
| k = 0, hand reductions: no vertex of N(p) with d = 3; n_3 in {0, 2}; profile (5,0,2) impossible | hand; the two used for n_3 = 2 re-derived by me on 07/10 | - |
| k = 0, n_3 = 0: six graphs x two profiles | excluded, computed: 615,405 bases, 0 complete | first program complete; second complete on some cases, running on the others (board, lines C2-C4) |
| k = 0, n_3 = 2 | route B (N(p) and the X_3 orbit in the base): profile (4,2,1) finished, 8,557 bases, 0 complete; profile (3,4,0) finishing; figures as reported by the laptop session at 12:45, not yet in the repository | first program finishing; second running |
| Hand lemmas of Codex (isolation of the inner X_0 pair, a_3 = 1, e(X_0) <= 8) | proved, re-read line by line by me; NOT used by the computations | - |
| Route A for n_3 = 2 (my decomposition) | not run: measured at about 1,000 core-hours; 183 of 700 base classes closed, 0 complete (a partial cross-check only) | - |
| Referee pass on the text | first pass done on sections 1-10 (Codex, `lemma/t20_CODEX/REFEREE_T20_PROOF.md`): no fatal gap, two repairable errors, three audit gaps; second pass needed on 9.B and the conclusion | - |

## 4. Coverage of the 156 lattices (lab tracker, 07/10)

Excluded: 143. Open: 13.

| Method recorded in the tracker | Lattices | Recount on 07/10 |
|---|---|---|
| Stream sweep (producer + consumer, all pairs) | 91 | OK-RECOMPUTED from the stored records: coverage complete, 212,825,691 pairs, twin classes all excluded. 55 of them rest on lab-local records of 28-29/09 (see below) |
| h-stage sweep on pair lists, 28-29/09 (044, 072, 096, 097, 105, 106, 108, 116, 119, 120, 121, 127, 130) | 13 | not recounted; lab-local runs |
| frame_dfs with Lemma U+ on the Gamma-reduced pairs, 27/09 (087, 111, 122-126, 131, 135, 137-141) | 14 | not recounted; lab-local runs |
| C1 pair-level results with certificates (115, 132) | 2 | SOURCE-ONLY |
| 000: 141 pair classes (86 by LP certificates, 8 + 47 searched EMPTY) | 1 | set arithmetic OK-RECOMPUTED; certificates and searches not re-run |
| Golay pair blocks (004, 010) | 2 | OK-RECOMPUTED from the stored blocks (416,383 and 3,962 pairs) |
| C1 packing argument (094, 128, 129, 133, 136, 144, 147, 148, 150, 154) | 10 | "run + argument re-read by C2" per the tracker; not re-read on 07/10 |
| Criterion (E) of C1 notes/139 (117, 134, 142) | 3 | SOURCE-ONLY ("depends on Sol's theta theorems" for 117) |
| Component-budget test at lattice level (143) | 1 | SOURCE-ONLY |
| "Sol 0836" arguments: D8^3, D >= 12, E8 (145, 146, 151, 152, 153, 155) | 6 | "re-read C1 notes/139" per the tracker; not re-read on 07/10 |

Twin deferrals: 1,622 dependencies between the 104 stream lattices, no cycle, every target class in the tracker (OK-RECOMPUTED).

The 13 open lattices (001, 002, 003, 005-009, 011-015): all swept in deferral mode except one y1 of 003; 5,190,752 pairs pending T18
and 2,508,295 pending T20; no INCOMPLETE pair. Dry run of the conversion (`convert_deferred.py`): 145 if both lemmas were accepted
today, 155 with all certificates, 156 when 003:181:182 is done.

**Weak point of the record keeping.** 55 stream lattices and the 29 lattices of the 27-29/09 runs (rows 2-4) were computed on the
lab PC before the cloud packages; for 26 of the stream lattices no code version is recorded. Proposal (board line D6): re-run these
with the final engine on free machines and compare.

## 5. What must still happen before statement A may be claimed

1. T20, n_3 = 2: first program finished and its counts in the repository; second program complete and agreeing.
2. T20, n_3 = 0: second program complete on the remaining cases.
3. One referee pass on `lemma/T20_PROOF.md` (section 9.B written after 1), with no open error.
4. Certificate run complete: every one of the 7,762 stream records certified; any record not certified is a pair to treat apart.
5. 003:181:182 finished, or its pairs treated apart.
6. Archival (referee's point G1, `lemma/t20_CODEX/REFEREE_T20_PROOF.md`): for every computation cited by T18 and T20, the per-base outputs
   and plans, the exact source revision, the hashes of the input lists, the commands and the completion checks are in the repository
   (some are still only in session scratch folders).
7. Then: `data/finishC/lemmas_accepted.json` written with the references of T18 and T20, and `convert_deferred.py --write`.

## 6. What the statement would still rest on without independent recheck (to say plainly in any announcement)

- R2 and R4: the upstream reduction and the completeness of the pair enumerations (source only).
- The search engine's code (calibrated between versions, not re-read line by line).
- T18 and T20 are computer-assisted: hand reductions plus exhaustive exact enumerations, each by at least two programs sharing
  the hand model. Scope of that independence (referee's points G2, G3): the second programs follow the first program's choice of
  the next unit (valid by the exhaustiveness lemma: any unfilled unit may be chosen; for case I the verifier asserts that the unit
  is unfilled, generates its own candidates and walks its own kept set: checked in the code by me on 07/10); equal counts are a
  cross-check, not an identity of the states; for III.1 the verifier shares the model file and part of the enumeration skeleton
  with the first program.
- First referee pass on `T20_PROOF.md` (Codex, 07/10): no fatal gap in the hand arguments of sections 1-10; one sign error to
  repair (line 744) and one wording error on the split level; section 9.B and the conclusion need a new pass once written.
- The 20 lattices excluded by lattice-level arguments (packing, criterion (E), component budget, Sol 0836): re-read earlier per the tracker, not on 07/10.
- F0, for statement B only.
