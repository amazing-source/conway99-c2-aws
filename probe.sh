#!/bin/bash
# Prints the state of the route-(C) run in the package folder $1 as KEY=VALUE lines (read by monitor_git.py).
D="${1:-$HOME/c2_cloud_run}"
cd "$D" 2>/dev/null || { echo "ERR=paquet pas encore decompresse"; exit 0; }
L=results/run_jobs.log
echo "LAST=$(tail -1 $L 2>/dev/null)"
echo "START=$(grep -m1 ' start:' $L 2>/dev/null | cut -c1-19)"
echo "STARTJOBS=$(grep -m1 ' start:' $L 2>/dev/null | sed -n 's/.* start: \([0-9]*\) jobs.*/\1/p')"
echo "FIN=$(grep -c 'all jobs finished' $L 2>/dev/null)"
echo "BADJOBS=$(grep 'done in' $L 2>/dev/null | grep -vc 'producer 0 consumer 0')"
echo "ERRLOG=$(grep -m1 -E 'Traceback|MANIFEST MISMATCH|No space|MemoryError|Killed' run.out 2>/dev/null | cut -c1-110)"
echo "CALIB=$(test -f calib/118_2_8.jsonl && .venv/bin/python verify_equivalence.py calib/118_2_8.jsonl calib_reference/118_2_8.jsonl 2>/dev/null | head -1 | cut -c1-10)"
echo "PROCS=$(pgrep -fc hstage_stream.py 2>/dev/null)"
echo "NPROC=$(nproc 2>/dev/null)"
echo "LOAD=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null)"
echo "MEMFREE=$(free -g 2>/dev/null | awk '/Mem:/{print $7}')"
echo "DISK=$(df -h . 2>/dev/null | awk 'NR==2{print $4}')"
echo "NOW=$(date '+%Y-%m-%d %H:%M:%S')"
