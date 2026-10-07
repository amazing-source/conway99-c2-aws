# T20 board: what is left until "the 156 envelopes are excluded" (single source of truth)

Rules of the board: one owner per line; the owner edits his own lines (status, date, link) and pushes; nobody edits another
owner's line. Times are UTC. "Closed" means: computed or proved, files in the repository, counts written. Messages between
sessions are for questions; results go here.

Owners: **LAP** = laptop session (coordination, AWS machines, sub-agents), **LAB** = lab session, **CDX** = Codex session.

## A. Critical path: T20, case I (k = 0), n_3 = 2: the only open case

| # | Item | Owner | Status (07/10) | Next deliverable | Due |
|---|---|---|---|---|---|
| A1 | Route A: lab decomposition (base S u {p} u X_3 u X_0', 700 classes, engine eng5z). 183 classes closed by search, 0 complete; 96 more excluded by hand only (isolation lemma); 421 left. Run stopped at 11:43 | LAB | **measured, answer clear at 12:30** (job `t20_n3_sample` on i-0cefd01aef8eade8a, branch `lemma-run/t20_n3_sample-i-0cefd01aef8eade8a`; method in `t20_HAND/n3_split.py`: one task in 300 below level 2 per base). 160 of 421 bases sampled (all of I.0, 128 of I.1, in file order): 173 million nodes estimated for these 160 alone = 373 core-hours at the node rate of the closed bases (129 per second), 793 at the samples' own rate; mean 1.08 million nodes per base (median 318,000, max 12.6 million); 26 bases over 4 h, 41 between 1 and 4 h; 0 complete configuration met. Extrapolated to the 421 bases: **about 1,000 core-hours per program (up to 2,000)**. Codex's independent program sees the same tree shape (`t20_CODEX/n3_second/MEASUREMENTS.md`). **Route A is not worth running.** The measurement can be stopped (it would end about 13:35) | none unless route B fails; the split-mode runner `n3_split.py run` exists if needed | done |
| A2 | Route B: N(p) and the X_3 orbit in the base (37 vertices), then the X_2 orbits outside N(p) | LAP (agent) | **both programs COMPLETE 14:00**: 50 cases (6 graphs, 25 types of z, 2 profiles), 64,528 bases = 64,498 classes, 86,968 nodes, at most 3 X_2 orbits placed, 0 complete configurations, rank bound never used; second program (`in_verify.py` basesz / follow / mergez) agrees on the classes of bases and on the kept count at every node; every rejection exact (`t20_R3_I/n3_verify.out`) | review of `SPEC_ROUTE_B_N3.txt` and of `T20_PROOF.md` 9.B.6 by CDX (A5) | done |
| A3 | **Decision** | LAP | **route B** (12:45): about 5 laptop CPU-hours for both programs, no cloud machine. Route A measured at about 1,000 core-hours per program: dropped | - | done |
| A4 | Run of the chosen route (first program) | LAP | **done 12:55, 0 complete configurations** (see A2) | - | done |
| A5 | Route-B model/specification review, independent of the first search implementation; route-A checker retained as an unused record | CDX | route B selected per coordination message 46; D3 first pass delivered, route-A optimization stopped; laptop already supplies the second route-B program, so no redundant full third run planned | review the self-contained route-B specification when published, especially stage-1 coverage, all 84 attachments of z to N(p), and quotient by the stabilizer of {U3,V3} | upon specification delivery |

## B. Already closed (do not redo)

| Item | Status | Where |
|---|---|---|
| Reduction to nine support configurations | closed (hand + two programs) | `t20/T20_REPORT.md` |
| III.0 (k = 4) | closed, two programs | `t20_R2/REPORT.md` |
| IIa.0 (k = 2) | closed, two independent programs | `t20_R2/REPORT.md` |
| III.1 (k = 4) | closed, first program + independent verifier over the whole tree (1,628,864 nodes, 0 complete; does not need the rank bound) | `t20_III1/README.md`, `VERIF.md` |
| Case I, n_3 = 0, six graphs x two profiles | closed by the first program (615,405 bases, 0 complete); I.0 (4,2,1), I.5 (4,2,1) by two programs | `t20_R3_I/REPORT.md` |
| Hand lemmas: profile (5,0,2) impossible; no d = 3 vertex in N(p); n_3 in {0, 2}; X_0 structure for (4,2,1); e(X_0) <= 8; a_3(u) = 1 | proved, re-read | `t20_R2`, `t20_HAND/NOTES.md`, `t20_CODEX/` |

## C. Second programs still running or to do (one independent re-run per computed step, no more)

| # | Item | Owner | Status | Due |
|---|---|---|---|---|
| C1 | III.1: independent verifier over the whole tree, plus the one node rejected by rank | LAP (agent) | **closed 11:47**: agrees at every node, 0 complete (`t20_III1/VERIF.md`) | done |
| C2 | n_3 = 0, eleven cases on the free account | LAP | **closed 14:33**: the second program agrees at every node on all eleven (with C3: all twelve cases), 0 complete. Last one, I.1 (4,2,1): 56,300 bases, 1,406,917 nodes, the 2 rank nodes closed by its own search (branch `lemma-run/t20_Iv_G-i-05703a74fbb027423`) | done |
| C3 | n_3 = 0, I.1 (3,4,0): job `t20_I1_340`, 128 cores | LAP | **closed 11:52**: stage 1 agrees (3,508,550 / 878,137 / 219,589), stage 2 agrees at every node (7,279,961 nodes), 0 complete; the 13 rank nodes closed by the second program's own search, no rank bound. Branch `lemma-run/t20_I1_340-i-019e86d399c17954f` | done |
| C4 | n_3 = 0, I.1 (4,2,1) with the fixed verifier | LAP | folded into C2: job `t20_Iv_G` runs the whole case from master (fixed `in_verify.py`) | 15:30 |

## D. Writing and conversion (start now, in parallel with A)

| # | Item | Owner | Status | Due |
|---|---|---|---|---|
| D1 | `lemma/T20_PROOF.md`: self-contained text, same form as `T18_PROOF.md`, for everything in B; the n_3 = 2 section left as a marked placeholder | LAP (agent) | **written 12:35** (2,709 lines, no GAP box; proves "T20 holds provided section 9.B is completed"); updates of III.1 and I.1 (3,4,0) listed at its top, to merge with D2 | done |
| D2 | n_3 = 2 section of the text | LAP | **written 14:10, refereed by CDX 14:20 (no blocking error), two presentation points merged**: `T20_PROOF.md` 9.B.6 and Theorem 10.2 (T20). Left: G1 (provenance table), G2 (verifier contract wording), C3 | done except G1, G2 |
| D3 | One mathematical referee pass on `T20_PROOF.md`, independent of the first search implementation | CDX | first pass complete on 8510844a4: `t20_CODEX/REFEREE_T20_PROOF.md`; one local sign repair, split-level wording, provenance and verifier-contract qualifications; nine support representatives/automorphism orders/unit lists checked independently; no fatal hand gap found, Theorem 10.1 remains conditional on the computations; new pass required after D2 | after D2 for n3=2 addition |
| D4 | Importer on the lab PC: `merged` records, DEFERRED verdicts and index lists, `producer_max_out` (accepted, condition producer.complete), fine blocks of 001; per-pair certificate (norms 7, orthogonality, root, Y = 5 or 4). The pairs stay DEFERRED in the lab tracker until T20 is closed | LAB | 12:30. (1) Reader + checker done (`q/tools/lab_2026-10-07/import_sweep.py`, `measures/SWEEP_LAB_2026-10-07.json`): 14,683 records accepted, 0 refused; all open lattices swept except 003 (one y1 left); 5,190,752 pairs pending T18, 2,508,295 pending T20, 0 INCOMPLETE; 016 EXCLUDED in the lab tracker (143/156); 012 fully computed, waits for 3 twin classes. (2) Certificates: exact checker `q/cert_stream.py`, runner `q/qcert.py` (model of qtail.py, never writes the queue; Q_CERT_PART i/n; one file per record; resume; summary), manifest `measures/CERT_MANIFEST_2026-10-07.json` (7,762 stream records, 5,179,532 + 2,501,532 pairs); tested end to end on the lab PC (006:196:228, 006:189:228, 006:139:228: same stream sha256 as AWS, all deferred pairs certified). Cost: one producer per record, upper bound 727 core-hours, probably 400 to 600; LAP launches on the free machines. (3) Golay 001 and 002 certified here, no producer needed (`measures/cert_golay_001.json`, `_002.json`): 4,545 + 3,169 and 6,675 + 3,594 pairs, 0 invalid (4) Conversion step written, dry run only (`q/tools/lab_2026-10-07/convert_deferred.py`: a lattice is excludable when swept, its lemmas are in `lemmas_accepted.json`, every deferral record has its certificate, and its twin classes are excludable; fixed point). Dry runs at 12:35: today 143; if T18 and T20 were accepted today 145 (001 and 002: certificates in); with all stream certificates 155; **003 stays blocked by its last y1 (003:181:182)** (5) Certificate run, first figures from the real machine at 12:39 (run/q-i-0fa91a45f074cf15e, part 0/6): 11 records certified, 0 failed, 0 not certified; the heaviest records take 80 to 190 s each (their original jobs: 200 to 7,000 s), so the whole run should cost well under the 727 h bound: of the order of 100 to 200 core-hours (projection from the heaviest records, not a measurement) (6) 13:00: norm-4 witnesses of T20 (deferred.T20_norm4, rule Q_DEFER_N4) supported by cert_stream.py, qcert.py, the importer and the conversion step (master 0c854fdbc); tested with a positive and a negative case. The rule was re-derived by hand and is complete: with the Y = 13 rule and the two root rules it detects every pair of dual minimum <= 10/7 (remark in `lemma/FINAL_STATEMENT_DRAFT.md`, line R8). The six-part manifest must NOT be regenerated while the run is on; 003:181:182 gets a separate manifest | import of the certificate files as the run comes back (LAP's machines, first part started 12:3x); the real conversion only when T20 is accepted | 17:00 |
| D5 | Final statement: T18 + T20 + bridge + sweep records => the 156 envelopes are excluded, with the list of what it rests on (upstream reduction: "source only, not re-read") | LAB | draft written 12:50: `lemma/FINAL_STATEMENT_DRAFT.md` (statements A and B, the chain R1-R9 with the status of each step, T20 part by part, the 143 excluded lattices by method with what was recounted, the six things that must still happen, and what stays unchecked) | final version when A4, C2-C4, D3 and the certificate run are in | after D1-D4 |
| D6 | Provenance of the 143 lattices already excluded (read-only recount, `q/tools/lab_2026-10-07/audit_stream_excluded.py`; table in `lemma/FINAL_STATEMENT_DRAFT.md` section 4). Recounted and agreeing: the 91 stream lattices (212,825,691 pairs, coverage complete), Golay 004 / 010, the 141 classes of 000, the twin dependency graph (1,622 edges, no cycle). Weak point: 84 lattices were computed on the lab PC on 27-29/09, before the cloud packages (55 stream lattices, 26 of them without a recorded code version; 13 h-stage sweeps; 14 frame_dfs runs; 2 C1 pair-level results) | LAB | found 12:45. **User's decision (07/10, 13:05): no re-run now; this can wait. The results should be findable on the lab PC, and several of these lattices were also computed in the compute repo.** First look: the old run branches run/pere-*, run/frere-*, run/toi-*, run/slice-* hold result files for 011, 014, 015, 018, 019, 031, 032, 034, 043, 053, 054, 055, 061, and the folder `resultats/` holds earlier ones; the reconciliation with the lab's chunk records is not done | reconciliation of the lab-local records with what the repository and the lab PC hold, after T20 and the certificates | - |

## E. Sweep (route C)

| Item | Owner | Status |
|---|---|---|
| All queue jobs except one: done (`q/tools/laptop_2026-10-06/sweep_report.py`) | LAP | closed |
| 003:181:182: **covered without any computation (14:50, fixed-y1 lemma of Codex, `BRIDGE.md` Corollary Y1).** U has the root r = -e_3 + e_10 with (r,y1) = -2 for the y1 of representative 181, so E(r) = 10 - (r,y2)^2 for every y2: T18 or T20 applies. Text and certificate of Codex: `lemma/t20_CODEX/FIXED_Y1_003.md`, `verify_003_fixed_y1.py`; lab certificate `measures/cert_y1/cert_y1_003.json` (`q/cert_y1.py`), standalone checker `q/check_cert_y1.py` (six negative controls rejected); own check of LAP with the package code. The lab import counts representative 181 as covered with no pair, status "pending T18 and T20"; the conversion step requires both lemmas and re-runs the checker. All runs of this job were stopped at 14:54 (LAP); nothing of them is imported. History: unbounded run stopped at 13:00 after 5.2 h on 124 cores; re-run with the norm-4 witness rule `Q_DEFER_N4=1` from 13:00 to 14:54, no record | CDX (lemma), LAB (certificate, import), LAP (machines) | **closed, pending T18 and T20 like every deferred pair** |

## Note of 12:30 (LAP)

The LAB session reached its usage limit at 12:30 and stopped. Until it is back, LAP reads the A1 measurement and keeps the LAB
lines; the relay to CDX goes through the LAB session's bridge, so CDX cannot be reached from the laptop in the meantime.
Left by LAB at 12:30 (its message): certificate runner pushed and tested (`q/qcert.py`, `q/cert_stream.py`,
`measures/CERT_MANIFEST_2026-10-07.json`: 7,762 stream records, 5,179,532 + 2,501,532 deferred pairs); Golay pairs certified
without the producer (`measures/cert_golay_001.json`, `cert_golay_002.json`: 4,545 + 3,169 and 6,675 + 3,594 pairs, 0 invalid).
Not done by LAB: the conversion step DEFERRED -> excluded (dry run), the review of CDX's second program, passing the route-B
specification to CDX.

## F. Upstream reduction audit (user's request of 07/10: no hole between the graph and the 156 lattices)

File: `lemma/upstream/AUDIT_REDUCTION.md`. No sub-agents for this (weekly limit).

| # | Task | Owner | State | Due |
|---|---|---|---|---|
| F1 | Theorem R (involution with one fixed vertex => frame in one of the 156), every step by hand; g in {18,20} removed from the chain; U indecomposable (A.9) | LAP | **done 13:40** (sections A, F) | done |
| F2 | Referee of section A once (statement R, A.4, A.6, A.9), then section B: every pruning rule of the engine against (R-i)..(R-vii) | CDX | **done**: A.0-A.9 refereed, no error (`t20_CODEX/REFEREE_REDUCTION.md`); section B = `upstream/AUDIT_ENGINE_RULES.md`, five conditions H1-H5 on the executable (lines F6-F10) | - |
| F3 | Sections C, D, E | LAB | **filled 13:35**; two weak points named: F4, F5 | done |
| F4 | Independent enumeration of the pairs: `ypairs_c2.py` to the end on 140, 141, 135 and one lattice whose roots do not span; compare with the producer | LAB (free machine from LAP if needed) | `ypairs_c2.py` on 140 on the lab PC: y_1 stage 112 s (22,892,544 norm-7 lines, 17,743,872 admissible, 30 W-orbits), y_2 stage not finished in 270 s: too long for the lab PC's 5-minute rule; the scripts and command lines for a free machine are NOT pushed yet (next lab item) | - |
| F5 | 143 (one unreviewed argument): producer + engine v10. 153: second proof by A.9 (refereed by CDX: no error) | LAB / CDX | 143: job list pushed (`measures/SWEEP_EXTRA_MANIFEST_2026-10-07.json`, identity-only symmetry file: C1's Gamma file for 143 aborts on the lab PC, no basis); its producer alone does not finish in 4 minutes on the lab PC, so no cost measure | records of 143 imported | when LAP has a slot |
| F6 | H1: silent cap of 1000 joint solutions | LAB | census: the affected verdict occurs in no stored record; importer refuses it | done |
| F7 | **H2: rigid kernel never builds a frame with a zero-footprint h.** Exact audit of the streams (`q/audit_rigid.py`, `q/qaudit.py`, 1,520 jobs): batch 1 = the 20 lattices already counted as excluded, batch 2 = 003, 006, 007, 014. 001 audited by the lab: 18 exposed pairs, all excluded again | LAB (scripts), LAP (machines) | batch 1 part 0/2 running since 13:50 on i-0ffabb9fb91879e62; part 1/2 and batch 2 when slots free up. **Until it ends, the 20 lattices are excluded subject to this audit** | - |
| F8 | H3: norm-4 shell count N4 = 196560 - 24 N2 - 24 N3 (`upstream/theta_odd24.py`) checked on the 156 lattices | LAP (formula), LAB (table `measures/SHELL_COUNTS_2026-10-07.json`) | all agree | done |
| F9 | H4: pairs excluded by an LP status ("pair budget", FD_PREBUDGET=1) in lab-local files | LAB | **found 14:10: they all belong to ONE lattice, 105** (6,310 of its 14,169 Gamma-reduced pairs, lab run of 29/09; my first count 12,620 read the files twice). No cloud record carries this verdict. Repair: 105 goes again through the v10 producer and consumer, without solver: `measures/SWEEP_EXTRA_MANIFEST_2026-10-07.json` (16 jobs with 143; runner `q/qaudit.py`, consumer = sweep) | records of 105 imported, all pairs excluded without LP | when LAP has a slot |
| F10 | H5: the 9/7 rule rests on T16 (no eigenfunction of squared norm 16): text pushed by the lab (9ad23660d); one referee pass | LAB (text), CDX (referee, after A5) | - | - |

## Machines running: NONE (07/10, 17:45 UTC)

No instance, volume or Spot request on either account, checked region by region. Deploy keys 165097369 and 165551629 revoked at
about 18:05 UTC; a new run needs a new key. Lab tracker: 156 excluded of 156 since 17:47 UTC (`measures/finishC_tracker_2026-10-07_156.json`).
Next work: the single proof document, `lemma/PROOF_C2/README.md`. State of everything: `HANDOFF_2026-10-01.md` section 19.
