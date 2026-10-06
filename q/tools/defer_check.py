"""Checks of the deferral rehearsal (q_defer_rehearsal.yml; C2, 2026-10-06 night): machine NAME ran the rehearsal jobs with Q_DEFER=1 on
queue branch queue-cid, run branch run/NAME. Reference: the records of the SAME jobs made in normal mode by the v10 rehearsal
(branch run/qci-v10a).
  python3 q/tools/defer_check.py NAME          (NAME = qci-<Q_TEST_NAME>)
For every job: done event with defer = 1, pushed record with chunk_ok, the package engine sha, the deferral marker, and
  n_pairs (and the stream sha256 / the pair-file sha256) identical to the normal record;
  every verdict that is not a search verdict has exactly the normal count;
  DEFERRED + search verdicts of the deferral record = search verdicts of the normal record (so no pair is lost or added);
  chunk_done is false exactly when a pair is deferred; a DEFERRED pair is never counted as excluded.
Exit 0 = PASS."""
import os, sys, json, subprocess
QBR, PREFIX, REF = "queue-cid", "run/", "run/qci-v10a"
FAILS = []


def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if check and r.returncode: sys.exit("git %s: %s" % (" ".join(a[:2]), r.stderr))
    return r.stdout


def ok(c, m):
    print(("PASS  " if c else "FAIL  ") + m)
    if not c: FAILS.append(m)


def last(branch, f):
    recs = [json.loads(l) for l in git("show", "origin/%s:%s" % (branch, f), check=False).splitlines() if l.strip()]
    return recs[-1] if recs else {}


def main():
    name = sys.argv[1]; S = lambda v: "stage 1" in v or "star" in v or "Lemma Z" in v
    git("fetch", "-q", "--prune", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (QBR, QBR), "+refs/heads/%s*:refs/remotes/origin/%s*" % (PREFIX, PREFIX),
        "+refs/heads/%s:refs/remotes/origin/%s" % (REF, REF))
    ev = [json.loads(l) for l in git("show", "origin/%s:events.jsonl" % QBR).splitlines() if l.strip()]
    st = dict(l.split("=", 1) for l in git("show", "origin/%s%s:status.txt" % (PREFIX, name)).splitlines() if "=" in l)
    ok(st.get("STATE") == "FINI", "%s ended FINI (state %s, reason %s)" % (name, st.get("STATE"), st.get("REASON")))
    ok(st.get("PKG") == os.environ.get("EXPECT_PKG", "v10"), "%s reports package PKG=%s" % (name, st.get("PKG")))
    dn = [e for e in ev if e["m"] == name and e["op"] == "done"]; done = [j for e in dn for j in e["jobs"]]
    want = [j for j in os.environ.get("EXPECT_JOBS", "").split(",") if j]
    ok(sorted(done) == sorted(want), "%s completed %s (expected %s)" % (name, sorted(done), sorted(want)))
    ok(all(e.get("defer") == 1 for e in dn), "every done event carries defer = 1")
    ndef = 0
    for j in done:
        lid, k, n = j.split(":"); f = "results/%s_%s_%s.jsonl" % (lid, k, n)
        r = last(PREFIX + name, f); a = last(REF, f); v = r.get("verdicts", {}); av = a.get("verdicts", {})
        print("--- %s\n      deferral: %s\n      normal:   %s" % (j, v, av))
        ok(bool(a.get("chunk_ok")) and bool(a.get("chunk_done")), "%s: the normal record exists and is chunk_done" % j)
        ok(r.get("chunk_ok") is True, "%s: chunk_ok" % j)
        ok(r.get("code_sha") == a.get("code_sha"), "%s: same engine sha as the normal record" % j)
        golay = r.get("kind") == "golay_pairs"
        mark = r.get("deferral", {}) if golay else r.get("merged", {})
        ok(mark.get("defer_nodes") == 10000 and bool(mark.get("defer_consumer_sha256")) and (golay or mark.get("defer") is True), "%s: deferral marker %s" % (j, {x: mark.get(x) for x in ("defer", "defer_nodes", "defer_consumer_sha256")}))
        for fld in ("n_pairs", "pair_files_sha256", "range") if golay else ("n_pairs", "sha256", "orbits", "twin_deferred"):
            ok(r.get(fld) == a.get(fld), "%s: %s identical to the normal record" % (j, fld))
        d = sum(c for x, c in v.items() if x.startswith("DEFERRED")); ndef += d
        ok(all(v.get(x, 0) == c for x, c in av.items() if not S(x)) and all(x in av or x.startswith("DEFERRED") for x in v), "%s: every non-search verdict has exactly the normal count" % j)
        ok(d + sum(c for x, c in v.items() if S(x)) == sum(c for x, c in av.items() if S(x)) and all(v.get(x, 0) <= c for x, c in av.items()),
           "%s: %d deferred + %d searched here = %d searched in normal mode" % (j, d, sum(c for x, c in v.items() if S(x)), sum(c for x, c in av.items() if S(x))))
        ok(r.get("chunk_done") is (d == 0), "%s: chunk_done %s with %d deferred pairs" % (j, r.get("chunk_done"), d))
        if golay:
            ok(len(r.get("not_excluded", [])) == d, "%s: not_excluded lists the %d deferred pairs" % (j, d))
        else:
            dd = r.get("deferred", {}); pos = dd.get("T18", []) + dd.get("T20", [])
            ok(len(pos) == d == len(set(pos)) and all(0 <= p < r["n_pairs"] for p in pos) and not r.get("not_excluded"), "%s: %d distinct stream positions listed, not_excluded empty" % (j, len(pos)))
    ok(ndef > 0, "at least one pair was deferred in the rehearsal (%d), so the deferral path was exercised" % ndef)
    print("RESULT:", "PASS" if not FAILS else "FAIL (%d)" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
