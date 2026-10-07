import cProfile, pstats, sys
import eng2, cases
prob = cases.CaseIII("III.0")
cProfile.run("eng2.run(prob, 0, 400, 40, 2, 'prof')", "prof.stats")
p = pstats.Stats("prof.stats"); p.sort_stats("cumulative").print_stats(22)
