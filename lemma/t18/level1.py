# Level 1: is there a sigma-closed family of outside-vertex types (neighbourhoods in Base = S u {inf})
# giving EXACTLY the right number of common neighbours to every pair of Base ?
# Exhaustive DFS (exact cover with multiplicities), stops at the first solution, or proves there is none.
# Types come from types.json (rows.py: graph filters G1-G4 + exact PSD; the lattice filter removed nothing more).
# usage: python level1.py <case> <structure> [time limit s]
import json, os, sys, itertools, time
from rows import base_adj

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
ci, si = int(sys.argv[1]), int(sys.argv[2])
tlimit = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
case = res[ci]; m = case["survivors"][si]; h = case["h"]
name = f"{case['name']} #{si}"
adj = base_adj(m, h)
INF = 18


def need(s, t):
    return (1 if t in adj[s] else 2) - len(adj[s] & adj[t])


# points to cover exactly: same-side pairs (x_i, x_j) and pairs (inf, x_i)
ss_need = {}
for i in range(9):
    for j in range(i + 1, 9):
        ss_need[(i, j)] = need(i, j)
inf_need = {i: need(INF, i) for i in range(9)}
cross_need = {(i, j): need(i, 9 + j) for i in range(9) for j in range(9)}
assert all(v >= 0 for v in ss_need.values()) and all(v >= 0 for v in inf_need.values())
assert all(v >= 0 for v in cross_need.values())
print(name)
print("  same-side needs: total", sum(ss_need.values()), " distribution",
      {k: sum(1 for v in ss_need.values() if v == k) for k in (0, 1, 2)})
print("  inf needs:", inf_need)

# sigma-orbits of 'big' types
orbits = []
seen = set()
for Np, Nm, flag in types[name]:
    Np, Nm = tuple(Np), tuple(Nm)
    d = len(Np)
    if (flag == 0 and d < 2) or (flag == 1 and d < 1):
        continue
    key = (min((Np, Nm), (Nm, Np)), flag)
    if key in seen:
        continue
    seen.add(key)
    Np, Nm = key[0]
    ss = [p for p in itertools.combinations(Np, 2)] + [p for p in itertools.combinations(Nm, 2)]
    infp = list(Np + Nm) if flag else []
    cross = [(i, j) for i in Np for j in Nm] + [(j, i) for i in Np for j in Nm]
    N1 = frozenset(Np) | frozenset(9 + j for j in Nm) | (frozenset([INF]) if flag else frozenset())
    N2 = frozenset(Nm) | frozenset(9 + j for j in Np) | (frozenset([INF]) if flag else frozenset())
    orbits.append({"Np": Np, "Nm": Nm, "flag": flag, "ss": ss, "inf": infp, "cross": cross, "N": (N1, N2)})
print("  sigma-orbits of big types:", len(orbits))
by_point = {}
for k, o in enumerate(orbits):
    for p in o["ss"]:
        by_point.setdefault(("ss", p), []).append(k)
    for i in o["inf"]:
        by_point.setdefault(("inf", i), []).append(k)

t0 = time.time()
nodes = 0
found = None
timed_out = False
chosen = []


def compat(o, o2):
    for a in o["N"]:
        for b in o2["N"]:
            if len(a & b) > 2:
                return False
    return True


def rec():
    global nodes, found, timed_out
    if found is not None or timed_out:
        return
    nodes += 1
    if nodes % 20000 == 0 and time.time() - t0 > tlimit:
        timed_out = True
        return
    # most constrained uncovered point
    best = None; bestc = None
    for p, v in ss_need.items():
        if v > 0:
            cands = [k for k in by_point.get(("ss", p), []) if fits(k)]
            if best is None or len(cands) < len(bestc):
                best, bestc = ("ss", p), cands
                if not cands:
                    return
    for i, v in inf_need.items():
        if v > 0:
            cands = [k for k in by_point.get(("inf", i), []) if fits(k)]
            if best is None or len(cands) < len(bestc):
                best, bestc = ("inf", i), cands
                if not cands:
                    return
    if best is None:
        # all exact needs met; singles fill the cross needs; count vertices
        n_big = 2 * len(chosen)
        n_single = sum(cross_need.values())
        n_infflag = 14 - len(adj[INF])
        n_inf_used = 2 * sum(1 for k in chosen if orbits[k]["flag"])
        n0 = 80 - (n_big - n_inf_used) - n_single - n_infflag
        if n_inf_used <= n_infflag and n0 >= 0:
            found = (list(chosen), n_single, n0)
        return
    for k in bestc:
        o = orbits[k]
        apply(o, -1)
        chosen.append(k)
        rec()
        chosen.pop()
        apply(o, +1)
        if found is not None or timed_out:
            return


def fits(k):
    o = orbits[k]
    if k in chosen:
        return False
    cnt = {}
    for p in o["ss"]:
        cnt[p] = cnt.get(p, 0) + 1
    for p, c in cnt.items():
        if ss_need[p] < c:
            return False
    for i in o["inf"]:
        if inf_need[i] < 1:
            return False
    cc = {}
    for p in o["cross"]:
        cc[p] = cc.get(p, 0) + 1
    for p, c in cc.items():
        if cross_need[p] < c:
            return False
    for k2 in chosen:
        if not compat(o, orbits[k2]):
            return False
    return True


def apply(o, sgn):
    for p in o["ss"]:
        ss_need[p] += sgn
    for i in o["inf"]:
        inf_need[i] += sgn
    for p in o["cross"]:
        cross_need[p] += sgn


rec()
print(f"  nodes {nodes}, time {time.time() - t0:.1f}s, timed_out={timed_out}")
if found:
    ch, ns, n0 = found
    print("  LEVEL-1 SOLUTION EXISTS.  big orbits (N+, N-, adjacent to inf):")
    for k in ch:
        print("     ", orbits[k]["Np"], orbits[k]["Nm"], orbits[k]["flag"])
    print(f"  then {ns} vertices with d = 1 fill the cross pairs, {n0} vertices (inf excluded) have no neighbour in S and are not in N(inf)")
elif not timed_out:
    print("  NO LEVEL-1 SOLUTION (exhaustive).")
