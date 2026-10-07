"""Read-only recount of the lattices marked EXCLUDED by the stream sweep (C2 lab audit, 2026-10-07).

  .venv/Scripts/python.exe scripts/cloud/audit_stream_excluded.py [--json out.json]

For every lattice with status "excluded" that has data/finishC/stream/<lid>/chunks.jsonl and plan.json, it re-derives the
exclusion from the stored records alone, with the checks of import_sweep.py on each record:
  * record accepted (chunk_ok, engine of a lab package, verdict counts adding up to n_pairs, producer end line when present,
    no unknown verdict);
  * a record counts as done if chunk_done, or if its only open pairs are INCOMPLETE and each of them has an EXCLUDED verdict in
    incomplete_resolved.jsonl (the rule of scripts/stream_finish.py);
  * coverage: the done records cover all the y1 representatives of the plan (chunk k/n = representatives k, k+n, ...);
  * no DEFERRED pair among the done records;
  * every twin class the done records deferred pairs to is a class whose lattices are all excluded in the tracker.
It prints one line per lattice that fails a point, then the totals. It writes nothing but the optional JSON."""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import import_sweep as IS
LAB = IS.LAB


def main():
    import twin_transfer as TT
    T = json.load(open(os.path.join(LAB, "data", "finishC", "finishC_tracker.json")))["lattices"]
    ST, GO = IS.engines(); PAR = IS.wrapper_shas("q/par_consumer.py"); DEF = IS.wrapper_shas("q/defer_consumer.py"); CL = TT.classes()
    out = {}; tot = collections.Counter(); engines = collections.Counter()
    for v in T:
        lid = "%03d" % v["id"]; d0 = os.path.join(LAB, "data", "finishC", "stream", lid)
        cf, pf = os.path.join(d0, "chunks.jsonl"), os.path.join(d0, "plan.json")
        if v["status"] != "excluded" or not os.path.exists(cf): continue
        tot["lattices"] += 1; problems = []
        if not os.path.exists(pf): problems.append("no plan.json"); out[lid] = problems; continue
        NR = len(json.load(open(pf))["y1_reps"]); res = {}
        rf = os.path.join(d0, "incomplete_resolved.jsonl")
        if os.path.exists(rf):
            for l in open(rf):
                if l.strip(): q = json.loads(l); res[(tuple(q["y1"]), tuple(q["y2"]))] = q["verdict"]
        cov = [0] * NR; nrec = nbad = npairs = 0; twins = collections.Counter(); c = collections.Counter(); nres = 0
        for l in open(cf, errors="replace"):
            if not l.strip(): continue
            d = json.loads(l)
            if not d.get("chunk_ok") or "verdicts" not in d: continue
            nrec += 1
            bad = IS.check(d, lid, d["chunk"][0], d["chunk"][1], ST, GO, PAR, DEF)
            if bad: nbad += 1; problems.append("record %s refused: %s" % (d["chunk"], "; ".join(bad)[:120])); continue
            ne = d.get("not_excluded") or []
            done = bool(d.get("chunk_done")) or (bool(ne) and all(x.get("verdict") == "INCOMPLETE" and
                                                 str(res.get((tuple(x["y1"]), tuple(x["y2"])), "")).startswith("EXCLUDED") for x in ne))
            if not done: continue
            k, n = d["chunk"]; mine = range(k, NR, n)
            if all(cov[i] for i in mine): continue
            for i in mine: cov[i] += 1
            npairs += d["n_pairs"]; twins.update(d.get("twin_deferred") or {}); nres += len(ne)
            engines[json.dumps(d.get("code_sha"), sort_keys=True)] += 1
            for vv, m in d["verdicts"].items(): c[IS.cls(vv)] += m
        miss = sum(1 for x in cov if x == 0)
        if miss: problems.append("%d of %d y1 representatives not covered by done records" % (miss, NR))
        if c["defer_T18"] or c["defer_T20"]: problems.append("DEFERRED pairs among the done records")
        if c["other"]: problems.append("unknown verdicts")
        pend = [k for k in twins if CL.get(eval(k), {"?"}) != {"excluded"}]
        if pend: problems.append("twin classes not excluded: %d" % len(pend))
        tot["records"] += nrec; tot["pairs"] += npairs; tot["resolved_incomplete_pairs"] += nres; tot["twin_pairs"] += c["twin"]
        for x in ("excl_at_once", "excl_search", "swap", "incomplete"): tot[x] += c[x]
        if problems: print("%s: %s" % (lid, " | ".join(problems[:4]))); tot["lattices_with_a_problem"] += 1
        out[lid] = {"records": nrec, "y1_reps": NR, "pairs": npairs, "problems": problems, **{x: c[x] for x in IS.CLASSES}}
    print("lattices excluded by the stream sweep and recounted: %d; with a problem: %d" % (tot["lattices"], tot["lattices_with_a_problem"]))
    print("records read: %d; pairs of the covering records: %d (at once %d, search %d, twin %d, swap %d, INCOMPLETE resolved by a second search %d)" % (
        tot["records"], tot["pairs"], tot["excl_at_once"], tot["excl_search"], tot["twin_pairs"], tot["swap"], tot["incomplete"]))
    print("engines of the covering records:")
    names = {**ST}
    for e, n in engines.most_common(): print("  %6d records  %s  (first package with this engine: %s)" % (n, {k: v[:8] for k, v in json.loads(e).items()}, names.get(e)))
    if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
