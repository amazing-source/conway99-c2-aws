# T20 board: what is left until "the 156 envelopes are excluded" (single source of truth)

Rules of the board: one owner per line; the owner edits his own lines (status, date, link) and pushes; nobody edits another
owner's line. Times are UTC. "Closed" means: computed or proved, files in the repository, counts written. Messages between
sessions are for questions; results go here.

Owners: **LAP** = laptop session (coordination, AWS machines, sub-agents), **LAB** = lab session, **CDX** = Codex session.

## A. Critical path: T20, case I (k = 0), n_3 = 2: the only open case

| # | Item | Owner | Status (07/10) | Next deliverable | Due |
|---|---|---|---|---|---|
| A1 | Route A: lab decomposition (base S u {p} u X_3 u X_0', 700 classes, engine eng5z). 183 classes closed by search, 0 complete; 101 more excluded by hand (isolation lemma); 416 left. Size very unequal: closed bases median 83 s, but one unfinished base sampled at about 2 million nodes = about 4 CPU-h (my first figure, 3.7 CPU-min per base, was biased: closed bases only). Run stopped at 11:43 | LAB | measurement job pushed 11:48 (`cloud/jobs/t20_n3_sample.sh`, master 33def8550; method in `t20_HAND/n3_split.py`); waits for the 8-core machine | `sample/ESTIMATE.txt` on the run branch: estimated nodes and core-hours per remaining base and in total; then this line | 12:45 |
| A2 | Route B: N(p) and the X_3 orbit in the base (the decomposition that closed n_3 = 0 at 0.3 s per base) | LAP (agent) | started 11:50 | number of bases after stage 1 for the 6 graphs x 2 profiles; measured stage-2 sample; estimated core-hours | 12:45 |
| A3 | **Decision**: one route, with a measured cost, proposed to the user; the other route stops | LAP | pending A1, A2 | time and price | 12:45 |
| A4 | Run of the chosen route (first program) | LAP launches | - | 0 complete configurations or the list of survivors | after A3 |
| A5 | Second program for n_3 = 2, from `t20_HAND/SPEC_N3.md`, no shared code | CDX | writing | measure on 5 bases, then job script | 14:00 |

## B. Already closed (do not redo)

| Item | Status | Where |
|---|---|---|
| Reduction to nine support configurations | closed (hand + two programs) | `t20/T20_REPORT.md` |
| III.0 (k = 4) | closed, two programs | `t20_R2/REPORT.md` |
| IIa.0 (k = 2) | closed, two independent programs | `t20_R2/REPORT.md` |
| III.1 (k = 4) | closed by the first program (1,628,864 nodes, 0 complete) | `t20_III1/` |
| Case I, n_3 = 0, six graphs x two profiles | closed by the first program (615,405 bases, 0 complete); I.0 (4,2,1), I.5 (4,2,1) by two programs | `t20_R3_I/REPORT.md` |
| Hand lemmas: profile (5,0,2) impossible; no d = 3 vertex in N(p); n_3 in {0, 2}; X_0 structure for (4,2,1); e(X_0) <= 8; a_3(u) = 1 | proved, re-read | `t20_R2`, `t20_HAND/NOTES.md`, `t20_CODEX/` |

## C. Second programs still running or to do (one independent re-run per computed step, no more)

| # | Item | Owner | Status | Due |
|---|---|---|---|---|
| C1 | III.1: independent verifier over the whole tree, plus the one node rejected by rank | LAP (agent) | running on the laptop | 18:00 |
| C2 | n_3 = 0, eleven cases: jobs `t20_Iv_B..F` on the free account | LAP | running since 11:10 | 15:30 |
| C3 | n_3 = 0, I.1 (3,4,0): job `t20_I1_340`, 128 cores | LAP | running since 11:19 | 12:15 |
| C4 | n_3 = 0, I.1 (4,2,1): one part of C2 stops at base 12632 (old verifier); re-run that part with the fixed verifier | LAP | to do when C2 is back | 16:00 |

## D. Writing and conversion (start now, in parallel with A)

| # | Item | Owner | Status | Due |
|---|---|---|---|---|
| D1 | `lemma/T20_PROOF.md`: self-contained text, same form as `T18_PROOF.md`, for everything in B; the n_3 = 2 section left as a marked placeholder | LAP (agent) | starting 11:55 | 17:00 |
| D2 | n_3 = 2 section of the text, once A4 is done | owner of the chosen route | - | after A4 |
| D3 | One referee pass on `T20_PROOF.md` (a reader who has seen none of the code) | CDX | after D1, D2 | - |
| D4 | Importer on the lab PC: `merged` records, DEFERRED verdicts and index lists, `producer_max_out` (accepted, condition producer.complete), fine blocks of 001; per-pair certificate (norms 7, orthogonality, root, Y = 5 or 4). The pairs stay DEFERRED in the lab tracker until T20 is closed | LAB | starts 12:00, in parallel with A (does not wait for T20) | importer run on two swept lattices (013, 016) with counts equal to `sweep_report.py` | 17:00 |
| D5 | Final statement: T18 + T20 + bridge + sweep records => the 156 envelopes are excluded, with the list of what it rests on (upstream reduction: "source only, not re-read") | LAB | after D1-D4 | - |

## E. Sweep (route C)

| Item | Owner | Status |
|---|---|---|
| All queue jobs except one: done (`q/tools/laptop_2026-10-06/sweep_report.py`) | LAP | closed |
| 003:181:182: running since 07:46 on 124 cores (i-00a0ab97a6a8099fd); stop at 13:00 if not back, then treated apart | LAP | running |

## Machines running (LAP keeps this current)

| Account | Machine | Job | Since |
|---|---|---|---|
| user | i-00a0ab97a6a8099fd, 128 vCPU, eu-north-1 | 003:181:182 | 07:46 |
| user | i-019e86d399c17954f, 128 vCPU, eu-west-2 | C3 | 11:19 |
| free | 5 x 8 vCPU | C2 | 11:10 |
