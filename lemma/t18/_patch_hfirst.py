import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_hfirst.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep("pc = lambda x: bin(x).count(\"1\")\nt0 = time.time()\n",
    "pc = lambda x: bin(x).count(\"1\")\nt0 = time.time()\n"
    "# cross-check mode: R2_NOPSD=1 switches the PSD test off (budgets only); output goes to a separate file\n"
    "NOPSD = os.environ.get(\"R2_NOPSD\") == \"1\"\n")
rep("    n = len(L)\n    A = np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)\n",
    "    if NOPSD:\n        return True\n"
    "    n = len(L)\n    A = np.array([[(rows[u] >> v) & 1 for v in L] for u in L], dtype=np.int64)\n")
rep('f"r2_hfirst_{si}_{part}of{nparts}.json"', 'f"r2_hfirst_{si}_{part}of{nparts}{\'_nopsd\' if NOPSD else \'\'}.json"')
open(fn, "w", encoding="utf-8").write(s)

fn2 = os.path.join(here, "r2_hfirst_check.py")
s2 = open(fn2, encoding="utf-8").read()
assert s2.count("import r2_hfirst_nopsd\n") == 1
s2 = s2.replace("import r2_hfirst_nopsd\n",
                "print('(1) is run separately:  R2_NOPSD=1 python r2_hfirst.py 1 0 200 120  -> r2_hfirst_1_0of200_nopsd.json')\n")
open(fn2, "w", encoding="utf-8").write(s2)
print("patched hfirst")
