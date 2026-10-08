"""Lemma I for every triangle-free ordered type with three lines per layer and 7-torsion (with or without type-I
4-cycle): a torsion vector carried by one component is never balanced.  Same pair test as balanced66.py, with
K[x][y] = 0 allowed (two common neighbours).  Prints the types for which the test does NOT conclude."""
import json, itertools
from multi import build
from gen66 import nullspace7
types = json.load(open("comp_m3_all.json")); bad = []; stats = {}
for idx, t in enumerate(types):
    if t["torsion"] == 0: continue
    key = tuple(tuple(x) for x in t["key"]); adj = build(key); lay = [v // 6 for v in range(18)]
    mate = [next(z for z in adj[v] if lay[z] == lay[v]) for v in range(18)]
    def K(x, y):
        if mate[x] == y: return 0
        if lay[x] == lay[y] or y in adj[x]: return 1
        return 2 - len(adj[x] & adj[y])
    triples = []
    for tr in itertools.combinations(range(18), 3):
        s = set(tr)
        if len({lay[v] for v in tr}) == 1: continue
        if any(K(a, b) == 0 for a, b in itertools.combinations(tr, 2)): continue
        if sum(1 for a, b in itertools.combinations(tr, 2) if b in adj[a]) > 1: continue
        if any(s <= adj[x] for x in range(18)): continue
        triples.append(tr)
    H = [[((3 if a == b else 0) - (1 if b in adj[a] else 0)) % 7 for b in range(18)] for a in range(18)]
    basis = []
    for v in nullspace7(H):
        m = (sum(v) * pow(4, -1, 7)) % 7; w = [(x - m) % 7 for x in v]
        if any(w) and len(nullspace7([list(c) for c in zip(*(basis + [w]))])) == 0: basis.append(w)
    assert len(basis) == t["torsion"]
    worst = None
    for coef in itertools.product(range(7), repeat=len(basis)):
        if not any(coef) or next(c for c in coef if c) != 1: continue
        phi = [sum(c * b[v] for c, b in zip(coef, basis)) % 7 for v in range(18)]
        zero = [tr for tr in triples if sum(phi[v] for v in tr) % 7 == 0]
        d = sum(1 for x, y in itertools.combinations(range(18), 2) if sum(1 for tr in zero if x in tr and y in tr) < K(x, y))
        worst = d if worst is None else min(worst, d)
    stats.setdefault((t["typeI"], t["torsion"]), []).append(worst)
    if worst == 0: bad.append(idx)
for k, v in sorted(stats.items()): print(f"typeI {k[0]} torsion rank {k[1]}: {len(v)} types, minimum number of pairs in default over all vectors: min {min(v)} max {max(v)}")
print("types where the pair test does not exclude a balanced vector:", bad)
