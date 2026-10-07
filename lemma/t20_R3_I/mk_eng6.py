# builds eng6.py from eng5.py (round 2).  Changes, all local:
#  1. LAZY single-orbit certificates.  In eng5 every single orbit (U, V, N0) on the base was decided once, exactly
#     (budget count, then integer certificate).  In eng6 a single orbit has a status
#        0 = rejected exactly;  1 = float-rejected by the PSD selection, NOT certified;  2 = kept.
#     The look-ahead (which only chooses the unit) treats status 1 as rejected.  The exact step of the chosen unit
#     calls gen(..., exact=True), which certifies every status-1 orbit it meets (integer vector, Python integers;
#     psd_fail) before leaving it out; if no certificate exists the orbit is kept.
#  2. The exact step always rebuilds the complete candidate list of the chosen unit with gen(..., exact=True)
#     (eng5 did this only when the look-ahead list was inherited).
#  3. files=False: no log / plan / json files, no printing (for the drivers that run thousands of bases).
src = open("eng5.py").read()


def rep(a, b, count=1):
    global src
    assert src.count(a) == count, (src.count(a), a)
    src = src.replace(a, b)


rep("# eng5.py = eng4.py with a faster selection (see mk_eng5.py)",
    "# eng6.py = eng5.py with lazy single-orbit certificates (see mk_eng6.py)\n"
    "# eng5.py = eng4.py with a faster selection (see mk_eng5.py)")

# Node: float-only PSD selection for one row
rep('''    def child(self, row, zz):''', '''    def psd_float_bad(self, row, zz):
        """FLOAT selection only (proves nothing): True if some block fails the Schur test"""
        for blk, (b, c) in zip(self.blocks, self.vectors(row, zz)):
            bf = b.astype(np.float64)
            y = blk.Bp @ bf
            s = c - float(bf @ y)
            res = blk.N @ bf
            if s < -TOL_S or float(res @ res) > TOL_R:
                return True
        return False

    def child(self, row, zz):''')

rep('''def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, setwise=False, save_certs=0,
        use_rank=True, width=0, plan=False):''', '''def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, setwise=False, save_certs=0,
        use_rank=True, width=0, plan=False, files=True):''')

rep('''    certf = open("%s_certs_%dof%d.jsonl" % (tag, part, nparts), "w") if save_certs else None''',
    '''    certf = open("%s_certs_%dof%d.jsonl" % (tag, part, nparts), "w") if (save_certs and files) else None''')

rep('''    def single_ok(U, V, N0):
        key = (U, V, N0)
        r = single.get(key)
        if r is None:
            row = base_row(U, V, N0, nb)
            if root.budget_fail(row, 0):
                stats.add("single_budget"); r = False
            elif root.psd_fail(row, 0, stats) is not None:
                stats.add("single_psd"); r = False
            else:
                r = True
            single[key] = r
        return r
''', '''    def single_ok(U, V, N0, exact):
        """status 0 = rejected EXACTLY, 1 = float-rejected (not certified), 2 = kept.  With exact=True a status 1
        is certified (integer vector) or turned into 2; with exact=False it counts as rejected (look-ahead only)."""
        key = (U, V, N0)
        r = single.get(key)
        if r is None:
            row = base_row(U, V, N0, nb)
            if root.budget_fail(row, 0):
                stats.add("single_budget"); r = 0
            elif root.psd_float_bad(row, 0):
                r = 1
            else:
                r = 2
            single[key] = r
        if r == 1 and exact:
            row = base_row(U, V, N0, nb)
            if root.psd_fail(row, 0, stats) is not None:
                stats.add("single_psd"); r = 0
            else:
                stats.add("single_float_bad_not_certified_kept"); r = 2
            single[key] = r
        return r == 2
''')

rep('''    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w")
    planf = open("%s_%dof%d.plan" % (tag, part, nparts), "w") if plan else None''',
    '''    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w") if files else None
    planf = open("%s_%dof%d.plan" % (tag, part, nparts), "w") if (plan and files) else None''')

rep('''    def gen(U0, orbs, tg, degs, cnt, K, remaining):''', '''    def gen(U0, orbs, tg, degs, cnt, K, remaining, exact):''')
rep('''                if not single_ok(U0, V, N0):
                    continue''', '''                if not single_ok(U0, V, N0, exact):
                    continue''')
