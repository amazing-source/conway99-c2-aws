"""Certificate runner (C2 lab, 2026-10-07): one machine certifies the DEFERRED pairs of a share of the swept stream records.

Started by q/qmachine.sh instead of the queue agent when Q_CERT=1 (same install, same calibrations). It claims nothing, publishes
no queue event and never writes the queue branch: it only reads the machine branches (to get the records) and pushes its own
branch run/<NAME>, like the tail runner.
  Q_CERT_MANIFEST=measures/CERT_MANIFEST_2026-10-07.json   list of the records to certify (written by the lab import, path in this repo)
  Q_CERT_PART="i/n"                                         this machine takes the records i, i+n, i+2n, ... of the list, heaviest first
                                                            (default 0/1); n machines with i = 0..n-1 do not overlap
  Q_CERT_WORKERS=8                                          certificates running at the same time (default: number of cores)
  Q_CERT_DONE=q/cert_done.txt                               optional list of keys already certified elsewhere (one per line): skipped
For each record of its share: the record is read from its machine branch (git show origin/<branch>:results/<file>, same sha256 and
same numbers of deferred pairs as the manifest), the package's own producer command for that job is started (through
q/producer_big.py when the record carries merged.producer_max_out) and piped into q/cert_stream.py, which recomputes the stream
sha256 and checks every deferred position in exact integers (y in U, norms 7, orthogonality, a witness root).
One output file per record, certs/<lid>_<k>_<n>.json, pushed to run/<NAME> as the work goes (a record whose file is already there
is skipped: a restarted machine resumes). At the end certs/SUMMARY.json: certified / not certified / failed / skipped.
Exit 0 = finished or interrupted (qmachine.sh then powers the machine off). Nothing here pronounces an exclusion."""
import os, sys, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import qagent as Q


