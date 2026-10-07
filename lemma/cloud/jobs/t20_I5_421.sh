#!/bin/bash
# T20 round 3, case I (k = 0), n_3 = 0: graph I.5, profile (4,2,1).  Stage 1 (configurations of N(p) up to Aut(B)),
# stage 2 (orbits of X_2 outside N(p), to exhaustion) and the second program, each in $NPROC parts that tile the task list.
# Driver and description: lemma/t20_R3_I/cloud_case.sh.  Outputs: $1/I5_421/ (stage1_*.out, stage2_*.out, verify_*.out,
# s1_*.json, parts/*.jsonl, logs/).
bash lemma/t20_R3_I/cloud_case.sh "$1" I.5 4 2 1
