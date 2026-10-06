import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_verify.py")
s = open(fn, encoding="utf-8").read()
old = ('        items = [e for e in items if e["tau"] in keep]\n'
       '        tagx = "_t" + os.environ["R3V_TAUS"].split(",")[0]\n')
assert s.count(old) == 1
s = s.replace(old, old +
              '    if os.environ.get("R3V_SKIP") or os.environ.get("R3V_TAKE"):\n'
              '        sk = int(os.environ.get("R3V_SKIP", "0")); tk = int(os.environ.get("R3V_TAKE", "1000000"))\n'
              '        items = items[sk:sk + tk]\n'
              '        tagx += f"_skip{sk}"\n')
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("verifier patched (skip/take), syntax ok")
