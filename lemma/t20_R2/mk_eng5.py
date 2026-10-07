# builds eng5.py from eng4.py: same search, same exact tests, faster selection.
#  - the vectorised selection uses float64 BLAS products of 0/1 matrices (all values are small integers, so the
#    products are exact); every budget rejection that is USED (chosen unit, pair cache) is confirmed by the
#    int64 recount Node.budget_fail;
#  - the pair cache keeps only the budget test (exact); semidefiniteness is tested on the whole node only;
#  - the integer certificate of a PSD rejection is built from the border vector already computed by the selection
#    (same certificate search as Node.psd_fail, which remains the fallback).
s = open("eng4.py").read()
s = s.replace("# eng4.py = eng3.py with inherited look-ahead lists (see mk_eng4.py)",
              "# eng5.py = eng4.py with a faster selection (see mk_eng5.py)\n"
              "# eng4.py = eng3.py with inherited look-ahead lists (see mk_eng4.py)", 1)

old = """        self.W2 = (CA >= 1).astype(np.int64)
        np.fill_diagonal(self.W2, 0)
"""
new = """        self.W2 = (CA >= 1).astype(np.int64)
        np.fill_diagonal(self.W2, 0)
        self.Af = A.astype(np.float64)
        self.W1f = self.W1.astype(np.float64)
        self.W2f = self.W2.astype(np.float64)
"""
assert old in s; s = s.replace(old, new, 1)

old = "    def budget_fail(self, row, zz):"
new = '''    def evaluate_f(self, R, psd=True):
        """float64 selection (zz = 0).  Returns (budget_bad, psd_bad, first failing block, border vectors).
        The budget part is exact (integer-valued float products of 0/1 matrices); the PSD part is a float decision."""
        Rf = R.astype(np.float64)
        RSf = Rf[:, self.sigarr]
        bad = ((Rf @ self.Af + Rf) > 2.5).any(1)
        bad |= np.einsum("ij,ij->i", Rf, RSf) > 2.5
        bad |= np.einsum("ij,ij->i", Rf @ self.W1f, Rf) > 0.5
        T = Rf * RSf
        bad |= np.einsum("ij,ij->i", T @ self.W2f, T) > 0.5
        if not psd:
            return bad, None, None, None
        a = Rf[:, self.reps]
        b = Rf[:, self.sreps]
        aodd = b - a
        aev = a + b
        rf = Rf[:, self.fixed]
        vecs = ((aodd, 3.0), (-aodd, 4.0),
                (np.hstack((2 - 18 * rf, 4 - 18 * aev)), 58.0),
                (np.hstack((22 * rf - 4, 22 * aev - 8)), 80.0))
        fb = np.full(R.shape[0], -1, dtype=np.int64)
        for bi, (blk, (Bv, c)) in enumerate(zip(self.blocks, vecs)):
            Y = Bv @ blk.Bp
            sv = c - np.einsum("ij,ij->i", Bv, Y)
            Res = Bv @ blk.N
            r2 = np.einsum("ij,ij->i", Res, Res)
            f = (sv < -TOL_S) | (r2 > TOL_R)
            fb[(fb < 0) & f] = bi
        return bad, fb >= 0, fb, vecs

    def psd_cert_block(self, bi, bf, c, stats):
        """integer certificate on block bi for the border vector bf (integer-valued floats) and corner c:
        (block name, x, q) with q = x^T [[B, b], [b^T, c]] x < 0 in Python integers, or None if none is found here"""
        blk = self.blocks[bi]
        y = blk.Bp @ bf
        sv = c - float(bf @ y)
        res = blk.N @ bf
        r2 = float(res @ res)
        if sv >= -TOL_S and r2 <= TOL_R:
            return None
        bl = [int(round(v)) for v in bf.tolist()]
        ci = int(round(c))
        if r2 > TOL_R:
            t = (abs(sv) + 2.0) / (2.0 * r2)
            cands = [-y - t * res]
            if sv < -TOL_S:
                cands.append(-y)
        else:
            cands = [-y]
        for u in cands:
            for sc in (1, 2, 3, 4, 6, 12, 30, 60, 120, 420, 1000, 2520, 10 ** 4, 10 ** 5, 10 ** 6):
                uf = np.rint(u * sc)
                qf = float(uf @ (blk.Bf @ uf)) + 2.0 * sc * float(uf @ bf) + sc * sc * c
                if qf < -0.5:
                    ui = [int(v) for v in uf.tolist()]
                    q = pform(blk.Bl, ui) + 2 * sc * sum(map(_mul, ui, bl)) + sc * sc * ci
                    if q < 0:
                        stats.add("psd_reject_" + blk.name)
                        return (blk.name, ui + [sc], q)
        return None

    def budget_fail(self, row, zz):'''
assert old in s; s = s.replace(old, new, 1)

