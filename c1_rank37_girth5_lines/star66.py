"""Complete star of a vertex u in a (6,6) ball at rank 37 (k = 22), with the rank-one residue.

NEW FACT USED.  For a line T whose cubic graph is C1 + C2 (two components of 18 vertices, girth >= 5, no 7-torsion in
either critical group), at rank 37 the 36 vectors p_w of N(T) span a NON-DEGENERATE hyperplane V_T of the 36-dimensional
space V (the only relation is the component vector), V = V_T + <n> orthogonally with q(n) = c0 != 0, and every far vertex f
is p_f = proj(p_f) + xi_f n.  With g'(n, n') = sum over the two components of n^T H_i^+ n' (H_i^+ = inverse of the
Laplacian of C_i on sum-zero vectors, mod 7) this reads
        g'(n_f, n_f) = 6 + c0 xi_f^2,          g'(n_f, n_f') = 3 - A_ff' + c0 xi_f xi_f',
and the eigenvector equation at a ball vertex u gives  sum over the ten far neighbours of u of xi_f = 0.
(September note 126 par.3 ter says "residue of rank <= 1, the star could apply"; it was not run.)
The search below is exhaustive: it looks for ten shadows through u, 0/1, two points per layer, three in each component,
with sum K e_u, the internal graph 4 K_2 + 2 K_1, and scalars xi satisfying the three displayed conditions.
usage: star66.py i1 i2 rho u c0 [mode]   (i1, i2 = indices in comp66_types.json; rho = index of the layer order of C2;
u = vertex of C1; c0 in 1..6; mode 'comb' ignores the conditions mod 7: control that the search finds stars)"""
import sys, json, itertools, time
sys.setrecursionlimit(10000)


def build_comp(key):
    iota, t1, t2, pi = key
    adj = [set() for _ in range(18)]
    def e(x, y):
        adj[x].add(y); adj[y].add(x)
    for i in range(6):
        e(i, iota[i]); e(6 + i, 6 + t1[i]); e(12 + i, 12 + t2[i])
        e(i, 6 + i); e(i, 12 + i); e(6 + i, 12 + pi[i])
    return adj


def inv_mod7(M):
    n = len(M)
    A = [[x % 7 for x in row] + [int(i == j) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c])
        A[c], A[p] = A[p], A[c]
        iv = pow(A[c][c], -1, 7)
        A[c] = [(x * iv) % 7 for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % 7 for x, y in zip(A[i], A[c])]
    return [row[n:] for row in A]


