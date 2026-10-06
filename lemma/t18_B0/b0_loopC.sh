#!/bin/bash
# Relaunches stage C for one part (idx mod 2) in successive processes of at most 560 s each, until nothing is left.
# usage: bash b0_loopC.sh <part> <first round number>
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
part=$1; r=$2
while [ $r -le 12 ]; do
  n=$(python -c "
import json,glob
R=json.load(open('b0_stageB_reps.json')); done=set()
for f in glob.glob('b0_stageC_done_*.jsonl'):
    for l in open(f):
        if l.strip(): done.add(json.loads(l)['idx'])
print(sum(1 for i in range(len(R)) if i % 2 == $part and i not in done))")
  echo "part $part round $r: $n left  $(date)" >> b0_loopC_${part}.log
  if [ "$n" = "0" ]; then break; fi
  R3_CERTCAP=1000 B0_RUNTAG=r$r python b0_stageC2.py 0 $part 2 560 > b0_stageC_r${r}_${part}.out 2> b0_stageC_r${r}_${part}.err
  r=$((r+1))
done
echo "part $part finished $(date)" >> b0_loopC_${part}.log
