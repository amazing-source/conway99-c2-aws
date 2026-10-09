"""THE SHELL OF THE THREE POSITIVES: all outside vertices adjacent to a positive, with their mutual adjacencies.

tau = number of outside vertices adjacent to the three positives; then the number of outside vertices adjacent to exactly {p, q} is
r(p,q) - tau and to p alone 6 - sum_q (r(p,q) - tau) - tau.  M vertices in all (18 when no two positives share an outside neighbour).
Unknowns: a[z][s] (s in N) and h[z][z'] (adjacency inside the shell).  ALL neighbours of a positive lie in S+ = S u shell, so the
common-neighbour counts with a positive are exact:
   p ~ z :  sum_{x in N_p} a[z][x] + sum_{z' in Z_p} h[z][z'] = 1 ;      p !~ z :  the same sum = 2.
Other constraints: block rules, pair rows of the positives (=), rows inside N (<=), lambda / mu inside S+ (<=), degrees.
Loop with the integer parabola on the 28 + M vertices as a cut (Lemma A), as in star.py.
usage: shell.py register.jsonl id [time_limit] [-v]"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST

class Shell:
    def __init__(self, d, tau=0):
        A = np.zeros((28, 28), dtype=np.int64)
        for x, y in d["edges"]: A[x, y] = A[y, x] = 1
        self.A = A; C = A @ A; r = np.where(A == 1, 1, 2) - C; np.fill_diagonal(r, 0); self.r = r; self.dZ = 14 - A.sum(axis=1)
        types = []
        types += [(0, 1, 2)] * tau
        npq = {}
        for p, q in itertools.combinations(range(3), 2):
            npq[(p, q)] = int(r[p, q]) - tau; types += [(p, q)] * npq[(p, q)]
        self.ok = all(v >= 0 for v in npq.values())
        for p in range(3):
            n1 = 6 - tau - sum(v for k, v in npq.items() if p in k); self.ok &= n1 >= 0; types += [(p,)] * max(n1, 0)
        self.types = types; self.M = len(types); self.n = 28 + self.M
        if self.ok: self.build()

    def build(self):
        A, r, M, T = self.A, self.r, self.M, self.types; m = cp_model.CpModel(); a = {}; h = {}
        N = range(3, 28); Np = [[x for x in N if A[p, x]] for p in range(3)]
        Zp = [[z for z in range(M) if p in T[z]] for p in range(3)]
        for z in range(M):
            for s in N:
                a[z, s] = m.NewBoolVar(f"a{z}_{s}")
                if any(r[p, s] == 0 for p in T[z]): m.Add(a[z, s] == 0)
        for z, z2 in itertools.combinations(range(M), 2): h[z, z2] = h[z2, z] = m.NewBoolVar(f"h{z}_{z2}")
        for z in range(M):
            m.Add(sum(a[z, s] for s in N) == 4 + len(T[z]))
            for s, t in itertools.combinations(N, 2):
                if r[s, t] <= 0: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
            m.Add(sum(h[z, z2] for z2 in range(M) if z2 != z) <= 10 - 2 * len(T[z]))
            for p in range(3):
                m.Add(sum(a[z, x] for x in Np[p]) + sum(h[z, z2] for z2 in Zp[p] if z2 != z) == (1 if p in T[z] else 2))
        for p in range(3):
            for s in N: m.Add(sum(a[z, s] for z in Zp[p]) == int(r[p, s]))
        for s in N: m.Add(sum(a[z, s] for z in range(M)) <= int(self.dZ[s]))
        # products
        ha = {}
        for z in range(M):
            for z2 in range(M):
                if z2 == z: continue
                for s in N:
                    b = m.NewBoolVar(""); m.AddBoolAnd([h[z, z2], a[z2, s]]).OnlyEnforceIf(b); m.AddBoolOr([h[z, z2].Not(), a[z2, s].Not(), b]); ha[z, z2, s] = b
        for z in range(M):
            for s in N:
                nb = sum(a[z, t] for t in N if A[s, t]) + sum(1 for p in T[z] if A[s, p])
                m.Add(nb + sum(ha[z, z2, s] for z2 in range(M) if z2 != z) <= 2 - a[z, s])
        for z, z2 in itertools.combinations(range(M), 2):
            terms = []
            for s in N:
                b = m.NewBoolVar(""); m.AddBoolAnd([a[z, s], a[z2, s]]).OnlyEnforceIf(b); m.AddBoolOr([a[z, s].Not(), a[z2, s].Not(), b]); terms.append(b)
            for z3 in range(M):
                if z3 in (z, z2): continue
                b = m.NewBoolVar(""); m.AddBoolAnd([h[z, z3], h[z2, z3]]).OnlyEnforceIf(b); m.AddBoolOr([h[z, z3].Not(), h[z2, z3].Not(), b]); terms.append(b)
            m.Add(sum(terms) + len(set(T[z]) & set(T[z2])) <= 2 - h[z, z2])
        for s, t in itertools.combinations(N, 2):
            if r[s, t] <= 0: continue
            terms = []
            for z in range(M):
                b = m.NewBoolVar(""); m.AddBoolAnd([a[z, s], a[z, t]]).OnlyEnforceIf(b); m.AddBoolOr([a[z, s].Not(), a[z, t].Not(), b]); terms.append(b)
            m.Add(sum(terms) <= int(r[s, t]))
        # symmetry between vertices of the same type
        key = {z: sum((1 << (27 - s)) * a[z, s] for s in N) for z in range(M)}
        for z in range(M - 1):
            if T[z] == T[z + 1]: m.Add(key[z] > key[z + 1])
        self.m, self.a, self.h, self.N = m, a, h, N; self.cuts = []

    def adjacency(self, sv):
        M = self.M; Ap = np.zeros((self.n, self.n), dtype=np.int64); Ap[:28, :28] = self.A
        for z in range(M):
            for p in self.types[z]: Ap[28 + z, p] = Ap[p, 28 + z] = 1
            for s in self.N:
                if sv.Value(self.a[z, s]): Ap[28 + z, s] = Ap[s, 28 + z] = 1
            for z2 in range(z + 1, M):
                if sv.Value(self.h[z, z2]): Ap[28 + z, 28 + z2] = Ap[28 + z2, 28 + z] = 1
        return Ap

    def add_cut(self, w, a_):
        m, a, h, A, M, T = self.m, self.a, self.h, self.A, self.M, self.types; w = [int(x) for x in w]; cS = A @ np.array(w[:28]); terms = []
        for k in range(self.n):
            if k < 3: t = int(cS[k]) + sum(w[28 + z] for z in range(M) if k in T[z]); terms.append(t * t + (w[k] - 2 * a_ - 1) * t); continue
            if k < 28: expr = int(cS[k]) + sum(w[28 + z] * a[z, k] for z in range(M) if w[28 + z]); const = not any(w[28:])
            else:
                z = k - 28
                expr = sum(w[p] for p in T[z]) + sum(w[s] * a[z, s] for s in self.N if w[s]) + sum(w[28 + z2] * h[z, z2] for z2 in range(M) if z2 != z and w[28 + z2])
                const = not any(w[s] for s in self.N) and not any(w[28 + z2] for z2 in range(M) if z2 != z)
            if const:
                t = int(cS[k]) if k < 28 else sum(w[p] for p in T[k - 28]); terms.append(t * t + (w[k] - 2 * a_ - 1) * t)
            else:
                t = m.NewIntVar(-80, 80, ""); m.Add(t == expr); sq = m.NewIntVar(0, 6400, ""); m.AddMultiplicationEquality(sq, [t, t])
                terms.append(sq + (w[k] - 2 * a_ - 1) * t)
        rhs = 12 * sum(x * x for x in w) + 2 * sum(w) ** 2 - 14 * (2 * a_ + 1) * sum(w) + (99 - self.n) * a_ * (a_ + 1)
        m.Add(sum(terms) <= rhs); self.cuts.append({"w": w, "a": int(a_)})

    def run(self, rng, max_rounds=200, tl=300, workers=8, verbose=False):
        t0 = time.time()
        for it in range(max_rounds):
            sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_workers = workers; sv.parameters.random_seed = it
            st = sv.Solve(self.m)
            if st == cp_model.INFEASIBLE: return "no shell", it, None
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return "solver undecided", it, None
            Ap = self.adjacency(sv); val, w, a_ = ST.witness(Ap, rng, restarts=80)
            if verbose: print(f"      round {it}: shell found [{time.time()-t0:.0f}s]; best Phi = {val} (a = {a_})", flush=True)
            if val >= 0: return "shell without witness", it, Ap
            assert ST.phi_direct(Ap, w, a_) == val
            self.add_cut(w, a_)
        return "undecided (round limit)", max_rounds, None

if __name__ == "__main__":
    fn = sys.argv[1]; sid = int(sys.argv[2]); TL = float(sys.argv[3]) if len(sys.argv) > 3 else 300; rng = random.Random(3)
    d = I.load(fn, sid)
    for tau in range(3):
        t0 = time.time(); S = Shell(d, tau)
        if not S.ok: continue
        st, it, Ap = S.run(rng, tl=TL, verbose="-v" in sys.argv)
        print(f"support {sid} (delta {d['delta']}), tau = {tau}: {S.M} shell vertices of types {sorted(set(S.types))}; {st} after {it} cut(s)  [{time.time()-t0:.0f}s]", flush=True)
        if Ap is not None: np.save(f"shell_{sid}_{tau}.npy", Ap)
