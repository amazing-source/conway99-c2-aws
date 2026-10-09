"""Z/9-refined theta programme (9 October 2026, mandate C).

NEW FACT USED.  The 3-part of the glue of the (-4)-eigenlattice is Z/9, and each of its classes has its own theta series:
  M side:  O = sqrt7 E(Z^99), classes k = (sum psi) mod 9;   Theta_k = number of vectors of O of class k by norm;
  L side:  L_9 = eigenvectors with all entries = c/9 mod 1, classes c;   Xi_c = number of vectors of class c by norm.
(L1 programme of notes 167-168:  theta_M = Theta_0 + 2 Theta_3,  theta_L1 = Xi_0 + 2 Xi_3.)
Gluing with A_8 (same discriminant form up to sign) gives the even lattices of rank 52 and level 7
  Lam = {(x, a) : class(x) = class(a)},   Pi = sqrt7 Lam^* = {(y, sqrt7 a') : class(y) = class(a')},
and for every zonal harmonic Z_m on the A_8 part (degree m, pole v)
  g_m  = sum_k w_k Theta_k(tau) theta_{k,m}(tau)              in M_(26+m)(Gamma_0(7)),
  gh_m = 7^(m/2) sum_c w_c Xi_c(tau) theta_{c,m}(7 tau)   =  - 7^((19-r)/2)  g_m | W_7 .
The lab's programme theta_pi.py is the single case m = 0, which mixes the classes; several m separate them.

Proved input used here (no hypothesis on the graph):
  L side zeros:  class 0: norms 2..12;  class 3: norms < 22;  class 1: norms < 178/9;  class 2: norms < 154/9;
                 class 4: norms < 220/9.
  M side:        class 0: 1 at norm 0, roots only in class 0;  class 1: nothing below 28/9, at least 99 at 28/9;
                 class 2: nothing below 22/9, at least 693 at 40/9;  class 3: no root, at least 231 at norm 4;
                 class 4: nothing below 34/9.
usage: z9theta.py r [N]"""
import sys, time
from fractions import Fraction as Fr
from flint import fmpq, fmpq_mat
import mf7, a8

RHO = {0: 0, 1: 5, 2: 2, 3: 0, 4: 8}      # M side: exponent of class k = (RHO[k] + 9 j) / 9
SIG = {0: 0, 1: 8, 2: 5, 3: 0, 4: 2}      # L side: exponent of class c = (SIG[c] + 9 j) / 9
W = {0: 1, 1: 2, 2: 2, 3: 2, 4: 2}
FUNCS = [(0, "r"), (4, "r"), (6, "r"), (6, "w"), (8, "r"), (8, "w")]
_spaces = {}


def space(k):
    if k not in _spaces:
        S = mf7.Space(k)
        V = [[sum(S.W[i][j] * S.ser[j][n] for j in range(len(S.ser))) for n in range(mf7.N + 1)] for i in range(len(S.ser))]
        _spaces[k] = (S, V)
    return _spaces[k]


