# T20 board: what is left until "the 156 envelopes are excluded" (single source of truth)

Rules of the board: one owner per line; the owner edits his own lines (status, date, link) and pushes; nobody edits another
owner's line. Times are UTC. "Closed" means: computed or proved, files in the repository, counts written. Messages between
sessions are for questions; results go here.

Owners: **LAP** = laptop session (coordination, AWS machines, sub-agents), **LAB** = lab session, **CDX** = Codex session.

## A. Critical path: T20, case I (k = 0), n_3 = 2: the only open case

| # | Item | Owner | Status (07/10) | Next deliverable | Due |
|---|---|---|---|---|---|
| A1 | Route A: lab decomposition (base S u {p} u X_3 u X_0', 700 classes, engine eng5z). 183 classes closed by search, 0 complete; 96 more excluded by hand only (isolation lemma); 421 left. Run stopped at 11:43 | LAB | **measured, answer clear at 12:30** (job `t20_n3_sample` on i-0cefd01aef8eade8a, branch `lemma-run/t20_n3_sample-i-0cefd01aef8eade8a`; method in `t20_HAND/n3_split.py`: one task in 300 below level 2 per base). 160 of 421 bases sampled (all of I.0, 128 of I.1, in file order): 173 million nodes estimated for these 160 alone = 373 core-hours at the node rate of the closed bases (129 per second), 793 at the samples' own rate; mean 1.08 million nodes per base (median 318,000, max 12.6 million); 26 bases over 4 h, 41 between 1 and 4 h; 0 complete configuration met. Extrapolated to the 421 bases: **about 1,000 core-hours per program (up to 2,000)**. Codex's independent program sees the same tree shape (`t20_CODEX/n3_second/MEASUREMENTS.md`). **Route A is not worth running.** The measurement can be stopped (it would end about 13:35) | none unless route B fails; the split-mode runner `n3_split.py run` exists if needed | done |
| A2 | Route B: N(p) and the X_3 orbit in the base (the decomposition that closed n_3 = 0 at 0.3 s per base) | LAP (agent) | started 11:50 | number of bases after stage 1 for the 6 graphs x 2 profiles; measured stage-2 sample; estimated core-hours | 12:45 |
| A3 | **Decision**: one route, with a measured cost, proposed to the user; the other route stops | LAP | pending A1, A2 | time and price | 12:45 |
| A4 | Run of the chosen route (first program) | LAP launches | - | 0 complete configurations or the list of survivors | after A3 |
| A5 | Second program for n_3 = 2, from `t20_HAND/SPEC_N3.md`, no shared code | CDX | implemented and locally checked 11:55; all 24 base counts match, 700 classes / 533 after hand lemmas; five 60 s timeouts and one 300 s timeout recorded in `t20_CODEX/n3_second/MEASUREMENTS.md`; route-A performance work on hold, no exclusion claimed | adapt the exact checker and runner to the chosen route after the 12:45 decision; route-B specification needed if B is chosen; job wrapper already written | 14:00 |

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
| C2 | n_3 = 0, eleven cases: jobs `t20_Iv_B..F` on the free account | LAP | running since 11:10 | 15:30 |
| C3 | n_3 = 0, I.1 (3,4,0): job `t20_I1_340`, 128 cores | LAP | **closed 11:52**: stage 1 agrees (3,508,550 / 878,137 / 219,589), stage 2 agrees at every node (7,279,961 nodes), 0 complete; the 13 rank nodes closed by the second program's own search, no rank bound. Branch `lemma-run/t20_I1_340-i-019e86d399c17954f` | done |
| C4 | n_3 = 0, I.1 (4,2,1): one part of C2 stops at base 12632 (old verifier); re-run that part with the fixed verifier | LAP | to do when C2 is back | 16:00 |

## D. Writing and conversion (start now, in parallel with A)

| # | Item | Owner | Status | Due |
|---|---|---|---|---|
| D1 | `lemma/T20_PROOF.md`: self-contained text, same form as `T18_PROOF.md`, for everything in B; the n_3 = 2 section left as a marked placeholder | LAP (agent) | **written 12:35** (2,709 lines, no GAP box; proves "T20 holds provided section 9.B is completed"); updates of III.1 and I.1 (3,4,0) listed at its top, to merge with D2 | done |
| D2 | n_3 = 2 section of the text, once A4 is done | owner of the chosen route | - | after A4 |
| D3 | One mathematical referee pass on `T20_PROOF.md`, independent of the first search implementation | CDX | queued after D1, D2; first-engine code has not been read, but CDX authors the second checker and therefore is not a code-blind referee | - |
| D4 | Importer on the lab PC: `merged` records, DEFERRED verdicts and index lists, `producer_max_out` (accepted, condition producer.complete), fine blocks of 001; per-pair certificate (norms 7, orthogonality, root, Y = 5 or 4). The pairs stay DEFERRED in the lab tracker until T20 is closed | LAB | 12:30. (1) Reader + checker done (`q/tools/lab_2026-10-07/import_sweep.py`, `measures/SWEEP_LAB_2026-10-07.json`): 14,683 records accepted, 0 refused; all open lattices swept except 003 (one y1 left); 5,190,752 pairs pending T18, 2,508,295 pending T20, 0 INCOMPLETE; 016 EXCLUDED in the lab tracker (143/156); 012 fully computed, waits for 3 twin classes. (2) Certificates: exact checker `q/cert_stream.py`, runner `q/qcert.py` (model of qtail.py, never writes the queue; Q_CERT_PART i/n; one file per record; resume; summary), manifest `measures/CERT_MANIFEST_2026-10-07.json` (7,762 stream records, 5,179,532 + 2,501,532 pairs); tested end to end on the lab PC (006:196:228, 006:189:228, 006:139:228: same stream sha256 as AWS, all deferred pairs certified). Cost: one producer per record, upper bound 727 core-hours, probably 400 to 600; LAP launches on the free machines. (3) Golay 001 and 002 certified here, no producer needed (`measures/cert_golay_001.json`, `_002.json`): 4,545 + 3,169 and 6,675 + 3,594 pairs, 0 invalid | conversion step DEFERRED -> excluded, dry run on the lab tracker; then import of the certificate files when the run is back | 17:00 |
| D5 | Final statement: T18 + T20 + bridge + sweep records => the 156 envelopes are excluded, with the list of what it rests on (upstream reduction: "source only, not re-read") | LAB | after D1-D4 | - |

## E. Sweep (route C)

| Item | Owner | Status |
|---|---|---|
| All queue jobs except one: done (`q/tools/laptop_2026-10-06/sweep_report.py`) | LAP | closed |
| 003:181:182: running since 07:46 on 124 cores (i-00a0ab97a6a8099fd); stop at 13:00 if not back, then treated apart | LAP | running |

## Note of 12:30 (LAP)

The LAB session reached its usage limit at 12:30 and stopped. Until it is back, LAP reads the A1 measurement and keeps the LAB
lines; the relay to CDX goes through the LAB session's bridge, so CDX cannot be reached from the laptop in the meantime.
Left by LAB at 12:30 (its message): certificate runner pushed and tested (`q/qcert.py`, `q/cert_stream.py`,
`measures/CERT_MANIFEST_2026-10-07.json`: 7,762 stream records, 5,179,532 + 2,501,532 deferred pairs); Golay pairs certified
without the producer (`measures/cert_golay_001.json`, `cert_golay_002.json`: 4,545 + 3,169 and 6,675 + 3,594 pairs, 0 invalid).
Not done by LAB: the conversion step DEFERRED -> excluded (dry run), the review of CDX's second program, passing the route-B
specification to CDX.

## Machines running (LAP keeps this current)

| Account | Machine | Job | Since |
|---|---|---|---|
| user | i-00a0ab97a6a8099fd, 128 vCPU, eu-north-1 | 003:181:182 | 07:46 |
| free | 5 x 8 vCPU | C2 | 11:10 |
| free | i-0cefd01aef8eade8a, 8 vCPU, eu-north-1 | A1 measurement (`t20_n3_sample`) | 11:50 |
