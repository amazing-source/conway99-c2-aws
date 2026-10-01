"""Watch and steer the adaptive route-(C) run from the PC (C2, 2026-10-01). Run from the repo folder:

  python q/monitor_q.py              table of the machines, the jobs and the spend ledger (refreshed every 5 min; Ctrl+C to quit)
  python q/monitor_q.py --once       one table only
  python q/monitor_q.py --aws        + read-only AWS check (needs the AWS CLI signed in): every running instance must report here
  python q/monitor_q.py --drain      machines finish their running jobs, take no new ones, then power off
  python q/monitor_q.py --stop       machines stop at once (running jobs are released to the queue) and power off
  python q/monitor_q.py --run        back to normal
  python q/monitor_q.py --cap 110    change the spend cap (USD); machines read it within a few minutes
  python q/monitor_q.py --fetch      copy every machine's results into resultats_q/<machine>/results (for the lab import)
"""
import os, sys, json, time, argparse, subprocess, tempfile, io, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from qagent import owners, ledger, live_names, TERMINAL           # the same formulas as on the machines

PREFIX, QBR, HB, DEADMAN = "run/q-", "queue", 300, 20


def git(*a, cwd=REPO, check=True, binary=False):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=not binary)
    if check and r.returncode:
        sys.exit("git %s: %s" % (" ".join(a[:2]), r.stderr if not binary else r.stderr.decode(errors="replace")))
    return r.stdout


def fetch():
    git("fetch", "-q", "--prune", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (QBR, QBR),
        "+refs/heads/%s*:refs/remotes/origin/%s*" % (PREFIX, PREFIX))


def state():
    ref = "origin/" + QBR
    order = [l.strip() for l in git("show", ref + ":order.txt").splitlines() if l.strip()]
    ctl = json.loads(git("show", ref + ":control.json"))
    ev = [json.loads(l) for l in git("show", ref + ":events.jsonl").splitlines() if l.strip()]
    ms = {}
    for r in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/" + PREFIX).split():
        txt = subprocess.run(["git", "show", r + ":status.txt"], cwd=REPO, capture_output=True, text=True).stdout
        st = dict(l.split("=", 1) for l in txt.splitlines() if "=" in l)
        if st.get("CAMPAIGN") == ctl.get("campaign") and st.get("NAME"):
            ms[st["NAME"]] = st
    return order, ctl, ev, ms


def table():
    fetch(); order, ctl, ev, ms = state(); now = time.time()
    own, done, fails = owners(ev); lease = int(ctl.get("lease_s", 1800)); live = live_names(ms, now, lease)
    led, proj = ledger(ms, now, ctl, HB, DEADMAN)
    jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(REPO, "..", "c2_cloud_run", "jobs.json")))} \
        if os.path.exists(os.path.join(REPO, "..", "c2_cloud_run", "jobs.json")) else {}
    print("\n=== Route (C) adaptive run, campaign %s, %s ===" % (ctl.get("campaign"), time.strftime("%d/%m %H:%M")))
    print("%-24s %-14s %-12s %6s %7s %4s %5s %4s %6s %6s  %s" % ("machine", "zone", "state", "up_h", "cost$", "run", "done", "fail", "age_m", "eta_h", "note"))
    for n, st in sorted(ms.items(), key=lambda kv: kv[1].get("BOOT", "")):
        try:
            up = (float(st["NOW"]) - float(st["BOOT"])) / 3600; cost = up * (float(st["PRICE"]) + float(st["OVH"]))
            age = (now - float(st["NOW"])) / 60
        except (KeyError, ValueError):
            up = cost = age = float("nan")
        note = st.get("REASON", "") or st.get("LAST_ERR", "")
        if st.get("STATE") not in TERMINAL and age > lease / 60:
            note = "SILENT (dead-man switch powers it off) " + note
        print("%-24s %-14s %-12s %6.2f %7.2f %4s %5s %4s %6.1f %6.1f  %s" % (n[:24], st.get("AZ", "")[:14], st.get("STATE", "")[:12], up, cost,
              st.get("RUNNING", ""), st.get("DONE", ""), st.get("FAILED", ""), age, float(st.get("ETA_S") or 0) / 3600, note[:70]))
    nfree = sum(1 for j in order if j not in done and fails[j] < int(ctl.get("max_fail", 2)) and own.get(j) not in live)
    claimed = sum(1 for j in order if own.get(j) in live and j not in done)
    rest_h = sum(float(jobs[j]["est_h"]) for j in order if j not in done and j in jobs) * float(ctl.get("ratio", 1.3))
    print("--- jobs: %d in queue | done %d | running/claimed %d | free %d | failed twice %d" % (
        len(order), len(done & set(order)), claimed, nfree, sum(1 for j in order if fails[j] >= int(ctl.get("max_fail", 2)))))
    print("--- spend ledger (upper bound, max prices): %.2f $ of cap %.2f $ | + running jobs ~%.2f $ | mode %s | machines alive %d" % (
        led, float(ctl["cap_usd"]), proj, ctl.get("mode"), len(live)))
    if rest_h:
        print("--- work left ~%.0f job-hours (x%.2f) = ~%.0f machine-hours at 26 jobs/machine" % (rest_h, float(ctl.get("ratio", 1.3)), rest_h / 26))


