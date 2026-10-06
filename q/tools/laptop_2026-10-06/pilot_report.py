"""Read-only report on one machine of the route-(C) queue: what it claimed, what it finished, how long each job took, and the
verdicts in its result files. Usage: python pilot_report.py <repo> <machine name, e.g. q-i-008a374f92faec021>"""
import sys, json, subprocess, collections, time, io, zipfile
REPO, M = sys.argv[1], sys.argv[2]


def git(*a, binary=False):
    r = subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=not binary)
    return r.stdout


git("fetch", "-q", "--prune", "origin", "+refs/heads/queue:refs/remotes/origin/queue", "+refs/heads/run/q-*:refs/remotes/origin/run/q-*")
ev = [json.loads(l) for l in git("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
now = time.time()
st = dict(l.split("=", 1) for l in git("show", "origin/run/%s:status.txt" % M).splitlines() if "=" in l)
if st:
    print("status: %s %s | pkg %s | up %.2f h | running %s | done %s | failed %s | mode %s | last report %.1f min ago | %s" % (
        st.get("STATE"), st.get("AZ"), st.get("PKG"), float(st.get("UPTIME_H") or 0), st.get("RUNNING"), st.get("DONE"), st.get("FAILED"),
        st.get("MODE"), (now - float(st.get("NOW") or now)) / 60, st.get("REASON") or st.get("LAST_ERR") or ""))
else:
    print("no status branch yet for", M)

claim, rows = {}, []
for e in ev:
    if e.get("m") != M:
        continue
    for j in e.get("jobs", []):
        if e["op"] == "claim":
            claim[j] = e["t"]
        elif j in claim:
            rows.append((j, e["op"], (e["t"] - claim.pop(j)) / 60.0))
running = sorted(claim.items(), key=lambda kv: kv[1])

# result files of the machine: verdict counts and wall time per job
res = {}
data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", "origin/run/%s" % M, "results"], capture_output=True).stdout
if data:
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in z.namelist():
        if not n.endswith(".jsonl"):
            continue
        last = None; inc = 0
        for l in z.read(n).decode(errors="replace").splitlines():
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if "verdicts" in d:
                last = d
        if last:
            ch = last.get("chunk") or [None, None]
            lid = last.get("id")
            v = last["verdicts"]; inc = sum(c for k, c in v.items() if "INCOMPLETE" in k)
            res[n.split("/")[-1]] = (last.get("wall_secs"), last.get("n_pairs"), inc, v)

per = collections.defaultdict(list)
for j, op, mins in rows:
    per[j.split(":")[0]].append((j, op, mins))
print("\nfinished or released jobs: %d   (still running: %d)" % (len(rows), len(running)))
print("%-4s %5s %5s %9s %9s %9s  %s" % ("lid", "done", "cut", "med_min", "max_min", "sum_h", "jobs (minutes)"))
for lid in sorted(per):
    d = sorted(x[2] for x in per[lid] if x[1] == "done"); c = [x for x in per[lid] if x[1] != "done"]
    detail = " ".join("%s=%.0f%s" % (x[0].split(":")[1], x[2], "" if x[1] == "done" else "[" + x[1] + "]") for x in sorted(per[lid], key=lambda x: -x[2])[:12])
    print("%-4s %5d %5d %9.1f %9.1f %9.2f  %s" % (lid, len(d), len(c), d[len(d) // 2] if d else float("nan"), d[-1] if d else float("nan"), sum(d) / 60, detail))
if running:
    print("\nstill running (minutes so far):", " ".join("%s=%.0f" % (j, (now - t) / 60) for j, t in running))
if res:
    tot = collections.Counter(); inc = 0
    for f, (w, n, i, v) in res.items():
        inc += i
        for k, c in v.items():
            tot[k] += c
    print("\nresult files: %d | INCOMPLETE pairs: %d" % (len(res), inc))
    for k, c in tot.most_common():
        print("   %8d  %s" % (c, k))
    slow = sorted(((w or 0, f) for f, (w, n, i, v) in res.items()), reverse=True)[:8]
    print("slowest result files (wall s):", " ".join("%s=%.0f" % (f.replace(".jsonl", ""), w) for w, f in slow))
