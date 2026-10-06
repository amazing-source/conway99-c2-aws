# For each of the 7 surviving S-structures (e(S+) = 0): list the admissible "types" of an outside vertex w
# (w != inf):  N+(w), N-(w) subset of the 9 active orbits, flag = [w ~ inf].
# Filters (all exact):
#   G1  balance |N+| = |N-| = d <= 3
#   G2  lambda/mu upper bounds against every vertex of Base = S u {inf}; w ~ inf => no common neighbour with inf in Base
#   G3  sigma: w ~ inf => N+ n N- empty ; else |N+ n N-| <= 1 and the common orbit is a word orbit
#   G4  two neighbours s, t of w inside Base must not already have all their common neighbours inside Base
#   P   exact PSD of 63 E_{-4} and 77 E_3 on Base u {w, sigma w}  (integer certificate for every rejection)
#   L   (conditional on H16 = the 04/10 lemma) lattice test on T u {O}: no value 1..8 of Q
import json, os, itertools, sys
from latt import lattice_test, G_T_of
from enum_S import neg_certificate

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))


def base_adj(m, h):
    adj = [set() for _ in range(19)]
    def add(u, v):
        adj[u].add(v); adj[v].add(u)
    for i in range(9):
        for j in range(9):
            if i != j and m[i][j] & 1:
                add(i, 9 + j)
    for i in h:
        add(i, 9 + i); add(18, i); add(18, 9 + i)
    return adj


def types_for(m, h, use_lattice=True, verbose=False):
    adj = base_adj(m, h)
    GT = G_T_of(m, h)
    stats = {}
    good = []
    for d in range(0, 4):
        for Np in itertools.combinations(range(9), d):
            for Nm in itertools.combinations(range(9), d):
                for flag in (0, 1):
                    key = (d, flag)
                    st = stats.setdefault(key, [0, 0, 0, 0])   # G, P, L(pass), sigma-classes
                    N = set(Np) | set(9 + j for j in Nm)
                    if flag:
                        N.add(18)
                    # G2
                    ok = True
                    for s in range(19):
                        c = len(N & adj[s])
                        if s in N:
                            if c > 1: ok = False; break
                        else:
                            if c > 2: ok = False; break
                    if not ok:
                        continue
                    if flag and (N & adj[18]):
                        continue
                    # G4: two neighbours s, t of w in Base must still need a common neighbour outside Base
                    for s, t in itertools.combinations(sorted(N), 2):
                        if len(adj[s] & adj[t]) + 1 > (1 if t in adj[s] else 2):
                            ok = False; break
                    if not ok:
                        continue
                    common = set(Np) & set(Nm)
                    if flag and common:
                        continue
                    if not flag and (len(common) > 1 or any(i in h for i in common)):
                        continue
                    if flag and len(h) == 0 and d > 3:
                        continue
                    st[0] += 1
                    # P: graph on Base u {w, sw}
                    n = 21
                    A = [[0] * n for _ in range(n)]
                    for u in range(19):
                        for v in adj[u]:
                            A[u][v] = 1
                    sN = set()
                    for v in N:
                        sN.add(v + 9 if v < 9 else (v - 9 if v < 18 else 18))
                    for v in N:
                        A[19][v] = A[v][19] = 1
                    for v in sN:
                        A[20][v] = A[v][20] = 1
                    if flag:
                        A[19][20] = A[20][19] = 1
                    # lambda/mu check between w and sigma w themselves
                    cw = len(N & sN)
                    if flag and cw != 1:
                        continue
                    M1 = [[9 * (3 * (u == v) - A[u][v]) + 1 for v in range(n)] for u in range(n)]
                    M2 = [[11 * (4 * (u == v) + A[u][v]) - 2 for v in range(n)] for u in range(n)]
                    if neg_certificate(M1) is not None or neg_certificate(M2) is not None:
                        continue
                    st[1] += 1
                    c = [(1 if i in Np else 0) - (1 if i in Nm else 0) for i in range(9)]
                    if use_lattice:
                        GW = [row[:] + [-c[i]] for i, row in enumerate(GT)]
                        GW.append([-x for x in c] + [4 if flag else 3])
                        r = lattice_test(GW, [1] * 9 + [0], 0)
                        if r is not None and r[0] != "degenerate":
                            continue
                    st[2] += 1
                    if (Np, Nm) <= (Nm, Np):
                        st[3] += 1
                    good.append((Np, Nm, flag))
    return good, stats


if __name__ == "__main__":
    out = {}
    for case in res:
        if not case["survivors"]:
            continue
        h = case["h"]
        for idx, m in enumerate(case["survivors"]):
            good, stats = types_for(m, h)
            name = f"{case['name']} #{idx}"
            print("=" * 60)
            print(name)
            print("  (d, adjacent to inf): [pass graph filters G, pass G+PSD, pass G+PSD+lattice(H16), sigma-classes of the last]")
            for key in sorted(stats):
                print("   ", key, stats[key])
            out[name] = [[list(a), list(b), f] for a, b, f in good]
            sys.stdout.flush()
    json.dump(out, open(os.path.join(here, "types.json"), "w"))
