# Route (C): the final statement and what it rests on — DRAFT 7 of 2026-10-07, state at 17:50 UTC (clock of the lab PC)

Lab session (Claude). Board line D5 of `lemma/T20_BOARD.md` (compute repo). This is a recheck by AI sessions, not a human referee
and not a formal proof.

> **State on 07/10, 17:50 UTC: the 156 lattices are all excluded in the lab tracker** (conversion run at 17:47, after the user accepted T18 and T20; record `data/finishC/lemmas_accepted.json`). The statement below holds under the conditions of section 6, which are part of it. It is the work of AI sessions: no human has read the proofs, nothing is formalised. Still to do before it is presented as a finished proof: section 5.

## 1. Statement

**Statement.** No strongly regular graph with parameters (99, 14, 1, 2) has an automorphism of order 2.

Scope: nothing is said about a graph without involution.

How it is reached: an automorphism of order 2 fixes exactly one vertex (`lemma/upstream/AUDIT_REDUCTION.md` A.0, by hand;
this replaces the citation of Makhnev-Minakova); such a graph gives a frame in one of 156 lattices (Theorem R, same file);
every lattice is excluded (sections 3, 4). T4 of `MODEL.md` and the reconstruction direction are not used.

## 2. The chain

| Step | Content | Where | Status on 07/10, 15:25 |
|---|---|---|---|
| R0 | An automorphism of order 2 has exactly one fixed vertex | `upstream/AUDIT_REDUCTION.md` A.0 | hand proof (laptop session); refereed by Codex: no error |
| R1 | Theorem R: frame (7 h of norm 4, 42 u of norm 3, y_1, y_2 of norm 7) in an odd unimodular lattice U of rank 24 without vector of norm 1; properties (R-i)..(R-vii), among them E(v) = 7 (v,v) - (v,y_1)^2 - (v,y_2)^2 >= 8 and the dictionary "v in U -> sigma-odd integer eigenfunction of squared norm 2 E(v)" | same, A.1-A.8; U indecomposable: A.9 | hand proof; refereed by Codex: no error. Cited theorems: the oddity formula; classification of forms over F_7. **The input "g in {18, 20}" of the older notes is no longer used** (A.4), and no rule of the engine or of the producer uses g (checked by me and by Codex) |
| R2 | U is one of 156 lattices | Borcherds' classification (cited) | the 156 data lattices: OK-RECOMPUTED 04/10 (determinant 1, odd, no norm 1, root systems; the seven pairs with equal root systems separated by their even neighbours). Mass check: not done, not needed |
| R3 | For each lattice, the pairs (y_1, y_2) up to Aut(U) x signs; swap and twin rules | C1 producers; `AUDIT_REDUCTION.md` section C | the producer's filters follow from Theorem R (reread). Completeness of the enumeration (board F4): the lab's independent enumerator `q/ypairs_c2.py` (all vectors of norm 7 by Fincke-Pohst, own simple roots) against the producer, both brought to one canonical form: **140, 135 and 141: the two pair sets are EQUAL** (288, 464 and 331 pairs; nothing only on one side; 22,892,544 lines of norm 7 = the theta-series value 11178 * 4096 / 2; files `f4/<lid>_compare.json` of run/q-i-02aa613ee361fbc10, read by me). With an identity-only symmetry file the producer lists most pairs twice (both signs of y_2): harmless duplicates. **064 (a_5^4, roots of rank 20, the non-spanning case): EQUAL as well** (17:43; 1,050,528 pairs on both sides, 1,856 y_1 orbits on both sides, 2,100,288 stream lines, nothing only on one side, 22,892,544 lines of norm 7; `f4/064_compare.json` of run/q-i-011dce74cd612fc52, read by me). For 064 both programs were run in parallel (producer in 28 chunks by its own option and merged with a completeness check; enumerator with its loop over y_1 dealt to 28 processes): both changes read by me before the run, and the same machine first reproduced the sequential result of 140 on every field. So the enumeration was compared on four lattices of 156; for the others it rests on the producer's code | Golay family: two implementations agree on 001 |
| R4 | Each pair is excluded by a rule of the engine | `upstream/AUDIT_ENGINE_RULES.md` (Codex: one line per rule, against Theorem R) | no rule uses g. Five qualifications H1-H5, section 3bis |
| R5 | T16: no eigenfunction of squared norm 16 (rule "norm-3 x with Y = 13") | `lemma/T16_PROOF.md` + dossier of 04/10 | refereed by Codex on 07/10: no blocking error (one defect in the dossier's verifier, covered by a stronger recheck) |
| R6 | T18: squared norm 18 | `lemma/T18_PROOF.md` | proved and refereed twice per the laptop session; not reread by me |
| R7 | T20: squared norm 20 | `lemma/T20_PROOF.md` | section 3 |
| R8 | Bridge and witnesses: norm 3 with Y = 13 (E = 8); root with Y = 5 (E = 9); root with Y = 4 or norm-4 vector with (+-3, +-3) (E = 10). These rules are complete for E <= 10 (hand remark of 07/10) | `lemma/BRIDGE.md`; certificates `q/cert_stream.py`, `cert_golay.py` | Golay 001 / 002: 17,983 pairs certified, 0 invalid. Stream: **7,762 of 7,762 records have a good certificate** (15:46; same stream sha256, ok, as many certified pairs as deferred ones: 5,179,532 pending T18, 2,501,532 pending T20; with the Golay pairs these are the 5,190,752 and 2,508,295 deferred pairs), 0 certificate not good, 5 records certified twice and agreeing (`scripts/cloud/cert_census.py`, `measures/CERT_CENSUS_2026-10-07.json`) |
| R8' | Corollary Y1 (Codex, 07/10): with T18 and T20, every root has \|(r,y_1)\| <= 1 and \|(r,y_2)\| <= 1; so a y_1 with a root r, (r,y_1) = +-2, hosts no frame **whatever y_2** (E(r) = 10 - (r,y_2)^2) | `lemma/BRIDGE.md` Corollary Y1; `lemma/t20_CODEX/FIXED_Y1_003.md` | three-line proof, reread by the lab and by the laptop session. Used for ONE y_1 representative, 003:181 (the only one of the campaign without a record): two certificates by two authors (`q/cert_y1.py`, Codex's `CERT_003_FIXED_Y1.json`), two standalone exact checkers, negative controls rejected. 96 of the 182 y_1 representatives of 003 have such a root; the 95 others keep their records |
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
| H2 | The rigid kernel (pairs without flex point) never builds a frame with an h of zero footprint | **real, and exercised** (24 pairs of lattice 080 were decided by it). Hand lemma (lab): impossible unless the two even neighbours have the same Coxeter number H and U has a root component of Coxeter number H: 27 lattices, 25 of them treated by the engine. Exact audit of their streams (`q/audit_rigid.py`): every pair without flex point that has a zero-footprint candidate is searched again with the general kernel. Coverage checked lattice by lattice (`scripts/cloud/audit_coverage.py`): **25 of 25 covered, every exposed pair excluded again** (15:36): 147,475,940 pairs read, 10,267 without flex point, 8,432 exposed, 0 not excluded again; 42 exposed pairs had reached a search in the original runs (003: 2, 006: 1, 014: 2, 023: 1, 077: 12, 080: 24), all excluded again by the general kernel. For the plan lattices the audited pairs add up exactly to the sweep's pair counts. In 003, 179 of the 182 y_1 representatives are covered by audit files; 162, 176 and 181 by Corollary Y1 (pending T18 and T20; 181 has no record, the audit jobs of 162 and 176 were stopped by the laptop session because the certificate covers them). The collector and its first report were reviewed by Codex (`AUDIT_ENGINE_RULES.md`) |
| H3 | The list of norm-4 vectors is produced by a floating-point enumeration | closed for the three shells at once (`q/tools/lab_2026-10-07/shell_counts.py`, `measures/SHELL_COUNTS_EXACT_2026-10-07.json`, run on the lab PC at 15:34 on all 156 lattices, exact arithmetic). For the lists the engine builds (roots, norm 3, norm 4): the engine's basis is a basis of U (unimodular change from the 24 generators, Gram determinant 1); every listed vector has exactly its norm; the vectors are distinct and none is listed with its opposite; and the counts satisfy the theta identity N4 = 196560 - 24 N2 - 24 N3. Lists that are correct can only be short; the identity holds for the true counts; so the three deficits d2, d3, d4 >= 0 satisfy d4 + 24 d2 + 24 d3 = 0 and vanish (argument checked by Codex). N3 = 4096 in all 156, as shadow theory predicts (Conway-Sloane 1990; cited, not used; `theta_odd24.py` takes N3 as an input). Scope: the lists of the lab PC's basis; the machines rebuild them with the same code, and the 47 audit files compared (22 lattices, cloud machines and lab) record the same number of norm-4 lines and of new-root pairs as this table |
| H4 | The per-pair budget test accepts an LP solver status | concerned one lattice, 105 (6,310 pairs, lab run of 29/09). **Closed 14:45**: its 56,544 pairs (enumeration up to W(R)) passed again through the v10 producer and consumer without the budget test: all excluded, swap-covered or twin-transferred; stream sha256 identical on AWS and on the lab PC |
| H5 | The 9/7 rule needs T16, which Theorem R does not give | T16 refereed (R5) |

