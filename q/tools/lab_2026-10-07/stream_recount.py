"""Recount of the stream lattices from the stored records, with the provenance of each record (C2 lab, 2026-10-07). READS and REPORTS.

  .venv/Scripts/python.exe scripts/cloud/stream_recount.py [--json out.json]

For every lattice that has data/finishC/stream/<lid>/chunks.jsonl and plan.json and is excluded in the tracker WITHOUT deferred
pairs (the lattices converted through T18 / T20 are reported by import_sweep.py): the checks of import_sweep.check on each record,
EXCEPT that a record whose only fault is "engine not of a lab package" is kept and classed by provenance:
  tier P  the record's code_sha is the engine of one of the lab packages c2_cloud_run*/MANIFEST.json;
  tier L  the record carries a code_sha that is not a package engine (a lab-PC version of the engine files, runs of 28-29/09);
  tier N  the record carries no code version at all.
A record counts as done if chunk_done, or if its only open pairs are INCOMPLETE and each has an EXCLUDED verdict in
incomplete_resolved.jsonl. Records are selected by tier (P first, then L, then N), each only if it covers a y1 representative not
yet covered. Reported per lattice: representatives covered, and how many of them by each tier; pairs and verdict classes of the
selected records; representatives covered twice; any other fault of a record; DEFERRED pairs (must be none); twin classes not
excluded in the tracker (must be none).
This is a recount of what the records say and of where they come from. It does not re-run anything."""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import import_sweep as IS
LAB = IS.LAB


def main():
    import twin_transfer as TT
    T = json.load(open(os.path.join(LAB, "data", "finishC", "finishC_tracker.json")))["lattices"]
    ST, GO = IS.engines(); PAR = IS.wrapper_shas("q/par_consumer.py"); DEF = IS.wrapper_shas("q/defer_consumer.py"); CL = TT.classes()
    out = {}; tot = collections.Counter(); eng = collections.Counter()
    for v in T:
        lid = "%03d" % v["id"]; d0 = os.path.join(LAB, "data", "finishC", "stream", lid)
        cf, pf = os.path.join(d0, "chunks.jsonl"), os.path.join(d0, "plan.json")
        if v["status"] != "excluded" or not os.path.exists(cf) or not os.path.exists(pf) or "deferral sweep" in v.get("by", ""): continue
        NR = len(json.load(open(pf))["y1_reps"]); res = {}
        rf = os.path.join(d0, "incomplete_resolved.jsonl")
        if os.path.exists(rf):
            for l in open(rf):
                if l.strip(): q = json.loads(l); res[(tuple(q["y1"]), tuple(q["y2"]))] = q["verdict"]
        recs = []; faults = []
        for l in open(cf, errors="replace"):
            if not l.strip(): continue
            d = json.loads(l)
            if not d.get("chunk_ok") or "verdicts" not in d: continue
            bad = IS.check(d, lid, d["chunk"][0], d["chunk"][1], ST, GO, PAR, DEF)
            other = [b for b in bad if not b.startswith("engine not of a lab package")]
            if other: faults.append("record %s: %s" % (d["chunk"], "; ".join(other)[:160])); continue
            tier = "P" if not bad else ("L" if d.get("code_sha") else "N")
            ne = d.get("not_excluded") or []
            done = bool(d.get("chunk_done")) or (bool(ne) and all(x.get("verdict") == "INCOMPLETE" and
                                                 str(res.get((tuple(x["y1"]), tuple(x["y2"])), "")).startswith("EXCLUDED") for x in ne))
            if done: recs.append((tier, d))
        cov = [None] * NR; twice = 0; c = collections.Counter(); npairs = 0; pt = collections.Counter(); twins = collections.Counter(); sel = collections.Counter(); nres = 0
        for tier, d in sorted(recs, key=lambda t: ("PLN".index(t[0]), t[1]["chunk"][1], t[1]["chunk"][0], str(t[1].get("t", "")))):
            k, n = d["chunk"]; mine = range(k, NR, n)
            if all(cov[i] is not None for i in mine): continue
            for i in mine:
                if cov[i] is None: cov[i] = tier
                else: twice += 1
            sel[tier] += 1; npairs += d["n_pairs"]; pt[tier] += d["n_pairs"]; twins.update(d.get("twin_deferred") or {}); nres += len(d.get("not_excluded") or [])
            eng[(tier, json.dumps(d.get("code_sha"), sort_keys=True))] += 1
            for vv, m in d["verdicts"].items(): c[IS.cls(vv)] += m
        by = collections.Counter(x for x in cov if x is not None); miss = sum(1 for x in cov if x is None)
        pend = [k for k in twins if CL.get(eval(k), {"?"}) != {"excluded"}]
        o = {"y1_reps": NR, "covered": NR - miss, "by_tier": {t: by.get(t, 0) for t in "PLN"}, "selected_records": dict(sel), "pairs": npairs, "pairs_by_tier": {t: pt.get(t, 0) for t in "PLN"}, "covered_twice": twice,
             "other_faults": faults, "incomplete_resolved_pairs": nres, "twin_classes_pending": len(pend), **{x: c[x] for x in IS.CLASSES}}
        o["ok"] = bool(miss == 0 and not faults and not c["defer_T18"] and not c["defer_T20"] and not c["other"] and not pend)
        out[lid] = o; tot["lattices"] += 1; tot["ok"] += o["ok"]; tot["pairs"] += npairs
        for x in ("excl_at_once", "excl_search", "twin", "swap"): tot[x] += c[x]
        for t in "PLN": tot["pairs_" + t] += pt.get(t, 0); tot["reps_" + t] += by.get(t, 0)
        tot["all_P"] += by.get("P", 0) == NR; tot["some_L"] += by.get("L", 0) > 0; tot["some_N"] += by.get("N", 0) > 0; tot["twice"] += twice > 0
        if not o["ok"]: print("%s NOT OK: missing %d, faults %s, pending twins %d" % (lid, miss, faults[:2], len(pend)))
    print("stream lattices recounted: %d; coverage complete and no fault: %d" % (tot["lattices"], tot["ok"]))
    print("pairs of the selected records: %d (at once %d, search %d, twin %d, swap %d); lattices with a representative covered twice: %d" % (
        tot["pairs"], tot["excl_at_once"], tot["excl_search"], tot["twin"], tot["swap"], tot["twice"]))
    print("provenance: every representative on a package engine: %d lattices; some on a lab-PC engine version: %d; some on records without code version: %d" % (
        tot["all_P"], tot["some_L"], tot["some_N"]))
    print("by tier: representatives P %d, L %d, N %d; pairs P %d, L %d, N %d" % tuple(tot[x] for x in ("reps_P", "reps_L", "reps_N", "pairs_P", "pairs_L", "pairs_N")))
    for (tier, e), n in sorted(eng.items(), key=lambda t: (t[0][0], -t[1])): print("  tier %s %6d records  %s" % (tier, n, {k: v[:8] for k, v in (json.loads(e) or {}).items()}))
    if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
