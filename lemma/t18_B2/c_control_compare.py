# t18_B2 / c_control_compare.py -- positive control of c_mine.py: on the two B1 matchings that carry the four known
# stage-C survivors (#813, #975), c_mine.py must return exactly the survivors of r3_p250.py (same 47-vertex graphs).
# usage: python c_control_compare.py <c_mine json> <r3_p250 json files with survivors ...>
import json, sys
mine = json.load(open(sys.argv[1]))
assert not mine["timed_out"]
A = set(tuple(e["rows"][:47]) for e in mine["survivors"])
B = set()
for fn in sys.argv[2:]:
    for e in json.load(open(fn))["survivors"]:
        B.add(tuple(e["rows"][:47]))
print(f"c_mine: {len(A)} survivors on {mine['totals']['triples_done']} triples; r3_p250: {len(B)} distinct survivors; "
      f"identical 47-vertex graphs: {A == B}; only c_mine {len(A - B)}, only r3_p250 {len(B - A)}")
for e in mine["survivors"]:
    print("   matching #%d, F = %s, types %s" % (e["tau"], e["F"], e["types"]))
