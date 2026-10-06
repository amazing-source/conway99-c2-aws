# B0, profile (2,5,0): summary of the stage-C logs (b0_stageC_done_*.jsonl), one line per orbit representative of stage B.
import json, glob, collections
R = json.load(open("b0_stageB_reps.json"))
done = {}; dup = 0
for f in sorted(glob.glob("b0_stageC_done_*.jsonl")):
    for l in open(f):
        if l.strip():
            d = json.loads(l)
            if d["idx"] in done:
                dup += 1
                assert len(done[d["idx"]]["survivors"]) == len(d["survivors"])
            done[d["idx"]] = d
for i, d in done.items():
    assert d["tau"] == R[i]["tau"] and d["F"] == R[i]["F"]
tot = collections.Counter()
for d in done.values():
    for k, v in d["delta"].items():
        tot[k] += v
missing = [i for i in range(len(R)) if i not in done]
surv = [s for d in done.values() for s in d["survivors"]]
print(f"stage-B orbit representatives: {len(R)} (covering {sum(e['orbit'] for e in R)} triples); completed at stage C: {len(done)}; "
      f"not completed: {len(missing)}; logged twice: {dup}")
print("counters summed over the completed representatives:", dict(sorted(tot.items())))
print(f"stage-C survivors (47 vertices): {len(surv)} in {len(set((s['tau'], tuple(s['F'])) for s in surv))} pairs (tau, F), "
      f"matchings {sorted(set(s['tau'] for s in surv))}")
if missing:
    print("first missing:", missing[:20], "by matching:", sorted(collections.Counter(R[i]['tau'] for i in missing).items()))
json.dump({"survivors": surv, "missing": missing}, open("b0_stageC_survivors.json", "w"))
