#!/bin/bash
# T20 round 3, case I (k = 0), n_3 = 0: ONE graph and ONE profile through the whole pipeline.
#   1. stage 1  (stage1c.py, N parts, then stage1_merge.py): the configurations of N(p) up to Aut(B), exact tests on
#               the 35 vertices S u N[p]  ->  <tag>/s1_<tag>.json ("bases")
#   2. stage 2  (run_stage2.py, N parts; engine eng6, model cases6): for every base, the orbits of X_2 outside N(p),
#               to exhaustion  ->  <tag>/parts/s2_<i>of<N>.jsonl, <tag>/stage2_<tag>.out (summary2.py: tiling, sha1,
#               time-outs, node counts, number of complete configurations)
#   3. second program (in_verify.py, shares no code with 1 and 2): own enumeration of the configurations of N(p)
#               ("bases", N parts) and re-traversal of every search tree of stage 2 ("follow", N parts)
#               ->  <tag>/verify_<tag>.out
# usage (from anywhere):  bash cloud_case.sh <out dir> <graph> <h2> <h1> <h0>      e.g.  ... out I.0 4 2 1
# environment: PY = python (numpy, python-flint); NPROC = number of processes (default 4);
#              T20_FIRST = K (optional, TEST ONLY: stage 2 and the re-traversal treat the first K bases of each part);
#              T20_SKIP_VERIFY = 1 (optional: stop after step 2).
mkdir -p "$1"
OUT="$(cd "$1" && pwd)"; G="$2"; H2="$3"; H1="$4"; H0="$5"
N="${NPROC:-4}"
PY="${PY:-python}"
TAG="${G/./}_$H2$H1$H0"
W="$OUT/$TAG"
mkdir -p "$W/parts" "$W/logs"
cd "$(dirname "$0")" || exit 1
FIRST=""
[ -n "$T20_FIRST" ] && FIRST="first=$T20_FIRST"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "start $(date -u +%H:%M:%S) graph $G profile ($H2,$H1,$H0) processes $N $FIRST" > "$W/timing.txt"

# ---- 1. stage 1
for ((p = 0; p < N; p++)); do
  $PY stage1c.py "$G" "$H2" "$H1" "$H0" "$W/parts/s1.part${p}of${N}.json" part=$p/$N > "$W/logs/s1_$p.out" 2>&1 &
done
wait
if ! $PY stage1_merge.py "$W/parts/s1" "$N" "$W/s1_$TAG.json" > "$W/stage1_$TAG.out" 2>&1; then
  echo "STAGE 1 FAILED" >> "$W/timing.txt"; exit 1
fi
rm -f "$W"/parts/s1.part*.json
echo "stage 1 done $(date -u +%H:%M:%S)" >> "$W/timing.txt"

# ---- 2. stage 2
for ((p = 0; p < N; p++)); do
  $PY run_stage2.py "$W/s1_$TAG.json" "$p" "$N" 400000 "$W/parts/s2" width=3 $FIRST > "$W/logs/s2_$p.out" 2>&1 &
done
wait
$PY summary2.py "$W/s1_$TAG.json" "$W/parts/s2" "$N" > "$W/stage2_$TAG.out" 2>&1
echo "stage 2 done $(date -u +%H:%M:%S)" >> "$W/timing.txt"
[ -n "$T20_SKIP_VERIFY" ] && exit 0

# ---- 3. second program
for ((p = 0; p < N; p++)); do
  $PY in_verify.py bases "$G" "$H2" "$H1" "$H0" "$W/parts/vb_${p}of${N}.json" part=$p/$N > "$W/logs/vb_$p.out" 2>&1 &
done
wait
echo "second program, stage 1 done $(date -u +%H:%M:%S)" >> "$W/timing.txt"
for ((p = 0; p < N; p++)); do
  $PY in_verify.py follow "$W/s1_$TAG.json" "$W/parts/s2" "$p" "$N" "$W/parts/vf_${p}of${N}.json" $FIRST > "$W/logs/vf_$p.out" 2>&1 &
done
wait
if $PY in_verify.py merge "$W/s1_$TAG.json" "$W/parts/vb" "$N" "$W/parts/vf" > "$W/verify_$TAG.out" 2>&1; then
  rm -f "$W"/parts/vb_*.json
fi
echo "second program done $(date -u +%H:%M:%S)" >> "$W/timing.txt"
cat "$W/stage1_$TAG.out" "$W/stage2_$TAG.out" "$W/verify_$TAG.out"
