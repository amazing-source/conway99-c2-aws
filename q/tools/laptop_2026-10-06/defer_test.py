"""Validation of the deferral mode (Q_DEFER=1: q/par_consumer.py -> q/defer_consumer.py) on real jobs, against the record the
same job produced on AWS with the unsplit v10 consumer:
  (a) n_pairs, sha256, producer, chunk_ok, code_sha identical; chunk_done false as soon as a pair is deferred;
  (b) every verdict that is not a search verdict (swap, twin, char-vector trap, dual minimum 9/7, ...) has exactly the AWS count,
      twin_deferred is identical, and every search verdict count is <= the AWS count;
  (c) the deferred lines, fed alone to the plain package consumer with the production limit, are all decided by a search, and
      their verdict counts added to the deferral record's (DEFERRED verdicts removed) are exactly the AWS verdict counts.
  <venv python> defer_test.py <repo> <pkg> <key> [<key> ...]"""
import sys, os, json, subprocess, io, zipfile, time, collections, hashlib
REPO, PKG, KEYS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3:]
sys.path.insert(0, PKG)
import run_jobs as RJ
env = RJ.env_exact(); out = os.path.join(os.path.dirname(PKG), "defer_test_out"); os.makedirs(out, exist_ok=True)
jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(PKG, "jobs.json")))}
ref = {}
for r in subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*"], capture_output=True, text=True).stdout.split():
    data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", r, "results"], capture_output=True).stdout
    if not data:
        continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for key in KEYS:
        lid, k, n = key.split(":"); f = "results/%s_%s_%s.jsonl" % (lid, k, n)
        if f in z.namelist():
            for l in z.read(f).decode().splitlines():
                d = json.loads(l)
                if d.get("code_sha", {}).get("frame_dfs_next.py") == "1591aeeac9c0be5c" and "merged" not in d:
                    ref[key] = d
allok = True


def check(c, m):
    global allok
    allok = allok and bool(c); print("   %s  %s" % ("PASS" if c else "FAIL", m))


def searched(v):
    return sum(c for k_, c in v.items() if "stage 1" in k_ or "star" in k_ or "Lemma Z" in k_)


