"""Write the pair list of a Golay-family lattice (package files data/golay/<lid>/pairs_*.json, sorted by name, concatenated: the
order of scripts/golay_pairs_job.py) as a stream in the format of the stream producer, for q/audit_rigid.py (C2 lab, 2026-10-07).
  python golay_stream.py <package dir> <lid>      -> stdout: {"o": index, "y1": [...], "y2": [...]} per pair, then the end line."""
import sys, os, json, glob, hashlib
pkg, lid = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2])
sh = hashlib.sha256(); n = 0; out = sys.stdout
for f in sorted(glob.glob(os.path.join(pkg, "data", "golay", lid, "pairs_*.json"))):
    d = json.load(open(f)); P = d["pairs"] if "pairs" in d else [[d["y1"], y2] for y2 in d["y2s"]]
    for y1, y2 in P:
        line = json.dumps({"o": n, "y1": [str(x) for x in y1], "y2": [str(x) for x in y2]})
        out.write(line + chr(10)); sh.update((line + chr(10)).encode()); n += 1
out.write(json.dumps({"end": True, "id": int(lid), "chunk": [0, 1], "pairs": n, "complete": True, "sha256": sh.hexdigest()}) + chr(10))
