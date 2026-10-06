# Summary of the extension runs (r2_stage2.py restricted to the survivors of r2_hfirst.py) for structure 1 (B1).
import json, os, glob
here = os.path.dirname(os.path.abspath(__file__))
files = ["r2_stage2_1_0of3_surv.json"] + sorted(glob.glob(os.path.join(here, "r2_stage2_1_0of1_surv_idx*.json")))
tot = {}
done = 0; planned = 0; unfinished = []
for f in files:
    d = json.load(open(os.path.join(here, f)))
    t = d["totals"]
    for k in ("F_ok_Np", "C", "H", "G", "Y_tables", "Y_psd_reject", "Y_tables_psd", "tau_with_psd_table"):
        tot[k] = tot.get(k, 0) + t.get(k, 0)
    done += t["tau_done"]; planned += t["tau"]
    print(os.path.basename(f), ": matchings", t["tau"], "done", t["tau_done"], "timed_out", d["timed_out"],
          " Y-tables", t["Y_tables"], " PSD-surviving", t["Y_tables_psd"], " saved", len(d["examples"]))
print("TOTAL: matchings planned", planned, "done", done, tot)
