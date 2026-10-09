"""THE CAP LEMMA and its test.

Lemma.  Let u, v be two vertices of S and X a set of neighbours of v inside S, u not in X.  An outside vertex z adjacent to u has
at most 2 common neighbours with v if z is not adjacent to v, exactly 1 if it is.  Hence
   u not adjacent to v:   sum_{x in X} r(u, x)  <=  2 (dZ(u) - r(u,v)) + min( r(u,v), #{x in X : r(v, x) = 1} ),
   u adjacent to v:       sum_{x in X} r(u, x)  <=  dZ(u) - r(u,v)                (u itself is one of the common neighbours).
(The left side counts the pairs (z, x), z outside adjacent to u, x in X adjacent to z.)
Test: among the killed supports without parabola witness, which have a violated cap inequality?  And none among the survivors."""
import json, glob, pickle, itertools
import p3n25_ilp as I
reg = {}
for line in open("register/supports_open_4581.jsonl", encoding="utf-8"):
    d = json.loads(line); reg[d["id"]] = d
res = {}
for f in glob.glob("phaseA/chunk_*.jsonl"):
    for l in open(f):
        rr = json.loads(l); res[rr["id"]] = rr["status"]
par = pickle.load(open("parabola_dead.pkl", "rb"))
def cap_violation(d):
    adj, r, dZ = I.boundary(d["edges"])
    best = None
    for v in range(28):
        for u in range(28):
            if u == v: continue
            X = [x for x in range(28) if (adj[v] >> x) & 1 and x != u and r[u][x] > 0]
            lhs = sum(r[u][x] for x in X)
            if (adj[u] >> v) & 1: rhs = dZ[u] - r[u][v]
            else: rhs = 2 * (dZ[u] - r[u][v]) + min(r[u][v], sum(1 for x in X if r[v][x] == 1))
            if lhs > rhs and (best is None or lhs - rhs > best[0]): best = (lhs - rhs, u, v, X)
    return best
dead = sorted(s for s in res if res[s] == "infeasible"); alive = sorted(s for s in res if res[s] == "feasible")
unexpl = [s for s in dead if s not in par or par[s][0] >= 0]
capv = {s: cap_violation(reg[s]) for s in dead}
both = [s for s in dead if capv[s] and s in par and par[s][0] < 0]
print(f"killed: {len(dead)}; parabola witness: {sum(1 for s in dead if s in par and par[s][0] < 0)}; cap violation: {sum(1 for s in dead if capv[s])}; both: {len(both)}")
rest = [s for s in unexpl if not capv[s]]
print(f"killed supports explained by neither: {len(rest)}: {rest[:40]}")
bad = sum(1 for s in alive if cap_violation(reg[s]))
print(f"survivors: {len(alive)}; cap violations among them (must be 0): {bad}")
import collections
print("pairs (u, v) used: u positive / v positive:", collections.Counter((capv[s][1] < 3, capv[s][2] < 3) for s in dead if capv[s]))
pickle.dump(rest, open("micro_rest2.pkl", "wb"))