## 4. Coverage of the 156 lattices (lab tracker, 07/10)

Excluded in the tracker: **156. Open: 0** (since 17:47 UTC on 07/10; backup of the tracker at 143 in `logs/`).

**Reservations that were attached to "excluded" during the day, and how each ended:**
- 20 lattices were excluded subject to the rigid-kernel audit H2: the audit is now complete and clean for all 20 (15:22); this
  reservation is lifted for them;
- 105: its 6,310 "pair budget" pairs are now excluded without a solver (H4 closed, 14:45);
- 143 rested on one lattice-level test that nobody had reviewed. It now has a two-line hand proof
  (`lemma/upstream/LATTICE_143.md`: (R-ii), (R-v) and the table of its 4096 vectors of norm 3; at most 28 of the 42 u fit in the
  a_8 budget, the 14 others exceed the budget of the line orthogonal to the roots, 63/8 > 7), re-run by the laptop session and
  **refereed by Codex: accepted** (`lemma/t20_CODEX/REFEREE_143_PROOF.md`; its exact glue check proves the table without any
  enumerator). The v10 run of 143 was stopped (15:18), nothing of it is imported;
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
| Component budget (143) | 1 | hand proof of 07/10 (`LATTICE_143.md`), table by an exact glue description and two programs; refereed by Codex: accepted |

