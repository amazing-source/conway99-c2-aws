"""Real-only star test (any rank) on a ball: realrun.py kind ...   (exploration)
   kind = 66 i j   : two components with three lines per layer (indices in comp_m3_all.json)
   kind = 222 i j k: three components with two lines per layer (indices in comp_m2.json order = types_m2.txt)"""
import sys, json, subprocess, os, time
import fastlib

def write(keys, u, path, limit=1, maxnodes=300000000):
    adj, lay, comp, K, quota, Gm, Hr = fastlib.ball_matrices(keys, [(0, 1, 2)] * len(keys))
    if Gm is None: Gm = [[0] * 36 for _ in range(36)]
    with open(path, "w") as f:
        f.write(f"{u} 0 0 {len(keys)} 1 {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, Gm):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for row in Hr: f.write(" ".join(f"{x:.12g}" for x in row) + "\n")

if __name__ == "__main__":
    kind = sys.argv[1]; idx = list(map(int, sys.argv[2:]))
    if kind == "66":
        T = json.load(open("comp_m3_all.json")); keys = [tuple(tuple(x) for x in T[i]["key"]) for i in idx]
    else:
        T = json.load(open("comp_m2.json")); keys = [tuple(tuple(x) for x in T[i]["key"]) for i in idx]
    for u in (0,):
        path = f"real_{kind}_{'_'.join(map(str, idx))}.txt"; write(keys, u, path); t0 = time.time()
        out = subprocess.run(["./realstar.exe", path], capture_output=True, text=True).stdout.strip().split("\n")
        os.remove(path)
        print(kind, idx, "u", u, "|", " / ".join(x[:230] for x in out[-3:]), f"| {time.time()-t0:.1f}s", flush=True)
