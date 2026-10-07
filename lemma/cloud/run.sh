#!/bin/bash
# Generic compute box for the lemma work (C2 laptop session, 2026-10-07). Started from the EC2 user data, as user ubuntu:
#   cd ~ && git clone git@github.com:amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/lemma/cloud/run.sh <job>
# It installs a venv (numpy, python-flint), runs lemma/cloud/jobs/<job>.sh <out dir> from the repository root, pushes the output
# folder to the branch lemma-run/<job>-<instance id> every 10 minutes and at the end, then powers the machine off
# ("Shutdown behavior: terminate"). Dead-man switch: powers off after LEMMA_MAX_HOURS (default 12) whatever happens.
# A job script gets: $1 = output folder, $PY = the venv python, $NPROC = number of cores; BLAS is single-threaded.
# Optional second argument: a branch lemma-run/... of an interrupted run of the same job; its files are copied into the output
# folder before the job starts, so that a job which skips finished pieces resumes instead of starting again.
JOB="${1:?job name}"; RESTORE="${2:-}"; REPO="$HOME/conway99-c2-aws"; OUT="$HOME/lemma_out"; mkdir -p "$OUT"
if [ -n "$RESTORE" ] && git -C "$REPO" fetch -q origin "refs/heads/$RESTORE"; then
  git -C "$REPO" archive FETCH_HEAD | tar -x -C "$OUT"; rm -f "$OUT/STATUS.txt"; mv "$OUT/job.log" "$OUT/job_before_restore.log" 2>/dev/null
fi
sudo shutdown -h +$(( ${LEMMA_MAX_HOURS:-12} * 60 )) >/dev/null 2>&1
TOK=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')
IID=$(curl -s -H "X-aws-ec2-metadata-token: $TOK" http://169.254.169.254/latest/meta-data/instance-id); IID=${IID:-unknown}
BR="lemma-run/$JOB-$IID"
push() {                                     # the whole output folder, files over 40 MB left out, forced push to the run branch
  rm -rf "$HOME/lemma_push"; mkdir -p "$HOME/lemma_push"; cd "$HOME/lemma_push" || return
  git init -q; git remote add origin "$(git -C "$REPO" remote get-url origin)"
  git config user.name amazing-source; git config user.email 206353265+amazing-source@users.noreply.github.com
  (cd "$OUT" && find . -type f -size -40M -print0 | cpio -0pdm --quiet "$HOME/lemma_push") 2>/dev/null
  echo "$1 $(date -u +%Y-%m-%dT%H:%M:%SZ) job=$JOB instance=$IID nproc=$(nproc)" > STATUS.txt
  git add -A >/dev/null 2>&1; git commit -qm "lemma run $JOB on $IID: $1" >/dev/null 2>&1
  git push -q -f origin HEAD:refs/heads/"$BR" >/dev/null 2>&1
}
push "INSTALLING"
{ sudo apt-get update -qq; sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv python3-pip cpio; } > "$OUT/install.log" 2>&1
python3 -m venv "$HOME/venv" >> "$OUT/install.log" 2>&1 && "$HOME/venv/bin/pip" -q install numpy python-flint >> "$OUT/install.log" 2>&1
export PY="$HOME/venv/bin/python" NPROC="$(nproc)" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
if ! "$PY" -c "import numpy, flint" >> "$OUT/install.log" 2>&1; then push "INSTALL FAILED"; sudo shutdown -h now; exit 1; fi
( while true; do sleep 600; push "RUNNING"; done ) &
LOOP=$!
( cd "$REPO" && bash "lemma/cloud/jobs/$JOB.sh" "$OUT" ) > "$OUT/job.log" 2>&1; RC=$?
kill $LOOP 2>/dev/null
push "FINISHED exit=$RC"
sudo shutdown -h now
