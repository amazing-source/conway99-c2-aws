# Part B. The 156 lattices: none hosts a frame

Lab session (Claude), first version 2026-10-07. Part of the single proof document `lemma/PROOF_C2/` (Part A, by the laptop
session: Theorem R, the bridge, the lemmas T16, T18, T20). Not frozen, not refereed as a whole. The table
`B_TABLE_156.md` is generated from the tracker and the checked reports; nothing in it is typed by hand.

## B.0 What Part B proves, and from what

**Statement B.** Let U be one of the 156 odd unimodular lattices of rank 24 without vector of norm 1. Then U contains no
frame: no vectors y_1, y_2, h_1..h_7, u_1..u_42 with the properties (R-i) to (R-vii) of Theorem R (Part A).

With Theorem R (a srg(99,14,1,2) with an automorphism of order 2 gives a frame in one of these lattices) this is the theorem:
no srg(99,14,1,2) has an automorphism of order 2.

Inputs of Part B:
- the list of the 156 lattices, as Gram data (`external_runs/structures_3eceb4d/U/<lid>.json` of the packages): cited theorem
  (Borcherds) for its completeness; determinant 1, oddness, absence of norm 1 and root systems recomputed on 04/10; the seven pairs
  with equal root systems separated by their even neighbours;
- (R-i) to (R-vii) of Theorem R, and nothing else about the graph;
- T16, T18, T20 (Part A.3): U has no vector v with E(v) = 8, 9, 10, where E(v) = 7 (v,v) - (v,y_1)^2 - (v,y_2)^2.

## B.1 The methods

Thirteen groups; the code is the column "method" of the table.

**Lattice-level arguments (20 lattices, no pair is enumerated).**
- **P, EP, SP, So** (19 lattices): the packing argument of C1 (`c1/code/envelope_pack.py`: the 3/2-sets of the 42 u on the new
  roots are pairwise disjoint, so the 42 smallest values of m(x) = r/8 - E_roots(x) must fit in the number of new roots), criterion
  (E), and the arguments of Sol's note 0836; 153 has in addition Theorem R, A.9 (U is indecomposable), which also covers 152.
  These were reread on 27-28/09 (tracker, appendix of the table); on 07/10 only the step "integrality on the words implies
  integrality on all frame vectors" was re-derived (Codex). They are not re-proved in this document: status CITED from the
  project's notes, with their rereaders.
- **B** (143): hand proof, `lemma/upstream/LATTICE_143.md`: from (R-ii), (R-v) and the table of the 4096 vectors of norm 3,
  378 <= 4 * 56 + 16 * 7 = 336. Refereed by Codex (accepted); the table is proved by an exact glue description.

**Pair-level methods (136 lattices).** A frame determines a pair (y_1, y_2) of orthogonal vectors of norm 7; the pairs are
enumerated up to Aut(U) and signs, and each pair is excluded.
- **The enumeration of the pairs** (producer `c1/code/y_pairs_gamma.py`): y_1 dominant for the Weyl group and reduced by a
  symmetry group Gamma, y_2 reduced by the stabiliser, under necessary filters that all follow from (R-vi) (reread: Part A / the
  reduction audit, section C). Completeness of this enumeration is NOT proved line by line. It was compared with an independent
  enumerator (all vectors of norm 7 by Fincke-Pohst, own Weyl reduction) on four lattices: 140, 135, 141 and 064 (the last with
  roots that do not span): the two pair sets are equal in each case (B.4).
- **S** (91 lattices) and **SD** (11): the stream sweep. Every pair passes through the engine (`frame_dfs` / `frame_dfs_next`),
  whose rules are justified one by one against Theorem R in `lemma/upstream/AUDIT_ENGINE_RULES.md` (Codex). A pair ends as:
  excluded at once (a witness vector with E < 8, or the norm-3 witness of T16); excluded by search (the frame search is
  exhausted: no 7 h, or no 42 u); swap-covered (the pair (y_2, y_1) is treated instead: invariant I(y_1) > I(y_2)); transferred
  to a twin lattice (dependencies between lattices: 1,622, without cycle, all resolved); and, for SD only, excluded through the
  bridge by T18 or T20 (a root with Y = 5 or 4), each such pair with an exact certificate.
- **GD** (001, 002) and **G** (004, 010): the same on the pair files of the Golay family.
- **O** (000, the odd Leech lattice): 141 pair classes; 86 by LP certificates verified in integers, 55 by search.
- **H, F, H3** (29 lattices): runs of 27-29/09 on the lab PC on C1's pair lists (h-stage sweep; frame_dfs with Lemma U+; three
  h-stage readings). Not recounted on 07/10; their numbers are in the tracker text only.

## B.2 What was recounted and checked on 07/10

