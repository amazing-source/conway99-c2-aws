"""General instance writer for starg.exe: a (6,6) ball at rank 37 whose Gram on N(T) has radical R0 = <z0> + torsion.
Model (hand, this session): T = true relations (z0 = 1_C1 - 1_C2 and the balanced torsion), rad = unbalanced torsion
(at most one vector phi here), beta a functional with beta(phi) = 1, beta(T) = 0.  For a shadow n: s = phi.n,
rhs = 3 + n - s beta, M0 c = rhs (M0 = 3J - H), g(i,j) = c_i . rhs_j, and at rank 37
   g(i,i) + 2 alpha_i s_i + C0 nu1_i^2 + C1 nu2_i^2 = 0,
   g(i,j) + alpha_i s_j + alpha_j s_i + C0 nu1_i nu1_j + C1 nu2_i nu2_j = 3 + A_ij,
   sum over a star of nu = 0 and of alpha = -(4 beta_u + beta_t + beta_mate + beta_u1 + beta_u2).
usage: gen66.py case i1 i2 rho u [c0] [lam]     case in 00, 01u, 10u, 11"""
import sys, json, itertools, subprocess, time
from star66 import make_ball, kmatrix, candidates, build_comp


def nullspace7(M):
    M = [[x % 7 for x in r] for r in M]; n = len(M[0]); piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; iv = pow(M[r][c], -1, 7); M[r] = [(x * iv) % 7 for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]; out = []
    for f in free:
        v = [0] * n; v[f] = 1
        for i, c in enumerate(piv): v[c] = (-M[i][f]) % 7
        out.append(v)
    return out


class Solver:
    """solves M x = rhs mod 7 for a fixed matrix M (returns None if inconsistent)"""
    def __init__(self, M):
        n = len(M); A = [[x % 7 for x in r] + [int(i == j) for j in range(n)] for i, r in enumerate(M)]
        self.piv = []; r = 0
        for c in range(n):
            p = next((i for i in range(r, n) if A[i][c]), None)
            if p is None: continue
            A[r], A[p] = A[p], A[r]; iv = pow(A[r][c], -1, 7); A[r] = [(x * iv) % 7 for x in A[r]]
            for i in range(n):
                if i != r and A[i][c]:
                    f = A[i][c]; A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[r])]
            self.piv.append(c); r += 1
        self.E = [row[n:] for row in A]; self.rank = r; self.n = n

    def solve(self, rhs):
        y = [sum(e * b for e, b in zip(row, rhs)) % 7 for row in self.E]
        if any(y[i] for i in range(self.rank, self.n)): return None
        x = [0] * self.n
        for i, c in enumerate(self.piv): x[c] = y[i]
        return x


def torsion_vectors(adj, comp, which):
    """a basis of the sum-zero vectors of ker_7(Laplacian) on one component, extended by zero"""
    idx = [v for v in range(36) if comp[v] == which]
    H = [[((3 if a == b else 0) - (1 if b in adj[a] else 0)) % 7 for b in idx] for a in idx]
    ns = nullspace7(H)
    ind = []
    for v in ns:
        m = (sum(v) * pow(len(idx) % 7, -1, 7)) % 7        # mean over the component (its size is prime to 7)
        w = [(x - m) % 7 for x in v]
        if not any(w): continue
        full = [0] * 36
        for a, x in zip(idx, w): full[a] = x
        if len(nullspace7([list(x) for x in zip(*(ind + [full]))])) == 0: ind.append(full)
    return ind