def make_ball(key1, key2, rho):
    """36 vertices: C1 = 0..17 with layers 0,1,2; C2 = 18..35, its layer l sent to rho[l]"""
    a1, a2 = build_comp(key1), build_comp(key2)
    adj = [set() for _ in range(36)]
    lay = [0] * 36; comp = [0] * 18 + [1] * 18
    for v in range(18):
        adj[v] = set(a1[v]); lay[v] = v // 6
        adj[18 + v] = {18 + w for w in a2[v]}; lay[18 + v] = rho[v // 6]
    Hp = [[0] * 36 for _ in range(36)]
    for base, a in ((0, a1), (18, a2)):
        M = [[((3 if i == j else 0) - (1 if j in a[i] else 0) + 1) % 7 for j in range(18)] for i in range(18)]
        I = inv_mod7(M)
        for i in range(18):
            for j in range(18):
                Hp[base + i][base + j] = (I[i][j] - 4) % 7
        # check: H * Hp = I - J/18 = I - 2J mod 7 on the component
        for i in range(18):
            for j in range(18):
                s = sum(((3 if i == k else 0) - (1 if k in a[i] else 0)) * Hp[base + k][base + j] for k in range(18)) % 7
                assert s == ((1 if i == j else 0) - 2) % 7
    return adj, lay, comp, Hp


def kmatrix(adj, lay):
    G2 = [[len(adj[i] & adj[j]) for j in range(36)] for i in range(36)]
    K = [[(12 if i == j else 0) - (1 if j in adj[i] else 0) + 2 - G2[i][j] - (1 if lay[i] == lay[j] else 0)
          for j in range(36)] for i in range(36)]
    assert all(K[i][i] == 10 for i in range(36)) and all(min(r) >= 0 for r in K) and all(sum(r) == 60 for r in K)
    return K


def candidates(u, adj, lay, comp, K):
    mate = [next(z for z in adj[w] if lay[z] == lay[w]) for w in range(36)]
    L = [[w for w in range(36) if lay[w] == l] for l in range(3)]
    lu = lay[u]; others = [l for l in range(3) if l != lu]
    out = []
    for a in L[lu]:
        if a == u or K[u][a] == 0: continue
        for b1, b2 in itertools.combinations(L[others[0]], 2):
            if mate[b1] == b2 or K[u][b1] == 0 or K[u][b2] == 0: continue
            for c1, c2 in itertools.combinations(L[others[1]], 2):
                if mate[c1] == c2 or K[u][c1] == 0 or K[u][c2] == 0: continue
                n = (u, a, b1, b2, c1, c2)
                if sum(comp[x] for x in n) != 3: continue
                s = set(n)
                if any(len(adj[x] & s) > 1 for x in n): continue
                if any(len(adj[x] & s) > 2 for x in range(36) if x not in s): continue
                if any(K[x][y] == 0 for x in n for y in n if x < y): continue
                out.append(n)
    return out


def search(u, adj, lay, comp, Hp, K, c0, mode="mod7", limit=1, planted=None, tmax=None):
    cands = candidates(u, adj, lay, comp, K)
    cross = [z for z in adj[u] if lay[z] != lay[u]]
    sq = {}
    for x in range(7):
        sq.setdefault((c0 * x * x) % 7, []).append(x)
    items = []          # (set, tuple, xi, is_apex, hv)
    for n in cands:
        hv = [sum(Hp[w][z] for w in n) % 7 for z in range(36)]
        gam = (sum(hv[z] for z in n) - 6) % 7
        apex = any(z in n for z in cross)
        if mode == "comb":
            items.append((frozenset(n), n, 0, apex, hv))
        else:
            for xi in sq.get(gam, []):
                items.append((frozenset(n), n, xi, apex, hv))
    by_vertex = {w: [i for i, it in enumerate(items) if w in it[0]] for w in range(36)}
    dem = [K[u][w] for w in range(36)]; dem[u] = 0
    stats = {"nodes": 0, "sols": [], "items": len(items), "cands": len(cands), "timeout": False}
    t0 = time.time()

    def rel(i, j):
        """0 = non-adjacent compatible, 1 = adjacent compatible, None = incompatible"""
        si, ni, xi, ai, hi = items[i]; sj, nj, xj, aj, hj = items[j]
        inter = len(si & sj)
        if planted is not None and i in planted and j in planted:
            return planted_rel(i, j)
        if mode == "comb":
            if inter == 1 and not ai and not aj: return 2      # either
            return 0 if inter <= 2 else None
        v = (sum(hi[z] for z in nj) - 3 - c0 * xi * xj) % 7
        if v == 0: return 0 if inter <= 2 else None
        if v == 6: return 1 if (inter == 1 and not ai and not aj) else None
        return None

    def planted_rel(i, j):
        return planted[i].get(j, 0)

    def dfs(chosen, partner, first_sign_fixed):
        if tmax is not None and time.time() - t0 > tmax:
            stats["timeout"] = True; return True
        stats["nodes"] += 1
        if len(chosen) == 10:
            if any(d for d in dem): return False
            if mode != "comb":
                if sum(items[i][2] for i in chosen) % 7: return False
                if any((not items[i][3]) and partner[i] is None for i in chosen): return False
            stats["sols"].append([(items[i][1], items[i][2]) for i in chosen])
            return len(stats["sols"]) >= limit
        # most constrained vertex with positive residual demand
        best_w, best_list = None, None
        for w in range(36):
            if dem[w] <= 0: continue
            lst = []
            for i in by_vertex[w]:
                if i in partner: continue
                si, ni, xi, ai, hi = items[i]
                if any(dem[z] <= 0 for z in ni if z != u): continue
                if mode != "comb" and not first_sign_fixed and xi > 3: continue
                okc = True; adjto = None
                for j in chosen:
                    r = rel(i, j)
                    if r is None: okc = False; break
                    if r == 1:
                        if adjto is not None or partner[j] is not None: okc = False; break
                        adjto = j
                if okc: lst.append((i, adjto))
            if best_list is None or len(lst) < len(best_list):
                best_w, best_list = w, lst
                if not lst: break
        if best_list is None or not best_list: return False
        for i, adjto in best_list:
            si, ni, xi, ai, hi = items[i]
            for z in ni:
                if z != u: dem[z] -= 1
            chosen.append(i); partner[i] = adjto
            if adjto is not None: partner[adjto] = i
            stop = dfs(chosen, partner, first_sign_fixed or xi != 0)
            chosen.pop(); del partner[i]
            if adjto is not None: partner[adjto] = None
            for z in ni:
                if z != u: dem[z] += 1
            if stop: return True
        return False

    dfs([], {}, False)
    stats["seconds"] = time.time() - t0
    return stats


def main():
    types = json.load(open("comp66_types.json"))
    i1, i2, r, u, c0 = (int(x) for x in sys.argv[1:6])
    mode = sys.argv[6] if len(sys.argv) > 6 else "mod7"
    rho = list(itertools.permutations(range(3)))[r]
    key = lambda t: tuple(tuple(x) for x in t["key"])
    adj, lay, comp, Hp = make_ball(key(types[i1]), key(types[i2]), rho)
    K = kmatrix(adj, lay)
    st = search(u, adj, lay, comp, Hp, K, c0, mode=mode, tmax=600)
    print(f"types ({i1},{i2}) rho={rho} u={u} c0={c0} mode={mode}: candidates {st['cands']}, with xi {st['items']}, "
          f"nodes {st['nodes']}, solutions {len(st['sols'])}, timeout {st['timeout']}, {st['seconds']:.1f}s")
    if st["sols"]: print(st["sols"][0])


if __name__ == "__main__":
    main()
