# Reduce the stage-B triples (tau, F, H) of B0 modulo the stabiliser of tau in Aut(B0).
# An automorphism g of B0 fixing the matching tau maps the X_2 vertex k (type (DEF[k]; DEF[tau k])) to the vertex g.k,
# hence a configuration (tau, F, H) to (tau, gF, gH); the two configurations are isomorphic as partial graphs with sigma.
# Output: b0_stageB_reps.json (one triple per orbit, with the orbit size).
import json, itertools, collections, sys
EDGES = "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78"
B = [[0] * 9 for _ in range(9)]
for e in EDGES.split():
    a, b = int(e[0]), int(e[1]); B[a][b] = B[b][a] = 1
td = json.load(open("r2_tau_0.json"))
DEF = [tuple(d) for d in td["DEF"]]; reps = [tuple(r) for r in td["reps"]]
pos = {d: k for k, d in enumerate(DEF)}
auts = [p for p in itertools.permutations(range(9)) if all(B[p[i]][p[j]] == B[i][j] for i in range(9) for j in range(i + 1, 9))]
assert len(auts) == 72
act = [[pos[tuple(sorted((g[a], g[b])))] for (a, b) in DEF] for g in auts]
src = sys.argv[1] if len(sys.argv) > 1 else "r3_p250_0_0of1_B.json"
d = json.load(open(src))
assert not d["timed_out"]
HL = d["H_stageB"]
by_tau = collections.defaultdict(list)
for e in HL:
    by_tau[e["tau"]].append(e)
out = []; tot = 0; stab_sizes = collections.Counter()
for ti, lst in sorted(by_tau.items()):
    tau = reps[ti]
    stab = [g for g in act if all(g[tau[k]] == tau[g[k]] for k in range(18))]
    stab_sizes[len(stab)] += 1
    def img(g, F, H):
        F2 = tuple(sorted(min(g[o], g[tau[o]]) for o in F))
        H2 = [0] * 18
        for k in range(18):
            v = 0
            for l in range(18):
                if (H[k] >> l) & 1:
                    v |= 1 << g[l]
            H2[g[k]] = v
        return (F2, tuple(H2))
    keys = set((tuple(sorted(e["F"])), tuple(e["H"])) for e in lst)
    assert len(keys) == len(lst)
    seen = set()
    for e in lst:
        key = (tuple(sorted(e["F"])), tuple(e["H"]))
        if key in seen:
            continue
        orb = set(img(g, key[0], key[1]) for g in stab)
        assert orb <= keys, "stage-B set not closed under the stabiliser"
        seen |= orb
        best = min(orb)
        out.append({"tau": ti, "F": list(best[0]), "H": list(best[1]), "orbit": len(orb), "stab": len(stab)})
    tot += len(lst)
tcount = collections.Counter(sum(bin(h).count("1") for h in e["H"]) // 2 for e in out)
print(f"stage-B triples: {tot} in {len(by_tau)} matchings; orbits under the stabilisers: {len(out)}; "
      f"sum of orbit sizes {sum(e['orbit'] for e in out)}")
print("stabiliser orders of the matchings carrying triples:", sorted(stab_sizes.items()))
print("t = e(X_2) of the orbit representatives:", sorted(tcount.items()))
print("triples per matching (top 10):", sorted(((len(v), k) for k, v in by_tau.items()), reverse=True)[:10])
json.dump(out, open("b0_stageB_reps.json", "w"))
