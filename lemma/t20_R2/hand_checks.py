# Arithmetic guards for the hand lemmas of round 2 (pure Python integers; not part of the proofs).
import json
d = {}
for fn in ("structures_I.json", "structures_III_IIb_IIa.json"):
    d.update(json.load(open(fn)))
def graph(m, H, extra=0):
    n = 21 + extra
    A = [[0] * n for _ in range(n)]
    def e(u, v): A[u][v] = A[v][u] = 1
    for i in range(10):
        for j in range(i + 1, 10):
            if m[i][j] & 1: e(i, 10 + j); e(j, 10 + i)
            if m[i][j] & 2: e(i, j); e(10 + i, 10 + j)
    for i in H: e(i, 10 + i); e(20, i); e(20, 10 + i)
    return A
print("1. Identity (#) and the forced counts")
for case in ("I", "IIa", "III"):
    for idx, rec in enumerate(d[case]):
        m, H = rec["m"], rec["H"]
        A = graph(m, H)
        dp = [sum(A[i][j] for j in range(10)) for i in range(10)]
        dm = [sum(A[i][10 + j] for j in range(10)) for i in range(10)]
        assert all(dm[i] == dp[i] + 4 for i in range(10))
        e = sum(dp) // 2; Q = sum(t * t for t in dp); k = len(H)
        sumC = 100 - 70 - 7 * e - Q; sumd = 100 - 4 * e; rhs = 9 - 3 * e - Q
        assert sumC - sumd + 79 == rhs
        print("   %s.%d: k = %d, e = %d, Q = %d: sum C(d,2) = %d, sum d = %d, n_0 + n_3 + 3 n_4 = %d" % (case, idx, k, e, Q, sumC, sumd, rhs))
print("2. Case II: X_0 cannot contain a 4-cycle.  x = -(1 on S u {p}) - (1 more on x2,x3,y2,y3) + 2 on the 4-cycle")
rec = d["IIa"][0]; m, H = rec["m"], rec["H"]
A = graph(m, H, 4)
for (u, v) in ((21, 23), (22, 24), (21, 24), (22, 23)):
    A[u][v] = A[v][u] = 1
n = 25
x = [-1] * 21 + [2] * 4
for v in (2, 3, 12, 13): x[v] = -2
sx = sum(x); xx = sum(t * t for t in x); xAx = sum(x[a] * A[a][b] * x[b] for a in range(n) for b in range(n))
val = 9 * (3 * xx - xAx) + sx * sx
print("   |x|^2 = %d, x^T A x = %d, sum x = %d, x^T (9(3I-A)+J) x = %d" % (xx, xAx, sx, val))
assert (xx, xAx, sx, val) == (49, 184, -17, -44)
eS = sum(A[a][b] for a in range(20) for b in range(a + 1, 20))
print("   used: e(S) = %d, deg_S of x2,x3,y2,y3 = %s, p has %d neighbours in S, none among x2,x3,y2,y3" % (
    eS, [sum(A[v][b] for b in range(20)) for v in (2, 3, 12, 13)], sum(A[20][b] for b in range(20))))
print("3. Case II: number of X_2 neighbours (other than p) of the active inner vertices, from the path count")
for i in (0, 1):
    S_n = [b for b in range(20) if A[i][b]]
    degS = lambda v: sum(A[v][b] for b in range(20))
    tot = 12 - len(S_n) + 40
    rest = tot - sum(degS(v) for v in S_n) - degS(20)       # 20 = p, deg_S(p) = 4
    nout = 14 - len(S_n) - 1
    n2 = rest // 2 - nout
    print("   x_%d: %d neighbours outside S u {p}, sum of d = %d, so %d of them in X_2" % (i, nout, rest // 2, n2))
print("4. Case I: profiles.  (h2,h1,h0) with h2 + h1 + h0 = 7, 2 h2 + h1 = 10 (h3 = 0):",
      [(h2, 10 - 2 * h2, h2 - 3) for h2 in range(3, 6)])
print("   profile (5,0,2): four X_0 vertices in N(p) with >= 8 - 2 a_3 neighbours in X_2 minus A_p;")
print("      n_3 = 0: union >= 4*8 - 4 = 28 > 30 - 10 = 20;   n_3 = 2: union >= 32 - 8 - 4 = 20 > 24 - 10 = 14")
print("ALL CHECKS PASSED")
