"""Even (quartic) nine-class programme.  For a harmonic polynomial P of even degree d > 0 on the (-4)-eigenspace
(here d = 4, P_T(y) = sum over the 231 lines of y(l)^4 - (18/161)|y|^4):
   M side:  T_k = sum over x in O of class k of P(sqrt7 x) q^(x^2/2)        (k = 0..4, T_(-k) = T_k)
   L side:  X_c = sum over y in L_9 of class c of P(y) q^(y^2/2)
With an even zonal harmonic Z_m on the A_8 part:   g_m = sum_k w_k T_k theta_{k,m}  in S_(26+d+m)(Gamma_0(7)),
   sum_c w_c X_c(tau) theta_{c,m}(7 tau) = - 7^((19 - r - m - d)/2)  g_m | W_7.
(Same rule as the degree-0, degree-1 and degree-3 systems: z9theta.py, z9lin.py, z9cubic.py.)"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, a8
import z9theta as Z

FUNCS = [(0, "r"), (4, "r"), (6, "r"), (6, "w"), (8, "r"), (8, "w")]
RHO, SIG, W = Z.RHO, Z.SIG, Z.W


class Even:
    def __init__(self, r, N, d=4, funcs=FUNCS):
        self.r, self.N, self.d = r, N, d; self.names = []; self.index = {}; self.rows = []; self.rhs = []
        for side, res in (("T", RHO), ("X", SIG)):
            for k in range(0, 5):
                j = 0
                while res[k] + 9 * j <= 9 * N: self._add((side, k, j)); j += 1
        for f in funcs:
            S, _ = Z.space(26 + d + f[0])
            for i in range(len(S.ser)): self._add(("x", f, i))
        for f in funcs:
            m, pole = f; S, V = Z.space(26 + d + m)
            assert (19 - r - m - d) % 2 == 0
            c7 = Fr(7) ** ((19 - r - m - d) // 2)
            th = {k: dict(a8.series(k, m, pole, N)) for k in range(0, 5)}
            for n in range(N + 1):
                row = {self.index[("x", f, i)]: Fr(S.ser[i][n]) for i in range(len(S.ser)) if S.ser[i][n]}
                for k in range(0, 5):
                    for E18, val in th[k].items():
                        if E18 % 2: continue
                        v = self.var("T", k, 9 * n - E18 // 2)
                        if v is not None: row[v] = row.get(v, Fr(0)) - W[k] * val
                self.rows.append(row); self.rhs.append(Fr(0))
                row = {self.index[("x", f, i)]: -c7 * Fr(V[i][n]) for i in range(len(S.ser)) if V[i][n]}
                for c in range(0, 5):
                    for E18, val in th[c].items():
                        if (7 * E18) % 2: continue
                        v = self.var("X", c, 9 * n - 7 * E18 // 2)
                        if v is not None: row[v] = row.get(v, Fr(0)) - W[c] * val
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
        """proved zeros (no vector there): same layers as for the counts; the zero vector contributes P(0) = 0"""
        self.fix("T", 0, 0); self.fix("X", 0, 0)
        for n in range(1, 7): self.fix("X", 0, 9 * n)
        for n in range(0, 11): self.fix("X", 3, 9 * n)
        for num9 in range(8, 89, 9): self.fix("X", 1, num9)
        for num9 in range(5, 77, 9): self.fix("X", 2, num9)
        for num9 in range(2, 110, 9): self.fix("X", 4, num9)
        self.fix("T", 3, 0); self.fix("T", 3, 9); self.fix("T", 1, 5); self.fix("T", 2, 2); self.fix("T", 4, 8)
    def reduce(self):
        """returns (free names, {class variable: {free index: coef}}) ; the system is homogeneous"""
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
        if nv in piv: return None, None
        pset = set(piv); freecols = [p for p in range(nv) if p not in pset]; fidx = {p: t for t, p in enumerate(freecols)}
        expr = {}
        for i, p in enumerate(piv):
            nm = names[order[p]]
            if nm[0] == "x": continue
            expr[nm] = (Fr(int(R[i, nv].p), int(R[i, nv].q)), {fidx[q]: -Fr(int(R[i, q].p), int(R[i, q].q)) for q in freecols if R[i, q] != 0})
        for q in freecols:
            nm = names[order[q]]
            if nm[0] != "x": expr[nm] = (Fr(0), {fidx[q]: Fr(1)})
        return [names[order[q]] for q in freecols], expr


if __name__ == "__main__":
    r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    t0 = time.time(); Q = Even(r, N); Q.zeros(); free, expr = Q.reduce()
    expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
    inner = [f for f in free if not (f[0] != "x" and expo(f) > 9 * (N - 9))]
    print(f"rank {r}, N {N}: quartic nine-class system with the proved zeros: {len(free)} free, {len(inner)} genuine  [{time.time()-t0:.0f}s]")
    print("genuine free:", [(s, k, f"{expo((s, k, j))}/9") if s != "x" else (s, k, j) for s, k, j in inner])
