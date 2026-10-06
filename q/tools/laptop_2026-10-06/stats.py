"""durations of the jobs finished since T0 and ages of the jobs still running, per lattice (read-only)"""
import sys, json, subprocess, collections, time
REPO, T0 = sys.argv[1], float(sys.argv[2])
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
g("fetch", "-q", "origin", "+refs/heads/queue:refs/remotes/origin/queue")
ev = [json.loads(l) for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
now = time.time(); claim = {}; dur = collections.defaultdict(list); cut = collections.Counter()
for e in ev:
    if e["t"] < T0: continue
    for j in e.get("jobs", []):
        k = (j, e["m"])
        if e["op"] == "claim": claim[k] = e["t"]
        elif k in claim:
            d = (e["t"] - claim.pop(k)) / 60
            if e["op"] == "done": dur[j.split(":")[0]].append(d)
            else: cut[j.split(":")[0]] += 1
age = collections.defaultdict(list)
for (j, m), t in claim.items(): age[j.split(":")[0]].append((now - t) / 60)
q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))]
print("%-4s | %5s %7s %7s %7s %8s | %5s %7s %7s" % ("lid", "done", "med", "p90", "max", "sum_h", "run", "med_age", "max_age"))
for lid in sorted(set(dur) | set(age)):
    d, a = dur[lid], age[lid]
    print("%-4s | %5d %6.1fm %6.1fm %6.1fm %7.1fh | %5d %6.1fm %6.1fm%s" % (lid, len(d), q(d, .5) if d else 0, q(d, .9) if d else 0, max(d) if d else 0, sum(d) / 60,
          len(a), q(a, .5) if a else 0, max(a) if a else 0, ("  (%d cut)" % cut[lid]) if cut[lid] else ""))
