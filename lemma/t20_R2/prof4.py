import cProfile, pstats, sys
import eng4, cases
prob = cases.CaseIII("III.1")
cProfile.run("eng4.run(prob, 7, 3000, 60, 3, 'prof4')", "prof4.stats")
p = pstats.Stats("prof4.stats"); p.sort_stats("tottime").print_stats(14)
