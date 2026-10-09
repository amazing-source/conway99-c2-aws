"""Pair lemma for the balanced torsion of a (4,8) ball (no prism through an edge of T).
Let E be the torsion space of the large component (dimension t) and B a subspace of balanced vectors: every shadow n
satisfies b(n) = 0 for b in B.  Two near points a, b with K_ab = c > 0 lie together in exactly c shadows, so at least
c admissible 6-sets containing a and b must be B-balanced.  The test below is purely combinatorial (no rank condition
beyond the fact that B is made of true relations): for every subspace B of dimension d of E it lists the pairs that
cannot be covered.  If every subspace of dimension d fails, no subspace of dimension >= d is balanced.
usage: python pair48.py T d [s]        T = torsion rank of the large component, d = dimension of B"""
import sys, json, itertools, time
from gen66 import torsion_vectors, nullspace7
from multi import make_ball, kmatrix, candidates
from sweep48 import SMALL, REPS, big_key
from sweep48t import subspaces

ID = [(0, 1, 2)] * 2


def shadows(adj, lay, comp, K, quota):
    """all admissible 6-sets (each one is found from each of its members)"""
    out = set()
    for u in range(36):
        for n in candidates(u, adj, lay, comp, K, quota): out.add(tuple(sorted(n)))
    return sorted(out)


def pair_test(s, b, line, d):
    adj, lay, comp = make_ball([SMALL[s], big_key(line)], ID); K = kmatrix(adj, lay)
    E = torsion_vectors(adj, comp, 1); t = len(E)
    sh = shadows(adj, lay, comp, K, [2, 4])
    pid = {}; need1 = need2 = 0
    for a in range(36):
        for c in range(a + 1, 36):
            pid[(a, c)] = len(pid)
            if K[a][c] >= 1: need1 |= 1 << pid[(a, c)]
            if K[a][c] >= 2: need2 |= 1 << pid[(a, c)]
    m1 = {}; m2 = {}
    for n in sh:
        code = tuple(sum(e[z] for z in n) % 7 for e in E)
        pm = 0
        for a, c in itertools.combinations(n, 2): pm |= 1 << pid[(a, c)]
        m2[code] = m2.get(code, 0) | (m1.get(code, 0) & pm); m1[code] = m1.get(code, 0) | pm
    passing = []; total = 0
    for piv, rows in subspaces(t, d):
        total += 1
        ns = nullspace7([r[:] for r in rows])                      # sigma with rows . sigma = 0
        ge1 = ge2 = 0
        for coef in itertools.product(range(7), repeat=len(ns)):
            code = tuple(sum(c * v[k] for c, v in zip(coef, ns)) % 7 for k in range(t))
            a1 = m1.get(code, 0)
            if a1:
                ge2 |= m2.get(code, 0) | (ge1 & a1); ge1 |= a1
        if (need1 & ~ge1) == 0 and (need2 & ~ge2) == 0: passing.append(rows)
    return t, len(sh), total, passing


if __name__ == "__main__":
    T = int(sys.argv[1]); d = int(sys.argv[2])
    lines = [l for l in open("types_m4_p0.txt").read().split("\n") if l.strip()]
    tors = [x for x in json.load(open("tors_m4.json")) if x[1] == T]
    reps = [int(sys.argv[3])] if len(sys.argv) > 3 else REPS
    bad = 0
    for s in reps:
        for (b, t) in tors:
            t0 = time.time()
            tt, nsh, total, passing = pair_test(s, b, lines[b], d)
            assert tt == T
            if passing: bad += 1
            print(f"pair48 {s} {b} | t={tt} shadows {nsh} subspaces of dimension {d}: {total}, passing the pair test: {len(passing)}"
                  f" {passing[:2] if passing else ''} | {time.time()-t0:.1f}s", flush=True)
    print(f"pair test T={T} d={d}: balls {len(reps) * len(tors)}, with a passing subspace {bad}", flush=True)
