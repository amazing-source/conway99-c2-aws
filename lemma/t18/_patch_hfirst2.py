import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_hfirst.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep('       "survivors": 0, "tau_with_survivor": 0, "psd_calls": 0, "exact_calls": 0}\n',
    '       "survivors": 0, "tau_with_survivor": 0, "psd_calls": 0, "exact_calls": 0,\n'
    '       "rej_budget": 0, "rej_certificate": 0, "rej_exact_elimination_only": 0}\n')
rep("            if c > 2 or (c > 1 and (ru >> L[b]) & 1):\n                return False\n",
    "            if c > 2 or (c > 1 and (ru >> L[b]) & 1):\n                TOT[\"rej_budget\"] += 1\n                return False\n")
rep("        if w < -1e-7 and neg_certificate(Mx.tolist()) is not None:\n            return False\n"
    "        TOT[\"exact_calls\"] += 1\n        if not psd_exact(Mx.tolist())[0]:\n            return False\n",
    "        if w < -1e-7 and neg_certificate(Mx.tolist()) is not None:\n            TOT[\"rej_certificate\"] += 1\n            return False\n"
    "        TOT[\"exact_calls\"] += 1\n        if not psd_exact(Mx.tolist())[0]:\n            TOT[\"rej_exact_elimination_only\"] += 1\n            return False\n")
open(fn, "w", encoding="utf-8").write(s)
print("patched hfirst2")
