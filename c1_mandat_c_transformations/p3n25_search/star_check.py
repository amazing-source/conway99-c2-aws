"""INDEPENDENT CHECK of a 'no star' verdict (no solver; exhaustive enumeration; only the edge list of the support is used).

p a positive.  Gamma(p) is a perfect matching on 14 vertices; 8 of them are in N.  The 6 others (slots) are outside the support.
Slot i < u is matched to the i-th vertex x_i of N_p that has no neighbour in N_p; the remaining slots are matched in pairs.
Every vertex s of S (s != p) lies in exactly rho(s) slots, rho(s) = r(p, s) = (1 if s ~ p else 2) - (common neighbours of s and p in S).
A star = six sets B_0..B_5 (p in each) such that, for each slot z:
   (1) |B_z inter N| - |B_z inter P| = 4;                (2) two vertices of B_z have r >= 1;
   (3) a vertex of B_z has at most 1 neighbour in B_z;    (4) a vertex s outside B_z has at most 2 common neighbours with z inside
   S u Z_p, i.e. |N(s) inter B_z| + [s in B_partner(z)] <= 2;      (5) two slots share at most one vertex besides p, none if paired.
The enumeration is a depth-first search over the vertices (the vertex with the fewest possible slot sets first), with no symmetry
reduction: every star is visited.  Each complete star gives a 34 x 34 adjacency matrix; it must violate one of the listed
integer-parabola cuts:  w^T(12 I + 2 J - A - A^2) w - (2a+1)(14 sum w - 1^T A w) + 65 a(a+1) < 0.
usage: star_check.py register.jsonl results.jsonl"""
import sys, json, itertools, time
import numpy as np

def pc(x): return bin(x).count("1")

