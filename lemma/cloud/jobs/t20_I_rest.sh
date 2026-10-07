#!/bin/bash
# T20 round 3, case I (k = 0), n_3 = 0: the nine (graph, profile) cases not closed on the laptop, one after the other, smallest
# first, FIRST PROGRAM ONLY (stage 1 + stage 2; the second program is skipped: T20_SKIP_VERIFY=1). Each case uses $NPROC processes.
# Driver and description: lemma/t20_R3_I/cloud_case.sh. Outputs: $1/<graph>_<profile>/ (stage1_*.out, stage2_*.out, s1_*.json,
# parts/, logs/, timing.txt) and $1/ALL.txt (the stage summaries of every case, in order).
export T20_SKIP_VERIFY=1
for c in "I.5 3 4 0" "I.2 4 2 1" "I.2 3 4 0" "I.4 4 2 1" "I.3 4 2 1" "I.1 4 2 1" "I.4 3 4 0" "I.3 3 4 0" "I.1 3 4 0"; do
  set -- "$1" $c
  echo "=== $2 ($3,$4,$5) start $(date -u +%H:%M:%S)" >> "$1/ALL.txt"
  bash lemma/t20_R3_I/cloud_case.sh "$1" "$2" "$3" "$4" "$5" >> "$1/ALL.txt" 2>&1
  T="${2/./}_$3$4$5"; cat "$1/$T/stage1_$T.out" "$1/$T/stage2_$T.out" >> "$1/ALL.txt" 2>/dev/null
  echo "=== $2 ($3,$4,$5) end $(date -u +%H:%M:%S)" >> "$1/ALL.txt"
done
