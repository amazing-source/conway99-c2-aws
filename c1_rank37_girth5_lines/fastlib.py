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
    path = f"fast_{tag}_{os.getpid()}.txt"
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


def run_rank(keys, rhos, u, limit=1, maxnodes=2000000000, tag="x", exe="./fastr.exe"):
    """rank mode (fastr.exe): no scalar enumerated, both classes of forms at once; D = components - 1 <= 2"""
    adj, lay, comp, K, quota, Gm, Hr = ball_matrices(keys, rhos)
    if Gm is None: return "TORSION"
    path = f"fastr_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {len(keys) - 1} {len(keys)} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, Gm):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
    res = subprocess.run([exe, path], capture_output=True, text=True).stdout.strip().split("\n")
    os.remove(path)
    return res[-1] if res else "NO OUTPUT"


def compute_beta(phi, Tvecs):
    """a functional beta with beta . phi = 1 and beta . tau = 0 for the true relations tau (same elimination as gen66.py)"""
    rows = [phi] + Tvecs; rhs = [1] + [0] * len(Tvecs)
    A = [r[:] + [b] for r, b in zip(rows, rhs)]; piv = []; rr = 0
    for c in range(36):
        p = next((i for i in range(rr, len(A)) if A[i][c] % 7), None)
        if p is None: continue
        A[rr], A[p] = A[p], A[rr]; iv = pow(A[rr][c], -1, 7); A[rr] = [(x * iv) % 7 for x in A[rr]]
        for i in range(len(A)):
            if i != rr and A[i][c] % 7:
                f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[rr])]
        piv.append(c); rr += 1
    assert rr == len(rows)
    beta = [0] * 36
    for i, c in enumerate(piv): beta[c] = A[i][36]
    return beta


def run_torsion(keys, rhos, u, extra_T, phi, C0, limit=1, maxnodes=2000000000, tag="x", exe="./fastg.exe"):
    """scalar mode with torsion (fastg.exe).  extra_T: balanced torsion vectors (true relations besides the component
    differences); phi: the unbalanced torsion vector or None; C0: 0 = no residue, else the class of the residue form."""
    from gen66 import Solver
    adj, lay, comp = make_ball(keys, rhos); K = kmatrix(adj, lay)
    quota = [3 * len(k[0]) // 6 for k in keys]; nc = len(keys)
    Z = [[(quota[k + 1] if comp[v] == k else (-quota[k] if comp[v] == k + 1 else 0)) % 7 for v in range(36)] for k in range(nc - 1)]
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    sol = Solver(M0)
    Q = [[0] * 36 for _ in range(36)]
    for i, c in enumerate(sol.piv): Q[c] = sol.E[i][:]
    beta = compute_beta(phi, Z + extra_T) if phi is not None else [0] * 36
    cross = [z for z in adj[u] if lay[z] != lay[u]]; mate = next(z for z in adj[u] if lay[z] == lay[u])
    blayer = sum(beta[z] * (2 * (1 if lay[z] == lay[u] else 0) + 2) for z in range(36))
    alsum = (-(4 * beta[u] + blayer + beta[mate] + sum(beta[z] for z in cross))) % 7
    path = f"fastg_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {C0} {nc} {len(extra_T)} {1 if phi is not None else 0} {alsum} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, M0, Q):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for tv in extra_T: f.write(" ".join(map(str, tv)) + "\n")
        f.write(" ".join(map(str, phi if phi is not None else [0] * 36)) + "\n" + " ".join(map(str, beta)) + "\n")
    r = subprocess.run([exe, path], capture_output=True, text=True)
    os.remove(path)
    out = r.stdout.strip().split("\n")
    return (out[-1] if out and out[-1] else "NO OUTPUT") + ((" ERR " + r.stderr.strip()) if r.stderr.strip() else "")


def run_torsion3(keys, rhos, u, extra_T, phis, C0, limit=1, maxnodes=2000000000, tag="x", exe="./fastg3.exe"):
    """scalar mode with several unbalanced torsion vectors (fastg3.exe).  extra_T: balanced torsion vectors; phis: a list
    of vectors whose images form a basis of the radical of the span; C0: 0 = no residue, else the class of the form."""
    from gen66 import Solver
    adj, lay, comp = make_ball(keys, rhos); K = kmatrix(adj, lay)
    quota = [3 * len(k[0]) // 6 for k in keys]; nc = len(keys)
    Z = [[(quota[k + 1] if comp[v] == k else (-quota[k] if comp[v] == k + 1 else 0)) % 7 for v in range(36)] for k in range(nc - 1)]
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    sol = Solver(M0)
    assert 36 - sol.rank == len(Z) + len(extra_T) + len(phis), "radical dimension does not match the model"
    Q = [[0] * 36 for _ in range(36)]
    for i, c in enumerate(sol.piv): Q[c] = sol.E[i][:]
    T = Z + extra_T; betas = []
    for k in range(len(phis)):
        rows = [p[:] for p in phis] + [t[:] for t in T]; rhs = [int(i == k) for i in range(len(phis))] + [0] * len(T)
        A = [r + [b] for r, b in zip(rows, rhs)]; piv = []; rr = 0
        for c in range(36):
            p = next((i for i in range(rr, len(A)) if A[i][c] % 7), None)
            if p is None: continue
            A[rr], A[p] = A[p], A[rr]; iv = pow(A[rr][c], -1, 7); A[rr] = [(x * iv) % 7 for x in A[rr]]
            for i in range(len(A)):
                if i != rr and A[i][c] % 7:
                    f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[rr])]
            piv.append(c); rr += 1
        assert rr == len(rows), "phi and the true relations are not independent"
        beta = [0] * 36
        for i, c in enumerate(piv): beta[c] = A[i][36]
        betas.append(beta)
    cross = [z for z in adj[u] if lay[z] != lay[u]]; mate = next(z for z in adj[u] if lay[z] == lay[u])
    als = []
    for beta in betas:
        blayer = sum(beta[z] * (2 * (1 if lay[z] == lay[u] else 0) + 2) for z in range(36))
        als.append((-(4 * beta[u] + blayer + beta[mate] + sum(beta[z] for z in cross))) % 7)
    als += [0] * (3 - len(als))
    path = f"fastg3_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {C0} {nc} {len(extra_T)} {len(phis)} {als[0]} {als[1]} {als[2]} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, M0, Q):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for tv in extra_T + phis + betas: f.write(" ".join(map(str, tv)) + "\n")
    r = subprocess.run([exe, path], capture_output=True, text=True)
    os.remove(path)
    out = r.stdout.strip().split("\n")
    return (out[-1] if out and out[-1] else "NO OUTPUT") + ((" ERR " + r.stderr.strip()) if r.stderr.strip() else "")


