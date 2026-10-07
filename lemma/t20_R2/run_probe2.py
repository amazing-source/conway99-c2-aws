import sys, eng4probe2, cases
prob = cases.CaseIII(sys.argv[1])
eng4probe2.run(prob, int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), "probe2")
