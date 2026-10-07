#!/usr/bin/env bash
set -euo pipefail
: "${PY:?Set PY to the Python executable}"
: "${NPROC:?Set NPROC to the worker count}"
OUT=${1:?Give an output directory}
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
LEMMA=$(cd -- "$HERE/../.." && pwd)
PROGRAM="$LEMMA/t20_CODEX/n3_second"
mkdir -p -- "$OUT"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" "$PROGRAM/bases.py" --output "$OUT/bases.json"
"$PY" "$PROGRAM/run.py" --manifest "$OUT/bases.json" --output "$OUT/results" --workers "$NPROC"
