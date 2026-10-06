# t18_B0_VERIFC / b1_coverage.py -- BOOKKEEPING + INPUT ADAPTER for B1 (no search, no test of the proof).
# Question: which r3_p250_1_*_BC.json files cover the 1259 matchings of B1 exactly once, and what is the stage-B triple list?
# Facts read in r3_p250.py (lines 420-445): a run works on the list `my` of matchings (index mod nparts == part, or the
# list R3_IDX; then the file name carries _idx<first index>), in that order; totals.tau = len(my); totals.tau_done = number of
# matchings finished; if the time limit cuts a matching the run stops there (timed_out True) and that matching may have left
# an INCOMPLETE set of H_stageB entries.  So a file certifies only the first tau_done matchings of its list.
# Lists: launch 1 = index mod 3; launch 2 = sorted(not done after 1)[g::3]; launch 3 = sorted(not done after 2)[g::2];
#        launch 4 = r3_left41_g<g>.txt; launch 5 = r3_last_g<g>.txt   (text files copied from SP\t18, written by r3_round4/5.py).
# Checks: totals.tau == len(list); file name idx == list[0]; the matchings appearing in H_stageB appear in list order and
#         only among the first tau_done (+1 if timed out) of the list; launch-3 lists == r3_left_g<g>.txt.
# Output (adapter): <out json> = {"timed_out": false, "H_stageB": [...]} holding, for every matching, the H_stageB entries of
#         the unique file that completed it (entries of cut matchings are dropped).  Nothing else is changed in an entry.
# Cross-check: that set against the union of the verifier's files r3v_B250_1_{0,1,2}of3.json (field "H").
# usage: python b1_coverage.py <dir with the copied r3 files> <dir with the verifier files> <out json>
import json, os, sys

D = sys.argv[1]; DV = sys.argv[2]; OUT = sys.argv[3]
NT = 1259
ALL = set(range(NT))


def load(fn):
    return json.load(open(os.path.join(D, fn)))


def txt(fn):
    return [int(x) for x in open(os.path.join(D, fn)).read().split(",")]


runs = []          # (launch, file name, list)
for g in range(3):
    runs.append((1, f"r3_p250_1_{g}of3_BC.json", [q for q in range(NT) if q % 3 == g]))
done = set()
def close_launch(launch):
    for (l, fn, lst) in runs:
        if l == launch:
            done.update(lst[:load(fn)["totals"]["tau_done"]])
close_launch(1)
left1 = sorted(ALL - done)
for g in range(3):
    lst = left1[g::3]
    runs.append((2, f"r3_p250_1_{g}of3_idx{lst[0]}_BC.json", lst))
close_launch(2)
left2 = sorted(ALL - done)
for g in range(2):
    lst = left2[g::2]
    assert lst == txt(f"r3_left_g{g}.txt"), "launch-3 list differs from r3_left_g*.txt"
    runs.append((3, f"r3_p250_1_{g}of2_idx{lst[0]}_BC.json", lst))
close_launch(3)
cov = json.load(open(os.path.join(D, "r3_coverage_B1_final.json")))
print(f"after launches 1-3: {len(done)} matchings completed; equal to r3_coverage_B1_final.json 'done': {sorted(done) == cov['done']}, "
      f"'not_done': {sorted(ALL - done) == cov['not_done']}")
for g in range(3):
    lst = txt(f"r3_left41_g{g}.txt")
    runs.append((4, f"r3_p250_1_{g}of3_idx{lst[0]}_BC.json", lst))
for g in range(3):
    lst = txt(f"r3_last_g{g}.txt")
    runs.append((5, f"r3_p250_1_{g}of5_idx{lst[0]}_BC.json", lst))

