# T20, configuration III.1 (k = 4, two triangles): enumeration completed on 07/10

Run on the laptop with the round-2 engine `lemma/t20_R2/eng5.py` (`run_eng5.py III.1 <i> 8 80000 3 e5_III1 setwise plan certs=2500`,
i = 0..7, `OPENBLAS_NUM_THREADS=1`), summary by `summary_parts.py e5_III1 8` in `summary_III1.out`:

- 8 parts, no time-out, 21,165 tasks at depth 3 in every part, same sha1 of the ordered task list in all parts;
- 1,628,864 nodes; 75,949,406 candidates; 17,487,147 rejected by budgets, 56,833,395 by a positive-semidefiniteness certificate,
  1 by the rank bound (at level 9);
- **0 complete configurations.**

Status: **one implementation**. The per-part logs, plan files (the unit chosen at each node, needed by the independent verifier)
and the sampled certificates are in the session scratchpad `t20_III1\` (not in git: too large). To count as excluded, III.1 needs
the independent verifier (`engv.py` / `engv2.py` of round 2, validated on III.0 first) and a re-check of the saved certificates.
