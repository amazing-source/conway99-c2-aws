# t18_B0_VERIFC / b1_survivors_compare.py -- BOOKKEEPING ONLY: the survivors of the full B1 run of c_mine.py (all parts in
# <run dir>) against (a) the survivors stored by the enumerator r3_p250.py in ALL the r3_p250_1_*_BC.json files of <dir>,
# (b) the survivors of the control run (c_mine.py on matchings #813, #975 only).  Compared objects: the 47 adjacency rows.
# usage: python b1_survivors_compare.py <run dir> <dir with r3_p250_1_*_BC.json> <control c_mine json>
import json, os, sys, re
rd, D, ctrl = sys.argv[1], sys.argv[2], sys.argv[3]
A = {}
for fn in sorted(os.listdir(rd)):
    if re.match(r"^c_mine_1_\d+of\d+\.json$", fn):
        d = json.load(open(os.path.join(rd, fn)))
        assert not d["timed_out"]
        for e in d["survivors"]:
            A[tuple(e["rows"][:47])] = (e["tau"], tuple(e["F"]), fn)
B = {}
nf = 0
for fn in sorted(os.listdir(D)):
    if fn.startswith("r3_p250_1_") and fn.endswith("_BC.json"):
        nf += 1
        for e in json.load(open(os.path.join(D, fn)))["survivors"]:
            B[tuple(e["rows"][:47])] = (e["tau"], tuple(e["F"]), fn)
C = set(tuple(e["rows"][:47]) for e in json.load(open(ctrl))["survivors"])
print(f"full B1 run of c_mine.py: {len(A)} distinct survivors; enumerator r3_p250.py ({nf} BC files read): {len(B)} distinct survivors; "
      f"control run: {len(C)}")
print(f"identical 47-vertex graphs, full run vs enumerator: {set(A) == set(B)}; only c_mine {len(set(A) - set(B))}, only enumerator {len(set(B) - set(A))}")
print(f"identical 47-vertex graphs, full run vs control run: {set(A) == C}")
for r, v in sorted(A.items(), key=lambda kv: kv[1]):
    print(f"   matching #{v[0]}, F = {list(v[1])}: found in {v[2]}; enumerator file: {B[r][2] if r in B else '-'}")