old = """        bb, pb = nd.evaluate(R)
        for a, (o2, pat) in enumerate(items):
            if bb[a]:
                stats.add("pair_budget"); r = False
            elif pb[a] and nd.psd_fail(R[a], 0, stats) is not None:
                stats.add("pair_psd"); r = False
            else:
                r = True
            pairc[(o1, o2, pat)] = r
"""
new = """        bb = nd.evaluate_f(R, psd=False)[0]
        for a, (o2, pat) in enumerate(items):
            r = True
            if bb[a]:
                if nd.budget_fail(R[a], 0):          # int64 recount
                    stats.add("pair_budget"); r = False
                else:
                    stats.add("float_int_budget_mismatch")
            pairc[(o1, o2, pat)] = r
"""
assert old in s; s = s.replace(old, new, 1)

old = """            Rl = rows_of(node.n, U0, lc)
            bbl, pbl = node.evaluate(Rl)
"""
new = """            Rl = rows_of(node.n, U0, lc)
            bbl, pbl, fbl, vcl = node.evaluate_f(Rl)
"""
assert old in s; s = s.replace(old, new, 1)
old = """                best = (U0, nk, inherited, lc, Rl, bbl, pbl)"""
new = """                best = (U0, nk, inherited, lc, Rl, bbl, pbl, fbl, vcl)"""
assert old in s; s = s.replace(old, new, 1)
old = """                best = (U0, 0, inherited, lc, None, None, None)"""
new = """                best = (U0, 0, inherited, lc, None, None, None, None, None)"""
assert old in s; s = s.replace(old, new, 1)
old = """            if cands:
                R = rows_of(node.n, U0, cands)
                bb, pb = node.evaluate(R)
            else:
                R, bb, pb = None, [], []
        else:
            cands, R, bb, pb = best[3], best[4], best[5], best[6]
            if not cands:
                bb, pb = [], []
"""
new = """            if cands:
                R = rows_of(node.n, U0, cands)
                bb, pb, fb, vc = node.evaluate_f(R)
            else:
                R, bb, pb, fb, vc = None, [], [], [], None
        else:
            cands, R, bb, pb, fb, vc = best[3], best[4], best[5], best[6], best[7], best[8]
            if not cands:
                bb, pb = [], []
"""
assert old in s; s = s.replace(old, new, 1)
old = """            if bb[a]:
                rej_b[t] += 1
                continue
            if pb[a]:
                r = node.psd_fail(R[a], 0, stats)
                if r is not None:"""
new = """            if bb[a]:
                if node.budget_fail(R[a], 0):        # int64 recount of the violated budget
                    rej_b[t] += 1
                    continue
                stats.add("float_int_budget_mismatch")
            if pb[a]:
                bi = int(fb[a])
                r = node.psd_cert_block(bi, vc[bi][0][a], vc[bi][1], stats)
                if r is None:
                    r = node.psd_fail(R[a], 0, stats)
                if r is not None:"""
assert old in s; s = s.replace(old, new, 1)
old = """        if t == norb:
            if any(degs[i] != tg[i] for i in range(norb)):
                stats.add("final_degH"); return
            if any(cnt[u] != x0t[u] for u in x0):
                stats.add("final_x0deg"); return
"""
new = """        if t == norb:
            if not getattr(prob, "caps_only", False):
                if any(degs[i] != tg[i] for i in range(norb)):
                    stats.add("final_degH"); return
                if any(cnt[u] != x0t[u] for u in x0):
                    stats.add("final_x0deg"); return
"""
assert old in s; s = s.replace(old, new, 1)
old = """            if t == split_depth:
                state["tasks"] += 1
                if (state["tasks"] - 1) % nparts != part:
                    continue
                state["mine"] += 1
            kept[t] += 1"""
new = """            if t == split_depth:
                state["tasks"] += 1
                thash.update(repr((orbs, U0, V, N0, choice)).encode())
                if (state["tasks"] - 1) % nparts != part:
                    continue
                state["mine"] += 1
            kept[t] += 1"""
assert old in s; s = s.replace(old, new, 1)
old = """    L = norb + 1
    visited = [0] * L """
new = """    import hashlib
    thash = hashlib.sha1()
    L = norb + 1
    visited = [0] * L """
assert old in s; s = s.replace(old, new, 1)
old = """           "setwise": setwise, "engine": "eng4","""
new = """           "task_list_sha1": thash.hexdigest(), "setwise": setwise, "engine": "eng4","""
assert old in s; s = s.replace(old, new, 1)
old = """    print("tasks at split depth: total %d, mine %d, done %d" % (state["tasks"], state["mine"], state["done"]))"""
new = """    print("tasks at split depth: total %d, mine %d, done %d" % (state["tasks"], state["mine"], state["done"]))
    print("sha1 of the ordered list of ALL tasks at the split depth:", thash.hexdigest())"""
assert old in s; s = s.replace(old, new, 1)
s = s.replace('"engine": "eng4"', '"engine": "eng5"')
open("eng5.py", "w").write(s)
t = open("run_eng4.py").read().replace("eng4", "eng5")
open("run_eng5.py", "w").write(t)
print("eng5.py and run_eng5.py written")