rep('''                lc = gen(U0, orbs, tg, degs, cnt, K, remaining)''', '''                lc = gen(U0, orbs, tg, degs, cnt, K, remaining, False)''')
rep('''        U0 = best[0]
        if best[2]:
            # exact step: the complete candidate list of the chosen unit
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if cands:
                R = rows_of(node.n, U0, cands)
                bb, pb, fb, vc = node.evaluate_f(R)
            else:
                R, bb, pb, fb, vc = None, [], [], [], None
        else:
            cands, R, bb, pb, fb, vc = best[3], best[4], best[5], best[6], best[7], best[8]
            if not cands:
                bb, pb = [], []
''', '''        U0 = best[0]
        # exact step: the complete candidate list of the chosen unit (every omitted single orbit is rejected exactly)
        cands = gen(U0, orbs, tg, degs, cnt, K, remaining, True)
        if cands:
            R = rows_of(node.n, U0, cands)
            bb, pb, fb, vc = node.evaluate_f(R)
        else:
            R, bb, pb, fb, vc = None, [], [], [], None
''')
rep('''                if state["done"] % progress_every == 0:''', '''                if logf is not None and state["done"] % progress_every == 0:''')
rep('''           "task_list_sha1": thash.hexdigest(), "setwise": setwise, "engine": "eng5", "use_rank": use_rank, "width": width}
    json.dump(out, open("%s_%dof%d.json" % (tag, part, nparts), "w"))
    print(prob.name''', '''           "task_list_sha1": thash.hexdigest(), "setwise": setwise, "engine": "eng6", "use_rank": use_rank, "width": width}
    if not files:
        return out
    json.dump(out, open("%s_%dof%d.json" % (tag, part, nparts), "w"))
    print(prob.name''')

#  4. Exact budget counts are done in int64 for whole batches (Node.budget_rows) instead of a float selection
#     followed by a scalar int64 recount: pair cache (pair_batch) and exact step.  Same counts, same results.
#  5. When the problem declares options_budget_exact (its options() already removed, by exact int64 counts, every
#     single orbit with a budget violation on the base) the scalar budget recount of a single orbit is skipped and
#     the float PSD status of all single orbits is computed in one batch (float: selection only).
#  6. plan="mem": the plan (level, unit, number of candidates, number kept) is returned in out["plan"].
rep("""    def psd_float_bad(self, row, zz):""", """    def budget_rows(self, R):
        \"\"\"EXACT (int64) budget test of a batch of candidate rows (zz = 0): True where the graph plus the orbit of
        the candidate has a pair with more than 2 - [adjacent] common neighbours\"\"\"
        RS = R[:, self.sigarr]
        bad = ((R @ self.A + R) > 2).any(1)              # the new vertex against an old vertex
        bad |= (R * RS).sum(1) > 2                        # the new vertex against its mate
        bad |= ((R @ self.W1) * R).sum(1) > 0             # two old neighbours that already have 2 - [adjacent]
        T = R * RS
        bad |= ((T @ self.W2) * T).sum(1) > 0             # two old vertices adjacent to both new vertices
        return bad

    def psd_float_bad(self, row, zz):""")

rep("""        bb = nd.evaluate_f(R, psd=False)[0]
        for a, (o2, pat) in enumerate(items):
            r = True
            if bb[a]:
                if nd.budget_fail(R[a], 0):          # int64 recount
                    stats.add("pair_budget"); r = False
                else:
                    stats.add("float_int_budget_mismatch")
            pairc[(o1, o2, pat)] = r
""", """        bb = nd.budget_rows(R).tolist()               # exact (int64)
        for a, (o2, pat) in enumerate(items):
            if bb[a]:
                stats.add("pair_budget")
            pairc[(o1, o2, pat)] = not bb[a]
""")

rep("""            row = base_row(U, V, N0, nb)
            if root.budget_fail(row, 0):
                stats.add("single_budget"); r = 0
            elif root.psd_float_bad(row, 0):""", """            row = base_row(U, V, N0, nb)
            if (not opt_exact) and root.budget_fail(row, 0):
                stats.add("single_budget"); r = 0
            elif root.psd_float_bad(row, 0):""")

