"""Validation of q/par_consumer.py on real jobs (laptop): run the package's producer piped into the parallel wrapper and compare
the merged record with the record the SAME job produced on AWS with the unsplit v10 consumer. Must be identical on:
n_pairs, sha256, orbits, verdicts, twin_deferred, not_excluded, chunk_ok, chunk_done, code_sha, node_limit, producer.
  <venv python> par_test.py <repo> <pkg> <P> <key> [<key> ...]"""
import sys, os, json, subprocess, io, zipfile, time
REPO, PKG, P, KEYS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4:]
sys.path.insert(0, PKG)
import run_jobs as RJ
env = RJ.env_exact(); out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "par_test_out"); os.makedirs(out, exist_ok=True)
jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(PKG, "jobs.json")))}
# AWS records of these jobs
ref = {}
for r in subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*"], capture_output=True, text=True).stdout.split():
    data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", r, "results"], capture_output=True).stdout
    if not data: continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for key in KEYS:
        lid, k, n = key.split(":"); f = "results/%s_%s_%s.jsonl" % (lid, k, n)
        if f in z.namelist():
            for l in z.read(f).decode().splitlines():
                d = json.loads(l)
                if d.get("code_sha", {}).get("frame_dfs_next.py") == "1591aeeac9c0be5c" and "merged" not in d: ref[key] = d
allok = True
for key in KEYS:
    job = jobs[key]; lid, k, n = job["lid"], job["k"], job["n"]; tag = "%s_%d_%d" % (lid, k, n); res = os.path.join(out, tag + ".jsonl")
    if os.path.exists(res): os.remove(res)
    U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid); t = time.time()
    prod = subprocess.Popen([sys.executable, os.path.join(PKG, "c1", "code", "y_pairs_gamma.py"), U, os.path.join(PKG, job["gamma"]), os.path.join(out, tag + "_stats.json"),
                             "--from-plan", os.path.join(PKG, job["plan"]), "--chunk", "%d/%d" % (k, n), "--stream", "-", "--max-seconds", "86400"],
                            env=env, cwd=os.path.join(PKG, "c1", "code"), stdout=subprocess.PIPE, stderr=open(os.path.join(out, tag + "_producer.err"), "w"))
    cons = subprocess.Popen([sys.executable, os.path.join(REPO, "q", "par_consumer.py"), PKG, lid, "-", res, "4000000000"] + P.split("/"), env=env, cwd=PKG, stdin=prod.stdout,
                            stdout=open(os.path.join(out, tag + "_consumer.out"), "w"), stderr=subprocess.STDOUT)
    prod.stdout.close(); cons.wait(); prod.wait(); dt = time.time() - t
    got = json.loads([l for l in open(res) if l.strip()][-1]); a = ref.get(key)
    print("\n%s: laptop %.0f s with %s shards (AWS unsplit: %s s) | done_already=%s" % (key, dt, got["merged"]["shards"], a and a.get("wall_secs"), RJ.done_already(out, job)))
    if a is None:
        print("   no AWS record to compare with"); allok = False; continue
    for f in ("n_pairs", "sha256", "orbits", "verdicts", "twin_deferred", "not_excluded", "chunk_ok", "chunk_done", "code_sha", "node_limit", "producer", "chunk", "id", "frame_dfs"):
        same = got.get(f) == a.get(f); allok &= same
        print("   %-14s %s%s" % (f, "IDENTICAL" if same else "DIFFERENT", "" if same else "  got %s | AWS %s" % (str(got.get(f))[:150], str(a.get(f))[:150])))
    ts = {k: sum(v.values()) for k, v in got["telemetry"].items()} == {k: sum(v.values()) for k, v in a["telemetry"].items()} and got["telemetry"]["trap_Yz"] == a["telemetry"]["trap_Yz"] and got["telemetry"]["search_K"] == a["telemetry"]["search_K"]
    print("   %-14s %s" % ("telemetry", "IDENTICAL counts (trap_Yz, search_K, totals)" if ts else "DIFFERENT")); allok &= ts
    print("   keys only in merged: %s | missing from merged: %s | bad: %s" % (sorted(set(got) - set(a)), sorted(set(a) - set(got)), got["merged"]["bad"]))
print("\nPAR CONSUMER VALIDATION:", "PASS" if allok else "FAIL")
