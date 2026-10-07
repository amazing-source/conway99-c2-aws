# T20 round 3: independent re-check, on the laptop, of the outputs of a cloud run (branch lemma-run/<job>-<instance>).
# For every case folder <graph>_<profile>/ found in the extracted branch:
#   - the stage-1 file is reloaded and the sha1 of its list of bases recomputed;
#   - every jsonl part is re-read: each base index must appear exactly once, in the right part, without time-out or
#     error; the number of complete configurations and the node counts are recomputed from the lines;
#   - the sha1 recorded by every part (its .sum.json) must be the recomputed one.
# usage: python check_cloud.py <extracted folder> <out file>
import sys, os, json, hashlib, glob

root, outfile = sys.argv[1], sys.argv[2]
lines = []


def say(s):
    print(s)
    lines.append(s)


allok = True
for d in sorted(glob.glob(os.path.join(root, "I*_*"))):
    tag = os.path.basename(d)
    s1file = os.path.join(d, "s1_%s.json" % tag)
    if not os.path.exists(s1file):
        say("%s: NO STAGE-1 FILE (case not finished or file over the push limit)" % tag)
        allok = False
        continue
    s1 = json.load(open(s1file))
    bases = s1["bases"]
    sha = hashlib.sha1(json.dumps(bases, sort_keys=True).encode()).hexdigest()
    n = len(bases)
    sums = sorted(glob.glob(os.path.join(d, "parts", "s2_*of*.sum.json")))
    parts = sorted(glob.glob(os.path.join(d, "parts", "s2_*of*.jsonl")))
    nparts = int(parts[0].rsplit("of", 1)[1].split(".")[0]) if parts else 0
    seen = {}
    bad = []
    L = 0
    for fn in parts:
        part = int(os.path.basename(fn).split("_")[1].split("of")[0])
        for line in open(fn):
            r = json.loads(line)
            if r.get("timeout") or r.get("error"):
                bad.append((r["i"], "timeout" if r.get("timeout") else "error"))
                continue
            if r["i"] % nparts != part:
                bad.append((r["i"], "wrong part"))
            if r["i"] in seen:
                bad.append((r["i"], "twice"))
            seen[r["i"]] = r
            L = max(L, len(r["visited"]))
    missing = [i for i in range(n) if i not in seen]
    shas = set(json.load(open(f))["bases_sha1"] for f in sums)
    vis = [sum(r["visited"][l] for r in seen.values() if len(r["visited"]) > l) for l in range(L)]
    kept = [sum(r["kept"][l] for r in seen.values() if len(r["kept"]) > l) for l in range(L)]
    while len(vis) > 1 and vis[-1] == 0:
        vis.pop()
    comp = sum(r["complete"] for r in seen.values())
    rank = sum(sum(r["rej_rank"]) for r in seen.values())
    ok = (not missing and not bad and len(parts) == nparts and len(sums) == nparts and shas == {sha} and comp == 0)
    allok = allok and ok
    say("%s  %s profile %s: |G| %d, N-configurations %d, orbits %d, bases %d (sha1 %s)" % (
        tag, s1["graph"], tuple(s1["profile"]), s1["group_order"], s1["nconfigs_labelled"], s1["nconfig_orbits"], n, sha))
    say("     parts %d of %d present, summaries %d; bases finished %d, missing %d, time-out / error / misplaced %d; "
        "sha1 of the parts equal to the recomputed one: %s" % (len(parts), nparts, len(sums), len(seen), len(missing),
                                                              len(bad), shas == {sha}))
    say("     nodes per level %s, total %d; rejected by the rank bound %d; complete configurations %d; cpu %.0f s"
        "   ->  %s" % (vis, sum(vis), rank, comp, sum(r["cpu"] for r in seen.values()),
                       "EXCLUDED (first program)" if ok else "NOT ESTABLISHED"))
say("ALL CASES FOUND ARE COMPLETE AND EMPTY: %s" % allok)
open(outfile, "w").write("\n".join(lines) + "\n")