def check(edges, p, cuts, limit=20_000_000):
    A = [[0] * 28 for _ in range(28)]
    for x, y in edges: A[x][y] = A[y][x] = 1
    adj = [sum(1 << t for t in range(28) if A[s][t]) for s in range(28)]
    r = [[0 if s == t else (1 if A[s][t] else 2) - pc(adj[s] & adj[t]) for t in range(28)] for s in range(28)]
    compat = [sum(1 << t for t in range(28) if t != s and r[s][t] >= 1) for s in range(28)]
    NM = sum(1 << s for s in range(3, 28)); PM = 7; pbit = 1 << p
    Np = [x for x in range(3, 28) if A[p][x]]; assert len(Np) == 8
    NpM = sum(1 << x for x in Np)
    U = [x for x in Np if not (adj[x] & NpM)]; u = len(U)
    partner = {}
    for i in range(u, 6, 2): partner[i] = i + 1; partner[i + 1] = i
    assert all(r[p][x] == (1 if x in U else 0) for x in Np)
    todo0 = [s for s in range(28) if s != p and s not in Np and r[p][s] > 0]
    rho = {s: r[p][s] for s in todo0}
    B0 = [pbit | ((1 << U[i]) if i < u else 0) for i in range(6)]
    final0 = sum(1 << s for s in range(28) if s not in todo0)          # vertices whose slots are completely known
    AN = np.array(A, dtype=np.int64); cutsW = [(np.array(c["w"], dtype=np.int64), c["a"]) for c in cuts]
    stat = {"stars": 0, "bad": 0, "nodes": 0}; free_pos = [sum(1 for s in todo0 if s < 3)]
    def bal(Bz): return pc(Bz & NM) - pc(Bz & PM)
    def can_add(z, s, B, final):
        Bz = B[z]
        if (Bz & ~pbit) & ~compat[s]: return False
        if s >= 3 and pc(Bz & NM) + 1 > 5 + pc(Bz & PM & ~pbit) + free_pos[0]: return False
        nb = adj[s] & Bz
        if nb:
            if nb & (nb - 1): return False
            t = nb.bit_length() - 1
            if adj[t] & Bz: return False
        pz = partner.get(z)
        if pz is not None and (B[pz] >> s) & 1: return False
        # vertices that are final and outside B_z: at most 2 common neighbours with z
        m = adj[s] & final & ~Bz
        while m:
            t = m.bit_length() - 1; m ^= 1 << t
            if pc(adj[t] & (Bz | (1 << s))) + (1 if pz is not None and (B[pz] >> t) & 1 else 0) > 2: return False
        return True
    def options(s, B, final):
        out = []
        if rho[s] == 1:
            for z in range(6):
                if can_add(z, s, B, final): out.append((z,))
        else:
            ok = [z for z in range(6) if can_add(z, s, B, final)]
            for z, z2 in itertools.combinations(ok, 2):
                if partner.get(z) == z2: continue
                if (B[z] & B[z2]) != pbit: continue
                out.append((z, z2))
        return out
    def final_ok(B):
        for z in range(6):
            Bz = B[z]
            if bal(Bz) != 4: return False
            pz = partner.get(z)
            for s in range(28):
                c = pc(adj[s] & Bz)
                if (Bz >> s) & 1:
                    if c > 1: return False
                elif c + (1 if pz is not None and (B[pz] >> s) & 1 else 0) > 2: return False
        for z, z2 in itertools.combinations(range(6), 2):
            if pc(B[z] & B[z2]) > (1 if partner.get(z) == z2 else 2): return False
        return True
    def refuted(B):
        Ap = np.zeros((34, 34), dtype=np.int64); Ap[:28, :28] = AN
        for z in range(6):
            for s in range(28):
                if (B[z] >> s) & 1: Ap[28 + z, s] = Ap[s, 28 + z] = 1
            if z in partner: Ap[28 + z, 28 + partner[z]] = 1
        M = 12 * np.eye(34, dtype=np.int64) + 2 - Ap - Ap @ Ap; lin = 14 - Ap.sum(axis=0)
        for w, a in cutsW:
            if int(w @ M @ w) - (2 * a + 1) * int(lin @ w) + 65 * a * (a + 1) < 0: return True
        return False
    def rec(todo, B, final):
        stat["nodes"] += 1
        if stat["nodes"] > limit: raise RuntimeError("limit")
        if not todo:
            if final_ok(B):
                stat["stars"] += 1
                if not refuted(B): stat["bad"] += 1
            return
        free_pos[0] = sum(1 for s in todo if s < 3)
        best = None; avail = [0] * 6
        for s in todo:
            o = options(s, B, final)
            if not o: return
            if s >= 3:
                for z in {z for zs in o for z in zs}: avail[z] += 1
            if best is None or len(o) < len(best[1]): best = (s, o)
        if free_pos[0] == 0:
            for z in range(6):                                   # the slot still needs  5 + positives - present  vertices of N
                if 5 + pc(B[z] & PM & ~pbit) - pc(B[z] & NM) > avail[z]: return
        s, opts = best; rest = [t for t in todo if t != s]
        for zs in opts:
            B2 = list(B)
            for z in zs: B2[z] |= 1 << s
            rec(rest, B2, final | (1 << s))
    rec(todo0, B0, final0)
    return stat["stars"], stat["bad"], stat["nodes"]

def _job(args):
    sid, edges, p, cuts = args; t1 = time.time()
    try:
        nstar, nbad, nodes = check(edges, p, cuts); ok = nbad == 0
    except RuntimeError: nstar = nbad = nodes = -1; ok = False
    return sid, p, nodes, nstar, len(cuts), nbad, ok, time.time() - t1

if __name__ == "__main__":
    from multiprocessing import Pool
    reg = {}
    for line in open(sys.argv[1], encoding="utf-8"):
        d = json.loads(line); reg[d["id"]] = d
    only = set(json.load(open(sys.argv[4]))) if len(sys.argv) > 4 else None
    jobs = []
    for line in open(sys.argv[2]):
        o = json.loads(line)
        if not o.get("dead") or (only is not None and o["id"] not in only): continue
        x = next(q for q in o["pos"] if q["status"] == "no star"); jobs.append((o["id"], reg[o["id"]]["edges"], x["p"], x["cuts"]))
    good = bad = 0; t0 = time.time()
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 4) as pl:
        for sid, p, nodes, nstar, nc, nbad, ok, t in pl.imap_unordered(_job, jobs, chunksize=1):
            good += ok; bad += not ok
            print(f"support {sid}, positive {p}: {nodes} nodes, {nstar} complete stars, {nc} cuts, stars not refuted: {nbad}; verdict confirmed: {ok}  [{t:.0f}s]", flush=True)
    print(f"confirmed {good}, not confirmed {bad}  [{time.time()-t0:.0f}s]")
