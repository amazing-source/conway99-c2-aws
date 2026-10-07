# T20 round 2: problem definitions for eng.py (self-contained: reads the structure files itself)
import json, os, itertools
import numpy as np
import eng

HERE = os.path.dirname(os.path.abspath(__file__))


def structure(name):
    d = {}
    for fn in ("structures_I.json", "structures_III_IIb_IIa.json"):
        d.update(json.load(open(os.path.join(HERE, fn))))
    case, idx = name.split(".")
    rec = d[case][int(idx)]
    return rec["m"], rec["H"]


def support_graph(m, H, extra=0):
    """S u {p} (x_i = i, y_i = 10+i, p = 20) plus `extra` isolated vertices"""
    A = np.zeros((21 + extra, 21 + extra), dtype=np.int64)

    def e(u, v):
        A[u, v] = A[v, u] = 1
    for i in range(10):
        for j in range(i + 1, 10):
            if m[i][j] & 1:
                e(i, 10 + j); e(j, 10 + i)
            if m[i][j] & 2:
                e(i, j); e(10 + i, 10 + j)
    for i in H:
        e(i, 10 + i); e(20, i); e(20, 10 + i)
    return A


def deficient_units(A):
    units = {}
    for i in range(10):
        for j in range(i + 1, 10):
            c = int((A[i, :21] * A[j, :21]).sum())
            need = (1 if A[i, j] else 2) - c
            assert need >= 0
            if need:
                units[(i, j)] = need
    return units


def sigma_base(nb):
    s = list(range(nb))
    for i in range(10):
        s[i], s[10 + i] = 10 + i, i
    for v in range(21, nb, 2):
        s[v], s[v + 1] = v + 1, v
    return s


class CaseIII(eng.Problem):
    """k = 4.  Base = S u N[p] (27 vertices): X_0 = the three inactive pairs (21,22), (23,24), (25,26)."""

    def __init__(self, name):
        self.name = name
        m, H = structure(name)
        assert len(H) == 4
        self.H = set(H)
        A = support_graph(m, H, 6)
        for a in (21, 23, 25):
            A[a, a + 1] = A[a + 1, a] = 1
            A[20, a] = A[a, 20] = 1
            A[20, a + 1] = A[a + 1, 20] = 1
        self.AB = A
        self.sig = sigma_base(27)
        self.x0 = [21, 22, 23, 24, 25, 26]
        self.units = deficient_units(A)
        assert sum(self.units.values()) == 24
        self.x0_target = {u: 4 for u in self.x0}
        self.group = eng.base_group(A, self.sig, self.x0)
        assert len(self.group) == 48

    def options(self, U, V):
        r = sum(1 for i in U if i in self.H) + sum(1 for i in V if i in self.H)
        k = 2 - r
        if k < 0:
            return []
        out = []
        for N0 in itertools.combinations(self.x0, k):
            if k == 2 and (N0[0] - 21) // 2 == (N0[1] - 21) // 2:
                continue            # never adjacent to both vertices of a pair of N(p)
            out.append((N0, k))
        return out


class CaseIIa(eng.Problem):
    """k = 2, e = 1, profile (0,5,0) at p (the only one, by hand).  Base = S u {p} u X_0, X_0 = two word orbits
    (21,22), (23,24); variant ex in {0, 1, 2}: no edge / z0~z1 (and mates) / z0~z1 and z0~sigma z1 (and mates)."""

    def __init__(self, name, ex):
        self.name = "%s/X0-%d" % (name, ex)
        m, H = structure(name)
        assert len(H) == 2
        self.H = set(H)
        A = support_graph(m, H, 4)
        if ex >= 1:
            A[21, 23] = A[23, 21] = 1; A[22, 24] = A[24, 22] = 1
        if ex == 2:
            A[21, 24] = A[24, 21] = 1; A[22, 23] = A[23, 22] = 1
        self.AB = A
        self.sig = sigma_base(25)
        self.x0 = [21, 22, 23, 24]
        self.units = deficient_units(A)
        assert sum(self.units.values()) == 20
        self.x0_target = {u: 6 + ex for u in self.x0}
        self.group = eng.base_group(A, self.sig, self.x0)
        assert len(self.group) == (8, 4, 8)[ex], len(self.group)
        self.plus = set()
        for i in range(10):
            for j in range(10):
                if i != j and m[i][j] & 2:
                    self.plus.add(i)
        assert self.plus == {2, 3}

    def options(self, U, V):
        q = sum(1 for i in U if i in self.plus) + sum(1 for i in V if i in self.plus)
        out = []
        for s in range(q, 5):
            for N0 in itertools.combinations(self.x0, s):
                out.append((N0, s - q))
        return out