| Check | Scope | Result | Files |
|---|---|---|---|
| Recount of the stream records | 91 lattices S | coverage of every y_1 representative complete, no fault, no y_1 covered twice: 220,260,576 pairs (97,628,147 at once; 22,702,398 by search; 93,822,540 swap-covered; 6,107,330 twin; + 161 first INCOMPLETE and excluded by a second search, sets checked pair by pair by Codex) | `stream_recount.py`, `measures/STREAM_RECOUNT_2026-10-07.json` |
| Import of the deferral sweep | 13 lattices SD, GD | swept, 0 record refused; 5,190,752 pairs through T18, 2,508,295 through T20 | `import_sweep.py`, `measures/SWEEP_LAB_2026-10-07.json` |
| Certificates of the deferred pairs | every deferred pair | stream: 7,762 of 7,762 records with a good certificate (stream regenerated, same sha256; norms 7, orthogonality, witness root); Golay: 17,983 pairs, 0 invalid | `q/cert_stream.py`, `cert_census.py`, `cert_golay.py` |
| Corollary Y1 | 003, y_1 representative 181 (no pair record) | a root r with (r,y_1) = -2: no frame has this y_1, whatever y_2 (T18, T20); two certificates, two checkers | `q/cert_y1.py`, `q/check_cert_y1.py`, `lemma/t20_CODEX/` |
| H1: truncated joint star sums | all stored records | the verdict it could falsify occurs in no record; the importer refuses it | census of 07/10 |
| H2: rigid kernel | the 25 lattices where a zero-footprint h can exist and the engine was used | every pair without flex point that has such a candidate searched again with the general kernel: 147,475,940 pairs read, 8,432 exposed, all excluded again | `q/audit_rigid.py`, `audit_coverage.py`, `measures/AUDIT_COVERAGE_2026-10-07.json` |
| H3: lists of norm 2, 3, 4 | 156 lattices | basis of U, exact norms, distinctness, theta identity: the three lists are complete together | `shell_counts.py`; referee run of Codex with overflow bounds, `lemma/t20_CODEX/REFEREE_SHELL_COUNTS.md` |
| H4: a solver status in the pair-budget test | 105 (6,310 pairs); 143 | 105 passed again without the test: all 56,544 pairs excluded; 143 replaced by the hand proof | `measures/` extra 105; `LATTICE_143.md` |
| Enumeration of the pairs (F4) | 140, 135, 141, 064 | equal sets: 288, 464, 331 and 1,050,528 pairs | `q/ypairs_c2.py`, `q/f4_compare.py`, run branches |

## B.3 Provenance of the records: the main reservation of Part B

The records of the pair-level methods are of three kinds (column "engine" of the table, and `measures/RECONCILE_RECORDS_2026-10-07.json`):

- **Package engine**: the record carries the code version of an engine archived in a package of the campaign. All 13 lattices
  SD / GD, and 36 of the 91 lattices S entirely. Of the 220,260,576 pairs of the lattices S, 212,804,047 are in such records.
- **Lab version, recovered**: 39 lattices S have y_1 representatives (6,282 of 43,718) covered only by records of the lab PC of
  29/09 (11:33 to 18:14) whose stream wrapper `hstage_stream.py` has the hash 4e310e72, which is in no package. The file was found
  on the lab PC on 07/10 under a backup name (`scripts/hstage_stream_v_pre_telemetry.py`, same hash) and is archived with the other
  backups of that week in `q/tools/lab_2026-10-07/engine_history/`; the core `frame_dfs.py` of these records is the one of package
  v1. 4,409,816 pairs. So for these records the program is identified.
- **No version**: 26 lattices S have representatives (4,520) covered only by records without any recorded code version.
  3,046,713 pairs.
- The 29 lattices H, F, H3, and G, O: lab-PC or early runs, single reading, not recounted on 07/10.

Balance for the 55 lattices S that are not entirely on package engines (10,802 y_1 representatives, 7,456,529 pairs): the
program is identified for the lab-version records (6,282 representatives; 234 records selected by the recount, of 251 stored
with that wrapper); it is not recorded for the 4,520 representatives of the no-version records. And 32 more lattices rest on runs
that were not recounted.

**Corollary Y1 removes most of it without any re-run (07/10, 18:20 UTC).** For each of the 55 lattices, `q/cert_y1.py --all` on
its plan: of the 10,802 representatives above, **9,143 have a root r with (r,y_1) = +-2**, so by Corollary Y1 (Part A.2; T18 and
T20) no frame has such a y_1, whatever y_2 and whatever the old record says. The 55 certificate files
(`measures/cert_y1_rerun/`) all pass the standalone exact checker `q/check_cert_y1.py` (12,193 representatives checked in all,
the certificates listing every representative with such a root, not only the 9,143). For these representatives the exclusion no
longer rests on the lab-PC records, but it now rests on T18 and T20, like the 13 last lattices.

Left without an identified program and without a Y1 certificate: **713 y_1 representatives, in 25 lattices** (043, 049-052,
055-058, 070, 073-075, 078, 095, 098-102, 104, 107, 112, 114, 118), covered only by records without code version (runs of
29/09, 00:00 to 13:00). For them the version can only be inferred by dating the record against the backups kept on the lab PC
(`engine_history/README.md`); that is an inference, not a record. And the 32 lattices not recounted. A re-run of these 713
representatives with the archived v10 engine would close the point for the group S; its cost has not been measured.

Where the records are: 33 lattices S entirely on machine branches `run/*` of the compute repository; the others on the lab PC,
copied as they are to the branch `lab-records-2026-10-07`.

## B.4 The table

`B_TABLE_156.md`: one row per lattice (root system, neighbours, number of roots, method, pairs, pairs excluded by search, pairs
through T18 and T20, certificates, engine version of the records, rigid-kernel audit, place of the records), then the tracker's own
text for each lattice. The generator asserts, before writing: 156 lattices, all excluded; the groups partition 0..155; every
lattice S recounted without fault; for SD and GD, as many good certificates as deferral records and as many certified pairs as
deferred ones; the 25 audited lattices covered with no exposed pair left; the shell check passed for all 156.

## B.5 What Part B does not establish

- The completeness of Borcherds' list (cited).
- The completeness of the pair enumeration, beyond the four lattices compared.
- The correctness of the engine's code line by line: its rules were audited against Theorem R, five holes were found and closed
  (H1-H5), two engines agree on calibrations; there is no certificate for a pair excluded by search (25,775,627 such pairs in
  the rows of the table that have the number).
- The lattice-level arguments P, EP, SP, So: cited from the project's notes.
- Everything was done and checked by AI sessions; no human has read it; nothing is formalised.
