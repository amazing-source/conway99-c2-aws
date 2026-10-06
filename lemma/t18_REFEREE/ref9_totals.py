# Sums the per-part counters of my runs (ref5 stage C, ref7b profile (3,3,1)) and prints them next to the repo's figures.
import re, glob, ast, json
def last_dict(fn):
    for line in reversed(open(fn).read().splitlines()):
        m = re.search(r"\{.*\}", line)
        if m and "progress" not in line: return ast.literal_eval(m.group(0)), line
    return None, None
def tot(pattern):
    acc = {}; n = 0; to = []
    for fn in sorted(glob.glob(pattern)):
        d, line = last_dict(fn)
        assert d is not None, fn
        n += 1; to.append("timed_out=True" in line)
        for k, v in d.items(): acc[k] = acc.get(k, 0) + v
    return n, acc, any(to)
print("profile (2,5,0), stage C on ALL stage-B triples (my model, my code; PSD rejections in floating point):")
for g, exp in (("B0", "repo: 5595 triples, 901 pairs, 0 survivors"), ("B1", "repo: 4977 triples, 1015 pairs, 4 survivors (#813 [2,9],[3,6]; #975 [1,2],[3,6])")):
    n, a, to = tot(f"ref5_stageC_{g}_all_*of3.out")
    print(f"  {g}: parts {n}, any time-out {to}: triples {a['triples']}, pairs (tau,F) {a['pairs_tauF']}, survivors on 47 vertices {a['survivors']}   [{exp}]")
    for fn in sorted(glob.glob(f"ref5_stageC_{g}_full_all_*of3.json")):
        for ti, F, _ in json.load(open(fn))["survivors"]: print(f"       survivor: matching {ti}, F = {F}")
d, _ = last_dict("ref5_stageC_B2.out"); print(f"  B2: triples {d['triples']}, pairs {d['pairs_tauF']}, survivors {d['survivors']}   [repo: 196, 74, 0]")
print("profile (3,3,1), from my 39-vertex survivors:")
for g, exp in (("B0", "repo: 383 / 8639 / 23 / 52 budget-valid on 51 / 0"), ("B1", "repo: 481 / 27203 / 164 / 1839 budget-valid on 51 / 0; 10 pass the first matrix alone")):
    n, a, to = tot(f"ref7b_p331_ext_{g}_*of3.out")
    print(f"  {g}: configs on 39: {a['configs39']}; covers {a['covers']}; tables passing budgets on 45: {a['tables45_budget']}; "
          f"budgets+PSD on 45: {a['tables45_psd']}; budget-valid graphs on 51: {a['graphs51_budget']}; PSD on 51: {a['graphs51_psd']}; "
          f"PSD of 9(3I-A)+J alone on 51: {a['graphs51_psd_M1only']}   [{exp}]")
d, _ = last_dict("ref7_p331_ext_B2.out"); print(f"  B2: configs on 39: {d['configs39']}; covers {d['covers']}; tables passing budgets on 45: {d['tables45_budget']}   [repo: 7 / 88 or 44 / 0]")
