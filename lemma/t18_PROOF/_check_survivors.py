# Transcription check for the appendix of T18_PROOF.txt (not part of the proof):
# reads the four B1 stage-C survivors from the repo outputs of c_mine.py and of r3_p250.py, prints them in the
# notation of the text, and recomputes the odd orbit determinant (fraction-free Bareiss, Python integers).
import json, glob, os, sys
from fractions import Fraction
REPO = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma"
td = json.load(open(os.path.join(REPO, "t18", "r2_tau_1.json")))
DEF = [tuple(d) for d in td["DEF"]]; reps = td["reps"]
print("DEF (B1):", " ".join(f"{k}:{a}{b}" for k, (a, b) in enumerate(DEF)))

def bareiss(M):
    M = [r[:] for r in M]; n = len(M); prev = 1; sign = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
            if sw is None: return 0
            M[k], M[sw] = M[sw], M[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]

def rank(M):
    M = [[Fraction(x) for x in r] for r in M]; n = len(M); r = 0
    for c in range(len(M[0])):
        piv = next((i for i in range(r, n) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(r + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r

def describe(sv, src):
    ti = sv["tau"]; tau = reps[ti]; F = sv["F"]; rows = sv["rows"]
    A = [[(rows[u] >> v) & 1 for v in range(47)] for u in range(47)]
    assert all(A[u][v] == A[v][u] for u in range(47) for v in range(47)) and not any(A[u][u] for u in range(47))
    print(f"--- matching #{ti}, F = {F}   [{src}]")
    print("   tau (pairs {k, tau k} of indices of DEF):", " ".join(f"{k}-{tau[k]}" for k in range(18) if k < tau[k]))
    print("   rectangles {U, tau U}:", " ".join(f"{DEF[k][0]}{DEF[k][1]}|{DEF[tau[k]][0]}{DEF[tau[k]][1]}" for k in range(18) if k < tau[k]))
    # checks of the structure
    for k in range(18):
        nb = [v for v in range(18) if A[19 + k][v]]
        assert sorted(nb) == sorted(list(DEF[k]) + [9 + j for j in DEF[tau[k]]])
    Ap = sorted(k for k in range(18) if A[18][19 + k])
    assert sorted(Ap) == sorted([k for o in F for k in (o, tau[o])])
    H = sorted((k, l) for k in range(18) for l in range(k + 1, 18) if A[19 + k][19 + l])
    print("   A_p (indices k of X_2 vertices adjacent to p):", Ap)
    print("   edges of H = A[X_2] (pairs of indices k):", " ".join(f"{k}-{l}" for k, l in H), f"  (t = {len(H)})")
    for c in range(5):
        w, sw = 37 + 2 * c, 38 + 2 * c
        i = [v for v in range(9) if A[w][v]]; j = [v - 9 for v in range(9, 18) if A[w][v]]
        K = [k for k in range(18) if A[w][19 + k]]; Ks = [k for k in range(18) if A[sw][19 + k]]
        assert len(i) == 1 and len(j) == 1 and A[w][18] and A[sw][18] and A[w][sw]
        assert sorted(Ks) == sorted(tau[k] for k in K)
        print(f"   w_{c}: type ({i[0]};{j[0]}), K = N(w) n X_2 = {K}; sigma w: type ({j[0]};{i[0]}), tau K = {sorted(Ks)}")
    # sigma
    sig = [9 + i for i in range(9)] + list(range(9)) + [18] + [19 + tau[k] for k in range(18)] + [37 + (c ^ 1) for c in range(10)]
    assert all(A[sig[u]][sig[v]] == A[u][v] for u in range(47) for v in range(47))
    # budgets
    for u in range(47):
        for v in range(u + 1, 47):
            c = sum(A[u][x] & A[v][x] for x in range(47))
            assert c <= 2 - A[u][v]
    R = list(range(9)) + [19 + k for k in range(18) if k < tau[k]] + [37 + 2 * c for c in range(5)]
    G = [[3 * (x == y) - A[x][y] + A[x][sig[y]] for y in R] for x in R]
    det = bareiss(G)
    # even part: e_p and e_x + e_sigma x, Gram w.r.t. M1 = 27I - 9A + J
    gens = [[18]] + [[x, sig[x]] for x in R]
    M1 = lambda u, v: 27 * (u == v) - 9 * A[u][v] + 1
    Ev = [[sum(M1(u, v) for u in g1 for v in g2) for g2 in gens] for g1 in gens]
    print(f"   checks: structure, sigma-invariance, budgets OK; odd matrix {len(R)}x{len(R)}: det = {det}, rank {rank(G)}; even matrix {len(gens)}x{len(gens)}: rank {rank(Ev)}")
    return (ti, tuple(F), tuple(rows))

seen = {}
for fn in sorted(glob.glob(os.path.join(REPO, "t18_B0_VERIFC", "B1", "c_mine_1_*of24.json"))):
    for sv in json.load(open(fn))["survivors"]:
        key = describe(sv, "c_mine.py: " + os.path.basename(fn))
        seen[key] = 1
enum = set()
for fn in sorted(glob.glob(os.path.join(REPO, "t18", "r3_p250_1_*_BC.json"))):
    for sv in json.load(open(fn))["survivors"]:
        if "rows" in sv:
            enum.add((sv["tau"], tuple(sv["F"]), tuple(sv["rows"][:47])))
print("distinct survivors: c_mine", len(seen), "; r3_p250", len(enum), "; identical sets:", set(seen) == enum)
