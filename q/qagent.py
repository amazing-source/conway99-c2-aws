"""Route (C) adaptive queue agent (C2, 2026-10-01). Runs on ONE cloud machine; started by q/qmachine.sh.

  python3 qagent.py status STATE [REASON]    push this machine's status (used by qmachine.sh before the agent runs)
  <package venv>/bin/python qagent.py run     the agent

What `run` does (one cycle every 30 s):
  * Jobs are started with the package's OWN functions run_jobs.start / env_exact / check_manifest, i.e. the same producer | consumer
    command lines, the same engine flags and the MANIFEST check as run_jobs.py: the computation is the lab's, byte for byte.
    A finished job counts as done only if its result file has a chunk_ok record (run_jobs.done_already).
  * Work comes from the shared queue (branch `queue`): order.txt (priority order: richest lattice first, like the PC scheduler),
    events.jsonl (append-only: claim / done / fail / release), control.json (campaign, mode, cap). A claim is published with a
    plain, NON-forced git push: if another machine pushed first the push is refused, the state is re-read and the choice redone,
    so no job is ever held by two machines. A claim whose machine sent no heartbeat for `lease_s` seconds is free again.
  * Every HEARTBEAT seconds: status.txt + finished results are pushed to run/<NAME>, and the dead-man switch is re-armed
    (`shutdown -h +DEADMAN`). A machine that cannot report for DEADMAN minutes powers itself off.
  * Spend cap. ledger = sum over every machine of the campaign of uptime x (max spot price + overhead): an upper bound of the
    real bill (spot is billed at the market price, never above the max price set at launch). A new job is claimed only if
    ledger + the time every machine still needs for its running jobs (est_h x ratio) stays under cap_usd. If the ledger itself
    reaches the cap, every machine stops at once. Silent machines are counted until their dead-man switch has fired.
Exit code 0 = finished, drained or stopped normally (qmachine.sh then powers the machine off); anything else = error.
"""
import os, sys, json, time, random, shutil, subprocess, collections, traceback, urllib.request

TERMINAL = {"FINI", "DRAINED", "STOP", "INTERRUPTED", "STOP CALIB", "ERREUR INSTALLATION", "REFUS", "ERREUR AGENT"}
CYCLE = 30          # seconds between two cycles
SYNC_EVERY = 60     # seconds between two queue syncs while there are free slots


def env(k, d=None):
    v = os.environ.get(k)
    return d if v in (None, "") else v


# ---------------------------------------------------------------- shared logic (also imported by monitor_q.py)
def owners(events):
    """events -> (owner of each job, done jobs, failure count per job)"""
    own, done, fails = {}, set(), collections.Counter()
    for e in events:
        op, m = e.get("op"), e.get("m")
        for j in e.get("jobs", []):
            if op == "claim":
                own[j] = m
            elif op == "done":
                done.add(j); own.pop(j, None)
            elif op in ("release", "fail"):
                if own.get(j) == m:
                    own.pop(j)
                if op == "fail":
                    fails[j] += 1
    return own, done, fails


def live_names(ms, now, lease):
    return {n for n, st in ms.items() if st.get("STATE") not in TERMINAL and now - float(st.get("NOW", 0)) <= lease}


def ledger(ms, now, ctl, hb, deadman_min, self_name=None, self_boot=None, self_rate=None):
    """-> (ledger_usd, projected_usd_for_running_jobs_of_the_other_machines). Upper bound of the bill: max price, silent machines
    counted until their dead-man switch has fired, terminal machines until 3 min after their last report."""
    lease = int(ctl.get("lease_s", 1800)); total = proj = 0.0
    for n, st in ms.items():
        if n == self_name:
            continue
        try:
            boot, last = float(st["BOOT"]), float(st["NOW"]); rate = float(st["PRICE"]) + float(st["OVH"])
        except (KeyError, ValueError):
            continue
        if st.get("STATE") in TERMINAL:
            end = last + 180
        elif now - last <= lease:
            end = now; proj += (float(st.get("ETA_S") or 0) + hb) / 3600.0 * rate
        else:
            end = last + (deadman_min + 2) * 60                    # silent: its dead-man switch has powered it off by then
        total += max(0.0, end - boot) / 3600.0 * rate
    if self_name is not None:
        total += max(0.0, now - self_boot) / 3600.0 * self_rate
    return total - float(ctl.get("credit_usd", 0)), proj


