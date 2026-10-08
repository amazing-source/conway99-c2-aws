"""Faster exhaustive star search for a (6,6) ball at rank 37 (same statement as star66.py; forward checking).
usage: star66b.py i1 i2 rho u c0 [mode] [tmax]"""
import sys, json, itertools, time
from star66 import make_ball, kmatrix, candidates
sys.setrecursionlimit(10000)


def search(u, adj, lay, comp, Hp, K, c0, mode="mod7", limit=1, tmax=None, override=None):
    cands = candidates(u, adj, lay, comp, K)
    cross = [z for z in adj[u] if lay[z] != lay[u]]
    sq = {}
    for x in range(7):
        sq.setdefault((c0 * x * x) % 7, []).append(x)
    N, XI, APEX, HV, MASK = [], [], [], [], []
    for n in cands:
        hv = [sum(Hp[w][z] for w in n) % 7 for z in range(36)]
        gam = (sum(hv[z] for z in n) - 6) % 7
        apex = any(z in n for z in cross)
        xis = [0] if mode == "comb" else sq.get(gam, [])
        if override is not None and n in override: xis = [override[n]]
        for xi in xis:
            N.append(n); XI.append(xi); APEX.append(apex); HV.append(hv); MASK.append(sum(1 << z for z in n))
    stats = {"nodes": 0, "sols": [], "items": len(N), "cands": len(cands), "timeout": False}
    t0 = time.time()
    dem = [K[u][w] for w in range(36)]; dem[u] = 0
    umask = 1 << u

    def rel(i, j):
        inter = bin(MASK[i] & MASK[j]).count("1")
        if override is not None and N[i] in override and N[j] in override:
            v = override[("pair", N[i], N[j])] if ("pair", N[i], N[j]) in override else override[("pair", N[j], N[i])]
        elif mode == "comb":
            return 0 if inter <= 2 else None
        else:
            hi = HV[i]
            v = (sum(hi[z] for z in N[j]) - 3 - c0 * XI[i] * XI[j]) % 7
        if v == 0: return 0 if inter <= 2 else None
        if v == 6: return 1 if (inter == 1 and not APEX[i] and not APEX[j]) else None
        return None

    def dfs(alive, chosen, partner, signfixed):
        # alive: list of (i, a) with a = index of the chosen member it must be adjacent to, or -1
        if tmax is not None and time.time() - t0 > tmax:
            stats["timeout"] = True; return True
        stats["nodes"] += 1
        if len(chosen) == 10:
            if any(dem): return False
            if mode != "comb":
                if sum(XI[i] for i in chosen) % 7: return False
                if any((not APEX[i]) and partner[i] < 0 for i in chosen): return False
            stats["sols"].append([(N[i], XI[i]) for i in chosen])
            return len(stats["sols"]) >= limit
        cnt = [0] * 36
        for i, a in alive:
            for z in N[i]: cnt[z] += 1
        best_w = -1
        for w in range(36):
            if dem[w] > 0:
                if cnt[w] < dem[w]: return False
                if best_w < 0 or cnt[w] < cnt[best_w]: best_w = w
        if best_w < 0: return False
        if mode != "comb":
            # every chosen non-apex member without partner needs an alive candidate adjacent to it, or cannot be completed
            need = [j for j in chosen if not APEX[j] and partner[j] < 0]
            if need:
                have = {a for i, a in alive if a >= 0}
                # members chosen earlier may still get a partner among future members only if such a candidate is alive
                if any(j not in have for j in need) and len(chosen) + len(need) > 10: return False
        branch = [(i, a) for i, a in alive if (MASK[i] >> best_w) & 1]
        for i, a in branch:
            if mode != "comb" and not signfixed and XI[i] > 3: continue
            if a >= 0 and partner[a] >= 0: continue
            for z in N[i]:
                if z != u: dem[z] -= 1
            chosen.append(i); partner[i] = a
            if a >= 0: partner[a] = i
            new = []
            for j, b in alive:
                if j == i: continue
                if N[j] == N[i]: continue                       # same shadow with another xi
                okd = True
                for z in N[j]:
                    if z != u and dem[z] <= 0: okd = False; break
                if not okd: continue
                r = rel(j, i)
                if r is None: continue
                if r == 1:
                    if b >= 0 or a >= 0: continue              # j already tied elsewhere, or i already has a partner
                    nb = i
                else:
                    if b >= 0 and b == a: continue             # j had to be adjacent to a, which is now taken by i
                    nb = b
                new.append((j, nb))
            stop = dfs(new, chosen, partner, signfixed or XI[i] != 0)
            chosen.pop(); del partner[i]
            if a >= 0: partner[a] = -1
            for z in N[i]:
                if z != u: dem[z] += 1
            if stop: return True
        return False

    class P(dict):
        def __missing__(self, k): return -1
    dfs([(i, -1) for i in range(len(N))], [], P(), False)
    stats["seconds"] = time.time() - t0
    return stats


def main():
    types = json.load(open("comp66_types.json"))
    i1, i2, r, u, c0 = (int(x) for x in sys.argv[1:6])
    mode = sys.argv[6] if len(sys.argv) > 6 else "mod7"
    tmax = float(sys.argv[7]) if len(sys.argv) > 7 else 600
    rho = list(itertools.permutations(range(3)))[r]
    key = lambda t: tuple(tuple(x) for x in t["key"])
    adj, lay, comp, Hp = make_ball(key(types[i1]), key(types[i2]), rho)
    K = kmatrix(adj, lay)
    st = search(u, adj, lay, comp, Hp, K, c0, mode=mode, tmax=tmax)
    print(f"types ({i1},{i2}) rho={rho} u={u} c0={c0} mode={mode}: candidates {st['cands']}, with xi {st['items']}, "
          f"nodes {st['nodes']}, solutions {len(st['sols'])}, timeout {st['timeout']}, {st['seconds']:.1f}s", flush=True)
    if st["sols"]: print(st["sols"][0])


if __name__ == "__main__":
    main()
