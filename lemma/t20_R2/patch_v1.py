m = open("mk_eng4.py").read()
old = "        if planf is not None and t >= split_depth + 1:"
new = "        if planf is not None:"
assert old in m; m = m.replace(old, new, 1)
open("mk_eng4.py", "w").write(m)

s = open("engv_run.txt").read()
old = """def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, cert_cap=0, setwise=False, order="mincand",
        use_rank=True):"""
new = """def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, cert_cap=0, setwise=False, order="mincand",
        use_rank=True, plan_file=None):
    # plan_file: the units are taken from a plan written by eng4.py (one line per visited node, in DFS order:
    # depth, unit, number of candidates, number kept).  The choice of the unit is not part of the proof; the
    # verifier regenerates all candidates of that unit with its own code, tests them with its own tests, and stops
    # with an error if its number of kept candidates differs from the plan."""
assert old in s; s = s.replace(old, new, 1)
old = """    def dfs(A, orbs, tg, degs, cnt, K, remaining):
        t = len(orbs)"""
new = """    planit = iter(open(plan_file)) if plan_file else None
    mism = {"cands": 0}

    def dfs(A, orbs, tg, degs, cnt, K, remaining):
        t = len(orbs)"""
assert old in s; s = s.replace(old, new, 1)
old = """        visited[t] += 1
        if order == "first":
            U0 = min(remaining)
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
        else:"""
new = """        visited[t] += 1
        pl = None
        if planit is not None:
            pl = [int(v) for v in next(planit).split()]
            assert pl[0] == t, "plan out of step (depth)"
            U0 = (pl[1], pl[2])
            assert U0 in remaining, "plan out of step (unit)"
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if len(cands) != pl[3]:
                mism["cands"] += 1
        elif order == "first":
            U0 = min(remaining)
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
        else:"""
assert old in s; s = s.replace(old, new, 1)
# two-phase: test all candidates, compare with the plan, then recurse
old = """        n = A.shape[0] + 2
        sg = sig_of(n)
        for (V, N0, tgt, choice, used) in cands:
            if t == split_depth:
                state["tasks"] += 1
                if (state["tasks"] - 1) % nparts != part:
                    continue
                state["mine"] += 1
            tested[t] += 1
            B = add_orbit(A, U0, V, N0)
            z, sz = n - 2, n - 1
            d2 = list(degs)
            for q, pat in enumerate(choice):
                zq, sq = nb + 2 * q, nb + 2 * q + 1
                if pat & 1:
                    B[z, zq] = B[zq, z] = 1; B[sz, sq] = B[sq, sz] = 1
                if pat & 2:
                    B[z, sq] = B[sq, z] = 1; B[sz, zq] = B[zq, sz] = 1
                d2[q] += (pat & 1) + (pat >> 1)
            if budgets_fail(B):
                rej_b[t] += 1
            elif tester.reject(B, sg, "L%d" % t) is not None:
                rej_p[t] += 1
            else:
                passed[t] += 1
                rv = rank_dead(B, sg) if use_rank else None
"""
new = """        n = A.shape[0] + 2
        sg = sig_of(n)
        good = []
        for (V, N0, tgt, choice, used) in cands:
            tested[t] += 1
            B = add_orbit(A, U0, V, N0)
            z, sz = n - 2, n - 1
            d2 = list(degs)
            for q, pat in enumerate(choice):
                zq, sq = nb + 2 * q, nb + 2 * q + 1
                if pat & 1:
                    B[z, zq] = B[zq, z] = 1; B[sz, sq] = B[sq, sz] = 1
                if pat & 2:
                    B[z, sq] = B[sq, z] = 1; B[sz, zq] = B[zq, sz] = 1
                d2[q] += (pat & 1) + (pat >> 1)
            if budgets_fail(B):
                rej_b[t] += 1
            elif tester.reject(B, sg, "L%d" % t) is not None:
                rej_p[t] += 1
            else:
                good.append((V, N0, tgt, choice, used, B, d2))
        if pl is not None:
            assert len(good) == pl[4], "DISAGREEMENT with the plan: kept %d, plan %d at depth %d" % (len(good), pl[4], t)
        for (V, N0, tgt, choice, used, B, d2) in good:
            if t == split_depth:
                state["tasks"] += 1
                if (state["tasks"] - 1) % nparts != part:
                    continue
                state["mine"] += 1
            if True:
                passed[t] += 1
                rv = rank_dead(B, sg) if use_rank else None
"""
assert old in s; s = s.replace(old, new, 1)
old = """           "setwise": setwise, "order": order, "engine": "engv", "use_rank": use_rank}"""
new = """           "setwise": setwise, "order": order, "engine": "engv", "use_rank": use_rank,
           "plan_file": plan_file, "plan_candidate_count_mismatches": mism["cands"]}
    if planit is not None:
        rest = sum(1 for _ in planit)
        out["plan_lines_left"] = rest
        print("plan followed: lines left unread %d, nodes with a different candidate count %d" % (rest, mism["cands"]))"""
assert old in s; s = s.replace(old, new, 1)
open("engv_run.txt", "w").write(s)
r = open("mk_engv.py").read()
old = """engv.run(prob, part, nparts, tlim, sd, tag, order=order, use_rank=("norank" not in sys.argv[7:]))"""
new = """planf = None
for a in sys.argv[7:]:
    if a.startswith("plan="):
        planf = a[5:]
engv.run(prob, part, nparts, tlim, sd, tag, order=order, use_rank=("norank" not in sys.argv[7:]), plan_file=planf)"""
assert old in r; r = r.replace(old, new, 1)
# do not re-patch eng3_run.txt in mk_engv
i = r.index('t = open("eng3_run.txt").read()')
r = r[:i] + 'print("ok")\n'
open("mk_engv.py", "w").write(r)
