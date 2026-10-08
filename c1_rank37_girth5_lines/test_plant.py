"""Positive control for starc.exe: plant a star (combinatorial star + chosen matching + chosen xi, the mod-7 Green rows of
its ten members rewritten so that the ten satisfy every condition) inside a true instance; the solver must find it."""
import sys, json, itertools, subprocess, random
import star66b, star66c
from star66 import make_ball, kmatrix

def solve_mod7(rows, rhs, nvar):
    M = [r[:] + [b] for r, b in zip(rows, rhs)]; piv = []; r = 0
    for c in range(nvar):
        p = next((i for i in range(r, len(M)) if M[i][c] % 7), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; iv = pow(M[r][c], -1, 7); M[r] = [(x * iv) % 7 for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % 7:
                f = M[i][c]; M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    if any(M[i][nvar] % 7 for i in range(r, len(M))): return None
    x = [0] * nvar
    for i, c in enumerate(piv): x[c] = M[i][nvar]
    return x

types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
i1, i2, r, u, c0 = 0, 0, 0, 0, 1
rho = list(itertools.permutations(range(3)))[r]
adj, lay, comp, Hp = make_ball(key(types[i1]), key(types[i2]), rho); K = kmatrix(adj, lay)
rng = random.Random(5); ok = False
st = star66b.search(u, adj, lay, comp, Hp, K, c0, mode="comb", limit=40)
cross = [z for z in adj[u] if lay[z] != lay[u]]
for sol in st["sols"]:
    mem = [s[0] for s in sol]; apex = [any(z in n for z in cross) for n in mem]
    non = [i for i in range(10) if not apex[i]]
    def match(rest):
        if not rest: return []
        a = rest[0]
        for b in rest[1:]:
            if len(set(mem[a]) & set(mem[b])) == 1:
                m = match([x for x in rest if x not in (a, b)])
                if m is not None: return [(a, b)] + m
        return None
    m = match(non)
    if m is None: continue
    A = [[0] * 10 for _ in range(10)]
    for a, b in m: A[a][b] = A[b][a] = 1
    xi = [1] * 7 + [0] * 3; rng.shuffle(xi)
    newhv = []
    for i in range(10):
        rows = [[1 if z in mem[j] else 0 for z in range(36)] for j in range(10) if j != i]
        rhs = [(3 + c0 * xi[i] * xi[j] - A[i][j]) % 7 for j in range(10) if j != i]
        x = solve_mod7(rows, rhs, 36)
        if x is None: break
        newhv.append(x)
    if len(newhv) < 10: continue
    path = "inst_plant.txt"
    star66c.write_instance(path, key(types[i1]), key(types[i2]), rho, u, c0, 0, 1, 2000000000)
    L = open(path).read().split("\n"); head, demline, items = L[0], L[1], [l for l in L[2:] if l.strip()]
    keep = [l for l in items if tuple(map(int, l.split()[:6])) not in set(mem)]
    for i in range(10):
        keep.append(" ".join(map(str, mem[i])) + f" {xi[i]} {int(apex[i])} " + " ".join(map(str, newhv[i])) + " 0.0 " + " ".join(["0.0"] * 36))
    h = head.split(); h[0] = str(len(keep))
    open(path, "w").write(" ".join(h) + "\n" + demline + "\n" + "\n".join(keep) + "\n")
    print("planted star with matching", m, "xi", xi)
    print(subprocess.run(["./starc.exe", path], capture_output=True, text=True).stdout.strip()[-400:])
    ok = True; break
print("control built:", ok)
