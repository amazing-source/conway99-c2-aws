"""Read-only breakdown of the route-(C) queue per lattice (from the files exported out of branch `queue`)."""
import json, os, collections, time, sys
S = os.path.dirname(os.path.abspath(__file__))
order = [l.strip() for l in open(os.path.join(S, "order.txt")) if l.strip()]
ev = [json.loads(l) for l in open(os.path.join(S, "events.jsonl")) if l.strip()]
jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(S, "pkg", "jobs.json")))}
man = json.load(open(os.path.join(S, "pkg", "MANIFEST.json")))
print("package on master:", man.get("version"), "| jobs.json:", len(jobs), "jobs")

own, done, fails = {}, set(), collections.Counter()
tdone = {}
for e in ev:
    op, m = e.get("op"), e.get("m")
    for j in e.get("jobs", []):
        if op == "claim":
            own[j] = (m, e["t"])
        elif op == "done":
            done.add(j); tdone[j] = e["t"]; own.pop(j, None)
        elif op in ("release", "fail"):
            if j in own and own[j][0] == m:
                own.pop(j)
            if op == "fail":
                fails[j] += 1

print("events:", len(ev), "| first", time.strftime("%d/%m %H:%M", time.gmtime(ev[0]["t"])), "| last", time.strftime("%d/%m %H:%M UTC", time.gmtime(ev[-1]["t"])))
print("order.txt:", len(order), "keys (", len(set(order)), "distinct ) | done in order:", len(done & set(order)), "| done total:", len(done))
print("keys in order missing from v10 jobs.json:", sum(1 for j in order if j not in jobs))
print("failed keys:", {j: c for j, c in fails.items() if j not in done})

# per lattice / chunking
tab = collections.defaultdict(lambda: dict(keys=0, done=0, est_all=0.0, est_left=0.0, nojob=0))
for j in order:
    lid, k, n = j.split(":")
    t = tab[(lid, int(n))]
    t["keys"] += 1
    e = float(jobs[j].get("est_h") or 0) if j in jobs else None
    if e is None:
        t["nojob"] += 1
    else:
        t["est_all"] += e
    if j in done:
        t["done"] += 1
    elif e is not None:
        t["est_left"] += e

bylid = collections.defaultdict(list)
for (lid, n), t in tab.items():
    bylid[lid].append((n, t))
print("\n%-6s %-8s %6s %6s %6s %9s %9s  %s" % ("lid", "n", "keys", "done", "left", "est_h", "est_left", "note"))
tot_left = tot_keys_left = 0
for lid in sorted(bylid):
    for n, t in sorted(bylid[lid]):
        left = t["keys"] - t["done"]
        note = ("%d keys not in v10 jobs.json" % t["nojob"]) if t["nojob"] else ""
        if left or "-a" in sys.argv:
            print("%-6s %-8d %6d %6d %6d %9.1f %9.1f  %s" % (lid, n, t["keys"], t["done"], left, t["est_all"], t["est_left"], note))
        tot_left += t["est_left"]; tot_keys_left += left
print("\nTOTAL not done: %d keys, %.0f est-h (v10 jobs.json estimates)" % (tot_keys_left, tot_left))

# first 40 free keys in queue order (what a machine would claim first)
free = [j for j in order if j not in done]
print("\nhead of the free queue:", " ".join(free[:30]))
seq = []
for j in free:
    lid = j.split(":")[0]
    if not seq or seq[-1][0] != lid:
        seq.append([lid, 0])
    seq[-1][1] += 1
print("free queue as runs of lattices (first 60 runs):", " ".join("%s×%d" % (a, b) for a, b in seq[:60]))