class Model:
    def __init__(self, r, N):
        self.r, self.N = r, N
        self.names = []; self.index = {}
        for side, res in (("T", RHO), ("X", SIG)):
            for k in range(5):
                j = 0
                while res[k] + 9 * j <= 9 * N:
                    self._add((side, k, j)); j += 1
        for f in FUNCS:
            S, _ = space(26 + f[0])
            for i in range(len(S.ser)): self._add(("x", f, i))
        self.rows = []; self.rhs = []; self.labels = []
        self._modular()

    def _add(self, name): self.index[name] = len(self.names); self.names.append(name)
    def var(self, side, k, num9):
        """variable of class k with exponent num9/9 on side 'T' (M side) or 'X' (L side); None if not a legal exponent"""
        res = (RHO if side == "T" else SIG)[k]
        if num9 < res or (num9 - res) % 9: return None
        return self.index.get((side, k, (num9 - res) // 9))
    def eq(self, coeffs, rhs, label):
        self.rows.append(coeffs); self.rhs.append(Fr(rhs)); self.labels.append(label)

    def _modular(self):
        r, N = self.r, self.N
        c7 = Fr(7) ** Fr(19 - r, 2) if (19 - r) % 2 == 0 else None
        for f in FUNCS:
            m, pole = f; S, V = space(26 + m)
            th = {k: dict(a8.series(k, m, pole, N)) for k in range(5)}
            for n in range(N + 1):
                row = {}
                for i in range(len(S.ser)):
                    if S.ser[i][n]: row[self.index[("x", f, i)]] = Fr(S.ser[i][n])
                for k in range(5):
                    for E18, val in th[k].items():
                        num9 = 9 * n - E18 // 2 if E18 % 2 == 0 else None      # exponent of Theta_k = n - E18/18
                        if num9 is None: continue
                        v = self.var("T", k, num9)
                        if v is not None: row[v] = row.get(v, Fr(0)) - W[k] * val
                self.eq(row, 0, ("M", f, n))
                row = {}
                for i in range(len(S.ser)):
                    if V[i][n]: row[self.index[("x", f, i)]] = -c7 * Fr(V[i][n])
                for c in range(5):
                    for E18, val in th[c].items():
                        if (7 * E18) % 2: continue
                        num9 = 9 * n - 7 * E18 // 2                              # exponent of Xi_c = n - 7 E18/18
                        v = self.var("X", c, num9)
                        if v is not None: row[v] = row.get(v, Fr(0)) - Fr(7) ** (m // 2) * W[c] * val
                self.eq(row, 0, ("L", f, n))

    def fix(self, side, k, num9, value, label=""):
        v = self.var(side, k, num9)
        if v is not None: self.eq({v: Fr(1)}, value, label or f"{side}{k}[{num9}/9]={value}")

    def geometry(self):
        N9 = 9 * self.N
        self.fix("T", 0, 0, 1); self.fix("X", 0, 0, 1)
        for n in range(1, 7): self.fix("X", 0, 9 * n, 0)                       # L: no norm < 14
        for n in range(1, 11): self.fix("X", 3, 9 * n, 0)                      # fractional class of L1: norm >= 22
        for num9 in range(8, 89, 9): self.fix("X", 1, num9, 0)                 # class 1: norm >= 178/9  (exponent >= 89/9)
        for num9 in range(5, 77, 9): self.fix("X", 2, num9, 0)                 # class 2: norm >= 154/9  (exponent >= 77/9)
        for num9 in range(2, 110, 9): self.fix("X", 4, num9, 0)                # class 4: norm >= 220/9  (exponent >= 110/9)
        self.fix("T", 3, 9, 0)                                                 # roots of M are of integral type
        self.fix("T", 3, 0, 0); self.fix("X", 3, 0, 0)                         # no zero vector in the classes +-3
        self.fix("T", 1, 5, 0); self.fix("T", 2, 2, 0); self.fix("T", 4, 8, 0)

    def matrix(self):
        nv = len(self.names)
        M = fmpq_mat(len(self.rows), nv + 1)
        for i, (row, b) in enumerate(zip(self.rows, self.rhs)):
            for j, c in row.items(): M[i, j] = fmpq(c.numerator, c.denominator)
            M[i, nv] = fmpq(b.numerator, b.denominator)
        return M

    def solve(self):
        """rref of the augmented system; returns (consistent, pivots, free variables, R)"""
        M = self.matrix(); R, rk = M.rref(); nv = len(self.names)
        piv = []
        for i in range(rk):
            j = next(j for j in range(nv + 1) if R[i, j] != 0); piv.append(j)
        consistent = nv not in piv
        free = [j for j in range(nv) if j not in set(piv)]
        return consistent, piv, free, R


if __name__ == "__main__":
    r = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    t0 = time.time(); Mo = Model(r, N)
    print(f"rank {r}, truncation {N}: {len(Mo.names)} unknowns ({sum(1 for n in Mo.names if n[0]=='T')} M-side, {sum(1 for n in Mo.names if n[0]=='X')} L-side, {sum(1 for n in Mo.names if n[0]=='x')} form coordinates), {len(Mo.rows)} modular equations  [{time.time()-t0:.0f}s]", flush=True)
    ok, piv, free, R = Mo.solve()
    print(f"modularity alone: consistent {ok}, rank {len(piv)}, free parameters {len(free)}  [{time.time()-t0:.0f}s]", flush=True)
    Mo.geometry(); ok, piv, free, R = Mo.solve()
    print(f"with the proved zeros: consistent {ok}, rank {len(piv)}, free parameters {len(free)}  [{time.time()-t0:.0f}s]")
    print("free variables:", [Mo.names[j] for j in free])
