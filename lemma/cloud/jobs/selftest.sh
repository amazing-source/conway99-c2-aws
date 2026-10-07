#!/bin/bash
# Self-test of the compute box: imports, and the first seconds of a real enumeration (T20 III.0, part 0 of 3, 60 s time limit).
OUT="$1"
$PY -c "import numpy, flint, sys; print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'flint', flint.__version__)" > "$OUT/versions.txt" 2>&1
cd lemma/t20_R2 && $PY run_eng5.py III.0 0 3 60 3 "$OUT/selftest_III0" setwise > "$OUT/selftest_run.out" 2>&1
echo "nproc $NPROC" >> "$OUT/versions.txt"
