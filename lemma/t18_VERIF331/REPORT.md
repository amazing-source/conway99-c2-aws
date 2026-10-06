# T18, profile (3,3,1): independent re-verification

Agent report of 2026-10-06, saved by the main session. Notation of `lemma/t18/T18_REPORT.md`.
No solver: backtracking, integer matrix products, exact positive-semidefiniteness decisions. Files: this folder
(`v5_summary.out`, `v4_compare.out`, `v6_m1_final.out`, `v7_step4_*.out`).

## Verdict: agrees

The independent enumeration finds 0 configurations on 51 vertices for B2, B1 and B0, and matches every well-defined count of the
first implementation. One caveat for the proof text: the result needs a second matrix, not only 9(3I - A) + J.

| Stage | B2 here / report | B1 here / report | B0 here / report |
|---|---|---|---|
| Matchings / orbits | 9229 / 528, same | 13799 / 1259, same | 25514 / 425, same |
| Survivors, 39 vertices | 7 / 7 | 481 / 481 | 383 / 383 |
| Tables passing budgets, 45 vertices | 0 / 0 | 27203 / 27203 | 8639 / 8639 |
| Tables passing budgets + PSD, 45 vertices | 0 / 0 | 164 / 164 | 23 / 23 |
| Survivors, 51 vertices | 0 / 0 | 0 / 0 | 0 / 0 |

- Sets: the 39-vertex survivors and the 45-vertex tables are identical to the first implementation's stored ones, as multisets of
  canonical forms under Aut(B).
- **Second matrix.** The report's counts are reproduced only when M2 = 11(4I + A) - 2J (= 77 E_3, valid) is tested alongside
  9(3I - A) + J. With 9(3I - A) + J alone, B1 keeps 10 configurations on 51 vertices (672 at 39, 190 at 45); B0 and B2 still end at 0.
- Hand checks: A8, A9, A10 are correct. A9 does not need the computed fact from A6: the hand argument gives
  2 h_3 + 4 h_0 + n_3 <= 4 directly.
