s = open("eng3_run.txt").read()
old = """    L = norb + 1
    visited = [0] * L """
new = """    def pair_batch(o1, items):
        \"\"\"fills the pair cache for (o1, o2, pat), (o2, pat) in items: exact budgets (vectorised integer counts),
        float selection for PSD, every PSD rejection confirmed exactly by psd_fail\"\"\"
        nd = single_node(o1)
        R = np.zeros((len(items), nb + 2), dtype=np.int64)
        for a, (o2, pat) in enumerate(items):
            for i in o2[0]:
                R[a, i] = 1
            for i in o2[1]:
                R[a, 10 + i] = 1
            for u in o2[2]:
                R[a, u] = 1
            if pat & 1:
                R[a, nb] = 1
            if pat & 2:
                R[a, nb + 1] = 1
        bb, pb = nd.evaluate(R)
        for a, (o2, pat) in enumerate(items):
            if bb[a]:
                stats.add("pair_budget"); r = False
            elif pb[a] and nd.psd_fail(R[a], 0, stats) is not None:
                stats.add("pair_psd"); r = False
            else:
                r = True
            pairc[(o1, o2, pat)] = r

    L = norb + 1
    visited = [0] * L """
assert old in s
s = s.replace(old, new, 1)
old = """        out = []
        for V in sorted(rem2):
            if V == U0:
                continue
            for N0, tgt in prob.options(U0, V):
                if any(cnt[u] >= x0t[u] for u in N0) or any(cnt[sigb[u]] >= x0t[sigb[u]] for u in N0):
                    continue
                if K:
                    smallest = True
                    for g in K:
                        if tuple(sorted(g[u] for u in N0)) < N0:
                            smallest = False
                            break
                    if not smallest:
                        continue
                if not single_ok(U0, V, N0):
                    continue
                onew = (U0, V, N0)
                allowed = []
"""
new = """        out = []
        onews = []
        for V in sorted(rem2):
            if V == U0:
                continue
            for N0, tgt in prob.options(U0, V):
                if any(cnt[u] >= x0t[u] for u in N0) or any(cnt[sigb[u]] >= x0t[sigb[u]] for u in N0):
                    continue
                if K:
                    smallest = True
                    for g in K:
                        if tuple(sorted(g[u] for u in N0)) < N0:
                            smallest = False
                            break
                    if not smallest:
                        continue
                if not single_ok(U0, V, N0):
                    continue
                onews.append((V, N0, tgt))
        # fill the pair cache in batches
        for i in range(t):
            room = tg[i] - degs[i]
            oi = orbs[i]
            miss = []
            for V, N0, tgt in onews:
                onew = (U0, V, N0)
                for pat in (0, 1, 2, 3):
                    need = (pat & 1) + (pat >> 1)
                    if need > room or need > tgt:
                        continue
                    if (oi, onew, pat) not in pairc:
                        miss.append((onew, pat))
            if miss:
                pair_batch(oi, miss)
        for V, N0, tgt in onews:
            if True:
                onew = (U0, V, N0)
                allowed = []
"""
assert old in s
s = s.replace(old, new, 1)
open("eng3_run.txt", "w").write(s)
