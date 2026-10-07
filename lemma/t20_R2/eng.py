# T20 round 2: general orbit-by-orbit engine ("stage B": X_2 added to a known base).  Self-contained (does not
# import r2c.py).  Exact rejections only: a common-neighbour count, or an integer vector x with x^T M x < 0
# evaluated in Python integers (M = M1 = 9(3I-A)+J or M2 = 11(4I+A)-2J on the current, completely known, vertex set).
#
# Model of a problem (class Problem):
#   base graph AB on vertices 0..nb-1 with involution sig (fixed points allowed), containing S u {p} u X_0;
#   x_i = i, y_i = 10+i, p = 20;  X_0 vertices (other than p) = self.x0;
#   units: deficient pairs {i,j} of S+ with multiplicities; every unit is N(z) n S+ of exactly one z of X_2 \ {p};
#   an X_2 orbit is z = (U ; V ; N0), sigma z = (V ; U ; sigma N0): z ~ x_i (i in U), y_i (i in V), u (u in N0);
#   options(U, V) lists the admissible (N0, target), target = exact number of neighbours of z in X_2 \ {p};
#   x0_target[u] = exact number of neighbours of u in X_2 \ {p};
#   group = permutations of the base vertices that fix S u {p} pointwise, commute with sig and preserve AB.
# Search: at each level the orbit of a vertex z whose U is the smallest unit not yet covered is added, with
# its V, its N0 (only the lexicographically smallest image under the pointwise stabiliser of the X_0 vertices used
# so far), and its edges to the earlier orbits (pattern 0: none, 1: z~z', 2: z~sigma z', 3: both).
import json, os, sys, time, itertools
import numpy as np

TOLG = 1e-9
TOLE = 1e-7


class Counter:
    def __init__(self):
        self.c = {}

    def add(self, k, n=1):
        self.c[k] = self.c.get(k, 0) + n


def qf_python(M, x):
    """x^T M x with Python integers"""
    xs = [int(t) for t in x]
    nz = [a for a in range(len(xs)) if xs[a]]
    tot = 0
    for a in nz:
        row = M[a]
        s = 0
        for b in nz:
            s += int(row[b]) * xs[b]
        tot += xs[a] * s
    return tot


def int_cert(M, P, vec):
    """vec: approximate eigenvector in block coordinates; P: integer matrix n x k (block basis).  Returns (x, q)
    with x = P c integer, q = x^T M x < 0 exact, or None."""
    mx = float(np.max(np.abs(vec)))
    if mx == 0:
        return None
    for sc in (2, 3, 6, 12, 30, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12):
        c = np.rint(vec * (sc / mx))
        if not c.any():
            continue
        x = [int(t) for t in (P @ c.astype(np.int64)).tolist()] if sc <= 10 ** 12 else None
        q = qf_python(M, x)
        if q < 0:
            return x, q
    return None


def exact_psd_fraction(Q):
    from fractions import Fraction
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