owner = {}
E = []; problems = []; dropped = 0
used = set()
print("launch  file                                   list  tau_done  timed_out  H_stageB  kept  dropped(cut matching)  matchings with triples kept")
for launch, fn, lst in runs:
    d = load(fn); used.add(fn)
    k = d["totals"]["tau_done"]
    if d["totals"]["tau"] != len(lst):
        problems.append(f"{fn}: totals.tau {d['totals']['tau']} != length of the reconstructed list {len(lst)}")
    if (not d["timed_out"]) != (k == len(lst)):
        problems.append(f"{fn}: timed_out {d['timed_out']} inconsistent with tau_done {k} of {len(lst)}")
    comp = lst[:k]
    for t in comp:
        if t in owner:
            problems.append(f"matching {t} completed by both {owner[t]} and {fn}")
        owner[t] = fn
    seq = []
    for e in d["H_stageB"]:
        if not seq or seq[-1] != e["tau"]:
            seq.append(e["tau"])
    pos = [lst.index(t) if t in lst else -1 for t in seq]
    if -1 in pos or pos != sorted(pos) or len(set(pos)) != len(pos) or (pos and pos[-1] > k - (0 if d["timed_out"] else 1)):
        problems.append(f"{fn}: the matchings of H_stageB do not follow the reconstructed list (positions {pos[:10]}..., tau_done {k})")
    cs = set(comp)
    kept = [e for e in d["H_stageB"] if e["tau"] in cs]
    dropped += len(d["H_stageB"]) - len(kept)
    E += kept
    print(f"  {launch}     {fn:38s} {len(lst):4d}  {k:8d}  {str(d['timed_out']):9s}  {len(d['H_stageB']):8d}  {len(kept):4d}  "
          f"{len(d['H_stageB']) - len(kept):6d}                 {len(set(e['tau'] for e in kept))}")
print(f"files used: {len(runs)} (launch 1: 3, launch 2: 3, launch 3: 2, launch 4: 3, launch 5: 3)")
others = sorted(f for f in os.listdir(D) if f.startswith("r3_p250_1_") and f.endswith(".json") and f not in used)
print("r3_p250_1_* files NOT used:", others)
for f in others:
    d = load(f)
    twin = [u for u in sorted(used) if open(os.path.join(D, u), "rb").read() == open(os.path.join(D, f), "rb").read()]
    print(f"     {f}: " + (f"byte-identical copy of {twin[0]}" if twin else
                           f"early trial ({d['totals']['tau']} matchings, part {d['part']} of {d['nparts']}, field H_stageB present: {'H_stageB' in d})"))
missing = sorted(ALL - set(owner))
print(f"matchings completed by exactly one used file: {len(owner)} of {NT}; by none: {len(missing)} {missing[:20]}")
if missing:
    problems.append(f"{len(missing)} matchings completed by no file")
Eset = set((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in E)
print(f"stage-B triples kept (each matching from the one file that completed it): {len(E)}, distinct {len(Eset)}, "
      f"in {len(set(t for t, _, _ in Eset))} matchings, {len(set((t, F) for t, F, _ in Eset))} pairs (tau, F); "
      f"entries dropped because their matching was cut by a time limit in that file: {dropped}")
V = []
for q in range(3):
    dv = json.load(open(os.path.join(DV, f"r3v_B250_1_{q}of3.json")))
    assert not dv["timed_out"] and dv["part"] == q and dv["nparts"] == 3
    V += [(e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in dv["H"]]
    if any(e["tau"] % 3 != q for e in dv["H"]):
        problems.append(f"verifier file {q}of3 holds a matching of another residue")
Vset = set(V)
print(f"verifier files r3v_B250_1_{{0,1,2}}of3.json: {len(V)} entries, distinct {len(Vset)}, in {len(set(t for t, _, _ in Vset))} matchings; "
      f"matchings per file {[json.load(open(os.path.join(DV, f'r3v_B250_1_{q}of3.json')))['stats']['tau'] for q in range(3)]}")
print(f"identical sets (enumerator exactly-once set == verifier set): {Eset == Vset}; only enumerator {len(Eset - Vset)}, only verifier {len(Vset - Eset)}")
if Eset != Vset:
    problems.append("enumerator exactly-once set differs from the verifier set")
if len(E) != len(Eset):
    problems.append("a triple appears twice in the kept entries")
for (a, b) in ((813, "813"), (975, "975")):
    print(f"   triples in matching #{b}: {sum(1 for t, _, _ in Eset if t == a)}  (from {owner[a]})")
for x in problems:
    print("PROBLEM:", x)
if not problems:
    json.dump({"timed_out": False, "made_by": "b1_coverage.py", "files": [fn for _, fn, _ in runs], "H_stageB": E}, open(OUT, "w"))
    print(f"written {OUT}: {len(E)} entries, timed_out False")
else:
    print("NOT written: problems above")
