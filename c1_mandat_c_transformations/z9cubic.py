"""Odd (cubic) nine-class programme.  P_3(x) = sum_v x_v^3 is harmonic on the (-4)-eigenspace and odd, so its theta
series on the classes +-1, +-2, +-3, +-4 of the 3-glue do not vanish:
   M side:  T_k = sum over x in O of class k of P_3(sqrt7 x) q^(x^2/2)        (k = 1..4, T_(-k) = -T_k)
   L side:  X_c = sum over y in L_9 of class c of P_3(y) q^(y^2/2)
With an ODD zonal harmonic Z_m on the A_8 part:  g_m = 2 sum_k T_k theta_{k,m} in S_(29+m)(Gamma_0(7)),
   2 sum_c X_c(tau) theta_{c,m}(7 tau) = - 7^((16 - r - m)/2)  g_m | W_7.
No positivity; exact linear algebra.  Question: after the proved zeros, are there exact relations among the first
non-zero moments (vertices, edges, lines, 22-cocliques, fractional norm 22, regular 44-sets)?      usage: z9cubic.py r [N]"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, a8
import z9theta as Z

FUNCS = [(3, "r"), (3, "w"), (5, "r"), (5, "w"), (7, "r"), (7, "w"), (9, "r"), (9, "w")]
RHO, SIG = Z.RHO, Z.SIG


class Cubic:
    def __init__(self, r, N, funcs=FUNCS):
        self.r, self.N = r, N; self.names = []; self.index = {}; self.rows = []; self.rhs = []
        for side, res in (("T", RHO), ("X", SIG)):
            for k in range(1, 5):
                j = 0
                while res[k] + 9 * j <= 9 * N: self._add((side, k, j)); j += 1
        for f in funcs:
            S, _ = Z.space(29 + f[0])
            for i in range(len(S.ser)): self._add(("x", f, i))
        for f in funcs:
            m, pole = f; S, V = Z.space(29 + m); c7 = Fr(7) ** ((16 - r - m) // 2)
            assert (16 - r - m) % 2 == 0
            th = {k: dict(a8.series(k, m, pole, N)) for k in range(1, 5)}
            for n in range(N + 1):
                row = {self.index[("x", f, i)]: Fr(S.ser[i][n]) for i in range(len(S.ser)) if S.ser[i][n]}
                for k in range(1, 5):
                    for E18, val in th[k].items():
                        v = self.var("T", k, 9 * n - E18 // 2)
                        if v is not None: row[v] = row.get(v, Fr(0)) - 2 * val
                self.rows.append(row); self.rhs.append(Fr(0))
                row = {self.index[("x", f, i)]: -c7 * Fr(V[i][n]) for i in range(len(S.ser)) if V[i][n]}
                for c in range(1, 5):
                    for E18, val in th[c].items():
                        v = self.var("X", c, 9 * n - 7 * E18 // 2)
                        if v is not None: row[v] = row.get(v, Fr(0)) - 2 * val
                self.rows.append(row); self.rhs.append(Fr(0))
    def _add(self, name): self.index[name] = len(self.names); self.names.append(name)
    def var(self, side, k, num9):
        res = (RHO if side == "T" else SIG)[k]
        if num9 < res or (num9 - res) % 9: return None
        return self.index.get((side, k, (num9 - res) // 9))
    def fix(self, side, k, num9, value=0):
        v = self.var(side, k, num9)
        if v is not None: self.rows.append({v: Fr(1)}); self.rhs.append(Fr(value))
    def zeros(self):
        for n in range(0, 11): self.fix("X", 3, 9 * n)
        for num9 in range(8, 89, 9): self.fix("X", 1, num9)
        for num9 in range(5, 77, 9): self.fix("X", 2, num9)
        for num9 in range(2, 110, 9): self.fix("X", 4, num9)
        self.fix("T", 3, 0); self.fix("T", 3, 9); self.fix("T", 1, 5); self.fix("T", 2, 2); self.fix("T", 4, 8)
    def reduce(self):
        names = self.names
        expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
        xs = [i for i, n in enumerate(names) if n[0] == "x"]
        cl = sorted([i for i, n in enumerate(names) if n[0] != "x"], key=lambda i: -expo(names[i]))
        order = xs + cl; pos = {v: p for p, v in enumerate(order)}; nv = len(names)
        M = fmpq_mat(len(self.rows), nv + 1)
        for i, (row, b) in enumerate(zip(self.rows, self.rhs)):
            for j, c in row.items(): M[i, pos[j]] = fmpq(c.numerator, c.denominator)
            M[i, nv] = fmpq(b.numerator, b.denominator)
        R, rk = M.rref()
        piv = [next(j for j in range(nv + 1) if R[i, j] != 0) for i in range(rk)]
        assert nv not in piv, "inconsistent"
        free = [p for p in range(nv) if p not in set(piv)]
        return [names[order[p]] for p in free], rk


if __name__ == "__main__":
    r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    t0 = time.time()
    # sanity of the odd zonal series: 4 x 4 leading matrix and its determinant
    C = Cubic(r, N); free0, rk0 = C.reduce()
    top = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2] > 9 * (N - 9)
    print(f"rank {r}, N {N}: modularity alone: {len(free0)} free, of which {sum(1 for f in free0 if f[0] != 'x' and top(f))} truncation-edge unknowns  [{time.time()-t0:.0f}s]")
    C.zeros(); free, rk = C.reduce()
    inner = [f for f in free if not (f[0] != 'x' and top(f))]
    print(f"with the proved zeros: {len(free)} free, {len(inner)} genuine")
    print("genuine free parameters:", [(s, k, f"{(RHO if s == 'T' else SIG)[k] + 9 * j}/9") if s != 'x' else (s, k, j) for s, k, j in inner])
