import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r4_verifyC2.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# R4V_FULL=1: in the exact-cover stage use the FULL test (both matrices) at every node instead of the sigma-odd test.
# (With the odd test alone some triples produce hundreds of complete configurations that only the final full test
#  rejects, and the search explodes; the answer is the same, only the pruning changes.)
rep("                    ST[\"nodes\"] += 1\n                    if fast_ok(A3, idx37 + list(range(37, 39 + 2 * c))):\n",
    "                    ST[\"nodes\"] += 1\n"
    "                    if (full_ok(A3, idx37 + list(range(37, 39 + 2 * c))) if FULL else fast_ok(A3, idx37 + list(range(37, 39 + 2 * c)))):\n")
rep("T0 = time.time()\n", "T0 = time.time()\nFULL = os.environ.get(\"R4V_FULL\") == \"1\"\n")
rep("    if skip:\n        tag += f\"_skip{skip}\"\n", "    if skip:\n        tag += f\"_skip{skip}\"\n    if FULL:\n        tag += \"_full\"\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r4_verifyC2 patched (R4V_FULL), syntax ok")
