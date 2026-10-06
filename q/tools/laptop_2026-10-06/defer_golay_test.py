"""Validation of the deferral mode on golay_pairs jobs (q/defer_consumer.py --golay), against the record the same block produced on
AWS with the plain package script:
  (a) n_pairs, range, pair_files_sha256, code_sha identical; chunk_ok true; chunk_done false as soon as a pair is deferred;
  (b) every verdict that is not a search verdict has exactly the AWS count; every search verdict count is <= the AWS count;
  (c) the deferred pairs (listed in not_excluded with their index), run alone through the package's own run_pair, are all decided by
      a search, and their verdict counts added to the deferral record's (DEFERRED removed) are exactly the AWS verdict counts.
  <venv python> defer_golay_test.py <repo> <pkg> <key> [<key> ...]"""
import sys, os, json, subprocess, io, zipfile, time, collections, glob
REPO, PKG, KEYS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3:]
sys.path.insert(0, PKG); sys.path.insert(0, os.path.join(PKG, "scripts"))
import run_jobs as RJ
env = RJ.env_exact(); out = os.path.join(os.path.dirname(PKG), "defer_test_out"); os.makedirs(out, exist_ok=True)
os.environ.update({k: v for k, v in env.items() if k.startswith("FD_") or k.endswith("_NUM_THREADS")})
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
                if d.get("code_sha", {}).get("frame_dfs_next.py") == "1591aeeac9c0be5c" and "deferral" not in d:
                    ref[key] = d
allok = True


def check(c, m):
    global allok
    allok = allok and bool(c); print("   %s  %s" % ("PASS" if c else "FAIL", m), flush=True)


S_ = lambda k_: "stage 1" in k_ or "star" in k_ or "Lemma Z" in k_
for key in KEYS:
    lid, k, n = key.split(":"); tag = "%s_%s_%s" % (lid, k, n); res = os.path.join(out, tag + "_defer.jsonl")
    if os.path.exists(res):
        os.remove(res)
    t = time.time()
    subprocess.run([sys.executable, os.path.join(REPO, "q", "defer_consumer.py"), PKG, "--golay", lid, k, n, res], env=dict(env, Q_DEFER="1", Q_DEFER_NODES=os.environ.get("Q_DEFER_NODES", "10000")), cwd=PKG,
                   stdout=open(os.path.join(out, tag + "_defer.out"), "w"), stderr=subprocess.STDOUT)
    td = time.time() - t
    if not os.path.exists(res):
        print("\n%s: no record written; log:\n%s" % (key, open(os.path.join(out, tag + "_defer.out")).read()[-1500:])); allok = False; continue
    got = json.loads([l for l in open(res) if l.strip()][-1]); a = ref[key]
    dfr = [e for e in got["not_excluded"] if e["verdict"].startswith("DEFERRED")]
    print("\n%s: %d pairs, %d deferred | deferral run %.0f s on the laptop (AWS full run: %s s)" % (key, got["n_pairs"], len(dfr), td, a.get("wall_secs")), flush=True)
    print("        deferral verdicts: %s" % got["verdicts"]); print("        AWS verdicts:      %s" % a["verdicts"])
    for f in ("n_pairs", "range", "pairs_total", "pair_files_sha256", "code_sha", "chunk", "id", "chunk_ok"):
        check(got.get(f) == a.get(f), "%s identical to the AWS record" % f)
    check(got["chunk_done"] is (len(dfr) == 0), "chunk_done is %s with %d deferred pairs" % (got["chunk_done"], len(dfr)))
    check("deferral" in got and got["deferral"]["defer_nodes"] == int(os.environ.get("Q_DEFER_NODES", "10000")), "record carries the deferral field")
    gv = {k_: v for k_, v in got["verdicts"].items() if not k_.startswith("DEFERRED")}
    check(sum(v for k_, v in got["verdicts"].items() if k_.startswith("DEFERRED")) == len(dfr) == len(got["not_excluded"]), "not_excluded = the deferred pairs, nothing else")
    check(all(gv.get(k_, 0) <= a["verdicts"].get(k_, 0) for k_ in gv), "every verdict count <= the AWS count")
    check(all(gv.get(k_, 0) == c for k_, c in a["verdicts"].items() if not S_(k_)), "every non-search verdict has exactly the AWS count")
    # (c) the deferred pairs through the package's own per-pair logic
    import numpy as np
    from fractions import Fraction as F
    import golay_pairs_job as GJ
    from frame_dfs_next import lattice_data
    import twin_transfer as TT
    files = sorted(glob.glob(os.path.join(PKG, "data", "golay", lid, "pairs_*.json")))
    (basis, scale, frame), fsha, N, a0, b0, pairs = GJ.load_block(files, int(k), int(n))
    L = lattice_data([[F(x) for x in row] for row in basis], F(1, int(scale))); Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
    conv = lambda v: np.rint(np.array([float(F(x)) for x in v]) @ Binv).astype(np.int64)
    CL = TT.classes(); bc = collections.Counter(); t = time.time()
    for e in dfr:
        c1, (s1, s2) = pairs[e["index"] - a0]
        check([str(x) for x in s1] == e["y1"] and [str(x) for x in s2] == e["y2"], "deferred index %d is that pair of the block" % e["index"])
        v, nodes, info = GJ.run_pair(L, conv(s1), conv(s2), CL); bc[v] += 1
        print("        index %d: %s -> full run: %s (%s nodes)" % (e["index"], e["verdict"][:22], v, sum(nodes) if nodes else None), flush=True)
    check(all(k_.startswith("EXCLUDED") for k_ in bc), "every deferred pair is excluded in the full run (%.0f s)" % (time.time() - t))
    tot = collections.Counter(gv); tot.update(bc)
    check(dict(tot) == a["verdicts"], "deferral record + deferred pairs re-run = AWS verdicts exactly")
print("\nGOLAY DEFERRAL VALIDATION:", "PASS" if allok else "FAIL")
