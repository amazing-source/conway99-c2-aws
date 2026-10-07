# usage: python run_eng.py <case> <part> <nparts> <tlim> <split_depth> <tag> [setwise]
#   case: III.0, III.1, IIa.0:0, IIa.0:1, IIa.0:2
import sys
import eng, cases
case = sys.argv[1]
part, nparts, tlim, sd = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
tag = sys.argv[6]
setwise = len(sys.argv) > 7 and sys.argv[7] == "setwise"
if case.startswith("III"):
    prob = cases.CaseIII(case)
else:
    nm, ex = case.split(":")
    prob = cases.CaseIIa(nm, int(ex))
eng.run(prob, part, nparts, tlim, sd, tag, setwise=setwise)
