# t18_B2 / b2_stats.py -- descriptive statistics of the stage-B triples (tau, F, H) of B2, profile (2,5,0), and totals of the runs.
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
tot = collections.Counter(); trip = []
for fn in ("r3_p250_2_0of2_BC.json", "r3_p250_2_1of2_BC.json"):
    d = json.load(open(os.path.join(HERE, fn)))
    assert not d["timed_out"] and d["stages"] == "BC"
    tot.update(d["totals"]); trip += d["H_stageB"]
    assert d["survivors"] == []
print("enumerator r3_p250.py, B2, both parts, summed totals:")
for k, v in tot.items():
    print(f"   {k}: {v}")
reps = json.load(open(os.path.join(HERE, "r2_tau_2.json")))["reps"]
print("stage-B triples:", len(trip), " distinct (tau,F):", len(set((e["tau"], tuple(e["F"])) for e in trip)),
      " distinct tau:", len(set(e["tau"] for e in trip)))
dt = collections.Counter(); dmax = collections.Counter(); dfl = collections.Counter(); ok3 = 0
for e in trip:
    tau = reps[e["tau"]]
    degs = [bin(h).count("1") for h in e["H"]]
    mem = [k for o in e["F"] for k in (o, tau[o])]
    dt[sum(degs) // 2] += 1; dmax[max(degs)] += 1; dfl[sum(degs[k] - 1 for k in mem)] += 1
    ok3 += max(degs) <= 3
print("t = e(X_2):", sorted(dt.items()))
print("max a_2 on X_2:", sorted(dmax.items()), " triples with a_2 <= 3 on X_2 (bound of N3_REPORT.md):", ok3)
print("sum over A_p of (a_2 - 1):", sorted(dfl.items()))
print("matchings carrying triples:", sorted(collections.Counter(e["tau"] for e in trip).items()))
