"""Second, clean pass of the profile (2,2,2) without triangle: the 275 multisets of sweep222r2.py, all of them, with
temporary files private to each process (fastlib now puts the process id in their names).  The search is deterministic,
so the node counts must be identical to those of the first pass (sweep_222r.log / sweep_222r2.log); the comparison is
printed at the end.  usage: python sweep222pass2.py workers"""
import sys, re, os
from multiprocessing import Pool
import sweep222r2 as first

if __name__ == "__main__":
    R, act = first.reps(); log = "sweep_222pass2.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(tuple(map(int, l.split("|")[0].split()[1:4])))
    todo = [t for t in R if t not in done]
    print(f"multisets: {len(R)}; to do: {len(todo)}", flush=True)
    out = open(log, "a")
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 9) as p:
        for line in p.imap_unordered(first.job, todo):
            out.write(line + "\n"); out.flush()
    out.close()
    def load(f):
        d = {}
        if os.path.exists(f):
            for l in open(f):
                m = re.search(r"cands (\d+) nodes (\d+) solutions (\d+) timeout (\d+)", l)
                if m: d[tuple(map(int, l.split("|")[0].split()[1:4]))] = tuple(map(int, m.groups()))
        return d
    old = load("sweep_222r.log"); old.update(load("sweep_222r2.log")); new = load(log)
    # a multiset of the first pass may be written with another representative of its orbit
    canon = lambda t: min(tuple(sorted((act[t[0]][s], act[t[1]][s], act[t[2]][s]))) for s in range(6))
    oldc = {}
    for k, v in old.items(): oldc.setdefault(canon(k), set()).add((k, v))
    same = diff = missing = 0
    for k, v in new.items():
        hits = [w for (kk, w) in oldc.get(canon(k), ()) if kk == k]
        if not hits: missing += 1
        elif v in hits: same += 1
        else: diff += 1; print("DIFFERENT:", k, v, hits, flush=True)
    dead = sum(1 for v in new.values() if v[2] == 0 and v[3] == 0)
    print(f"second pass: {len(new)} multisets, dead {dead}; identical (cands, nodes) to the first pass: {same}, different: {diff}, "
          f"not run under the same representative in the first pass: {missing}", flush=True)