class Tester:
    """sigma-block semidefiniteness tests on a sigma-invariant vertex set"""

    def __init__(self, stats, cert_file=None, cert_cap=0):
        self.stats = stats
        self.cert_file = cert_file
        self.cert_cap = cert_cap
        self.ncert = 0

    def blocks(self, A, sig):
        n = A.shape[0]
        reps = [v for v in range(n) if sig[v] > v]
        fixed = [v for v in range(n) if sig[v] == v]
        k = len(reps)
        D = np.zeros((n, k), dtype=np.int64)
        P = np.zeros((n, k + len(fixed)), dtype=np.int64)
        for j, v in enumerate(fixed):
            P[v, j] = 1
        for j, v in enumerate(reps):
            D[v, j] = 1
            D[sig[v], j] = -1
            P[v, len(fixed) + j] = 1
            P[sig[v], len(fixed) + j] = 1
        return D, P

    def reject(self, A, sig, tag=""):
        """None (kept, float decision) or (matrix name, x, q): x^T M x = q < 0 in Python integers"""
        n = A.shape[0]
        I = np.eye(n, dtype=np.int64)
        M1 = 9 * (3 * I - A) + 1
        M2 = 11 * (4 * I + A) - 2
        D, P = self.blocks(A, sig)
        # odd part: D^T M1 D = 18 G, D^T M2 D = 22 (7I - G),  G = 3I - A[R,R] + A[R,sigma R]
        G2 = D.T @ (3 * I - A) @ D            # = 2 G
        w, v = np.linalg.eigh(G2.astype(np.float64))
        res = None
        if w[0] < -2 * TOLG:
            res = self._cert("M1", M1, D, v[:, 0])
        if res is None and w[-1] > 14 + 2 * TOLG:
            res = self._cert("M2", M2, D, v[:, -1])
        if res is None:
            E1 = P.T @ M1 @ P
            w, v = np.linalg.eigh(E1.astype(np.float64))
            if w[0] < -TOLE:
                res = self._cert("M1", M1, P, v[:, 0])
        if res is None:
            E2 = P.T @ M2 @ P
            w, v = np.linalg.eigh(E2.astype(np.float64))
            if w[0] < -TOLE:
                res = self._cert("M2", M2, P, v[:, 0])
        if res is not None and self.cert_file is not None and self.ncert < self.cert_cap:
            self.ncert += 1
            self.cert_file.write(json.dumps({"tag": tag, "M": res[0], "A": ["".join(map(str, r)) for r in A.tolist()],
                                             "x": res[1], "q": res[2]}) + "\n")
        return res

    def _cert(self, name, M, P, vec):
        c = int_cert(M, P, vec)
        if c is None:
            # float says negative but no integer certificate found: decide exactly on the block
            B = (P.T @ M @ P).tolist()
            if exact_psd_fraction(B):
                self.stats.add("float_negative_but_exactly_psd")
                return None
            self.stats.add("exact_negative_without_certificate")
            return (name, None, None)
        self.stats.add("psd_reject_" + name)
        return (name, c[0], c[1])


def budgets_fail(A):
    C = A @ A
    V = C + A > 2
    np.fill_diagonal(V, False)
    return bool(V.any())


class Problem:
    """filled by the case scripts"""
    name = ""
    AB = None
    sig = None
    x0 = ()
    group = ()
    units = None
    x0_target = None

    def options(self, U, V):
        raise NotImplementedError


