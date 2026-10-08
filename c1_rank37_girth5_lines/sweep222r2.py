"""(4,4,4), reduced: multisets of three ORDERED-layer triangle-free types with two lines per layer, up to a simultaneous
permutation of the layers; vertex u = 0 of the first component; rank mode (rank <= 2, zero row sums).
Results of sweep_222r.log (unreduced run, stopped) are reused when the same multiset was already done."""
import sys, json, time, itertools, os
from multiprocessing import Pool
import fastlib
from multi import build, canon_ordered
TYPES = json.load(open("comp_m2.json")); KEY = [tuple(tuple(x) for x in t["key"]) for t in TYPES]

def reps():
    index = {k: i for i, k in enumerate(KEY)}; perms = list(itertools.permutations(range(3)))
    act = [[index[canon_ordered(build(k), 4, order)] for order in perms] for k in KEY]
    nt = len(KEY); out = set()
    for a in range(nt):
        for b in range(a, nt):
            for c in range(b, nt):
                out.add(min(tuple(sorted((act[a][s], act[b][s], act[c][s]))) for s in range(6)))
    return sorted(out), act

def job(t):
    a, b, c = t; t0 = time.time()
    res = fastlib.run_rank([KEY[a], KEY[b], KEY[c]], [(0, 1, 2)] * 3, 0, tag=f"q222_{a}_{b}_{c}")
    return f"222r {a} {b} {c} | {res} | {time.time()-t0:.1f}s"

if __name__ == "__main__":
    R, act = reps(); done = set()
    for f in ("sweep_222r.log", "sweep_222r2.log"):
        if os.path.exists(f):
            for l in open(f):
                if "solutions 0 timeout 0" in l: done.add(tuple(map(int, l.split("|")[0].split()[1:4])))
    # a done multiset covers its whole orbit
    cov = set()
    for d in done:
        for s in range(6): cov.add(tuple(sorted((act[d[0]][s], act[d[1]][s], act[d[2]][s]))))
    todo = [t for t in R if t not in cov]
    print(f"multisets up to layer permutation: {len(R)}; already covered: {len(R) - len(todo)}; to do: {len(todo)}", flush=True)
    out = open("sweep_222r2.log", "a"); bad = 0
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 9) as p:
        for line in p.imap_unordered(job, todo):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"222 reduced: runs {len(todo)}, not dead {bad}", flush=True)
