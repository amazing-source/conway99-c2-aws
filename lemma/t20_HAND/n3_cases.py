"""T20, case I (k = 0), branch n_3 = 2: the bases and the model handed to the engine eng5z.py.

Vertex order of the engine: x_i = i, y_i = 10 + i (i = 0..9), p = 20, z = 21, z' = sigma z = 22, X_0' = 23..28 with
(o, s) -> 23 + 2 o + s (o = 0, 1, 2 the three orbits, s = 0, 1), then the orbits of X_2 placed by the engine.

A base is the determined set Y = S u {p} u {z, z'} u X_0' (29 vertices) of NOTES.md H1 / H7:
  type (U ; V) of z, case i / ii / iii (the normalised T = N(z) n X_0'), at most one inner orbit in X_0' (profile (4,2,1); none for
  profile (3,4,0)), and the 2^6 edge orbits between the three orbits of X_0'.
Tests on a base: budgets, the degree bounds and exact common-neighbour statements of H1, and M1[Y], M2[Y] positive semidefinite
(a rejection is an explicit integer vector of negative form, checked in Python integers).
Bases are then taken up to the relabellings Aut(B) x (z <-> z') x (permutations and flips of the orbits of X_0').

Model for the engine (class CaseIN3). All twelve orbits of X_2 are placed by the engine. Exact numbers (NOTES H0, H1):
  * p has 2 h_2 neighbours in X_2 (h_2 = 3 without inner orbit in X_0', 4 with one); they are the inner orbits of X_2;
  * z and z' have alpha neighbours in X_2 (alpha = 1 in case iii, 0 otherwise); a vertex of X_2 is never adjacent to both;
  * x in X_0' has a_0(x) + 6 - 2 a_3(x) neighbours in X_2 (a_0, a_3 read on the base);
  * a vertex s of X_2 with W = N(s) n X_0', a_3 = a_3(s) in {0, 1}, zz = [s inner]: a_0(s) = |W| + zz, a_2(s) = a_0(s) - 2 a_3,
    and a_1(s) = 10 - 2 a_2 - 3 a_3 >= 0. So s has exactly |W| - 2 a_3 neighbours in the OTHER orbits of X_2, |W| >= 2 a_3, and
    a_2(s) <= 5 (a_3 = 0) or <= 3 (a_3 = 1);
  * an inner s is adjacent to no inner vertex of X_0' and to at most one end of each word orbit of X_0';
    a word s is not adjacent to both ends of the inner orbit of X_0'.
An orbit is inner  <=>  p (vertex 20) is in its tuple N0 (convention of eng5z.py)."""
import itertools as it
import numpy as np

E = {"I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79", "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
     "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89", "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
     "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79", "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89"}
# types (U ; V) of a vertex of X_3 up to Aut(B) x (z <-> z'): output of x3_types.py
TYPES = {"I.0": ["034 179"], "I.1": ["034 178", "034 258", "034 278", "257 268", "257 368", "257 678", "258 345", "278 349", "368 457"],
         "I.2": ["034 189", "034 589", "345 389"], "I.3": ["034 156", "034 159", "159 168", "159 368"],
         "I.4": ["025 279", "027 035", "035 169", "035 279", "279 348"], "I.5": ["012 168", "012 579", "016 359"]}
P, Z, ZP, NB = 20, 21, 22, 29
X0V = list(range(23, 29))
TCASE = {"i": [(0, 0), (1, 0), (2, 0)], "ii": [(0, 0), (0, 1), (1, 0)], "iii": [(0, 0), (0, 1), (1, 0), (2, 0)]}
PAIRS = [(0, 1), (0, 2), (1, 2)]
SIG = [10 + i for i in range(10)] + list(range(10)) + [20, 22, 21, 24, 23, 26, 25, 28, 27]
J = np.ones((NB, NB), dtype=np.int64); I = np.eye(NB, dtype=np.int64)


def x0(o, s): return 23 + 2 * o + s


