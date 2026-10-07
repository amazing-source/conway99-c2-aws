# Small sanity checks of definitions and identities quoted in T18_PROOF.txt (not part of the proof).
import itertools, numpy as np
E = {0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
     1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
     2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78"}
for g in (0, 1, 2):
    B = np.zeros((9, 9), dtype=int)
    for w in E[g].split():
        i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
    assert (B.sum(0) == 4).all()
    C = B @ B
    cod = {}
    for i, j in itertools.combinations(range(9), 2):
        cod[(B[i, j], C[i, j])] = cod.get((B[i, j], C[i, j]), 0) + 1
    D = [(i, j) for i, j in itertools.combinations(range(9), 2) if C[i, j] == 1]
    nb = [set(np.nonzero(B[i])[0].tolist()) for i in range(9)]
    def R1(U, V):
        return all(len(nb[i] & set(V)) <= 1 for i in U) and all(len(nb[l] & set(U)) <= 1 for l in V)
    rect = [(a, b) for a, b in itertools.combinations(range(18), 2) if R1(D[a], D[b])]
    rin = [(a, b) for a, b in rect if not set(D[a]) & set(D[b])]
    # matchings with (R1) + (R2)
    ok = set(rect)
    cap = 2 - B
    cnt = np.zeros((9, 9), dtype=int)
    used = [False] * 18
    tot = [0]
    def rec():
        try:
            a = used.index(False)
        except ValueError:
            tot[0] += 1; return
        used[a] = True
        for b in range(a + 1, 18):
            if used[b] or (a, b) not in ok: continue
            cl = [(i, l) for i in D[a] for l in D[b]] + [(l, i) for i in D[a] for l in D[b]]
            for c in cl: cnt[c] += 1
            if all(cnt[c] <= cap[c] for c in cl):
                used[b] = True; rec(); used[b] = False
            for c in cl: cnt[c] -= 1
        used[a] = False
    rec()
    ev = np.round(np.linalg.eigvalsh(B.astype(float)), 4).tolist()
    print(f"B{g}: codegrees (adjacent?, codeg): {sorted(cod.items())}; deficient pairs {len(D)}; rectangles (R1) {len(rect)}; with U n V empty {len(rin)}; matchings (R1)+(R2) {tot[0]}")
    print("    spectrum", ev)
    print("    deficient pairs:", " ".join(f"{i}{j}" for i, j in D))
# arithmetic identities
import sympy as sp
t = sp.symbols('t')
expr = (576 - 2*t) - 8*(36 + 2*t) + 16*9 - 5*(144 - 4*t) + 6*54 - 2*t
print("(*) constant:", sp.expand(expr))
# min sum y^2
def miny(tt):
    return min(sum(v*v for v in y) for y in itertools.product(range(tt + 1), repeat=4) if sum(y) == tt)
print("2*min sum y_q^2:", {tt: 2*miny(tt) for tt in range(10)})
# spectrum bound
print("14*324/99 + 3*(18-324/99) =", sp.Rational(14*324, 99) + 3*(18 - sp.Rational(324, 99)))
print("55440 =", sp.factorial(9)//72 + sp.factorial(9)//12 + sp.factorial(9)//18)
