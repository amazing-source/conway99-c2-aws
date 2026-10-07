# eng4.py = eng3.py with inherited look-ahead lists (see mk_eng4.py)
# T20 round 2: orbit-by-orbit engine with DYNAMIC unit order ("fail first").  Same model as eng.py (see its header).
# At every node all uncovered units are examined (floating-point selection, vectorised); the unit with the fewest
# surviving candidates is chosen (the first one, in increasing order, among ties; the scan stops at the first
# unit with no survivor).  Exhaustiveness: the chosen unit must be N(z) n S+ of some vertex z of X_2 whose orbit
# is not yet placed, and ALL candidates (V, N0, edges to the earlier orbits) of that unit are either kept or
# rejected exactly (budget count, or integer certificate, or exact elimination).  The other units only serve to
# choose; nothing is concluded from them.
# Tests:
#  - budgets: incremental (only the pairs whose common-neighbour count changes);
#  - semidefiniteness: sigma-blocks (odd block G = 3I - A^ with 0 <= G <= 7; even blocks of M1 and M2) and Schur
#    complements with respect to the parent node: [[B, b], [b^T, c]] >= 0  iff  b in range(B) and c - b^T B^+ b >= 0.
#    The floating-point Schur test only SELECTS; every rejection is confirmed by an integer vector c with
#    c^T Block c < 0 evaluated in Python integers (Block is the integer block matrix; with x = P c, P the integer
#    block basis, c^T Block c = x^T M x up to the positive factor 18 or 22 on odd blocks).  If no integer vector is
#    found the candidate is decided by exact rational elimination.
# Does not import r2c.py or eng.py.
import json, os, sys, time, itertools
from fractions import Fraction
from operator import mul as _mul
import numpy as np

TOL_S = 1e-7      # Schur complement tolerance (float selection only)
TOL_R = 1e-7      # range-residual tolerance
RANK_EPS = 1e-8


class Counter:
    def __init__(self):
        self.c = {}

    def add(self, k, n=1):
        self.c[k] = self.c.get(k, 0) + n


def pform(B, x):
    """x^T B x with Python integers (B: list of lists of Python ints, x: list of Python ints)"""
    tot = 0
    for row, xa in zip(B, x):
        if xa:
            tot += xa * sum(map(_mul, row, x))
    return tot


def exact_psd(Q):
    n = len(Q)
    A = [[Fraction(int(x)) for x in row] for row in Q]
    idx = list(range(n))
    while idx:
        for i in idx:
            if A[i][i] < 0:
                return False
        piv = None
        for i in idx:
            if A[i][i] > 0:
                piv = i
                break
        if piv is None:
            return all(A[i][j] == 0 for i in idx for j in idx)
        idx.remove(piv)
        p = A[piv][piv]
        for i in idx:
            f = A[i][piv] / p
            if f != 0:
                for j in idx:
                    A[i][j] -= f * A[piv][j]
    return True


class Block:
    """a PSD (float-checked) integer block of the parent with its pseudo-inverse and kernel projector"""
    __slots__ = ("B", "Bp", "N", "name", "Bf", "Bl")

    def __init__(self, B, name):
        self.B = B
        self.name = name
        self.Bf = B.astype(np.float64)
        self.Bl = B.tolist()           # Python integers
        w, V = np.linalg.eigh(B.astype(np.float64))
        scale = max(1.0, float(w[-1]))
        pos = w > RANK_EPS * scale
        Vp = V[:, pos]
        self.Bp = (Vp / w[pos]) @ Vp.T
        V0 = V[:, ~pos]
        self.N = V0 @ V0.T


