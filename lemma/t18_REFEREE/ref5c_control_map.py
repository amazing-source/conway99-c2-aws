# Positive control for my stage C: locate the two B1 matchings of the repo that carry the four 47-vertex survivors
# (#813 and #975 of lemma/t18/r2_tau_1.json) in MY list of orbit representatives, and write the sub-list of my stage-B triples.
# Only r2_tau_1.json (a data file, checked by two stage-1 programs and by my own recount) is read from the repo.
import json, itertools, sys
import numpy as np
REPO = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma\t18\r2_tau_1.json"
theirs = json.load(open(REPO))
mine = json.load(open("ref4_stageB_B1_0of1.json"))
DEF = [tuple(d) for d in mine["DEF"]]
assert [tuple(d) for d in theirs["DEF"]] == DEF, "different numbering of the deficient pairs"
reps = [tuple(r) for r in mine["reps"]]
B = np.zeros((9, 9), dtype=int)
for w in "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78".split():
    i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
auts = [q for q in itertools.permutations(range(9)) if all(B[q[i], q[j]] == B[i, j] for i in range(9) for j in range(i + 1, 9))]
idx = {d: k for k, d in enumerate(DEF)}
gd = [[idx[tuple(sorted((q[a], q[b])))] for (a, b) in DEF] for q in auts]
pos = {r: k for k, r in enumerate(reps)}
out = {}
for t in (813, 975):
    s = tuple(theirs["reps"][t])
    hit = None
    for g in gd:
        img = [0] * 18
        for a in range(18): img[g[a]] = g[s[a]]
        if tuple(img) in pos: hit = pos[tuple(img)]
    assert hit is not None
    out[t] = hit
    print(f"repo matching #{t} = my representative index {hit}; my stage-B triples on it: {sum(1 for x in mine['triples'] if x[0] == hit)}")
sub = dict(mine); sub["triples"] = [x for x in mine["triples"] if x[0] in out.values()]
json.dump(sub, open("ref5c_control_B1_triples.json", "w"))
print("total triples in the control:", len(sub["triples"]), "(the repo reports 170 on #813 and #975)")
