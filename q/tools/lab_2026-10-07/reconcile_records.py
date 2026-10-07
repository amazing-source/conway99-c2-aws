"""Where are the records of the excluded lattices? (C2 lab, 2026-10-07; READS and REPORTS.)

  .venv/Scripts/python.exe scripts/cloud/reconcile_records.py [--json out.json]

For every lattice marked excluded in data/finishC/finishC_tracker.json:
  * the method recorded in the tracker (field "by", shortened);
  * stream lattices (data/finishC/stream/<lid>/chunks.jsonl + plan.json): the y1 representatives covered by its chunk_ok records,
    split by the field `machine` of the record: "labpc" (computed on the lab PC) or a cloud machine; whether every record has a
    code version (code_sha); and, for each record, whether a file with the same name and the same stream sha256 is in the working
    tree of the compute repository (aws_repo/resultats/*/results, aws_repo/resultats_q/*/results);
  * other lab folders holding files for the lattice (frame_dfs, golay, o24_cloud, o24_dfs, pack, telemetry_backfill, ypairs_c2).
Classes printed at the end:
  A  stream, every representative covered by records that are ALSO in the compute repository (GitHub);
  B  stream, complete on the lab PC, but some representatives rest on records that exist only on the lab PC;
  C  other lab-local records (frame_dfs, h-stage, Golay blocks, ...): only on the lab PC;
  D  lattice-level arguments (packing, criterion (E), Sol 0836, A.9, component budget): texts and scripts, no pair records.
The lab folder data/finishC is not in any repository; nothing here copies it."""
import sys, os, json, glob, collections
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); REPO = os.path.join(LAB, "aws_repo"); FC = os.path.join(LAB, "data", "finishC")


def main():
    T = json.load(open(os.path.join(FC, "finishC_tracker.json")))["lattices"]
    repo = collections.defaultdict(set)                                   # file name -> stream sha256 found in the compute repo
    for f in glob.glob(os.path.join(REPO, "resultats", "*", "results", "*.jsonl")) + glob.glob(os.path.join(REPO, "resultats_q", "*", "results", "*.jsonl")):
        for l in open(f, errors="replace"):
            if '"sha256"' not in l: continue
            try: d = json.loads(l)
            except ValueError: continue
            if d.get("chunk_ok") and d.get("sha256"): repo[os.path.basename(f)].add(d["sha256"])
    other = {}
    for name in ("frame_dfs", "golay", "o24_cloud", "o24_dfs", "pack", "telemetry_backfill", "ypairs_c2"):
        for p in glob.glob(os.path.join(FC, name, "*")):
            b = os.path.basename(p)
            for lid in {b[:3], b[-8:-5], b.replace("class_", "")[:3], b.replace("pairs_", "")[:3], b.replace("gamma_", "")[:3]}:
                if lid.isdigit() and len(lid) == 3: other.setdefault(lid, set()).add(name)
    out = {}; cl = collections.defaultdict(list)
    for v in T:
        if v["status"] != "excluded": continue
        lid = "%03d" % v["id"]; o = {"by": v.get("by", "")[:160], "other_lab_folders": sorted(other.get(lid, []))}
        cf = os.path.join(FC, "stream", lid, "chunks.jsonl"); pf = os.path.join(FC, "stream", lid, "plan.json")
        if os.path.exists(cf) and os.path.exists(pf):
            NR = len(json.load(open(pf))["y1_reps"]); cov_any = [0] * NR; cov_repo = [0] * NR; mach = collections.Counter(); nosha = 0; nrec = 0
            for l in open(cf, errors="replace"):
                if not l.strip(): continue
                d = json.loads(l)
                if not d.get("chunk_ok") or "verdicts" not in d: continue          # accepted record (the exclusion itself is re-derived by audit_stream_excluded.py)
                nrec += 1; k, n = d["chunk"]; m = d.get("machine") or "?"; mach["labpc" if m == "labpc" else "cloud"] += 1
                if not d.get("code_sha"): nosha += 1
                fn = os.path.basename(str(d.get("imported_from") or "%s_%d_%d.jsonl" % (lid, k, n)))
                inrepo = d.get("sha256") in repo.get(fn, ()) or d.get("sha256") in repo.get("%s_%d_%d.jsonl" % (lid, k, n), ())
                for i in range(k, NR, n):
                    cov_any[i] = 1
                    if inrepo: cov_repo[i] = 1
            o.update(kind="stream", y1_reps=NR, done_records=nrec, records_by_machine=dict(mach), records_without_code_version=nosha,
                     reps_covered=sum(cov_any), reps_covered_by_records_in_compute_repo=sum(cov_repo))
            c = "A" if sum(cov_repo) == NR else "B" if sum(cov_any) == NR else "B?"
        elif other.get(lid): o["kind"] = "other lab records"; c = "C"
        else: o["kind"] = "lattice-level argument"; c = "D"
        o["class"] = c; out[lid] = o; cl[c].append(lid)
    for c in sorted(cl): print("%s (%d): %s" % (c, len(cl[c]), " ".join(cl[c])))
    print("class C, folders: %s" % {l: out[l]["other_lab_folders"] for l in cl.get("C", [])})
    print("stream lattices, detail (lid: representatives, covered, covered by records also in the compute repo, records lab / cloud, without code version):")
    for lid, o in sorted(out.items()):
        if o["kind"] == "stream":
            print("  %s: %5d %5d %5d | lab %4d cloud %4d | no version %4d" % (lid, o["y1_reps"], o["reps_covered"], o["reps_covered_by_records_in_compute_repo"],
                  o["records_by_machine"].get("labpc", 0), o["records_by_machine"].get("cloud", 0), o["records_without_code_version"]))
    if "--json" in sys.argv: json.dump({"classes": cl, "lattices": out}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
