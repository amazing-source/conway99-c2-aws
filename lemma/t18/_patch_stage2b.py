import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_stage2.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep("import json, os, sys, itertools, time\n",
    "import json, os, sys, itertools, time\nimport numpy as np\nfrom enum_S import neg_certificate\n")
rep('TOT = {"tau": 0, "tau_done": 0, "F": 0, "F_ok_Np": 0, "C": 0, "H": 0, "G": 0, "Y_tables": 0, "tau_with_table": 0}\n',
    'TOT = {"tau": 0, "tau_done": 0, "F": 0, "F_ok_Np": 0, "C": 0, "H": 0, "G": 0, "Y_tables": 0, "tau_with_table": 0,\n'
    '       "Y_psd_reject": 0, "Y_tables_psd": 0, "tau_with_psd_table": 0}\n'
    'PSD_HIT = [False]\n\n\n'
    'def psd_ok_rows(rows):\n'
    '    """exact PSD test of 9(3I-A)+J and 11(4I+A)-2J on the determined graph (integer certificate for a rejection)"""\n'
    '    n = len(rows)\n'
    '    A = np.array([[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)], dtype=np.int64)\n'
    '    for Mx in (27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2):\n'
    '        if np.linalg.eigvalsh(Mx.astype(float))[0] < -1e-7 and neg_certificate(Mx.tolist()) is not None:\n'
    '            return False\n'
    '    return True\n')
rep('                            TOT["Y_tables"] += 1\n                            found_any = True\n',
    '                            TOT["Y_tables"] += 1\n                            found_any = True\n'
    '                            if psd_ok_rows(rows):\n'
    '                                TOT["Y_tables_psd"] += 1\n'
    '                                PSD_HIT[0] = True\n'
    '                            else:\n'
    '                                TOT["Y_psd_reject"] += 1\n'
    '                                continue\n')
rep("    before = dict(TOT)\n    fa = process(tau)\n", "    before = dict(TOT)\n    PSD_HIT[0] = False\n    fa = process(tau)\n")
rep('    if fa:\n        TOT["tau_with_table"] += 1\n',
    '    if fa:\n        TOT["tau_with_table"] += 1\n    if PSD_HIT[0]:\n        TOT["tau_with_psd_table"] += 1\n')
rep('    per_tau.append({k: TOT[k] - before[k] for k in ("F", "F_ok_Np", "C", "H", "G", "Y_tables")})\n',
    '    per_tau.append({k: TOT[k] - before[k] for k in ("F", "F_ok_Np", "C", "H", "G", "Y_tables", "Y_tables_psd")})\n')
open(fn, "w", encoding="utf-8").write(s)
print("patched b")