def main():
    a = Q.Agent()
    man = json.load(open(os.path.join(REPO, Q.env("Q_CERT_MANIFEST", "measures/CERT_MANIFEST_2026-10-07.json"))))["records"]
    man.sort(key=lambda m: (-m["n_pairs"], m["key"]))
    i0, n0 = [int(x) for x in Q.env("Q_CERT_PART", "0/1").split("/")]; assert 0 <= i0 < n0
    mine = man[i0::n0]
    W = int(Q.env("Q_CERT_WORKERS", str(max(1, os.cpu_count() or 1))))
    donef = Q.env("Q_CERT_DONE", ""); elsewhere = set()
    if donef and os.path.exists(os.path.join(REPO, donef)): elsewhere = {l.strip() for l in open(os.path.join(REPO, donef)) if l.strip()}
    sys.path.insert(0, a.pkg)
    import run_jobs as RJ                                           # the package's own runner (hashed in MANIFEST.json)
    RJ.check_manifest(); envx = RJ.env_exact(); work = os.path.join(a.pkg, "results_cert"); os.makedirs(work, exist_ok=True)
    jobs = {}
    for j in json.load(open(os.path.join(a.pkg, "jobs.json"))):
        if not j.get("kind") and j["lid"] not in jobs: jobs[j["lid"]] = j          # gamma and plan are the same for every chunk of a lattice
    a.est = {}                                                       # this machine claims nothing
    Q.init_repo(a.qd, a.url); a.fetch()
    try: a.campaign = json.loads(a.show("origin/" + a.qbr, "control.json")).get("campaign", "?")
    except Exception: a.campaign = "?"
    a.log("certificate runner start: %d records of %d (part %d/%d), %d at a time" % (len(mine), len(man), i0, n0, W))
    if not a.push_status("EN_COURS", "certificates: %d records (part %d/%d), %d at a time" % (len(mine), i0, n0, W)):
        raise RuntimeError("cannot push the first status")
    a.rearm_deadman()
    cd = os.path.join(a.pd, "certs"); os.makedirs(cd, exist_ok=True)

    def outfile(m): return os.path.join(cd, "%s_%d_%d.json" % (m["lid"], m["k"], m["n"]))

    todo = []; skipped = 0
    for m in mine:
        if m["key"] in elsewhere or os.path.exists(outfile(m)): skipped += 1
        else: todo.append(m)
    running = {}; ok = []; notok = []; failed = []; last = time.time(); t00 = time.time()

    def start(m):
        tag = "%s_%d_%d" % (m["lid"], m["k"], m["n"]); rec = None
        raw = Q.git(a.qd, "show", "origin/%s:results/%s" % (m["branch"], m["file"]), check=False)
        for l in (raw.stdout or "").splitlines():
            if '"deferred"' not in l: continue
            try: d = json.loads(l)
            except ValueError: continue
            df = d.get("deferred") or {}
            if d.get("sha256") == m["sha256"] and d.get("n_pairs") == m["n_pairs"] and len(df.get("T18", [])) == m["T18"] and len(df.get("T20", [])) == m["T20"]:
                rec = {k: d[k] for k in ("id", "chunk", "sha256", "n_pairs", "deferred")}; break
        if rec is None or m["lid"] not in jobs:
            failed.append(m["key"]); a.log("FAIL %s: record not found on %s" % (m["key"], m["branch"])); return
        recf = os.path.join(work, tag + "_record.json"); json.dump(rec, open(recf, "w"))
        job = jobs[m["lid"]]; U = os.path.join(a.pkg, "external_runs", "structures_3eceb4d", "U", "%s.json" % m["lid"])
        head = [os.path.join(HERE, "producer_big.py"), a.pkg, str(m["producer_max_out"])] if m.get("producer_max_out") else [os.path.join(a.pkg, "c1", "code", "y_pairs_gamma.py")]
        prod = subprocess.Popen([sys.executable] + head + [U, os.path.join(a.pkg, job["gamma"]), os.path.join(work, tag + "_producer_stats.json"),
                                 "--from-plan", os.path.join(a.pkg, job["plan"]), "--chunk", "%d/%d" % (m["k"], m["n"]), "--stream", "-", "--max-seconds", "86400"],
                                env=envx, cwd=os.path.join(a.pkg, "c1", "code"), stdout=subprocess.PIPE,
                                stderr=open(os.path.join(work, tag + "_producer.err"), "w"))      # = run_jobs.start, producer side
        tmp = os.path.join(work, tag + "_cert.json")
        cert = subprocess.Popen([sys.executable, os.path.join(HERE, "cert_stream.py"), a.pkg, m["lid"], recf, tmp], env=envx, cwd=a.pkg,
                                stdin=prod.stdout, stdout=open(os.path.join(work, tag + "_cert.out"), "w"), stderr=subprocess.STDOUT)
        prod.stdout.close(); running[m["key"]] = (m, prod, cert, tmp, tag, time.time())

    def status(state="EN_COURS"):
        return a.push_status(state, "certificates: %d certified, %d not certified, %d failed, %d running, %d left, %d skipped; %.1f h" % (
            len(ok), len(notok), len(failed), len(running), len(todo), skipped, (time.time() - t00) / 3600))

    while todo or running:
        while todo and len(running) < W: start(todo.pop(0))
        for key, (m, prod, cert, tmp, tag, t0) in list(running.items()):
            if cert.poll() is None: continue
            prod.wait(); del running[key]; d = None
            try: d = json.load(open(tmp))
            except Exception: pass
            if d is None or prod.returncode != 0:
                failed.append(key); a.log("FAIL %s (producer %s certifier %s)" % (key, prod.returncode, cert.returncode))
                os.makedirs(os.path.join(a.pd, "failed"), exist_ok=True)
                for suffix in ("_cert.out", "_producer.err"):
                    src = os.path.join(work, tag + suffix)
                    if os.path.exists(src):
                        with open(src, errors="replace") as x, open(os.path.join(a.pd, "failed", tag + suffix), "w") as y: y.writelines(x.readlines()[-60:])
                continue
            d["producer_seconds"] = round(time.time() - t0, 1); d["manifest_branch"] = m["branch"]
            json.dump(d, open(outfile(m), "w"), indent=0)
            (ok if d.get("ok") else notok).append(key); a.done_here.append(key)
            a.log("%s %s in %.0f s" % ("certified" if d.get("ok") else "NOT CERTIFIED", key, time.time() - t0))
        if a.spot_interrupted():
            for (m, prod, cert, tmp, tag, t0) in running.values():
                for p in (cert, prod):
                    try: p.kill()
                    except Exception: pass
            status("INTERRUPTED"); return 0
        if time.time() - last >= 240:
            if status(): a.rearm_deadman()
            last = time.time()
        time.sleep(2)
    json.dump({"part": [i0, n0], "records_in_share": len(mine), "certified": len(ok), "not_certified": sorted(notok), "failed": sorted(failed),
               "skipped_already_done": skipped, "hours": round((time.time() - t00) / 3600, 2)}, open(os.path.join(cd, "SUMMARY_part%dof%d.json" % (i0, n0)), "w"), indent=1)
    status("FINI")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc(); sys.exit(2)
