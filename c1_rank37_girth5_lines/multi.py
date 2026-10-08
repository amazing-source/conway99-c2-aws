"""Disconnected balls with several components, no triangle (4-cycles allowed), torsion-free: star search at rank 37.

NEW FACT USED (same as the (6,6) note, with c components): the differences m_j 1_Ci - m_i 1_Cj are integer 3-eigenvectors,
hence true relations; if no component has 7-torsion they are the whole radical of the Gram M0 = 3J - H, so the 36 vectors
of N(T) span a non-degenerate subspace of codimension c - 1 in the 36-dimensional space V, and every far vertex carries a
vector nu_f in a non-degenerate space N0 of dimension c - 1:
     g(f, f) + q(nu_f) = 0,   g(f, f') + b(nu_f, nu_f') = 3 + A_ff',   sum of nu_f over a star = 0,
with g(i, j) = c_i . (3 + n_j), M0 c_i = 3 + n_i.  For c = 3 the form q is <1,1> or <1,3> (the two classes of rank 2).

Components: normal form (iota, t1, t2, pi) on 0..2m-1 as in comp66.py.
usage: multi.py types m          -> enumerate the triangle-free types with m lines per layer, write comp_m{m}.json
       multi.py run222 [workers] -> every ball made of three components with 2 lines per layer"""
import sys, json, itertools, subprocess, time
from gen66 import Solver, nullspace7


def matchings(e):
    e = list(e)
    if not e:
        yield (); return
    a = e[0]
    for b in e[1:]:
        for m in matchings([x for x in e if x not in (a, b)]): yield ((a, b),) + m


def build(key):
    iota, t1, t2, pi = key; n = len(iota)
    adj = [set() for _ in range(3 * n)]
    def e(x, y): adj[x].add(y); adj[y].add(x)
    for i in range(n):
        e(i, iota[i]); e(n + i, n + t1[i]); e(2 * n + i, 2 * n + t2[i]); e(i, n + i); e(i, 2 * n + i); e(n + i, 2 * n + pi[i])
    return adj


def ok_tf(adj):
    N = len(adj)
    if any(len(s) != 3 for s in adj): return False
    for u in range(N):
        for v in range(u + 1, N):
            c = len(adj[u] & adj[v])
            if v in adj[u]:
                if c: return False
            elif c > 2: return False
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen) == N


def canon_ordered(adj, n, order):
    """minimal key for a FIXED order of the layers (over the labellings of the first layer)"""
    best = None; lay = lambda v: v // n
    L0 = [v for v in range(3 * n) if lay(v) == order[0]]
    for perm in itertools.permutations(range(n)):
        lab = {}
        for idx, v in zip(perm, L0):
            lab[v] = (0, idx)
            for w in adj[v]:
                if lay(w) == order[1]: lab[w] = (1, idx)
                elif lay(w) == order[2]: lab[w] = (2, idx)
        inv = {val: k for k, val in lab.items()}
        def mate(l, i):
            v = inv[(l, i)]; return lab[next(w for w in adj[v] if lay(w) == lay(v))][1]
        iota = tuple(mate(0, i) for i in range(n))
        if best is not None and iota > best[0]: continue
        k = (iota, tuple(mate(1, i) for i in range(n)), tuple(mate(2, i) for i in range(n)),
             tuple(lab[next(w for w in adj[inv[(1, i)]] if lay(w) == order[2])][1] for i in range(n)))
        if best is None or k < best: best = k
    return best


def enumerate_types(m):
    n = 2 * m
    def inv(mm):
        v = [0] * n
        for a, b in mm: v[a] = b; v[b] = a
        return tuple(v)
    ms = [inv(x) for x in matchings(range(n))]
    iota = ms[0]; ordered = {}
    for t1 in ms:
        for t2 in ms:
            for pi in itertools.permutations(range(n)):
                adj = build((iota, t1, t2, pi))
                if ok_tf(adj):
                    k = canon_ordered(adj, n, (0, 1, 2))
                    ordered[k] = ordered.get(k, 0) + 1
    out = []
    for k, mult in sorted(ordered.items()):
        adj = build(k); N = 3 * n
        H = [[((3 if i == j else 0) - (1 if j in adj[i] else 0)) % 7 for j in range(N)] for i in range(N)]
        out.append({"key": [list(x) for x in k], "mult": mult, "torsion": len(nullspace7(H)) - 1})
    json.dump(out, open(f"comp_m{m}.json", "w"))
    print(f"m = {m}: {sum(ordered.values())} triangle-free normal forms, {len(out)} types with ORDERED layers; torsion ranks:",
          sorted(set(t["torsion"] for t in out)))
    return out


