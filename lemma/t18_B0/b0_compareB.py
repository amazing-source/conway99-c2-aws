# B0, profile (2,5,0), stage B: compare the triples (tau, F, H) of the enumerator (r3_p250.py, stage B) with those of the
# independent verifier (b0_verify.py = r3_verify.py + explicit list of matchings), on all 425 matchings.
import json, itertools
td = json.load(open("r2_tau_0.json")); reps = td["reps"]
def min_y2(t):
    return min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t)
MY = {t: 2 * min_y2(t) for t in range(10)}
ver = set(); ver_all = 0; taus = []
d1 = json.load(open("r3v_B250_0_0of1.json"))          # timed out after the first 418 matchings (0..417)
assert d1["timed_out"] and d1["stats"]["tau"] == 418
done1 = set(range(418))
assert all(e["tau"] in done1 for e in d1["H"])
d2 = json.load(open("r3v_B250_0_0of1_t418.json"))     # matchings 418..424
assert not d2["timed_out"] and sorted(d2["taus_started"]) == list(range(418, 425))
for d in (d1, d2):
    for e in d["H"]:
        ver_all += 1
        tau = reps[e["tau"]]
        mem = [k for o in e["F"] for k in (o, tau[o])]
        degs = [bin(h).count("1") for h in e["H"]]
        t = sum(degs) // 2
        if t <= 9 and sum(degs[k] - 1 for k in mem) <= 8 and sum(x * (x - 1) for x in degs) + MY[t] <= 36:
            ver.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
en = json.load(open("r3_p250_0_0of1_B.json"))
assert not en["timed_out"] and en["totals"]["tau_done"] == 425
enum = set((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in en["H_stageB"])
print(f"B0 stage B, all 425 matchings: verifier {ver_all} triples, {len(ver)} after the counting conditions; "
      f"enumerator {len(enum)}; identical sets: {ver == enum}; only verifier {len(ver - enum)}, only enumerator {len(enum - ver)}")
print("   matchings carrying triples:", len(set(x[0] for x in enum)), "; values of t:", sorted(set(sum(bin(h).count('1') for h in x[2]) // 2 for x in enum)),
      "; max a_2 on X_2:", max(max(bin(h).count('1') for h in x[2]) for x in enum))
