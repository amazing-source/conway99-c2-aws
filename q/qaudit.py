"""Rigid-kernel audit runner (C2 lab, 2026-10-07): one machine regenerates a share of the pair streams of the lattices at risk and
passes them through q/audit_rigid.py. Same shape as q/qcert.py: started by q/qmachine.sh instead of the queue agent when Q_AUDIT=1
(same install, same calibrations); it claims nothing, publishes no queue event, never writes the queue branch; it pushes only its
own branch run/<NAME>.
  Q_AUDIT_MANIFEST=measures/AUDIT_RIGID_MANIFEST_2026-10-07.json   the jobs (written by the lab): lid, k, n, gamma, plan, batch
  Q_AUDIT_BATCH=1                                                  only the jobs of this batch (1 = the lattices already counted as
                                                                   excluded, 2 = the open ones); default: all
  Q_AUDIT_LIDS="137 138 105 ..."                                   only these lattices, in this order (after the batch filter)
  Q_AUDIT_PART="i/n"                                               this machine takes the jobs i, i+n, ... of the (filtered) list
  Q_AUDIT_WORKERS=8                                                jobs running at the same time (default: number of cores)
A job with "consumer": "sweep" in the manifest is piped into the package's own consumer scripts/hstage_stream_next.py instead (a normal
sweep record, copied to results/<lid>_<k>_<n>.jsonl): used to pass a lattice that is not in the package's job list through the engine.
A job = the package's own producer for chunk k/n of the lattice (with --from-plan when the manifest gives a plan; gamma and plan
paths starting with "repo:" are files of this repository, the others are files of the package), piped into q/audit_rigid.py.
A job with "producer_max_out" runs its producer through q/producer_big.py with that cap (the package's producer stops the y2 of one y1
at 10^6 candidates and then says complete = false: such a job FAILS here, it is never counted as audited).
A job with "lll" (a json of reduced bases, "repo:" path) runs its producer through q/producer_lll.py, so that a plan made on the lab PC
is valid on this machine for a lattice that is not in the package's basis cache.
One output file per job, audit/<lid>_<k>_<n>.json, pushed to run/<NAME> as the work goes; a job whose file is already there is
skipped (a restarted machine resumes). At the end audit/SUMMARY_*.json: per lattice, pairs, pairs with a zero-footprint candidate,
general, exposed, exposed pairs not excluded again, jobs failed. Exit 0 = finished or interrupted."""
import os, sys, json, time, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import qagent as Q


