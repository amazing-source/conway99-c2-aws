# T20 round 3, case I, branch n_3 = 2: completeness check of the first program, recomputed from the files only.
# For each of the 50 cases (graph, type of z, profile): the stage-1 file is reloaded, the sha1 of its list of bases is
# recomputed; every stage-2 jsonl line is re-read: each base index exactly once, no time-out, no error; the sha1
# recorded by the part summary must be the recomputed one.  Totals per case, per graph and per profile.
# usage: python check_n3.py <stage-1 dir> <stage-2 dir> <out file>
import sys, json, os, glob, hashlib
d1, d2, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
zt = json.load(open("ztypes.json"))
lines = []


def say(s):
    print(s)
    lines.append(s)


allok = True
grand = {}
for prof in ("421", "340"):
    for g in sorted(zt):
        G = {"cases": 0, "nconf": 0, "orb": 0, "bases": 0, "nodes": 0, "complete": 0, "rank": 0, "timeouts": 0,
             "deepest": 0, "empty": 0, "cpu": 0.0, "levels": []}
        for k, r in enumerate(zt[g]):
            tag = "%s_%s_t%d" % (g.replace(".", ""), prof, k)
            s1 = json.load(open(os.path.join(d1, "s1z_%s.json" % tag)))
            assert tuple(s1["ztype"][0]) == tuple(r["U"]) and tuple(s1["ztype"][1]) == tuple(r["V"])
            assert s1["graph"] == g and "".join(map(str, s1["profile"])) == prof and s1["nparts"] == 1
            bases = s1["bases"]
            n = len(bases)
            sha = hashlib.sha1(json.dumps(bases, sort_keys=True).encode()).hexdigest()
            seen = {}
            bad = 0
            parts = sorted(glob.glob(os.path.join(d2, "%s_*of*.jsonl" % tag)))
            for fn in parts:
                for line in open(fn):
                    rr = json.loads(line)
                    if rr.get("timeout") or rr.get("error"):
                        bad += 1
                        continue
                    assert rr["i"] not in seen, "base twice"
                    seen[rr["i"]] = rr
            sums = [json.load(open(f)) for f in glob.glob(os.path.join(d2, "%s_*of*.sum.json" % tag))]
            ok = (n == 0 and not parts) or (sorted(seen) == list(range(n)) and bad == 0 and len(sums) == len(parts) == 1
                                            and all(sm["bases_sha1"] == sha and not sm["unfinished"] for sm in sums))
            L = max([len(rr["visited"]) for rr in seen.values()] + [1])
            vis = [sum(rr["visited"][l] for rr in seen.values() if len(rr["visited"]) > l) for l in range(L)]
            while len(vis) > 1 and vis[-1] == 0:
                vis.pop()
            comp = sum(rr["complete"] for rr in seen.values())
            rk = sum(sum(rr["rej_rank"]) for rr in seen.values())
            imp = sum(1 for rr in seen.values() if rr.get("impossible"))
            allok = allok and ok and comp == 0
            say("%-11s z = %s;%s  |G_z| %d  N-configurations %8d  classes %7d  bases kept %5d  sha1 %s  stage 2: %s  "
                "nodes %s  complete %d  rank %d  time-outs/errors %d  impossible by a cap %d  ->  %s" % (
                    tag, "".join(map(str, r["U"])), "".join(map(str, r["V"])), s1["group_order"], s1["nconfigs_labelled"],
                    s1["nconfig_orbits"], n, sha[:12], "no base" if n == 0 else "%d of %d" % (len(seen), n),
                    vis if n else [], comp, rk, bad, imp, "OK" if ok and comp == 0 else "NOT ESTABLISHED"))
            G["cases"] += 1; G["nconf"] += s1["nconfigs_labelled"]; G["orb"] += s1["nconfig_orbits"]; G["bases"] += n
            G["nodes"] += sum(vis) if n else 0; G["complete"] += comp; G["rank"] += rk; G["timeouts"] += bad
            G["deepest"] = max(G["deepest"], len(vis) - 1 if n else 0); G["empty"] += (n == 0)
            G["cpu"] += sum(rr["cpu"] for rr in seen.values())
            for l, v in enumerate(vis if n else []):
                while len(G["levels"]) <= l:
                    G["levels"].append(0)
                G["levels"][l] += v
        grand[(prof, g)] = G
say("")
say("profile graph  types  N-configurations   classes   bases kept  types with no base  stage-2 nodes  nodes per level              deepest  complete  rank  time-outs  cpu s")
for prof in ("421", "340"):
    T = None
    for g in sorted(zt):
        G = grand[(prof, g)]
        say("%-7s %-5s %5d  %15d  %8d  %10d  %18d  %13d  %-27s %7d  %8d  %4d  %9d  %5.0f" % (
            prof, g, G["cases"], G["nconf"], G["orb"], G["bases"], G["empty"], G["nodes"], G["levels"], G["deepest"],
            G["complete"], G["rank"], G["timeouts"], G["cpu"]))
        if T is None:
            T = {k: (list(v) if isinstance(v, list) else v) for k, v in G.items()}
        else:
            for k, v in G.items():
                if k == "deepest":
                    T[k] = max(T[k], v)
                elif k == "levels":
                    for l, x in enumerate(v):
                        while len(T[k]) <= l:
                            T[k].append(0)
                        T[k][l] += x
                else:
                    T[k] += v
    say("%-7s %-5s %5d  %15d  %8d  %10d  %18d  %13d  %-27s %7d  %8d  %4d  %9d  %5.0f" % (
        prof, "all", T["cases"], T["nconf"], T["orb"], T["bases"], T["empty"], T["nodes"], T["levels"], T["deepest"],
        T["complete"], T["rank"], T["timeouts"], T["cpu"]))
say("ALL 50 CASES COMPLETE (every base once, same list hash, no time-out, no error) AND EMPTY (0 complete): %s" % allok)
open(outfile, "w").write("\n".join(lines) + "\n")
