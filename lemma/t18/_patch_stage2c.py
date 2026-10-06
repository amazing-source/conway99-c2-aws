import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_stage2.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep('                                TOT["Y_psd_reject"] += 1\n                                continue\n',
    '                                TOT["Y_psd_reject"] += 1\n'
    '                                if len(rejected) < 3:\n'
    '                                    rejected.append({"tau": list(tau), "F": list(Forb), "Az": Az, "H": list(h), "G": list(g)})\n'
    '                                continue\n')
rep("examples = []\n", "examples = []\nrejected = []\n")
rep('"per_tau": per_tau, "examples": examples},', '"per_tau": per_tau, "examples": examples, "rejected_examples": rejected},')
open(fn, "w", encoding="utf-8").write(s)
print("patched c")
