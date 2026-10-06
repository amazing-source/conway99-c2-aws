import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_hfirst.py")
s = open(fn, encoding="utf-8-sig").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


# A rejection needs an exact proof; an acceptance does not (over-acceptance only weakens the filter).
# So the costly exact elimination is used only when the float eigenvalue is clearly negative and no integer
# certificate was found by rounding.
rep("        if w > 1e-7:\n            continue\n        if w < -1e-7 and neg_certificate(Mx.tolist()) is not None:\n",
    "        if w > -1e-7:\n            continue\n        if neg_certificate(Mx.tolist()) is not None:\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
print("patched hfirst3")
