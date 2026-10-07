# T20 round 3: totals of a stage-2 run split in parts.  Checks that the parts tile the list of bases of the
# stage-1 file (every index exactly once, in the right part), that no base timed out or raised an error, and that
# all parts used the same list (sha1).
# usage: python summary2.py <stage1.json> <prefix> <nparts>
import sys, json, hashlib, os
s1file, prefix, nparts = sys.argv[1], sys.argv[2], int(sys.argv[3])
s1 = json.load(open(s1file))
bases = s1["bases"]
sha = hashlib.sha1(json.dumps(bases, sort_keys=True).encode()).hexdigest()
n = len(bases)
recs = {}
bad = []
shas = set()
for part in range(nparts):
    fn = "%s_%dof%d.jsonl" % (prefix, part, nparts)
    if not os.path.exists(fn):
        bad.append("part %d: no file" % part)
        continue
    sm = "%s_%dof%d.sum.json" % (prefix, part, nparts)
    if os.path.exists(sm):
        shas.add(json.load(open(sm))["bases_sha1"])
    else:
        bad.append("part %d: not finished (no summary file)" % part)
    for line in open(fn):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("timeout") or r.get("error"):
            continue
        assert r["i"] % nparts == part
        recs[r["i"]] = r
missing = [i for i in range(n) if i not in recs]
L = max([len(r["visited"]) for r in recs.values()] + [1])


def tot(key):
    return [sum(r[key][l] for r in recs.values() if len(r[key]) > l) for l in range(L)]


def trim(v):
    while len(v) > 1 and v[-1] == 0:
        v = v[:-1]
    return v


st = {}
for r in recs.values():
    for k, v in r["stats"].items():
        st[k] = st.get(k, 0) + v
print("%s profile %s%s: stage-1 file %s, %d bases, sha1 %s" % (
    s1["graph"], tuple(s1["profile"]), (" z = %s" % (s1["ztype"],)) if s1.get("ztype") else "", s1file, n, sha))
print("   parts %d; sha1 recorded by the parts: %s; bases finished %d; missing %d; problems: %s" % (
    nparts, sorted(shas), len(recs), len(missing), bad if bad else "none"))
print("   COMPLETE (tiles the list, no time-out, no error, same list): %s" % (
    not missing and not bad and shas == {sha}))
print("   bases impossible by a cap: %d" % sum(1 for r in recs.values() if r.get("impossible")))
print("   nodes visited per level   :", trim(tot("visited")), " total", sum(tot("visited")))
print("   candidates (chosen unit)  :", trim(tot("cand")), " total", sum(tot("cand")))
print("     rejected by budgets     :", trim(tot("rej_b")))
print("     rejected by PSD (exact) :", trim(tot("rej_p")))
print("     kept                    :", trim(tot("kept")))
print("     of which dead by rank   :", trim(tot("rej_rank")))
print("   complete configurations: %d" % sum(r["complete"] for r in recs.values()))
print("   stats:", ", ".join("%s=%d" % (k, st[k]) for k in sorted(st)))
print("   cpu seconds: %.0f (mean %.3f per base, max %.1f)" % (
    sum(r["cpu"] for r in recs.values()), sum(r["cpu"] for r in recs.values()) / max(1, len(recs)),
    max([r["cpu"] for r in recs.values()] + [0])))
