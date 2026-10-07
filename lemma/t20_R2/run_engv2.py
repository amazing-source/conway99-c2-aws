# usage: python run_engv.py <case> <part> <nparts> <tlim> <split_depth> <tag> [first|mincand] [norank]
import sys
import engv2 as engv, cases
case = sys.argv[1]
part, nparts, tlim, sd = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
tag = sys.argv[6]
order = "first" if "first" in sys.argv[7:] else "mincand"
setw = "setwise" in sys.argv[7:]
if case.startswith("III"):
    prob = cases.CaseIII(case)
else:
    nm, ex = case.split(":")
    prob = cases.CaseIIa(nm, int(ex))
planf = None
for a in sys.argv[7:]:
    if a.startswith("plan="):
        planf = a[5:]
engv.run(prob, part, nparts, tlim, sd, tag, order=order, use_rank=("norank" not in sys.argv[7:]), plan_file=planf, setwise=setw)
