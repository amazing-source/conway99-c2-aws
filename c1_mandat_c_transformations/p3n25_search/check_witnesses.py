"""Independent check of the lemma witnesses (pure integer arithmetic from the edges of the register).

Integer parabola lemma, closed form.  For a vertex set S of an srg(99,14,1,2) with induced adjacency matrix A_S, every integer
vector w on S and every integer a:
    Phi(w, a) = w^T (12 I + 2 J - A_S - A_S^2) w - (2a + 1) (14 sum(w) - 1^T A_S w) + (99 - |S|) a (a + 1)  >=  0,
because Phi(w, a) = sum over the vertices z outside S of (t_z - a)(t_z - a - 1), t_z = sum of w over the neighbours of z in S.
Cap lemma.  For u, v in S and X a set of neighbours of v in S not containing u:
    u not adjacent to v:  sum_{x in X} r(u,x) <= 2 (dZ(u) - r(u,v)) + min(r(u,v), #{x in X: r(v,x) = 1});
    u adjacent to v:      sum_{x in X} r(u,x) <= dZ(u) - r(u,v).
usage: check_witnesses.py register.jsonl witnesses.jsonl"""
import sys, json
def mat(edges, n=28):
    A = [[0] * n for _ in range(n)]
    for a, b in edges: A[a][b] = A[b][a] = 1
    return A
def phi_closed(A, w, a):
    n = len(A); Aw = [sum(A[i][j] * w[j] for j in range(n)) for i in range(n)]
    A2w = [sum(A[i][j] * Aw[j] for j in range(n)) for i in range(n)]
    sw = sum(w); quad = 12 * sum(x * x for x in w) + 2 * sw * sw - sum(w[i] * Aw[i] for i in range(n)) - sum(w[i] * A2w[i] for i in range(n))
    return quad - (2 * a + 1) * (14 * sw - sum(Aw)) + (99 - n) * a * (a + 1)
def r_and_d(A):
    n = len(A); r = [[0] * n for _ in range(n)]
    for s in range(n):
        for t in range(n):
            if s != t: r[s][t] = (1 if A[s][t] else 2) - sum(A[s][k] * A[t][k] for k in range(n))
    return r, [14 - sum(row) for row in A]
if __name__ == "__main__":
    reg = {}
    for line in open(sys.argv[1], encoding="utf-8"):
        d = json.loads(line); reg[d["id"]] = d
    npar = ncap = bad = 0
    for line in open(sys.argv[2]):
        rec = json.loads(line); A = mat(reg[rec["id"]]["edges"]); r, dZ = r_and_d(A)
        if rec.get("parabola"):
            p = rec["parabola"]; val = phi_closed(A, p["w"], p["a"])
            ok = (val == p["phi"] and val < 0); npar += ok; bad += not ok
        if rec.get("cap"):
            c = rec["cap"]; u, v, X = c["u"], c["v"], c["X"]
            assert all(A[v][x] for x in X) and u not in X
            lhs = sum(r[u][x] for x in X)
            rhs = (dZ[u] - r[u][v]) if A[u][v] else 2 * (dZ[u] - r[u][v]) + min(r[u][v], sum(1 for x in X if r[v][x] == 1))
            ok = lhs > rhs; ncap += ok; bad += not ok
    print(f"parabola witnesses verified: {npar}; cap witnesses verified: {ncap}; failures: {bad}")
