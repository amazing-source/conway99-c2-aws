m = open("mk_eng4.py").read()
# 1. inherit only when the stabiliser is trivial
old = """                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3, newdoms)\"\"\""""
new = """                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3,
                    newdoms if len(K) <= 1 else None)\"\"\""""
assert old in m, "p1"; m = m.replace(old, new, 1)
# 2. plan output: one line per visited node: depth, chosen unit, number of candidates, number kept
old = """r = r.replace('"engine": "eng3"', '"engine": "eng4"')"""
new = """old = \"\"\"        for a in todo:
            V, N0, tgt, choice, used = cands[a]
            if t == split_depth:\"\"\"
new = \"\"\"        if planf is not None and t >= split_depth + 1:
            planf.write("%d %d %d %d %d\\n" % (t, U0[0], U0[1], len(cands), len(todo)))
        for a in todo:
            V, N0, tgt, choice, used = cands[a]
            if t == split_depth:\"\"\"
assert old in r; r = r.replace(old, new, 1)
old = \"\"\"    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w")\"\"\"
new = \"\"\"    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w")
    planf = open("%s_%dof%d.plan" % (tag, part, nparts), "w") if plan else None\"\"\"
assert old in r; r = r.replace(old, new, 1)
old = \"\"\"        use_rank=True, width=0):\"\"\"
new = \"\"\"        use_rank=True, width=0, plan=False):\"\"\"
assert old in r; r = r.replace(old, new, 1)
old = \"\"\"    logf.close()
    if certf:\"\"\"
new = \"\"\"    logf.close()
    if planf:
        planf.close()
    if certf:\"\"\"
assert old in r; r = r.replace(old, new, 1)
r = r.replace('"engine": "eng3"', '"engine": "eng4"')"""
assert old in m, "p2"; m = m.replace(old, new, 1)
old = """t = open("run_eng3.py").read().replace("eng3", "eng4")"""
new = """t = open("run_eng3.py").read().replace("eng3", "eng4")
t = t.replace("width=width)", "width=width, plan=('plan' in sys.argv[7:]))")"""
assert old in m, "p3"; m = m.replace(old, new, 1)
open("mk_eng4.py", "w").write(m)
