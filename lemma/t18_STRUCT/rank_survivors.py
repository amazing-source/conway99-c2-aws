# Rank test on the four 47-vertex stage-C survivors of B1 (profile (2,5,0)) found by r3_p250.py.
# Necessary condition in a real srg(99,14,1,2) with the involution sigma:
#   27I - 9A + J = 63 E_{-4} has rank 44; its sigma-odd part has rank 22 and its sigma-even part rank 22.
#   Hence for a sigma-invariant vertex set Y: rank(odd part of M_Y) <= 22 and rank(even part of M_Y) <= 22.
#   Similarly 44I + 11A - 2J = 77 E_3: odd part rank <= 27, even part rank <= 27.
# Exact arithmetic (fractions).  Read-only on ../t18.
import json, glob, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
T18 = os.path.join(os.path.dirname(HERE), "t18")

def rank_exact(M):
    M = [[Fraction(x) for x in r] for r in M]
    n = len(M); m = len(M[0]) if n else 0
    r = 0
    for c in range(m):
        piv = None
        for i in range(r, n):
            if M[i][c] != 0:
                piv = i; break
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        pr = M[r]
        for i in range(r + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / pr[c]
                M[i] = [a - f * b for a, b in zip(M[i], pr)]
        r += 1
        if r == n: break
    return r

def sectors(A, sig):
    """orbit representatives; returns the odd and even quadratic forms of 27I-9A+J and 44I+11A-2J"""
    n = len(A)
    fixed = [v for v in range(n) if sig[v] == v]
    reps = [v for v in range(n) if sig[v] > v]
    out = {}
    for name, c0, c1, cj in (("E-4", 27, -9, 1), ("E3", 44, 11, -2)):
        M = [[(c0 if u == v else 0) + c1 * A[u][v] + cj for v in range(n)] for u in range(n)]
        # odd basis: e_v - e_sig(v)
        odd = [[M[u][v] - M[u][sig[v]] - M[sig[u]][v] + M[sig[u]][sig[v]] for v in reps] for u in reps]
        evb = [("f", v) for v in fixed] + [("o", v) for v in reps]
        def vec(b):
            return [(b[1], 1)] if b[0] == "f" else [(b[1], 1), (sig[b[1]], 1)]
        even = [[sum(M[x][y] for x, _ in vec(a) for y, _ in vec(b)) for b in evb] for a in evb]
        out[name] = (rank_exact(M), len(M), rank_exact(odd), len(odd), rank_exact(even), len(even))
    return out

if __name__ == "__main__":
    reps_tau = json.load(open(os.path.join(T18, "r2_tau_1.json")))["reps"]
    seen = set()
    for f in sorted(glob.glob(os.path.join(T18, "r3_p250_1_*_BC.json"))):
        d = json.load(open(f))
        for e in d.get("survivors", []):
            key = (e["tau"], tuple(e["F"]), tuple(e["rows"]))
            if key in seen: continue
            seen.add(key)
            rows = e["rows"]; n = 47
            A = [[(rows[u] >> v) & 1 for v in range(n)] for u in range(n)]
            tau = reps_tau[e["tau"]]
            sig = list(range(n))
            for i in range(9): sig[i] = i + 9; sig[i + 9] = i
            for k in range(18): sig[19 + k] = 19 + tau[k]
            for x in range(10): sig[37 + x] = 37 + (x ^ 1)
            assert all(A[u][v] == A[v][u] for u in range(n) for v in range(n))
            assert all(A[u][v] == A[sig[u]][sig[v]] for u in range(n) for v in range(n)), "not sigma-invariant"
            # sanity: support graph bipartite P-Q, p adjacent to A_p u W only
            assert all(A[i][j] == 0 for i in range(9) for j in range(9))
            res = sectors(A, sig)
            print("survivor tau #%d F=%s" % (e["tau"], e["F"]))
            for name, bound in (("E-4", 22), ("E3", 27)):
                r, nn, ro, no, re_, ne = res[name]
                print("   %-4s total rank %d of %d | odd rank %d of %d (must be <= %d) | even rank %d of %d (must be <= %d)  -> %s"
                      % (name, r, nn, ro, no, bound, re_, ne, bound,
                         "RANK VIOLATION" if (ro > bound or re_ > bound) else "ok"))
    print("distinct survivors:", len(seen))