def base_group(AB, sig, x0):
    """all permutations of the vertices x0 (others fixed) commuting with sig and preserving AB"""
    nb = AB.shape[0]
    x0 = list(x0)
    out = []
    for perm in itertools.permutations(x0):
        g = list(range(nb))
        for a, b in zip(x0, perm):
            g[a] = b
        if any(g[sig[v]] != sig[g[v]] for v in x0):
            continue
        ok = True
        for a in x0:
            ga = g[a]
            for b in range(nb):
                if AB[a, b] != AB[ga, g[b]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append(tuple(g))
    return out


def run(prob, part, nparts, tlim, split_depth, tag, progress_every=200, cert_cap=0, setwise=False):
    t0 = time.time()
    stats = Counter()
    cf = open("%s_certs_%dof%d.jsonl" % (tag, part, nparts), "w") if cert_cap else None
    tester = Tester(stats, cf, cert_cap)
    AB = prob.AB
    nb = AB.shape[0]
    sigb = list(prob.sig)
    assert not budgets_fail(AB)
    assert tester.reject(AB, sigb) is None, "base graph rejected"
    units = dict(prob.units)
    norb = sum(units.values()) // 2
    x0 = list(prob.x0)
    x0t = dict(prob.x0_target)

    def add_orbit(A, U, V, N0):
        n = A.shape[0]
        B = np.zeros((n + 2, n + 2), dtype=np.int64)
        B[:n, :n] = A
        z, sz = n, n + 1
        for i in U:
            B[z, i] = B[i, z] = 1
            B[sz, 10 + i] = B[10 + i, sz] = 1
        for i in V:
            B[z, 10 + i] = B[10 + i, z] = 1
            B[sz, i] = B[i, sz] = 1
        for u in N0:
            B[z, u] = B[u, z] = 1
            B[sz, sigb[u]] = B[sigb[u], sz] = 1
        return B

    def sig_of(n):
        return sigb + [v + 1 if (v - nb) % 2 == 0 else v - 1 for v in range(nb, n)]

    single = {}

    def single_ok(U, V, N0):
        key = (U, V, N0)
        r = single.get(key)
        if r is None:
            B = add_orbit(AB, U, V, N0)
            if budgets_fail(B):
                stats.add("single_budget"); r = False
            elif tester.reject(B, sig_of(nb + 2), "single") is not None:
                stats.add("single_psd"); r = False
            else:
                r = True
            single[key] = r
        return r

    pairc = {}

    def pair_ok(o1, o2, pat):
        key = (o1, o2, pat)
        r = pairc.get(key)
        if r is None:
            B = add_orbit(add_orbit(AB, *o1), *o2)
            z1, s1, z2, s2 = nb, nb + 1, nb + 2, nb + 3
            if pat & 1:
                B[z1, z2] = B[z2, z1] = 1; B[s1, s2] = B[s2, s1] = 1
            if pat & 2:
                B[z1, s2] = B[s2, z1] = 1; B[s1, z2] = B[z2, s1] = 1
            if budgets_fail(B):
                stats.add("pair_budget"); r = False
            elif tester.reject(B, sig_of(nb + 4), "pair") is not None:
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

    def dfs(A, orbs, tg, degs, cnt, K, remaining):
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
                              "A": ["".join(map(str, r)) for r in A.tolist()]})
            return
        U0 = min(remaining)
        rem2 = dict(remaining)
        rem2[U0] -= 1
        if rem2[U0] == 0:
            del rem2[U0]
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
                # symmetry: N0 must be the smallest image under K
                if K:
                    smallest = True
                    for g in K:
                        img = tuple(sorted(g[u] for u in N0))
                        if img < N0:
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
                    B = add_orbit(A, U0, V, N0)
                    n = B.shape[0]
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
                        stats.add("budget_L%d" % t)
                    elif tester.reject(B, sig_of(n), "L%d" % t) is not None:
                        stats.add("psd_L%d" % t)
                    else:
                        passed[t] += 1
                        dfs(B, orbs + [onew], tg + [tgt], d2 + [used], cnt2, K2, rem3)
                    if t == split_depth and not state["timeout"]:
                        state["done"] += 1
                        if state["done"] % progress_every == 0:
                            logf.write("%.0f s: %d own tasks done, passed %s, complete %d\n" % (
                                time.time() - t0, state["done"], passed, len(survivors)))
                            logf.flush()
                    if state["timeout"]:
                        return

    cnt0 = {u: 0 for u in x0}
    dfs(AB, [], [], [], cnt0, list(prob.group), units)
    out = {"name": prob.name, "tag": tag, "part": part, "nparts": nparts, "split_depth": split_depth,
           "timeout": state["timeout"], "tasks_total": state["tasks"], "tasks_mine": state["mine"],
           "tasks_done": state["done"], "tested": tested, "passed": passed, "stats": stats.c,
           "survivors": survivors, "seconds": time.time() - t0, "group_order": len(prob.group),
           "setwise": setwise}
    json.dump(out, open("%s_%dof%d.json" % (tag, part, nparts), "w"))
    print(prob.name, tag, "part", part, "of", nparts, "split depth", split_depth, "timeout", state["timeout"],
          "seconds %.1f" % (time.time() - t0))
    print("tasks at split depth: total %d, mine %d, done %d" % (state["tasks"], state["mine"], state["done"]))
    print("tested per level:", tested)
    print("passed per level:", passed)
    print("stats:", ", ".join("%s=%d" % (k, stats.c[k]) for k in sorted(stats.c)))
    print("complete configurations:", len(survivors))
    if cf:
        cf.close()
    logf.close()
    return out
