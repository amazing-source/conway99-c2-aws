"""Degree-0 theta programme of notes 167-168 (conway99-c1) as an exact rational LP, usable in-process.
Variables: c_1..c_7 (free coordinates of theta_L1 in the basis F_j).  All data exact (Fractions).
    T = Theta(r, nmax)        builds a_n, b_n as affine forms and the standard inequalities
    T.feasible(extra)         extra = list of affine forms (>= 0), built with T.form("a9"), T.le("a9", 100) ...
    T.minimum(name, extra)    smallest integer X such that  name <= X  is feasible (bisection, exact)"""
import json, sys
from fractions import Fraction as Fr
import exact_lp

F = json.load(open("C:/home/researcher/Desktop/Nouveau/conway99-c1/data/codex_theta7_basis_q84.json"))


class Theta:
    def __init__(self, r, nmax=40, standard=True):
        self.r = r; self.nmax = nmax; alpha = r - 1
        cs = [[Fr(0)] * 8 for _ in range(15)]
        cs[0][0] = Fr(7) ** (25 - alpha // 2)
        for j in range(1, 8): cs[j][j] = Fr(1)
        for n in range(7):
            j = 14 - n
            tot = [sum(cs[k][t] * F[k][n] for k in range(j + 1, 15)) for t in range(8)]
            cs[j] = [Fr(int(n == 0 and t == 0)) - tot[t] for t in range(8)]
        ds = [[x * Fr(7) ** (alpha // 2 + 3 - 2 * i) for x in cs[14 - i]] for i in range(15)]
        ex = lambda co, n: [sum(co[j][t] * F[j][n] for j in range(15)) for t in range(8)]
        self.a = [ex(cs, n) for n in range(nmax + 1)]; self.b = [ex(ds, n) for n in range(nmax + 1)]
        self.cs, self.ds = cs, ds
        assert self.a[0] == [1] + [0] * 7 and all(self.a[n] == [0] * 8 for n in range(1, 7))
        self.G = []; self.labels = []
        if standard: self.standard()

    # affine forms are lists of 8 Fractions (constant first)
    def form(self, name):
        k = int(name[1:]); return list(self.a[k] if name[0] == "a" else self.b[k])
    @staticmethod
    def lin(*terms):
        """lin((coef, form), ..., const) -> affine form"""
        out = [Fr(0)] * 8
        for t in terms:
            if isinstance(t, tuple):
                c, f = t
                for i in range(8): out[i] += Fr(c) * f[i]
            else: out[0] += Fr(t)
        return out
    def ge(self, f, label): self.G.append((f[0], f[1:])); self.labels.append(label)
    def le_form(self, name, X): return self.lin((-1, self.form(name)), X)
    def ge_form(self, name, X): return self.lin((1, self.form(name)), -X)

    def standard(self):
        a, b, lin = self.a, self.b, self.lin
        for n in range(7, self.nmax + 1): self.ge(a[n], f"a{n}>=0")
        for n in range(1, self.nmax + 1): self.ge(b[n], f"b{n}>=0")
        self.ge(lin((-1, a[7]), 990), "a7<=990")
        self.ge(lin((-7, a[7]), (-8, a[8]), 55440), "7a7+8a8<=55440")
        self.ge(lin((-1, b[1]), 44), "b1<=44")
        self.ge(lin((1, b[2]), (-41, b[1]), -462), "b2>=462+41b1")
        self.ge(lin((1, b[3]), -(45964 if self.r >= 37 else 24948)), "b3>=known")
        self.ge(lin((1, b[4]), -2729034), "b4>=2729034")
        self.ge(lin((1, b[5]), -18001368), "b5>=18001368")
        for k in range(1, self.nmax // 7 + 1): self.ge(lin((1, a[7 * k]), (-1, b[k])), f"a{7*k}>=b{k}")

    def solve(self, extra=()):
        G = self.G + [(f[0], f[1:]) for f in extra]
        return exact_lp.solve(G)
    def feasible(self, extra=()): return self.solve(extra)[0] == "feasible"
    def minimum(self, f, extra=(), hi=10 ** 12):
        """smallest integer X with  f <= X  feasible (f an affine form), or None if infeasible even at hi"""
        cap = lambda X: self.lin((-1, f), X)
        if not self.feasible(list(extra) + [cap(hi)]): return None
        lo = -1
        if self.feasible(list(extra) + [cap(0)]):
            # may be negative-unbounded only if f can be < 0; all our forms are counts >= 0
            return 0
        lo = 0
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.feasible(list(extra) + [cap(mid)]): hi = mid
            else: lo = mid
        return hi
    def maximum(self, f, extra=(), hi=10 ** 15):
        """largest integer X with  f >= X  feasible, or 'unbounded' beyond hi"""
        flo = lambda X: self.lin((1, f), -X)
        if self.feasible(list(extra) + [flo(hi)]): return "unbounded"
        if not self.feasible(list(extra) + [flo(0)]): return None
        lo = 0
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.feasible(list(extra) + [flo(mid)]): lo = mid
            else: hi = mid
        return lo


if __name__ == "__main__":
    import time
    for r in (35, 37, 39, 41, 43):
        t0 = time.time(); T = Theta(r, 40)
        print(r, "feasible" if T.feasible() else "INFEASIBLE", f"{time.time()-t0:.1f}s", flush=True)
