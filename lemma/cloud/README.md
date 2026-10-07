# Compute box for the lemma work

`run.sh <job>` turns an EC2 machine into a one-shot runner for `jobs/<job>.sh`: see the header of `run.sh`. Results arrive on the
branch `lemma-run/<job>-<instance id>` (STATUS.txt, job.log, and whatever the job wrote in its output folder), every 10 minutes
while it runs. The machine powers itself off at the end, or after 12 hours.

A job script is run from the repository root with: `$1` = output folder, `$PY` = python with numpy and python-flint, `$NPROC` =
number of cores. It should start its parts in the background with `$PY`, `wait`, and write everything under `$1`.
The user data that starts a box holds the deploy key and is not in git; the laptop session launches the machines.