for key in KEYS:
    job = jobs[key]; lid, k, n = job["lid"], job["k"], job["n"]; tag = "%s_%d_%d" % (lid, k, n)
    U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)
    stream = os.path.join(out, tag + "_stream.jsonl")
    with open(stream, "wb") as fh:                                  # the producer stream, kept to rebuild the deferred lines
        subprocess.run([sys.executable, os.path.join(PKG, "c1", "code", "y_pairs_gamma.py"), U, os.path.join(PKG, job["gamma"]), os.path.join(out, tag + "_stats.json"),
                        "--from-plan", os.path.join(PKG, job["plan"]), "--chunk", "%d/%d" % (k, n), "--stream", "-", "--max-seconds", "86400"],
                       env=env, cwd=os.path.join(PKG, "c1", "code"), stdout=fh, stderr=open(os.path.join(out, tag + "_producer.err"), "w"), check=True)
    res = os.path.join(out, tag + "_defer.jsonl")
    if os.path.exists(res):
        os.remove(res)
    t = time.time()
    subprocess.run([sys.executable, os.path.join(REPO, "q", "par_consumer.py"), PKG, lid, stream, res, "4000000000", "1", "1"], env=dict(env, Q_DEFER="1", Q_DEFER_NODES=os.environ.get("Q_DEFER_NODES", "10000")), cwd=PKG,
                   stdout=open(os.path.join(out, tag + "_defer.out"), "w"), stderr=subprocess.STDOUT)
    td = time.time() - t
    if not os.path.exists(res):
        print("\n%s: no record written; log:\n%s" % (key, open(os.path.join(out, tag + "_defer.out")).read()[-1500:])); allok = False; continue
    got = json.loads([l for l in open(res) if l.strip()][-1]); a = ref[key]
    d18, d20 = got.get("deferred", {}).get("T18", []), got.get("deferred", {}).get("T20", [])
    print("\n%s: %d pairs, deferred T18 %d, T20 %d | deferral run %.0f s on the laptop (AWS full run: %s s)" % (key, got["n_pairs"], len(d18), len(d20), td, a.get("wall_secs")))
    for f in ("n_pairs", "sha256", "producer", "chunk_ok", "code_sha", "chunk", "id"):
        check(got.get(f) == a.get(f), "%s identical to the AWS record" % f)
    check(got["chunk_done"] is (len(d18) + len(d20) == 0), "chunk_done is %s with %d deferred pairs" % (got["chunk_done"], len(d18) + len(d20)))
    gv = {k_: v for k_, v in got["verdicts"].items() if not k_.startswith("DEFERRED")}
    check(sum(v for k_, v in got["verdicts"].items() if k_.startswith("DEFERRED")) == len(d18) + len(d20), "DEFERRED verdict counts = lengths of the index lists")
    check(all(gv.get(k_, 0) <= a["verdicts"].get(k_, 0) for k_ in gv), "every verdict count <= the AWS count")
    S_ = lambda k_: "stage 1" in k_ or "star" in k_ or "Lemma Z" in k_
    check(all(gv.get(k_, 0) == c for k_, c in a["verdicts"].items() if not S_(k_) and (os.environ.get("Q_DEFER_NODES") != "0" or "char" in k_ or "dual min" in k_ or not k_.startswith("EXCLUDED") or "twin" in k_)),
          "every non-search verdict has exactly the AWS count (quick variant: a pair-setup exclusion may be deferred instead)")
    check(got.get("twin_deferred", {}) == a.get("twin_deferred", {}), "twin_deferred identical to the AWS record")
    check(not got["not_excluded"], "not_excluded holds no pair besides the deferred ones (moved to the index lists)")
    lines = [l.rstrip(b"\r\n") for l in open(stream, "rb") if l.strip()]
    recs = [json.loads(l) for l in lines]
    info = [l for l, r_ in zip(lines, recs) if not r_.get("end") and ("o" not in r_ or "y1" not in r_)]
    pl = [l for l, r_ in zip(lines, recs) if not r_.get("end") and "o" in r_ and "y1" in r_]
    check(len(pl) == got["n_pairs"], "stream has %d pair lines" % len(pl))
    sel = [pl[i] for i in sorted(d18 + d20)]; sh = hashlib.sha256()
    for l in sel:
        sh.update(l + b"\n")
    dfile = os.path.join(out, tag + "_deferred_only.jsonl")
    with open(dfile, "wb") as fh:
        for l in info + sel:
            fh.write(l + b"\n")
        fh.write(json.dumps({"end": True, "id": int(lid), "chunk": [k, n], "pairs": len(sel), "complete": True, "sha256": sh.hexdigest()}).encode() + b"\n")
    r2 = os.path.join(out, tag + "_deferred_only_res.jsonl")
    if os.path.exists(r2):
        os.remove(r2)
    t = time.time()
    subprocess.run([sys.executable, os.path.join(PKG, "scripts", "hstage_stream_next.py"), lid, dfile, r2, "4000000000"], env=env, cwd=PKG,
                   stdout=open(os.path.join(out, tag + "_deferred_only.out"), "w"), stderr=subprocess.STDOUT)
    b = json.loads([l for l in open(r2) if l.strip()][-1])
    tot = collections.Counter(gv); tot.update(b["verdicts"])
    check(b["chunk_ok"] and b["n_pairs"] == len(sel), "deferred pairs re-run alone: %d pairs, chunk_ok %s, %.0f s" % (b["n_pairs"], b["chunk_ok"], time.time() - t))
    print("        their verdicts: %s" % b["verdicts"])
    check(all(k_.startswith("EXCLUDED") for k_ in b["verdicts"]) and (os.environ.get("Q_DEFER_NODES") == "0" or all(S_(k_) for k_ in b["verdicts"])),
          "every deferred pair is excluded in the full run (budget variant: by a search)")
    check(dict(tot) == a["verdicts"], "deferral record + deferred pairs re-run = AWS verdicts exactly")
    td_ = collections.Counter(got.get("twin_deferred", {})); td_.update(b.get("twin_deferred", {}))
    check(dict(td_) == a.get("twin_deferred", {}), "twin_deferred adds up to the AWS record")
    check(not got["not_excluded"] and not b["not_excluded"] and not a["not_excluded"], "no not_excluded pair anywhere")
    print("   searched pairs: AWS %d -> deferral run %d (%.1f %% of the searches set aside)" % (searched(a["verdicts"]), searched(gv), 100.0 * (searched(a["verdicts"]) - searched(gv)) / max(1, searched(a["verdicts"]))))
print("\nDEFERRAL VALIDATION:", "PASS" if allok else "FAIL")
