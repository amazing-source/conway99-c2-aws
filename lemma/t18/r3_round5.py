# Round 3, very last launch: the 3 big matchings left by r3_round4.py plus the 138 matchings without stage-B triple.
#   python r3_round5.py prepare   -> r3_last_g{0,1,2}.txt
#   python r3_round5.py final     -> coverage of ALL 1259 matchings, survivors
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
cov = json.load(open(os.path.join(HERE, "r3_coverage_B1_final.json")))
big = json.load(open(os.path.join(HERE, "r3_remaining_B1.json")))["not_done_with_triples"]
done4 = set()
for g in range(3):
    lst = [int(x) for x in open(os.path.join(HERE, f"r3_left41_g{g}.txt")).read().split(",")]
    d = json.load(open(os.path.join(HERE, f"r3_p250_1_{g}of3_idx{lst[0]}_BC.json")))
    done4.update(lst[:d["totals"]["tau_done"]])
rest = sorted(set(cov["not_done"]) - done4)
small = [t for t in rest if t not in big]
if sys.argv[1] == "prepare":
    for g in range(3):
        lst = small[g::3] + ([big[g]] if g < len(big) else [])
        open(os.path.join(HERE, f"r3_last_g{g}.txt"), "w").write(",".join(map(str, lst)))
    print(f"left: {len(rest)} matchings = {len(small)} without stage-B triple + {len(big)} big ones {big}")
else:
    done5 = set(); surv = []
    for g in range(3):
        lst = [int(x) for x in open(os.path.join(HERE, f"r3_last_g{g}.txt")).read().split(",")]
        fn = f"r3_p250_1_{g}of5_idx{lst[0]}_BC.json"
        d = json.load(open(os.path.join(HERE, fn)))
        assert d["totals"]["tau"] == len(lst)
        k = d["totals"]["tau_done"]
        done5.update(lst[:k])
        print(f"{fn}: matchings {len(lst)}, completed {k}, timed_out {d['timed_out']}, H {d['totals']['H_after_counts']}, "
              f"stage-C survivors {d['totals']['C_survivors']}")
        surv += [(e["tau"], e["F"], e["types"]) for e in d["survivors"]]
    alld = set(cov["done"]) | done4 | done5
    print(f"matchings completed by the enumerator, all launch rounds: {len(alld)} of 1259; not done: {sorted(set(range(1259)) - alld)}")
    print("survivors found in this last launch:", surv)
