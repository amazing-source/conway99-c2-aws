# T20, configuration III.1: independent verification (07/10, 11:35 - 13:47 local)

Agent report, saved by the main session. Files: `RESULT_III1_VERIF.out` (start here), `summary_verif_III1.out`,
`rank_node_III1.out`, `validation_engv2_III0.out`, `runs_table.out`; the rest is in the session scratchpad `t20_III1_VERIF\`.

**Result: complete, agrees with the first program, 0 complete configurations.**
- Nodes re-traversed: 1,628,864, per level 1, 13, 208, 2156, 21165, 132172, 492124, 764789, 211921, 4315, 0, identical to
  `eng5`. No time-out, all 21,165 tasks done, 0 plan lines left unread. The kept count is equal at every node (asserted per node).
- The one node `eng5` rejected by the rank test (part 3 of 8, plan line 131167, 47 vertices) is reached and rejected by the
  verifier's own exact rank test: odd part of M1 (23 x 23) of rank 23 (flint, Fractions, two primes; determinant
  17,341,031,120,896), even part (24 x 24) of rank 23. The node has no budget violation and is exactly PSD on all four blocks.
  **It is also dead without the rank bound**: for unit (3,4) all 126 candidates are rejected, 112 by budgets and 14 by PSD
  certificates re-evaluated in Python integers. III.1 therefore does not depend on the rank lemma.
- Certificates: 20,000 checked with `check_certs.py`, 0 invalid.

**Verifier.** `engv2.py`, unmodified, with the `setwise` flag as in the `eng5` run. Validation: on the whole of III.0 (3 parts,
130,004 nodes) every result field is identical to the validated `engv.py` outputs; on III.1 parts 0, 1 and 43 of 48, `engv.py`
itself gives the same fields as `engv2` (including the rank node). Negative controls: a plan with one kept count changed, and one
with a line deleted, both stop the verifier with an AssertionError.

**One difference to know.** The verifier's candidate counts differ from the plan (55,844,478 candidates tested against 75,949,406
for `eng5`) because `engv` / `engv2` pre-filter pairs with an exact PSD test and `eng5` with budgets only; only nodes and kept
tables are comparable. With that pre-filter switched off (part 2 of 48): 0 candidate mismatches.

**Not checked.** `cases.py`, the group and the first part of candidate generation (loops, X_0 caps, symmetry rule) are the same
lines in `eng5.py` and `engv.py`: independence covers the budget and PSD tests and the bookkeeping, not the model or the
enumeration skeleton. The setwise symmetry rule rests on a hand argument. Only counts of kept children are compared, not the
configurations. A full pass with `engv.py` itself was run on 3 of the 48 parts only.

**Laptop note.** Windows power-throttles windowless background processes (about 0.3 core each); the agent opted its own worker
processes out, per process and not persistently (`boost.py` in its scratch folder), and each then got about 0.97 core.
