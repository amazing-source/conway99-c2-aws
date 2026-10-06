# T20: description of the surviving S-structures and first facts about the vertices outside S.
# Exact arithmetic (sympy for factoring characteristic polynomials, Fractions for PSD).
# Run with the 3.12 venv (sympy).   Usage: t20_survivors.py [time limit in seconds for the type scan]
import sys, json, time
from itertools import combinations
import numpy as np
import sympy as sp
from t20_common import *

TL = float(sys.argv[1]) if len(sys.argv) > 1 else 400.0
T0 = time.time()
ref = {}
for fn in ("structures_III_IIb_IIa.json", "structures_I.json"):
    ref.update(json.load(open(fn)))

NAMES = []
for case in ("I", "IIa", "III"):
    for idx, rec in enumerate(ref[case]):
        NAMES.append(("%s.%d" % (case, idx), rec))

t = sp.symbols("t")


def full_adj(m, H, extra_pairs=0):
    st = {(i, j): m[i][j] for (i, j) in PAIRS if m[i][j]}
    adj = graph_of(st, H)
    # extra_pairs inactive inner pairs {a, b}: a ~ b, a ~ p, b ~ p, no neighbour in S
    n = NV
    for q in range(extra_pairs):
        a, b = n, n + 1
        adj += [0, 0]
        for (u, v) in ((a, b), (a, PV), (b, PV)):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        n += 2
    return adj, n


def type_scan(m, H, d, inner):
    """outside vertex z with N(z) n S+ = {x_i : i in Np}, N(z) n S- = {y_j : j in Nm}, |Np| = |Nm| = d;
    sigma z gets the mirrored neighbourhood.  inner = True: z in N(p) (z ~ sigma z ~ p).
    Returns (number passing (L) on S u {p, z, sigma z}, list of those also passing exact PSD), up to sigma."""
    st = {(i, j): m[i][j] for (i, j) in PAIRS if m[i][j]}
    base = graph_of(st, H)
    A0 = np.zeros((23, 23), dtype=np.int64)
    for u in range(21):
        for v in range(21):
            A0[u, v] = (base[u] >> v) & 1
    off = 1 - np.eye(23, dtype=np.int64)
    Z, SZ = 21, 22
    passL = 0
    good = []
    for Np in combinations(range(N), d):
        for Nm in combinations(range(N), d):
            if Nm < Np:
                continue                      # sigma swaps (Np, Nm)
            A = A0.copy()
            for i in Np:
                A[Z, i] = A[i, Z] = 1
                A[SZ, 10 + i] = A[10 + i, SZ] = 1
            for j in Nm:
                A[Z, 10 + j] = A[10 + j, Z] = 1
                A[SZ, j] = A[j, SZ] = 1
            if inner:
                A[Z, SZ] = A[SZ, Z] = 1
                A[Z, 20] = A[20, Z] = 1
                A[SZ, 20] = A[20, SZ] = 1
            C = A @ A
            if not np.all((C + A) * off <= 2):
                continue
            passL += 1
            adj = [int(sum(int(A[u, v]) << v for v in range(23))) for u in range(23)]
            _, M1, M2 = int_matrices(adj, list(range(23)))
            if psd_exact(M1)[0] and psd_exact(M2)[0]:
                good.append((Np, Nm))
    return passL, good


for name, rec in NAMES:
    m, H = rec["m"], rec["H"]
    print("=" * 100)
    print("structure %s   inner orbits H = %s   |Aut| = %d" % (name, H, rec["aut"]))
    print("  minus edges (x_i ~ y_j): %s" % edges_str(m, 1))
    pl = edges_str(m, 2)
    if pl:
        print("  plus edges  (x_i ~ x_j): %s" % pl)
    B = sp.Matrix(N, N, lambda i, j: (m[i][j] & 1) if i != j else (1 if i in H else 0))
    P = sp.Matrix(N, N, lambda i, j: 1 if (i != j and m[i][j] & 2) else 0)
    print("  charpoly of B (diagonal 1 on inner orbits): %s" % sp.factor(B.charpoly(t).as_expr()))
    # orbit Gram on the support: G = 3I + B - P (sign convention c = 1 on every active orbit)
    G = 3 * sp.eye(N) + B - P
    print("  charpoly of the orbit Gram G_T = 3I + B - P: %s" % sp.factor(G.charpoly(t).as_expr()))
    B0 = np.array([[m[i][j] & 1 if i != j else 0 for j in range(N)] for i in range(N)], dtype=np.int64)
    C = B0 @ B0
    adjc = sorted(int(C[i, j]) for i in range(N) for j in range(i + 1, N) if B0[i, j])
    nonc = sorted(int(C[i, j]) for i in range(N) for j in range(i + 1, N) if not B0[i, j])
    tri = int(np.trace(B0 @ B0 @ B0)) // 6
    print("  minus graph: triangles %d; codegrees on adjacent pairs %s, on non-adjacent pairs %s" % (
        tri, {c: adjc.count(c) for c in sorted(set(adjc))}, {c: nonc.count(c) for c in sorted(set(nonc))}))
    adj, n = full_adj(m, H)
    rep = psd_report(adj, list(range(n)))
    print("  exact PSD on S u {p} (21 vertices): M1 %s, M2 %s" % (rep["M1"][:2], rep["M2"][:2]))
    if name.startswith("III"):
        adj, n = full_adj(m, H, extra_pairs=3)
        assert local_ok(adj, n)
        rep = psd_report(adj, list(range(n)))
        print("  exact PSD on S u N[p] (27 vertices, the 3 inactive pairs have no neighbour in S): M1 %s, M2 %s" % (
            rep["M1"][:2], rep["M2"][:2]))
    sys.stdout.flush()

print("=" * 100)
print("Type scan: outside vertices z with d(z) = d (graph rule (L) on S u {p, z, sigma z}, then exact PSD)")
for d in (4, 5, 3):
    for name, rec in NAMES:
        m, H = rec["m"], rec["H"]
        for inner in (False, True):
            if time.time() - T0 > TL:
                print("TIME LIMIT reached before d=%d %s inner=%s  (scan NOT complete from here on)" % (d, name, inner))
                sys.stdout.flush()
                continue
            passL, good = type_scan(m, H, d, inner)
            print("  d=%d  %-6s  z %s: pass (L) %d, pass (L)+PSD %d (classes under sigma)  %s" % (
                d, name, "in N(p) " if inner else "not in N(p)", passL, len(good), good[:6] if len(good) <= 6 else str(good[:3]) + " ..."))
            sys.stdout.flush()
