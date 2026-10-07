# independent check of a sample file written by sample_certs.py: uses only the json lines (no engine code).
# For every record: the adjacency is symmetric, sigma is an automorphism of it, x_i ~ y_j iff B_ij, S+ and S- are
# independent, p is adjacent exactly to the seven pairs, no pair of vertices has more than 2 - [adjacent] common
# neighbours, and x^T M x = q < 0 with M = 27 I - 9 A + J (M1) or 44 I + 11 A - 2 J (M2), in Python integers.
# usage: python check_sample.py <file.jsonl>
import sys, json
lines = open(sys.argv[1]).read().split("\n")
head = json.loads(lines[0])
B = head["B"]
n_ok = 0
for line in lines[1:]:
    if not line.strip():
        continue
    r = json.loads(line)
    A = [[int(ch) for ch in row] for row in r["adjacency"]]
    n = r["n_vertices"]
    sg = r["sigma"]
    assert len(A) == n and all(len(row) == n for row in A)
    assert all(A[a][b] == A[b][a] for a in range(n) for b in range(n)) and all(A[a][a] == 0 for a in range(n))
    assert all(A[sg[a]][sg[b]] == A[a][b] for a in range(n) for b in range(n)) and all(sg[sg[a]] == a for a in range(n))
    assert all(A[i][10 + j] == B[i][j] for i in range(10) for j in range(10))
    assert all(A[i][j] == 0 and A[10 + i][10 + j] == 0 for i in range(10) for j in range(10))
    assert [v for v in range(n) if A[20][v]] == list(range(21, 35))
    for a in range(n):
        for b in range(a + 1, n):
            c = sum(A[a][k] * A[b][k] for k in range(n))
            assert c <= 2 - A[a][b], ("budget", a, b)
    x = r["x"]
    sx = sum(x)
    q = 0
    for a in range(n):
        if x[a]:
            sa = sum(x[b] for b in range(n) if A[a][b])
            q += x[a] * ((27 * x[a] - 9 * sa + sx) if r["matrix"] == "M1" else (44 * x[a] + 11 * sa - 2 * sx))
    assert q == r["q"] and q < 0
    c = r["c"]; Bk = r["block_matrix_on_support"]
    qb = sum(c[a] * Bk[a][b] * c[b] for a in range(len(c)) for b in range(len(c)))
    assert qb == r["block_form"] and qb < 0
    n_ok += 1
    print("record %d: base %d, placed %d, n = %d, %s %s block, support (%d orbits) %s, c = %s, block form %d, x^T M x = %d: OK" % (
        n_ok, r["base_index"], r["placed"], n, r["matrix"], r["block"], r["support_size"], " ".join(r["support"]), c, qb, q))
print("all %d records verified" % n_ok)
