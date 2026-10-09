"""Microscopic study, step 7: test of LEMMA 2 (two pure lines) on all processed supports.
Lemma 2.  If a positive p has two lines {p, x1, x2}, {p, x3, x4} inside the support whose four N-points are adjacent to p only,
then  c(p,a) + c(p,b) - c(a,b) >= 2,  where a, b are the two other positives and c(.,.) counts common neighbours inside N."""
import json, glob, itertools, pickle, collections
reg = {}
for line in open("register/supports_open_4581.jsonl", encoding="utf-8"):
    d = json.loads(line); reg[d["id"]] = d
res = {}
for f in glob.glob("phaseA/chunk_*.jsonl"):
    for l in open(f):
        rr = json.loads(l); res[rr["id"]] = rr["status"]
m4 = pickle.load(open("micro4.pkl", "rb"))
def lemma2(d):
    adj = [set() for _ in range(28)]
    for a, b in d["edges"]: adj[a].add(b); adj[b].add(a)
    P = [0, 1, 2]
    c = {frozenset(pq): len(adj[pq[0]] & adj[pq[1]]) for pq in itertools.combinations(P, 2)}
    out = []
    for p in P:
        pure = [(x, w) for x in adj[p] for w in adj[p] if x < w and w in adj[x] and all(q not in adj[x] and q not in adj[w] for q in P if q != p)]
        a, b = [q for q in P if q != p]
        val = c[frozenset((p, a))] + c[frozenset((p, b))] - c[frozenset((a, b))]
        out.append((len(pure), val))
    return out
viol_dead = viol_alive = 0; dead = [s for s in res if res[s] == "infeasible"]; alive = [s for s in res if res[s] == "feasible"]
exp1 = {s for s in dead if s in m4 and m4[s][1][0] > 71}
exp2 = set()
for s in dead:
    if any(n >= 2 and v < 2 for n, v in lemma2(reg[s])): exp2.add(s)
for s in alive:
    if any(n >= 2 and v < 2 for n, v in lemma2(reg[s])): viol_alive += 1
print(f"processed: {len(res)}; dead: {len(dead)}; explained by Lemma 1 (pigeonhole): {len(exp1)}; by Lemma 2 (two pure lines): {len(exp2)}; by one of them: {len(exp1 | exp2)}")
print(f"survivors violating Lemma 2 (must be 0): {viol_alive}")
rest = sorted(set(dead) - exp1 - exp2); print("still unexplained:", len(rest), rest[:40])
pickle.dump(rest, open("micro_rest.pkl", "wb"))
