import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_stage2.py")
s = open(fn, encoding="utf-8-sig").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


# explicit list of matchings (indices in the survivor-filtered list of representatives): env R2_IDX = "3,17,..."
rep("my = [r for q, r in enumerate(reps) if q % nparts == part]\n",
    "my = [r for q, r in enumerate(reps) if q % nparts == part]\n"
    "TAG = ''\n"
    "if os.environ.get('R2_IDX'):\n"
    "    my = [reps[int(i)] for i in os.environ['R2_IDX'].split(',')]\n"
    "    TAG = '_idx' + os.environ['R2_IDX'].split(',')[0]\n")
rep("{'_surv' if SURV is not None else ''}.json", "{'_surv' if SURV is not None else ''}{TAG}.json")
rep('    per_tau.append({k: TOT[k] - before[k] for k in ("F", "F_ok_Np", "C", "H", "G", "Y_tables", "Y_tables_psd")})\n',
    '    per_tau.append({k: TOT[k] - before[k] for k in ("F", "F_ok_Np", "C", "H", "G", "Y_tables", "Y_tables_psd")})\n'
    '    per_tau[-1]["rep_index"] = reps.index(tau)\n'
    '    per_tau[-1]["seconds"] = round(time.time() - t0, 1)\n')
open(fn, "w", encoding="utf-8", newline="\n").write(s)
import ast
ast.parse(s)
print("patched e, syntax ok")
