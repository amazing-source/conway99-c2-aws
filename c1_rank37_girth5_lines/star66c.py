"""Instance writer + driver for starc.exe ((6,6) ball at rank 37, rank-one residue; statement in star66.py).
usage: star66c.py i1 i2 rho u c0 use_real [limit] [maxnodes] [mode]     mode 'comb' = control without the mod-7 conditions"""
import sys, json, itertools, subprocess, time
from fractions import Fraction as Fr
from star66 import make_ball, kmatrix, candidates, build_comp


def real_pinv(a):
    n = 18
    A = [[Fr((3 if i == j else 0) - (1 if j in a[i] else 0)) + Fr(1, 18) for j in range(n)] + [Fr(int(i == j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [x / pv for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return [[float(A[i][n + j] - Fr(1, 18)) for j in range(n)] for i in range(n)]


def write_instance(path, key1, key2, rho, u, c0, use_real, limit, maxnodes, mode="mod7"):
    adj, lay, comp, Hp = make_ball(key1, key2, rho)
    K = kmatrix(adj, lay)
    R1, R2 = real_pinv(build_comp(key1)), real_pinv(build_comp(key2))
    Hr = [[0.0] * 36 for _ in range(36)]
    for i in range(18):
        for j in range(18):
            Hr[i][j] = R1[i][j]; Hr[18 + i][18 + j] = R2[i][j]
    cands = candidates(u, adj, lay, comp, K)
    cross = [z for z in adj[u] if lay[z] != lay[u]]
    sq = {}
    for x in range(7):
        sq.setdefault((c0 * x * x) % 7, []).append(x)
    lines = []
    for n in cands:
        hv = [sum(Hp[w][z] for w in n) % 7 for z in range(36)]
        gam = (sum(hv[z] for z in n) - 6) % 7
        hr = [sum(Hr[w][z] for w in n) for z in range(36)]
        e = sum(hr[z] for z in n)
        apex = int(any(z in n for z in cross))
        if mode == "comb":
            xis = [0]; hv = [0] * 36; hv[u] = 3     # g'(i,j) = 3 for every pair: all pairs read as non-adjacent
        else:
            xis = sq.get(gam, [])
        for x in xis:
            lines.append(" ".join(map(str, n)) + f" {x} {apex} " + " ".join(map(str, hv)) + f" {e:.17g} " + " ".join(f"{t:.17g}" for t in hr))
    dem = [K[u][w] for w in range(36)]; dem[u] = 0
    with open(path, "w") as f:
        f.write(f"{len(lines)} {u} {c0} {use_real} {limit} {maxnodes}\n" + " ".join(map(str, dem)) + "\n" + "\n".join(lines) + "\n")
    return len(cands), len(lines)


def main():
    types = json.load(open("comp66_types.json"))
    i1, i2, r, u, c0, use_real = (int(x) for x in sys.argv[1:7])
    limit = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    maxnodes = int(sys.argv[8]) if len(sys.argv) > 8 else 2000000000
    mode = sys.argv[9] if len(sys.argv) > 9 else "mod7"
    rho = list(itertools.permutations(range(3)))[r]
    key = lambda t: tuple(tuple(x) for x in t["key"])
    path = f"inst_{i1}_{i2}_{r}_{u}_{c0}_{use_real}.txt"
    nc, ni = write_instance(path, key(types[i1]), key(types[i2]), rho, u, c0, use_real, limit, maxnodes, mode)
    t0 = time.time()
    out = subprocess.run(["./starc.exe", path], capture_output=True, text=True).stdout.strip()
    print(f"types ({i1},{i2}) rho={rho} u={u} c0={c0} real={use_real} mode={mode}: candidates {nc}; {out} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
