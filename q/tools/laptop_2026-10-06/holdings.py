"""What each live machine holds (running + backlog), with the Golay full searches it holds. python holdings.py <repo>"""
import sys, json, subprocess, collections, time
REPO = sys.argv[1]
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
g("fetch", "-q", "origin", "+refs/heads/run/q-*:refs/remotes/origin/run/q-*", "+refs/heads/queue:refs/remotes/origin/queue")
ev = [json.loads(l) for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
own = {}; done = set(); tcl = {}
for e in ev:
    for j in e.get("jobs", []):
        if e["op"] == "claim": own[j] = e["m"]; tcl[j] = e["t"]
        elif e["op"] == "done": own.pop(j, None); done.add(j)
        elif own.get(j) == e["m"]: own.pop(j, None)
order = g("show", "origin/queue:order.txt").split()
st = {}
for r in g("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*").split():
    s_ = dict(l.split("=", 1) for l in g("show", r + ":status.txt").splitlines() if "=" in l); st[s_.get("NAME")] = s_
now = time.time(); live = {n for n, s_ in st.items() if s_.get("STATE") == "EN_COURS" and now - float(s_.get("NOW") or 0) < 1800}
w = {}
import os
for lid in ("002", "001"):
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "golay_heavy_%s.txt" % lid)):
        k, full, dfr = l.split(); w[k] = int(full)
per = collections.defaultdict(collections.Counter); heavy = collections.Counter(); hrun = collections.Counter()
for j, m in own.items():
    if m in live:
        per[m][j.split(":")[0]] += 1; heavy[m] += w.get(j, 0)
        if j in st[m].get("RUNNING_JOBS", "").split(): hrun[m] += w.get(j, 0)
for m in sorted(live, key=lambda m: -sum(per[m].values())):
    rj = st[m].get("RUNNING_JOBS", "").split(); old = max([now - tcl.get(j, now) for j in rj] or [0])
    print("%s %-11s holds %3d (running %2s, oldest claim %4.0f min): %s | Golay full searches: held %d, of which running %d" % (m[-6:], st[m].get("ITYPE"), sum(per[m].values()), st[m].get("RUNNING"), old / 60, dict(per[m]), heavy[m], hrun[m]))
free = [j for j in order if j not in done and own.get(j) not in live]
print("not done: %d | free: %d %s" % (sum(1 for j in order if j not in done), len(free), dict(collections.Counter(j.split(":")[0] for j in free))))
