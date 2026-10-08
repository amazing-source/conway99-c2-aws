"""Lemma (I): a 7-torsion vector carried by ONE (6,6) component of girth >= 5 is never balanced.
(September note 126 par.3 bis states it with the check x32; re-done here independently.)
A far vertex meets the component C in an admissible triple (at most two points per layer, no two mates, at most one
edge of G, no vertex of C adjacent to all three); a pair {x, y} of C lies in exactly K[x][y] such triples (K = number of
common far neighbours: 0 for mates, 1 for the same layer, adjacent or at distance 2, 2 otherwise), and two far vertices
have different triples.  If phi is balanced every one of these triples has phi-sum 0 mod 7.  So for every pair we need at
least K[x][y] admissible triples of phi-sum 0 containing it.  Prints, for every phi up to a scalar, the number of pairs
in default."""
import json, itertools
from star66 import build_comp
from gen66 import nullspace7

types = json.load(open("comp66_types.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
for idx, t in enumerate(types):
    if t["torsion"] == 0: continue
    adj = build_comp(key(t)); lay = [v // 6 for v in range(18)]
    mate = [next(z for z in adj[v] if lay[z] == lay[v]) for v in range(18)]
    def K(x, y):
        if mate[x] == y: return 0
        if lay[x] == lay[y] or y in adj[x]: return 1
        return 2 - len(adj[x] & adj[y])
    triples = []
    for tr in itertools.combinations(range(18), 3):
        s = set(tr)
        if len({lay[v] for v in tr}) == 1: continue
        if any(mate[a] in s for a in tr): continue
        if sum(1 for a, b in itertools.combinations(tr, 2) if b in adj[a]) > 1: continue
        if any(s <= adj[x] for x in range(18)): continue
        triples.append(tr)
    H = [[((3 if a == b else 0) - (1 if b in adj[a] else 0)) % 7 for b in range(18)] for a in range(18)]
    ns = nullspace7(H); basis = []
    for v in ns:
        m = (sum(v) * pow(4, -1, 7)) % 7
        w = [(x - m) % 7 for x in v]
        if any(w) and len(nullspace7([list(c) for c in zip(*(basis + [w]))])) == 0: basis.append(w)
    assert len(basis) == t["torsion"]
    seen = set(); worst = None; nphi = 0
    for coef in itertools.product(range(7), repeat=len(basis)):
        if not any(coef): continue
        lead = next(c for c in coef if c)
        if lead != 1: continue                      # up to a scalar
        phi = [sum(c * b[v] for c, b in zip(coef, basis)) % 7 for v in range(18)]
        nphi += 1
        zero = [tr for tr in triples if sum(phi[v] for v in tr) % 7 == 0]
        bad = 0
        for x, y in itertools.combinations(range(18), 2):
            if sum(1 for tr in zero if x in tr and y in tr) < K(x, y): bad += 1
        worst = bad if worst is None else min(worst, bad)
    print(f"type {idx} (torsion rank {t['torsion']}): {len(triples)} admissible triples, {nphi} vectors up to a scalar, "
          f"minimum number of pairs in default = {worst}")
