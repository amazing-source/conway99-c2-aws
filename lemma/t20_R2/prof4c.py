import cProfile, pstats, sys, time
import eng4, cases
prob = cases.CaseIII("III.1")
pr = cProfile.Profile()
# prefix only (no profiling of interest), then the tasks
t0 = time.time()
pr.enable()
eng4.run(prob, 0, 400, 600, 3, 'prof4c', setwise=True)
pr.disable()
print("total", time.time() - t0)
p = pstats.Stats(pr); p.sort_stats("tottime").print_stats(18)
