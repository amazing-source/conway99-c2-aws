"""DOES A CLEAN DOUBLE STAR EXTEND TO THE THIRD POSITIVE?

Step 1: a double star at (p, q) on which no integer-parabola witness is found (doublestar.py): a KNOWN graph G on 40 vertices.
Step 2: the star of the third positive c over the base graph G (the star engine of star.py with an arbitrary base graph): six new
vertices, each with a neighbourhood in G; all neighbours of c are then in G u Z_c, so  sum_z a[z][s] = r_G(c, s)  for every s of G.
Cut loop with Lemma A on the 46 vertices.  Result: 'no star' (this double star cannot be completed) or a shell without witness.
Only for supports where the positives have no common outside neighbour.       usage: shell_ext.py id ntries [rounds]"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST, doublestar as DS

class GenStar:
    def __init__(self, G, c):
        self.G = G; self.c = c; n = len(G); self.n = n
        C = G @ G; r = np.where(G == 1, 1, 2) - C; np.fill_diagonal(r, 0); self.r = r
        Nc = [x for x in range(n) if G[c, x]]; assert len(Nc) == 8 and all(3 <= x < 28 for x in Nc)
        self.U = [x for x in Nc if not any(G[x, y] for y in Nc)]; self.u = len(self.U)
        self.partner = {}
        for i in range(self.u, 6, 2): self.partner[i] = i + 1; self.partner[i + 1] = i
        self.others = [s for s in range(n) if s != c]; self.build()
    def build(self):
        G, r, c, others = self.G, self.r, self.c, self.others; m = cp_model.CpModel(); a = {}
        for z in range(6):
            for s in others:
                a[z, s] = m.NewBoolVar("")
                if r[c, s] <= 0: m.Add(a[z, s] == 0)
        for i, x in enumerate(self.U):
            for z in range(6): m.Add(a[z, x] == (1 if z == i else 0))
        for z in range(6):
            m.Add(sum(a[z, s] for s in others if 3 <= s < 28) - sum(a[z, s] for s in others if s < 3) == 5)
            m.Add(sum(a[z, s] for s in others) + 1 + (1 if z in self.partner else 0) <= 14)
            for s, t in itertools.combinations(others, 2):
                if r[s, t] <= 0: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
            for s in others:
                ns = sum(a[z, t] for t in others if G[s, t]) + int(G[s, c]); pz = self.partner.get(z)
                m.Add(ns + (a[pz, s] if pz is not None else 0) <= 2 - a[z, s])
        for s in others: m.Add(sum(a[z, s] for z in range(6)) == int(max(r[c, s], 0)))
        for z, z2 in itertools.combinations(range(6), 2):
            prods = []
            for s in others:
                if r[c, s] >= 2:
                    b = m.NewBoolVar(""); m.AddMultiplicationEquality(b, [a[z, s], a[z2, s]]); prods.append(b)
            m.Add(sum(prods) <= (0 if self.partner.get(z) == z2 else 1))
        key = {z: sum((1 << (self.n - s)) * a[z, s] for s in others) for z in range(self.u, 6)}
        for i in range(self.u, 6, 2):
            m.Add(key[i] > key[i + 1])
            if i + 2 < 6: m.Add(key[i] > key[i + 2])
        self.m = m; self.a = a; self.cuts = []
    def adjacency(self, sv):
        n = self.n; Ap = np.zeros((n + 6, n + 6), dtype=np.int64); Ap[:n, :n] = self.G
        for z in range(6):
            Ap[n + z, self.c] = Ap[self.c, n + z] = 1
            for s in self.others:
                if sv.Value(self.a[z, s]): Ap[n + z, s] = Ap[s, n + z] = 1
            if z in self.partner: Ap[n + z, n + self.partner[z]] = 1
        return Ap
    def add_cut(self, w, a_):
        m, a, G, c, n = self.m, self.a, self.G, self.c, self.n; w = [int(x) for x in w]; cS = G @ np.array(w[:n]); terms = []
        for k in range(n + 6):
            if k == c: expr = int(cS[k]) + sum(w[n:]); var = False
            elif k < n: var = any(w[n:]); expr = int(cS[k]) + sum(w[n + z] * a[z, k] for z in range(6) if w[n + z])
            else:
                z = k - n; var = any(w[s] for s in self.others)
                expr = w[c] + sum(w[s] * a[z, s] for s in self.others if w[s]) + (w[n + self.partner[z]] if z in self.partner else 0)
            if not var:
                t = int(expr); terms.append(t * t + (w[k] - 2 * a_ - 1) * t)
            else:
                t = m.NewIntVar(-80, 80, ""); m.Add(t == expr); sq = m.NewIntVar(0, 6400, ""); m.AddMultiplicationEquality(sq, [t, t])
                terms.append(sq + (w[k] - 2 * a_ - 1) * t)
        rhs = 12 * sum(x * x for x in w) + 2 * sum(w) ** 2 - 14 * (2 * a_ + 1) * sum(w) + (99 - n - 6) * a_ * (a_ + 1)
        m.Add(sum(terms) <= rhs); self.cuts.append({"w": w, "a": int(a_)})
    def run(self, rng, rounds=60, tl=120, workers=6, percut=8):
        for it in range(rounds):
            sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_workers = workers; sv.parameters.random_seed = it
            st = sv.Solve(self.m)
            if st == cp_model.INFEASIBLE: return "no star", it, None
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return "solver undecided", it, None
            Ap = self.adjacency(sv); found = {}
            for k in range(percut):
                val, w, a_ = ST.witness(Ap, rng, restarts=25)
                if val < 0: w2 = DS.shrink(Ap, w, a_, rng); found[(a_, tuple(int(x) for x in w2))] = 1
            if not found: return "shell without witness", it, Ap
            for (a_, w2) in found: self.add_cut(list(w2), a_)
            if it % 5 == 4: print(f"      third star: round {it}, {len(self.cuts)} cuts, last solve {sv.WallTime():.0f}s", flush=True)
        return "undecided (round limit)", rounds, None

def clean_double_star(d, p, q, rng, seed, rounds=40):
    S = DS.DoubleStar(d, p, q)
    for it in range(rounds):
        sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 120; sv.parameters.num_workers = 6; sv.parameters.random_seed = 1000 * seed + it
        sv.parameters.randomize_search = True
        st = sv.Solve(S.m)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None, sv.StatusName(st)
        Ap = S.adjacency(sv); found = {}
        for k in range(10):
            val, w, a_ = ST.witness(Ap, rng, restarts=25)
            if val < 0: w2 = DS.shrink(Ap, w, a_, rng); found[(a_, tuple(int(x) for x in w2))] = 1
        if not found: return Ap, f"clean after {it} round(s)"
        for (a_, w2) in found: S.add_cut(list(w2), a_)
    return None, "round limit"

if __name__ == "__main__":
    sid = int(sys.argv[1]); NT = int(sys.argv[2]); R = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    d = I.load("register/supports_open_4581.jsonl", sid); rng = random.Random(11)
    for k in range(NT):
        p, q = [(0, 1), (0, 2), (1, 2)][k % 3]; c = 3 - p - q; t0 = time.time()
        G, msg = clean_double_star(d, p, q, rng, k)
        if G is None: print(f"try {k}: double star {'ABC'[p]}{'ABC'[q]}: {msg}", flush=True); continue
        t1 = time.time(); S = GenStar(G, c); st, it, Ap = S.run(rng, rounds=R)
        print(f"support {sid}, try {k}: double star {'ABC'[p]}{'ABC'[q]} ({msg}, {t1-t0:.0f}s); third star at {'ABC'[c]}: {st} after {it} round(s), {len(S.cuts)} cuts  [{time.time()-t1:.0f}s]", flush=True)
        if Ap is not None: np.save(f"shell_clean_{sid}_{k}.npy", Ap)
