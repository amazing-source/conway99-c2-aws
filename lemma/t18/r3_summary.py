# Summary of the profile (2,5,0) runs of r3_p250.py for one structure: coverage of the 1259 (or 425, 528) matchings,
# union of the stage-B sets (tau, F, H), survivors of stage C.
# usage: python r3_summary.py <structure> <json files ...>
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
si = int(sys.argv[1])
nrep = len(json.load(open(os.path.join(here, f"r2_tau_{si}.json")))["reps"])
done = set(); H = set(); surv = 0
tot = {}
for fn in sys.argv[2:]:
    d = json.load(open(os.path.join(here, fn)))
    t = d["totals"]
    # matchings completed by this run = the first tau_done of its list
    if "_idx" in fn:
        lst = None
    else:
        lst = [i for i in range(nrep) if i % d["nparts"] == d["part"]]
    completed = t["tau_done"]
    print(f"{fn}: matchings {t['tau']}, completed {completed}, timed_out {d['timed_out']}, "
          f"H after counts {t['H_after_counts']}, stage-C survivors {t['C_survivors']}, certificates saved {d['n_cert']}")
    surv += t["C_survivors"]
    for k, v in t.items():
        tot[k] = tot.get(k, 0) + v
    for e in d["H_stageB"]:
        H.add((e["tau"], tuple(e["F"]), tuple(e["H"])))
    d["_lst"] = lst
    if lst is not None:
        done.update(lst[:completed])
    else:
        done.update(set(e["tau"] for e in d["H_stageB"]))     # lower bound only; exact list is in the launch log
print(f"distinct (tau, F, H) of stage B: {len(H)}, in {len(set(h[0] for h in H))} matchings, {len(set(h[:2] for h in H))} pairs (tau, F)")
print(f"stage-C survivors, all runs: {surv}")
print("summed counters (the 3 matchings interrupted by the time limit in the first round are counted twice):")
print("  ", {k: tot[k] for k in ("F", "F_base_ok", "B_nodes", "H_complete", "H_after_counts", "type_sols", "type_sols_ok33",
                                 "C_type_solutions", "C_ts_dead_by_counts", "C_nodes", "C_survivors", "rej_budget", "rej_psd",
                                 "psd_float_neg_no_cert")})
