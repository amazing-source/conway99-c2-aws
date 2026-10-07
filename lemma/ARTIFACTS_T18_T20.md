# Where every computation cited by T16, T18 and T20 lives (provenance table, 2026-10-07)

Answer to reserve G1 of `lemma/t20_CODEX/REFEREE_T20_PROOF.md`. One line per computation: the programs (with the git blob id of the
version that ran), where the outputs are (a path on `master`, or a branch with its commit), the line to read at the end, and the
second program. Blob ids are `git rev-parse <commit>:<path>` (first ten characters): they identify file contents.
The proof texts keep their own appendices with the commands (`T18_PROOF.md` Appendix A, `T20_PROOF.md` Appendix A); this page adds
what they lacked: the run branches, the program versions, and the archive of the outputs that were only on one laptop.

## T18 and T16

| Computation | Programs and outputs | Second program |
|---|---|---|
| T18, Computations 5.x to 8.8 | `lemma/T18_PROOF.md` Appendix A.1 to A.7: folders `lemma/t18`, `t18_B0`, `t18_B0_VERIFC`, `t18_B2`, `t18_N3`, `t18_STRUCT`, `t18_VERIF331`, `t18_REFEREE`, `t18_REFEREE2`, all on `master` with their outputs | every computation re-done by at least three programs, one written from the text alone (the two referee folders) |
| T16 (dual minimum > 8/7 becomes >= 9/7) | `lemma/T16_PROOF.md`, folder `lemma/t16` (the dossier of 04/10 as received, the lab's check, the independent enumeration) | referee pass `lemma/t20_CODEX/REFEREE_T16_PROOF.md`: one defect in the dossier's verifier (`check_B` did not test W <= set(V)); with the test added the 32 witnesses and the 240 obstructions pass again |

## T20

Program versions of `lemma/t20_R3_I` (case I). "v1" = commit 6471b9d64 (07/10, 10:35 UTC), "v2" = ea16eb42b (11:18 UTC: the
second program closes by its own search the nodes the first rejected by the rank bound), "v3" = 99eb1fb50 (13:52 UTC: the `z=`
branch for n_3 = 2; the n_3 = 0 behaviour is unchanged, regression in `T20_PROOF.md` 9.B.6).

| File | v1 | v2 | v3 |
|---|---|---|---|
| `stage1c.py` | 1fc255c3d1 | 1fc255c3d1 | 78cff2c820 |
| `stage1_merge.py` | 8054146192 | 8054146192 | 3fa9647377 |
| `cases6.py` | 43a5d7e8a6 | 43a5d7e8a6 | 43a5d7e8a6 |
| `eng6.py` | 849cba6598 | cb7d0996f5 | cb7d0996f5 |
| `run_stage2.py` | 0c9aef9353 | 0c9aef9353 | 0c9aef9353 |
| `summary2.py` | d68aea1da9 | d68aea1da9 | d68aea1da9 |
| `in_verify.py` (second program) | bc657c2bad | a1e9b479f4 | 373dd5ae20 |
| `cloud_case.sh` | 97fb860b0b | 97fb860b0b | 97fb860b0b |

A cloud run clones `master` when its machine starts, so its version is the one of its launch time (column "version").
Each run of `cloud_case.sh` executes the first program AND the second program on its case, so one branch holds both.

| Computation of `T20_PROOF.md` | Case | Outputs: branch (commit) or path | Version | Line to read |
|---|---|---|---|---|
| 4.12 support structures (nine configurations) | all | `lemma/t20/` on master (645201b5b) | - | Appendix A.1; two programs (enumerator and verifier) |
| 7.4 | III.0 | `lemma/t20_R2/` on master (715802e33): `summary_III0.out` | - | A.2; two engines, identical counters |
| 7.5 | III.1 | `lemma/t20_III1/` on master (dff2a08f5): `summary_III1.out`, `e5_III1_{0..7}of8.json`, `VERIF.md` | - | A.3; second verification with shared components (stated in `VERIF.md`) |
| 8.8, 8.9 | IIa.0 | `lemma/t20_R2/` on master | - | A.4; two independent programs |
| 9.19, 9.20 | I.1 (3,4,0) | `lemma-run/t20_I1_340-i-019e86d399c17954f` (c3d6dba726) | v1 | `ALL.txt`: "STAGE 1 AGREES: True", "STAGE 2 AGREES AT EVERY NODE, 0 complete, all bases: True" |
| 9.19, 9.20, first program alone | the nine cases of the first cloud run | `lemma-run/t20_I_rest-i-02f356c70da99d700` (937323d571) | v1 | `ALL.txt`, per case `stage1_*.out`, `stage2_*.out` |
| 9.19, 9.20 | I.3 (3,4,0), I.0 (3,4,0) | `lemma-run/t20_Iv_B-i-0a03ce79bff09fa5d` (2950e59c8a) | v1 | as above, per case |
| 9.19, 9.20 | I.4 (3,4,0), I.3 (4,2,1) | `lemma-run/t20_Iv_C-i-092f5550d84f61e09` (531fb79b3d) | v1 | as above |
| 9.19, 9.20 | I.2 (3,4,0), I.4 (4,2,1) | `lemma-run/t20_Iv_D-i-09169834049067883` (685659ca90) | v1 | as above |
| 9.19, 9.20 | I.5 (3,4,0) | `lemma-run/t20_Iv_E-i-0cd9427b48ee5704e` (ab8e27e6d0) | v1 | `ALL.txt` up to "=== I.5 (3,4,0) end"; the machine was reclaimed during its next case, which is not used |
| 9.19, 9.20 | I.1 (4,2,1) | `lemma-run/t20_Iv_G-i-05703a74fbb027423` (f7ea733d70) | v2 | as above; 1,406,917 nodes; the 2 rank nodes closed by the second program's own search |
| 9.19, 9.20 | I.2 (4,2,1) | `lemma-run/t20_Iv_H-i-004334efafb6ceb56` (951b8ff5e1) | v2 | as above |
| 9.19, 9.20 | I.0 (4,2,1) | `lemma-run/t20_Iv_I-i-032b7d25d335204f8` (bb1d5b5e00) | v2 | as above |
| 9.19, 9.20 | I.5 (4,2,1) | `lemma-run/t20_Iv_J-i-038ea54927e5a01c4` (e1f3c52bee) | v2 | as above |
| 9.29 (n_3 = 2, route B) | the 50 cases | summaries on master in `lemma/t20_R3_I/`: `n3_check.out`, `n3_table.out`, `n3_verify.out`, `n3_stage1_regen_compare.out`; raw outputs (stage 1 lists, stage 2 plans, second program): branch `lemma-archive/t20_n3_routeB` (b960cd136b) | v3 | last two lines of `n3_verify.out`: "TOTAL: cases 50, agreeing on both stages 50 ...", "ALL 50 CASES: SAME CLASSES OF BASES, SAME KEPT COUNT AT EVERY NODE, 0 COMPLETE: True" |

Not used by the proof and kept only as records: `lemma-run/t20_Iv_F-*` (reclaimed before any result), `lemma-run/t20_n3-*` and
`lemma-run/t20_n3_sample-*` (route A, stopped), `lemma/cloud/jobs/split_pairs.sh` (never run).

## What this page does not certify

- The run branches are copies pushed by the machines as they worked; nobody recomputed their contents after the fact, except where
  a second program did (column "Line to read").
- The versions are inferred from the launch times and the history of `master`; the machines did not record the commit they cloned.
- III.1 has a second verification that shares the model file and part of the enumeration skeleton with the first program.
