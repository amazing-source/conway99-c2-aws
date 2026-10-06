"""The INCOMPLETE pairs left in old records of lattice 001: do they have a witness root (T18 / T20)?"""
import sys, os, json, subprocess, collections
REPO, PKG = sys.argv[1], os.path.abspath(sys.argv[2])
os.chdir(PKG); sys.path.insert(0, os.path.join(PKG, "scripts"))
os.environ.setdefault("FD_LEMMA_U", "1"); os.environ.setdefault("FD_SYM", "1"); os.environ.setdefault("FD_SYM3", "1"); os.environ["FD_MIN97"] = "1"
import numpy as np, glob
from fractions import Fraction as F
from frame_dfs_next import lattice_data, char_trap, min97_witness
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
ents = []
for r in g("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*").split():
    for f in g("ls-tree", "-r", "--name-only", r, "results").split():
        b = f.split("/")[-1]
        if b.startswith("001_") and b.endswith(".jsonl"):
            for l in g("show", r + ":" + f).splitlines():
                d = json.loads(l)
                for e in d.get("not_excluded", []) if isinstance(d.get("not_excluded"), list) else []:
                    if not str(e.get("verdict", "")).startswith("DEFERRED"):
                        ents.append((d["chunk"], e, d.get("code_sha", {}).get("frame_dfs_next.py"), d.get("node_limit"), r[-19:]))
print(len(ents), "not-excluded pairs in 001 records:", collections.Counter((tuple(c), e["verdict"], sha, lim) for c, e, sha, lim, r in ents))
d0 = json.load(open(sorted(glob.glob(os.path.join(PKG, "data", "golay", "001", "pairs_*.json")))[0]))
L = lattice_data([[F(x) for x in row] for row in d0["basis"]], F(1, int(d0["scale"])))
Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]])); RG = (L["R"] @ L["G"]).astype(np.int64)
conv = lambda v: np.rint(np.array([float(F(x)) for x in v]) @ Binv).astype(np.int64)
cnt = collections.Counter(); out = []
for c, e, sha, lim, r in ents:
    y1, y2 = conv(e["y1"]), conv(e["y2"]); u = RG @ y1; v = RG @ y2; Y = u * u + v * v
    w = "T18" if (Y == 5).any() else "T20" if (Y == 4).any() else "none"
    st = "min97" if min97_witness(L, y1, y2) is not None else "char" if char_trap(L, y1, y2) is not None else "search"
    cnt[(w, st)] += 1; out.append({"chunk": c, "index": e.get("index"), "witness": w, "v10_immediate": st, "nodes": e.get("nodes")})
print(dict(cnt))
json.dump(out, open(os.path.join(os.path.dirname(PKG), "incomplete_001.json"), "w"))
