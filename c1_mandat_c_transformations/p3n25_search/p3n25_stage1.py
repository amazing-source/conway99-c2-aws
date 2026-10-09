"""P3/N25, STAGE 1: the 71 outside vertices around one support, as an exact design problem (CP-SAT).

Unknown: a[z][s] = 1 if the outside vertex z (z = 0..70) is adjacent to s in S.  Exact conditions (necessary for an srg(99,14,1,2)
in which 2/9 + 1_P - 1_N is a (-4)-eigenvector):
  (1) for every z:  (number of neighbours in N) - (number in P) = 4;
  (2) the S-neighbours of z induce a partial matching (the neighbourhood of a vertex is 7 K_2);
  (3) every pair {s, s'} of S has exactly r(s, s') common neighbours outside S;
  (4) every s has exactly dZ(s) neighbours outside S;
  (5) two outside vertices have at most 2 common neighbours in S.
Rows are ordered lexicographically to break the symmetry of the 71 outside vertices.
The solver's answer is re-checked here from the returned matrix when it is 'feasible'.  An 'infeasible' answer is a solver
verdict only: it is NOT a proof until it is certified independently.
usage: p3n25_stage1.py supports.jsonl index [time_limit_s] [workers] [nolex] [no5]"""
import sys, json, time, itertools
from ortools.sat.python import cp_model
import p3n25_support as PS

fn, idx = sys.argv[1], int(sys.argv[2])
TL = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
WK = int(sys.argv[4]) if len(sys.argv) > 4 else 8
OPT = set(sys.argv[5:])
d = json.loads(open(fn).read().splitlines()[idx])
adj = [set() for _ in range(28)]
for a, b in d["edges"]: adj[a].add(b); adj[b].add(a)
data = PS.check(adj); assert data is not None
r, dZ = data["r"], data["dZ"]
S = list(range(28)); P = [0, 1, 2]; N = list(range(3, 28)); NZ = 71
assert sum(dZ.values()) == 320
print(f"support {idx}: t = {d['t']}, delta = {d['delta']}, u = {d['u']};  pairs with r = 0/1/2: "
      f"{sum(1 for v in r.values() if v == 0)}/{sum(1 for v in r.values() if v == 1)}/{sum(1 for v in r.values() if v == 2)}", flush=True)
m = cp_model.CpModel()
a = [[m.NewBoolVar(f"a{z}_{s}") for s in S] for z in range(NZ)]
for z in range(NZ):
    m.Add(sum(a[z][s] for s in N) - sum(a[z][s] for s in P) == 4)                       # (1)
    for s in S:                                                                        # (2)
        for s1, s2 in itertools.combinations(sorted(adj[s]), 2):
            m.AddBoolOr([a[z][s].Not(), a[z][s1].Not(), a[z][s2].Not()])
for s in S: m.Add(sum(a[z][s] for z in range(NZ)) == dZ[s])                              # (4)
for (s, t), val in r.items():                                                            # (3)
    if val == 0:
        for z in range(NZ): m.AddBoolOr([a[z][s].Not(), a[z][t].Not()])
    else:
        ys = []
        for z in range(NZ):
            y = m.NewBoolVar(""); m.AddBoolAnd([a[z][s], a[z][t]]).OnlyEnforceIf(y); m.AddBoolOr([a[z][s].Not(), a[z][t].Not(), y]); ys.append(y)
        m.Add(sum(ys) == val)
if "no5" not in OPT:                                                                     # (5)
    for z1, z2 in itertools.combinations(range(NZ), 2):
        ws = []
        for s in S:
            w = m.NewBoolVar(""); m.AddBoolAnd([a[z1][s], a[z2][s]]).OnlyEnforceIf(w); m.AddBoolOr([a[z1][s].Not(), a[z2][s].Not(), w]); ws.append(w)
        m.Add(sum(ws) <= 2)
if "nolex" not in OPT:                                                                   # rows in decreasing lexicographic order
    for z in range(NZ - 1):
        eq = m.NewConstant(1)                                                            # prefix equal so far
        for s in S:
            # if prefix equal: a[z][s] >= a[z+1][s]
            m.AddImplication(a[z + 1][s], a[z][s]).OnlyEnforceIf(eq)
            neq = m.NewBoolVar("")
            # neq = eq and (a[z][s] == a[z+1][s])
            same = m.NewBoolVar("")
            m.Add(a[z][s] == a[z + 1][s]).OnlyEnforceIf(same); m.Add(a[z][s] != a[z + 1][s]).OnlyEnforceIf(same.Not())
            m.AddBoolAnd([eq, same]).OnlyEnforceIf(neq); m.AddBoolOr([eq.Not(), same.Not(), neq])
            eq = neq
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = TL; solver.parameters.num_search_workers = WK
t0 = time.time(); st = solver.Solve(m); el = time.time() - t0
name = solver.StatusName(st)
print(f"stage 1: {name} in {el:.1f} s  (limit {TL:.0f} s, {WK} workers; conflicts {solver.NumConflicts()}, branches {solver.NumBranches()})", flush=True)
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    M = [[int(solver.Value(a[z][s])) for s in S] for z in range(NZ)]
    # independent re-check of the returned matrix
    ok = all(sum(M[z][s] for s in N) - sum(M[z][s] for s in P) == 4 for z in range(NZ))
    ok &= all(sum(M[z][s] for z in range(NZ)) == dZ[s] for s in S)
    ok &= all(sum(M[z][s] * M[z][t] for z in range(NZ)) == val for (s, t), val in r.items())
    for z in range(NZ):
        B = [s for s in S if M[z][s]]
        ok &= all(len(adj[s] & set(B)) <= 1 for s in B)
    ok &= all(sum(M[z1][s] * M[z2][s] for s in S) <= 2 for z1, z2 in itertools.combinations(range(NZ), 2))
    sizes = sorted(sum(row) for row in M)
    print(f"   re-check of the solution: {ok};  block sizes: { {k: sizes.count(k) for k in sorted(set(sizes))} }")
    json.dump({"support": idx, "edges": d["edges"], "blocks": M}, open(f"stage1_sol_{idx}.json", "w"))
