# T20 round 3, case I, branch n_3 = 2: agreement of the second program (in_verify.py) with the first, per case,
# recomputed from the files: the stage-1 file and the stage-2 jsonl of the first program, the "basesz" and "follow"
# outputs of the second program.  (The node-by-node equality of the kept counts is asserted inside "follow"; here the
# totals are compared and the classes of bases are recomputed from the keys.)
# usage: python check_n3_verify.py <stage-1 dir> <stage-2 dir> <second program dir> <out file>
import sys, json, os, glob
d1, d2, dv, outfile = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
zt = json.load(open("ztypes.json"))
lines = []


def say(s):
    print(s)
    lines.append(s)


allok = True
T = {"cases": 0, "agree": 0, "bases": 0, "classes": 0, "followed": 0, "nodes": 0, "certs": 0, "elim": 0, "complete": 0,
     "att": 0, "att_psd": 0, "missing": 0}
say("case         z            bases(1st)  classes 1st/2nd  stage 1  | bases followed  nodes 1st/2nd  kept 1st/2nd  complete  stage 2 | certificates (integer vector / exact elimination)")
for prof in ("421", "340"):
    for g in sorted(zt):
        for k, r in enumerate(zt[g]):
            tag = "%s_%s_t%d" % (g.replace(".", ""), prof, k)
            zs = "%s;%s" % ("".join(map(str, r["U"])), "".join(map(str, r["V"])))
            T["cases"] += 1
            vb = os.path.join(dv, "vbz_%s_0of1.json" % tag)
            vo = os.path.join(dv, "verify_%s.out" % tag)
            if not (os.path.exists(vb) and os.path.exists(vo)):
                say("%-12s %-12s second program NOT FINISHED" % (tag, zs))
                T["missing"] += 1
                allok = False
                continue
            s1 = json.load(open(os.path.join(d1, "s1z_%s.json" % tag)))
            b = json.load(open(vb))
            txt = open(vo).read()
            n = len(s1["bases"])
            mine = set(kk for kk, v in b["keys"])
            ok1 = "STAGE 1 AGREES: True" in txt
            m1 = [l for l in txt.split("\n") if "kept bases as classes" in l][0]
            c2 = int(m1.split("this program ")[1].split(",")[0]); c1 = int(m1.split("first program ")[1].split(" ")[0])
            assert c2 == len(mine)
            nodes1 = kept1 = 0
            for fn in glob.glob(os.path.join(d2, "%s_*of*.jsonl" % tag)):
                for line in open(fn):
                    rr = json.loads(line)
                    nodes1 += sum(rr["visited"]); kept1 += sum(rr["kept"])
            if n:
                vf = os.path.join(dv, "vfz_%s_0of1.json" % tag)
                f = json.load(open(vf)) if os.path.exists(vf) else {"partial": True}
                if f.get("partial"):
                    say("%-12s %-12s second program, stage 2 NOT FINISHED" % (tag, zs))
                    T["missing"] += 1
                    allok = False
                    continue
                tt = f["totals"]
                ok2 = (f["bases_followed"] == n and tt["nodes"] == nodes1 and tt["kept"] == kept1 and tt["complete"] == 0
                       and tt.get("rank_nodes", 0) == 0 and "STAGE 2 AGREES AT EVERY NODE, 0 complete, all bases: True" in txt)
                c = f["certificates"]
                s2txt = "%6d  %7d/%-7d %6d/%-6d %3d      %s" % (f["bases_followed"], nodes1, tt["nodes"], kept1, tt["kept"],
                                                              tt["complete"], "agrees" if ok2 else "DISAGREES")
                T["followed"] += f["bases_followed"]; T["nodes"] += tt["nodes"]; T["complete"] += tt["complete"]
                T["certs"] += c["integer_vector"]; T["elim"] += c["exact_elimination"]
            else:
                ok2 = True
                c = b["certificates"]
                s2txt = "     -  no base: nothing to traverse            agrees"
            cb = b["certificates"]
            T["att"] += b["counts"]["attach"]; T["att_psd"] += b["counts"]["att_psd"]
            T["bases"] += n; T["classes"] += c2
            T["agree"] += (ok1 and ok2)
            allok = allok and ok1 and ok2
            say("%-12s %-12s %8d   %7d/%-7d  %s | %s | stage 1: %d / %d%s" % (
                tag, zs, n, c1, c2, "agrees   " if ok1 else "DISAGREES", s2txt, cb["integer_vector"], cb["exact_elimination"],
                ("; stage 2: %d / %d" % (c["integer_vector"], c["exact_elimination"])) if n else ""))
say("TOTAL: cases %d, agreeing on both stages %d, not finished %d; bases of the first program %d = %d classes; bases "
    "re-traversed %d, nodes %d, complete %d; attachments tested by the second program %d (rejected by PSD %d); "
    "stage-2 certificates: integer vector %d, exact elimination %d" % (
        T["cases"], T["agree"], T["missing"], T["bases"], T["classes"], T["followed"], T["nodes"], T["complete"],
        T["att"], T["att_psd"], T["certs"], T["elim"]))
say("ALL 50 CASES: SAME CLASSES OF BASES, SAME KEPT COUNT AT EVERY NODE, 0 COMPLETE: %s" % allok)
open(outfile, "w").write("\n".join(lines) + "\n")
