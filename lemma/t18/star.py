# Round 2.  "Star" test at one active orbit I, for a structure without d = 3 vertices (B1) -- or, for B0 / B2,
# restricted to stars whose 10 outside neighbours all have d <= 2 (then NOT exhaustive for those graphs).
#
# W_I = S u {inf} u N(x_I) u N(y_I)   (18 + 1 + 10 + 8 = 37 vertices; z_I, sigma z_I lie in both neighbourhoods)
# is COMPLETELY determined by:
#   (a) the types (N+, N-) of the 10 outside neighbours of x_I: 4 quads u_{Ik} (k with codeg(I,k) = 1, N- = Q_k an
#       R-edge) and 6 singles (I; j) with multiplicity need(I,j) - #{k : j in Q_k};
#   (b) the perfect matching of the 6 "free" outside neighbours of x_I (the 3 triangles {x_I, u, u'});
#   (c) the symmetric 8x8 matrix M[v][w] = [v ~ sigma w], v, w outside neighbours of x_I other than z_I, sigma z_I;
#       M[v][v] = 1 iff v is in N(inf) (exactly two such v), row sums forced:
#       sum_w M[v][w] + [v matched with z_I or sigma z_I] = 2 - |N+(v) n B(I)|   (mu = 2 for the pair v, y_I).
# Tests on W_I: lambda/mu upper bounds on every pair, exact PSD of 9(3I-A)+J and 11(4I+A)-2J (integer certificate
# for every rejection).
# Output: for every (a), the number of completions (b),(c) passing; list of (a) with at least one completion.
# usage: python star.py <structure index 0|1|2> <I> [time limit s]
import json, os, sys, itertools, time
import numpy as np
from enum_S import neg_certificate

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si, I = int(sys.argv[1]), int(sys.argv[2])
tlimit = float(sys.argv[3]) if len(sys.argv) > 3 else 540.0
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
Bn = [set(j for j in range(9) if j != i and m[i][j] & 1) for i in range(9)]
codeg = lambda a, b: len(Bn[a] & Bn[b])
Redges = [(a, b) for a in range(9) for b in range(a + 1, 9) if codeg(a, b) == 1]
AT0 = set(); AT1 = set(); AS1 = set()
for Np, Nm, flag in types[name]:
    if len(Np) == 2:
        (AT1 if flag else AT0).add((tuple(Np), tuple(Nm)))
    if len(Np) == 1 and flag:
        AS1.add((Np[0], Nm[0]))
need = lambda i, j: 1 if j in Bn[i] else 2          # outside common neighbours of x_i and y_j (also i = j)

Rk = sorted(k for k in range(9) if k != I and codeg(I, k) == 1)
assert len(Rk) == 4, "this script needs 4 need-partners at I"
cand = {}
for k in Rk:
    P = tuple(sorted((I, k)))
    cand[k] = [Q for Q in Redges if Q != P and ((P, Q) in AT0 or (P, Q) in AT1)]

# ---------- (a) level-1 data of the star
stars = []
for Qs in itertools.product(*[cand[k] for k in Rk]):
    if len(set(Qs)) < 4:
        continue
    if any(len(set(Qs[a]) & set(Qs[b])) > 1 for a in range(4) for b in range(a + 1, 4)):
        continue
    cnt = [sum(1 for Q in Qs if j in Q) for j in range(9)]
    if any(cnt[j] > need(I, j) for j in range(9)):
        continue
    ok = True
    for a, k in enumerate(Rk):
        Q = Qs[a]
        if I in Q:                                   # u_{Ik} is z_I or sigma z_I: sigma u = u_{Q} must be the quad (Q; {I,k})
            j = Q[0] if Q[1] == I else Q[1]
            if j not in Rk or Qs[Rk.index(j)] != tuple(sorted((I, k))):
                ok = False; break
    if not ok:
        continue
    stars.append(Qs)
print(f"{name}  I = {I}: need-partners {Rk}, candidate N- per quad {[len(cand[k]) for k in Rk]}, level-1 stars: {len(stars)}")
sys.stdout.flush()

SIG = lambda v: v + 9 if v < 9 else v - 9
adjS = [set() for _ in range(18)]
for i in range(9):
    for j in Bn[i]:
        adjS[i].add(9 + j); adjS[9 + j].add(i)

t0 = time.time()
stats = {"stars": len(stars), "stars_done": 0, "stars_alive": 0, "matchings": 0, "M_tried": 0,
         "fail_local": 0, "fail_psd": 0, "pass": 0}
alive = []
timed_out = False


def matchings(vs, ok):
    if not vs:
        yield []
        return
    a = vs[0]
    for t in range(1, len(vs)):
        b = vs[t]
        if ok(a, b):
            for rest in matchings(vs[1:t] + vs[t + 1:], ok):
                yield [(a, b)] + rest


def psd_ok(A):
    n = len(A)
    An = np.array(A, dtype=np.int64)
    M1 = 27 * np.eye(n, dtype=np.int64) - 9 * An + 1
    M2 = 44 * np.eye(n, dtype=np.int64) + 11 * An - 2
    for Mx in (M1, M2):
        w = np.linalg.eigvalsh(Mx.astype(float))
        if w[0] < -1e-7:
            if neg_certificate(Mx.tolist()) is not None:
                return False
    return True


