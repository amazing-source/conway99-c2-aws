"""Checks of the v2 rehearsal (q_v2_rehearsal.yml) on branch queue-ci / run/qci-* (C2, 2026-10-02).
  python3 q/tools/v2_check.py s1 NAME   the machine NAME (Q_TEST, package v2) installed, passed both calibrations, ran its claimed job(s),
                                        pushed each result (chunk_ok, chunk_done, v2 engine sha) BEFORE its done event, and ended FINI.
Exit 0 = PASS."""
import os, sys, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
QBR, PREFIX = "queue-ci", "run/qci-"
V2_ENGINE = None
FAILS = []


def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if check and r.returncode: sys.exit("git %s: %s" % (" ".join(a[:2]), r.stderr))
    return r.stdout


def ok(c, m):
    print(("PASS  " if c else "FAIL  ") + m)
    if not c: FAILS.append(m)


def main():
    name = sys.argv[2]
    git("fetch", "-q", "--prune", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (QBR, QBR), "+refs/heads/%s*:refs/remotes/origin/%s*" % (PREFIX, PREFIX))
    ev = [json.loads(l) for l in git("show", "origin/%s:events.jsonl" % QBR).splitlines() if l.strip()]
    st = dict(l.split("=", 1) for l in git("show", "origin/run/%s:status.txt" % name).splitlines() if "=" in l)
    ok(st.get("STATE") == "FINI", "%s ended FINI (state %s, reason %s)" % (name, st.get("STATE"), st.get("REASON")))
    ok(st.get("PKG") == "v2", "%s reports package v2 (PKG=%s)" % (name, st.get("PKG")))
    man = json.load(open(os.path.join(os.path.expanduser("~"), "c2_cloud_run", "MANIFEST.json")))
    eng = man["engine_code_sha"]
    done = [j for e in ev if e["m"] == name and e["op"] == "done" for j in e["jobs"]]
    ok(len(done) >= 1, "%s completed %d job(s): %s" % (name, len(done), done))
    for j in done:
        lid, k, n = j.split(":"); f = "results/%s_%s_%s.jsonl" % (lid, k, n)
        txt = git("show", "origin/run/%s:%s" % (name, f), check=False)
        recs = [json.loads(l) for l in txt.splitlines() if l.strip()]
        r = recs[-1] if recs else {}
        ok(bool(r.get("chunk_ok")) and bool(r.get("chunk_done")), "%s: chunk_ok %s chunk_done %s verdicts %s" % (f, r.get("chunk_ok"), r.get("chunk_done"), r.get("verdicts")))
        ok(r.get("code_sha") == eng, "%s: engine %s == package v2 engine %s" % (f, r.get("code_sha"), eng))
    print("RESULT:", "PASS" if not FAILS else "FAIL (%d)" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__" and sys.argv[1] == "s1":
    main()
