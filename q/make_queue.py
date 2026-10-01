"""Build the queue branch of the adaptive route-(C) run, from the lab's real state (run on the lab PC). C2, 2026-10-01.

  python q/make_queue.py --branch queue --cap 115                     real queue: every package job not yet done in the lab
  python q/make_queue.py --branch queue-ci --cap 1 --jobs 028:0:8,...  rehearsal queue with explicit jobs

order.txt  = remaining jobs, richest lattice first (same key as the PC scheduler sched.py: -nroots, id), then longest job first.
events.jsonl = empty (append-only log of claim / done / fail / release).
control.json = campaign, mode (run | drain | stop), cap_usd, lease_s, credit_usd, max_fail, ratio (measured actual/estimated hours).
Refuses to overwrite an existing branch that already has events, unless --force.
"""
import os, sys, json, time, argparse, subprocess, tempfile

LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # ...\c2_experimental
PKG = os.path.join(LAB, "c2_cloud_run")


def git(cwd, *a, check=True):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()))
    return r


def remaining_jobs():
    jobs = [j for j in json.load(open(os.path.join(PKG, "jobs.json"))) if not j.get("calib")]
    done = set()
    for j in jobs:
        f = os.path.join(LAB, "data", "finishC", "stream", j["lid"], "chunks.jsonl")
        if os.path.exists(f):
            for l in open(f):
                if l.strip():
                    r = json.loads(l)
                    if r.get("chunk_done") and r.get("chunk") == [j["k"], j["n"]]:
                        done.add((j["lid"], j["k"], j["n"])); break
    T = {"%03d" % v["id"]: v for v in json.load(open(os.path.join(LAB, "data", "finishC", "finishC_tracker.json")))["lattices"]}
    rem = [j for j in jobs if (j["lid"], j["k"], j["n"]) not in done and T[j["lid"]]["status"] != "excluded"]
    rem.sort(key=lambda j: (-T[j["lid"]]["nroots"], int(j["lid"]), -j["est_h"], j["k"]))
    return ["%s:%d:%d" % (j["lid"], j["k"], j["n"]) for j in rem], sum(j["est_h"] for j in rem), len(done)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="queue"); ap.add_argument("--cap", type=float, required=True)
    ap.add_argument("--campaign", default="c2q-" + time.strftime("%Y%m%d")); ap.add_argument("--jobs", default="")
    ap.add_argument("--lease", type=int, default=1800); ap.add_argument("--ratio", type=float, default=1.30)
    ap.add_argument("--remote", default="https://github.com/amazing-source/conway99-c2-aws.git"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.jobs:
        order = a.jobs.split(","); est = None; ndone = None
    else:
        order, est, ndone = remaining_jobs()
    d = tempfile.mkdtemp(prefix="q_make_")
    git(d, "init", "-q"); git(d, "remote", "add", "origin", a.remote)
    git(d, "config", "user.name", "amazing-source"); git(d, "config", "user.email", "206353265+amazing-source@users.noreply.github.com")
    if git(d, "fetch", "-q", "origin", a.branch, check=False).returncode == 0:
        ev = git(d, "show", "FETCH_HEAD:events.jsonl", check=False).stdout
        if ev.strip() and not a.force:
            sys.exit("branch %s already has events (%d lines): refusing to overwrite (use --force)" % (a.branch, len(ev.splitlines())))
    git(d, "checkout", "-q", "--orphan", a.branch)
    ctl = {"campaign": a.campaign, "mode": "run", "cap_usd": a.cap, "lease_s": a.lease, "credit_usd": 0, "max_fail": 2,
           "ratio": a.ratio, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    open(os.path.join(d, "control.json"), "w", newline="\n").write(json.dumps(ctl, indent=1) + "\n")
    open(os.path.join(d, "order.txt"), "w", newline="\n").write("".join(j + "\n" for j in order))
    open(os.path.join(d, "events.jsonl"), "w", newline="\n").write("")
    git(d, "add", "-A"); git(d, "commit", "-qm", "queue %s: %d jobs, cap %.2f USD, campaign %s" % (a.branch, len(order), a.cap, a.campaign))
    git(d, "push", "-qf", "origin", "HEAD:refs/heads/" + a.branch)
    print("queue %s pushed: %d jobs%s, cap %.2f USD, campaign %s" % (
        a.branch, len(order), "" if est is None else " (est %.0f h; %d package jobs already done in the lab)" % (est, ndone), a.cap, a.campaign))


if __name__ == "__main__":
    main()
