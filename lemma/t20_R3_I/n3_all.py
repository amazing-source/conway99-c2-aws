# T20 round 3, case I, branch n_3 = 2: all cases (6 graphs, 25 types of z, the given profiles) with a pool of worker
# processes, one case per process (n3_case.py), the largest first.  Then, with "first": table_n3.py -> <out>/table_n3.out.
# usage: python n3_all.py <out dir> <nworkers> first|second|both <profile> [<profile> ...] [graphs=I.0,...]   profile = 421 or 340
import sys, json, os, subprocess, time
out, nw, what = sys.argv[1], int(sys.argv[2]), sys.argv[3]
profs = [a for a in sys.argv[4:] if a in ("421", "340")]
os.makedirs(out, exist_ok=True)
zt = json.load(open("ztypes.json"))
for a in sys.argv[4:]:
    if a.startswith("graphs="):                    # test option: only these graphs, e.g. graphs=I.0,I.5
        zt = {g: zt[g] for g in a[7:].split(",")}
jobs = []
for prof in profs:
    for g in sorted(zt):
        for k in range(len(zt[g])):
            jobs.append("%s_%s_t%d" % (g.replace(".", ""), prof, k))
# largest first: profile (3,4,0) before (4,2,1), I.1 before the others
jobs.sort(key=lambda t: (0 if "_340_" in t else 1, 0 if t.startswith("I1") else 1, t))
running = []
t0 = time.time()
log = open(os.path.join(out, "n3_all_%s.log" % what), "a")
failed = 0
while jobs or running:
    while jobs and len(running) < nw:
        tag = jobs.pop(0)
        f = open(os.path.join(out, "case_%s_%s.out" % (tag, what)), "w")
        running.append((tag, subprocess.Popen([sys.executable, "n3_case.py", out, tag, what], stdout=f, stderr=subprocess.STDOUT), f, time.time()))
    for it in list(running):
        if it[1].poll() is not None:
            it[2].close()
            failed += (it[1].returncode != 0)
            log.write("%s exit %d  %.0f s  (at %.0f s)\n" % (it[0], it[1].returncode, time.time() - it[3], time.time() - t0))
            log.flush()
            running.remove(it)
    time.sleep(0.5)
log.write("ALL DONE %.0f s, failed %d\n" % (time.time() - t0, failed))
log.close()
if what in ("first", "both"):
    with open(os.path.join(out, "table_n3.out"), "w") as f:
        subprocess.call([sys.executable, "table_n3.py", os.path.join(out, "s1z"), os.path.join(out, "s2z")] + profs, stdout=f, stderr=subprocess.STDOUT)
if what in ("second", "both"):
    lines = []
    for prof in profs:
        for g in sorted(zt):
            for k in range(len(zt[g])):
                tag = "%s_%s_t%d" % (g.replace(".", ""), prof, k)
                fn = os.path.join(out, "vz", "verify_%s.out" % tag)
                txt = open(fn).read() if os.path.exists(fn) else "MISSING\n"
                ok1 = "STAGE 1 AGREES: True" in txt
                ok2 = ("STAGE 2 AGREES AT EVERY NODE, 0 complete, all bases: True" in txt) or ("first program 0 (from 0 bases)" in txt)
                lines.append("%-15s second program: stage 1 agrees %s; stage 2 agrees at every node and 0 complete (or no base) %s" % (tag, ok1, ok2))
    lines.append("ALL AGREE: %s" % all(("agrees True" in l) and l.endswith("True") for l in lines))
    open(os.path.join(out, "verify_all.out"), "w").write("\n".join(lines) + "\n")
print("done; failed cases:", failed)