def set_control(**kv):
    d = tempfile.mkdtemp(prefix="q_ctl_"); url = git("remote", "get-url", "origin").strip()
    for _ in range(8):
        subprocess.run(["git", "init", "-q", d], capture_output=True)
        subprocess.run(["git", "-C", d, "remote", "remove", "origin"], capture_output=True)
        subprocess.run(["git", "-C", d, "remote", "add", "origin", url], capture_output=True)
        git("fetch", "-q", "origin", QBR, cwd=d); git("checkout", "-q", "-B", QBR, "FETCH_HEAD", cwd=d)
        p = os.path.join(d, "control.json"); ctl = json.load(open(p)); ctl.update(kv)
        open(p, "w", newline="\n").write(json.dumps(ctl, indent=1) + "\n")
        git("-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com", "commit", "-qam",
            "control: %s" % " ".join("%s=%s" % i for i in kv.items()), cwd=d)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + QBR], cwd=d, capture_output=True).returncode == 0:
            print("control updated:", kv); return
        time.sleep(3)
    sys.exit("could not update control.json (8 refused pushes)")


def fetch_results():
    fetch(); n = 0
    for r in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/" + PREFIX).split():
        data = subprocess.run(["git", "archive", "--format=zip", r, "results"], cwd=REPO, capture_output=True).stdout
        if data:
            dst = os.path.join(REPO, "resultats_q", r.split("/")[-1]); os.makedirs(dst, exist_ok=True)
            zipfile.ZipFile(io.BytesIO(data)).extractall(dst); n += 1
    print("results of %d machines copied into %s" % (n, os.path.join(REPO, "resultats_q")))
    print("import on the lab PC:  cd ..  &&  .venv\\Scripts\\python.exe scripts\\cloud\\import_results.py c2_cloud_run "
          "aws_repo\\resultats_q\\<machine>\\results ...  &&  .venv\\Scripts\\python.exe scripts\\stream_finish.py")


def aws_check():
    P = json.load(open(os.path.join(HERE, "prices.json"))); fetch(); _, ctl, _, ms = state(); now = time.time()
    seen = {st["NAME"]: st for st in ms.values()}
    for reg in P["max_price_usd_per_h"]:
        out = subprocess.run(["aws", "ec2", "describe-instances", "--region", reg, "--filters", "Name=instance-state-name,Values=pending,running",
                              "--query", "Reservations[].Instances[].[InstanceId,InstanceType,InstanceLifecycle,SpotInstanceRequestId,Placement.AvailabilityZone]",
                              "--output", "json"], capture_output=True, text=True, shell=(os.name == "nt"))
        try:
            inst = json.loads(out.stdout or "[]")
        except ValueError:
            print(reg, "AWS CLI error:", (out.stderr or out.stdout)[:200]); continue
        for iid, itype, life, sir, az in inst:
            maxp = ""
            if sir:
                o = subprocess.run(["aws", "ec2", "describe-spot-instance-requests", "--region", reg, "--spot-instance-request-ids", sir,
                                    "--query", "SpotInstanceRequests[0].SpotPrice", "--output", "text"], capture_output=True, text=True, shell=(os.name == "nt"))
                maxp = o.stdout.strip()
            st = seen.get("q-" + iid); flags = []
            if itype not in P["instance_types"]: flags.append("WRONG TYPE")
            if life != "spot": flags.append("NOT SPOT")
            if maxp and abs(float(maxp) - P["max_price_usd_per_h"][reg]) > 1e-9: flags.append("MAX PRICE %s != %s" % (maxp, P["max_price_usd_per_h"][reg]))
            if st is None: flags.append("NOT REPORTING YET (fine during the first ~10 min)")
            elif now - float(st["NOW"]) > 20 * 60: flags.append("SILENT %.0f min" % ((now - float(st["NOW"])) / 60))
            print("%-12s %-20s %-12s %-6s max %-6s %-12s %s" % (reg, iid, itype, life or "on-demand", maxp, st.get("STATE", "") if st else "-",
                                                               " | ".join(flags) or "OK"))
    print("(read-only check: nothing was changed on AWS)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("once", "aws", "drain", "stop", "run", "fetch"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--cap", type=float); ap.add_argument("--every", type=float, default=5.0)
    a = ap.parse_args()
    if a.drain: set_control(mode="drain")
    if a.stop: set_control(mode="stop")
    if a.run: set_control(mode="run")
    if a.cap is not None: set_control(cap_usd=a.cap)
    if a.fetch: fetch_results(); sys.exit(0)
    if a.aws: aws_check(); sys.exit(0)
    while True:
        table()
        if a.once or a.drain or a.stop or a.run or a.cap is not None:
            break
        time.sleep(a.every * 60)
