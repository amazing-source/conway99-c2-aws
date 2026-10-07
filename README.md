# Raw outputs of Computation 9.29 of lemma/T20_PROOF.md (T20, case I, n_3 = 2, route B), laptop session, 2026-10-07

Copy as produced, deposited so that the files cited by the proof text exist outside one laptop. Not a certified archive.

- `s1z/`: stage 1 of the first program (`stage1c.py` with `z=`, `stage1_merge.py`): the kept bases of the 50 cases.
- `s2z/`: stage 2 of the first program (`run_stage2.py`, engine `eng6.py`, model `cases6.py`): one jsonl per case with the search plans.
- `vz/`: the second program (`in_verify.py`, modes `basesz`, `follow`, `mergez`): its own classes of bases and its re-traversal.

The programs are in `lemma/t20_R3_I/` on master; the summaries read from these files are `n3_check.out`, `n3_table.out` and
`n3_verify.out` there. `python n3_all.py <out> <workers> both 340 421` regenerates everything.