def main():
    a = Q.Agent()
    man = json.load(open(os.path.join(REPO, Q.env("Q_AUDIT_MANIFEST", "measures/AUDIT_RIGID_MANIFEST_2026-10-07.json"))))["jobs"]
    batch = Q.env("Q_AUDIT_BATCH", "")
    if batch: man = [m for m in man if str(m.get("batch")) == batch]
    lids = (Q.env("Q_AUDIT_LIDS", "") or "").split()                 # optional: only these lattices, in the order given
    if lids: man = [m for l in lids for m in man if m["lid"] == l]
    i0, n0 = [int(x) for x in Q.env("Q_AUDIT_PART", "0/1").split("/")]; assert 0 <= i0 < n0
    mine = man[i0::n0]
    W = int(Q.env("Q_AUDIT_WORKERS", str(max(1, os.cpu_count() or 1))))
    sys.path.insert(0, a.pkg)
    import run_jobs as RJ
    RJ.check_manifest(); envx = RJ.env_exact(); work = os.path.join(a.pkg, "results_audit"); os.makedirs(work, exist_ok=True)
    a.est = {}
    Q.init_repo(a.qd, a.url); a.fetch(queue_only=True)
    try: a.campaign = json.loads(a.show("origin/" + a.qbr, "control.json")).get("campaign", "?")
    except Exception: a.campaign = "?"
    a.log("rigid-kernel audit start: %d jobs of %d (part %d/%d, batch %s), %d at a time" % (len(mine), len(man), i0, n0, batch or "all", W))
    if not a.push_status("EN_COURS", "rigid audit: %d jobs (part %d/%d, batch %s), %d at a time" % (len(mine), i0, n0, batch or "all", W)):
        raise RuntimeError("cannot push the first status")
    a.rearm_deadman()
    od = os.path.join(a.pd, "audit"); os.makedirs(od, exist_ok=True)

    def path(p): return os.path.join(REPO, p[5:]) if p.startswith("repo:") else os.path.join(a.pkg, p)
    def outfile(m): return os.path.join(od, "%s_%d_%d.json" % (m["lid"], m["k"], m["n"]))
    todo = [m for m in mine if not os.path.exists(outfile(m))]; skipped = len(mine) - len(todo)
    running = {}; done = []; notok = []; failed = []; last = time.time(); t00 = time.time()

    def start(m):
        tag = "%s_%d_%d" % (m["lid"], m["k"], m["n"])
        U = os.path.join(a.pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % m["lid"])
        # a job with "producer_max_out" runs the producer through q/producer_big.py (raised cap on the y2 candidates of one y1), as the sweep did
        head = [os.path.join(HERE, "producer_big.py"), a.pkg, str(m["producer_max_out"])] if m.get("producer_max_out") else [os.path.join(a.pkg, "c1", "code", "y_pairs_gamma.py")]
        # a job with "lll" runs the producer through q/producer_lll.py: the lab PC's reduced basis for a lattice outside the package's basis cache
        if m.get("lll"): head = [os.path.join(HERE, "producer_lll.py"), a.pkg, path(m["lll"]), str(m.get("producer_max_out") or 0)]
        cmd = [sys.executable] + head + [U, path(m["gamma"]), os.path.join(work, tag + "_producer_stats.json")]
        if m.get("plan"): cmd += ["--from-plan", path(m["plan"])]
        if m["n"] > 1: cmd += ["--chunk", "%d/%d" % (m["k"], m["n"])]
        cmd += ["--stream", "-", "--max-seconds", "86400"]
        prod = subprocess.Popen(cmd, env=envx, cwd=os.path.join(a.pkg, "c1", "code"), stdout=subprocess.PIPE, stderr=open(os.path.join(work, tag + "_producer.err"), "w"))
        if m.get("consumer") == "sweep":                               # the package's own stream consumer: a normal sweep record
            tmp = os.path.join(work, tag + ".jsonl")
            if os.path.exists(tmp): os.remove(tmp)
            aud = subprocess.Popen([sys.executable, os.path.join(a.pkg, "scripts", "hstage_stream_next.py"), m["lid"], "-", tmp, "4000000000"], env=envx, cwd=a.pkg,
                                   stdin=prod.stdout, stdout=open(os.path.join(work, tag + "_audit.out"), "w"), stderr=subprocess.STDOUT)
        else:
            tmp = os.path.join(work, tag + "_audit.json")
            aud = subprocess.Popen([sys.executable, os.path.join(HERE, "audit_rigid.py"), a.pkg, m["lid"], tmp, str(m["k"]), str(m["n"])], env=envx, cwd=a.pkg,
                                   stdin=prod.stdout, stdout=open(os.path.join(work, tag + "_audit.out"), "w"), stderr=subprocess.STDOUT)
        prod.stdout.close(); running[tag] = (m, prod, aud, tmp, time.time())

    def status(state="EN_COURS"):
        return a.push_status(state, "rigid audit: %d jobs done (%d with a pair not excluded again), %d failed, %d running, %d left, %d skipped; %.1f h" % (
            len(done), len(notok), len(failed), len(running), len(todo), skipped, (time.time() - t00) / 3600))

    while todo or running:
        while todo and len(running) < W: start(todo.pop(0))
        for tag, (m, prod, aud, tmp, t0) in list(running.items()):
            if aud.poll() is None: continue
            prod.wait(); del running[tag]; d = None
            try:
                if m.get("consumer") == "sweep":                       # last record of the consumer's jsonl; same fields for the bookkeeping below
                    r = [json.loads(l) for l in open(tmp) if l.strip()][-1]
                    open_ = [x for x in (r.get("not_excluded") or [])]
                    d = dict(r, stream_ok=bool(r.get("chunk_ok")), ok=bool(r.get("chunk_done")), counts=r.get("verdicts", {}), exposed_not_excluded_again=len(open_))
                else: d = json.load(open(tmp))
            except Exception: pass
            if d is None or prod.returncode != 0 or not d.get("stream_ok"):
                failed.append(tag); a.log("FAIL %s (producer %s audit %s)" % (tag, prod.returncode, aud.returncode))
                os.makedirs(os.path.join(a.pd, "failed"), exist_ok=True)
                for suffix in ("_audit.out", "_producer.err"):
                    src = os.path.join(work, tag + suffix)
                    if os.path.exists(src):
                        with open(src, errors="replace") as x, open(os.path.join(a.pd, "failed", tag + suffix), "w") as y: y.writelines(x.readlines()[-60:])
                continue
            d["job_seconds"] = round(time.time() - t0, 1)
            json.dump(d, open(outfile(m), "w"), indent=0); done.append(tag); a.done_here.append(tag)
            if m.get("consumer") == "sweep":                           # also the record itself, where the lab importer reads sweep records
                os.makedirs(os.path.join(a.pd, "results"), exist_ok=True)
                with open(tmp) as x, open(os.path.join(a.pd, "results", tag + ".jsonl"), "w") as y: y.write(x.read())
            if not d.get("ok"): notok.append(tag)
            a.log("%s %s in %.0f s: pairs %d, counts %s" % ("audited" if d.get("ok") else "NOT OK", tag, time.time() - t0, d["n_pairs"], d["counts"]))
        if a.spot_interrupted():
            for (m, prod, aud, tmp, t0) in running.values():
                for p in (aud, prod):
                    try: p.kill()
                    except Exception: pass
            status("INTERRUPTED"); return 0
        if time.time() - last >= 240:
            if status(): a.rearm_deadman()
            last = time.time()
        time.sleep(2)
    per = collections.defaultdict(lambda: collections.Counter())
    for f in sorted(os.listdir(od)):
        if not f.endswith(".json") or f.startswith("SUMMARY"): continue
        d = json.load(open(os.path.join(od, f))); c = per["%03d" % d["id"]]
        c["jobs"] += 1; c["pairs"] += d["n_pairs"]; c["exposed_not_excluded_again"] += d["exposed_not_excluded_again"]
        for k, v in d["counts"].items(): c[k] += v
    json.dump({"part": [i0, n0], "batch": batch or "all", "jobs_in_share": len(mine), "done_here": len(done), "failed": sorted(failed),
               "jobs_with_a_pair_not_excluded_again": sorted(notok), "skipped_already_done": skipped, "per_lattice": {k: dict(v) for k, v in sorted(per.items())},
               "hours": round((time.time() - t00) / 3600, 2)}, open(os.path.join(od, "SUMMARY_part%dof%d_batch%s.json" % (i0, n0, batch or "all")), "w"), indent=1)
    status("FINI")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc(); sys.exit(2)