def write_general(path, adj, lay, comp, u, Tvecs, phi, C0, C1, limit=1, maxnodes=20000000000):
    K = kmatrix(adj, lay)
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    sol = Solver(M0)
    beta = [0] * 36
    if phi is not None:
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
        for i, c in enumerate(piv): beta[c] = A[i][36]
        assert sum(b * p for b, p in zip(beta, phi)) % 7 == 1
        assert all(sum(b * t for b, t in zip(beta, tv)) % 7 == 0 for tv in Tvecs)
    cands = candidates(u, adj, lay, comp, K)
    cross = [z for z in adj[u] if lay[z] != lay[u]]
    lines = []; kept = 0
    for n in cands:
        if any(sum(tv[z] for z in n) % 7 for tv in Tvecs): continue
        kept += 1
        s = (sum(phi[z] for z in n) % 7) if phi is not None else 0
        rhs = [(3 + (1 if z in n else 0) - s * beta[z]) % 7 for z in range(36)]
        c = sol.solve(rhs)
        assert c is not None
        gii = sum(a * b for a, b in zip(c, rhs)) % 7
        cs3 = (3 * sum(c)) % 7; cb = sum(a * b for a, b in zip(c, beta)) % 7
        apex = int(any(z in n for z in cross))
        for n1 in (range(7) if C0 else [0]):
            for n2 in (range(7) if C1 else [0]):
                for al in (range(7) if phi is not None else [0]):
                    if (gii + 2 * al * s + C0 * n1 * n1 + C1 * n2 * n2) % 7 == 0:
                        lines.append(" ".join(map(str, n)) + f" {n1} {n2} {al} {s} {apex} {cs3} {cb} " + " ".join(map(str, c)))
    dem = [K[u][w] for w in range(36)]; dem[u] = 0
    mate = next(z for z in adj[u] if lay[z] == lay[u])
    blayer = sum(beta[z] * (2 * (1 if lay[z] == lay[u] else 0) + 2) for z in range(36))
    alsum = (-(4 * beta[u] + blayer + beta[mate] + sum(beta[z] for z in cross))) % 7
    with open(path, "w") as f:
        f.write(f"{len(lines)} {u} {C0} {C1} {alsum} {limit} {maxnodes}\n" + " ".join(map(str, dem)) + "\n" + "\n".join(lines) + "\n")
    return len(cands), kept, len(lines)


def make_ball_any(key1, key2, rho):
    """as make_ball, without the mod-7 Green function (it does not exist when a component has 7-torsion)"""
    a1, a2 = build_comp(key1), build_comp(key2)
    adj = [set() for _ in range(36)]; lay = [0] * 36; comp = [0] * 18 + [1] * 18
    for v in range(18):
        adj[v] = set(a1[v]); lay[v] = v // 6
        adj[18 + v] = {18 + w for w in a2[v]}; lay[18 + v] = rho[v // 6]
    return adj, lay, comp


def run(case, i1, i2, r, u, c0=1, lam=1, tag="g"):
    types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
    rho = list(itertools.permutations(range(3)))[r]
    adj, lay, comp = make_ball_any(key(types[i1]), key(types[i2]), rho)
    z0 = [1 if comp[v] == 0 else 6 for v in range(36)]
    if case == "00":
        Tv, phi, C0, C1 = [z0], None, c0, 0
    elif case == "01u":
        t2 = torsion_vectors(adj, comp, 1); assert len(t2) == 1
        Tv, phi, C0, C1 = [z0], t2[0], 0, 0
    elif case == "10u":
        t1 = torsion_vectors(adj, comp, 0); assert len(t1) == 1
        Tv, phi, C0, C1 = [z0], t1[0], 0, 0
    elif case == "11":
        t1 = torsion_vectors(adj, comp, 0); t2 = torsion_vectors(adj, comp, 1); assert len(t1) == 1 and len(t2) == 1
        psi = [(a + lam * b) % 7 for a, b in zip(t1[0], t2[0])]
        Tv, phi, C0, C1 = [z0, psi], t1[0], c0, 0
    else:
        raise SystemExit("unknown case")
    path = f"inst_{tag}.txt"
    nc, kept, ni = write_general(path, adj, lay, comp, u, Tv, phi, C0, C1)
    t0 = time.time()
    res = subprocess.run(["./starg.exe", path], capture_output=True, text=True).stdout.strip().split("\n")[-1]
    return f"{case} {i1} {i2} rho={r} u={u} c0={c0} lam={lam} cands={nc} kept={kept} | {res} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    case = sys.argv[1]; i1, i2, r, u = (int(x) for x in sys.argv[2:6])
    c0 = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    lam = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    print(run(case, i1, i2, r, u, c0, lam, tag=f"g{case}_{i1}_{i2}_{r}_{u}_{c0}_{lam}"), flush=True)
