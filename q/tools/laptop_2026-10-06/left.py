"""print the number of queue jobs not yet done for the given lattice ids (read-only)"""
import sys, json, subprocess
REPO = sys.argv[1]; lids = set(sys.argv[2:])
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
g("fetch", "-q", "origin", "+refs/heads/queue:refs/remotes/origin/queue")
done = {j for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip() for e in [json.loads(l)] if e["op"] == "done" for j in e["jobs"]}
print(sum(1 for j in g("show", "origin/queue:order.txt").split() if j.split(":")[0] in lids and j not in done))
