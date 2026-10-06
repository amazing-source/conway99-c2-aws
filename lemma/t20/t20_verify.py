# T20, enumerator 2 (independent of t20_enum.py / t20_kernel.py / t20_common.py: no shared code).
# Different program: pure Python (no numba), orbit pairs taken in the reverse order (orbit 9 first), inner orbits
# carry the HIGHEST labels here (the lowest in enumerator 1), other symmetry breaking in case I (row 9 instead of
# row 0), bitmask test of (L) during the search and a from-scratch test with integer matrix products
# (C = A @ A on the 21 vertices) plus the eigen-equation A phi = -4 phi on every structure found.  No isomorphism test: the labelled structures are sorted by an isomorphism invariant (traces of the
# powers of the weighted orbit matrix) and the counts are compared with |G| / |Aut| of the classes of enumerator 1.
import sys, json, time
from itertools import combinations
from math import factorial
import numpy as np

N = 10


def build(minus, plus, H):
    A = np.zeros((21, 21), dtype=np.int64)
    for (i, j) in minus:
        A[i, 10 + j] = A[10 + j, i] = 1
        A[j, 10 + i] = A[10 + i, j] = 1
    for (i, j) in plus:
        A[i, j] = A[j, i] = 1
        A[10 + i, 10 + j] = A[10 + j, 10 + i] = 1
    for i in H:
        A[i, 10 + i] = A[10 + i, i] = 1
        A[20, i] = A[i, 20] = 1
        A[20, 10 + i] = A[10 + i, 20] = 1
    return A


OFF = 1 - np.eye(21, dtype=np.int64)


def lam_mu_ok(A):
    C = A @ A
    return bool(np.all((C + A) * OFF <= 2))      # adjacent: C <= 1, non-adjacent: C <= 2


def eigen_ok(A):
    phi = np.array([1] * 10 + [-1] * 10 + [0], dtype=np.int64)
    r = A @ phi
    return bool(np.all(r[:10] == -4) and np.all(r[10:20] == 4) and r[20] == 0)


def invariant(minus, plus, H):
    W = np.zeros((N, N), dtype=np.int64)
    for (i, j) in minus:
        W[i, j] += 1; W[j, i] += 1
    for (i, j) in plus:
        W[i, j] += 3; W[j, i] += 3
    for i in H:
        W[i, i] += 1
    out = []
    Z = np.eye(N, dtype=np.int64)
    for k in range(1, 11):
        Z = Z @ W
        out.append(int(np.trace(Z)))
    return tuple(out)


def run(H, plus, forced_row9=None):
    """pair-by-pair search in the REVERSE order of enumerator 1 (orbit 9 first, partners from high to low),
    pure Python integers (bitmasks + int.bit_count), leaves re-checked from scratch with matrix products."""
    hs = set(H)
    pdeg = [0] * N
    for (i, j) in plus:
        pdeg[i] += 1; pdeg[j] += 1
    target = [pdeg[i] + 4 - (1 if i in hs else 0) for i in range(N)]
    order = [(j, i) for i in range(9, 0, -1) for j in range(i - 1, -1, -1)]
    A0 = build([], plus, H)
    if not lam_mu_ok(A0):
        return {}, 0
    adj = [int(sum(int(A0[u, v]) << v for v in range(21))) for u in range(21)]
    minus = []
    have = [0] * N
    left = [9] * N
    hist = {}
    nodes = [0]
    forced = set(forced_row9) if forced_row9 is not None else None

    def touch_ok(vs):
        for u in vs:
            au = adj[u]
            for v in range(21):
                if v == u:
                    continue
                c = (au & adj[v]).bit_count()
                if c > 2 or (c > 1 and (au >> v) & 1):
                    return False
        return True

    def pair_ok(u, v):
        c = (adj[u] & adj[v]).bit_count()
        return c <= 1 or (c == 2 and not (adj[u] >> v) & 1)

    def edge_ok(u, v):
        # the edge u-v was just added: only the pairs (u,v), (u,w) with w ~ v and (v,w) with w ~ u can have changed
        if not pair_ok(u, v):
            return False
        for a, b in ((u, v), (v, u)):
            nb = adj[b] & ~(1 << a)
            while nb:
                low = nb & -nb
                if not pair_ok(a, low.bit_length() - 1):
                    return False
                nb ^= low
        return True

    def rec(k):
        nodes[0] += 1
        if k == 45:
            A = build(minus, plus, H)
            assert lam_mu_ok(A) and eigen_ok(A)
            inv = invariant(minus, plus, H)
            hist[inv] = hist.get(inv, 0) + 1
            return
        j, i = order[k]
        for s in (0, 1):
            if forced is not None and i == 9 and s != (1 if j in forced else 0):
                continue
            if have[i] + s > target[i] or have[j] + s > target[j]:
                continue
            if have[i] + s + left[i] - 1 < target[i] or have[j] + s + left[j] - 1 < target[j]:
                continue
            if s:
                adj[i] |= 1 << (10 + j); adj[10 + j] |= 1 << i
                adj[j] |= 1 << (10 + i); adj[10 + i] |= 1 << j
                good = edge_ok(i, 10 + j) and edge_ok(j, 10 + i)
            else:
                good = True
            if good:
                if s:
                    minus.append((j, i))
                have[i] += s; have[j] += s; left[i] -= 1; left[j] -= 1
                rec(k + 1)
                have[i] -= s; have[j] -= s; left[i] += 1; left[j] += 1
                if s:
                    minus.pop()
            if s:
                adj[i] &= ~(1 << (10 + j)); adj[10 + j] &= ~(1 << i)
                adj[j] &= ~(1 << (10 + i)); adj[10 + i] &= ~(1 << j)
    rec(0)
    return hist, nodes[0]


