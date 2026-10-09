"""Nine-class programme: which EXTRA zeros (absence of a configuration) make a rank infeasible?
Each infeasible line is a statement 'rank r forces one of these configurations'.  Exact rational LP."""
import sys, time
from fractions import Fraction as Fr
import z9theta as Z, z9lp, exact_lp
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
HYP = {  # name: list of (side, class, exponent*9) set to zero / to the proved minimum
    "no 22-coclique (L class 2, norm 154/9)": [("X", 2, 77, 0)],
    "no regular 44-set (L class 4, norm 220/9)": [("X", 4, 110, 0)],
    "no L class-1 vector of norm 178/9": [("X", 1, 89, 0)],
    "no fractional vector of norm 22": [("X", 3, 99, 0)],
    "exactly 99 class-1 vectors of norm 28/9 (no ghost vertex)": [("T", 1, 14, 99)],
    "no M class-2 vector of norm 22/9": [("T", 2, 11, 0)],
    "no M class-4 vector of norm 34/9": [("T", 4, 17, 0)],
    "no root (b1 = 0)": [("T", 0, 9, 0)],
}
def run(r, names):
    Mo = Z.Model(r, N); Mo.geometry()
    for nm in names:
        for side, k, num9, val in HYP[nm]: Mo.fix(side, k, num9, val, nm)
    # same inequalities as z9lp.build, on the modified model
    import types
    orig = Z.Model
    class Fixed:  # monkeypatch so that build() reuses our model
        def __new__(cls, r_, N_): return Mo
    Z.Model = Fixed; geo = Mo.geometry; Mo.geometry = lambda: None
    try: _, free, G = z9lp.build(r, N)
    finally: Z.Model = orig; Mo.geometry = geo
    used = sorted({t for _, cf, _ in G for t in cf})
    triv = [lab for c0, cf, lab in G if not cf and c0 < 0]
    if triv: return "INFEASIBLE (constant inequality: " + triv[0] + ")"
    Gd = [(c0, [cf.get(t, Fr(0)) for t in used]) for c0, cf, _ in G]
    st, sol, it = exact_lp.solve(Gd)
    return "feasible" if st == "feasible" else "INFEASIBLE"
allnames = list(HYP)
for r in (37, 39, 41, 43):
    t0 = time.time()
    try: res = run(r, allnames)
    except AssertionError as e: res = "INFEASIBLE (equalities: " + str(e) + ")"
    print(f"rank {r}, all eight absences together: {res}  [{time.time()-t0:.0f}s]", flush=True)
