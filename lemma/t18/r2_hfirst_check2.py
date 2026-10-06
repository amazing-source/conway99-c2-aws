# Cross-check (1) of r2_hfirst.py, made precise:
# every budget-valid Y-table found by r2_stage2.py (an independent program: X_0-first, H from degrees) restricts to a
# configuration (F, H, A_z0) on Y1 that the PSD-free run of r2_hfirst.py (H-first) must list among its survivors.
# usage: python r2_hfirst_check2.py <stage2 json with rejected_examples> <nopsd hfirst json for the same tau>
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, sys.argv[1])))
h = json.load(open(os.path.join(here, sys.argv[2])))
M18 = (1 << 18) - 1
surv = set()
for s in h["survivors"]:
    rows = s["rows"]
    tau = s["tau"]
    Hrows = tuple((rows[19 + k] >> 19) & M18 for k in range(18))
    A0 = (rows[37] >> 19) & M18
    A1 = (rows[38] >> 19) & M18
    surv.add((tuple(tau), tuple(s["F"]), Hrows, frozenset((A0, A1))))
print("PSD-free H-first survivors loaded:", len(surv), "(total reported:", h["totals"]["survivors"], ")")
ok = 0
exs = d.get("rejected_examples", []) + d.get("examples", [])
for ex in exs:
    tau, Az, H, G, F = ex["tau"], ex["Az"], ex["H"], ex["G"], ex["F"]
    zin = [q for q in range(1, 9) if (G[0] >> q) & 1]
    key = (tuple(tau), tuple(F), tuple(H), frozenset(Az[q] for q in zin))
    present = key in surv
    ok += present
    print("   stage-2 table F =", F, " -> its (F, H, A_z0) is among the H-first survivors:", present)
print(f"{ok} of {len(exs)} found")
