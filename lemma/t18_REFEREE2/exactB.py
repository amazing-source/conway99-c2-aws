# Referee 2: exact check (characteristic polynomial, Descartes) that every one of MY stage-B triples has M1[Y37] and
# M2[Y37] positive semidefinite, and satisfies all budgets on Y37; ranks recorded.
import json, glob, sys
from collections import Counter
from common import *
from flint import fmpz_mat
def info(M):
    n = len(M); cp = fmpz_mat(M).charpoly(); co = [int(cp[i]) for i in range(n + 1)]
    z = 0
    while co[z] == 0: z += 1
    q = [co[i] * (-1) ** i for i in range(n + 1)]; q = [c for c in q if c != 0]
    return sum(1 for a, b in zip(q, q[1:]) if (a > 0) != (b > 0)), n - z
for s_ in (2, 0, 1):
    adjB = Bgraph(s_); D = deficient_pairs(adjB)
    REPS = [tuple(t) for t in json.load(open("my_tau_%d.json" % s_))["orbit_reps"]]
    files = ["myB_2_0_528.json"] if s_ == 2 else sorted(glob.glob("myB_%d_*.json" % s_))
    TR = []
    for fn in files: TR += json.load(open(fn))["triples"]
    bad = 0; badb = 0; r1 = Counter(); r2 = Counter()
    for ti, F, H in TR:
        tau = REPS[ti]; nb = [set() for _ in range(37)]
        def E(a, b): nb[a].add(b); nb[b].add(a)
        for i in range(9):
            for j in adjB[i]: E(i, 9 + j)
        for k in range(18):
            for i in D[k]: E(19 + k, i)
            for l in D[tau[k]]: E(19 + k, 9 + l)
        for a in F:
            E(18, 19 + a); E(18, 19 + tau[a])
        for k, l in H: E(19 + k, 19 + l)
        if not budget_ok(nb): badb += 1
        A = [[1 if j in nb[i] else 0 for j in range(37)] for i in range(37)]
        n1, k1 = info([[(27 if i == j else 0) - 9 * A[i][j] + 1 for j in range(37)] for i in range(37)])
        n2, k2 = info([[(44 if i == j else 0) + 11 * A[i][j] - 2 for j in range(37)] for i in range(37)])
        if n1 or n2: bad += 1
        r1[k1] += 1; r2[k2] += 1
    print("B%d: %d stage-B triples; with a budget violation on Y37: %d; not exactly PSD (M1 or M2): %d; rank M1[Y37]: %s; rank M2[Y37]: %s"
          % (s_, len(TR), badb, bad, sorted(r1.items()), sorted(r2.items())), flush=True)
