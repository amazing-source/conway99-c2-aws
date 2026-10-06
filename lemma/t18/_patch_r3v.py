import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_verify.py")
s = open(fn, encoding="utf-8").read()
old = '    items.sort(key=lambda e: (e["tau"], e["F"], e["H"]))\n'
assert s.count(old) == 1
s = s.replace(old, old +
              '    tagx = ""\n'
              '    if os.environ.get("R3V_TAUS"):\n'
              '        keep = set(int(x) for x in os.environ["R3V_TAUS"].split(","))\n'
              '        items = [e for e in items if e["tau"] in keep]\n'
              '        tagx = "_t" + os.environ["R3V_TAUS"].split(",")[0]\n')
old2 = 'f"r3v_C250_{s}_{part}of{nparts}.json"'
assert s.count(old2) == 1
s = s.replace(old2, 'f"r3v_C250_{s}_{part}of{nparts}{tagx}.json"')
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
left = __import__("json").load(open(os.path.join(here, "r3_coverage_B1.json")))["not_done"]
open(os.path.join(here, "r3_left_g0.txt"), "w").write(",".join(map(str, left[0::2])))
open(os.path.join(here, "r3_left_g1.txt"), "w").write(",".join(map(str, left[1::2])))
print("verifier patched, syntax ok; left", len(left), "groups", len(left[0::2]), len(left[1::2]), "first", left[0], left[1])
