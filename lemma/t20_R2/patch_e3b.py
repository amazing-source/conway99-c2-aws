s = open("eng3_run.txt").read()
old = """def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, setwise=False, save_certs=0,
        use_rank=True):"""
new = """def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, setwise=False, save_certs=0,
        use_rank=True, width=0):
    # width = 0: every uncovered unit is examined at every node.  width = w > 0: only the w units that had the
    # fewest float survivors at the nearest ancestor where they were examined (all units at the root).  The
    # choice of the unit is a heuristic; the exhaustiveness argument does not depend on it."""
assert old in s; s = s.replace(old, new, 1)
old = """    def dfs(node, orbs, tg, degs, cnt, K, remaining):
        t = len(orbs)"""
new = """    def dfs(node, orbs, tg, degs, cnt, K, remaining, prio):
        t = len(orbs)"""
assert old in s; s = s.replace(old, new, 1)
old = """        best = None
        for U0 in sorted(remaining):
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if not cands:
                best = (U0, cands, None, [], [], 0)
                break
            R = rows_of(node.n, U0, cands)
            bb, pb = node.evaluate(R)
            looked[0] += len(cands)
            nk = int((~bb & ~pb).sum())
            if best is None or nk < best[5]:
                best = (U0, cands, R, bb, pb, nk)
            if nk == 0:
                break
"""
new = """        best = None
        order = sorted(remaining, key=lambda U: (prio.get(U, -1), U))
        prio2 = {U: prio[U] for U in remaining if U in prio}
        for idx, U0 in enumerate(order):
            if width and prio and idx >= width:
                break
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if not cands:
                best = (U0, cands, None, [], [], 0)
                prio2[U0] = 0
                break
            R = rows_of(node.n, U0, cands)
            bb, pb = node.evaluate(R)
            looked[0] += len(cands)
            nk = int((~bb & ~pb).sum())
            prio2[U0] = nk
            if best is None or nk < best[5]:
                best = (U0, cands, R, bb, pb, nk)
            if nk == 0:
                break
"""
assert old in s; s = s.replace(old, new, 1)
old = """                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3)"""
new = """                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3, prio2)"""
assert old in s; s = s.replace(old, new, 1)
old = """    dfs(root, [], [], [], cnt0, list(prob.group), units)"""
new = """    dfs(root, [], [], [], cnt0, list(prob.group), units, {})"""
assert old in s; s = s.replace(old, new, 1)
old = """           "setwise": setwise, "engine": "eng3", "use_rank": use_rank}"""
new = """           "setwise": setwise, "engine": "eng3", "use_rank": use_rank, "width": width}"""
assert old in s; s = s.replace(old, new, 1)
open("eng3_run.txt", "w").write(s)
m = open("mk_eng3.py").read()
old = """                   "use_rank=('norank' not in sys.argv[7:]))")"""
new = """                   "use_rank=('norank' not in sys.argv[7:]), width=width)")
r = r.replace("certs = 0\n", "certs = 0\nwidth = 0\n")
r = r.replace("        certs = int(a[6:])\n", "        certs = int(a[6:])\n    if a.startswith('width='):\n        width = int(a[6:])\n")"""
assert old in m; m = m.replace(old, new, 1)
open("mk_eng3.py", "w").write(m)
