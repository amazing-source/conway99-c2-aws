"""Weight of every remaining golay_pairs job of a lattice in deferral mode = number of its pairs that the engine will search in full:
pairs that pass char_trap and min97_witness and have NO root r with (r,y1)^2 + (r,y2)^2 in {5, 4}. (Twin transfer is ignored: it can
only remove pairs.) Writes "<key> <to_search> <deferred>" per line, heaviest first.
  <venv python> golay_heavy.py <repo> <pkg> <lid> <out file>"""
import sys, os, json, glob, subprocess, time
REPO, PKG, LID, OUT = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4]
os.chdir(PKG); sys.path.insert(0, os.path.join(PKG, "scripts"))
os.environ.setdefault("FD_LEMMA_U", "1"); os.environ.setdefault("FD_SYM", "1"); os.environ.setdefault("FD_SYM3", "1"); os.environ["FD_MIN97"] = "1"
import numpy as np
from fractions import Fraction as F
import golay_pairs_job as GJ
from frame_dfs_next import lattice_data, char_trap, min97_witness
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
order = g("show", "origin/queue:order.txt").split()
done = {j for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip() for e in [json.loads(l)] if e["op"] == "done" for j in e["jobs"]}
keys = [j for j in order if j.startswith(LID + ":") and j not in done]
files = sorted(glob.glob(os.path.join(PKG, "data", "golay", LID, "pairs_*.json")))
allp = []; meta = None
for f in files:
    d = json.load(open(f)); meta = meta or (d["basis"], d["scale"]); allp += GJ.pairs_of(d)
N = len(allp); L = lattice_data([[F(x) for x in row] for row in meta[0]], F(1, int(meta[1])))
Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]])); RG = (L["R"] @ L["G"]).astype(np.int64)
conv = lambda v: np.rint(np.array([float(F(x)) for x in v]) @ Binv).astype(np.int64)
rows = []; t = time.time()
for n_, key in enumerate(keys):
    _, k, n = key.split(":"); k, n = int(k), int(n); a, b = N * k // n, N * (k + 1) // n; full = dfr = 0
    for s1, s2 in allp[a:b]:
        y1, y2 = conv(s1), conv(s2)
        if char_trap(L, y1, y2) is not None or min97_witness(L, y1, y2) is not None: continue
        u = RG @ y1; v = RG @ y2; Y = u * u + v * v
        if (Y == 5).any() or (Y == 4).any(): dfr += 1
        else: full += 1
    rows.append((full, dfr, key))
    if n_ % 300 == 0: print(LID, n_, "/", len(keys), "%.0f s" % (time.time() - t), flush=True)
rows.sort(key=lambda r: (-r[0], r[2]))
open(OUT, "w", newline="\n").write("".join("%s %d %d\n" % (r[2], r[0], r[1]) for r in rows))
import collections
h = collections.Counter(r[0] for r in rows)
print("%s: %d jobs, %d pairs to search in full, %d deferred | jobs by number of full searches: %s" % (LID, len(rows), sum(r[0] for r in rows), sum(r[1] for r in rows), " ".join("%d:%d" % (i, h[i]) for i in sorted(h, reverse=True))))
