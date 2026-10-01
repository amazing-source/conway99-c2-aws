"""Local test of the v2 control switch (C2, 2026-10-02): an agent of this version obeys 'mode_v2' when present, else 'mode'.
Bare git repo as 'GitHub', no engine, no network. One process, < 1 min, < 100 MB."""
import os, sys, json, time, subprocess, tempfile
AWS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(AWS, "q"))
S = tempfile.mkdtemp(prefix="qmv2_"); os.environ["USERPROFILE"] = S; os.environ["HOME"] = S
import qagent as Q


def git(*a, cwd=None):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True); assert r.returncode == 0, r.stderr; return r.stdout


origin = os.path.join(S, "o.git"); git("init", "-q", "--bare", origin); url = "file:///" + origin.replace("\\", "/")
JOBS = ["999:%d:4" % k for k in range(4)]


def seed(ctl):
    d = tempfile.mkdtemp(dir=S); git("init", "-q", d); git("config", "user.name", "t", cwd=d); git("config", "user.email", "t@t", cwd=d)
    open(os.path.join(d, "order.txt"), "w", newline="\n").write("".join(j + "\n" for j in JOBS))
    open(os.path.join(d, "events.jsonl"), "w", newline="\n").write("")
    open(os.path.join(d, "control.json"), "w", newline="\n").write(json.dumps(ctl))
    git("add", "-A", cwd=d); git("commit", "-qm", "s", cwd=d); git("push", "-qf", url, "HEAD:refs/heads/queue-ci", cwd=d)


base = {"campaign": "c2q-mv2", "cap_usd": 1000, "lease_s": 1800, "credit_usd": 0, "max_fail": 2, "ratio": 1.3}
cases = [({"mode": "drain", "mode_v2": "run"}, "run"), ({"mode": "run", "mode_v2": "stop"}, "stop"), ({"mode": "stop", "mode_v2": "drain"}, "drain"),
         ({"mode": "drain"}, "drain"), ({"mode": "run"}, "run")]
ok = True
for i, (m, want) in enumerate(cases):
    seed(dict(base, **m))
    os.environ.update(Q_NAME="qci-m%d" % i, Q_URL=url, Q_QUEUE="queue-ci", Q_RUNPREFIX="run/qci-", Q_TEST="1", Q_PRICE="0.1", Q_OVH="0.01",
                      Q_BOOT=str(time.time()), Q_WORKERS="1", Q_HEARTBEAT="60")
    a = Q.Agent(); a.est = {j: 0.01 for j in JOBS}; Q.init_repo(a.qd, a.url); a.fetch(); a.campaign = "c2q-mv2"
    assert a.push_status("EN_COURS", "t")
    picked = a.sync()
    got = a.info["mode"]; good = got == want and (bool(picked) == (want == "run"))
    ok &= good
    print("control %-36s -> agent mode %-5s claimed %s  %s" % (json.dumps(m), got, picked, "PASS" if good else "FAIL"))
print("MODE_V2 TEST:", "PASS" if ok else "FAIL")
