import sys, json, subprocess, io, zipfile, collections
REPO = sys.argv[1]
H = collections.defaultdict(collections.Counter); W = collections.Counter(); NJ = collections.Counter(); seen = set()
for r in subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*"], capture_output=True, text=True).stdout.split():
    data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", r, "results"], capture_output=True).stdout
    if not data: continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for f in z.namelist():
        if not f.endswith(".jsonl"): continue
        for l in z.read(f).decode().splitlines():
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: continue
            if not isinstance(d, dict) or d.get("code_sha", {}).get("frame_dfs_next.py") != "1591aeeac9c0be5c" or not d.get("chunk_ok"): continue
            key = (d.get("id"), tuple(d.get("chunk") or ()))
            if key in seen: continue
            seen.add(key); lid = d["id"]
            for k, v in d.get("telemetry", {}).get("search_nodes_log2", {}).items(): H[lid][int(k)] += v
            W[lid] += d.get("wall_secs", 0); NJ[lid] += 1
for lid in sorted(H):
    h = H[lid]; tot = sum(h.values()); nodes = sum(v * 1.5 * 2 ** k for k, v in h.items())
    print("lattice %03d: %d jobs, %d searched pairs, wall %.0f h, ~%.3g nodes, %.3g nodes/s" % (lid, NJ[lid], tot, W[lid] / 3600, nodes, nodes / max(1, W[lid])))
    cum = 0; cn = 0
    for k in sorted(h):
        cum += h[k]; cn += h[k] * 1.5 * 2 ** k
        if k in (10, 13, 16, 18, 20, 22, 24, 26, 28, 30) or k == max(h):
            print("    nodes < 2^%-2d : %6.2f %% of searched pairs, %6.2f %% of the nodes" % (k + 1, 100.0 * cum / tot, 100.0 * cn / nodes))
