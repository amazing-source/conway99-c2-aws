# Print the surviving S-structures (e(S+) = 0) with exact invariants.
import json, itertools, os
import sympy as sp
here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
for case in res:
    if not case["survivors"]:
        continue
    h = case["h"]
    print("=" * 70)
    print(case["name"], " h orbits:", h)
    for idx, m in enumerate(case["survivors"]):
        B = sp.Matrix(9, 9, lambda i, j: 1 if (m[i][j] & 1) else 0)
        edges = [(i, j) for i in range(9) for j in range(i + 1, 9) if m[i][j] & 1]
        # automorphisms (orbit permutations preserving B and h flags)
        aut = 0
        for p in itertools.permutations(range(9)):
            if any((p[i] in h) != (i in h) for i in range(9)):
                continue
            if all(m[p[i]][p[j]] == m[i][j] for i, j in edges) :
                aut += 1
        lam = sp.symbols("t")
        cp = sp.factor(B.charpoly(lam).as_expr())
        tri = sum(1 for a, b, c in itertools.combinations(range(9), 3) if m[a][b] & 1 and m[a][c] & 1 and m[b][c] & 1)
        codeg = {}
        for i in range(9):
            for j in range(i + 1, 9):
                c = sum(1 for k in range(9) if m[i][k] & 1 and m[j][k] & 1)
                key = ("adj" if m[i][j] & 1 else "non", c)
                codeg[key] = codeg.get(key, 0) + 1
        print(f"--- structure #{idx}: minus edges (i~j iff x_i ~ sigma x_j): {edges}")
        print(f"    degrees {[sum(1 for j in range(9) if m[i][j] & 1) for i in range(9)]}, |Aut| = {aut}, triangles of B = {tri}")
        print(f"    charpoly(B) = {cp}")
        print(f"    codegree distribution (adjacency, codeg): count = {sorted(codeg.items())}")
