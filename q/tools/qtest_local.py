"""Local integration test of the queue protocol of q/qagent.py (no engine, no network): a bare git repo as 'GitHub',
4 agents in threads claiming from a 20-job queue concurrently. Checks: fleet listing sees everyone, no job ever held by two
agents, every job done exactly once, ledger counts all machines. One process, < 3 min, < 200 MB."""
import os, sys, json, time, shutil, subprocess, threading, tempfile
AWS = r"C:\Users\RESEARCHER\Desktop\c2_experimental\aws_repo"
sys.path.insert(0, os.path.join(AWS, "q"))
S = tempfile.mkdtemp(prefix="qtest_")
os.environ["USERPROFILE"] = S; os.environ["HOME"] = S          # agents' working dirs go to the scratch folder
import qagent as Q


def git(*a, cwd=None):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


origin = os.path.join(S, "origin.git"); git("init", "-q", "--bare", origin)
url = "file:///" + origin.replace("\\", "/")
seed = os.path.join(S, "seed"); git("init", "-q", seed)
git("config", "user.name", "t", cwd=seed); git("config", "user.email", "t@t", cwd=seed)
JOBS = ["999:%d:20" % k for k in range(20)]
open(os.path.join(seed, "order.txt"), "w", newline="\n").write("".join(j + "\n" for j in JOBS))
open(os.path.join(seed, "events.jsonl"), "w", newline="\n").write("")
open(os.path.join(seed, "control.json"), "w", newline="\n").write(json.dumps(
    {"campaign": "c2q-test", "mode": "run", "cap_usd": 1000, "lease_s": 1800, "credit_usd": 0, "max_fail": 2, "ratio": 1.3}))
git("add", "-A", cwd=seed); git("commit", "-qm", "seed", cwd=seed); git("push", "-q", url, "HEAD:refs/heads/queue-ci", cwd=seed)

agents = []
for n in "abcd":
    os.environ.update(Q_NAME="qci-" + n, Q_URL=url, Q_QUEUE="queue-ci", Q_RUNPREFIX="run/qci-", Q_TEST="1", Q_PRICE="0.1",
                      Q_OVH="0.01", Q_BOOT=str(time.time() - 600), Q_WORKERS="1", Q_HEARTBEAT="60")
    a = Q.Agent(); a.est = {j: 0.01 for j in JOBS}; Q.init_repo(a.qd, a.url)
    a.fetch(); a.campaign = "c2q-test"; assert a.push_status("EN_COURS", "test"); agents.append(a)
for a in agents:
    a.fetch(); seen = sorted(a.statuses("c2q-test"))
    assert seen == ["qci-a", "qci-b", "qci-c", "qci-d"], ("fleet listing", a.name, seen)
print("fleet listing: every agent sees all 4 machines")

claims = []; lock = threading.Lock()


def worker(a):
    while True:
        picked = a.sync()
        if picked:
            with lock:
                claims.extend((a.name, j) for j in picked)
            a.running = {j: {"t0": time.time()} for j in picked}
            time.sleep(0.2)                                            # "compute"
            a.running = {}
            a.pending.append({"t": round(time.time()), "m": a.name, "op": "done", "jobs": picked})
        elif not a.pending:
            if a.info.get("free", 0) == 0:
                return


ts = [threading.Thread(target=worker, args=(a,)) for a in agents]
t0 = time.time(); [t.start() for t in ts]; [t.join(timeout=240) for t in ts]
assert not any(t.is_alive() for t in ts), "workers did not finish"
for a in agents:                                                    # publish remaining done events
    if a.pending:
        a.sync(claim=False)
a = agents[0]; a.fetch(); order, ctl, ev = a.read_queue()
held = {}; double = []
for e in ev:
    for j in e["jobs"]:
        if e["op"] == "claim":
            if held.get(j) not in (None, e["m"]):
                double.append((j, held[j], e["m"]))
            held[j] = e["m"]
        elif e["op"] == "done" and held.get(j) == e["m"]:
            held.pop(j)
done = [j for e in ev if e["op"] == "done" for j in e["jobs"]]
assert not double, ("double claims", double)
assert sorted(done) == sorted(JOBS), ("done once each", len(done))
per = {n: sum(1 for m, _ in claims if m == n) for n in "qci-a qci-b qci-c qci-d".split()}
print("concurrency: 20 jobs, %d events, no double claim, each job done exactly once, %.1f s; jobs per agent %s" % (len(ev), time.time() - t0, per))
ms = a.statuses("c2q-test"); led, proj = Q.ledger(ms, time.time(), ctl, 60, 20, last_event=Q.last_events(ev))
assert len(ms) == 4 and led > 0
print("ledger over the 4 machines: %.4f $ (4 x 10 min x 0.11 $/h = %.4f)" % (led, 4 * 600 / 3600 * 0.11))
shutil.rmtree(S, ignore_errors=True)
print("LOCAL QUEUE TEST: PASS")