# ---------------------------------------------------------------- git helpers
def git(cwd, *args, timeout=120, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError("git %s failed: %s" % (" ".join(args[:3]), (r.stderr or r.stdout).strip()[-400:]))
    return r


def init_repo(d, url):
    os.makedirs(d, exist_ok=True)
    if not os.path.isdir(os.path.join(d, ".git")):
        git(d, "init", "-q")
        git(d, "config", "user.name", "amazing-source"); git(d, "config", "user.email", "206353265+amazing-source@users.noreply.github.com")
        git(d, "remote", "add", "origin", url)


class Agent:
    def __init__(self):
        self.name = env("Q_NAME"); self.url = env("Q_URL"); self.qbr = env("Q_QUEUE", "queue"); self.prefix = env("Q_RUNPREFIX", "run/q-")
        assert self.name and self.url and ("run/" + self.name).startswith(self.prefix), "bad Q_NAME / Q_URL / Q_RUNPREFIX"
        self.br = "run/" + self.name
        self.pkg = env("Q_PKG", os.path.expanduser("~/c2_cloud_run"))
        self.test = bool(env("Q_TEST")); self.hb = int(env("Q_HEARTBEAT", "300")); self.deadman = int(env("Q_DEADMAN_MIN", "20"))
        self.max_up = float(env("Q_MAX_UPTIME_H", "96")) * 3600
        self.region, self.az, self.itype = env("Q_REGION", "?"), env("Q_AZ", "?"), env("Q_ITYPE", "?")
        self.price, self.ovh, self.boot = float(env("Q_PRICE")), float(env("Q_OVH", "0.01")), float(env("Q_BOOT"))
        self.rate = self.price + self.ovh
        self.workers = int(env("Q_WORKERS", "1"))
        home = os.path.expanduser("~")
        self.qd = os.path.join(home, "q_queue_" + self.name); self.pd = os.path.join(home, "q_push_" + self.name)
        self.logf = os.path.join(home, "q_agent_%s.log" % self.name)
        self.running = {}; self.pending = []; self.done_here = []; self.failed_here = []
        self.unpushed = []          # done/fail events whose result is not yet on GitHub: published only after a successful push
        self.campaign = "?"; self.info = {}; self.last_err = ""

    def log(self, m):
        with open(self.logf, "a") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), m))

    # -- queue
    def fetch(self):
        git(self.qd, "fetch", "-q", "--prune", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (self.qbr, self.qbr),
            "+refs/heads/%s*:refs/remotes/origin/%s*" % (self.prefix, self.prefix))

    def show(self, ref, path):
        return git(self.qd, "show", "%s:%s" % (ref, path)).stdout

    def read_queue(self):
        ref = "origin/" + self.qbr
        order = [l.strip() for l in self.show(ref, "order.txt").splitlines() if l.strip()]
        ctl = json.loads(self.show(ref, "control.json"))
        ev = [json.loads(l) for l in self.show(ref, "events.jsonl").splitlines() if l.strip()]
        return order, ctl, ev

    def statuses(self, campaign):
        ms = {}
        refs = git(self.qd, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/" + self.prefix).stdout.split()
        for ref in refs:
            r = git(self.qd, "show", ref + ":status.txt", check=False)
            if r.returncode:
                continue
            st = dict(l.split("=", 1) for l in r.stdout.splitlines() if "=" in l)
            if st.get("CAMPAIGN") == campaign and st.get("NAME"):
                ms[st["NAME"]] = st
        return ms

    def eta_s(self, now, ratio):
        return max([max(0.0, self.est[k] * ratio * 3600 - (now - r["t0"])) for k, r in self.running.items()] or [0.0])

    def sync(self, claim=True):
        """One atomic queue transaction: publish pending events + (if claim) claim new jobs, the choice being redone on the fresh
        state whenever the push is refused. Returns the jobs claimed; fills self.info (mode, reason, ledger, projection, free)."""
        for attempt in range(12):
            self.fetch()
            order, ctl, ev = self.read_queue(); self.campaign = ctl.get("campaign", "?")
            ms = self.statuses(self.campaign); own, done, fails = owners(ev); now = time.time()
            led, proj_others = ledger(ms, now, ctl, self.hb, self.deadman, self.name, self.boot, self.rate)
            ratio, cap, maxfail = float(ctl.get("ratio", 1.3)), float(ctl["cap_usd"]), int(ctl.get("max_fail", 2))
            live = live_names(ms, now, int(ctl.get("lease_s", 1800))) | {self.name}
            free = [j for j in order if j not in done and fails[j] < maxfail and own.get(j) not in live and j in self.est]
            if ctl.get("mode") == "stop":
                mode, reason = "stop", "control: stop"
            elif led >= cap:
                mode, reason = "stop", "cap reached (ledger %.2f >= %.2f)" % (led, cap)
            elif now - self.boot > self.max_up:
                mode, reason = "drain", "max uptime"
            elif ctl.get("mode") == "drain":
                mode, reason = "drain", "control: drain"
            else:
                mode, reason = "run", ""
            picked = []
            if mode == "run" and claim:
                eta = self.eta_s(now, ratio); nfree = self.workers - len(self.running)
                for j in free:
                    if len(picked) >= nfree:
                        break
                    new_eta = max(eta, self.est[j] * ratio * 3600)
                    if led + proj_others + (new_eta + self.hb) / 3600.0 * self.rate > cap:
                        continue                                   # would not finish under the cap: try a shorter job
                    picked.append(j); eta = new_eta
                if free and not picked and not self.running:
                    reason = "projected spend would exceed the cap"
            self.info = dict(mode=mode, reason=reason, ledger=led, proj=proj_others, cap=cap, free=len(free), ratio=ratio,
                             machines=len(ms))
            evs = list(self.pending) + ([{"t": round(now), "m": self.name, "op": "claim", "jobs": picked}] if picked else [])
            if not evs:
                return []
            git(self.qd, "checkout", "-q", "-B", self.qbr, "origin/" + self.qbr)
            with open(os.path.join(self.qd, "events.jsonl"), "a") as f:
                for e in evs:
                    f.write(json.dumps(e) + "\n")
            git(self.qd, "add", "events.jsonl")
            git(self.qd, "commit", "-qm", "%s %s" % (self.name, " ".join("%s:%d" % (e["op"], len(e["jobs"])) for e in evs)))
            r = git(self.qd, "push", "-q", "origin", "HEAD:refs/heads/" + self.qbr, check=False)
            if r.returncode == 0:
                self.pending = []
                return picked
            time.sleep(random.uniform(2, 8) * (1 + attempt / 3.0))
        raise RuntimeError("queue push refused 12 times in a row")

    # -- own branch
    def push_status(self, state, reason=""):
        init_repo(self.pd, self.url)
        if not os.path.exists(os.path.join(self.pd, "status.txt")):
            r = git(self.pd, "fetch", "-q", "origin", self.br, check=False)        # same machine restarting: keep its results
            if r.returncode == 0:
                git(self.pd, "reset", "-q", "--hard", "FETCH_HEAD")
        now = time.time(); i = self.info
        st = [("CAMPAIGN", self.campaign), ("NAME", self.name), ("STATE", state), ("REASON", reason.replace("\n", " ")[:300]),
              ("REGION", self.region), ("AZ", self.az), ("ITYPE", self.itype), ("PRICE", self.price), ("OVH", self.ovh),
              ("BOOT", "%.0f" % self.boot), ("NOW", "%.0f" % now), ("UPTIME_H", "%.2f" % ((now - self.boot) / 3600.0)),
              ("WORKERS", self.workers), ("RUNNING", len(self.running)), ("RUNNING_JOBS", " ".join(sorted(self.running))),
              ("ETA_S", "%.0f" % self.eta_s(now, float(i.get("ratio", 1.3))) if hasattr(self, "est") else 0),
              ("DONE", len(self.done_here)), ("FAILED", len(self.failed_here)), ("MODE", i.get("mode", "")),
              ("LEDGER_USD", "%.2f" % i["ledger"] if "ledger" in i else ""), ("CAP_USD", i.get("cap", "")),
              ("FREE_JOBS", i.get("free", "")), ("LAST_ERR", self.last_err[:200])]
        with open(os.path.join(self.pd, "status.txt"), "w") as f:
            f.write("".join("%s=%s\n" % kv for kv in st))
        with open(os.path.join(self.pd, "done.txt"), "w") as f:
            f.write("".join(j + "\n" for j in self.done_here))
        if os.path.exists(self.logf):
            with open(self.logf) as a, open(os.path.join(self.pd, "tail_agent.txt"), "w") as b:
                b.writelines(a.readlines()[-60:])
        git(self.pd, "add", "-A")
        git(self.pd, "commit", "-qm", "%s %s %s" % (self.name, state, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), check=False)
        for _ in range(3):
            if git(self.pd, "push", "-qf", "origin", "HEAD:refs/heads/" + self.br, check=False).returncode == 0:
                return True
            time.sleep(15)
        return False

    def rearm_deadman(self):
        if not self.test:
            subprocess.run(["sudo", "shutdown", "-c"], capture_output=True)
            subprocess.run(["sudo", "shutdown", "-h", "+%d" % self.deadman], capture_output=True)

    def spot_interrupted(self):
        if self.test:
            return False
        try:
            tok = urllib.request.urlopen(urllib.request.Request("http://169.254.169.254/latest/api/token", method="PUT",
                                         headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"}), timeout=2).read().decode()
            urllib.request.urlopen(urllib.request.Request("http://169.254.169.254/latest/meta-data/spot/instance-action",
                                                          headers={"X-aws-ec2-metadata-token": tok}), timeout=2)
            return True                                            # 200: AWS announced the interruption (2 minutes)
        except Exception:
            return False                                           # 404 (normal) or metadata unreachable

    # -- jobs
    def start_jobs(self, keys):
        for k in keys:
            self.running[k] = self.RJ.start(self.jobs[k], self.out, self.envx)
            self.log("start %s (est %.2f h)" % (k, self.est[k]))

    def poll_jobs(self):
        for k, r in list(self.running.items()):
            if r["cons"].poll() is None:
                continue
            r["prod"].wait(); del self.running[k]
            if self.RJ.done_already(self.out, self.jobs[k]):
                os.makedirs(os.path.join(self.pd, "results"), exist_ok=True)
                shutil.copy(r["res"], os.path.join(self.pd, "results", os.path.basename(r["res"])))
                self.done_here.append(k); self.unpushed.append({"t": round(time.time()), "m": self.name, "op": "done", "jobs": [k]})
                self.log("done %s in %.0f s" % (k, time.time() - r["t0"]))
            else:
                self.failed_here.append(k); self.unpushed.append({"t": round(time.time()), "m": self.name, "op": "fail", "jobs": [k]})
                os.makedirs(os.path.join(self.pd, "failed"), exist_ok=True)
                for suffix in ("_consumer.out", "_producer.err"):
                    src = os.path.join(self.out, r["tag"] + suffix)
                    if os.path.exists(src):
                        with open(src, errors="replace") as a, open(os.path.join(self.pd, "failed", r["tag"] + suffix), "w") as b:
                            b.writelines(a.readlines()[-80:])
                self.log("FAIL %s (producer %s consumer %s)" % (k, r["prod"].returncode, r["cons"].returncode))

    def kill_all(self):
        for k, r in list(self.running.items()):
            for p in (r["cons"], r["prod"]):
                try:
                    p.kill(); p.wait(timeout=30)
                except Exception:
                    pass
            self.pending.append({"t": round(time.time()), "m": self.name, "op": "release", "jobs": [k]})
            del self.running[k]

    def flush_results(self, state, reason=""):
        """push results first; only then may their done/fail events be published (a done job always has its result on GitHub)"""
        if self.push_status(state, reason):
            self.pending.extend(self.unpushed); self.unpushed = []
            return True
        return False

    def finish(self, state, reason):
        self.log("%s: %s" % (state, reason))
        if self.unpushed:
            self.flush_results("FINISHING", reason)
        for _ in range(3):
            try:
                self.sync(claim=False); break
            except Exception as e:
                self.last_err = str(e); time.sleep(20)
        self.push_status(state, reason)

    def run(self):
        sys.path.insert(0, self.pkg)
        import run_jobs as RJ                                       # the package's own runner (hashed in MANIFEST.json)
        self.RJ = RJ; RJ.check_manifest(); self.envx = RJ.env_exact(); self.out = os.path.join(self.pkg, "results")
        os.makedirs(self.out, exist_ok=True)
        self.jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(self.pkg, "jobs.json")))}
        self.est = {k: float(j.get("est_h") or 0) for k, j in self.jobs.items()}
        init_repo(self.qd, self.url)
        self.log("agent start: %d workers, price %.4f + %.4f $/h, region %s" % (self.workers, self.price, self.ovh, self.region))
        last_hb = last_sync = 0.0
        while True:
            now = time.time()
            if self.spot_interrupted():
                self.kill_all(); self.finish("INTERRUPTED", "AWS spot interruption notice"); return 0
            self.poll_jobs()
            if self.unpushed:                                          # results to GitHub first, then their done events
                state = "EN_COURS" if self.info.get("mode", "run") == "run" else "DRAINING"
                if self.flush_results(state, self.info.get("reason", "")):
                    self.rearm_deadman(); last_hb = now
            if self.pending or (len(self.running) < self.workers and now - last_sync >= SYNC_EVERY) or now - last_sync >= self.hb:
                picked = self.sync(); last_sync = now
                if self.info["mode"] == "stop":
                    self.kill_all(); self.finish("STOP", self.info["reason"]); return 0
                if picked:
                    self.start_jobs(picked)
                if not self.running and not picked:
                    if self.info["mode"] == "run" and self.info["free"] == 0:
                        self.finish("FINI", "no free job left in the queue"); return 0
                    self.finish("DRAINED", self.info["reason"] or self.info["mode"]); return 0
            if now - last_hb >= self.hb:
                state = "EN_COURS" if self.info.get("mode", "run") == "run" else "DRAINING"
                if self.push_status(state, self.info.get("reason", "")):
                    self.rearm_deadman(); last_hb = now
            time.sleep(CYCLE)


def main():
    a = Agent()
    if len(sys.argv) >= 3 and sys.argv[1] == "status":
        init_repo(a.qd, a.url)
        try:
            a.fetch(); a.campaign = json.loads(a.show("origin/" + a.qbr, "control.json")).get("campaign", "?")
        except Exception as e:
            a.last_err = "queue unreadable: %s" % e
        return 0 if a.push_status(sys.argv[2], " ".join(sys.argv[3:])) else 1
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        try:
            return a.run()
        except Exception:
            tb = traceback.format_exc(); a.last_err = tb.strip().splitlines()[-1]; a.log(tb)
            try:
                a.kill_all(); a.finish("ERREUR AGENT", a.last_err)
            except Exception:
                pass
            return 2
    print(__doc__); return 1


if __name__ == "__main__":
    sys.exit(main())
