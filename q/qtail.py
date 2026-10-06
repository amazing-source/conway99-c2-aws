"""Tail runner (C2, 2026-10-06): one machine finishes a short list of heavy one-y1 stream jobs, each cut over all its cores.

Started by q/qmachine.sh instead of the queue agent when Q_TAIL_KEYS is set (same install, same calibrations):
  Q_TAIL_KEYS="016:414:479 016:431:479 ..."   the jobs, in the order given
  Q_PAR_WORKERS=31                             consumers running at the same time (default: cores - 1)
  Q_PAR=124                                    shards per job (default: 4 x workers)
For each key, one at a time: the package's own producer command (the one of run_jobs.start), piped into q/par_consumer.py, which
runs the unchanged package consumer on P shards and adds the records up. A job counts only if run_jobs.done_already accepts its
record; its result is pushed to run/<NAME> BEFORE its done event is published, as the agent does.
The keys are NOT claimed: they usually belong to a machine that has been computing them for hours on one core. Once the done event
is in the queue the job is done for everyone; the old owner's later result is a duplicate the lab importer ignores.
A key already done when its turn comes is skipped. Exit 0 = finished or interrupted (qmachine.sh then powers the machine off)."""
import os, sys, json, time, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import qagent as Q


def main():
    a = Q.Agent(); keys = (Q.env("Q_TAIL_KEYS", "") or "").split()
    W = int(Q.env("Q_PAR_WORKERS", str(max(1, (os.cpu_count() or 2) - 1))))   # consumers running at the same time
    P = int(Q.env("Q_PAR", str(4 * W)))                                          # shards per job (small shards keep the cores busy)
    sys.path.insert(0, a.pkg)
    import run_jobs as RJ                                           # the package's own runner (hashed in MANIFEST.json)
    RJ.check_manifest(); envx = RJ.env_exact(); out = os.path.join(a.pkg, "results"); os.makedirs(out, exist_ok=True)
    jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(a.pkg, "jobs.json")))}
    a.est = {}                                                       # this machine claims nothing
    Q.init_repo(a.qd, a.url); a.fetch()
    a.campaign = json.loads(a.show("origin/" + a.qbr, "control.json")).get("campaign", "?")
    a.log("tail runner start: %d keys, %d shards per job, %d at a time" % (len(keys), P, W))
    if not a.push_status("EN_COURS", "tail runner: %d jobs, %d shards each, %d at a time" % (len(keys), P, W)):
        raise RuntimeError("cannot push the first status")
    a.rearm_deadman(); nfail = 0
    for key in keys:
        a.fetch(); _, _, ev = a.read_queue(); _, done, _ = Q.owners(ev)
        if key in done or key not in jobs or jobs[key].get("kind"):
            a.log("skip %s (%s)" % (key, "already done" if key in done else "not a stream job of this package")); continue
        job = jobs[key]; lid, k, n = job["lid"], job["k"], job["n"]; tag = "%s_%d_%d" % (lid, k, n)
        res = os.path.join(out, tag + ".jsonl"); stats = os.path.join(out, tag + "_producer_stats.json")
        U = os.path.join(a.pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)
        prod = subprocess.Popen([sys.executable, os.path.join(a.pkg, "c1", "code", "y_pairs_gamma.py"), U, os.path.join(a.pkg, job["gamma"]), stats,
                                 "--from-plan", os.path.join(a.pkg, job["plan"]), "--chunk", "%d/%d" % (k, n), "--stream", "-", "--max-seconds", "86400"],
                                env=envx, cwd=os.path.join(a.pkg, "c1", "code"), stdout=subprocess.PIPE,
                                stderr=open(os.path.join(out, tag + "_producer.err"), "w"))      # = run_jobs.start, producer side
        cons = subprocess.Popen([sys.executable, os.path.join(HERE, "par_consumer.py"), a.pkg, lid, "-", res, "4000000000", str(P), str(W)], env=envx, cwd=a.pkg,
                                stdin=prod.stdout, stdout=open(os.path.join(out, tag + "_consumer.out"), "w"), stderr=subprocess.STDOUT)
        prod.stdout.close(); t0 = time.time(); last = t0; a.log("start %s on %d shards, %d at a time" % (key, P, W))
        while cons.poll() is None:
            if a.spot_interrupted():
                for p in (cons, prod):
                    try: p.kill()
                    except Exception: pass
                subprocess.run(["pkill", "-f", "hstage_stream_next.py"], capture_output=True)
                a.finish("INTERRUPTED", "AWS spot interruption notice (tail runner)"); return 0
            if time.time() - last >= 240:
                if a.push_status("EN_COURS", "tail: %s running for %d s; %d done, %d failed" % (key, time.time() - t0, len(a.done_here), nfail)):
                    a.rearm_deadman()
                last = time.time()
            time.sleep(10)
        prod.wait()
        if RJ.done_already(out, job):
            os.makedirs(os.path.join(a.pd, "results"), exist_ok=True)
            shutil.copy(res, os.path.join(a.pd, "results", os.path.basename(res)))
            a.done_here.append(key); a.unpushed.append({"t": round(time.time()), "m": a.name, "op": "done", "jobs": [key]})
            a.log("done %s in %.0f s" % (key, time.time() - t0))
            if a.flush_results("EN_COURS", "tail: %s done in %d s" % (key, time.time() - t0)):      # result on GitHub first
                a.rearm_deadman()
                try: a.sync(claim=False)                                                              # then its done event
                except Exception as e: a.last_err = str(e)[:200]
        else:
            nfail += 1; a.failed_here.append(key); a.log("FAIL %s (producer %s consumer %s)" % (key, prod.returncode, cons.returncode))
            os.makedirs(os.path.join(a.pd, "failed"), exist_ok=True)
            for suffix in ("_consumer.out", "_producer.err"):
                src = os.path.join(out, tag + suffix)
                if os.path.exists(src):
                    with open(src, errors="replace") as x, open(os.path.join(a.pd, "failed", tag + suffix), "w") as y:
                        y.writelines(x.readlines()[-80:])
            a.push_status("EN_COURS", "tail: %s FAILED" % key)
    a.finish("FINI", "tail runner: %d done, %d failed" % (len(a.done_here), nfail))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc(); sys.exit(2)
