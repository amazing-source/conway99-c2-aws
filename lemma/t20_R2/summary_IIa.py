# totals of the IIa.0 runs with N(p) in the base (eng5), over the 87 type sets of N(p)
import json, glob
res = []
for fn in ("iian/all_summary_0-44.json", "iian/all_summary_44-87.json"):
    res += json.load(open(fn))
assert sorted(r["wset"] for r in res) == list(range(87))
assert all(not r["timeout"] for r in res), "time-out"
keys = ("visited", "candidates", "rejected_budget", "rejected_psd", "kept", "rejected_rank")
tot = {k: [sum(r[k][lev] for r in res) for lev in range(11)] for k in keys}
print("IIa.0, base S u N[p]: %d type sets of N(p), no time-out, complete configurations: %d" % (len(res), sum(r["complete"] for r in res)))
for k in keys:
    print("   %-16s %s   total %d" % (k, tot[k], sum(tot[k])))
st = {}
for r in res:
    for k, v in r["stats"].items():
        st[k] = st.get(k, 0) + v
print("   stats:", st)
print("   deepest level with a visited node:", max(lev for lev in range(11) if tot["visited"][lev]))
print("   nodes per type set: min %d, max %d;  cpu seconds total %.0f" % (
    min(sum(r["visited"]) for r in res), max(sum(r["visited"]) for r in res), sum(r["cpu_seconds"] for r in res)))
print("   type sets dead at the root (no candidate kept for the first unit):", sum(1 for r in res if r["kept"][0] == 0))
