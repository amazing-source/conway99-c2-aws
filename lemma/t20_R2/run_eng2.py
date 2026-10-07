# usage: python run_eng2.py <case> <part> <nparts> <tlim> <split_depth> <tag> [setwise] [certs=N]
import sys
import eng2, cases
case = sys.argv[1]
part, nparts, tlim, sd = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
tag = sys.argv[6]
setwise = "setwise" in sys.argv[7:]
certs = 0
for a in sys.argv[7:]:
    if a.startswith("certs="):
        certs = int(a[6:])
if case.startswith("III"):
    prob = cases.CaseIII(case)
else:
    nm, ex = case.split(":")
    prob = cases.CaseIIa(nm, int(ex))
eng2.run(prob, part, nparts, tlim, sd, tag, setwise=setwise, save_certs=certs)