class CaseIIaW(eng.Problem):
    """k = 2, e = 1 with N(p) and X_0 in the base.  Base = S u N[p] u X_0 (35 vertices):
    W = five mate pairs (21,22), ..., (29,30): pair t has type (i_t ; k_t): 21+2t ~ p, 22+2t, x_i, y_k;
    X_0 = two word orbits (31,32), (33,34), each vertex with exactly two neighbours in W; pat = 1: 31 ~ 33.
    Exact numbers (report, case II): a vertex s of X_2 minus p has 2 - r(s) neighbours in W (never two mates),
    |N(s) n X_0| - q(s) neighbours in X_2 minus p; a vertex of X_0 has 6 + a_0 neighbours in X_2; a vertex w of W has
    a_0(w) + 2 - q(w) neighbours in X_2 minus p."""

    def __init__(self, name, wset, alpha, beta, pat):
        self.name = "%s/W%s/X0%s%s/%d" % (name, wset, alpha, beta, pat)
        m, H = structure(name)
        self.H = set(H)
        A = support_graph(m, H, 14)

        def e(u, v):
            A[u, v] = A[v, u] = 1
        for t, (i, k) in enumerate(wset):
            w, sw = 21 + 2 * t, 22 + 2 * t
            e(w, sw); e(w, 20); e(sw, 20); e(w, i); e(w, 10 + k); e(sw, k); e(sw, 10 + i)
        sig = sigma_base(35)
        for (z, nb_) in ((31, alpha), (33, beta)):
            for u in nb_:
                e(z, u); e(sig[z], sig[u])
        if pat:
            e(31, 33); e(32, 34)
        self.AB = A
        self.sig = sig
        self.W = list(range(21, 31))
        self.X0 = [31, 32, 33, 34]
        self.x0 = self.W + self.X0
        self.units = deficient_units(A)
        assert sum(self.units.values()) == 20
        plus = {2, 3}
        self.plus = plus
        tgt = {}
        for z in self.X0:
            tgt[z] = 6 + pat
        for w in self.W:
            a0 = int(sum(A[w, z] for z in self.X0))
            q = int(sum(A[w, v] for v in (2, 3, 12, 13)))
            tgt[w] = a0 + 2 - q
        self.x0_target = tgt
        self.group = []
        self._wsets = {0: [()], 1: [(w,) for w in self.W],
                       2: [(a, b) for a in self.W for b in self.W if a < b and (a - 21) // 2 != (b - 21) // 2]}
        self._xsets = [c for s in range(0, 5) for c in itertools.combinations(self.X0, s)]

    def options(self, U, V):
        r = sum(1 for i in U if i in self.H) + sum(1 for i in V if i in self.H)
        if r > 2:
            return []
        q = sum(1 for i in U if i in self.plus) + sum(1 for i in V if i in self.plus)
        out = []
        for NW in self._wsets[2 - r]:
            for NX in self._xsets:
                if len(NX) < q:
                    continue
                out.append((tuple(sorted(NW + NX)), len(NX) - q))
        return out


class CaseIIaN(eng.Problem):
    """k = 2, e = 1 with N(p) in the base and X_0 NOT in the vertex set.  Base = S u N[p] (31 vertices), W as in
    CaseIIaW.  A vertex s of X_2 minus p: exactly 2 - r(s) neighbours in W (never two mates);
    number of neighbours in X_2 minus p = a_0(s) - q(s) <= 3 - q(s)   (only an upper bound: caps_only);
    a vertex w of W has a_0(w) + 2 - q(w) <= 4 - q(w) neighbours in X_2 minus p (upper bound).
    With caps_only the engine keeps every configuration that reaches the last level (no equality is required)."""
    caps_only = True

    def __init__(self, name, wset):
        self.name = "%s/N(p)=%s" % (name, wset)
        m, H = structure(name)
        self.H = set(H)
        A = support_graph(m, H, 10)

        def e(u, v):
            A[u, v] = A[v, u] = 1
        for t, (i, k) in enumerate(wset):
            w, sw = 21 + 2 * t, 22 + 2 * t
            e(w, sw); e(w, 20); e(sw, 20); e(w, i); e(w, 10 + k); e(sw, k); e(sw, 10 + i)
        self.AB = A
        self.sig = sigma_base(31)
        self.W = list(range(21, 31))
        self.x0 = self.W
        self.units = deficient_units(A)
        assert sum(self.units.values()) == 20
        self.plus = {2, 3}
        self.x0_target = {w: 4 - int(sum(A[w, v] for v in (2, 3, 12, 13))) for w in self.W}
        self.group = []
        self._wsets = {0: [()], 1: [(w,) for w in self.W],
                       2: [(a, b) for a in self.W for b in self.W if a < b and (a - 21) // 2 != (b - 21) // 2]}

    def options(self, U, V):
        r = sum(1 for i in U if i in self.H) + sum(1 for i in V if i in self.H)
        if r > 2:
            return []
        q = sum(1 for i in U if i in self.plus) + sum(1 for i in V if i in self.plus)
        if q > 3:
            return []
        return [(NW, 3 - q) for NW in self._wsets[2 - r]]


class CaseIN(eng.Problem):
    """k = 0 (case I), n_3 = 0, with N(p) in the base (exploration for round 3).  Base = S u N[p] (35 vertices):
    seven pairs (21,22), ..., (33,34) of N(p); pair t is ("2", U, V): 21+2t ~ p, mate, x_U, y_V (an X_2 pair);
    ("1", i, k): 21+2t ~ p, mate, x_i, y_k (an X_1 pair); ("0",): an X_0 pair.
    A vertex s of X_2 outside N(p): exactly 2 neighbours in N(p), in different pairs; a_2(s) = a_0(s) <= 5, so at
    most 5 - |N(s) n A_p| neighbours among the X_2 vertices outside N(p)  (upper bounds only: caps_only)."""
    caps_only = True

    def __init__(self, name, pairs):
        self.name = "%s/N(p)=%s" % (name, pairs)
        m, H = structure(name)
        assert not H
        A = support_graph(m, H, 14)

        def e(u, v):
            A[u, v] = A[v, u] = 1
        units = deficient_units(A)
        h0 = sum(1 for t in pairs if t[0] == "0")
        self.Ap = []
        caps = {}
        for t, tp in enumerate(pairs):
            w, sw = 21 + 2 * t, 22 + 2 * t
            e(w, sw); e(w, 20); e(sw, 20)
            if tp[0] == "2":
                U, V = tp[1], tp[2]
                for i in U:
                    e(w, i); e(sw, 10 + i)
                for i in V:
                    e(w, 10 + i); e(sw, i)
                for X in (tuple(U), tuple(V)):
                    units[X] -= 1
                    if units[X] == 0:
                        del units[X]
                self.Ap += [w, sw]
                caps[w] = caps[sw] = 4 - h0
            elif tp[0] == "1":
                e(w, tp[1]); e(w, 10 + tp[2]); e(sw, tp[2]); e(sw, 10 + tp[1])
                caps[w] = caps[sw] = 8 - h0
            else:
                caps[w] = caps[sw] = 12 - h0
        self.AB = A
        self.sig = sigma_base(35)
        self.x0 = list(range(21, 35))
        self.units = units
        self.x0_target = caps
        self.group = []
        self._np = [(a, b) for a in self.x0 for b in self.x0 if a < b and (a - 21) // 2 != (b - 21) // 2]
        self._aps = set(self.Ap)

    def options(self, U, V):
        return [(NP, 5 - sum(1 for v in NP if v in self._aps)) for NP in self._np]
