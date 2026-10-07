import cProfile, pstats, sys
import eng4, cases
prob = cases.CaseIII("III.0")
cProfile.run("eng4.run(prob, 0, 1, 150, 99, 'prof4b')", "prof4b.stats")
p = pstats.Stats("prof4b.stats"); p.sort_stats("tottime").print_stats(16)
