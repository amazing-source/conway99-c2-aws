"""THE DOUBLE STAR: the outside neighbours of TWO positives p, q, with their mutual adjacencies (between the star at one positive, decided in a
second, and the shell of the three, which does not close).

Vertices: r(p,q) common outside neighbours of p and q, 6 - r(p,q) for p alone, 6 - r(p,q) for q alone (the third positive q' is an
ordinary vertex of S here: a[z][q'] is unknown).  All neighbours of p and of q are in S+ = S u Z_p u Z_q, so the common-neighbour
counts with p and with q are equalities.  Loop with the integer parabola on S+ as a cut, several shrunk witnesses per round.
usage: doublestar.py register.jsonl rounds solve_tl id [id ...]"""
import sys, json, time, random, itertools
import numpy as np
from ortools.sat.python import cp_model
import p3n25_ilp as I, star as ST

class DoubleStar:
    def __init__(self, d, p, q):
        A = np.zeros((28, 28), dtype=np.int64)
        for x, y in d["edges"]: A[x, y] = A[y, x] = 1
        self.A = A; C = A @ A; r = np.where(A == 1, 1, 2) - C; np.fill_diagonal(r, 0); self.r = r; self.dZ = 14 - A.sum(axis=1)
        self.act = (p, q); self.V = [s for s in range(28) if s not in (p, q)]
        k = int(r[p, q]); self.types = [(p, q)] * k + [(p,)] * (6 - k) + [(q,)] * (6 - k); self.M = len(self.types); self.n = 28 + self.M
        self.build()

    def build(self):
        A, r, M, T, V = self.A, self.r, self.M, self.types, self.V; m = cp_model.CpModel(); a = {}; h = {}
        third = [s for s in V if s < 3]; NV = [s for s in V if s >= 3]
        Nt = {t: [x for x in NV if A[t, x]] for t in self.act}; Zt = {t: [z for z in range(M) if t in T[z]] for t in self.act}
        for z in range(M):
            for s in V:
                a[z, s] = m.NewBoolVar("")
                if any(r[t, s] == 0 for t in T[z]): m.Add(a[z, s] == 0)
        for z, z2 in itertools.combinations(range(M), 2): h[z, z2] = h[z2, z] = m.NewBoolVar("")
        for z in range(M):
            m.Add(sum(a[z, s] for s in NV) - sum(a[z, s] for s in third) == 4 + len(T[z]))
            for s, t in itertools.combinations(V, 2):
                if r[s, t] <= 0: m.AddBoolOr([a[z, s].Not(), a[z, t].Not()])
            m.Add(sum(h[z, z2] for z2 in range(M) if z2 != z) + 2 * sum(a[z, s] for s in third) <= 10 - 2 * len(T[z]))
            for t in self.act:
                m.Add(sum(a[z, x] for x in Nt[t]) + sum(h[z, z2] for z2 in Zt[t] if z2 != z) == (1 if t in T[z] else 2))
        for t in self.act:
            for s in V: m.Add(sum(a[z, s] for z in Zt[t]) == int(r[t, s]))
        for s in V: m.Add(sum(a[z, s] for z in range(M)) <= int(self.dZ[s]))
        def AND(x, y):
            b = m.NewBoolVar(""); m.AddBoolAnd([x, y]).OnlyEnforceIf(b); m.AddBoolOr([x.Not(), y.Not(), b]); return b
        for z in range(M):
            for s in V:
                nb = sum(a[z, t] for t in V if A[s, t]) + sum(1 for t in T[z] if A[s, t])
                m.Add(nb + sum(AND(h[z, z2], a[z2, s]) for z2 in range(M) if z2 != z) <= 2 - a[z, s])
        for z, z2 in itertools.combinations(range(M), 2):
            terms = [AND(a[z, s], a[z2, s]) for s in V] + [AND(h[z, z3], h[z2, z3]) for z3 in range(M) if z3 not in (z, z2)]
            m.Add(sum(terms) + len(set(T[z]) & set(T[z2])) <= 2 - h[z, z2])
        for s, t in itertools.combinations(V, 2):
            if r[s, t] > 0: m.Add(sum(AND(a[z, s], a[z, t]) for z in range(M)) <= int(r[s, t]))
        key = {z: sum((1 << (27 - s)) * a[z, s] for s in V) for z in range(M)}
        for z in range(M - 1):
            if T[z] == T[z + 1]: m.Add(key[z] > key[z + 1])
        self.m, self.a, self.h = m, a, h; self.cuts = []

    def adjacency(self, sv):
        M = self.M; Ap = np.zeros((self.n, self.n), dtype=np.int64); Ap[:28, :28] = self.A
        for z in range(M):
            for t in self.types[z]: Ap[28 + z, t] = Ap[t, 28 + z] = 1
            for s in self.V:
                if sv.Value(self.a[z, s]): Ap[28 + z, s] = Ap[s, 28 + z] = 1
            for z2 in range(z + 1, M):
                if sv.Value(self.h[z, z2]): Ap[28 + z, 28 + z2] = Ap[28 + z2, 28 + z] = 1
        return Ap

    def add_cut(self, w, a_):
        m, a, h, A, M, T = self.m, self.a, self.h, self.A, self.M, self.types; w = [int(x) for x in w]; cS = A @ np.array(w[:28]); terms = []
        for k in range(self.n):
            if k in self.act: expr = int(cS[k]) + sum(w[28 + z] for z in range(M) if k in T[z]); var = False
            elif k < 28: var = any(w[28:]); expr = int(cS[k]) + sum(w[28 + z] * a[z, k] for z in range(M) if w[28 + z])
            else:
                z = k - 28; var = any(w[s] for s in self.V) or any(w[28 + z2] for z2 in range(M) if z2 != z)
                expr = sum(w[t] for t in T[z]) + sum(w[s] * a[z, s] for s in self.V if w[s]) + sum(w[28 + z2] * h[z, z2] for z2 in range(M) if z2 != z and w[28 + z2])
            if not var:
                t = int(expr); terms.append(t * t + (w[k] - 2 * a_ - 1) * t)
            else:
                t = m.NewIntVar(-80, 80, ""); m.Add(t == expr); sq = m.NewIntVar(0, 6400, ""); m.AddMultiplicationEquality(sq, [t, t])
                terms.append(sq + (w[k] - 2 * a_ - 1) * t)
        rhs = 12 * sum(x * x for x in w) + 2 * sum(w) ** 2 - 14 * (2 * a_ + 1) * sum(w) + (99 - self.n) * a_ * (a_ + 1)
        m.Add(sum(terms) <= rhs); self.cuts.append({"w": w, "a": int(a_)})

