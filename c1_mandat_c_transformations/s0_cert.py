"""S0 (rank 43, no root, no vector of L1 of norm 16..24): EXACT CERTIFICATE of
        (number of vectors of L_9 of class 2 and norm 208/9)  >=  10.
Prints every inequality used with its exact expression in the 7 free parameters and its exact multiplier, then re-checks the
identity  sum_i lam_i (c0_i + cf_i . t) = -1  from the printed data alone.     usage: s0_cert.py [N] [bound]"""
import sys, time, json
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
BOUND = int(sys.argv[2]) if len(sys.argv) > 2 else 9
t0 = time.time()
Mo = Z.Model(43, N); Mo.geometry()
for c in range(5):
    j = 0
    while 7 * (Z.RHO[c] + 9 * j) <= 9 * N:
        num9 = Z.RHO[c] + 9 * j
        a, b = Mo.var("X", c, 7 * num9), Mo.var("T", c, num9)
        if a is not None and b is not None: Mo.eq({a: Fr(1), b: Fr(-1)}, 0, "class equality")
        j += 1
Mo.fix("X", 0, 63, 0)                                    # S0: no root
for n in range(8, 13): Mo.fix("X", 0, 9 * n, 0)           # S0: no integral vector of norm 16..24
for n in (11, 12): Mo.fix("X", 3, 9 * n, 0)               # S0: no fractional vector of norm 22, 24
free, expr = z9lp.reduce(Mo)
top = 9 * (N - 9)
res = lambda side: (Z.RHO if side == "T" else Z.SIG)
E = lambda side, c, num9: expr[(side, c, (num9 - res(side)[c]) // 9)]
def nice(nm):
    side, c, j = nm; num9 = res(side)[c] + 9 * j
    return f"{'Theta' if side == 'T' else 'Xi'}_{c}[{num9}/9]"
G = [(e[0], dict(e[1]), nice(nm) + " >= 0") for nm, e in expr.items() if z9lp.expo9(Mo, nm) <= top]
def comb(terms, const=0):
    c0 = Fr(const); cf = {}
    for coef, e in terms:
        c0 += coef * e[0]
        for t, v in e[1].items(): cf[t] = cf.get(t, Fr(0)) + coef * v
    return c0, {t: v for t, v in cf.items() if v != 0}
def addge(terms, const, label):
    c0, cf = comb(terms, const); G.append((c0, cf, label))
addge([(1, E("T", 3, 18))], -231, "Theta_3[18/9] >= 231   (lines)")
addge([(1, E("T", 1, 14))], -99, "Theta_1[14/9] >= 99   (vertices)")
addge([(1, E("T", 2, 20))], -693, "Theta_2[20/9] >= 693   (edges)")
addge([(1, E("T", 0, 27))], -8316, "Theta_0[27/9] >= 8316   (differences of non-adjacent vertices)")
addge([(1, E("T", 3, 18)), (-22, E("X", 2, 77))], -231, "Theta_3[18/9] >= 231 + 22 Xi_2[77/9]   (22 profile-C vectors per 22-coclique)")
c0, cf = E("X", 2, 104)
G.append((Fr(BOUND) - c0, {t: -v for t, v in cf.items()}, f"HYPOTHESIS  Xi_2[104/9] <= {BOUND}"))
used = sorted({t for _, cf, _ in G for t in cf})
rows = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in G]
st, lam, it = exact_lp.solve(rows)
print(f"truncation {N}; free parameters ({len(used)}): {[nice(free[t]) for t in used]}")
print(f"hypothesis Xi_2[104/9] <= {BOUND}: {st}  [{time.time()-t0:.0f}s]")
if st == "infeasible":
    out = []
    print("\ninequalities used (expression in the free parameters, in the order above) and exact multipliers:")
    for (c0, cf, lab), l in zip(G, lam):
        if l == 0: continue
        vec = [cf.get(t, Fr(0)) for t in used]
        print(f"  [{lab}]\n      = {c0}  +  {[str(v) for v in vec]}\n      multiplier {l}")
        out.append({"label": lab, "const": str(c0), "coef": [str(v) for v in vec], "multiplier": str(l)})
    # independent re-check from the printed data
    tot0 = sum(Fr(o["multiplier"]) * Fr(o["const"]) for o in out)
    totv = [sum(Fr(o["multiplier"]) * Fr(o["coef"][k]) for o in out) for k in range(len(used))]
    print("\nre-check: sum of multiplier x constant =", tot0, "; sum of multiplier x coefficients =", [str(x) for x in totv],
          "; all multipliers >= 0:", all(Fr(o["multiplier"]) >= 0 for o in out))
    json.dump({"statement": f"S0 => Xi_2[104/9] >= {BOUND + 1}", "truncation": N, "parameters": [nice(free[t]) for t in used], "rows": out},
              open(f"s0_cert_N{N}_b{BOUND}.json", "w"), indent=1)
else:
    print("   feasible point:", {nice(free[t]): str(x) for t, x in zip(used, lam)})
