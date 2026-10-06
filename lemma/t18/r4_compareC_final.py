# Round 4.  Stage C of B1, profile (2,5,0): what the SECOND implementations have covered, and whether they agree with
# the enumerator r3_p250.py.  Second implementations (all independent of r3_p250.py):
#   v0 = r3_verify.py C250   (dual order, full tests)            files r3v_C250_1_0of1_t813*.json
#   v2 = r4_verifyC2.py      (pair order, sigma-odd tests + full test at the end)   files r4v_C2_1_*.json
# (r4_verifyC.py, a dual-order variant with sigma-odd tests, was run once: file r4v_C_1_0of1_t813.json.)
# Supersedes r4_compareC.py.  No import from the enumerators.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
items = []
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3v_B250_1_") and fn.endswith(".json"):
        items += json.load(open(os.path.join(HERE, fn)))["H"]
items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
key = lambda e: (e["tau"], tuple(e["F"]), tuple(e["H"]))
t813 = [e for e in items if e["tau"] in (813, 975)]
skey = lambda e: (e["tau"], tuple(e["F"]), tuple(e["H"]), tuple(sorted(tuple(x) for x in e["types"])))
cover = {}          # triple -> set of implementations that completed it
surv = {"v0": {}, "v1": {}, "v2": {}}


def add(impl, proc, survivors, fn):
    for e in proc:
        cover.setdefault(key(e), set()).add(impl)
    for e in survivors:
        surv[impl][skey(e)] = surv[impl].get(skey(e), 0) + 1
    print(f"   {impl}  {fn}: {len(proc)} triples completed, {len(survivors)} survivors reported")


for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3v_C250_1_0of1_t813") and fn.endswith(".json"):
        d = json.load(open(os.path.join(HERE, fn)))
        sk = int(fn.split("_skip")[1].split(".")[0]) if "_skip" in fn else 0
        add("v0", t813[sk: sk + d["stats"]["H_mine"]], d["survivors"], fn)
    if fn == "r4v_C_1_0of1_t813.json":
        d = json.load(open(os.path.join(HERE, fn)))
        add("v1", t813[: d["completed"]], d["survivors"], fn)
    if fn.startswith("r4v_C2_1_") and fn.endswith(".json") and "first34" not in fn:
        d = json.load(open(os.path.join(HERE, fn)))
        its = t813 if "_t813" in fn else items
        if d.get("idx_list"):
            proc = [its[q] for q in d["idx_list"]][: d["completed"]]
        else:
            mine = [e for n, e in enumerate(its) if n % d["nparts"] == d["part"]]
            proc = mine[d["skip"]: d["skip"] + d["completed"]]
        add("v2", proc, d["survivors"], fn)
M18 = (1 << 18) - 1
esurv = {}
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3_p250_1_") and fn.endswith("_BC.json"):
        for e in json.load(open(os.path.join(HERE, fn))).get("survivors", []):
            H = tuple((e["rows"][19 + k] >> 19) & M18 for k in range(18))
            esurv[(e["tau"], tuple(sorted(e["F"])), H, tuple(sorted(tuple(x) for x in e["types"])))] = 1
any2 = set(cover)
print(f"triples of B1 (stage B): {len(items)};  of matchings #813 and #975: {len(t813)}")
print(f"triples completed by at least one second implementation: {len(any2)}; "
      f"of #813 / #975: {sum(1 for e in t813 if key(e) in any2)} of {len(t813)}; "
      f"elsewhere: {sum(1 for k in any2 if k[0] not in (813, 975))}")
print(f"   by v0: {sum(1 for v in cover.values() if 'v0' in v)}, by v1: {sum(1 for v in cover.values() if 'v1' in v)}, "
      f"by v2: {sum(1 for v in cover.values() if 'v2' in v)}")
print("enumerator survivors (complete list):")
for k in sorted(esurv):
    who = sorted(impl for impl in surv if k in surv[impl])
    cov = sorted(cover.get(k[:3], []))
    print(f"    matching {k[0]}, F {list(k[1])}: triple completed by {cov if cov else 'no second implementation'}; "
          f"found as survivor by {who if who else 'none'}")
extra = set()
for impl in surv:
    extra |= set(surv[impl]) - set(esurv)
print(f"survivors reported by a second implementation that the enumerator does not have: {len(extra)}")
miss = [(k, impl) for k in esurv for impl in cover.get(k[:3], []) if k not in surv[impl]]
print(f"enumerator survivors lying in a triple completed by an implementation that did not report them: {len(miss)}")
left = [n for n, e in enumerate(t813) if key(e) not in any2]
print(f"triples of #813 / #975 not completed by any second implementation: {len(left)}; indices {left}")
json.dump({"left_t813": left}, open(os.path.join(HERE, "r4_left_t813.json"), "w"))
