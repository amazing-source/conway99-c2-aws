# Round 3, last launch round: bookkeeping for the matchings that still carry stage-B triples.
#   python r3_round4.py prepare   -> r3_left41_g{0,1,2}.txt (matchings not done that have stage-B triples, 3 balanced groups)
#   python r3_round4.py final     -> coverage, survivors, what remains (after the runs)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
cov = json.load(open(os.path.join(HERE, "r3_coverage_B1_final.json")))
left = set(cov["not_done"])
cnt = {}
for q in range(3):
    for e in json.load(open(os.path.join(HERE, f"r3v_B250_1_{q}of3.json")))["H"]:
        if e["tau"] in left:
            cnt[e["tau"]] = cnt.get(e["tau"], 0) + 1
order = sorted(cnt, key=lambda t: -cnt[t])
groups = [[], [], []]
load = [0, 0, 0]
for t in order:
    g = load.index(min(load))
    groups[g].append(t); load[g] += cnt[t]
if sys.argv[1] == "prepare":
    for g in range(3):
        groups[g].sort(key=lambda t: cnt[t])          # small ones first, so that the time limit cuts as few as possible
        open(os.path.join(HERE, f"r3_left41_g{g}.txt"), "w").write(",".join(map(str, groups[g])))
    print(f"{len(order)} matchings with stage-B triples among the {len(left)} not done; triples per group {load}; "
          f"{len(left) - len(order)} matchings have NO stage-B triple (verifier) and need no stage C")
else:
    done4 = set(); surv = 0; H4 = 0
    for g in range(3):
        lst = [int(x) for x in open(os.path.join(HERE, f"r3_left41_g{g}.txt")).read().split(",")]
        fn = f"r3_p250_1_{g}of3_idx{lst[0]}_BC.json"
        d = json.load(open(os.path.join(HERE, fn)))
        assert d["totals"]["tau"] == len(lst)
        k = d["totals"]["tau_done"]
        done4.update(lst[:k])
        surv += d["totals"]["C_survivors"]
        H4 += sum(cnt[t] for t in lst[:k])
        print(f"{fn}: matchings {len(lst)}, completed {k}, timed_out {d['timed_out']}, H {d['totals']['H_after_counts']}, "
              f"stage-C survivors {d['totals']['C_survivors']}")
        for e in d["survivors"]:
            print("     survivor: matching", e["tau"], "F", e["F"], "types", e["types"],
                  "" if e["tau"] in lst[:k] else "(matching not completed)")
    rest = sorted(t for t in order if t not in done4)
    print(f"last round: {len(done4)} more matchings completed ({H4} stage-B triples), survivors found in this round: {surv}")
    print(f"STILL NOT DONE at stage C: {len(rest)} matchings carrying {sum(cnt[t] for t in rest)} stage-B triples: {rest}")
    json.dump({"not_done_with_triples": rest, "triples": {str(t): cnt[t] for t in rest}},
              open(os.path.join(HERE, "r3_remaining_B1.json"), "w"))
