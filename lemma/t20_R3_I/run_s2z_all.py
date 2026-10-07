# T20 round 3, case I, n_3 = 2: stage 2 (run_stage2.py, one part) for every stage-1 file s1z_*_<profile>_t*.json of
# a folder that has at least one base and no finished stage-2 summary yet.  Sequential (the cases are small).
# usage: python run_s2z_all.py <stage-1 dir> <stage-2 dir> <time limit per base, s> <profile> [<profile> ...]
import sys, json, os, glob, subprocess, time
d1, d2, tl = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(d2, exist_ok=True)
for prof in sys.argv[4:]:
    for fn in sorted(glob.glob(os.path.join(d1, "s1z_*_%s_t*.json" % prof))):
        tag = os.path.basename(fn)[4:-5]
        if os.path.exists(os.path.join(d2, "%s_0of1.sum.json" % tag)):
            continue
        if not json.load(open(fn))["bases"]:
            continue
        t0 = time.time()
        with open(os.path.join(d2, "run_%s.out" % tag), "w") as f:
            rc = subprocess.call([sys.executable, "run_stage2.py", fn, "0", "1", tl, os.path.join(d2, tag), "width=3"],
                                 stdout=f, stderr=subprocess.STDOUT)
        print("%s: exit %d, %.1f s" % (tag, rc, time.time() - t0))
        sys.stdout.flush()
