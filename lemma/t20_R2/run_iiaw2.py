# usage: python run_iiaw2.py <list of base indices, comma separated> <tlim per base> <tag>
import sys, json, time, os
import eng5, cases
idx = [int(t) for t in sys.argv[1].split(",")]
tl, tag = float(sys.argv[2]), sys.argv[3]
wsets = json.load(open("iia_w.json")); bases = json.load(open("iia_bases.json"))
os.makedirs("iiaw", exist_ok=True)
res = []
for bi in idx:
    wi, alpha, beta, pat = bases[bi]
    prob = cases.CaseIIaW("IIa.0", [tuple(t) for t in wsets[wi]], tuple(alpha), tuple(beta), pat)
    t0 = time.process_time()
    out = eng5.run(prob, 0, 1, tl, 99, "iiaw/%s_b%d" % (tag, bi))
    res.append({"base": bi, "timeout": out["timeout"], "visited": out["visited"], "kept": out["kept"],
                "complete": len(out["survivors"]), "cpu_seconds": time.process_time() - t0})
    json.dump(res, open("iiaw/%s_summary.json" % tag, "w"))
    print("BASE %d: timeout %s cpu %.1f s visited %s complete %d" % (bi, out["timeout"], res[-1]["cpu_seconds"], out["visited"], len(out["survivors"])))
    sys.stdout.flush()
