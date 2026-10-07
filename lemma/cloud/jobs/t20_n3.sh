#!/bin/bash
# T20, case I, branch n_3 = 2 (lab session, 07/10): the engine eng5z on every base S u {p} u X_3 u X_0' of the six graphs
# (lemma/t20_HAND/n3_cases.py: 44 + 227 + 87 + 121 + 146 + 75 = 700 classes of bases), all twelve orbits of X_2 placed by the engine.
# $NPROC processes, shared between the graphs in proportion to their number of bases; each process treats its bases one after the
# other (index % nparts == part), one JSON per base. Time limit per base: $T20_N3_TLIM seconds (default 4 hours).
# A base is closed when its JSON has "timeout": false and no survivor. The summary is written at the end.
OUT="$1"; TLIM="${T20_N3_TLIM:-14400}"; NP="${NPROC:-1}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd lemma/t20_HAND || exit 1
$PY mk_eng5z.py > "$OUT/mk_eng5z.out" 2>&1 || exit 1
$PY - "$NP" > "$OUT/shares.txt" <<'PYEOF'
import sys
n = int(sys.argv[1]); bases = {"I.0": 44, "I.1": 227, "I.2": 87, "I.3": 121, "I.4": 146, "I.5": 75}; tot = sum(bases.values())
sh = {g: max(1, n * b // tot) for g, b in bases.items()}
while sum(sh.values()) < n:                       # give the spare processes to the graphs with the most bases per process
    g = max(bases, key=lambda g: bases[g] / sh[g]); sh[g] += 1
for g in bases: print(g, min(sh[g], bases[g]))
PYEOF
while read -r G K; do
  mkdir -p "$OUT/$G"
  for ((i = 0; i < K; i++)); do
    $PY run_n3.py "$G" "$i" "$K" "$TLIM" "$OUT/$G" > "$OUT/$G/part_${i}of${K}.out" 2>&1 &
  done
done < "$OUT/shares.txt"
wait
$PY summary_n3.py "$OUT" > "$OUT/SUMMARY_n3.txt" 2>&1
