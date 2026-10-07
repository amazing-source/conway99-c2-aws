#!/bin/bash
# T20 round 3, case I (k = 0), n_3 = 0: FULL pipeline (first program, then the second, independent program in_verify.py) for the
# cases of group E, one after the other, on $NPROC processes. Driver: lemma/t20_R3_I/cloud_case.sh. Outputs: $1/<graph>_<profile>/
# (stage1_*.out, stage2_*.out, verify_*.out, timing.txt, parts/, logs/) and $1/ALL.txt. Groups A-F cover the twelve cases.
for c in "I.5 3 4 0" "I.1 4 2 1"; do
  set -- "$1" $c
  echo "=== $2 ($3,$4,$5) start $(date -u +%H:%M:%S)" >> "$1/ALL.txt"
  bash lemma/t20_R3_I/cloud_case.sh "$1" "$2" "$3" "$4" "$5" >> "$1/ALL.txt" 2>&1
  echo "=== $2 ($3,$4,$5) end $(date -u +%H:%M:%S)" >> "$1/ALL.txt"
done
