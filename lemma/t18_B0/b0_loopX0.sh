#!/bin/bash
# X_0-first route on all stage-B orbit representatives: one part (idx mod 2), successive processes of at most 540 s.
# usage: bash b0_loopX0.sh <part>
cd "$(dirname "$0")"
part=$1; r=1
while [ $r -le 8 ]; do
  n=$(python -c "
import json,glob
R=json.load(open('b0_stageB_reps.json')); done=set()
for f in glob.glob('b0_x0_done_*.jsonl'):
    for l in open(f):
        if l.strip(): done.add(json.loads(l)['idx'])
print(sum(1 for i in range(len(R)) if i % 2 == $part and i not in done))")
  echo "part $part round $r: $n left  $(date)" >> b0_loopX0_${part}.log
  if [ "$n" = "0" ]; then break; fi
  python b0_x0.py $part 2 540 x$r > b0_x0_x${r}_${part}.out 2> b0_x0_x${r}_${part}.err
  r=$((r+1))
done
echo "part $part finished $(date)" >> b0_loopX0_${part}.log
