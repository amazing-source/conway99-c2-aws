# usage: python run_iiaw.py <first base> <last base (excl.)> <tlim per base> <tag>
# IIa.0 with N(p) and X_0 in the base: runs eng4 on the bases iia_bases.json[first:last]
import sys, json, time
import eng5 as eng4, cases
first, last, tl, tag = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
wsets = json.load(open("iia_w.json"))
bases = json.load(open("iia_bases.json"))
res = []
for bi in range(first, min(last, len(bases))):
    wi, alpha, beta, pat = bases[bi]
    prob = cases.CaseIIaW("IIa.0", [tuple(t) for t in wsets[wi]], tuple(alpha), tuple(beta), pat)
    t0 = time.time()
    out = eng4.run(prob, 0, 1, tl, 99, "%s_b%d" % (tag, bi))
    res.append({"base": bi, "timeout": out["timeout"], "visited": out["visited"], "kept": out["kept"],
                "complete": len(out["survivors"]), "seconds": time.time() - t0, "stats": out["stats"]})
    json.dump(res, open("%s_%d_%d.json" % (tag, first, last), "w"))
    sys.stdout.flush()
