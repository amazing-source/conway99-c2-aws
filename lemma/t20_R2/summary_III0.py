# totals of the III.0 runs (eng3 and eng4): levels 0..3 are common to the three parts, levels >= 4 are summed
import json
for tag in ("e3_III0", "e4_III0"):
    parts = [json.load(open("%s_%dof3.json" % (tag, i))) for i in range(3)]
    assert all(not p["timeout"] for p in parts)
    assert all(p["tasks_total"] == parts[0]["tasks_total"] for p in parts)
    assert sum(p["tasks_done"] for p in parts) == parts[0]["tasks_total"]
    sd = parts[0]["split_depth"]
    def tot(key):
        out = []
        for lev in range(13):
            vals = [p[key][lev] for p in parts]
            if lev <= sd and key in ("visited", "candidates", "rejected_budget", "rejected_psd"):
                assert vals[0] == vals[1] == vals[2], (key, lev, vals)
                out.append(vals[0])
            elif lev < sd and key == "kept":
                assert vals[0] == vals[1] == vals[2]
                out.append(vals[0])
            else:
                out.append(sum(vals))
        return out
    print(tag, "(engine %s): tasks at depth %d: %d, all done, no time-out; complete configurations: %d" % (
        parts[0]["engine"], sd, parts[0]["tasks_total"], sum(len(p["survivors"]) for p in parts)))
    for key in ("visited", "candidates", "rejected_budget", "rejected_psd", "kept", "rejected_rank"):
        t = tot(key)
        print("   %-16s %s   total %d" % (key, t, sum(t)))
    print("   look-ahead candidates (float selection only):", sum(p["lookahead_candidates"] for p in parts))
    st = {}
    for p in parts:
        for k, v in p["stats"].items():
            st[k] = st.get(k, 0) + v
    print("   stats summed over the three parts (the cached single / pair tests are repeated in each part):", st)
    print("   seconds per part:", [round(p["seconds"]) for p in parts])
