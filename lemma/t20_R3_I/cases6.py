# T20 round 3, case I (k = 0): the model given to eng6.py.  N(p) is in the base; n_3 = 0 or n_3 = 2.
#
# Base (completely known graph):  S (0..19), p (20), [z = 21, sigma z = 22 when n_3 = 2], then the seven pairs
# of N(p) in the order of the stage-1 record: pair t = vertices (off + 2t, off + 2t + 1), off = 21 or 23.
#   ("A", U, V): w ~ p, sigma w, x_U, y_V; sigma w ~ p, w, x_V, y_U          (N(p) n X_2)
#   ("W", i, k): w ~ p, sigma w, x_i, y_k; sigma w ~ p, w, x_k, y_i          (N(p) n X_1)
#   ("Z",)     : w ~ p, sigma w                                               (N(p) n X_0)
# n_3 = 2: z ~ x_U3, y_V3 and the two vertices off + zn[0], off + zn[1] of N(p);  sigma z: the images.
#
# What is enumerated by the engine: the orbits {s, sigma s} of X_2 outside N(p) (all words).  Such an s has
#   N(s) n S+ = x_U, N(s) n S- = y_V with U, V deficient pairs still to be realised ("units");
#   exactly two neighbours in N(p), in two different pairs (a word has exactly 2 common neighbours with p,
#   and they are not mates);
#   n_3 = 2: possibly z or sigma z as a neighbour, not both (a_2(z) <= 1);
#   edges to the other orbits of X_2 outside N(p): patterns chosen by the engine.
# Upper bounds used (hand part; "caps", never equalities):
#   n_3 = 0:  s: a_2(s) = a_0(s) <= 5;   A-vertex: at most 4 - h0 neighbours among the words of X_2;
#             W-vertex: at most 8 - h0;   Z-vertex: at most min(10, 12 - h0).
#   n_3 = 2:  s: a_2(s) + 2 a_3(s) = a_0(s) <= 4;   with a3 = number of neighbours in {z, sigma z}:
#             A-vertex: at most 3 - h0 - 2 a3;  W-vertex: at most 7 - h0 - 2 a3;
#             Z-vertex: at most min(11 - h0 - 2 a3, (20 - 3 a3) // 2);   z, sigma z: a_2 <= 1.
# options(U, V) returns every N0 (neighbours of s in the base outside S) that is not rejected by an EXACT budget
# count on the base plus the orbit of s (int64 arithmetic, function budget_rows), with its cap.
import itertools
import numpy as np
import eng
import r3lib


def budget_rows(A, W1, W2, sigarr, R):
    """EXACT (int64).  R: candidate rows (zz = 0) on the vertices of the graph A (sigma-invariant).  True where the
    graph A plus the orbit {s, sigma s} has a pair with more than 2 - [adjacent] common neighbours."""
    RS = R[:, sigarr]
    bad = ((R @ A + R) > 2).any(1)                 # s against an old vertex
    bad |= (R * RS).sum(1) > 2                     # s against sigma s
    bad |= ((R @ W1) * R).sum(1) > 0               # two old vertices of N(s) that already have 2 - [adjacent]
    T = R * RS
    bad |= ((T @ W2) * T).sum(1) > 0               # two old vertices of N(s) n N(sigma s)
    return bad


