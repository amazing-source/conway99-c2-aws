# usage: python run_iian.py <list of W-set indices, comma separated, or a:b> <tlim per W-set> <tag> [certs=N]
# IIa.0 with N(p) in the base (X_0 not in the vertex set): eng5 on the W type sets of iia_w.json
import sys, json, time, os
import eng5, cases
a = sys.argv[1]
idx = list(range(int(a.split(":")[0]), int(a.split(":")[1]))) if ":" in a else [int(t) for t in a.split(",")]
tl, tag = float(sys.argv[2]), sys.argv[3]
certs = 0
for x in sys.argv[4:]:
    if x.startswith("certs="):
        certs = int(x[6:])
wsets = json.load(open("iia_w.json"))
os.makedirs("iian", exist_ok=True)
res = []
for wi in idx:
    prob = cases.CaseIIaN("IIa.0", [tuple(t) for t in wsets[wi]])
    t0 = time.process_time()
    out = eng5.run(prob, 0, 1, tl, 99, "iian/%s_w%d" % (tag, wi), save_certs=certs, plan=True)
    res.append({"wset": wi, "types": wsets[wi], "timeout": out["timeout"], "visited": out["visited"],
                "candidates": out["candidates"], "rejected_budget": out["rejected_budget"],
                "rejected_psd": out["rejected_psd"], "kept": out["kept"], "rejected_rank": out["rejected_rank"],
                "complete": len(out["survivors"]), "cpu_seconds": time.process_time() - t0, "stats": out["stats"]})
    json.dump(res, open("iian/%s_summary_%s.json" % (tag, a.replace(":", "-").replace(",", "_")), "w"))
    print("WSET %d: timeout %s cpu %.1f s visited %s kept %s complete %d" % (
        wi, out["timeout"], res[-1]["cpu_seconds"], out["visited"], out["kept"], len(out["survivors"])))
    sys.stdout.flush()
