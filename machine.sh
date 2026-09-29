#!/bin/bash
# Route (C) on ONE AWS machine (C2, 29/09/2026). In the home folder of a fresh Ubuntu machine:
#
#   git clone https://x-access-token:TOKEN@github.com/amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/machine.sh SLICE NAME
#   (example: bash conway99-c2-aws/machine.sh 5/18 toi-francfort)
#
# The command returns at once: installation, calibration and the computation go on in the background (the window can be closed).
# Every 10 minutes the machine pushes its state (status.txt) and its finished results (results/*.jsonl) to the branch run/NAME.
# Re-running the same command on a NEW machine resumes the slice: the results already on the branch are restored, finished
# jobs are skipped.
set -u
SLICE="${1:?tranche, ex. 5/18}"; NAME="${2:?nom de machine, ex. toi-francfort}"
REPO="$(cd "$(dirname "$0")" && pwd)"
if [ "${3:-}" != "--inner" ]; then
  nohup bash "$REPO/machine.sh" "$SLICE" "$NAME" --inner > "$HOME/machine_$NAME.log" 2>&1 &
  echo "OK : $NAME (tranche $SLICE) s'installe puis calcule en arriere-plan. Tu peux fermer cette fenetre."
  echo "Suivi depuis ton PC : python monitor_git.py (etat envoye sur GitHub toutes les 10 minutes)."
  exit 0
fi
PKG="$HOME/c2_cloud_run"; PUSH="$HOME/push_$NAME"; BR="run/$NAME"
URL="${C2_PUSH_URL:-$(git -C "$REPO" remote get-url origin)}"
EVERY="${C2_EVERY:-600}"; ONLY="${C2_ONLY:-}"                              # C2_ONLY / C2_EVERY: tests only
W="${C2_WORKERS:-$(( $(nproc) * 13 / 16 ))}"; [ "$W" -ge 1 ] || W=1          # 32 cores -> 26 jobs (a job = consumer + producer)
mkdir -p "$PUSH" && cd "$PUSH" && git init -q
git config user.name amazing-source; git config user.email 206353265+amazing-source@users.noreply.github.com
git remote remove origin 2>/dev/null; git remote add origin "$URL"
if git fetch -q origin "$BR" 2>/dev/null; then git reset -q --hard FETCH_HEAD; fi   # resume: previous results of this slice
push() (                                                  # subshell: never changes the caller's folder
  cd "$PUSH"
  { echo "STATE=$1"; echo "NAME=$NAME"; echo "SLICE=$SLICE"; bash "$REPO/probe.sh" "$PKG"; } > status.txt
  mkdir -p results; cp "$PKG"/results/*.jsonl results/ 2>/dev/null
  for f in results/run_jobs.log run.out setup.log; do [ -f "$PKG/$f" ] && tail -40 "$PKG/$f" > "tail_$(basename "$f").txt"; done
  git add -A >/dev/null 2>&1
  git commit -qm "$NAME $1 $(date -u +%FT%TZ)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1
  for i in 1 2 3; do git push -qf origin "HEAD:refs/heads/$BR" && exit 0; sleep 20; done
)
push INSTALLATION
cd "$HOME"
[ -f "$PKG/MANIFEST.json" ] || python3 -m zipfile -e "$REPO/c2_cloud_run.zip" "$PKG"
mkdir -p "$PKG/results"; cp "$PUSH"/results/*.jsonl "$PKG/results/" 2>/dev/null   # restore finished jobs (resume)
cd "$PKG"
if ! bash setup_linux.sh "--only 118:2 --out calib" > setup.log 2>&1; then push "ERREUR INSTALLATION"; exit 1; fi
if ! .venv/bin/python verify_equivalence.py calib/118_2_8.jsonl calib_reference/118_2_8.jsonl | grep -q "^EQUIVALENT"; then
  push "STOP CALIB"; exit 1
fi
if [ -n "$ONLY" ]; then ARGS="--only $ONLY"; else ARGS="--slice $SLICE"; fi
nohup .venv/bin/python run_jobs.py $ARGS --workers "$W" --out results > run.out 2>&1 &
RUNPID=$!
sleep 30
while kill -0 "$RUNPID" 2>/dev/null; do push EN_COURS; sleep "$EVERY"; done
if grep -q "all jobs finished" "$PKG/results/run_jobs.log" 2>/dev/null; then push FINI; else push ERREUR; fi