class Node:
    """a completely known sigma-invariant graph"""

    def __init__(self, A, sig):
        self.A = A
        self.n = A.shape[0]
        self.sig = list(sig)
        self.reps = [v for v in range(self.n) if self.sig[v] > v]
        self.sreps = [self.sig[v] for v in self.reps]
        self.fixed = [v for v in range(self.n) if self.sig[v] == v]
        self.ready = False

    def prepare(self):
        if self.ready:
            return
        A = self.A
        R, SR, F = self.reps, self.sreps, self.fixed
        k, f = len(R), len(F)
        self.sigarr = np.array(self.sig)
        self.C = A @ A
        CA = self.C + A
        self.W1 = (CA >= 2).astype(np.int64)
        np.fill_diagonal(self.W1, 0)
        self.W2 = (CA >= 1).astype(np.int64)
        np.fill_diagonal(self.W2, 0)
        Aodd = A[np.ix_(R, R)] - A[np.ix_(R, SR)]
        Aev = A[np.ix_(R, R)] + A[np.ix_(R, SR)]
        G = 3 * np.eye(k, dtype=np.int64) - Aodd
        Hm = 7 * np.eye(k, dtype=np.int64) - G
        E1 = np.zeros((f + k, f + k), dtype=np.int64)
        E2 = np.zeros((f + k, f + k), dtype=np.int64)
        AF = A[np.ix_(F, F)]
        E1[:f, :f] = 27 * np.eye(f, dtype=np.int64) - 9 * AF + 1
        E2[:f, :f] = 44 * np.eye(f, dtype=np.int64) + 11 * AF - 2
        AFR = A[np.ix_(F, R)]
        E1[:f, f:] = 2 - 18 * AFR
        E1[f:, :f] = (2 - 18 * AFR).T
        E2[:f, f:] = 22 * AFR - 4
        E2[f:, :f] = (22 * AFR - 4).T
        E1[f:, f:] = 54 * np.eye(k, dtype=np.int64) - 18 * Aev + 4
        E2[f:, f:] = 88 * np.eye(k, dtype=np.int64) + 22 * Aev - 8
        self.blocks = [Block(G, "M1odd"), Block(Hm, "M2odd"), Block(E1, "M1even"), Block(E2, "M2even")]
        self.ready = True

    def vectors(self, row, zz):
        """the four border vectors and corner entries of the candidate orbit"""
        a = row[self.reps]
        b = row[self.sreps]
        aodd = b - a
        aev = a + b
        rf = row[self.fixed]
        return ((aodd, 3 + zz), (-aodd, 4 - zz),
                (np.concatenate((2 - 18 * rf, 4 - 18 * aev)), 58 - 18 * zz),
                (np.concatenate((22 * rf - 4, 22 * aev - 8)), 80 + 22 * zz))

    def evaluate(self, R):
        """vectorised selection for a batch of candidate rows (zz = 0): returns (budget_bad [exact], psd_bad [float])"""
        A = self.A
        RS = R[:, self.sigarr]
        bad = ((R @ A + R) > 2).any(1)
        bad |= (R * RS).sum(1) > 2
        bad |= ((R @ self.W1) * R).sum(1) > 0
        T = R * RS
        bad |= ((T @ self.W2) * T).sum(1) > 0
        a = R[:, self.reps]
        b = R[:, self.sreps]
        aodd = (b - a).astype(np.float64)
        aev = a + b
        rf = R[:, self.fixed]
        vecs = ((aodd, 3.0), (-aodd, 4.0),
                (np.hstack((2 - 18 * rf, 4 - 18 * aev)).astype(np.float64), 58.0),
                (np.hstack((22 * rf - 4, 22 * aev - 8)).astype(np.float64), 80.0))
        pb = np.zeros(R.shape[0], dtype=bool)
        for blk, (Bv, c) in zip(self.blocks, vecs):
            Y = Bv @ blk.Bp
            s = c - np.einsum("ij,ij->i", Bv, Y)
            Res = Bv @ blk.N
            r2 = np.einsum("ij,ij->i", Res, Res)
            pb |= (s < -TOL_S) | (r2 > TOL_R)
        return bad, pb

    def budget_fail(self, row, zz):
        A = self.A
        rs = row[self.sigarr]
        # z against old vertices
        cn = A @ row
        if zz:
            cn = cn + rs
        if (cn + row > 2).any():
            return True
        # z against sigma z
        if int(row @ rs) + zz > 2:
            return True
        # old pairs inside N(z)
        idx = np.flatnonzero(row)
        if len(idx) > 1:
            sub = self.C[np.ix_(idx, idx)] + A[np.ix_(idx, idx)] + 1 + np.outer(rs[idx], rs[idx])
            np.fill_diagonal(sub, 0)
            if (sub > 2).any():
                return True
        return False

    def psd_fail(self, row, zz, stats):
        """None if the candidate is kept; else (block name, x, q): x integer vector in block coordinates (last
        coordinate = the new orbit), q = x^T Block' x < 0 evaluated in Python integers, Block' = [[B, b], [b^T, c]]
        (x None if the rejection was decided by exact rational elimination)"""
        vecs = self.vectors(row, zz)
        for blk, (b, c) in zip(self.blocks, vecs):
            bf = b.astype(np.float64)
            y = blk.Bp @ bf
            s = c - float(bf @ y)
            res = blk.N @ bf
            r2 = float(res @ res)
            if s >= -TOL_S and r2 <= TOL_R:
                continue
            bl = b.tolist()
            ci = int(c)
            cert = None
            if r2 > TOL_R:
                t = (abs(s) + 2.0) / (2.0 * r2)
                cands = [-y - t * res]
                if s < -TOL_S:
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
                            cert = (ui + [sc], q)
                            break
                if cert:
                    break
            if cert is None:
                Bn = [rw + [bb] for rw, bb in zip(blk.Bl, bl)]
                Bn.append(bl + [ci])
                w, V = np.linalg.eigh(np.array(Bn, dtype=np.float64))
                if w[0] < 0:
                    v = V[:, 0]
                    mx = float(np.max(np.abs(v)))
                    for sc in (2, 3, 6, 12, 30, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10):
                        x = [int(round(float(tt) * sc / mx)) for tt in v]
                        q = pform(Bn, x)
                        if q < 0:
                            cert = (x, q)
                            break
                if cert is None:
                    if exact_psd(Bn):
                        stats.add("float_reject_but_exactly_psd_" + blk.name)
                        continue
                    stats.add("rejected_by_exact_elimination_" + blk.name)
                    return (blk.name, None, None)
            stats.add("psd_reject_" + blk.name)
            return (blk.name, cert[0], cert[1])
        return None

    def child(self, row, zz):
        n = self.n
        B = np.zeros((n + 2, n + 2), dtype=np.int64)
        B[:n, :n] = self.A
        rs = row[np.array(self.sig)]
        B[n, :n] = row
        B[:n, n] = row
        B[n + 1, :n] = rs
        B[:n, n + 1] = rs
        B[n, n + 1] = B[n + 1, n] = zz
        return Node(B, self.sig + [n + 1, n])


