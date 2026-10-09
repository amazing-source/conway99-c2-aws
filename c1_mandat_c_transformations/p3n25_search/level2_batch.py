"""level-2 filters + linear screen on a spread sample of supports that survive the plain linear screen.   usage: level2_batch.py n workers"""
import sys, json, glob, time, random, collections
from multiprocessing import Pool
import p3n25_ilp as I, level2 as L2
FN = "register/supports_open_4581.jsonl"
def job(sid):
    d = I.load(FN, sid); t0 = time.time()
    P = L2.prepare(d); pool = L2.make_pool(P["R"], P["dv"], random.Random(5)); c1, c2, pk = L2.filter_blocks(P, pool); keep = ~(c1 | c2 | pk)
    st = L2.lp_blocks(P, keep)
    return {"id": sid, "delta": d["delta"], "blocks": len(P["Ms"]), "C1": int(c1.sum()), "C2": int(c2.sum()), "P": int(pk.sum()), "left": int(keep.sum()), "lp": st, "t": round(time.time() - t0)}
if __name__ == "__main__":
    n, nw = int(sys.argv[1]), int(sys.argv[2])
    res = {}
    for f in glob.glob("phaseA/chunk_*.jsonl"):
        for l in open(f):
            rr = json.loads(l); res[rr["id"]] = (rr["status"], rr["delta"])
    alive = collections.defaultdict(list)
    for sid, (st, dl) in sorted(res.items()):
        if st == "feasible": alive[dl].append(sid)
    rng = random.Random(3); sample = []
    for dl in sorted(alive):
        rng.shuffle(alive[dl]); sample += alive[dl][:max(1, n // len(alive))]
    with Pool(nw) as pl, open("level2_batch.jsonl", "w") as out:
        for o in pl.imap_unordered(job, sample):
            out.write(json.dumps(o) + "\n"); out.flush()
            print(o, flush=True)