def run_both(keys, rhos, u, limit=1, maxnodes=2000000000, tag="x", exe=None):
    """torsion-free ball with two components: scalar mode for both square classes of c0, matrices built once.
    Returns 'TORSION' when the radical is larger than the component relation."""
    exe = exe or os.path.abspath("fast.exe")
    adj, lay, comp = make_ball(keys, rhos); K = kmatrix(adj, lay)
    nc = len(keys); quota = [3 * len(k[0]) // 6 for k in keys]
    Z = [[(quota[k + 1] if comp[v] == k else (-quota[k] if comp[v] == k + 1 else 0)) % 7 for v in range(36)] for k in range(nc - 1)]
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    Gm = inv_mod7([[(M0[i][j] + sum(z[i] * z[j] for z in Z)) % 7 for j in range(36)] for i in range(36)])
    if Gm is None: return "TORSION"
    body = " ".join(map(str, quota)) + "\n" + " ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n"
    body += "".join(" ".join(map(str, sorted(adj[v]))) + "\n" for v in range(36))
    body += "".join(" ".join(map(str, row)) + "\n" for M in (K, Gm) for row in M)
    body += ("0 " * 36 + "\n") * 36
    out = []
    for c0 in (1, 3):
        path = f"fast_{tag}_{c0}_{os.getpid()}.txt"
        with open(path, "w") as f: f.write(f"{u} {c0} 0 {nc} 0 {limit} {maxnodes}\n" + body)
        res = subprocess.run([exe, path], capture_output=True, text=True).stdout.strip().split("\n")
        os.remove(path)
        out.append(f"c0={c0}: " + (res[-1] if res and res[-1] else "NO OUTPUT"))
    ok = all("solutions 0 timeout 0" in x for x in out)
    return " ; ".join(out) + " ; " + ("solutions 0 timeout 0" if ok else "CHECK")
