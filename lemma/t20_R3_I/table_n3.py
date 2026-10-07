# T20 round 3, case I, n_3 = 2: table of the cases (graph, type of z, profile), from the stage-1 files s1z_*.json and,
# when present, the stage-2 parts (jsonl).  Everything is recomputed from the files.
# usage: python table_n3.py <stage-1 dir> <stage-2 dir or -> [<profile> ...]
import sys, json, os, glob, hashlib
d1, d2 = sys.argv[1], sys.argv[2]
profs = [a for a in sys.argv[3:] if a in ("421", "340")] or ["421", "340"]
zt = json.load(open("ztypes.json"))
for a in sys.argv[3:]:
    if a.startswith("graphs="):
        zt = {g: zt[g] for g in a[7:].split(",")}
tot = {}
print("case            z = U3 ; V3        |G_z| rect  N-config   orbits  with a choice  kept bases  beta    | stage 2: bases done, nodes per level, deepest, complete, rank, cpu s")
for prof in profs:
    T = {"nconf": 0, "orb": 0, "kept": 0, "nodes": 0, "complete": 0, "rank": 0, "cpu": 0.0, "done": 0, "cases": 0, "empty": 0, "missing": 0}
    for g in sorted(zt):
        for k, r in enumerate(zt[g]):
            tag = "%s_%s_t%d" % (g.replace(".", ""), prof, k)
            fn = os.path.join(d1, "s1z_%s.json" % tag)
            zs = "%s;%s" % ("".join(map(str, r["U"])), "".join(map(str, r["V"])))
            if not os.path.exists(fn):
                print("%-15s %-18s  stage 1 NOT FINISHED" % (tag, zs))
                T["missing"] += 1
                continue
            s1 = json.load(open(fn))
            assert tuple(s1["ztype"][0]) == tuple(r["U"]) and tuple(s1["ztype"][1]) == tuple(r["V"])
            n = len(s1["bases"])
            T["cases"] += 1; T["nconf"] += s1["nconfigs_labelled"]; T["orb"] += s1["nconfig_orbits"]; T["kept"] += n
            T["empty"] += (n == 0)
            line = "%-15s %-18s %4d %4d %9d %8d %9s %10d  %-7s |" % (
                tag, zs, s1["group_order"], s1["rects"], s1["nconfigs_labelled"], s1["nconfig_orbits"],
                s1.get("n35_with_choice", "-"), n, ",".join("%s:%d" % (kk[4:], v) for kk, v in sorted(s1.get("kept_by_beta", {}).items())) or "-")
            if d2 != "-":
                seen = {}
                bad = 0
                for f2 in glob.glob(os.path.join(d2, "%s_*of*.jsonl" % tag)):
                    for l in open(f2):
                        rr = json.loads(l)
                        if rr.get("timeout") or rr.get("error"):
                            bad += 1
                            continue
                        seen[rr["i"]] = rr
                if n == 0:
                    line += " no base: nothing to enumerate"
                elif not seen and not bad:
                    line += " stage 2 not run"
                else:
                    L = max([len(rr["visited"]) for rr in seen.values()] + [1])
                    vis = [sum(rr["visited"][l] for rr in seen.values() if len(rr["visited"]) > l) for l in range(L)]
                    while len(vis) > 1 and vis[-1] == 0:
                        vis.pop()
                    comp = sum(rr["complete"] for rr in seen.values())
                    rk = sum(sum(rr["rej_rank"]) for rr in seen.values())
                    cpu = sum(rr["cpu"] for rr in seen.values())
                    ok = sorted(seen) == list(range(n)) and not bad
                    line += " %d of %d%s, %s, deepest %d, complete %d, rank %d, cpu %.1f" % (
                        len(seen), n, "" if ok else " (INCOMPLETE, time-out/error %d)" % bad, vis, len(vis) - 1, comp, rk, cpu)
                    T["nodes"] += sum(vis); T["complete"] += comp; T["rank"] += rk; T["cpu"] += cpu; T["done"] += len(seen)
            print(line)
    print("profile %s TOTAL: cases %d (stage 1 missing %d), N-configurations %d, orbits %d, bases kept %d (cases with no base: %d); "
          "stage 2: bases done %d, nodes %d, complete %d, rank %d, cpu %.0f s" % (
              prof, T["cases"], T["missing"], T["nconf"], T["orb"], T["kept"], T["empty"], T["done"], T["nodes"], T["complete"], T["rank"], T["cpu"]))