class CaseIN6(eng.Problem):
    caps_only = True
    options_budget_exact = True

    def __init__(self, name, rec, ztype=None):
        pairs = [tuple(tuple(x) if isinstance(x, list) else x for x in t) for t in rec["pairs"]]
        zn = rec.get("zn")
        self.name = "%s/N(p)=%s%s" % (name, pairs, ("/z=%s,zn=%s" % (ztype, zn)) if ztype else "")
        m = r3lib.load_B(name)
        units = r3lib.units_of(m)
        off = 23 if ztype else 21
        nb = off + 14
        A = r3lib.support(m, nb - 21)
        sig = r3lib.sigma_of(nb)

        def e(u, v):
            A[u, v] = A[v, u] = 1

        def use(X):
            units[X] -= 1
            assert units[X] >= 0
            if units[X] == 0:
                del units[X]
        if ztype:
            U3, V3 = ztype
            for i in U3:
                e(21, i); e(22, 10 + i)
            for i in V3:
                e(21, 10 + i); e(22, i)
            for T3 in (U3, V3):
                for pr in itertools.combinations(T3, 2):
                    use(pr)
            for a in zn:
                e(21, off + a); e(22, sig[off + a])
        assert len(pairs) == 7
        h0 = sum(1 for t in pairs if t[0] == "Z")
        Ap = set()
        kind = {}
        for t, tp in enumerate(pairs):
            w, sw = off + 2 * t, off + 2 * t + 1
            e(w, sw); e(w, 20); e(sw, 20)
            kind[w] = kind[sw] = tp[0]
            if tp[0] == "A":
                U, V = tp[1], tp[2]
                for i in U:
                    e(w, i); e(sw, 10 + i)
                for i in V:
                    e(w, 10 + i); e(sw, i)
                use(tuple(U)); use(tuple(V))
                Ap |= {w, sw}
            elif tp[0] == "W":
                e(w, tp[1]); e(w, 10 + tp[2]); e(sw, tp[2]); e(sw, 10 + tp[1])
        self.AB = A
        self.sig = sig
        self.off = off
        self.units = units
        self.NP = list(range(off, nb))
        self.x0 = ([21, 22] if ztype else []) + self.NP
        self.group = []
        self.Ap = Ap
        self.impossible = None          # exact hand reason why the base cannot occur
        caps = {}
        for w in self.NP:
            a3 = int(A[w, 21] + A[w, 22]) if ztype else 0
            if not ztype:
                caps[w] = {"A": 4 - h0, "W": 8 - h0, "Z": min(10, 12 - h0)}[kind[w]]
            else:
                caps[w] = {"A": 3 - h0 - 2 * a3, "W": 7 - h0 - 2 * a3,
                           "Z": min(11 - h0 - 2 * a3, (20 - 3 * a3) // 2)}[kind[w]]
            if caps[w] < 0:
                self.impossible = "cap < 0 at a vertex of N(p)"
        if ztype:
            for v in (21, 22):
                caps[v] = 1 - sum(int(A[v, w]) for w in Ap)
                if caps[v] < 0:
                    self.impossible = "a_2(z) > 1"
        self.x0_target = caps
        self.ztype = ztype
        self.smax = 4 if ztype else 5
        self._opt = None

    def _build_options(self):
        A = self.AB
        nb = A.shape[0]
        sigarr = np.array(self.sig)
        C = A @ A
        CA = C + A
        W1 = (CA >= 2).astype(np.int64); np.fill_diagonal(W1, 0)
        W2 = (CA >= 1).astype(np.int64); np.fill_diagonal(W2, 0)
        ul = sorted(self.units)
        uv = [(U, V) for U in ul for V in ul if U != V]
        self.n_rows = 0

        def srow(U, V):
            r = np.zeros(nb, dtype=np.int64)
            for i in U:
                r[i] = 1
            for i in V:
                r[10 + i] = 1
            return r

        def bad_of(rows):
            if not rows:
                return np.zeros(0, dtype=bool)
            self.n_rows += len(rows)
            return budget_rows(A, W1, W2, sigarr, np.array(rows, dtype=np.int64))
        # level a: the neighbours in S alone (a spanning subgraph: budgets are monotone)
        base_rows = [srow(U, V) for (U, V) in uv]
        bad = bad_of(base_rows)
        good = [(uv[a], base_rows[a]) for a in range(len(uv)) if not bad[a]]
        # level b: one more neighbour
        rows, keys = [], []
        for (U, V), r in good:
            for v in self.x0:
                r2 = r.copy(); r2[v] = 1
                rows.append(r2); keys.append(((U, V), v))
        bad = bad_of(rows)
        ok1 = {}
        for a, (k, v) in enumerate(keys):
            if not bad[a]:
                ok1.setdefault(k, []).append(v)
        # level c: two neighbours in N(p) (different pairs) and at most one of z, sigma z
        rows, keys = [], []
        off = self.off
        for (U, V), r in good:
            vs = ok1.get((U, V), [])
            nps = [v for v in vs if v >= off]
            zs = [()] + [(v,) for v in vs if v < off]
            for a in range(len(nps)):
                for b in range(a + 1, len(nps)):
                    w1, w2 = nps[a], nps[b]
                    if (w1 - off) // 2 == (w2 - off) // 2:
                        continue
                    for zc in zs:
                        N0 = zc + (w1, w2)
                        tgt = self.smax - 2 * len(zc) - sum(1 for w in (w1, w2) if w in self.Ap)
                        if tgt < 0:
                            continue
                        r2 = r.copy()
                        for v in N0:
                            r2[v] = 1
                        rows.append(r2); keys.append(((U, V), N0, tgt))
        bad = bad_of(rows)
        opt = {}
        for a, (k, N0, tgt) in enumerate(keys):
            if not bad[a]:
                opt.setdefault(k, []).append((N0, tgt))
        self._opt = opt

    def options(self, U, V):
        if self._opt is None:
            self._build_options()
        return self._opt.get((U, V), [])