Twin deferrals: 1,622 dependencies between the 104 stream lattices, no cycle (OK-RECOMPUTED).

The 13 lattices that were open (001, 002, 003, 005-009, 011-015): all swept; 5,190,752 pairs rested on T18 and 2,508,295 on T20, each
with an exact certificate (R8); no INCOMPLETE pair; one y_1 representative, 003:181, carries no pair record and is covered by the
fixed-y1 certificate (R8'). Converted at 17:47 by `scripts/cloud/convert_deferred.py --write` with the real lemma file and the real
certificates: 13 lattices marked excluded, exactly these 13 tracker entries changed.

Provenance of the records of the 143 excluded lattices (recensement of 07/10, `measures/RECONCILE_RECORDS_2026-10-07.json`, script
`q/tools/lab_2026-10-07/reconcile_records.py`; it locates records, it re-derives nothing):
- 33 stream lattices (016-027, 029-042, 045-047, 059, 062-064): every y_1 representative is covered by records that
  are also on a machine branch `run/*` of the compute repository;
- 58 stream lattices (028, 043, 048-058, 060, 061, 065-071, 073-086, 088-093, 095, 098-104, 107, 109, 110, 112-114, 118, 149):
  some or all representatives rest on records made on the lab PC only (45 of them entirely); 26 lattices have records without
  a recorded code version;
- 32 lattices with other lab-PC records (frame_dfs and h-stage runs of 27-29/09, Golay blocks, lattice 000);
- 20 lattices excluded by lattice-level arguments: no pair records.
Since 07/10 a copy of the lab PC's folder `data/finishC` is on the branch `lab-records-2026-10-07` of the compute repository (as it
is; not a certified archive). The user decided on 07/10 not to re-run the lab-local lattices now.

## 5. What is done, and what is still to do

Done on 07/10: T20 text and referee passes; archival G1 (per the laptop session, `lemma/ARTIFACTS_T18_T20.md`; not reviewed; program
versions inferred from launch times); rigid-kernel audit H2 on 25 of 25 lattices; hand proof of 143, refereed; stream certificates
7,762 of 7,762; 003:181 by Corollary Y1; pair enumeration compared on 140, 135, 141, 064; acceptance of T18 and T20 by the user
(`lemmas_accepted.json`: references, git blob ids of the two texts, scope "AI sessions only, no human reader, not formalised", G2
open); conversion: tracker at 156.

Still to do:
1. G2: the wording of the verifier contract in `T20_PROOF.md` (presentation; laptop session).
2. One merged proof document, frozen with a manifest, and one referee pass by Codex on it.
3. The lab-local lattices (section 4, provenance): the user decided on 07/10 not to re-run them; that decision can be revisited.
4. A formalisation: scope to be agreed with the user (`lemma/t20_CODEX/LEAN_FEASIBILITY.md`); nothing exists yet.

## 6. What the statement would still rest on without independent recheck

- Borcherds' classification and the oddity formula (cited theorems).
- The completeness of the pair enumerations, until item 6 is done.
- The search engine's code: one audit of its rules against Theorem R (Codex), no line-by-line second reading; calibrations between
  versions.
- Corollary Y1 is used for one y_1 only, and is conditional on T18 and T20 like every deferred pair.
- T16, T18, T20 are computer-assisted: hand reductions plus exhaustive exact enumerations, each by two programs sharing the hand
  model; the second programs follow the first program's choice of unit (valid by the exhaustiveness lemma; for case I the verifier
  checks that the unit is unfilled and walks its own candidates: read in the code by me).
- The 20 lattices excluded by lattice-level arguments of C1 / Sol (packing, criterion (E), Sol 0836): reread earlier, not on 07/10,
  except what is noted in the table.
