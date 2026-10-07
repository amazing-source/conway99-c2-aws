# Referee 2: orbits of MY 5595 stage-B triples of B0 under the stabilisers of the matchings in Aut(B0)
# (the reduction used by program E for B0, section 8.4), and comparison of my set of triples with the repository's
# sets (V: r3v_B250_0_*.json; R: ref4_stageB_B0_0of1.json) after bringing every triple to a canonical form under Aut(B).
import json, glob, sys
from collections import Counter
from common import *
s_ = int(sys.argv[1])
adjB = Bgraph(s_); D = deficient_pairs(adjB); idx = {U: k for k, U in enumerate(D)}
aut = automorphisms(adjB)
perms = [[idx[tuple(sorted((g[U[0]], g[U[1]])))] for U in D] for g in aut]
REPS = [tuple(t) for t in json.load(open("my_tau_%d.json" % s_))["orbit_reps"]]
TR = []
for fn in sorted(glob.glob("myB_%d_*.json" % s_)):
    if s_ == 2 and fn != "myB_2_0_528.json": continue
    TR += json.load(open(fn))["triples"]
def act(pd, tau, F, H):
    t2 = [0] * 18
    for a in range(18): t2[pd[a]] = pd[tau[a]]
    F2 = tuple(sorted(min(pd[a], t2[pd[a]]) for a in F))
    H2 = tuple(sorted(tuple(sorted((pd[k], pd[l]))) for k, l in H))
    return tuple(t2), F2, H2
def canon(tau, F, H):
    return min(act(pd, tau, F, H) for pd in perms)
mine = Counter()
S = set((ti, tuple(F), tuple(tuple(e) for e in H)) for ti, F, H in TR)
print("B%d: my stage-B triples: %d (distinct %d)" % (s_, len(TR), len(S)))
# orbits under stabilisers
stab = {}
orb = 0; seen = set(); closed = True; sizes = Counter()
for (ti, F, H) in sorted(S):
    if (ti, F, H) in seen: continue
    tau = REPS[ti]
    if ti not in stab:
        stab[ti] = [pd for pd in perms if all(pd[tau[a]] == tau[pd[a]] for a in range(18))]
    O = set()
    for pd in stab[ti]:
        t2, F2, H2 = act(pd, tau, F, H)
        assert t2 == tau
        O.add((ti, F2, H2))
    if not O <= S: closed = False
    seen |= O; orb += 1; sizes[len(O)] += 1
print("   closed under the stabilisers: %s ; orbits: %d ; stabiliser orders of the matchings carrying triples: %s"
      % (closed, orb, sorted(Counter(len(v) for v in stab.values()).items())))
for ti, F, H in S:
    mine[canon(REPS[ti], F, H)] += 1
print("   canonical forms under Aut(B) (mine): %d" % len(mine))
# repository sets
import os
REPO = r"C:\Users\RESEARCHER\Desktop\Nouveau\conway99-c2-aws\lemma"
rr = json.load(open(os.path.join(REPO, "t18", "r2_tau_%d.json" % s_)))["reps"]
def load_V(files):
    c = Counter()
    n = 0
    for fn in files:
        for e in json.load(open(fn))["H"]:
            tau = tuple(rr[e["tau"]]); F = tuple(e["F"])
            H = tuple((k, l) for k in range(18) for l in range(k + 1, 18) if (e["H"][k] >> l) & 1)
            c[canon(tau, F, H)] += 1; n += 1
    return c, n
vf = {0: [os.path.join(REPO, "t18_B0", "r3v_B250_0_0of1.json"), os.path.join(REPO, "t18_B0", "r3v_B250_0_0of1_t418.json")],
      1: [os.path.join(REPO, "t18", "r3v_B250_1_%dof3.json" % q) for q in range(3)],
      2: [os.path.join(REPO, "t18_B2", "r3v_B250_2_0of1.json")]}[s_]
cv, nv = load_V(vf)
print("   verifier V files: %d triples, %d canonical forms; identical multisets of canonical forms (mine vs V): %s"
      % (nv, len(cv), cv == mine))