def bmat(name):
    B = np.zeros((10, 10), dtype=np.int64)
    for e in E[name].split(): a, b = int(e[0]), int(e[1]); B[a, b] = B[b, a] = 1
    return B


def neg_vector(M):
    """integer x with x^T M x < 0 (checked in Python integers), or None (kept: float decision)"""
    w, vec = np.linalg.eigh(M.astype(np.float64))
    if w[0] > -1e-7: return None
    v = vec[:, 0]; Ml = M.tolist()
    for scale in (4, 8, 16, 32, 64, 128, 512, 4096):
        x = [int(t) for t in np.rint(v * scale / np.abs(v).max()).tolist()]
        if sum(xa * sum(r * xb for r, xb in zip(row, x)) for row, xa in zip(Ml, x) if xa) < 0: return x
    raise RuntimeError("no integer certificate found (float eigenvalue %g)" % w[0])


def labelled_bases(name):
    """all labelled bases of the graph that pass the tests; list of dicts"""
    B = bmat(name); out = []; counts = {"labelled": 0, "after_budget_degree": 0, "after_psd": 0}
    for ty in TYPES[name]:
        U, V = [[int(ch) for ch in part] for part in ty.split()]
        eps = len(set(U) & set(V))
        base = np.zeros((NB, NB), dtype=np.int64)
        base[:10, 10:20] = B; base[10:20, :10] = B.T
        for i in U: base[Z, i] = base[i, Z] = 1; base[ZP, 10 + i] = base[10 + i, ZP] = 1
        for j in V: base[Z, 10 + j] = base[10 + j, Z] = 1; base[ZP, j] = base[j, ZP] = 1
        for case, T in TCASE.items():
            if case != "i" and eps: continue
            for inner in (None, 0, 1, 2):
                if inner == 0 and case != "i": continue
                for bits in range(64):
                    A = base.copy()
                    for (o, s) in T:
                        A[Z, x0(o, s)] = A[x0(o, s), Z] = 1; A[ZP, x0(o, 1 - s)] = A[x0(o, 1 - s), ZP] = 1
                    if inner is not None:
                        a, b = x0(inner, 0), x0(inner, 1)
                        A[a, b] = A[b, a] = 1; A[P, a] = A[a, P] = A[P, b] = A[b, P] = 1
                    for t, (o, o2) in enumerate(PAIRS):
                        if bits >> (2 * t) & 1:
                            for s in (0, 1): A[x0(o, s), x0(o2, s)] = A[x0(o2, s), x0(o, s)] = 1
                        if bits >> (2 * t + 1) & 1:
                            for s in (0, 1): A[x0(o, s), x0(o2, 1 - s)] = A[x0(o2, 1 - s), x0(o, s)] = 1
                    counts["labelled"] += 1
                    C = A @ A; cap = 2 - A; np.fill_diagonal(cap, 99)
                    if (C > cap).any(): continue
                    ok = True
                    for x in X0V:
                        a0 = int(A[x, 20] + A[x, 23:29].sum()); a3 = int(A[x, Z] + A[x, ZP])
                        if a0 > (5 if a3 == 2 else 4): ok = False
                    if case != "i" and C[x0(0, 0), x0(0, 1)] != 2: ok = False
                    if case == "i" and C[Z, ZP] != 2 * eps: ok = False
                    if not ok: continue
                    counts["after_budget_degree"] += 1
                    if neg_vector(9 * (3 * I - A) + J) is not None or neg_vector(11 * (4 * I + A) - 2 * J) is not None: continue
                    counts["after_psd"] += 1
                    out.append({"graph": name, "type": ty, "case": case, "inner": inner, "bits": bits, "A": A})
    return out, counts


def automorphisms(B):
    return [p for p in it.permutations(range(10)) if all(B[p[i], p[j]] == B[i, j] for i in range(10) for j in range(i))]