def make_ball(keys, rhos):
    """components placed one after the other; component c has its layer l in ball layer rhos[c][l]"""
    adj = []; lay = []; comp = []; base = 0
    for ci, (key, rho) in enumerate(zip(keys, rhos)):
        a = build(key); n = len(key[0])
        for v in range(3 * n):
            adj.append({base + w for w in a[v]}); lay.append(rho[v // n]); comp.append(ci)
        base += 3 * n
    assert base == 36
    return adj, lay, comp


def kmatrix(adj, lay):
    G2 = [[len(adj[i] & adj[j]) for j in range(36)] for i in range(36)]
    K = [[(12 if i == j else 0) - (1 if j in adj[i] else 0) + 2 - G2[i][j] - (1 if lay[i] == lay[j] else 0)
          for j in range(36)] for i in range(36)]
    assert all(K[i][i] == 10 for i in range(36)) and all(min(r) >= 0 for r in K) and all(sum(r) == 60 for r in K)
    return K


def candidates(u, adj, lay, comp, K, quota):
    mate = [next(z for z in adj[w] if lay[z] == lay[w]) for w in range(36)]
    L = [[w for w in range(36) if lay[w] == l] for l in range(3)]
    lu = lay[u]; others = [l for l in range(3) if l != lu]; out = []
    for a in L[lu]:
        if a == u or K[u][a] == 0: continue
        for b1, b2 in itertools.combinations(L[others[0]], 2):
            if mate[b1] == b2 or K[u][b1] == 0 or K[u][b2] == 0: continue
            for c1, c2 in itertools.combinations(L[others[1]], 2):
                if mate[c1] == c2 or K[u][c1] == 0 or K[u][c2] == 0: continue
                n = (u, a, b1, b2, c1, c2)
                cnt = [0] * len(quota)
                for x in n: cnt[comp[x]] += 1
                if cnt != quota: continue
                s = set(n)
                if any(len(adj[x] & s) > 1 for x in n): continue
                if any(len(adj[x] & s) > 2 for x in range(36) if x not in s): continue
                if any(K[x][y] == 0 for x in n for y in n if x < y): continue
                out.append(n)
    return out


def write_instance(path, adj, lay, comp, quota, u, C0, C1, limit=1, maxnodes=3000000000):
    K = kmatrix(adj, lay)
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    sol = Solver(M0)
    assert 36 - sol.rank == len(quota) - 1, "radical larger than the component relations (7-torsion)"
    cands = candidates(u, adj, lay, comp, K, quota)
    cross = [z for z in adj[u] if lay[z] != lay[u]]
    lines = []
    for n in cands:
        rhs = [(3 + (1 if z in n else 0)) % 7 for z in range(36)]
        c = sol.solve(rhs); assert c is not None
        gii = sum(a * b for a, b in zip(c, rhs)) % 7
        cs3 = (3 * sum(c)) % 7; apex = int(any(z in n for z in cross))
        for n1 in range(7):
            for n2 in (range(7) if C1 else [0]):
                if (gii + C0 * n1 * n1 + C1 * n2 * n2) % 7 == 0:
                    lines.append(" ".join(map(str, n)) + f" {n1} {n2} 0 0 {apex} {cs3} 0 " + " ".join(map(str, c)))
    dem = [K[u][w] for w in range(36)]; dem[u] = 0
    with open(path, "w") as f:
        f.write(f"{len(lines)} {u} {C0} {C1} 0 {limit} {maxnodes}\n" + " ".join(map(str, dem)) + "\n" + "\n".join(lines) + "\n")
    return len(cands), len(lines)


def job222(a):
    (i1, i2, i3, r2, r3, C0, C1) = a
    types = json.load(open("comp_m2.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
    perms = list(itertools.permutations(range(3)))
    try:
        adj, lay, comp = make_ball([key(types[i1]), key(types[i2]), key(types[i3])], [(0, 1, 2), perms[r2], perms[r3]])
        path = f"inst_222_{i1}_{i2}_{i3}_{r2}_{r3}_{C0}_{C1}.txt"
        nc, ni = write_instance(path, adj, lay, comp, [2, 2, 2], 0, C0, C1)
        t0 = time.time()
        res = subprocess.run(["./starg.exe", path], capture_output=True, text=True).stdout.strip().split("\n")[-1]
        import os; os.remove(path)
        return f"222 {i1} {i2} {i3} r2={r2} r3={r3} form=<{C0},{C1}> cands={nc} | {res} | {time.time()-t0:.1f}s"
    except AssertionError as ex:
        return f"222 {i1} {i2} {i3} r2={r2} r3={r3} form=<{C0},{C1}> SKIPPED {ex}"


if __name__ == "__main__":
    if sys.argv[1] == "types":
        enumerate_types(int(sys.argv[2]))
    elif sys.argv[1] == "run222":
        from multiprocessing import Pool
        types = json.load(open("comp_m2.json")); nt = len(types)
        # the types have ORDERED layers, so the relative orders are already in the types: identity alignment only
        jobs = [(i1, i2, i3, 0, 0, 1, C1) for i1 in range(nt) for i2 in range(i1, nt) for i3 in range(i2, nt) for C1 in (1, 3)]
        out = open("sweep_222.log", "a"); bad = 0
        with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 12) as p:
            for line in p.imap_unordered(job222, jobs):
                out.write(line + "\n"); out.flush()
                if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
        print(f"222: runs {len(jobs)}, not dead {bad}", flush=True)
