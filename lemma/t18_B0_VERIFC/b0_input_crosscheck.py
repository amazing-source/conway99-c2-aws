# t18_B0_VERIFC / b0_input_crosscheck.py -- BOOKKEEPING ONLY: is the B0 stage-B list given to c_mine.py (enumerator file
# r3_p250_0_0of1_B.json, field H_stageB) the same set as the one of the independent stage-B verifier of the B0 session
# (r3v_B250_0_0of1.json: matchings 0..417, stopped by its time limit; r3v_B250_0_0of1_t418.json: matchings 418..424)?
# Raw comparison of (tau, sorted F, H), no filter.  Also: how many early exits c_mine.py will take (descriptive only,
# recomputed from the input with the same formulas as c_mine.py lines 156-183: slack < 0, max f > 2).
# usage: python b0_input_crosscheck.py <enumerator json> <verifier json 0..417> <verifier json 418..424> <r2_tau_0.json>
import json, sys
en = json.load(open(sys.argv[1])); d1 = json.load(open(sys.argv[2])); d2 = json.load(open(sys.argv[3])); td = json.load(open(sys.argv[4]))
E = [(e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in en["H_stageB"]]
print(f"enumerator: timed_out {en['timed_out']}, matchings {en['totals']['tau']}, done {en['totals']['tau_done']}, "
      f"entries {len(E)}, distinct {len(set(E))}, matchings with triples {len(set(t for t, _, _ in E))}, tau_alive {len(en['tau_alive'])}")
print(f"verifier file 1: keys {sorted(d1.keys())}, timed_out {d1['timed_out']}, stats {d1['stats']}, entries {len(d1['H'])}, "
      f"tau range {min(e['tau'] for e in d1['H'])}..{max(e['tau'] for e in d1['H'])}")
print(f"verifier file 2: keys {sorted(d2.keys())}, timed_out {d2['timed_out']}, stats {d2['stats']}, entries {len(d2['H'])}, "
      f"tau range {min(e['tau'] for e in d2['H'])}..{max(e['tau'] for e in d2['H'])}, taus_started {sorted(d2.get('taus_started', []))}")
V1 = [(e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in d1["H"]]
V2 = [(e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in d2["H"]]
n1 = d1["stats"]["tau"]
print(f"verifier file 1 holds only matchings < {n1}: {all(t < n1 for t, _, _ in V1)}; file 2 only matchings >= {n1}: {all(t >= n1 for t, _, _ in V2)}")
V = set(V1) | set(V2)
print(f"verifier union: {len(V1)} + {len(V2)} = {len(V1) + len(V2)} entries, distinct {len(V)}")
print(f"identical sets (enumerator == verifier): {set(E) == V}; only enumerator {len(set(E) - V)}, only verifier {len(V - set(E))}")
DEF = [tuple(x) for x in td["DEF"]]; REPS = td["reps"]
print(f"r2_tau_0.json: {len(REPS)} matching representatives, {len(DEF)} deficient pairs")
pc = int.bit_count
neg = 0; f3 = 0; byt = {}
for ti, F, H in set(E):
    tau = REPS[ti]
    mem = sorted(k for o in F for k in (o, tau[o]))
    FL = sum(pc(H[k]) - 1 for k in mem)
    slack = 4 - FL // 2
    f = [sum(1 for k in mem if i in DEF[k]) for i in range(9)]
    t = sum(pc(h) for h in H) // 2
    byt[t] = byt.get(t, 0) + 1
    if slack < 0:
        neg += 1
    elif max(f) > 2:
        f3 += 1
print(f"triples by t = e(X_2): {dict(sorted(byt.items()))}; triples with slack < 0: {neg}; with slack >= 0 and max f > 2: {f3}")
