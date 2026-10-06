# Round 2, stage 1 (case n_3 = 0): matchings of the 18 deficient pairs.
# A deficient pair is {i,j} with (B^2)_ij = 1; each X_2 vertex sees a deficient pair U in S+ and a deficient pair V in S-,
# its mate sees V in S+ and U in S-.  The 9 sigma-orbits of X_2 form a perfect matching tau of the 18 deficient pairs.
# Tests (Wagner note section 3):
#   (i)   every row and column of B[U,V] has at most one 1   (lambda = 1 between the X_2 vertex and a support vertex)
#   (i')  |U n V| <= 1                                        (z, sigma z have at most 2 common neighbours)
#   (iii) cell budgets: number of rectangles on the cell (i,j) at most 2 - B_ij (2 on the diagonal)
#   (P)   the type (U;V) passes the exact PSD test of rows.py (types.json), as an outer vertex or as a vertex of N(p)
# (ii) "two rectangles share at most 2 support neighbours" is automatic for distinct deficient pairs.
# Output: number of matchings, number of orbits under Aut(B), saved to r2_tau_<s>.json
# usage: python r2_stage1.py <structure index>
import json, os, sys, itertools, time

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si = int(sys.argv[1])
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
B = [[1 if (m[i][j] & 1) else 0 for j in range(9)] for i in range(9)]
Bn = [set(j for j in range(9) if B[i][j]) for i in range(9)]
codeg = lambda a, b: len(Bn[a] & Bn[b])
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if codeg(a, b) == 1]
assert all(codeg(a, b) in (1, 2) for a in range(9) for b in range(a + 1, 9))
print(name, "deficient pairs:", len(DEF), DEF)
AT = set()
for Np, Nm, flag in types[name]:
    if len(Np) == 2:
        AT.add((tuple(Np), tuple(Nm)))

def rect_ok(U, V):
    if len(set(U) & set(V)) > 1:
        return False
    for i in U:
        if sum(B[i][j] for j in V) > 1:
            return False
    for j in V:
        if sum(B[i][j] for i in U) > 1:
            return False
    return (U, V) in AT

n = len(DEF)
OK = [[rect_ok(DEF[a], DEF[b]) and rect_ok(DEF[b], DEF[a]) for b in range(n)] for a in range(n)]
print("admissible unordered rectangles {U,V}:", sum(OK[a][b] for a in range(n) for b in range(a + 1, n)))

# automorphisms of B
auts = []
for p in itertools.permutations(range(9)):
    if all(B[p[i]][p[j]] == B[i][j] for i in range(9) for j in range(i + 1, 9)):
        auts.append(p)
print("|Aut(B)| =", len(auts))
idx = {d: k for k, d in enumerate(DEF)}
aut_on_def = [[idx[tuple(sorted((p[a], p[b])))] for (a, b) in DEF] for p in auts]

budget = [[2 - B[i][j] for j in range(9)] for i in range(9)]
sols = []
tau = [-1] * n
t0 = time.time()

def use(a, b, sgn):
    U, V = DEF[a], DEF[b]
    for i in U:
        for j in V:
            budget[i][j] -= sgn
            budget[j][i] -= sgn

def fits(a, b):
    U, V = DEF[a], DEF[b]
    cnt = {}
    for i in U:
        for j in V:
            cnt[(i, j)] = cnt.get((i, j), 0) + 1
            cnt[(j, i)] = cnt.get((j, i), 0) + 1
    return all(budget[i][j] >= c for (i, j), c in cnt.items())

def rec():
    try:
        a = tau.index(-1)
    except ValueError:
        sols.append(tuple(tau))
        return
    for b in range(a + 1, n):
        if tau[b] == -1 and OK[a][b] and fits(a, b):
            tau[a] = b; tau[b] = a
            use(a, b, 1)
            rec()
            use(a, b, -1)
            tau[a] = -1; tau[b] = -1

rec()
print(f"admissible matchings tau: {len(sols)}   ({time.time() - t0:.1f}s)")
# orbits under Aut(B)
seen = set(); reps = []
for s in sols:
    if s in seen:
        continue
    reps.append(s)
    for g in aut_on_def:
        img = [0] * n
        for a in range(n):
            img[g[a]] = g[s[a]]
        seen.add(tuple(img))
print("orbits under Aut(B):", len(reps))
json.dump({"name": name, "DEF": DEF, "n_tau": len(sols), "reps": reps},
          open(os.path.join(here, f"r2_tau_{si}.json"), "w"))
