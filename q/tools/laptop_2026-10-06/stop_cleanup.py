"""After machines were terminated from the AWS side (no agent left to do it), do by hand what their agents do on STOP:
  1. push a terminal status (STATE=STOP) to run/<name>, so the ledger stops counting them and the monitor shows the truth;
  2. append one release event per machine to events.jsonl of branch `queue`, so their jobs are free at once (not after the lease).
Non-forced pushes only, retried on refusal.   python stop_cleanup.py <repo> <reason> <name> [<name> ...]"""
import os, sys, json, time, subprocess, tempfile
REPO, REASON, NAMES = sys.argv[1], sys.argv[2], sys.argv[3:]
ID = ["-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com"]


def git(*a, cwd, check=True):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a[:3]), r.stderr.strip()[-300:]))
    return r


url = git("remote", "get-url", "origin", cwd=REPO).stdout.strip()
d = tempfile.mkdtemp(prefix="q_stop_"); git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
now = time.time()

# 1. terminal status on each machine branch
for n in NAMES:
    for attempt in range(4):
        if git("fetch", "-q", "origin", "run/" + n, cwd=d, check=False).returncode:
            print("%s: no status branch (never reported)" % n); break
        git("checkout", "-q", "-f", "-B", "w", "FETCH_HEAD", cwd=d)
        p = os.path.join(d, "status.txt"); st = [l.rstrip("\n").split("=", 1) for l in open(p) if "=" in l]
        cur = dict(st)
        if cur.get("STATE") != "EN_COURS":
            print("%s: already %s, status left as it is" % (n, cur.get("STATE"))); break
        new = {"STATE": "STOP", "REASON": REASON, "NOW": "%.0f" % now, "UPTIME_H": "%.2f" % ((now - float(cur["BOOT"])) / 3600.0),
               "RUNNING": "0", "RUNNING_JOBS": "", "ETA_S": "0"}
        open(p, "w", newline="\n").write("".join("%s=%s\n" % (k, new.get(k, v)) for k, v in st))
        git(*ID, "commit", "-qam", "%s STOP (terminated from the PC) %s" % (n, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))), cwd=d)
        if git("push", "-q", "origin", "HEAD:refs/heads/run/" + n, cwd=d, check=False).returncode == 0:
            print("%s: status STOP pushed (up %s h)" % (n, new["UPTIME_H"])); break
        time.sleep(5)
    else:
        print("%s: could NOT push the status" % n)

# 2. release their jobs
for attempt in range(8):
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
    evs = []
    for n in NAMES:
        jobs = sorted(j for j, m in own.items() if m == n and j not in done)
        if jobs:
            evs.append({"t": round(time.time()), "m": n, "op": "release", "jobs": jobs})
    if not evs:
        print("no job left to release"); break
    with open(p, "a", newline="\n") as f:
        for e in evs:
            f.write(json.dumps(e) + "\n")
    git(*ID, "commit", "-qam", "PC: release %d jobs of %d terminated machines" % (sum(len(e["jobs"]) for e in evs), len(evs)), cwd=d)
    if git("push", "-q", "origin", "HEAD:refs/heads/queue", cwd=d, check=False).returncode == 0:
        for e in evs:
            by = {}
            for j in e["jobs"]:
                by[j.split(":")[0]] = by.get(j.split(":")[0], 0) + 1
            print("%s: released %d jobs %s" % (e["m"], len(e["jobs"]), by))
        break
    time.sleep(3 + 2 * attempt)
else:
    sys.exit("could not push the release events (8 refused pushes)")
