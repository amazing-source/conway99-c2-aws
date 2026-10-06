# Round 4: split the triples of #813 / #975 not yet completed by a second implementation into lists for r4_verifyC2.py;
# the triple of the enumerator's fourth survivor (matching #975, F = [3,6]) is put first.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ngroups = int(sys.argv[1])
items = []
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3v_B250_1_") and fn.endswith(".json"):
        items += json.load(open(os.path.join(HERE, fn)))["H"]
items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))
t813 = [e for e in items if e["tau"] in (813, 975)]
left = json.load(open(os.path.join(HERE, "r4_left_t813.json")))["left_t813"]
M18 = (1 << 18) - 1
target = None
for fn in sorted(os.listdir(HERE)):
    if fn.startswith("r3_p250_1_") and fn.endswith("_BC.json"):
        for e in json.load(open(os.path.join(HERE, fn))).get("survivors", []):
            if e["tau"] == 975 and sorted(e["F"]) == [3, 6]:
                H = [(e["rows"][19 + k] >> 19) & M18 for k in range(18)]
                for n, it in enumerate(t813):
                    if it["tau"] == 975 and it["F"] == [3, 6] and it["H"] == H:
                        target = n
print("index of the triple of the 4th survivor:", target, " still to do:", target in left)
if target in left:
    left = [target] + [x for x in left if x != target]
for g in range(ngroups):
    open(os.path.join(HERE, f"r4_left_g{g}.txt"), "w").write(",".join(map(str, left[g::ngroups])))
    print(f"group {g}: {left[g::ngroups]}")
