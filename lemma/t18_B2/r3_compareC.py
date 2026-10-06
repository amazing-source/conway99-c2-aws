# Round 3.  Comparison of the stage-C survivors of the enumerator (r3_p250.py) and of the dual-order verifier
# (r3_verify.py C250, restricted to matchings #813 and #975, stopped by its time limit).
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
v = json.load(open(os.path.join(HERE, "r3v_C250_1_0of1_t813.json")))
print("verifier C250 (dual order):", v["stats"], "timed_out", v["timed_out"])
vs = {}
for e in v["survivors"]:
    key = (e["tau"], tuple(e["F"]), tuple(e["H"]), tuple(sorted(tuple(x) for x in e["types"])))
    vs[key] = vs.get(key, 0) + 1
es = {}
M18 = (1 << 18) - 1
for fn in os.listdir(HERE):
    if fn.startswith("r3_p250_1_") and fn.endswith("_BC.json"):
        for e in json.load(open(os.path.join(HERE, fn)))["survivors"]:
            H = tuple((e["rows"][19 + k] >> 19) & M18 for k in range(18))
            key = (e["tau"], tuple(sorted(e["F"])), H, tuple(sorted(tuple(x) for x in e["types"])))
            es[key] = es.get(key, 0) + 1
print("enumerator survivors (tau, F, types): multiplicity")
for k, c in sorted(es.items()):
    print("   ", k[0], list(k[1]), [list(x) for x in k[3]], ":", c, "  found by the verifier:", vs.get(k, 0))
extra = [k for k in vs if k not in es]
print("survivors of the verifier that the enumerator does not have:", len(extra))
for k in extra:
    print("   ", k[0], list(k[1]), [list(x) for x in k[3]], ":", vs[k])
# which H items did the verifier process before its time limit ?  (items are sorted by (tau, F, H); it processed the first H_mine)
items = []
for q in range(3):
    items += [e for e in json.load(open(os.path.join(HERE, f"r3v_B250_1_{q}of3.json")))["H"] if e["tau"] in (813, 975)]
items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
n = v["stats"]["H_mine"]
proc = items[:n]
print(f"verifier processed {n} of {len(items)} triples: matchings {sorted(set(e['tau'] for e in proc))}, "
      f"last processed (tau, F) = {(proc[-1]['tau'], proc[-1]['F'])}")
pk = set((e["tau"], tuple(e["F"]), tuple(e["H"])) for e in proc[:-1])
print("enumerator survivors lying in the triples fully processed by the verifier:",
      sum(c for k, c in es.items() if (k[0], k[1], k[2]) in pk))