for Qs in stars:
    if time.time() - t0 > tlimit:
        timed_out = True
        break
    stats["stars_done"] += 1
    # the 10 outside neighbours of x_I
    X = []
    for a, k in enumerate(Rk):
        X.append((frozenset((I, k)), frozenset(Qs[a])))
    cnt = [sum(1 for Q in Qs if j in Q) for j in range(9)]
    for j in range(9):
        for _ in range(need(I, j) - cnt[j]):
            X.append((frozenset((I,)), frozenset((j,))))
    assert len(X) == 10
    Z = [t for t in range(10) if I in X[t][1]]
    assert len(Z) == 2
    nz = [t for t in range(10) if t not in Z]                      # 8 vertices
    free = [t for t in range(10) if not (X[t][1] & Bn[I])]
    assert len(free) == 6
    hcap = []                                                      # may be in N(inf)
    for t in nz:
        Np, Nm = X[t]
        if Np & Nm:
            hcap.append(False); continue
        if len(Np) == 2:
            hcap.append((tuple(sorted(Np)), tuple(sorted(Nm))) in AT1)
        else:
            hcap.append((min(Np), min(Nm)) in AS1)
    # base neighbourhoods as sets of indices in 0..17
    nbX = [set(Np) | set(9 + j for j in Nm) for Np, Nm in X]
    nbY = [set(SIG(v) for v in nb) for nb in nbX]
    # entry (v, w) of M allowed only if X_v and Y_w have at most one common neighbour in S
    allow = [[len(nbX[nz[a]] & nbY[nz[b]]) <= 1 for b in range(8)] for a in range(8)]
    star_pass = 0
    mok = lambda a, b: (X[a][0] & X[b][0]) == frozenset((I,)) and not (X[a][1] & X[b][1])
    for mt in matchings(free, mok):
        stats["matchings"] += 1
        partner = {}
        for a, b in mt:
            partner[a] = b; partner[b] = a
        rs = []
        for t in nz:
            zadj = 1 if (t in partner and partner[t] in Z) else 0
            rs.append(2 - len(X[t][0] & Bn[I]) - zadj)
        if any(r < 0 for r in rs):
            continue
        # enumerate symmetric M with row sums rs, exactly two diagonal ones (the two neighbours of x_I in N(inf))
        Mm = [[0] * 8 for _ in range(8)]
        rem = rs[:]

        def build(Mm):
            n = 37
            A = [[0] * n for _ in range(n)]
            def add(u, v):
                A[u][v] = 1; A[v][u] = 1
            for u in range(18):
                for v in adjS[u]:
                    A[u][v] = 1
            xi = {t: 19 + t for t in range(10)}                    # X vertices 19..28, inf = 18
            yi = {}
            for a, t in enumerate(nz):
                yi[t] = 29 + a
            yi[Z[0]] = xi[Z[1]]; yi[Z[1]] = xi[Z[0]]
            for t in range(10):
                for v in nbX[t]:
                    add(xi[t], v)
                for v in nbY[t]:
                    add(yi[t], v)
            for a, b in mt:
                add(xi[a], xi[b]); add(yi[a], yi[b])
            for a in range(8):
                for b in range(8):
                    if Mm[a][b]:
                        add(xi[nz[a]], yi[nz[b]])
                if Mm[a][a]:
                    add(18, xi[nz[a]]); add(18, yi[nz[a]])
            return A

        def local_ok(A):
            n = len(A)
            rows = [0] * n
            for u in range(n):
                b = 0
                for v in range(n):
                    if A[u][v]:
                        b |= 1 << v
                rows[u] = b
            for u in range(n):
                ru = rows[u]
                for v in range(u + 1, n):
                    c = bin(ru & rows[v]).count("1")
                    if c > 2 or (c > 1 and (ru >> v) & 1):
                        return False
            return True

        def recM(a, b, ndiag):
            nonlocal_pass = 0
            if a == 8:
                if ndiag != 2:
                    return 0
                stats["M_tried"] += 1
                A = build(Mm)
                if not local_ok(A):
                    stats["fail_local"] += 1
                    return 0
                if not psd_ok(A):
                    stats["fail_psd"] += 1
                    return 0
                stats["pass"] += 1
                return 1
            if b == 8:
                if rem[a] != 0:
                    return 0
                return recM(a + 1, a + 1, ndiag)
            tot = 0
            # option 0
            # feasibility: remaining entries in row a from b..7 must be able to reach rem[a]
            if rem[a] <= (8 - b - 1):
                tot += recM(a, b + 1, ndiag)
            # option 1
            if rem[a] >= 1 and allow[a][b] and allow[b][a]:
                if a == b:
                    if hcap[a] and ndiag < 2:
                        Mm[a][a] = 1; rem[a] -= 1
                        tot += recM(a, b + 1, ndiag + 1)
                        Mm[a][a] = 0; rem[a] += 1
                elif rem[b] >= 1:
                    Mm[a][b] = Mm[b][a] = 1; rem[a] -= 1; rem[b] -= 1
                    tot += recM(a, b + 1, ndiag)
                    Mm[a][b] = Mm[b][a] = 0; rem[a] += 1; rem[b] += 1
            return tot

        star_pass += recM(0, 0, 0)
        if star_pass and len(sys.argv) > 4:
            break                                                   # optional: only existence per star
    if star_pass:
        stats["stars_alive"] += 1
        alive.append([list(Q) for Q in Qs])
print(f"  time {time.time() - t0:.1f}s timed_out={timed_out}")
print("  stats:", stats)
json.dump({"name": name, "I": I, "Rk": Rk, "stats": stats, "timed_out": timed_out, "alive": alive},
          open(os.path.join(here, f"star_{si}_{I}.json"), "w"))
