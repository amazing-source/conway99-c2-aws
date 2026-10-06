# Independent re-enumeration of the S-structures (different algorithm from enum_S.py: row by row with
# itertools.combinations on the 18(+1)-vertex graph, NO symmetry breaking except the position of the
# plus edges and of the h orbits), followed by an independent canonical form (minimum over all 9! orbit
# permutations is too slow, so we use the class invariants + the iso test of enum_S only for counting).
# Purpose: confirm the counts 0 for e(S+) = 1, 2 and the numbers of classes for e(S+) = 0.
import itertools, sys, json, datetime
from enum_S import dedupe, mat_of, PAIRS

def run(name, plus_edges, h, both_allowed=True):
    hs = set(h)
    plus = set(plus_edges)
    pdeg = [0] * 9
    for i, j in plus:
        pdeg[i] += 1; pdeg[j] += 1
    target = [pdeg[i] + 4 - (i in hs) for i in range(9)]
    sols = []
    # N[i] = set of j with a minus edge between orbits i and j (symmetric relation)
    N = [set() for _ in range(9)]

    def adjacency():
        adj = [set() for _ in range(19)]
        def add(u, v):
            adj[u].add(v); adj[v].add(u)
        for i in range(9):
            for j in N[i]:
                add(i, 9 + j)
        for i, j in plus:
            add(i, j); add(9 + i, 9 + j)
        for i in hs:
            add(i, 9 + i); add(18, i); add(18, 9 + i)
        return adj

    def valid(final):
        adj = adjacency()
        for u in range(19):
            for v in range(u + 1, 19):
                c = len(adj[u] & adj[v])
                if c > 2: return False
                if v in adj[u] and c > 1: return False
        return True

    def rec(i):
        if i == 9:
            if valid(True):
                st = {}
                for (a, b) in PAIRS:
                    st[(a, b)] = (1 if b in N[a] else 0) + (2 if ((a, b) in plus) else 0)
                sols.append(st)
            return
        have = set(N[i])              # minus neighbours already decided by earlier rows (all < i)
        need = target[i] - len(have)
        if need < 0: return
        cand = []
        for j in range(i + 1, 9):
            if i in hs and j in hs: continue                      # two h orbits are never joined
            p = (i, j)
            if p in plus and (i in hs or j in hs): continue        # x never adjacent to both a_c and b_c
            if p in plus and not both_allowed: continue
            if len(N[j]) >= target[j]: continue
            cand.append(j)
        for comb in itertools.combinations(cand, need):
            for j in comb:
                N[i].add(j); N[j].add(i)
            if valid(False):
                rec(i + 1)
            for j in comb:
                N[i].discard(j); N[j].discard(i)

    rec(0)
    reps = dedupe(sols, h)
    print(f"{name}: labelled {len(sols)}, iso classes {len(reps)}")
    sys.stdout.flush()
    return reps

if __name__ == "__main__":
    print(datetime.datetime.now())
    r = {}
    r["(i) e=1"] = run("(i) e=1  plus edge (0,1)", [(0, 1)], ())
    r["(ii) e=1 ww"] = run("(ii) e=1 plus edge word-word (0,1), h={7,8}", [(0, 1)], (7, 8))
    r["(ii) e=1 wh"] = run("(ii) e=1 plus edge word-h (0,7), h={7,8}", [(0, 7)], (7, 8))
    r["(i) e=2 d"] = run("(i) e=2 disjoint plus edges", [(0, 1), (2, 3)], ())
    r["(i) e=2 p"] = run("(i) e=2 path of plus edges", [(0, 1), (1, 2)], ())
    r["(ii) e=2 a"] = run("(ii) e=2 ww,ww disjoint", [(0, 1), (2, 3)], (7, 8))
    r["(ii) e=2 b"] = run("(ii) e=2 ww + wh disjoint", [(0, 1), (2, 7)], (7, 8))
    r["(ii) e=2 c"] = run("(ii) e=2 wh + wh disjoint", [(0, 7), (1, 8)], (7, 8))
    r["(ii) e=0"] = run("(ii) e=0 h={7,8}", [], (7, 8))
    r["(i) e=0"] = run("(i) e=0", [], ())
    print(datetime.datetime.now())
