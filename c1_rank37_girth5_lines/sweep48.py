"""Profile (4,8) without prism through an edge of T: a component with two lines per layer (7 ordered types without
type-I 4-cycle, 3 orbits under the permutations of the layers: representatives 0, 1, 3 of the list below) plus a
component with four lines per layer (types_m4_p0.txt, 81 959 ordered types, produced by: enumc.exe 4 types_m4_p0.txt 1).
One line per ball: exhaustive star search at vertex u = 0 of the small component, scalar mode, both classes of c0
(fast.exe).  'TORSION' = the large component has 7-torsion: to be treated separately with the torsion model.
usage: python sweep48.py workers [part nparts] [first last]
   part/nparts: only the balls whose index is = part modulo nparts;  first/last: only indices in [first, last)."""
import sys, os, time
from multiprocessing import Pool
import fastlib

SMALL = []
for line in open("types_m2.txt"):
    v = list(map(int, line.split()))
    if v[12] == 0: SMALL.append(((1, 0, 3, 2), tuple(v[0:4]), tuple(v[4:8]), tuple(v[8:12])))
REPS = [0, 1, 3]      # orbit representatives of the 7 small types under the 6 orders of the layers


def big_key(line):
    v = list(map(int, line.split()))
    return ((1, 0, 3, 2, 5, 4, 7, 6), tuple(v[0:8]), tuple(v[8:16]), tuple(v[16:24]))


def job(a):
    idx, s, b, line = a
    t0 = time.time()
    try:
        res = fastlib.run_both([SMALL[s], big_key(line)], [(0, 1, 2)] * 2, 0, tag=f"s48_{s}_{b}")
    except Exception as ex:
        res = f"ERROR {type(ex).__name__}: {ex}"
    return f"48 {s} {b} | {res} | {time.time()-t0:.1f}s"


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    part = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nparts = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    first = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    lines = [l for l in open("types_m4_p0.txt").read().split("\n") if l.strip()]
    assert len(lines) == 81959, "types_m4_p0.txt must have 81959 lines"
    last = int(sys.argv[5]) if len(sys.argv) > 5 else len(REPS) * len(lines)
    jobs = [(i, REPS[i // len(lines)], i % len(lines), lines[i % len(lines)]) for i in range(len(REPS) * len(lines))
            if i % nparts == part and first <= i < last]
    if os.path.exists("reps48.txt"):       # one ball per isomorphism class (reps48.py)
        keep = {tuple(map(int, l.split()[:2])) for l in open("reps48.txt") if l.strip()}
        jobs = [j for j in jobs if (j[1], j[2]) in keep]
        print(f"restricted to the representatives of reps48.txt ({len(keep)} balls in all)", flush=True)
    log = f"sweep_48_part{part}of{nparts}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [j for j in jobs if f"48 {j[1]} {j[2]}" not in done]
    print(f"balls in this part: {len(jobs)}; to do: {len(todo)}", flush=True)
    out = open(log, "a"); bad = tors = 0; n = 0; t0 = time.time()
    with Pool(workers) as pool:
        for line in pool.imap_unordered(job, todo, chunksize=8):
            out.write(line + "\n"); n += 1
            if n % 200 == 0: out.flush()
            if "TORSION" in line: tors += 1
            elif "solutions 0 timeout 0 |" not in line: bad += 1; print("NOT DEAD:", line, flush=True)
            if n % 5000 == 0: print(f"{n} done, {tors} with torsion, {bad} not dead, {time.time()-t0:.0f}s", flush=True)
    out.close()
    print(f"(4,8) part {part}/{nparts}: runs {len(todo)}, with torsion {tors}, not dead {bad}", flush=True)
