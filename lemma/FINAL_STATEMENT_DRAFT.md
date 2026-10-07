# Route (C): the final statement and what it rests on — DRAFT 2 of 2026-10-07, state at about 15:00 UTC

Lab session (Claude). Board line D5 of `lemma/T20_BOARD.md` (compute repo). This is a recheck by AI sessions, not a human referee
and not a formal proof.

> **Not yet true on the day of writing.** Section 5 lists what is still missing; nothing below may be quoted as a result before.

## 1. Statement

**Statement.** No strongly regular graph with parameters (99, 14, 1, 2) has an automorphism of order 2.

Scope: nothing is said about a graph without involution.

How it is reached: an automorphism of order 2 fixes exactly one vertex (`lemma/upstream/AUDIT_REDUCTION.md` A.0, by hand;
this replaces the citation of Makhnev-Minakova); such a graph gives a frame in one of 156 lattices (Theorem R, same file);
every lattice is excluded (sections 3, 4). T4 of `MODEL.md` and the reconstruction direction are not used.

## 2. The chain

| Step | Content | Where | Status on 07/10, 14:20 |
|---|---|---|---|
| R0 | An automorphism of order 2 has exactly one fixed vertex | `upstream/AUDIT_REDUCTION.md` A.0 | hand proof (laptop session); refereed by Codex: no error |
| R1 | Theorem R: frame (7 h of norm 4, 42 u of norm 3, y_1, y_2 of norm 7) in an odd unimodular lattice U of rank 24 without vector of norm 1; properties (R-i)..(R-vii), among them E(v) = 7 (v,v) - (v,y_1)^2 - (v,y_2)^2 >= 8 and the dictionary "v in U -> sigma-odd integer eigenfunction of squared norm 2 E(v)" | same, A.1-A.8; U indecomposable: A.9 | hand proof; refereed by Codex: no error. Cited theorems: the oddity formula; classification of forms over F_7. **The input "g in {18, 20}" of the older notes is no longer used** (A.4), and no rule of the engine or of the producer uses g (checked by me and by Codex) |
| R2 | U is one of 156 lattices | Borcherds' classification (cited) | the 156 data lattices: OK-RECOMPUTED 04/10 (determinant 1, odd, no norm 1, root systems; the seven pairs with equal root systems separated by their even neighbours). Mass check: not done, not needed |
| R3 | For each lattice, the pairs (y_1, y_2) up to Aut(U) x signs; swap and twin rules | C1 producers; `AUDIT_REDUCTION.md` section C | the producer's filters follow from Theorem R (reread). **Completeness of the enumeration: never compared with an independent enumerator (OPEN, board F4)**; Golay family: two implementations agree on 001 |
| R4 | Each pair is excluded by a rule of the engine | `upstream/AUDIT_ENGINE_RULES.md` (Codex: one line per rule, against Theorem R) | no rule uses g. Five qualifications H1-H5, section 3bis |
| R5 | T16: no eigenfunction of squared norm 16 (rule "norm-3 x with Y = 13") | `lemma/T16_PROOF.md` + dossier of 04/10 | refereed by Codex on 07/10: no blocking error (one defect in the dossier's verifier, covered by a stronger recheck) |
| R6 | T18: squared norm 18 | `lemma/T18_PROOF.md` | proved and refereed twice per the laptop session; not reread by me |
| R7 | T20: squared norm 20 | `lemma/T20_PROOF.md` | section 3 |
| R8 | Bridge and witnesses: norm 3 with Y = 13 (E = 8); root with Y = 5 (E = 9); root with Y = 4 or norm-4 vector with (+-3, +-3) (E = 10). These rules are complete for E <= 10 (hand remark of 07/10) | `lemma/BRIDGE.md`; certificates `q/cert_stream.py`, `cert_golay.py` | Golay 001 / 002: 17,983 pairs certified, 0 invalid. Stream: 7,762 records, run in progress, 0 failure so far |
| R9 | Coverage of the 156 lattices | section 4 | - |

## 3. T20 on 07/10, 14:20 UTC

| Part | Status | Programs |
|---|---|---|
| Reduction to nine support configurations; k = 4 (III.0, III.1); k = 2 (IIa.0) | excluded, hand + computed | two each; for III.1 the second verification shares the model file and part of the enumeration skeleton |
| k = 0, n_3 = 0: six graphs x two profiles | excluded: 615,405 bases, 0 complete | second program agreeing on all 12 cases (the last one, I.1 (4,2,1), at 14:33) |
| k = 0, n_3 = 2 (route B: N(p) and the X_3 orbit in the base) | excluded: 64,528 bases, 86,968 nodes, 0 complete, rank bound never used | second program: 50 of 50 cases agree |
| Text | `T20_PROOF.md` complete (Theorem 10.2) | - |
| Referee (Codex) | two passes, no blocking error; its corrections are applied in the text per the laptop session (14:17). Standing qualifications: G1 (archive outputs, source revisions, commands), G2 (state the verifier contract; equal counts are a cross-check), G3 (III.1) | - |

## 3bis. The engine: Codex's five qualifications (07/10)

| | Finding | Status |
|---|---|---|
| H1 | `joint` keeps at most 1000 joint star sums per leaf, without a flag | real in the code, never exercised: the verdict it could falsify occurs in no stored record (17,676 + 356 + 57 files); the lab importer refuses it |
| H2 | The rigid kernel (pairs without flex point) never builds a frame with an h of zero footprint | **real, and exercised** (16 pairs of lattice 080 were decided by it). Hand lemma (lab): impossible unless the two even neighbours have the same Coxeter number H and U has a root component of Coxeter number H: 27 lattices, 25 of them treated by the engine. Exact audit of their streams (`q/audit_rigid.py`): every exposed pair is searched again with the general kernel. Done: 001, 080, 101, 103, 104, 105, 137, 138 (all exposed pairs excluded again; in 080, 16 exposed pairs had reached the search: stage 1 is empty with the general kernel too); running on machines: the 12 others counted as excluded, and 003, 006, 007, 014 |
| H3 | The list of norm-4 vectors is produced by a floating-point enumeration | closed: N3 = 4096 and N4 = 196560 - 24 (N2 + N3) for all 156 lattices (theta series), every vector rechecked |
| H4 | The per-pair budget test accepts an LP solver status | concerned one lattice, 105 (6,310 pairs, lab run of 29/09). **Closed 14:45**: its 56,544 pairs (enumeration up to W(R)) passed again through the v10 producer and consumer without the budget test: all excluded, swap-covered or twin-transferred; stream sha256 identical on AWS and on the lab PC |
| H5 | The 9/7 rule needs T16, which Theorem R does not give | T16 refereed (R5) |

## 4. Coverage of the 156 lattices (lab tracker, 07/10)

Excluded in the tracker: 143. Open: 13.

**Read "excluded" with these reservations until the items of section 5 are done:**
- 20 lattices are excluded subject to the rigid-kernel audit H2: 022, 023, 024, 026, 027, 028, 037, 049, 050, 052, 053, 077, 079,
  080, 101, 103, 104, 105, 137, 138 (audit done for 080, 101, 103, 104, 105, 137, 138);
- 105: its 6,310 "pair budget" pairs are now excluded without a solver (H4 closed, 14:45);
- 143 rests on one lattice-level test that nobody reviewed: passing through the v10 engine (launched 14:17);
- 153 had one argument reviewed by its author's side only; it now has a second proof (A.9: U is indecomposable), refereed.

| Method recorded in the tracker | Lattices | Recount on 07/10 |
|---|---|---|
| Stream sweep (producer + consumer, all pairs) | 91 | OK-RECOMPUTED from the stored records: coverage complete, 212,825,691 pairs, twin classes all excluded |
| h-stage sweep on pair lists, 28-29/09 (044, 072, 096, 097, 105, 106, 108, 116, 119, 120, 121, 127, 130) | 13 | not recounted; lab-local runs |
| frame_dfs with Lemma U+ on the Gamma-reduced pairs, 27/09 (087, 111, 122-126, 131, 135, 137-141) | 14 | not recounted; lab-local runs |
| Three h-stage readings on C1's pairs (115, 132) | 2 | SOURCE-ONLY |
| 000: 141 pair classes (86 LP certificates, 8 + 47 searched EMPTY) | 1 | set arithmetic OK-RECOMPUTED; certificates and searches not re-run |
| Golay pair blocks (004, 010) | 2 | OK-RECOMPUTED from the stored blocks |
| C1 packing argument (094, 128, 129, 133, 136, 144, 147, 148, 150, 154) | 10 | reread on 27-28/09 per the tracker; the step "integrality on the words implies integrality on all frame vectors" re-derived by Codex on 07/10 |
| Criterion (E) AND packing (117, 134, 142) | 3 | two methods each |
| "Sol 0836" AND packing (145, 146, 151, 152, 155) | 5 | two methods each; 152 also by A.9 |
| "Sol 0836" only (153) | 1 | second proof by A.9 |
| Component-budget test only (143) | 1 | single unreviewed method: being re-run |

Twin deferrals: 1,622 dependencies between the 104 stream lattices, no cycle (OK-RECOMPUTED).

The 13 open lattices: all swept in deferral mode except one y1 of 003 (re-run since 13:00 with the norm-4 witness rule); 5,190,752
pairs pending T18 and 2,508,295 pending T20; no INCOMPLETE pair. Dry run of the conversion: 145 if the lemmas were accepted today,
155 with all certificates, 156 when 003:181:182 is done.

Provenance: 84 lattices were computed on the lab PC on 27-29/09, before the cloud packages (26 of the stream ones without a recorded
code version). The user decided on 07/10 not to re-run them now; the records are on the lab PC (`data/finishC/`, not in any
repository yet) and partly in the compute repository.

## 5. What must still happen before the statement may be claimed

1. T20: archival G1 (outputs, source revisions, commands of every computation cited).
2. Rigid-kernel audit H2 complete on the 25 lattices, with every exposed pair excluded again.
3. 143 through the v10 engine; its records imported (105: done).
4. Certificate run complete: every stream record certified.
5. 003:181:182 finished, imported and certified.
6. Pair enumeration (R3): an independent enumeration on a few lattices, one of them with non-spanning roots (board F4).
7. Then: `data/finishC/lemmas_accepted.json` written with the references of T18 and T20 (T16 is already a rule of the engine),
   and `convert_deferred.py --write`.
8. Decision of the user on the 84 lab-local lattices (reconciliation with the stored records, or re-run).

## 6. What the statement would still rest on without independent recheck

- Borcherds' classification and the oddity formula (cited theorems).
- The completeness of the pair enumerations, until item 6 is done.
- The search engine's code: one audit of its rules against Theorem R (Codex), no line-by-line second reading; calibrations between
  versions.
- T16, T18, T20 are computer-assisted: hand reductions plus exhaustive exact enumerations, each by two programs sharing the hand
  model; the second programs follow the first program's choice of unit (valid by the exhaustiveness lemma; for case I the verifier
  checks that the unit is unfilled and walks its own candidates: read in the code by me).
- The 20 lattices excluded by lattice-level arguments of C1 / Sol (packing, criterion (E), Sol 0836): reread earlier, not on 07/10,
  except what is noted in the table.
