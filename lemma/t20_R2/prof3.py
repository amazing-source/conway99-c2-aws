import cProfile, pstats, sys
import eng3, cases
prob = cases.CaseIII("III.0")
cProfile.run("eng3.run(prob, 0, 1, 60, 99, 'prof')", "prof.stats")
p = pstats.Stats("prof.stats"); p.sort_stats("tottime").print_stats(18)
