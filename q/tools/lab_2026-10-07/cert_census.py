"""Census of the stream certificates against the manifest (C2 lab, 2026-10-07). READS and REPORTS.

  .venv/Scripts/python.exe scripts/cloud/cert_census.py <manifest json> <folder of certificate folders> [--json out.json]

For every record of the manifest (aws_repo/measures/CERT_MANIFEST_2026-10-07.json; key lid:k:n, stream sha256, numbers of deferred
pairs T18 / T20 / T20_norm4): the certificates <lid>_<k>_<n>.json found in the sub-folders (one per machine branch, files of
q/cert_stream.py). A certificate is GOOD for the record when: same id, chunk and stream sha256; stream_ok and ok are true; the
numbers of certified pairs equal the numbers of deferred pairs of the record, for each of the three lists.
Reported: records with a good certificate; records without; certificates that are not good (with the reason); records present
on several branches whose certificates disagree (verdict or counts); versions of q/cert_stream.py."""
import sys, os, json, glob, collections


def main():
    man = json.load(open(sys.argv[1]))["records"]; root = sys.argv[2]
    C = collections.defaultdict(list)
    for f in glob.glob(os.path.join(root, "*", "*_*_*.json")):
        try: c = json.load(open(f))
        except ValueError: continue
        if "chunk" in c and "sha256" in c: C[("%03d" % c["id"], c["chunk"][0], c["chunk"][1])].append((os.path.basename(os.path.dirname(f)), c))
    good = 0; missing = []; notgood = []; disagree = []; ver = collections.Counter(); per = collections.defaultdict(lambda: [0, 0, 0, 0, 0]); dup = 0
    for m in man:
        L = C.get((m["lid"], m["k"], m["n"]), []); g = []
        for src, c in L:
            why = []
            if c["sha256"] != m["sha256"]: why.append("stream sha256 differs")
            if not (c.get("stream_ok") is True and c.get("ok") is True): why.append("not ok")
            got = (c["T18"]["certified"], c["T20"]["certified"], (c.get("T20_norm4") or {}).get("certified", 0))
            if got != (m["T18"], m["T20"], m.get("T20_norm4", 0)): why.append("certified %s, deferred %s" % (got, (m["T18"], m["T20"], m.get("T20_norm4", 0))))
            if why: notgood.append((m["key"], src, why))
            else: g.append((src, c))
        p = per[m["lid"]]; p[0] += 1
        if g:
            good += 1; p[1] += 1; p[2] += m["T18"]; p[3] += m["T20"]; p[4] += m.get("T20_norm4", 0); ver[g[0][1].get("cert_stream_sha256")] += 1
            if len(L) > 1:
                dup += 1
                if len({(c["sha256"], c.get("ok"), c["T18"]["certified"], c["T20"]["certified"]) for _, c in L}) > 1: disagree.append(m["key"])
        else: missing.append(m["key"])
    print("records in the manifest: %d; with a good certificate: %d; without: %d %s" % (len(man), good, len(missing), missing[:10]))
    print("certificates not good: %d %s" % (len(notgood), notgood[:5]))
    print("records on several branches: %d; disagreeing: %d %s" % (dup, len(disagree), disagree[:5]))
    print("versions of cert_stream.py: %s" % dict(ver))
    print("%-4s %8s %8s %10s %10s %10s" % ("lid", "records", "good", "T18", "T20", "T20 norm4"))
    for lid in sorted(per): print("%-4s %8d %8d %10d %10d %10d" % (lid, *per[lid]))
    print("certified pairs: %d pending T18, %d pending T20 (of which %d by a norm-4 vector)" % (
        sum(p[2] for p in per.values()), sum(p[3] + p[4] for p in per.values()), sum(p[4] for p in per.values())))
    if "--json" in sys.argv:
        json.dump({"records": len(man), "good": good, "missing": missing, "not_good": notgood, "disagree": disagree, "per_lattice": per, "versions": dict(ver)},
                  open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
