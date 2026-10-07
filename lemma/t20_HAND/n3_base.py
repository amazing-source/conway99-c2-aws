"""T20, case I (k = 0), sub-case n_3 = 2: the determined set Y = S u {z, sigma z} u X_0  (29 vertices).

Written from lemma/T20_WORK.md and my hand notes (NOTES.md, H1-H3); shares no code with the project's engines.
Single process, exact rejections only, a few minutes at most, < 1 GB.

Why the induced graph on Y is determined by the data enumerated here (n_3 = 2):
  X_3 = {z, z' = sigma z}, z a word, z !~ z', type (U ; V).   X_0 = {p} u X_0', X_0' = 3 sigma-orbits {(o,0), (o,1)}, o = 0, 1, 2.
  No vertex of X_0 has a neighbour in S; p !~ z; T = N(z) n X_0 lies in X_0', |T| = 3 or 4, and (H1) up to relabelling
     case i  : T = {(0,0), (1,0), (2,0)}            (T n sigma T empty)
     case ii : T = {(0,0), (0,1), (1,0)}            (orbit 0 = N(z) n N(z'), a word orbit)
     case iii: T = {(0,0), (0,1), (1,0), (2,0)}     (same)
  An orbit o is "inner" (its two vertices adjacent to each other and to p) or a "word" orbit (not adjacent to each other nor to p).
  At most one inner orbit (h_0 <= 1 for the two open profiles); the common orbit of cases ii, iii is a word orbit; z is never adjacent
  to both ends of an inner pair (true in the three cases).
  Between two different orbits o < o' there are two possible edge orbits: "par" {(o,0)-(o',0), (o,1)-(o',1)} and
  "cross" {(o,0)-(o',1), (o,1)-(o',0)}: 2^6 choices.
Relabellings that keep T: any permutation of the orbits that preserves the pattern of T; they are NOT quotiented out here
(the count below is of labelled configurations), only the types (U ; V) are taken up to Aut(B) x (z <-> z').

Tests (necessary conditions in a real graph):
  (B) budget: two vertices of Y have at most 2 - [adjacent] common neighbours inside Y;
  (D) degrees: for x in X_0', a_0(x) <= 4 if a_3(x) <= 1, <= 5 if a_3(x) = 2   (a_1 = 8 - 2 a_0 + a_3 >= 0);
      in cases ii, iii the common orbit {u, u'} has N(u) n N(u') = {z, z'}: no third common neighbour in Y;
      in case i with U n V empty, N(z) n N(z') is an X_1 orbit, so z, z' have NO common neighbour in Y; with |U n V| = 1 it is
      {x_i, y_i}; cases ii, iii need U n V empty;
  (P) M1 = 9(3I - A) + J and M2 = 11(4I + A) - 2J restricted to Y are positive semidefinite. Rejection only with an explicit
      integer vector x with x^T M x < 0 (found from a float eigenvector, checked in Python integers); "kept" may be a float decision.
Output: per graph and type, the number of labelled configurations kept after (B)+(D) and after (P)."""
import itertools as it, sys, time, json
import numpy as np
E = {"I.0": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79", "I.1": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78",
     "I.2": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89", "I.3": "01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79",
     "I.4": "01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79", "I.5": "01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89"}
TYPES = {"I.0": ["034 179"], "I.1": ["034 178", "034 258", "034 278", "257 268", "257 368", "257 678", "258 345", "278 349", "368 457"],
         "I.2": ["034 189", "034 589", "345 389"], "I.3": ["034 156", "034 159", "159 168", "159 368"],
         "I.4": ["025 279", "027 035", "035 169", "035 279", "279 348"], "I.5": ["012 168", "012 579", "016 359"]}
Z, ZP, P = 20, 21, 22
X0 = lambda o, s: 23 + 2 * o + s
TCASE = {"i": [(0, 0), (1, 0), (2, 0)], "ii": [(0, 0), (0, 1), (1, 0)], "iii": [(0, 0), (0, 1), (1, 0), (2, 0)]}
PAIRS = [(0, 1), (0, 2), (1, 2)]
J29 = np.ones((29, 29), dtype=np.int64); I29 = np.eye(29, dtype=np.int64)


