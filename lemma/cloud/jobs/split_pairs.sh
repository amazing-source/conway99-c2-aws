#!/bin/bash
# Branch split of a few hard pairs with the lab's v1 split tool (q/tools/lab_2026-10-07/split_v1, engine scripts/frame_dfs.py of the
# package, unchanged). Run by lemma/cloud/run.sh:  SPLIT_PAIRS=<repo path of {"pairs": [[y1, y2], ...]}> SPLIT_LID=003 SPLIT_K=127
#   [SPLIT_LIMIT=0] [SPLIT_CHECK=<index of a pair to run also with K = 1, and with K = 8, for the comparison of the node counts>]
# Outputs in $1: parts/p<k>_r<r>.jsonl (one line per part: nodes per depth, complete, leaves, joint, frame), logs/, SUMMARY.txt.
# A pair is EXCLUDED when its K parts all have complete = true, frame = 0 and joint = 0 (README of the tool). Nothing is published
# to the queue; the conclusion is drawn from SUMMARY.txt by the session, not by this script.
OUT="$(cd "$1" && pwd)"; REPO="$(pwd)"; PY="${PY:-python3}"; N="${NPROC:-4}"
PAIRS="$REPO/${SPLIT_PAIRS:?SPLIT_PAIRS}"; LID="${SPLIT_LID:?SPLIT_LID}"; K="${SPLIT_K:-127}"; LIMIT="${SPLIT_LIMIT:-0}"
PKGD="$HOME/pkg_split"
[ -f "$PKGD/MANIFEST.json" ] || "$PY" -m zipfile -e "$REPO/c2_cloud_run.zip" "$PKGD"
"$PY" -m pip -q install -r "$PKGD/requirements.txt" > "$OUT/pip.log" 2>&1 || { echo "PIP FAILED" > "$OUT/SUMMARY.txt"; exit 1; }
cp "$REPO/q/tools/lab_2026-10-07/split_v1/frame_dfs_split.py" "$PKGD/scripts/"
U="$PKGD/external_runs/structures_3eceb4d/U/$LID.json"
mkdir -p "$OUT/parts" "$OUT/logs" "$OUT/check"
NP=$("$PY" -c "import json; print(len(json.load(open('$PAIRS'))['pairs']))")
echo "start $(date -u +%H:%M:%S) lattice $LID pairs $NP parts $K processes $N limit $LIMIT" > "$OUT/timing.txt"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 FD_LEMMA_U=1 FD_NODE_LIMIT="$LIMIT"
cd "$PKGD/scripts" || exit 1
# one warm-up call compiles the kernels once (numba cache), so the parallel parts do not all compile at the same time
FD_NODE_LIMIT=1000 "$PY" frame_dfs_split.py "$U" "$PAIRS" 0 "$K" 0 "$OUT/logs/warmup.jsonl" > "$OUT/logs/warmup.log" 2>&1
echo "warm-up done $(date -u +%H:%M:%S)" >> "$OUT/timing.txt"
{
  if [ -n "${SPLIT_CHECK:-}" ]; then
    echo "$SPLIT_CHECK 1 0 $OUT/check/K1"
    for r in 0 1 2 3 4 5 6 7; do echo "$SPLIT_CHECK 8 $r $OUT/check/K8"; done
  fi
  for ((k = 0; k < NP; k++)); do for ((r = 0; r < K; r++)); do echo "$k $K $r $OUT/parts/p$k"; done; done
} | xargs -P "$N" -L 1 bash -c '"$0" frame_dfs_split.py "$1" "$2" "$3" "$4" "$5" "$6_r$5.jsonl" > "$6_r$5.log" 2>&1' "$PY" "$U" "$PAIRS"
echo "parts done $(date -u +%H:%M:%S)" >> "$OUT/timing.txt"
"$PY" - "$OUT" "$NP" "$K" "${SPLIT_CHECK:-}" > "$OUT/SUMMARY.txt" 2>&1 <<'PYEOF'
import sys, json, glob, os
out, NP, K, chk = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]


def load(prefix, K):
    rows = {}
    for r in range(K):
        f = "%s_r%d.jsonl" % (prefix, r)
        if os.path.exists(f):
            L = [json.loads(l) for l in open(f) if l.strip()]
            if L: rows[r] = L[-1]
    return rows


def line(name, rows, K):
    nodes = None
    for d in rows.values():
        n = d.get("nodes") or []
        nodes = n if nodes is None else [a + b for a, b in zip(nodes, n)]
    comp = len(rows) == K and all(d.get("complete") is True for d in rows.values())
    fr = sum(int(d.get("frame") or 0) for d in rows.values()); jo = sum(int(d.get("joint") or 0) for d in rows.values())
    lv = sum(int(d.get("leaves") or 0) for d in rows.values())
    v = "EXCLUDED" if comp and fr == 0 and jo == 0 else "NOT EXCLUDED (look at it)" if comp else "INCOMPLETE"
    print("%s: parts %d of %d, all complete %s, leaves %d, joint %d, frame %d, nodes per depth %s  ->  %s" % (name, len(rows), K, comp, lv, jo, fr, nodes, v))
    return nodes


if chk != "":
    a = line("CHECK pair %s, K = 1" % chk, load(os.path.join(out, "check", "K1"), 1), 1)
    b = line("CHECK pair %s, K = 8" % chk, load(os.path.join(out, "check", "K8"), 8), 8)
    print("CHECK: summed node counts of the 8 parts equal to the unsplit run: %s" % (a is not None and a == b))
for k in range(NP):
    line("pair %d" % k, load(os.path.join(out, "parts", "p%d" % k), K), K)
PYEOF
cat "$OUT/SUMMARY.txt"
