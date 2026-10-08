"""Python side of fast.exe: builds the ball matrices (K, Gm = (M0 + Z Z^T)^(-1) mod 7, real H^+) and runs the search.
Statement and model: NOTE.md of c1_rank37_girth5_lines and the header of fast.c."""
import itertools, subprocess, os
from multi import build, make_ball, kmatrix


def inv_mod7(M):
    n = len(M)
    A = [[x % 7 for x in row] + [int(i == j) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next((i for i in range(c, n) if A[i][c]), None)
        if p is None: return None
        A[c], A[p] = A[p], A[c]
        iv = pow(A[c][c], -1, 7)
        A[c] = [(x * iv) % 7 for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[c])]
    return [row[n:] for row in A]


_pinv_cache = {}


def real_pinv(key):
    """real pseudo-inverse of the Laplacian of one component (floats, Gauss-Jordan on H + J/N)"""
    if key in _pinv_cache: return _pinv_cache[key]
    a = build(key); N = len(a)
    A = [[(3.0 if i == j else 0.0) - (1.0 if j in a[i] else 0.0) + 1.0 / N for j in range(N)] + [float(i == j) for j in range(N)] for i in range(N)]
    for c in range(N):
        p = max(range(c, N), key=lambda i: abs(A[i][c]))
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [x / pv for x in A[c]]
        for i in range(N):
            if i != c and A[i][c] != 0.0:
                f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    R = [[A[i][N + j] - 1.0 / N for j in range(N)] for i in range(N)]
    _pinv_cache[key] = R
    return R


def ball_matrices(keys, rhos):
    adj, lay, comp = make_ball(keys, rhos)
    K = kmatrix(adj, lay)
    nc = len(keys); sizes = [3 * len(k[0]) for k in keys]; quota = [s // 6 for s in sizes]
    # relations z_k = m_{k+1} 1_{C_k} - m_k 1_{C_{k+1}}
    Z = []
    for k in range(nc - 1):
        Z.append([(quota[k + 1] if comp[v] == k else (-quota[k] if comp[v] == k + 1 else 0)) % 7 for v in range(36)])
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    for z in Z:
        assert all(sum(M0[i][j] * z[j] for j in range(36)) % 7 == 0 for i in range(36))
    Mz = [[(M0[i][j] + sum(z[i] * z[j] for z in Z)) % 7 for j in range(36)] for i in range(36)]
    Gm = inv_mod7(Mz)          # None when the radical is larger than the component relations (7-torsion)
    Hr = [[0.0] * 36 for _ in range(36)]; base = 0
    for key, s in zip(keys, sizes):
        R = real_pinv(key)
        for i in range(s):
            for j in range(s): Hr[base + i][base + j] = R[i][j]
        base += s
    return adj, lay, comp, K, quota, Gm, Hr


def run(keys, rhos, u, C0, C1, use_real=1, limit=1, maxnodes=2000000000, tag="x", exe="./fast.exe"):
    adj, lay, comp, K, quota, Gm, Hr = ball_matrices(keys, rhos)
    if Gm is None: return "TORSION"
    path = f"fast_{tag}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {C0} {C1} {len(keys)} {use_real} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, Gm):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for row in Hr: f.write(" ".join(f"{x:.12g}" for x in row) + "\n")
    res = subprocess.run([exe, path], capture_output=True, text=True).stdout.strip().split("\n")
    os.remove(path)
    return res[-1] if res else "NO OUTPUT"