def full_budget_fail(A):
    C = A @ A
    V = C + A > 2
    np.fill_diagonal(V, False)
    return bool(V.any())


def exact_rank(M):
    import flint
    return flint.fmpz_mat([[int(x) for x in row] for row in M.tolist()]).rank()


def rank_violation(node):
    """exact: odd Gram of rank > 22 or even part of M1 of rank > 22 (rank bound); None if no violation"""
    node.prepare()
    k = len(node.reps)
    if k + len(node.fixed) < 23:
        return None
    if k >= 23:
        ro = exact_rank(node.blocks[0].B)
        if ro > 22:
            return ("odd", ro)
    re_ = exact_rank(node.blocks[2].B)
    if re_ > 22:
        return ("even", re_)
    return None


def run(prob, part, nparts, tlim, split_depth, tag, progress_every=50, setwise=False, save_certs=0,
        use_rank=True, width=0, plan=False):
    # width = 0: every uncovered unit is examined at every node.  width = w > 0: only the w units that had the
    # fewest float survivors at the nearest ancestor where they were examined (all units at the root).  The
    # choice of the unit is a heuristic; the exhaustiveness argument does not depend on it.
    t0 = time.time()
    stats = Counter()
    AB = prob.AB
    nb = AB.shape[0]
    sigb = list(prob.sig)
    assert not full_budget_fail(AB)
    root = Node(AB.copy(), sigb)
    root.prepare()
    for blk in root.blocks:
        w = np.linalg.eigvalsh(blk.B.astype(np.float64))
        assert w[0] > -1e-7, "base graph not PSD (float)"
    units = dict(prob.units)
    norb = sum(units.values()) // 2
    x0 = list(prob.x0)
    x0t = dict(prob.x0_target)
    certf = open("%s_certs_%dof%d.jsonl" % (tag, part, nparts), "w") if save_certs else None
    ncert = [0]

    def base_row(U, V, N0, n):
        row = np.zeros(n, dtype=np.int64)
        for i in U:
            row[i] = 1
        for i in V:
            row[10 + i] = 1
        for u in N0:
            row[u] = 1
        return row

    single = {}

    def single_ok(U, V, N0):
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

    singlenode = {}

    def single_node(o):
        nd = singlenode.get(o)
        if nd is None:
            nd = root.child(base_row(o[0], o[1], o[2], nb), 0)
            nd.prepare()
            singlenode[o] = nd
        return nd

    pairc = {}

    def pair_ok(o1, o2, pat):
        key = (o1, o2, pat)
        r = pairc.get(key)
        if r is None:
            nd = single_node(o1)
            row = base_row(o2[0], o2[1], o2[2], nb + 2)
            if pat & 1:
                row[nb] = 1
            if pat & 2:
                row[nb + 1] = 1
            if nd.budget_fail(row, 0):
                stats.add("pair_budget"); r = False
            elif nd.psd_fail(row, 0, stats) is not None:
                stats.add("pair_psd"); r = False
            else:
                r = True
            pairc[key] = r
        return r

    def pair_batch(o1, items):
        """fills the pair cache for (o1, o2, pat), (o2, pat) in items: exact budgets (vectorised integer counts),
        float selection for PSD, every PSD rejection confirmed exactly by psd_fail"""
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
    visited = [0] * L          # nodes at which a unit is chosen
    ncand = [0] * L            # candidates of the chosen unit (after the cached single / pair tests)
    kept = [0] * L
    rej_b = [0] * L
    rej_p = [0] * L
    rej_rank = [0] * L
    looked = [0]
    probe_app = [0] * L
    probe_dead = [0] * L
    survivors = []
    state = {"timeout": False, "tasks": 0, "mine": 0, "done": 0}
    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w")
    planf = open("%s_%dof%d.plan" % (tag, part, nparts), "w") if plan else None

    def gen(U0, orbs, tg, degs, cnt, K, remaining):
        """all candidates (V, N0, tgt, choice, used) for the unit U0 that pass the caps, the symmetry rule and the
        cached exact single / pair tests"""
        t = len(orbs)
        rem2 = dict(remaining)
        rem2[U0] -= 1
        if rem2[U0] == 0:
            del rem2[U0]
        out = []
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
                ok = True
                for i in range(t):
                    room = tg[i] - degs[i]
                    pats = []
                    for pat in (0, 1, 2, 3):
                        need = (pat & 1) + (pat >> 1)
                        if need > room or need > tgt:
                            continue
                        if pair_ok(orbs[i], onew, pat):
                            pats.append(pat)
                    if not pats:
                        ok = False
                        break
                    allowed.append(pats)
                if not ok:
                    stats.add("no_pattern")
                    continue
                for choice in itertools.product(*allowed):
                    used = sum((pat & 1) + (pat >> 1) for pat in choice)
                    if used > tgt:
                        continue
                    out.append((V, N0, tgt, choice, used))
        return out

    def rows_of(n, U0, cands):
        R = np.zeros((len(cands), n), dtype=np.int64)
        for a, (V, N0, tgt, choice, used) in enumerate(cands):
            for i in U0:
                R[a, i] = 1
            for i in V:
                R[a, 10 + i] = 1
            for u in N0:
                R[a, u] = 1
            for q, pat in enumerate(choice):
                if pat & 1:
                    R[a, nb + 2 * q] = 1
                if pat & 2:
                    R[a, nb + 2 * q + 1] = 1
        return R

    NEED = (0, 1, 1, 2)

    def extend(dom, U0, orbs, tg, degs, cnt, remaining):
        """candidates of U0 at the current node obtained from the parent's float survivors `dom` (look-ahead only)"""
        last = len(orbs) - 1
        olast = orbs[last]
        room_last = tg[last] - degs[last]
        miss = []
        seen = set()
        for (V, N0, tgt, choice, used) in dom:
            if (V, N0) in seen:
                continue
            seen.add((V, N0))
            onew = (U0, V, N0)
            for pat in (0, 1, 2, 3):
                if NEED[pat] > room_last or NEED[pat] > tgt:
                    continue
                if (olast, onew, pat) not in pairc:
                    miss.append((onew, pat))
        if miss:
            pair_batch(olast, miss)
        out = []
        for (V, N0, tgt, choice, used) in dom:
            if V not in remaining:
                continue
            if any(cnt[u] >= x0t[u] for u in N0) or any(cnt[sigb[u]] >= x0t[sigb[u]] for u in N0):
                continue
            ok = True
            for i2 in range(last):
                p = choice[i2]
                if p and NEED[p] > tg[i2] - degs[i2]:
                    ok = False
                    break
            if not ok:
                continue
            onew = (U0, V, N0)
            for pat in (0, 1, 2, 3):
                nd_ = NEED[pat]
                if nd_ > room_last or used + nd_ > tgt:
                    continue
                if pairc[(olast, onew, pat)]:
                    out.append((V, N0, tgt, choice + (pat,), used + nd_))
        return out

    def dfs(node, orbs, tg, degs, cnt, K, remaining, doms):
        t = len(orbs)
        if state["timeout"]:
            return
        if time.time() - t0 > tlim:
            state["timeout"] = True
            return
        if t == norb:
            if any(degs[i] != tg[i] for i in range(norb)):
                stats.add("final_degH"); return
            if any(cnt[u] != x0t[u] for u in x0):
                stats.add("final_x0deg"); return
            stats.add("complete")
            survivors.append({"orbs": [[list(o[0]), list(o[1]), list(o[2])] for o in orbs],
                              "A": ["".join(map(str, r)) for r in node.A.tolist()]})
            return
        node.prepare()
        visited[t] += 1
        if t >= 2:
            G = node.blocks[0].B
            k = G.shape[0]
            cvec = np.zeros(k, dtype=np.int64); cvec[:10] = 1
            inner = np.zeros(k, dtype=bool)
            for ii, v in enumerate(node.reps):
                if node.A[v, node.sig[v]]:
                    inner[ii] = True
            viol = False
            nfound = 0
            import itertools as _it
            idxs = list(range(k))
            for size in (2, 3, 4):
                for comb in _it.combinations(idxs, size):
                    sub = G[np.ix_(comb, comb)]
                    for signs in _it.product((1, -1), repeat=size - 1):
                        sg = np.array((1,) + signs)
                        for flip in (1, -1):
                            nv = sg * flip
                            q = int(nv @ sub @ nv)
                            sdot = int((cvec[list(comb)] * nv).sum())
                            if q == 2 * sdot and q > 0:
                                nfound += 1
                                full = np.zeros(k, dtype=np.int64); full[list(comb)] = nv
                                cp = cvec - G @ full
                                if (np.abs(cp[~inner]) > 1).any() or (np.abs(cp[inner]) > 2).any():
                                    viol = True
            probe_app[t] += 1 if nfound else 0
            probe_dead[t] += 1 if viol else 0
        best = None
        newdoms = {}
        for U0 in sorted(remaining):
            inherited = doms is not None and U0 in doms
            if inherited:
                lc = extend(doms[U0], U0, orbs, tg, degs, cnt, remaining)
            else:
                lc = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if not lc:
                best = (U0, 0, inherited, lc, None, None, None)
                break
            Rl = rows_of(node.n, U0, lc)
            bbl, pbl = node.evaluate(Rl)
            looked[0] += len(lc)
            alive = ~bbl & ~pbl
            nk = int(alive.sum())
            newdoms[U0] = [c for c, al in zip(lc, alive.tolist()) if al]
            if best is None or nk < best[1]:
                best = (U0, nk, inherited, lc, Rl, bbl, pbl)
            if nk == 0:
                break
        U0 = best[0]
        if best[2]:
            # exact step: the complete candidate list of the chosen unit
            cands = gen(U0, orbs, tg, degs, cnt, K, remaining)
            if cands:
                R = rows_of(node.n, U0, cands)
                bb, pb = node.evaluate(R)
            else:
                R, bb, pb = None, [], []
        else:
            cands, R, bb, pb = best[3], best[4], best[5], best[6]
            if not cands:
                bb, pb = [], []
        ncand[t] += len(cands)
        todo = []
        for a, cd in enumerate(cands):
            if bb[a]:
                rej_b[t] += 1
                continue
            if pb[a]:
                r = node.psd_fail(R[a], 0, stats)
                if r is not None:
                    rej_p[t] += 1
                    if certf is not None and ncert[0] < save_certs and r[1] is not None:
                        ncert[0] += 1
                        ch = node.child(R[a], 0)
                        certf.write(json.dumps({"block": r[0], "c": r[1], "q": r[2], "sig": ch.sig,
                                                "A": ["".join(map(str, rr)) for rr in ch.A.tolist()]}) + "\n")
                    continue
                stats.add("float_selected_but_not_rejected")
            todo.append(a)
        if planf is not None:
            planf.write("%d %d %d %d %d" % (t, U0[0], U0[1], len(cands), len(todo)) + chr(10))
        for a in todo:
            V, N0, tgt, choice, used = cands[a]
            if t == split_depth:
                state["tasks"] += 1
                if (state["tasks"] - 1) % nparts != part:
                    continue
                state["mine"] += 1
            kept[t] += 1
            ch = node.child(R[a], 0)
            dead = False
            if use_rank:
                rv = rank_violation(ch)
                if rv is not None:
                    rej_rank[t] += 1
                    stats.add("rank_%s_%d" % rv)
                    dead = True
            if not dead:
                rem3 = dict(remaining)
                for W in (U0, V):
                    rem3[W] -= 1
                    if rem3[W] == 0:
                        del rem3[W]
                cnt2 = dict(cnt)
                for u in N0:
                    cnt2[u] += 1
                    cnt2[sigb[u]] += 1
                if setwise:
                    K2 = [g for g in K if tuple(sorted(g[u] for u in N0)) == N0]
                else:
                    K2 = [g for g in K if all(g[u] == u for u in N0)]
                d2 = list(degs)
                for q, pat in enumerate(choice):
                    d2[q] += (pat & 1) + (pat >> 1)
                dfs(ch, orbs + [(U0, V, N0)], tg + [tgt], d2 + [used], cnt2, K2, rem3,
                    newdoms if len(K) <= 1 else None)
            if t == split_depth and not state["timeout"]:
                state["done"] += 1
                if state["done"] % progress_every == 0:
                    logf.write("%.0f s: %d own tasks done; visited %s kept %s complete %d\n" % (
                        time.time() - t0, state["done"], visited, kept, len(survivors)))
                    logf.flush()
            if state["timeout"]:
                return

    cnt0 = {u: 0 for u in x0}
    dfs(root, [], [], [], cnt0, list(prob.group), units, None)
    out = {"name": prob.name, "tag": tag, "part": part, "nparts": nparts, "split_depth": split_depth,
           "timeout": state["timeout"], "tasks_total": state["tasks"], "tasks_mine": state["mine"],
           "tasks_done": state["done"], "visited": visited, "candidates": ncand, "kept": kept,
           "rejected_budget": rej_b, "rejected_psd": rej_p, "rejected_rank": rej_rank,
           "lookahead_candidates": looked[0], "stats": stats.c,
           "survivors": survivors, "seconds": time.time() - t0, "group_order": len(prob.group),
           "setwise": setwise, "engine": "eng4", "use_rank": use_rank, "width": width}
    json.dump(out, open("%s_%dof%d.json" % (tag, part, nparts), "w"))
    print(prob.name, tag, "part", part, "of", nparts, "split depth", split_depth, "timeout", state["timeout"],
          "seconds %.1f" % (time.time() - t0))
    print("tasks at split depth: total %d, mine %d, done %d" % (state["tasks"], state["mine"], state["done"]))
    print("nodes visited per level   :", visited)
    print("candidates (chosen unit)  :", ncand)
    print("  rejected by budgets     :", rej_b)
    print("  rejected by PSD (exact) :", rej_p)
    print("  kept                    :", kept)
    print("  of which dead by rank   :", rej_rank)
    print("PROBE2 nodes with some mutation n:", probe_app)
    print("PROBE2 nodes with an A1 violation:", probe_dead)
    print("lookahead candidates evaluated (float, all units):", looked[0])
    print("stats:", ", ".join("%s=%d" % (k, stats.c[k]) for k in sorted(stats.c)))
    print("complete configurations:", len(survivors))
    logf.close()
    if planf:
        planf.close()
    if certf:
        certf.close()
    return out
