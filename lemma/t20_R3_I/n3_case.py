# T20 round 3, case I, branch n_3 = 2: ONE case (graph, type of z, profile) through the pipeline, sequentially.
#   first   : stage 1 (stage1c.py ... z=...)  ->  <out>/s1z/s1z_<tag>.json ; stage 2 (run_stage2.py, one part)
#             ->  <out>/s2z/<tag>_0of1.jsonl ; summary2.py  ->  <out>/s2z/summary_<tag>.out
#   second  : in_verify.py basesz (one part) ; follow ; mergez  ->  <out>/vz/verify_<tag>.out
# A step whose output exists is skipped.  <tag> = <graph without dot>_<profile>_t<k>, k = index of the type in
# ztypes.json (classes of the types (U3 ; V3) of z under Aut(B) x (z <-> sigma z)).
# usage: python n3_case.py <out dir> <tag> first|second|both
import sys, json, os, subprocess
out, tag, what = sys.argv[1], sys.argv[2], sys.argv[3]
g, prof, t = tag.split("_")
graph = g[0] + "." + g[1:]
r = json.load(open("ztypes.json"))[graph][int(t[1:])]
zs = "%s:%s" % (",".join(map(str, r["U"])), ",".join(map(str, r["V"])))
for d in ("s1z", "s2z", "vz"):
    os.makedirs(os.path.join(out, d), exist_ok=True)
py = sys.executable
s1 = os.path.join(out, "s1z", "s1z_%s.json" % tag)
s2p = os.path.join(out, "s2z", tag)


def run(cmd, outfile, mode="w"):
    with open(outfile, mode) as f:
        return subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT)


if what in ("first", "both"):
    if not os.path.exists(s1):
        rc = run([py, "stage1c.py", graph, prof[0], prof[1], prof[2], s1, "z=" + zs], os.path.join(out, "s1z", "s1z_%s.out" % tag))
        assert rc == 0, "stage 1 failed"
    nb = len(json.load(open(s1))["bases"])
    if nb and not os.path.exists(s2p + "_0of1.sum.json"):
        rc = run([py, "run_stage2.py", s1, "0", "1", "400000", s2p, "width=3"], os.path.join(out, "s2z", "run_%s.out" % tag))
        assert rc == 0, "stage 2 failed"
    if nb:
        run([py, "summary2.py", s1, s2p, "1"], os.path.join(out, "s2z", "summary_%s.out" % tag))
if what in ("second", "both"):
    vb = os.path.join(out, "vz", "vbz_%s" % tag)
    vf = os.path.join(out, "vz", "vfz_%s" % tag)
    if not os.path.exists(vb + "_0of1.json"):
        rc = run([py, "in_verify.py", "basesz", graph, prof[0], prof[1], prof[2], zs, vb + "_0of1.json"],
                 os.path.join(out, "vz", "vbz_%s.out" % tag))
        assert rc == 0, "second program, stage 1 failed"
    nb = len(json.load(open(s1))["bases"])
    args = [py, "in_verify.py", "mergez", s1, vb, "1"]
    if nb:
        if not os.path.exists(vf + "_0of1.json") or json.load(open(vf + "_0of1.json")).get("partial"):
            rc = run([py, "in_verify.py", "follow", s1, s2p, "0", "1", vf + "_0of1.json"], os.path.join(out, "vz", "vfz_%s.out" % tag))
            assert rc == 0, "second program, stage 2 failed"
        args.append(vf)
    run(args, os.path.join(out, "vz", "verify_%s.out" % tag))
print(tag, "done", what)
