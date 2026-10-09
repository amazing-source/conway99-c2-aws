"""P3/N25, STAGE 1 as an exact 0/1 programme on BLOCKS (formulation suggested by Codex for the triple rows).

For one support S = P u N (register of Codex, P = {0,1,2}, N = {3..27}): a block is the set B = N(z) inter S of an outside vertex z.
Admissible blocks (masks):  |B inter N| - |B inter P| = 4;  every pair inside B has r >= 1 outside common neighbour available;
                            B induces a partial matching in S.
Programme:  x_B in {0, 1};   for every pair {s, s'}:  sum_{B contains s, s'} x_B = r(s, s');   for every s:  sum_{B contains s} x_B = dZ(s);
            for every triple T of S:  sum_{B contains T} x_B <= 1     (two outside vertices have at most 2 common neighbours).
'INFEASIBLE' is a solver verdict (to be certified separately); 'FEASIBLE' is re-checked here from the returned blocks.
usage: p3n25_ilp.py register.jsonl id [time_limit_s] [workers]"""
import sys, json, time, itertools
from ortools.sat.python import cp_model

def load(fn, sid):
    for line in open(fn, encoding="utf-8"):
        d = json.loads(line)
        if d["id"] == sid: return d
    raise KeyError(sid)

def boundary(edges):
    adj = [0] * 28
    for a, b in edges: adj[a] |= 1 << b; adj[b] |= 1 << a
    r = [[0] * 28 for _ in range(28)]
    for s in range(28):
        for t in range(28):
            if s == t: continue
            c = bin(adj[s] & adj[t]).count("1")
            r[s][t] = (1 - c) if (adj[s] >> t) & 1 else (2 - c)
            assert r[s][t] >= 0, (s, t)
    dZ = [14 - bin(adj[s]).count("1") for s in range(28)]
    return adj, r, dZ

def masks(adj, r):
    """all admissible blocks, as bit masks"""
    comp = [0] * 28                                   # compatibility: r >= 1
    for s in range(28):
        for t in range(28):
            if s != t and r[s][t] >= 1: comp[s] |= 1 << t
    out = []
    def ok_matching(B, s):
        """adding s to B keeps max degree <= 1 in the induced graph"""
        nb = adj[s] & B
        if bin(nb).count("1") > 1: return False
        if nb:
            t = nb.bit_length() - 1
            if adj[t] & B: return False                # t already has a neighbour in B
        return True
    for k in range(4):                                # number of P-points
        for A in itertools.combinations(range(3), k):
            B0 = 0; good = True
            for p in A:
                if (B0 & ~comp[p]) & ((1 << 28) - 1): good = False; break
                B0 |= 1 << p
            if not good: continue
            cand0 = ((1 << 28) - 1) & ~7
            for p in A: cand0 &= comp[p]
            need = 4 + k
            def rec(B, cand, last, left):
                if left == 0: out.append(B); return
                c = cand >> (last + 1) << (last + 1)
                while c:
                    s = (c & -c).bit_length() - 1; c &= c - 1
                    if bin(cand >> s).count("1") < left: break
                    if ok_matching(B, s): rec(B | (1 << s), cand & comp[s], s, left - 1)
            rec(B0, cand0, 2, need)
    return out

if __name__ == "__main__":
    fn, sid = sys.argv[1], int(sys.argv[2])
    TL = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
    WK = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    SEED = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 0
    d = load(fn, sid); t0 = time.time()
    adj, r, dZ = boundary(d["edges"])
    if "filtered" in sys.argv:
        import p3n25_lp2 as L2
        adj, r, dZ, Ms, n0, info = L2.filtered_masks(d)
    else:
        Ms = masks(adj, r)
    sizes = {}
    for B in Ms: sizes[bin(B).count("1")] = sizes.get(bin(B).count("1"), 0) + 1
    print(f"support id {sid} (delta {d['delta']}): {len(Ms)} admissible blocks by size {dict(sorted(sizes.items()))}  [{time.time()-t0:.1f}s]", flush=True)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(len(Ms))]
    bypoint = [[] for _ in range(28)]; bypair = {}; bytriple = {}
    for i, B in enumerate(Ms):
        pts = [s for s in range(28) if (B >> s) & 1]
        for s in pts: bypoint[s].append(i)
        for pr in itertools.combinations(pts, 2): bypair.setdefault(pr, []).append(i)
        for tr in itertools.combinations(pts, 3): bytriple.setdefault(tr, []).append(i)
    infeasible_trivially = False
    for s in range(28): m.Add(sum(x[i] for i in bypoint[s]) == dZ[s])
    for s, t in itertools.combinations(range(28), 2):
        lst = bypair.get((s, t), [])
        if r[s][t] > 0 and not lst: infeasible_trivially = True
        if lst: m.Add(sum(x[i] for i in lst) == r[s][t])
    ntr = 0
    for tr, lst in bytriple.items():
        if len(lst) >= 2: m.Add(sum(x[i] for i in lst) <= 1); ntr += 1
    print(f"   {len(bypair)} pair rows, {ntr} triple rows" + ("   (a required pair is in no admissible block: infeasible)" if infeasible_trivially else ""), flush=True)
    solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = TL; solver.parameters.num_search_workers = WK; solver.parameters.random_seed = SEED
    t1 = time.time(); st = solver.Solve(m); el = time.time() - t1
    print(f"   stage 1: {solver.StatusName(st)} in {el:.1f} s  (limit {TL:.0f} s, {WK} workers; conflicts {solver.NumConflicts()})", flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [Ms[i] for i in range(len(Ms)) if solver.Value(x[i])]
        ok = len(chosen) == 71
        for s in range(28): ok &= sum(1 for B in chosen if (B >> s) & 1) == dZ[s]
        for s, t in itertools.combinations(range(28), 2): ok &= sum(1 for B in chosen if (B >> s) & 1 and (B >> t) & 1) == r[s][t]
        for B1, B2 in itertools.combinations(chosen, 2): ok &= bin(B1 & B2).count("1") <= 2
        for B in chosen:
            pts = [s for s in range(28) if (B >> s) & 1]
            ok &= all(bin(adj[s] & B).count("1") <= 1 for s in pts)
            ok &= sum(1 for s in pts if s >= 3) - sum(1 for s in pts if s < 3) == 4
        cs = sorted(bin(B).count("1") for B in chosen)
        print(f"   re-check of the 71 blocks: {ok};  sizes { {k: cs.count(k) for k in sorted(set(cs))} }")
        json.dump({"id": sid, "edges": d["edges"], "blocks": chosen}, open(f"stage1_blocks_{sid}.json", "w"))
