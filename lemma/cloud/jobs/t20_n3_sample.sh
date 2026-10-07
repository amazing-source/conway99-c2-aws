#!/bin/bash
# T20, case I, branch n_3 = 2 (lab session, 07/10): MEASURE the cost of the bases that are not closed yet, before any long run.
# Start it with the branch of the last run as second argument of run.sh, so that the closed bases are restored and left out:
#   bash conway99-c2-aws/lemma/cloud/run.sh t20_n3_sample lemma-run/t20_n3-i-04bb3ac564f658b79
# For every remaining base (the 101 excluded by hand, isolation lemma of lemma/t20_CODEX/PROFILE_421.md, are left out):
# one task in N below level 2 with the engine eng5z (lemma/t20_HAND/n3_split.py sample). Outputs: sample.out (one line per base),
# sample/ESTIMATE.txt and .json (estimated nodes and core-hours per base and in total, with the method), SUMMARY_before.txt.
# Expected: 30 to 45 minutes on 8 cores. Nothing here closes a base.
OUT="$1"; NP="${NPROC:-1}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 N3_SKIP_LEMMA=1
cd lemma/t20_HAND || exit 1
$PY mk_eng5z.py > "$OUT/mk_eng5z.out" 2>&1 || exit 1
$PY n3_split.py summary "$OUT" > "$OUT/SUMMARY_before.txt" 2>&1
$PY n3_split.py sample "$OUT" "$NP" "${N3_SAMPLE_N:-300}" "${N3_SAMPLE_TLIM:-600}" > "$OUT/sample.out" 2>&1
