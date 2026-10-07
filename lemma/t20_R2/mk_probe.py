# experimental copy of eng4 with a (float, non-pruning) probe: can the X_1-type vertices v_{c,c'} be added?
s = open("eng4.py").read()
old = """        node.prepare()
        visited[t] += 1
        best = None
        newdoms = {}"""
new = """        node.prepare()
        visited[t] += 1
        if t >= 3:
            Hs = prob.H
            n = node.n
            dead = False
            napp = 0
            for c in sorted(Hs):
                for c2 in sorted(Hs):
                    if c2 <= c:
                        continue
                    isx2 = any((c in o[0] and c2 in o[1]) or (c2 in o[0] and c in o[1]) for o in orbs)
                    if isx2:
                        continue
                    remc = any(c in U for U in remaining)
                    remc2 = any(c2 in U for U in remaining)
                    if remc and remc2:
                        continue
                    napp += 1
                    idx = list(range(nb, n))
                    rows = []
                    for k in range(0, 4):
                        for comb in itertools.combinations(idx, k):
                            r = np.zeros(n, dtype=np.int64)
                            r[c] = 1; r[10 + c2] = 1
                            for v in comb:
                                r[v] = 1
                            rows.append(r)
                    R_ = np.array(rows)
                    bb_, pb_ = node.evaluate(R_)
                    if not (~bb_ & ~pb_).any():
                        dead = True
            probe_app[t] += 1 if napp else 0
            probe_dead[t] += 1 if dead else 0
        best = None
        newdoms = {}"""
assert old in s; s = s.replace(old, new, 1)
old = """    looked = [0]"""
new = """    looked = [0]
    probe_app = [0] * L
    probe_dead = [0] * L"""
assert old in s; s = s.replace(old, new, 1)
old = """    print("lookahead candidates evaluated"""
new = """    print("PROBE applicable per level:", probe_app)
    print("PROBE dead per level      :", probe_dead)
    print("lookahead candidates evaluated"""
assert old in s; s = s.replace(old, new, 1)
open("eng4probe.py", "w").write(s)
