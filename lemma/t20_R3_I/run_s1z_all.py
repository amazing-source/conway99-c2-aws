# T20 round 3, case I, n_3 = 2: stage 1 for every graph, every type of z (ztypes.json: classes under Aut(B) x
# (z <-> sigma z)) and the given profiles, with a pool of worker processes.
# usage: python run_s1z_all.py <outdir> <nworkers> <profile> [<profile> ...] [graphs=I.0,I.5]     profile = 421 or 340
import sys, json, os, subprocess, time
outdir, nw = sys.argv[1], int(sys.argv[2])
profs = [a for a in sys.argv[3:] if a in ("421", "340")]
graphs = None
for a in sys.argv[3:]:
    if a.startswith("graphs="):
        graphs = a[7:].split(",")
os.makedirs(outdir, exist_ok=True)
zt = json.load(open("ztypes.json"))
jobs = []
for prof in profs:
    for g in sorted(zt):
        if graphs and g not in graphs:
            continue
        for k, r in enumerate(zt[g]):
            tag = "%s_%s_t%d" % (g.replace(".", ""), prof, k)
            zarg = "z=%s:%s" % (",".join(map(str, r["U"])), ",".join(map(str, r["V"])))
            jobs.append((tag, [sys.executable, "stage1c.py", g, prof[0], prof[1], prof[2],
                               os.path.join(outdir, "s1z_%s.json" % tag), zarg]))
running = []
t0 = time.time()
log = open(os.path.join(outdir, "run_s1z_all_%s.log" % "_".join(profs)), "a")
while jobs or running:
    while jobs and len(running) < nw:
        tag, cmd = jobs.pop(0)
        if os.path.exists(os.path.join(outdir, "s1z_%s.json" % tag)):
            continue
        f = open(os.path.join(outdir, "s1z_%s.out" % tag), "w")
        running.append((tag, subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT), f, time.time()))
    for it in list(running):
        if it[1].poll() is not None:
            it[2].close()
            log.write("%s exit %d  %.0f s  (at %.0f s)\n" % (it[0], it[1].returncode, time.time() - it[3], time.time() - t0))
            log.flush()
            running.remove(it)
    time.sleep(1)
log.write("ALL DONE %.0f s\n" % (time.time() - t0))
log.close()
