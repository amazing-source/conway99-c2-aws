"""Measured run time of the fine (v9) jobs, per lattice, from queue events: duration = done.t - last claim.t by the same machine.
Read-only. Gives real/estimate ratios and a projection of the work left (v9 engine; v10 never ran on AWS)."""
import json, os, collections, statistics as st
S = os.path.dirname(os.path.abspath(__file__))
order = [l.strip() for l in open(os.path.join(S, "order.txt")) if l.strip()]
ev = [json.loads(l) for l in open(os.path.join(S, "events.jsonl")) if l.strip()]
jobs = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(S, "pkg", "jobs.json")))}
oset = set(order)
claim, dur, done, lost = {}, {}, set(), collections.defaultdict(float)
last_t = collections.defaultdict(float)
for e in ev:
    m, op, t = e.get("m"), e.get("op"), e["t"]
    last_t[m] = max(last_t[m], t)
    for j in e.get("jobs", []):
        if op == "claim":
            claim[(j, m)] = t
        elif op == "done":
            done.add(j)
            if (j, m) in claim:
                dur[j] = (t - claim.pop((j, m)), m)
        elif op in ("release", "fail"):
            if (j, m) in claim:
                lost[j.split(":")[0]] += (t - claim.pop((j, m))) / 3600
# claims never closed (machine died silently): count until the machine's last event
for (j, m), t in claim.items():
    if j not in done:
        lost[j.split(":")[0]] += max(0, last_t[m] - t) / 3600

per = collections.defaultdict(list)
for j, (d, m) in dur.items():
    if j in oset and j in jobs:
        per[j.split(":")[0]].append((d / 3600, float(jobs[j]["est_h"] or 0), j, m))

left = collections.defaultdict(lambda: [0, 0.0])
for j in order:
    if j not in done:
        left[j.split(":")[0]][0] += 1; left[j.split(":")[0]][1] += float(jobs[j]["est_h"] or 0)

print("%-5s %5s %8s %8s %7s %7s %7s | %6s %8s %10s %9s" % ("lid", "n_ok", "real_h", "est_h", "ratio", "med_h", "max_h", "left", "est_left", "proj_real", "lost_h"))
tot = 0.0; tot_nolattice = 0.0
for lid in sorted(left):
    xs = per.get(lid, [])
    real = sum(x[0] for x in xs); est = sum(x[1] for x in xs)
    ratio = real / est if est else float("nan")
    nl, el = left[lid]
    proj = el * ratio if xs and est else float("nan")
    # alternative projection: mean real hours per done job x jobs left (robust when est is tiny)
    proj2 = (real / len(xs)) * nl if xs else float("nan")
    print("%-5s %5d %8.1f %8.1f %7.2f %7.2f %7.2f | %6d %8.1f %10.0f %9.1f   (mean-per-job proj %.0f)" % (
        lid, len(xs), real, est, ratio, st.median([x[0] for x in xs]) if xs else float("nan"), max([x[0] for x in xs]) if xs else float("nan"),
        nl, el, proj, lost.get(lid, 0.0), proj2))
    if proj == proj:
        tot += proj
print("\nprojected real job-hours left (est_left x measured ratio, v9 engine, small sample): %.0f" % tot)
print("job-hours lost to interruptions / stops on the open lattices (fine jobs only): %.0f" % sum(lost[l] for l in left))
print("\nlongest finished fine jobs:")
allx = sorted((x for xs in per.values() for x in xs), reverse=True)[:15]
for h, e, j, m in allx:
    print("  %-16s %6.2f h  (est %.2f)  %s" % (j, h, e, m))
