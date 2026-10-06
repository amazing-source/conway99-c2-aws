# Level 1, complete enumeration (with a time limit) of the sigma-closed families of outside types for one structure,
# followed by test F1 on each solution:
#   F1: for every i, the 6 outside neighbours of x_i that are not the third vertex of a triangle x_i y_j w
#       must be perfectly matched into 3 adjacent pairs {v, v'}; an adjacent pair has x_i as its ONLY common neighbour,
#       so v, v' may not share any other neighbour in Base = S u {inf}.
# usage: python level1_count.py <case> <structure> [time limit s]
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
Bn = [set(j for j in range(9) if j != i and m[i][j] & 1) for i in range(9)]


def need(s, t):
    return (1 if t in adj[s] else 2) - len(adj[s] & adj[t])


ss_need = {(i, j): need(i, j) for i in range(9) for j in range(i + 1, 9)}
inf_need = {i: need(INF, i) for i in range(9)}
cross_need = {(i, j): need(i, 9 + j) for i in range(9) for j in range(9)}

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
    ss = list(itertools.combinations(Np, 2)) + list(itertools.combinations(Nm, 2))
    infp = list(Np + Nm) if flag else []
    cross = [(i, j) for i in Np for j in Nm] + [(j, i) for i in Np for j in Nm]
    N1 = frozenset(Np) | frozenset(9 + j for j in Nm) | (frozenset([INF]) if flag else frozenset())
    N2 = frozenset(Nm) | frozenset(9 + j for j in Np) | (frozenset([INF]) if flag else frozenset())
    orbits.append({"Np": Np, "Nm": Nm, "flag": flag, "ss": ss, "inf": infp, "cross": cross, "N": (N1, N2)})
by_point = {}
for k, o in enumerate(orbits):
    for p in set(o["ss"]):
        by_point.setdefault(("ss", p), []).append(k)
    for i in set(o["inf"]):
        by_point.setdefault(("inf", i), []).append(k)
ncomp = len(orbits)
COMP = [[all(len(a & b) <= 2 for a in orbits[k]["N"] for b in orbits[l]["N"]) for l in range(ncomp)] for k in range(ncomp)]

t0 = time.time()
nodes = 0
timed_out = False
chosen = []
solutions = set()
stats = {"solutions": 0, "F1_fail": 0, "F1_pass": 0}
examples = []


def fits(k):
    o = orbits[k]
    if k in chosen:
        return False
    for p in o["ss"]:
        if ss_need[p] < o["ss"].count(p):
            return False
    for i in o["inf"]:
        if inf_need[i] < 1:
            return False
    for p in o["cross"]:
        if cross_need[p] < o["cross"].count(p):
            return False
    for k2 in chosen:
        if not COMP[k][k2]:
            return False
    return True


def apply(o, sgn):
    for p in o["ss"]:
        ss_need[p] += sgn
    for i in o["inf"]:
        inf_need[i] += sgn
    for p in o["cross"]:
        cross_need[p] += sgn


def perfect_matching(vs, ok):
    if not vs:
        return True
    a = vs[0]
    for t in range(1, len(vs)):
        b = vs[t]
        if ok(a, b):
            if perfect_matching(vs[1:t] + vs[t + 1:], ok):
                return True
    return False


def F1():
    # all outside vertices with their Base neighbourhoods
    verts = []
    for k in chosen:
        verts.append(orbits[k]["N"][0]); verts.append(orbits[k]["N"][1])
    for (i, j), r in cross_need.items():
        for _ in range(r):
            verts.append(frozenset([i, 9 + j]))
    for i in range(9):
        nb = [N for N in verts if i in N]
        if len(nb) != 14 - len(adj[i]):
            return False
        free = [N for N in nb if not any((9 + j) in N for j in Bn[i])]
        if len(free) != 6:
            return False
        if not perfect_matching(free, lambda a, b: len(a & b) == 1):
            return False
    return True


def rec():
    global nodes, timed_out
    if timed_out:
        return
    nodes += 1
    if nodes % 5000 == 0 and time.time() - t0 > tlimit:
        timed_out = True
        return
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
        key = frozenset(chosen)
        if key in solutions:
            return
        solutions.add(key)
        n_infflag = 14 - len(adj[INF])
        n_inf_used = 2 * sum(1 for k in chosen if orbits[k]["flag"])
        n0 = 80 - (2 * len(chosen) - n_inf_used) - sum(cross_need.values()) - n_infflag
        if n_inf_used > n_infflag or n0 < 0:
            return
        stats["solutions"] += 1
        if F1():
            stats["F1_pass"] += 1
            if len(examples) < 3:
                examples.append([(orbits[k]["Np"], orbits[k]["Nm"], orbits[k]["flag"]) for k in chosen])
        else:
            stats["F1_fail"] += 1
        return
    for k in bestc:
        o = orbits[k]
        apply(o, -1)
        chosen.append(k)
        rec()
        chosen.pop()
        apply(o, +1)
        if timed_out:
            return


rec()
print(f"{name}: nodes {nodes}, time {time.time() - t0:.1f}s, timed_out={timed_out}, stats {stats}")
for e in examples:
    print("   example passing F1:", e)
