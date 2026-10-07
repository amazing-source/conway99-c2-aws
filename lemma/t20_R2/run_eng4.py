# usage: python run_eng4.py <case> <part> <nparts> <tlim> <split_depth> <tag> [setwise] [certs=N] [width=W] [norank]
import sys
import eng4, cases
case = sys.argv[1]
part, nparts, tlim, sd = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
tag = sys.argv[6]
setwise = "setwise" in sys.argv[7:]
certs = 0
width = 0
for a in sys.argv[7:]:
    if a.startswith("certs="):
        certs = int(a[6:])
    if a.startswith("width="):
        width = int(a[6:])
if case.startswith("III"):
    prob = cases.CaseIII(case)
else:
    nm, ex = case.split(":")
    prob = cases.CaseIIa(nm, int(ex))
eng4.run(prob, part, nparts, tlim, sd, tag, setwise=setwise, save_certs=certs,
         use_rank=("norank" not in sys.argv[7:]), width=width, plan=('plan' in sys.argv[7:]))
