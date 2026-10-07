import cProfile, pstats, sys, time
import eng5, cases
prob = cases.CaseIII("III.0")
pr = cProfile.Profile(); pr.enable()
eng5.run(prob, -1, 100000000, 300, 2, 'prof5')
pr.disable()
p = pstats.Stats(pr); p.sort_stats("tottime").print_stats(12)
