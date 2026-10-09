"""THE STAR OF A POSITIVE, with the integer parabola as a cut.

p a positive of the support S.  Its 14 neighbours form 7 disjoint edges: 8 are in N (t_p edges, u = 8 - 2 t_p unmatched vertices), 6 are
outside: Z_p.  Slot i < u is the apex of the i-th unmatched neighbour x_i; the other slots are paired (u, u+1), (u+2, u+3), ...
So the graph induced on S u Z_p (34 vertices) is KNOWN once the six neighbourhoods B_z are chosen.
Model (exact, CP-SAT): a[z][s] for s in S minus p, with
   |B_z inter N| - |B_z inter P| = 4;   sum_z a[z][s] = r(p, s);   B_z induces a partial matching, pairs inside have r >= 1, a vertex
   outside B_z has at most 2 neighbours in it;   two slots share at most one vertex besides p, none if they are paired;
   lambda / mu inside S u Z_p for the pairs (z, s).
Loop: solve; on the 34 vertices search an integer weighting (w, a) with Phi < 0 (Lemma A); add  Phi(w, a) >= 0  as a constraint; again.
End: INFEASIBLE (no star: the support is impossible, given the solver verdict) or a star on which no witness is found.
usage: star.py register.jsonl id [id ...]"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I

def witness(Ap, rng, wmax=2, restarts=60, avals=(0, 1, -1, 2)):
    """local search for (w, a) with Phi < 0 on the vertex set carrying the adjacency matrix Ap"""
    n = len(Ap); nz = 99 - n
    M = 12 * np.eye(n, dtype=np.int64) + 2 - Ap - Ap @ Ap; dv = 14 - Ap.sum(axis=1)
    best = (10 ** 9, None, None); Mf = np.linalg.pinv(M.astype(float))
    for a in avals:
        st0 = np.clip(np.round((2 * a + 1) / 2 * (Mf @ dv)), -wmax, wmax).astype(np.int64)
        for k in range(restarts):
            w = st0.copy() if k == 0 else np.array([rng.choice([0, 0, 0, 1, 1, -1]) for _ in range(n)], dtype=np.int64)
            val = int(w @ M @ w - (2 * a + 1) * (dv @ w) + nz * a * (a + 1)); improved = True
            while improved:
                improved = False; g = M @ w
                for s in rng.sample(range(n), n):
                    for step in (1, -1):
                        if abs(w[s] + step) > wmax: continue
                        dl = 2 * step * int(g[s]) + int(M[s, s]) - (2 * a + 1) * step * int(dv[s])
                        if dl < 0: w[s] += step; val += dl; g = M @ w; improved = True; break
            if val < best[0]:
                best = (val, w.copy(), a)
                if val < 0: return best
    return best

def phi_direct(Ap, w, a):
    n = len(Ap); w = np.asarray(w, dtype=np.int64)
    M = 12 * np.eye(n, dtype=np.int64) + 2 - Ap - Ap @ Ap
    return int(w @ M @ w) - (2 * a + 1) * int(14 * w.sum() - Ap.sum(axis=0) @ w) + (99 - n) * a * (a + 1)

class Star:
    def __init__(self, d, p):
        self.d = d; self.p = p
        A = np.zeros((28, 28), dtype=np.int64)
        for x, y in d["edges"]: A[x, y] = A[y, x] = 1
        self.A = A; C = A @ A; self.r = np.where(A == 1, 1, 2) - C; np.fill_diagonal(self.r, 0); self.dZ = 14 - A.sum(axis=1)
        Np = [x for x in range(3, 28) if A[p, x]]
        self.U = [x for x in Np if not any(A[x, y] for y in Np)]; self.u = len(self.U)
        self.partner = {}
        for i in range(self.u, 6, 2): self.partner[i] = i + 1; self.partner[i + 1] = i
        self.others = [s for s in range(28) if s != p]
        self.build()

    def build(self):
        A, r, p = self.A, self.r, self.p; m = cp_model.CpModel(); a = {}
        for z in range(6):
            for s in self.others:
                a[z, s] = m.NewBoolVar(f"a{z}_{s}")
                if r[p, s] == 0: m.Add(a[z, s] == 0)
        for i, x in enumerate(self.U):
            for z in range(6): m.Add(a[z, x] == (1 if z == i else 0))
        for z in range(6):
            m.Add(sum(a[z, s] for s in self.others if s >= 3) - sum(a[z, s] for s in self.others if s < 3) == 5)
            for s, t in itertools.combinations(self.others, 2):
                if r[s, t] <= 0: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
            for s in self.others:
                ns = sum(a[z, t] for t in self.others if A[s, t]) + int(A[s, p])
                pz = self.partner.get(z)
                m.Add(ns + (a[pz, s] if pz is not None else 0) <= 2 - a[z, s])
        for s in self.others: m.Add(sum(a[z, s] for z in range(6)) == int(r[p, s]))
        self.common = {}
        for z, z2 in itertools.combinations(range(6), 2):
            prods = []
            for s in self.others:
                if r[p, s] >= 2 or (r[p, s] == 1 and False):
                    b = m.NewBoolVar(""); m.AddMultiplicationEquality(b, [a[z, s], a[z2, s]]); prods.append(b)
            m.Add(sum(prods) <= (0 if self.partner.get(z) == z2 else 1))
        # symmetry: inside a pair of slots and between pairs, order by the smallest vertex number
        key = {z: sum((1 << (27 - s)) * a[z, s] for s in self.others) for z in range(self.u, 6)}
        for i in range(self.u, 6, 2):
            m.Add(key[i] > key[i + 1])
            if i + 2 < 6: m.Add(key[i] > key[i + 2])
        self.m = m; self.a = a; self.cuts = []

    def adjacency(self, sol):
        """34 x 34 matrix: S (0..27), slots 28..33"""
        Ap = np.zeros((34, 34), dtype=np.int64); Ap[:28, :28] = self.A
        for z in range(6):
            Ap[28 + z, self.p] = Ap[self.p, 28 + z] = 1
            for s in self.others:
                if sol[z][s]: Ap[28 + z, s] = Ap[s, 28 + z] = 1
            if z in self.partner: Ap[28 + z, 28 + self.partner[z]] = 1
        return Ap

    def add_cut(self, w, a_):
        """Phi(w, a) >= 0 written with t = A+ w:  sum_k (t_k^2 + (w_k - 2a - 1) t_k)  <=  12|w|^2 + 2 (sum w)^2 - 14 (2a+1) sum w + 65 a (a+1)"""
        m, a, A, p = self.m, self.a, self.A, self.p; w = [int(x) for x in w]; wS = np.array(w[:28]); terms = []
        cS = A @ wS
        for k in range(34):
            if k < 28:
                if k == p: expr = int(cS[k]) + sum(w[28:]); lin = None
                else: lin = sum(w[28 + z] * a[z, k] for z in range(6) if w[28 + z]); expr = int(cS[k]) + lin
            else:
                z = k - 28
                expr = w[p] + sum(w[s] * a[z, s] for s in self.others if w[s]) + (w[28 + self.partner[z]] if z in self.partner else 0)
            if isinstance(expr, (int, np.integer)):
                t = int(expr); terms.append(t * t + (w[k] - 2 * a_ - 1) * t)
            else:
                t = m.NewIntVar(-60, 60, ""); m.Add(t == expr); sq = m.NewIntVar(0, 3600, ""); m.AddMultiplicationEquality(sq, [t, t])
                terms.append(sq + (w[k] - 2 * a_ - 1) * t)
        rhs = 12 * sum(x * x for x in w) + 2 * sum(w) ** 2 - 14 * (2 * a_ + 1) * sum(w) + 65 * a_ * (a_ + 1)
        m.Add(sum(terms) <= rhs); self.cuts.append({"w": w, "a": int(a_)})

    def run(self, rng, max_rounds=400, tl=120, workers=8, verbose=False):
        t0 = time.time()
        for it in range(max_rounds):
            sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_workers = workers
            sv.parameters.random_seed = it
            st = sv.Solve(self.m)
            if st == cp_model.INFEASIBLE: return "no star", it, None
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return "solver undecided", it, None
            sol = [{s: int(sv.Value(self.a[z, s])) for s in self.others} for z in range(6)]
            Ap = self.adjacency(sol); val, w, a_ = witness(Ap, rng)
            if val >= 0: return "star without witness", it, sol
            assert phi_direct(Ap, w, a_) == val
            self.add_cut(w, a_)
            if verbose: print(f"      round {it}: cut Phi = {val}, a = {a_}, support of w: {int(np.count_nonzero(w))}  [{time.time()-t0:.0f}s]", flush=True)
        return "undecided (round limit)", max_rounds, None

if __name__ == "__main__":
    fn = sys.argv[1]; rng = random.Random(3)
    for sid in map(int, sys.argv[2:]):
        d = I.load(fn, sid)
        for p in range(3):
            t0 = time.time(); S = Star(d, p); st, it, sol = S.run(rng, verbose="-v" in sys.argv)
            print(f"support {sid} (delta {d['delta']}), positive {p}: u = {S.u}; {st} after {it} cut(s)  [{time.time()-t0:.0f}s]", flush=True)