CASES = {
    # name: (H, plus, forced row 9, |G|, name of the case in enumerator 1)
    "I":   ((), [], (5, 6, 7, 8), None, "I"),
    "IIa": ((8, 9), [(0, 1)], None, 2 * 2 * factorial(6), "IIa"),
    "IIb": ((8, 9), [(0, 9)], None, factorial(7), "IIb"),
    "III": ((6, 7, 8, 9), [], None, factorial(4) * factorial(6), "III"),
    # same cases with the plus edge on high labels (the count of labelled structures does not depend on the labels;
    # the search is much shorter because the orbits of degree 5 are met early)
    "IIa2": ((8, 9), [(6, 7)], None, 2 * 2 * factorial(6), "IIa"),
    "IIb2": ((8, 9), [(7, 9)], None, factorial(7), "IIb"),
}


def main():
    names = sys.argv[1:] or ["IIb", "IIa", "III", "I"]
    ref = {}
    for fn in ("structures_III_IIb_IIa.json", "structures_I.json"):
        try:
            ref.update(json.load(open(fn)))
        except Exception as ex:
            print("cannot read", fn, ex)
    for name in names:
        H, plus, forced, G, rname = CASES[name]
        t0 = time.time()
        hist, nodes = run(H, plus, forced)
        tot = sum(hist.values())
        print("case %s: labelled structures %d, distinct invariants %d, nodes %d, %.1f s" % (name, tot, len(hist), nodes, time.time() - t0))
        # prediction from the classes of enumerator 1
        pred = {}
        for rec in ref.get(rname, []):
            m = rec["m"]
            Hr = rec["H"]
            minus_r = [(i, j) for i in range(N) for j in range(i + 1, N) if m[i][j] & 1]
            plus_r = [(i, j) for i in range(N) for j in range(i + 1, N) if m[i][j] & 2]
            inv = invariant(minus_r, plus_r, Hr)
            cnt = factorial(10) // (126 * rec["aut"]) if name == "I" else G // rec["aut"]
            pred[inv] = pred.get(inv, 0) + cnt
        print("   enumerator-1 classes: %d, distinct invariants among them: %d" % (len(ref.get(rname, [])), len(pred)))
        for inv in sorted(set(hist) | set(pred)):
            print("   invariant tr(W^2..5)=%s : verifier %d, predicted from enumerator 1 %d  %s" % (
                inv[1:5], hist.get(inv, 0), pred.get(inv, 0), "OK" if hist.get(inv, 0) == pred.get(inv, 0) else "MISMATCH"))
        print("   AGREEMENT: %s" % (hist == pred))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
