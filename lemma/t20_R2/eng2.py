# T20 round 2: fast orbit-by-orbit engine.  Same model as eng.py (see its header), different tests:
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


def run(prob, part, nparts, tlim, split_depth, tag, progress_every=200, setwise=False, save_certs=0):
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

    passed = [0] * (norb + 1)
    tested = [0] * (norb + 1)
    survivors = []
    state = {"timeout": False, "tasks": 0, "mine": 0, "done": 0}
    logf = open("%s_%dof%d.log" % (tag, part, nparts), "w")

    def dfs(node, orbs, tg, degs, cnt, K, remaining):
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
        U0 = min(remaining)
        rem2 = dict(remaining)
        rem2[U0] -= 1
        if rem2[U0] == 0:
            del rem2[U0]
        n = node.n
        for V in sorted(rem2):
            if V == U0:
                continue
            rem3 = dict(rem2)
            rem3[V] -= 1
            if rem3[V] == 0:
                del rem3[V]
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
                cnt2 = dict(cnt)
                for u in N0:
                    cnt2[u] += 1
                    cnt2[sigb[u]] += 1
                if setwise:
                    K2 = [g for g in K if tuple(sorted(g[u] for u in N0)) == N0]
                else:
                    K2 = [g for g in K if all(g[u] == u for u in N0)]
                rowb = base_row(U0, V, N0, n)
                for choice in itertools.product(*allowed):
                    used = sum((pat & 1) + (pat >> 1) for pat in choice)
                    if used > tgt:
                        continue
                    if t == split_depth:
                        state["tasks"] += 1
                        if (state["tasks"] - 1) % nparts != part:
                            continue
                        state["mine"] += 1
                    tested[t] += 1
                    row = rowb.copy()
                    d2 = list(degs)
                    for q, pat in enumerate(choice):
                        if pat & 1:
                            row[nb + 2 * q] = 1
                        if pat & 2:
                            row[nb + 2 * q + 1] = 1
                        d2[q] += (pat & 1) + (pat >> 1)
                    node.prepare()
                    if node.budget_fail(row, 0):
                        stats.add("budget_L%d" % t)
                    else:
                        r = node.psd_fail(row, 0, stats)
                        if r is not None:
                            stats.add("psd_L%d" % t)
                            if certf is not None and ncert[0] < save_certs and r[1] is not None:
                                ncert[0] += 1
                                ch = node.child(row, 0)
                                certf.write(json.dumps({"block": r[0], "c": r[1], "q": r[2], "sig": ch.sig,
                                                        "A": ["".join(map(str, rr)) for rr in ch.A.tolist()]}) + "\n")
                        else:
                            passed[t] += 1
                            dfs(node.child(row, 0), orbs + [onew], tg + [tgt], d2 + [used], cnt2, K2, rem3)
                    if t == split_depth and not state["timeout"]:
                        state["done"] += 1
                        if state["done"] % progress_every == 0:
                            logf.write("%.0f s: %d own tasks done, passed %s, complete %d\n" % (
                                time.time() - t0, state["done"], passed, len(survivors)))
                            logf.flush()
                    if state["timeout"]:
                        return

    cnt0 = {u: 0 for u in x0}
    dfs(root, [], [], [], cnt0, list(prob.group), units)
    out = {"name": prob.name, "tag": tag, "part": part, "nparts": nparts, "split_depth": split_depth,
           "timeout": state["timeout"], "tasks_total": state["tasks"], "tasks_mine": state["mine"],
           "tasks_done": state["done"], "tested": tested, "passed": passed, "stats": stats.c,
           "survivors": survivors, "seconds": time.time() - t0, "group_order": len(prob.group),
           "setwise": setwise, "engine": "eng2"}
    json.dump(out, open("%s_%dof%d.json" % (tag, part, nparts), "w"))
    print(prob.name, tag, "part", part, "of", nparts, "split depth", split_depth, "timeout", state["timeout"],
          "seconds %.1f" % (time.time() - t0))
    print("tasks at split depth: total %d, mine %d, done %d" % (state["tasks"], state["mine"], state["done"]))
    print("tested per level:", tested)
    print("passed per level:", passed)
    print("stats:", ", ".join("%s=%d" % (k, stats.c[k]) for k in sorted(stats.c)))
    print("complete configurations:", len(survivors))
    logf.close()
    if certf:
        certf.close()
    return out