def relabellings(B):
    """the vertex permutations of the 29 base vertices that preserve the roles: Aut(B) on S+ and S- together, z <-> z',
    permutations and flips of the three orbits of X_0'"""
    out = []
    for pi in automorphisms(B):
        for sw in (0, 1):
            for q in it.permutations(range(3)):
                for fl in it.product((0, 1), repeat=3):
                    perm = list(range(NB))
                    for i in range(10): perm[i] = pi[i]; perm[10 + i] = 10 + pi[i]
                    if sw: perm[Z], perm[ZP] = ZP, Z
                    for o in range(3):
                        for s in (0, 1): perm[x0(o, s)] = x0(q[o], s ^ fl[o])
                    inv = [0] * NB
                    for u, v in enumerate(perm): inv[v] = u
                    out.append(np.array(inv))
    return out


def quotient(recs, B):
    """one representative per class under the relabellings; each record gets its class size"""
    rel = relabellings(B); classes = {}
    for r in recs:
        A = r["A"]; key = min(A[np.ix_(inv, inv)].tobytes() for inv in rel)
        if key in classes: classes[key]["class_size"] += 1
        else: r["class_size"] = 1; classes[key] = r
    return list(classes.values())


class CaseIN3:
    def __init__(self, rec):
        A = rec["A"]; self.AB = A.copy(); self.sig = list(SIG)
        self.name = "%s n3=2 type %s case %s inner %s bits %d" % (rec["graph"], rec["type"], rec["case"], rec["inner"], rec["bits"])
        inner = rec["inner"]; self.h2 = 3 if inner is None else 4; self.alpha = 1 if rec["case"] == "iii" else 0
        units = {}
        for i in range(10):
            for j in range(i + 1, 10):
                need = 2 - int((A[i] * A[j]).sum())
                assert need >= 0
                if need: units[(i, j)] = need
        assert sum(units.values()) == 24, sum(units.values())
        self.units = units
        tx = {x: int(A[x, 20] + A[x, 23:29].sum()) + 6 - 2 * int(A[x, Z] + A[x, ZP]) for x in X0V}
        self.x0 = [P, Z, ZP] + X0V
        self.x0_target = {P: 2 * self.h2, Z: self.alpha, ZP: self.alpha}
        self.x0_target.update(tx)
        self.group = []
        innerv = set() if inner is None else {x0(inner, 0), x0(inner, 1)}
        zopts = [()] + ([(Z,), (ZP,)] if self.alpha else [])
        self.opts0 = []; self.opts1 = []
        for za in zopts:
            a3 = len(za)
            for r in range(0, 7):
                for W in it.combinations(X0V, r):
                    if any(tx[x] == 0 for x in W) or r < 2 * a3: continue
                    Ws = set(W)
                    if innerv and innerv <= Ws: pass
                    else:
                        if r - 2 * a3 <= 5 - 2 * a3:                                  # word: a_2 = |W| - 2 a_3
                            self.opts0.append((tuple(sorted(za + W)), r - 2 * a3))
                    if not (Ws & innerv) and all(not ({x0(o, 0), x0(o, 1)} <= Ws) for o in range(3)):
                        if r + 1 - 2 * a3 <= 5 - 2 * a3:                              # inner: a_2 = |W| + 1 - 2 a_3
                            self.opts1.append((tuple(sorted((P,) + za + W)), r - 2 * a3))

    def options(self, U, V):
        return self.opts0 + (self.opts1 if not (set(U) & set(V)) else [])


if __name__ == "__main__":
    for name in E:
        recs, counts = labelled_bases(name)
        reps = quotient(recs, bmat(name))
        assert sum(r["class_size"] for r in reps) == len(recs)
        print("%s: %s -> %d classes of bases; by profile: (3,4,0) %d, (4,2,1) %d; by case: %s" % (
            name, counts, len(reps), sum(1 for r in reps if r["inner"] is None), sum(1 for r in reps if r["inner"] is not None),
            {c: sum(1 for r in reps if r["case"] == c) for c in TCASE}), flush=True)