rep("""    single = {}

    def single_ok(U, V, N0, exact):""", """    single = {}
    opt_exact = bool(getattr(prob, "options_budget_exact", False))
    if opt_exact:
        # float PSD status of every single orbit in one batch (selection only; status 1 is certified on demand)
        keys0 = []
        for U_ in sorted(units):
            for V_ in sorted(units):
                if V_ != U_:
                    for N0_, tgt_ in prob.options(U_, V_):
                        keys0.append((U_, V_, N0_))
        if keys0:
            R0 = np.zeros((len(keys0), nb), dtype=np.int64)
            for a_, (U_, V_, N0_) in enumerate(keys0):
                for i_ in U_:
                    R0[a_, i_] = 1
                for i_ in V_:
                    R0[a_, 10 + i_] = 1
                for u_ in N0_:
                    R0[a_, u_] = 1
            assert not root.budget_rows(R0).any(), "options() returned a single orbit with a budget violation"
            pb0 = root.evaluate_f(R0)[1].tolist()
            for k_, b_ in zip(keys0, pb0):
                single[k_] = 1 if b_ else 2

    def single_ok(U, V, N0, exact):""")

rep("""        ncand[t] += len(cands)
        todo = []
        for a, cd in enumerate(cands):
            if bb[a]:
                if node.budget_fail(R[a], 0):        # int64 recount of the violated budget
                    rej_b[t] += 1
                    continue
                stats.add("float_int_budget_mismatch")
""", """        ncand[t] += len(cands)
        todo = []
        bx = node.budget_rows(R).tolist() if cands else []     # exact (int64)
        for a, cd in enumerate(cands):
            if bx[a] != bool(bb[a]):
                stats.add("float_int_budget_mismatch")
            if bx[a]:
                rej_b[t] += 1
                continue
""")
rep("""        if planf is not None:
            planf.write("%d %d %d %d %d" % (t, U0[0], U0[1], len(cands), len(todo)) + chr(10))""", """        if planf is not None:
            planf.write("%d %d %d %d %d" % (t, U0[0], U0[1], len(cands), len(todo)) + chr(10))
        if plan == "mem":
            planmem.append([t, U0[0], U0[1], len(cands), len(todo)])""")
rep("""    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w") if files else None""", """    planmem = []
    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w") if files else None""")
rep("""    if not files:
        return out""", """    out["plan"] = planmem
    if not files:
        return out""")


#  7. width = w > 0 (announced in eng5 but not implemented there): below the root only the w units with the
#     fewest float survivors at the nearest ancestor where they were examined are examined (all units at the
#     root).  This changes only WHICH unit is chosen; the exact step of the chosen unit is unchanged.
rep("""    def dfs(node, orbs, tg, degs, cnt, K, remaining, doms):
        t = len(orbs)""", """    def dfs(node, orbs, tg, degs, cnt, K, remaining, doms, est=None):
        t = len(orbs)""")
rep("""        best = None
        newdoms = {}
        for U0 in sorted(remaining):
            inherited = doms is not None and U0 in doms""", """        best = None
        newdoms = {}
        newest = dict(est) if est else {}
        ulist = sorted(remaining)
        if width > 0 and est:
            ulist = sorted(ulist, key=lambda U_: (est.get(U_, 10 ** 9), U_))[:width]
        for U0 in ulist:
            inherited = doms is not None and U0 in doms""")
rep("""            if not lc:
                best = (U0, 0, inherited, lc, None, None, None, None, None)
                break""", """            if not lc:
                best = (U0, 0, inherited, lc, None, None, None, None, None)
                newest[U0] = 0
                break""")
rep("""            newdoms[U0] = [c for c, al in zip(lc, alive.tolist()) if al]""", """            newdoms[U0] = [c for c, al in zip(lc, alive.tolist()) if al]
            newest[U0] = nk""")
rep("""                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3,
                    newdoms if len(K2) == len(K) else None)""", """                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3,
                    newdoms if len(K2) == len(K) else None, newest)""")


#  8. plan="mem": a plan line gets a 6th field, the list of the positions (in the order of the kept children of the
#     node) of the children rejected by the rank bound.  Nothing else changes (same search, same counters).
rep("""        if plan == "mem":
            planmem.append([t, U0[0], U0[1], len(cands), len(todo)])
        for a in todo:""", """        pline = [t, U0[0], U0[1], len(cands), len(todo), []]
        if plan == "mem":
            planmem.append(pline)
        for pos_, a in enumerate(todo):""")
rep("""                if rv is not None:
                    rej_rank[t] += 1""", """                if rv is not None:
                    rej_rank[t] += 1
                    pline[5].append(pos_)""")

open("eng6.py", "w").write(src)
print("eng6.py written,", len(src), "bytes")
