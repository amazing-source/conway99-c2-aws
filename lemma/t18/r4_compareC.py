# Round 4.  Stage C of B1, profile (2,5,0): comparison of the enumerator (r3_p250.py) with the independent second
# implementation r4_verifyC2.py, on exactly the triples (tau, F, H) that the latter completed.
# No import from the enumerators.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
items = []
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3v_B250_1_") and fn.endswith(".json"):
        items += json.load(open(os.path.join(HERE, fn)))["H"]
items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
key = lambda e: (e["tau"], tuple(e["F"]), tuple(e["H"]))
processed = set(); vsurv = set(); nfiles = 0; stats = {}
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r4v_C2_1_") and fn.endswith(".json"):
        d = json.load(open(os.path.join(HERE, fn)))
        its = items
        if "_t813" in fn:
            its = [e for e in items if e["tau"] in (813, 975)]
        mine = [e for n, e in enumerate(its) if n % d["nparts"] == d["part"]]
        assert len(mine) == d["in_part"], fn
        proc = mine[d["skip"]: d["skip"] + d["completed"]]
        processed.update(key(e) for e in proc)
        for e in d["survivors"]:
            vsurv.add((e["tau"], tuple(e["F"]), tuple(e["H"]), tuple(e["rows"])))
        nfiles += 1
        for k, v in d["stats"].items():
            stats[k] = stats.get(k, 0) + v
        print(f"   {fn}: completed {d['completed']} triples (skip {d['skip']}), timed_out {d['timed_out']}, survivors {len(d['survivors'])}")
M18 = (1 << 18) - 1
esurv = set()
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3_p250_1_") and fn.endswith("_BC.json"):
        d = json.load(open(os.path.join(HERE, fn)))
        for e in d.get("survivors", []):
            H = tuple((e["rows"][19 + k] >> 19) & M18 for k in range(18))
            esurv.add((e["tau"], tuple(sorted(e["F"])), H, tuple(e["rows"])))
print(f"second implementation: {nfiles} files, {len(processed)} distinct triples completed out of {len(items)}; "
      f"matchings touched: {len(set(k[0] for k in processed))}")
t813 = [key(e) for e in items if e["tau"] in (813, 975)]
print(f"triples of matchings #813 and #975 completed: {sum(1 for k in t813 if k in processed)} of {len(t813)}")
e_in = set(x for x in esurv if x[:3] in processed)
print(f"enumerator survivors (all 4977 triples): {len(esurv)}; of which in the triples completed by the second implementation: {len(e_in)}")
print(f"second implementation survivors: {len(vsurv)}; identical 47-vertex graphs (same rows): {vsurv == e_in}; "
      f"only second implementation: {len(vsurv - e_in)}; only enumerator: {len(e_in - vsurv)}")
for x in sorted(vsurv):
    print("    survivor of the second implementation: matching", x[0], "F", list(x[1]))
print("summed counters of the second implementation:", stats)
