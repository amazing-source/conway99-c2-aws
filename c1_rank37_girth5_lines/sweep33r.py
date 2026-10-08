"""(6,6) balls WITHOUT prism of Gamma through an edge of T (no triangle, no type-I 4-cycle), both components without
7-torsion: every pair of ORDERED-layer types up to a simultaneous permutation of the layers and the exchange of the two
components; vertex u = 0 of the first component; rank mode (fastr.exe: rank <= 1 and zero row sums).
usage: sweep33r.py workers [part nparts]      (the list of pairs is split by index modulo nparts; logs can be merged)"""
import sys, json, time, itertools, os
from multiprocessing import Pool
import fastlib
from multi import build, canon_ordered

TYPES = json.load(open("comp_m3_all.json"))
KEY = [tuple(tuple(x) for x in t["key"]) for t in TYPES]


def action_table():
    if os.path.exists("act33.json"): return json.load(open("act33.json"))
    index = {k: i for i, k in enumerate(KEY)}
    perms = list(itertools.permutations(range(3))); act = []
    for i, k in enumerate(KEY):
        adj = build(k); act.append([index[canon_ordered(adj, 6, order)] for order in perms])
    json.dump(act, open("act33.json", "w"))
    return act


def pair_list():
    act = action_table()
    good = [i for i, t in enumerate(TYPES) if t["typeI"] == 0 and t["torsion"] == 0]
    gs = set(good); reps = set()
    for a in good:
        for b in good:
            if b < a: continue
            orbit = []
            for s in range(6):
                x, y = act[a][s], act[b][s]
                orbit.append((min(x, y), max(x, y)))
            reps.add(min(orbit))
    assert all(x in gs and y in gs for x, y in reps)
    return sorted(reps)


def job(p):
    a, b = p
    t0 = time.time()
    # scalar mode, both square classes of c0 (about three times faster than the rank mode when the residue has rank 1)
    r1 = fastlib.run([KEY[a], KEY[b]], [(0, 1, 2)] * 2, 0, 1, 0, use_real=0, tag=f"r33_{a}_{b}_1")
    r3 = fastlib.run([KEY[a], KEY[b]], [(0, 1, 2)] * 2, 0, 3, 0, use_real=0, tag=f"r33_{a}_{b}_3")
    ok = ("solutions 0 timeout 0" in r1) and ("solutions 0 timeout 0" in r3)
    return f"33r {a} {b} | c0=1: {r1} ; c0=3: {r3} ; {'solutions 0 timeout 0' if ok else 'CHECK'} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    part = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nparts = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    pairs = pair_list()
    mine = [p for i, p in enumerate(pairs) if i % nparts == part]
    log = f"sweep_33r_part{part}of{nparts}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [p for p in mine if f"33r {p[0]} {p[1]}" not in done]
    print(f"pairs in all: {len(pairs)}; this part: {len(mine)}; still to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"33 rank mode part {part}/{nparts}: runs {len(todo)}, not dead {bad}", flush=True)
