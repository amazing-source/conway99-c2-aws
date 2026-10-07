# Referee 2: compare MY stage-C survivors of B1 (myC_1_*.json) with the four graphs printed in Appendix B of the text,
# after bringing everything to a canonical form under Aut(B1) (my matching representatives are not those of the repo).
import json, glob
from common import *
import survivors as SV
adjB = Bgraph(1); D = deficient_pairs(adjB); idx = {U: k for k, U in enumerate(D)}
aut = automorphisms(adjB)
perms = [(g, [idx[tuple(sorted((g[U[0]], g[U[1]])))] for U in D]) for g in aut]
def canon(tau, F, H, W):
    best = None
    for g, pd in perms:
        t2 = [0] * 18
        for a in range(18): t2[pd[a]] = pd[tau[a]]
        F2 = tuple(sorted(min(pd[a], t2[pd[a]]) for a in F))
        H2 = tuple(sorted(tuple(sorted((pd[k], pd[l]))) for k, l in H))
        W2 = []
        for (i, j), K in W:
            v1 = (g[i], g[j], tuple(sorted(pd[k] for k in K)))
            v2 = (g[j], g[i], tuple(sorted(t2[pd[k]] for k in K)))
            W2.append(tuple(sorted([v1, v2])))
        c = (tuple(t2), F2, H2, tuple(sorted(W2)))
        if best is None or c < best: best = c
    return best
doc = {}
for sv in SV.SURV:
    tau = sv["tau"]
    F = sorted(set(min(k, tau[k]) for k in sv["Ap"]))
    doc[canon(tau, F, sv["H"], sv["W"])] = sv["name"]
print("Appendix B: %d graphs, %d canonical forms" % (len(SV.SURV), len(doc)))
mine = {}
ntr = 0
for fn in sorted(glob.glob("myC_1_*of*.json")):
    d = json.load(open(fn)); ntr += d["stats"]["triples"]
    for o in d["survivors"]:
        W = [((a[0][0], a[0][1]), a[1]) for a in o["W"]]
        c = canon(o["tau"], o["F"], [tuple(e) for e in o["H"]], W)
        mine.setdefault(c, []).append((o["tau_index_mine"], o["F"]))
print("my stage C of B1: triples processed %d; survivors %d; canonical forms %d" % (ntr, sum(len(v) for v in mine.values()), len(mine)))
for c, v in mine.items():
    print("   mine %s  <->  Appendix B: %s" % (v, doc.get(c, "NOT IN APPENDIX B")))
print("same set of canonical forms:", set(mine) == set(doc))