- Not reproduced: the "completions C" counter (a different object in the two programs), the report's step-4 node counters, and
  test (i'), which could not be identified.

## Independence

- Read: the lemma note, rounds 1-2 of `T18_REPORT.md`, the Wagner dossier. No `.py` of `t18/` was opened.
- Output files of `t18/` (`r2_hfirst_*.json`, `r2_stage2_*surv*.json`, `r2_summary_1.out`, `r2_diag.out`) were read only after all
  counts existed, for the set comparison.

## Hand re-derivations

- **A8:** counting paths from z to S+ gives the sum over outside neighbours of d(w) = 18 - 5d, hence d <= 3 and
  a_0 = a_2 + 2 a_3 + 3d - 4. The identity (*) also checks out; the programs record it but never prune with it.
- **A9:** with omega = a_2 + 2 a_3, the sum over N(p) is 36 - 2 n_3 - 2 h_2 - 4 h_3. Lower bounds: omega >= 2 (X_3, mate),
  >= 1 (X_2), >= 2 (X_1), >= 6 (X_0). This gives 2 h_3 + 4 h_0 + n_3 <= 4, so h_0 = 1 forces h_3 = 0, n_3 = 0 and profile (3,3,1)
  by hand alone.
- **A10:** equality gives a_2 = 1 on A_p, a_2 = 2 and a_0 = 1 on W, a_2 = 6 and a_0 = 2 on z_0. X_2 splits as
  A_p + A_{z_0} + sigma A_{z_0}, and each of the six other X_0 vertices sees exactly 2 vertices of A_p and nothing in
  W u {z_0, sigma z_0}.
- **Determined sets:** the 39-, 45- and 51-vertex sets are fully determined by the listed data. In particular every vertex of X_2
  outside A_p has exactly one neighbour in W and deg_H + 1 neighbours among the six other X_0 vertices.

## How this implementation differs from the first

- Stage 1 (`v1_stage1.py`): test (i) plus cell budgets only. The 21-vertex PSD test removes nothing; all three graphs give 99
  admissible rectangles, 63 of them usable inside N(p).
- Stage 2 (`v2_stage2.py`): the six X_2 orbits outside N(p) are added one at a time, each with its side relative to z_0 and its
  H-edges to earlier orbits. A_{z_0} is therefore chosen before H is complete, the reverse of the first implementation.
- Stages 3-4 (`v3_stage34.py`): from each 39-vertex survivor both the X_0 extensions and the W extensions are built separately,
  then combined on 51 vertices. The W-first order is not in the first implementation.
- Direct step 4 (`v7_step4_direct.py`): every W completion of every surviving 45-vertex table, with budgets only as a pre-filter,
  then exact PSD.
- Exactness (`vcommon.py`): a PSD rejection is an integer vector with negative form re-evaluated in Python integers, or the exact
  characteristic polynomial (python-flint) with a sign test. Acceptances at 39, 45 and 51 vertices use the exact characteristic
  polynomial.

## Additional counts

| | B2 | B1 | B0 |
|---|---|---|---|
| (tau, F) passing budgets on S u {p} u A_p, here / report | 2406 / 2406 | 7224 / 7224 | 3510 / 3510 |
| 39-vertex survivors: matchings, (tau, F) pairs (same as report) | 1, 1 | 55, 76 | 50, 95 |
| 39-vertex survivors with 9(3I - A) + J only | 7 | 672 | 887 |
| "Completions C", here / report | 88 / 44 | 45362 / 93684 | 11797 / 23155 |
| 45-vertex tables with 9(3I - A) + J only | 0 | 190 | 102 |
| W-first order: tables on the 39 vertices plus W, both matrices | 0 | 2 | 0 |
| Direct step 4: budget-valid 51-vertex graphs, of which PSD | - | 1839, 0 | 52, 0 |
| 51-vertex survivors with 9(3I - A) + J only | 0 | 10 | 0 |

- The 164 and 23 tables lie in 9 matchings each, as in the report.
- The "completions C" numbers differ because the first program counts C before H is fixed; this one counts C per 39-vertex
  configuration.
- In the direct step 4, the per-table counts of budget-valid graphs include 39, 39, 39, 0, 0, 0 (B1) and 12, 12, 2 (B0), the values
  quoted from the report's brute-force check.
- For B0 and B2 the W-first order already ends at 45 vertices, so X_0 beyond {p, z_0, sigma z_0} is not needed there.
- Running stages 3-4 a second way (PSD also on single rows of C) gives 164 and 23 again.

## The B1 configurations that need the second matrix

- All 10 lie in one matching orbit (index 1256 here), with F = [0,2,8] or [1,3,5] and t = 3 (no H-edges outside A_p).
- Each passes every budget on 51 vertices and 9(3I - A) + J is exactly PSD there.
- Each is rejected by M2 with an explicit integer vector (form values -88, -594 or -726). For 8 of them M2 already fails on the
  39 vertices plus W; for 2 it fails only on the full 51.
- In the direct step 4, 1829 of the 1839 graphs fall to 9(3I - A) + J and exactly these 10 to M2 only.
- At 39 vertices, 191 (B1) and 504 (B0) configurations are rejected by M2 only. So the sentence of A11 that "the violated matrix is
  9(3I - A) + J" does not hold for all rejections.
- The first implementation evidently tests both matrices, since its counts match the two-matrix mode exactly; this was not
  confirmed in its code.

## Coverage

- Every run in the tables completed without a time-out; the first, too-slow attempt at stage 3 is kept in `partial_first_run/` and
  is superseded. Longest run 335 s, at most 2 heavy processes at a time.
- Not re-verified here: the round-1 reduction to B0, B1, B2, and anything about profile (2,5,0).
