"""Profile (2,2,2) with ALL components with two lines per layer, triangles allowed (comp_m2_tri.json: 35 ordered types,
18 without triangle, 17 with triangles; 7 of the latter have 7-torsion and are NOT treated here).
Multisets of three torsion-free types up to a simultaneous permutation of the layers; those made of three triangle-free
types are already done (sweep_222r.log, sweep_222r2.log) and skipped.  Rank mode (rank <= 2, zero row sums), u = 0.
usage: python sweep222all.py workers"""
import sys, json, time, itertools, os
from multiprocessing import Pool
import fastlib
from multi import build, canon_ordered
TYPES = json.load(open("comp_m2_tri.json")); KEY = [tuple(tuple(x) for x in t["key"]) for t in TYPES]


def reps():
    index = {k: i for i, k in enumerate(KEY)}; perms = list(itertools.permutations(range(3)))
    act = [[index[canon_ordered(build(k), 4, order)] for order in perms] for k in KEY]
    good = [i for i, t in enumerate(TYPES) if t["torsion"] == 0]; out = set()
    for a in good:
        for b in good:
            if b < a: continue
            for c in good:
                if c < b: continue
                if all(TYPES[x]["triangles"] == 0 for x in (a, b, c)): continue
                out.add(min(tuple(sorted((act[a][s], act[b][s], act[c][s]))) for s in range(6)))
    return sorted(out)


def job(t):
    a, b, c = t; t0 = time.time()
    # the test vertex is vertex 0 of the first component: put a triangle-free type first when there is one
    order = sorted((a, b, c), key=lambda x: (TYPES[x]["triangles"], x))
    res = fastlib.run_rank([KEY[x] for x in order], [(0, 1, 2)] * 3, 0, tag=f"qa_{a}_{b}_{c}")
    return f"222all {a} {b} {c} first={order[0]} | {res} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    R = reps(); log = "sweep_222all.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(tuple(map(int, l.split("|")[0].split()[1:4])))
    todo = [t for t in R if t not in done]
    print(f"multisets with at least one triangle type, torsion-free, up to layer permutation: {len(R)}; to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = 0
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 9) as p:
        for line in p.imap_unordered(job, todo):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line[:300], flush=True)
    print(f"222 with triangles: runs {len(todo)}, not dead {bad}", flush=True)
