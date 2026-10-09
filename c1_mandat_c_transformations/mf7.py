"""Modular forms on Gamma_0(7), trivial character, even weight, as exact q-expansions (Python integers / Fractions).
Generators: h^2 (h = theta series of the binary form x^2+xy+2y^2, weight 1, character chi_{-7}),
E4(tau), E4(7 tau), E6(tau), E6(7 tau).  Fricke involution with the convention of note 167:
    (f|_k W7)(tau) = 7^(-k/2) tau^(-k) f(-1/(7 tau)),
    h^2 -> -h^2,   E_k(tau) -> 7^(k/2) E_k(7 tau),   E_k(7 tau) -> 7^(-k/2) E_k(tau).
A monomial is (a, b, c, d, e) = h^(2a) E4^b E4(7.)^c E6^d E6(7.)^e, of weight 2a + 4(b+c) + 6(d+e)."""
from fractions import Fraction as Fr
import itertools, json

N = 84


def mul(f, g):
    r = [0] * (N + 1)
    for i, x in enumerate(f):
        if x:
            for j in range(0, N + 1 - i):
                y = g[j]
                if y: r[i + j] += x * y
    return r


def power(f, k):
    r = [1] + [0] * N
    for _ in range(k): r = mul(r, f)
    return r


def sigma(n, k): return sum(d ** k for d in range(1, n + 1) if n % d == 0)
def dil(f, m): return [f[i // m] if i % m == 0 else 0 for i in range(N + 1)]


H1 = [0] * (N + 1)
B = int((4 * N) ** 0.5) + 3
for x in range(-B, B + 1):
    for y in range(-B, B + 1):
        v = x * x + x * y + 2 * y * y
        if v <= N: H1[v] += 1
H2 = mul(H1, H1)
E4 = [1] + [240 * sigma(n, 3) for n in range(1, N + 1)]
E6 = [1] + [-504 * sigma(n, 5) for n in range(1, N + 1)]
E4s, E6s = dil(E4, 7), dil(E6, 7)
GEN = [H2, E4, E4s, E6, E6s]


def monomials(k):
    out = []
    for a in range(k // 2 + 1):
        for b in range(k // 4 + 1):
            for c in range(k // 4 + 1):
                for d in range(k // 6 + 1):
                    for e in range(k // 6 + 1):
                        if 2 * a + 4 * (b + c) + 6 * (d + e) == k: out.append((a, b, c, d, e))
    return out


def series(m):
    r = [1] + [0] * N
    for g, p in zip(GEN, m): r = mul(r, power(g, p))
    return r


def fricke(m):
    """image of the monomial m under W7: (coefficient, monomial)"""
    a, b, c, d, e = m
    return Fr(-1) ** a * Fr(7) ** (2 * b - 2 * c + 3 * d - 3 * e), (a, c, b, e, d)


def dim(k): return 1 + 2 * (k // 3)          # dim M_k(Gamma_0(7)), k even >= 2


def rref(rows):
    """row reduce a list of Fraction rows; returns (reduced rows, pivot columns, transformation rows)"""
    rows = [list(map(Fr, r)) for r in rows]; n = len(rows)
    T = [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
    piv = []; r = 0
    for col in range(len(rows[0])):
        p = next((i for i in range(r, n) if rows[i][col] != 0), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]; T[r], T[p] = T[p], T[r]
        iv = 1 / rows[r][col]; rows[r] = [x * iv for x in rows[r]]; T[r] = [x * iv for x in T[r]]
        for i in range(n):
            if i != r and rows[i][col] != 0:
                f = rows[i][col]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]; T[i] = [x - f * y for x, y in zip(T[i], T[r])]
        piv.append(col); r += 1
        if r == n: break
    return rows[:r], piv, T[:r]


class Space:
    """M_k(Gamma_0(7)) with a basis of monomials, q-expansions and the Fricke matrix in that basis."""
    def __init__(self, k):
        self.k = k; mons = monomials(k); ser = {m: series(m) for m in mons}
        # choose dim(k) independent monomials
        chosen = []; mat = []
        for m in mons:
            trial = mat + [ser[m][:3 * dim(k)]]
            if len(rref(trial)[0]) == len(trial): chosen.append(m); mat = trial
            if len(chosen) == dim(k): break
        assert len(chosen) == dim(k), (k, len(chosen), dim(k))
        self.mons = chosen; self.ser = [ser[m] for m in chosen]
        # Fricke matrix: image of basis element i = sum_j W[i][j] basis_j
        self.W = []
        for m in chosen:
            cf, m2 = fricke(m); self.W.append(self.coords(ser[m2] if m2 in ser else series(m2), scale=cf))
    def coords(self, f, scale=Fr(1)):
        """coordinates of the q-series f (in M_k) in the monomial basis"""
        d = len(self.ser); P = 3 * d
        aug = [[Fr(self.ser[j][n]) for j in range(d)] + [Fr(f[n])] for n in range(P)]
        red, piv, _ = rref(aug)
        assert piv == list(range(d)), "not in the space"
        return [scale * red[j][d] for j in range(d)]
    def expand(self, co):
        return [sum(c * s[n] for c, s in zip(co, self.ser)) for n in range(N + 1)]
    def fricke_coords(self, co):
        d = len(co); return [sum(co[i] * self.W[i][j] for i in range(d)) for j in range(d)]


if __name__ == "__main__":
    for k in (2, 4, 6, 22, 24, 26):
        S = Space(k); print("weight", k, "dimension", len(S.mons))
    # check against the basis F_j of note 167: F_j | W7 = -7^(2j-14) F_(14-j)
    F = json.load(open("C:/home/researcher/Desktop/Nouveau/conway99-c1/data/codex_theta7_basis_q84.json"))
    S = Space(22); ok = True
    for j in range(15):
        co = S.coords(F[j]); im = S.expand(S.fricke_coords(co))
        ok &= all(im[n] == -Fr(7) ** (2 * j - 14) * F[14 - j][n] for n in range(N + 1))
    print("Fricke on the basis F_j of note 167 reproduced:", ok)
