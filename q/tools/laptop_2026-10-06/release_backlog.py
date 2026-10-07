"""Release, on behalf of a LIVE machine, the jobs it has claimed but is not running (its look-ahead backlog), so that the other
machines take them now (laptop, 2026-10-07). Used when one machine's backlog holds the heavy blocks while the others run dry.
The machine is not told: if it reaches one of these jobs later it runs it again and publishes a second, identical record and a
second done event, which is harmless. Its running jobs (RUNNING_JOBS of its last status) are left alone.
Non-forced push, retried on refusal.   python release_backlog.py <repo> <machine name> [--only LID,LID]"""
import os, sys, json, time, subprocess, tempfile
REPO, NAME = sys.argv[1], sys.argv[2]
ONLY = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
ID = ["-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com"]


def git(*a, cwd, check=True):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a[:3]), r.stderr.strip()[-300:]))
    return r


url = git("remote", "get-url", "origin", cwd=REPO).stdout.strip()
d = tempfile.mkdtemp(prefix="q_rel_"); git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
for attempt in range(10):
    git("fetch", "-q", "origin", "queue", "run/" + NAME, cwd=d)
    st = dict(l.split("=", 1) for l in git("show", "FETCH_HEAD:status.txt", cwd=d, check=False).stdout.splitlines() if "=" in l)
    git("fetch", "-q", "origin", "run/" + NAME, cwd=d); st = dict(l.split("=", 1) for l in git("show", "FETCH_HEAD:status.txt", cwd=d).stdout.splitlines() if "=" in l)
    running = set(st.get("RUNNING_JOBS", "").split())
    git("fetch", "-q", "origin", "queue", cwd=d); git("checkout", "-q", "-f", "-B", "queue", "FETCH_HEAD", cwd=d)
    p = os.path.join(d, "events.jsonl"); own, done = {}, set()
    for l in open(p):
        if not l.strip():
            continue
        e = json.loads(l)
        for j in e.get("jobs", []):
            if e["op"] == "claim":
                own[j] = e["m"]
            elif e["op"] == "done":
                done.add(j); own.pop(j, None)
            elif own.get(j) == e["m"]:
                own.pop(j)
    jobs = sorted(j for j, m in own.items() if m == NAME and j not in done and j not in running and (ONLY is None or j.split(":")[0] in ONLY))
    print("%s: state %s, status age %.0f s, running %d, held and not running %d" % (NAME, st.get("STATE"), time.time() - float(st.get("NOW") or 0), len(running), len(jobs)))
    if not jobs:
        print("nothing to release"); break
    with open(p, "a", newline="\n") as f:
        f.write(json.dumps({"t": round(time.time()), "m": NAME, "op": "release", "jobs": jobs}) + "\n")
    git(*ID, "commit", "-qam", "PC: release %d backlog jobs of %s (rebalancing)" % (len(jobs), NAME), cwd=d)
    if git("push", "-q", "origin", "HEAD:refs/heads/queue", cwd=d, check=False).returncode == 0:
        by = {}
        for j in jobs:
            by[j.split(":")[0]] = by.get(j.split(":")[0], 0) + 1
        print("released %d jobs %s" % (len(jobs), by)); break
    time.sleep(3 + 2 * attempt)
else:
    sys.exit("could not push the release event (10 refused pushes)")
