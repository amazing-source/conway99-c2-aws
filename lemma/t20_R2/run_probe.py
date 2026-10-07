import sys, eng4probe, cases
prob = cases.CaseIII(sys.argv[1])
eng4probe.run(prob, int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), 3, "probe")
