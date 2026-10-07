# case III: table of the admissible single types (U;V) with the three X_0 situations (r = 2: none; r = 1: one
# inactive inner vertex; r = 0: two, in different pairs: the "a,a" and "a,b" classes are equivalent under relabelling
# when only one orbit is present), exact tests on S u N[p] u {z, sigma z}.
import sys, numpy as np
import eng2, cases
for name in sys.argv[1:]:
    prob = cases.CaseIII(name)
    root = eng2.Node(prob.AB.copy(), prob.sig); root.prepare()
    st = eng2.Counter()
    units = sorted(prob.units)
    print(name, "units:", {u: prob.units[u] for u in units})
    tab = {}
    for U in units:
        for V in units:
            if U == V: continue
            for N0, tgt in prob.options(U, V):
                if len(N0) == 1 and N0 != (21,): continue
                if len(N0) == 2 and N0 not in ((21, 23),): continue
                row = np.zeros(27, dtype=np.int64)
                for i in U: row[i] = 1
                for i in V: row[10 + i] = 1
                for u in N0: row[u] = 1
                ok = (not root.budget_fail(row, 0)) and root.psd_fail(row, 0, st) is None
                if ok:
                    tab.setdefault(U, []).append((V, len(N0)))
    for U in units:
        print("  U=%s: %d admissible V:" % (U, len(tab.get(U, []))), " ".join("%d%d/r%d" % (v[0], v[1], 2 - k) for v, k in tab.get(U, [])))
