import sys, os, json, glob, collections, random, time
sys.path.insert(0, "scripts")
os.environ.setdefault("FD_LEMMA_U", "1"); os.environ.setdefault("FD_SYM", "1"); os.environ.setdefault("FD_SYM3", "1"); os.environ["FD_MIN97"] = "1"
import numpy as np
from fractions import Fraction as F
import golay_pairs_job as GJ
from frame_dfs_next import lattice_data, char_trap, min97_witness
lid = sys.argv[1]; NS = int(sys.argv[2])
files = sorted(glob.glob(os.path.join("data", "golay", lid, "pairs_*.json")))
d0 = json.load(open(files[0])); t = time.time()
L = lattice_data([[F(x) for x in row] for row in d0["basis"]], F(1, int(d0["scale"])))
Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
RG = (L["R"] @ L["G"]).astype(np.int64)
print("lattice %s: %d pair files, %d +- root pairs, lattice_data %.0f s" % (lid, len(files), len(RG), time.time() - t), flush=True)
random.seed(7); allp = []
for f in files:
    d = json.load(open(f)); P = GJ.pairs_of(d); allp += [(os.path.basename(f), i, p) for i, p in enumerate(P)]
print("total pairs", len(allp), flush=True)
samp = random.sample(allp, min(NS, len(allp))); cnt = collections.Counter()
for f, i, (s1, s2) in samp:
    y1 = np.rint(np.array([float(F(x)) for x in s1]) @ Binv).astype(np.int64); y2 = np.rint(np.array([float(F(x)) for x in s2]) @ Binv).astype(np.int64)
    a = RG @ y1; b = RG @ y2; Y = a * a + b * b
    w = "Y=5" if (Y == 5).any() else "Y=4" if (Y == 4).any() else "none(maxY=%d)" % Y.max()
    stage = "char-trap" if char_trap(L, y1, y2) is not None else "dualmin97" if min97_witness(L, y1, y2) is not None else "reaches setup/search"
    cnt[(stage, w)] += 1
for k, v in sorted(cnt.items()): print("   %-22s %-16s %6d" % (k[0], k[1], v))