def neg_vector(Mi):
    """integer x with x^T M x < 0, or None (then M is kept: float decision)"""
    w, vec = np.linalg.eigh(Mi.astype(np.float64))
    if w[0] > -1e-7: return None
    v = vec[:, 0]
    for scale in (4, 8, 16, 32, 64, 128, 512, 4096):
        x = np.rint(v * scale / np.abs(v).max()).astype(np.int64)
        if int(x @ Mi @ x) < 0: return x
    raise RuntimeError("no integer certificate found for a matrix with float eigenvalue %g" % w[0])


def run(name):
    B = np.zeros((10, 10), dtype=np.int64)
    for e in E[name].split(): a, b = int(e[0]), int(e[1]); B[a, b] = B[b, a] = 1
    tot = {"labelled": 0, "after_BD": 0, "after_P": 0}; lines = []
    for ty in TYPES[name]:
        U, V = [[int(ch) for ch in part] for part in ty.split()]
        eps = len(set(U) & set(V))
        base = np.zeros((29, 29), dtype=np.int64)
        base[:10, 10:20] = B; base[10:20, :10] = B.T
        for i in U: base[Z, i] = base[i, Z] = 1; base[ZP, 10 + i] = base[10 + i, ZP] = 1
        for j in V: base[Z, 10 + j] = base[10 + j, Z] = 1; base[ZP, j] = base[j, ZP] = 1
        for case, T in TCASE.items():
            if case != "i" and eps: continue                       # cases ii, iii need U n V empty
            nlab = nbd = nps = 0; kept = []
            for inner in (None, 0, 1, 2):
                if inner == 0 and case != "i": continue             # the common orbit is a word orbit
                for bits in range(64):
                    A = base.copy()
                    for (o, s) in T:
                        A[Z, X0(o, s)] = A[X0(o, s), Z] = 1; A[ZP, X0(o, 1 - s)] = A[X0(o, 1 - s), ZP] = 1
                    if inner is not None:
                        a, b = X0(inner, 0), X0(inner, 1)
                        A[a, b] = A[b, a] = 1; A[P, a] = A[a, P] = A[P, b] = A[b, P] = 1
                    for t, (o, o2) in enumerate(PAIRS):
                        if bits >> (2 * t) & 1:                     # par
                            for s in (0, 1): A[X0(o, s), X0(o2, s)] = A[X0(o2, s), X0(o, s)] = 1
                        if bits >> (2 * t + 1) & 1:                 # cross
                            for s in (0, 1): A[X0(o, s), X0(o2, 1 - s)] = A[X0(o2, 1 - s), X0(o, s)] = 1
                    nlab += 1
                    C = A @ A
                    cap = 2 - A; np.fill_diagonal(cap, 99)
                    if (C > cap).any(): continue                    # (B)
                    ok = True
                    for o in range(3):                              # (D)
                        for s in (0, 1):
                            x = X0(o, s); a0 = int(A[x, 22:29].sum()); a3 = int(A[x, Z] + A[x, ZP])
                            if a0 > (5 if a3 == 2 else 4): ok = False
                    if case != "i" and C[X0(0, 0), X0(0, 1)] != 2: ok = False
                    if case == "i" and C[Z, ZP] != 2 * eps: ok = False
                    if not ok: continue
                    nbd += 1
                    M1 = 9 * (3 * I29 - A) + J29; M2 = 11 * (4 * I29 + A) - 2 * J29
                    if neg_vector(M1) is not None or neg_vector(M2) is not None: continue
                    nps += 1; kept.append({"case": case, "inner": inner, "bits": bits})
            tot["labelled"] += nlab; tot["after_BD"] += nbd; tot["after_P"] += nps
            lines.append("   U=%s V=%s case %-3s: labelled %4d, after budgets+degrees %4d, after PSD %4d%s" % (
                ty.split()[0], ty.split()[1], case, nlab, nbd, nps, "" if nps == 0 or nps > 6 else "  " + json.dumps(kept)))
    print("%s: %s" % (name, tot)); print("\n".join(lines), flush=True)


if __name__ == "__main__":
    t = time.time()
    for name in (sys.argv[1:] or list(E)): run(name)
    print("done in %.0f s" % (time.time() - t))