def shrink(Ap, w, a, rng):
    w = np.array(w); changed = True
    while changed:
        changed = False
        for k in rng.sample(list(np.nonzero(w)[0]), int(np.count_nonzero(w))):
            for new in (0, w[k] - np.sign(w[k])):
                w2 = w.copy(); w2[k] = new
                if ST.phi_direct(Ap, w2, a) < 0: w, changed = w2, True; break
    return w

def run(d, p, q, rng, rounds=40, tl=120, workers=4, percut=8):
    S = DoubleStar(d, p, q); t0 = time.time()
    for it in range(rounds):
        sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_workers = workers; sv.parameters.random_seed = it
        st = sv.Solve(S.m)
        if st == cp_model.INFEASIBLE: return "no double star", it, len(S.cuts), time.time() - t0, S
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return "solver undecided", it, len(S.cuts), time.time() - t0, S
        Ap = S.adjacency(sv); found = {}
        for k in range(percut):
            val, w, a_ = ST.witness(Ap, rng, restarts=25)
            if val < 0: w2 = shrink(Ap, w, a_, rng); found[(a_, tuple(int(x) for x in w2))] = 1
        if not found: return "double star without witness", it, len(S.cuts), time.time() - t0, S
        for (a_, w2) in found: S.add_cut(list(w2), a_)
    return "undecided (round limit)", rounds, len(S.cuts), time.time() - t0, S

if __name__ == "__main__":
    fn = sys.argv[1]; R = int(sys.argv[2]); TL = float(sys.argv[3]); rng = random.Random(3)
    for sid in map(int, sys.argv[4:]):
        d = I.load(fn, sid)
        for p, q in itertools.combinations(range(3), 2):
            st, it, nc, t, S = run(d, p, q, rng, R, TL)
            print(f"support {sid} (delta {d['delta']}), positives {'ABC'[p]}{'ABC'[q]}: {S.M} vertices; {st} after {it} round(s), {nc} cuts  [{t:.0f}s]", flush=True)
            if st == "no double star": break
