#!/bin/bash
# Route (C), adaptive queue: bootstrap of ONE cloud machine (C2, 2026-10-01). The SAME line on every machine, any region:
#
#   git clone https://x-access-token:TOKEN@github.com/amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/q/qmachine.sh
#
# (or the user-data script of the README, which runs that line by itself at boot). Order of events:
#   1. dead-man switch armed FIRST (shutdown -h +60): a machine that never gets going powers itself off;
#   2. identity from the instance metadata; REFUS + immediate power-off if not c7a.8xlarge, not Spot, or region without a price;
#   3. status INSTALLATION pushed to run/q-<instance-id> (from now on the machine counts in the spend ledger);
#   4. package unzipped, environment installed, calibration job 118:2 computed and compared with the lab's reference:
#      anything but EQUIVALENT -> STOP CALIB + power-off (nothing is computed on a machine that differs from the lab);
#   5. the agent q/qagent.py runs the queue until the queue is empty, the cap is reached or the control says stop;
#   6. power-off (sudo shutdown -h now). With "Shutdown behavior: Terminate" the instance is deleted and billing ends.
# Q_TEST=1 (rehearsal only): no metadata, no power-off; identity from Q_TEST_NAME / Q_TEST_PRICE.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
if [ "${1:-}" != "--inner" ]; then
  [ -n "${Q_TEST:-}" ] || sudo shutdown -h +60 >/dev/null 2>&1
  nohup bash "$REPO/q/qmachine.sh" --inner > "$HOME/qmachine.log" 2>&1 &
  echo "OK: the machine installs, calibrates, then computes in the background. Follow it from the PC: python q/monitor_q.py"
  exit 0
fi

PKG="$HOME/c2_cloud_run"
off() { [ -n "${Q_TEST:-}" ] && { echo "TEST: would power off now"; exit "${1:-0}"; }; sudo shutdown -h now; exit "${1:-0}"; }
imds() {
  local tok; tok=$(curl -s -m 3 -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
  curl -s -m 3 -H "X-aws-ec2-metadata-token: $tok" "http://169.254.169.254/latest/meta-data/$1"
}
if [ -n "${Q_TEST:-}" ]; then
  IID="${Q_TEST_NAME:?Q_TEST_NAME}"; REGION=ci; AZ=ci; ITYPE=ci; LIFE=spot; PRICE="${Q_TEST_PRICE:-0.10}"
  BOOT=$(date +%s); W="${Q_WORKERS:-1}"
  export Q_RUNPREFIX="${Q_RUNPREFIX:-run/qci-}" Q_QUEUE="${Q_QUEUE:-queue-ci}"; NAME="qci-$IID"
else
  IID=$(imds instance-id); REGION=$(imds placement/region); AZ=$(imds placement/availability-zone)
  ITYPE=$(imds instance-type); LIFE=$(imds instance-life-cycle)
  PRICE=$(python3 -c "import json; p=json.load(open('$REPO/q/prices.json')); print(p.get('max_price_by_region_type', {}).get('$REGION', {}).get('$ITYPE') or p['max_price_usd_per_h'].get('$REGION', ''))")
  BOOT=$(( $(date +%s) - $(cut -d. -f1 /proc/uptime) ))
  W=$(( $(nproc) * 13 / 16 )); [ "$W" -ge 1 ] || W=1                          # 32 cores -> 26 jobs, exactly as before
  export Q_RUNPREFIX="run/q-" Q_QUEUE="queue"; NAME="q-$IID"
fi
OVH=$(python3 -c "import json; print(json.load(open('$REPO/q/prices.json'))['overhead_usd_per_h'])")
export Q_NAME="$NAME" Q_URL="${Q_URL:-$(git -C "$REPO" remote get-url origin)}" Q_PKG="$PKG" Q_REGION="$REGION" Q_AZ="$AZ" \
       Q_ITYPE="$ITYPE" Q_PRICE="${PRICE:-0}" Q_OVH="$OVH" Q_BOOT="$BOOT" Q_WORKERS="$W"
A="python3 $REPO/q/qagent.py"

if [ -z "${Q_TEST:-}" ]; then
  ALLOWED=$(python3 -c "import json; print(' '.join(json.load(open('$REPO/q/prices.json'))['instance_types']))")
  case " $ALLOWED " in *" $ITYPE "*) ;; *) $A status REFUS "instance type $ITYPE is not allowed ($ALLOWED)"; off 0;; esac
  [ "$LIFE" = "spot" ] || { $A status REFUS "not a Spot instance ($LIFE): far too expensive"; off 0; }
  [ -n "$PRICE" ] || { $A status REFUS "region $REGION has no max price in q/prices.json"; off 0; }
fi

$A status INSTALLATION "setup + calibration"
[ -f "$PKG/MANIFEST.json" ] || python3 -m zipfile -e "$REPO/c2_cloud_run.zip" "$PKG"
cd "$PKG" || { $A status "ERREUR INSTALLATION" "package not unpacked"; off 1; }
if ! bash setup_linux.sh "--only 118:2 --out calib" > setup.log 2>&1; then
  $A status "ERREUR INSTALLATION" "$(tail -3 setup.log | tr '\n' ' ')"; off 1
fi
if ! .venv/bin/python verify_equivalence.py calib/118_2_8.jsonl calib_reference/118_2_8.jsonl > calib_check.txt 2>&1; then
  $A status "STOP CALIB" "$(head -2 calib_check.txt | tr '\n' ' ')"; off 1
fi
if [ -f calib_extra.sh ]; then                                                   # package v2: second calibration (deep symmetry + twin rule)
  if ! bash calib_extra.sh > calib_extra_check.txt 2>&1; then
    $A status "STOP CALIB" "v2 calibration: $(tail -2 calib_extra_check.txt | tr '\n' ' ')"; off 1
  fi
fi
$A status INSTALLATION "calibration EQUIVALENT, starting the agent"
touch "$HOME/q_calibrated_$NAME"                                                 # used by the rehearsal only
.venv/bin/python "$REPO/q/qagent.py" run; RC=$?
[ "$RC" -eq 0 ] || $A status "ERREUR AGENT" "agent exit code $RC (see tail_agent.txt)"
off "$RC"
