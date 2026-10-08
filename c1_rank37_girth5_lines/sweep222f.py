"""(4,4,4) = three triangle-free components with two lines per layer: every multiset of three ORDERED-layer types,
both classes of binary forms <1,1> and <1,3>, vertex u = 0 of the first component; fast.exe without the real filter."""
import sys, json, time
from multiprocessing import Pool
import fastlib

def job(a):
    i1, i2, i3, C1 = a
    types = json.load(open("comp_m2.json")); key = lambda t: tuple(tuple(x) for x in t["key"])
    t0 = time.time()
    res = fastlib.run([key(types[i1]), key(types[i2]), key(types[i3])], [(0, 1, 2)] * 3, 0, 1, C1, use_real=0, tag=f"s222_{i1}_{i2}_{i3}_{C1}")
    return f"222 {i1} {i2} {i3} form=<1,{C1}> | {res} | {time.time()-t0:.1f}s"

if __name__ == "__main__":
    nt = len(json.load(open("comp_m2.json")))
    jobs = [(i1, i2, i3, C1) for i1 in range(nt) for i2 in range(i1, nt) for i3 in range(i2, nt) for C1 in (1, 3)]
    done = set()
    try:
        for l in open("sweep_222f.log"): done.add(l.split("|")[0].strip())
    except FileNotFoundError: pass
    jobs = [j for j in jobs if f"222 {j[0]} {j[1]} {j[2]} form=<1,{j[3]}>" not in done]
    out = open("sweep_222f.log", "a"); bad = 0
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as p:
        for line in p.imap_unordered(job, jobs):
            out.write(line + "\n"); out.flush()
            if "solutions 0 timeout 0" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
    print(f"222 fast: runs {len(jobs)}, not dead {bad}", flush=True)
