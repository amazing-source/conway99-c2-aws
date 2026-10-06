"""Build a queue order in which, inside each stream lattice, the jobs run heaviest-first, the weight being predicted by the root
energy I(y1) = sum over the roots (one per +- pair) of (r,y1)^2 of the job's y1 (on 016, v10: I >= 18 -> median 17-34 min and up to
100 min; I <= 14 -> under 2 min). The order of the lattices is kept. Golay lattices (001, 002) are left as they are.
  python heavy_first.py <repo> <pkg dir> <out keyfile>"""
import sys, os, json, subprocess, collections
REPO, PKG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
from fractions import Fraction as F
import frame_dfs_next as FD
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
g("fetch", "-q", "origin", "+refs/heads/queue:refs/remotes/origin/queue")
order = g("show", "origin/queue:order.txt").split()
done = {j for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip() for e in [json.loads(l)] if e["op"] == "done" for j in e["jobs"]}
free = [j for j in order if j not in done]
lat = []; by = collections.defaultdict(list)
for j in free:
    l = j.split(":")[0]
    if l not in by: lat.append(l)
    by[l].append(j)
keys = []
for l in lat:
    pf = os.path.join(PKG, "data", "finishC", "stream", l, "plan.json")
    if l in ("001", "002") or not os.path.exists(pf):
        keys += by[l]; print("%s: %5d keys, order kept" % (l, len(by[l]))); continue
    plan = json.load(open(pf)); Y = np.array(plan["y1_reps"], dtype=np.int64)
    gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % l)))["gens"]
    L = FD.lattice_data(gens, F(1)); G = L["G"]
    assert set(np.einsum("ij,jk,ik->i", Y, G, Y).tolist()) == {7}, "plan basis differs from the engine basis"
    I = ((Y @ (L["R"] @ G).T) ** 2).sum(axis=1)
    ks = []
    for j in by[l]:
        _, k, n = j.split(":"); assert int(n) == len(Y), (j, len(Y)); ks.append((int(I[int(k)]), int(k), j))
    ks.sort(key=lambda t: (-t[0], t[1])); keys += [t[2] for t in ks]
    h = collections.Counter(t[0] for t in ks)
    print("%s: %5d keys, heaviest first | I(y1): %s" % (l, len(ks), " ".join("%d:%d" % (i, h[i]) for i in sorted(h, reverse=True))))
assert sorted(keys) == sorted(free) and len(set(keys)) == len(keys)
open(OUT, "w", newline="\n").write("".join(k + "\n" for k in keys))
print("written %d keys to %s" % (len(keys), OUT))
