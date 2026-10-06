# B0, profile (2,5,0): summary of the X_0-first logs (b0_x0_done_*.jsonl) and comparison with the stage-C logs.
import json, glob, collections
R = json.load(open("b0_stageB_reps.json"))
x0 = {}
for f in sorted(glob.glob("b0_x0_done_*.jsonl")):
    for l in open(f):
        if l.strip():
            d = json.loads(l); x0[d["idx"]] = d
c = {}
for f in sorted(glob.glob("b0_stageC_done_*.jsonl")):
    for l in open(f):
        if l.strip():
            d = json.loads(l); c[d["idx"]] = d
tot = collections.Counter()
for d in x0.values():
    for k, v in d["stats"].items():
        if k != "t":
            tot[k] += v
alive = sorted(i for i, d in x0.items() if d["alive"])
print(f"X_0-first route: {len(x0)} of {len(R)} orbit representatives processed; killed without W (no table on 45 vertices): "
      f"{len(x0) - len(alive)}; with at least one table left: {len(alive)}")
print("   counters:", dict(sorted(tot.items())))
for i in alive:
    d = x0[i]
    print(f"   alive idx {i}: matching #{d['tau']}, F = {d['F']}, t = {d['stats']['t']}, tables left {len(d['alive'])}; "
          f"stage C on this triple: {'completed, ' + str(len(c[i]['survivors'])) + ' survivors' if i in c else 'not completed'}")
both = [i for i in x0 if i in c]
print(f"   representatives processed by both routes: {len(both)}; killed by both: {sum(1 for i in both if not x0[i]['alive'] and not c[i]['survivors'])}; "
      f"killed by stage C only: {sum(1 for i in both if x0[i]['alive'] and not c[i]['survivors'])}; "
      f"killed by X_0-first only: {sum(1 for i in both if not x0[i]['alive'] and c[i]['survivors'])}; by neither: {sum(1 for i in both if x0[i]['alive'] and c[i]['survivors'])}")
