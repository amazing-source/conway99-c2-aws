"""Checks of the free rehearsal (GitHub Actions, q_rehearsal.yml) of the adaptive queue. C2, 2026-10-01.

  python3 q/rehearsal_check.py set KEY=VALUE ... [--order-add JOB]   edit control.json (and order.txt) of branch queue-ci
  python3 q/rehearsal_check.py s1 N                                   scenario 1: two agents, N real jobs
  python3 q/rehearsal_check.py s2 NAME                                scenario 2: agent NAME must stop on the cap, without claiming
  python3 q/rehearsal_check.py s3 NAME STATE                          scenario 3: agent NAME must end in STATE, without claiming
Exit code 0 = PASS. Every failed check is printed.
"""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qagent import owners
QBR, PREFIX = "queue-ci", "run/qci-"
FAILS = []


def git(*a, cwd=None, check=True):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("git %s: %s" % (" ".join(a[:2]), r.stderr))
    return r.stdout


def ok(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def load():
    git("fetch", "-q", "--prune", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (QBR, QBR),
        "+refs/heads/%s*:refs/remotes/origin/%s*" % (PREFIX, PREFIX))
    order = [l for l in git("show", "origin/%s:order.txt" % QBR).split() if l]
    ev = [json.loads(l) for l in git("show", "origin/%s:events.jsonl" % QBR).splitlines() if l.strip()]
    ms = {}
    for r in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/" + PREFIX + "*").split():
        st = dict(l.split("=", 1) for l in git("show", r + ":status.txt", check=False).splitlines() if "=" in l)
        ms[st.get("NAME", r)] = (r, st)
    return order, ev, ms


def s1(n):
    order, ev, ms = load(); own, done, fails = owners(ev)
    held = {}; overlap = []
    for e in ev:                                         # replay: a claim on a job held by the other agent is a double claim
        for j in e["jobs"]:
            if e["op"] == "claim":
                if held.get(j) not in (None, e["m"]):
                    overlap.append((j, held[j], e["m"]))
                held[j] = e["m"]
            elif e["op"] in ("done", "fail", "release") and held.get(j) == e["m"]:
                held.pop(j)
    ok(not overlap, "no job ever held by two machines at once %s" % (overlap or ""))
    ndone = [j for e in ev if e["op"] == "done" for j in e["jobs"]]
    ok(sorted(ndone) == sorted(order) and len(order) == n, "each of the %d jobs done exactly once (done events: %d)" % (n, len(ndone)))
    for e in ev:
        if e["op"] != "done":
            continue
        ref = ms.get(e["m"], (None,))[0]
        for j in e["jobs"]:
            lid, k, nn = j.split(":"); f = "results/%s_%s_%s.jsonl" % (lid, k, nn)
            txt = git("show", "%s:%s" % (ref, f), check=False) if ref else ""
            recs = [json.loads(l) for l in txt.splitlines() if l.strip()]
            good = any(r.get("chunk_ok") and r.get("chunk_done") for r in recs)
            ok(good, "result %s is on %s with chunk_ok and chunk_done" % (f, ref))
    for name, (ref, st) in sorted(ms.items()):
        if name in ("qci-a", "qci-b"):
            ok(st.get("STATE") == "FINI", "%s ended in FINI (state %s, done %s)" % (name, st.get("STATE"), st.get("DONE")))
    ok(all(int(ms[x][1].get("DONE") or 0) > 0 for x in ("qci-a", "qci-b") if x in ms), "both agents did real work")


def s3(name, want):
    order, ev, ms = load()
    claims = [e for e in ev if e["m"] == name and e["op"] == "claim"]
    st = ms.get(name, (None, {}))[1]
    ok(st.get("STATE") == want, "%s ended in %s (state %s, reason: %s)" % (name, want, st.get("STATE"), st.get("REASON")))
    ok(not claims, "%s claimed nothing" % name)


def set_control(args):
    url = git("remote", "get-url", "origin").strip(); d = tempfile.mkdtemp()
    git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
    git("fetch", "-q", "origin", QBR, cwd=d); git("checkout", "-q", "-B", QBR, "FETCH_HEAD", cwd=d)
    ctl = json.load(open(os.path.join(d, "control.json")))
    i = 0
    while i < len(args):
        if args[i] == "--order-add":
            with open(os.path.join(d, "order.txt"), "a", newline="\n") as f:
                f.write(args[i + 1] + "\n")
            i += 2; continue
        k, v = args[i].split("=", 1)
        try:
            v = json.loads(v)
        except ValueError:
            pass
        ctl[k] = v; i += 1
    open(os.path.join(d, "control.json"), "w", newline="\n").write(json.dumps(ctl, indent=1) + "\n")
    git("-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com", "commit", "-qam", "rehearsal control", cwd=d)
    git("push", "-q", "origin", "HEAD:refs/heads/" + QBR, cwd=d)
    print("queue-ci control:", ctl)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "set":
        set_control(sys.argv[2:]); sys.exit(0)
    if cmd == "s1":
        s1(int(sys.argv[2]))
    elif cmd == "s2":
        s3(sys.argv[2], "STOP")
    elif cmd == "s3":
        s3(sys.argv[2], sys.argv[3])
    print("RESULT:", "PASS" if not FAILS else "FAIL (%d)" % len(FAILS))
    sys.exit(1 if FAILS else 0)
