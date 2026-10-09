"""Microscopic study, step 1: which support features separate the supports killed by the linear screen from the survivors?"""
import json, glob, collections, itertools
reg = {}
for line in open("register/supports_open_4581.jsonl", encoding="utf-8"):
    d = json.loads(line); reg[d["id"]] = d
res = {}
for f in glob.glob("phaseA/chunk_*.jsonl"):
    for l in open(f):
        r = json.loads(l); res[r["id"]] = r["status"]
def feats(d):
    adj = [set() for _ in range(28)]
    for a, b in d["edges"]: adj[a].add(b); adj[b].add(a)
    P = [0, 1, 2]; N = range(3, 28)
    t = [sum(1 for a, b in itertools.combinations(sorted(adj[p]), 2) if b in adj[a]) for p in P]
    c = [len(adj[p] & adj[q]) for p, q in itertools.combinations(P, 2)]
    n = collections.Counter(len([p for p in P if p in adj[x]]) for x in N)
    # outgoing P-N edges per p (b_p), outgoing N-N edges (delta)
    b = [8 - 2 * tt for tt in t]
    # N-N edges by type: inside a line with p (common P-neighbour) or outgoing
    out_edges = [(x, w) for x in N for w in adj[x] if w > x and w >= 3 and not any(p in adj[x] and p in adj[w] for p in P)]
    # type of the outgoing N-N edges: by the label sets of their ends
    lab = lambda x: "".join("ABC"[p] for p in P if p in adj[x]) or "-"
    out_types = tuple(sorted(tuple(sorted((lab(x), lab(w)))) for x, w in out_edges))
    # r = 0 pairs among N (pairs that no outside vertex may see together), and number of r values
    r0 = r1 = r2 = 0
    for s, tt_ in itertools.combinations(range(28), 2):
        cc = len(adj[s] & adj[tt_]); rr = (1 - cc) if tt_ in adj[s] else (2 - cc)
        r0 += rr == 0; r1 += rr == 1; r2 += rr == 2
    return {"delta": d["delta"], "t": tuple(sorted(t)), "c": tuple(sorted(c)), "u": sum(c), "n": (n[0], n[1], n[2], n[3]), "paths": tuple(d["path_counts"]),
            "star": d["star"], "iso": d["isolates"], "deg2": d["degree2"], "out_types": out_types, "r": (r0, r1, r2)}
rows = [(sid, res[sid], feats(reg[sid])) for sid in res]
print("supports analysed:", len(rows), " dead:", sum(1 for r in rows if r[1] == "infeasible"))
def table(key, minn=8):
    c = collections.Counter(); k = collections.Counter()
    for sid, st, f in rows:
        v = f[key] if not callable(key) else key(f); c[v] += 1; k[v] += st == "infeasible"
    print(f"--- by {key if not callable(key) else 'custom'}:")
    for v in sorted(c, key=lambda v: (-k[v] / c[v], str(v))):
        if c[v] >= minn: print(f"     {str(v):60s} dead {k[v]:4d} / {c[v]:4d}  ({100*k[v]/c[v]:.0f} %)")
for key in ("delta", "t", "c", "u", "n", "star", "iso", "deg2"): table(key)
table(lambda f: (f["u"], f["delta"]), 10)
table(lambda f: (f["t"], f["c"]), 10)
table("paths", 12)
table("r", 12)
import pickle; pickle.dump(rows, open("micro_rows.pkl", "wb"))
