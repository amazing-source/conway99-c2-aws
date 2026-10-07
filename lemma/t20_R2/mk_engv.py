s = open("eng.py").read()
i = s.index("def run(prob")
head = s[:i].replace("# T20 round 2: general orbit-by-orbit engine", "# T20 round 2 (verifier engine engv.py; tests of eng.py: full sigma-block eigen-decompositions, full budget recount; search order chosen WITHOUT any test on the current node)\n# T20 round 2: general orbit-by-orbit engine", 1)
open("engv.py", "w").write(head + open("engv_run.txt").read())
open("run_engv.py", "w").write('''# usage: python run_engv.py <case> <part> <nparts> <tlim> <split_depth> <tag> [first|mincand] [norank]
import sys
import engv, cases
case = sys.argv[1]
part, nparts, tlim, sd = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
tag = sys.argv[6]
order = "first" if "first" in sys.argv[7:] else "mincand"
if case.startswith("III"):
    prob = cases.CaseIII(case)
else:
    nm, ex = case.split(":")
    prob = cases.CaseIIa(nm, int(ex))
planf = None
for a in sys.argv[7:]:
    if a.startswith("plan="):
        planf = a[5:]
engv.run(prob, part, nparts, tlim, sd, tag, order=order, use_rank=("norank" not in sys.argv[7:]), plan_file=planf)
''')
print("ok")
