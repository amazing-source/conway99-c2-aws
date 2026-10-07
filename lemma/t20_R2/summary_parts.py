# usage: python summary_parts.py <tag> <nparts>      totals of a run split in parts (eng3 / eng4 / eng5 json files)
import json, sys
tag, n = sys.argv[1], int(sys.argv[2])
parts = []
for i in range(n):
    try:
        parts.append(json.load(open("%s_%dof%d.json" % (tag, i, n))))
    except FileNotFoundError:
        print("part %d of %d: NOT FINISHED (no result file)" % (i, n))
if len(parts) < n:
    print("RUN INCOMPLETE: %d of %d parts finished" % (len(parts), n))
    sys.exit(0)
ok = all(not p["timeout"] for p in parts)
print(tag, "engine", parts[0]["engine"], "| parts:", n, "| time-out in some part:", not ok)
print("   tasks at depth %d: %s (must be equal in all parts); done: %d" % (
    parts[0]["split_depth"], sorted(set(p["tasks_total"] for p in parts)), sum(p["tasks_done"] for p in parts)))
if "task_list_sha1" in parts[0]:
    print("   sha1 of the ordered task list, per part:", sorted(set(p["task_list_sha1"] for p in parts)))
sd = parts[0]["split_depth"]
L = len(parts[0]["visited"])
for key in ("visited", "candidates", "rejected_budget", "rejected_psd", "kept", "rejected_rank"):
    out = []
    for lev in range(L):
        vals = [p[key][lev] for p in parts]
        common = (lev <= sd) if key != "kept" else (lev < sd)
        if common:
            assert len(set(vals)) == 1, (key, lev, vals)
            out.append(vals[0])
        else:
            out.append(sum(vals))
    print("   %-16s %s   total %d" % (key, out, sum(out)))
print("   complete configurations:", sum(len(p["survivors"]) for p in parts))
st = {}
for p in parts:
    for k, v in p["stats"].items():
        st[k] = st.get(k, 0) + v
print("   stats summed over the parts:", st)
print("   seconds per part:", [round(p["seconds"]) for p in parts])
