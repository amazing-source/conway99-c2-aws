"""does a richer pool of (w, a) kill more?  compares pools on supports alive after the standard level-2 pass.   usage: level2_rich.py workers"""
import sys, json, time, random
from multiprocessing import Pool
import numpy as np
import p3n25_ilp as I, level2 as L2
FN = "register/supports_open_4581.jsonl"
def job(sid):
    d = I.load(FN, sid); t0 = time.time(); P = L2.prepare(d); out = {"id": sid, "delta": d["delta"], "blocks": len(P["Ms"])}
    for name, kw in (("std", dict()), ("rich", dict(thresh=24, restarts=1500, wmax=3, cap=12000))):
        pool = L2.make_pool(P["R"], P["dv"], random.Random(5), **kw); c1, c2, pk = L2.filter_blocks(P, pool); keep = ~(c1 | c2 | pk)
        Bm = P["Bm"][keep]; cover = Bm.T @ Bm
        deadp = sum(1 for s in range(28) for t in range(s + 1, 28) if P["r"][s][t] > 0 and cover[s, t] < P["r"][s][t])
        out[name] = {"pool": len(pool[0]), "left": int(keep.sum()), "dead_pairs": deadp, "lp": L2.lp_blocks(P, keep) if not deadp else "dead pair"}
    out["t"] = round(time.time() - t0); return out
if __name__ == "__main__":
    rs = [json.loads(l) for l in open("level2_batch.jsonl")]
    ids = [r["id"] for r in rs if r["lp"] == "feasible" and r["delta"] <= 7][:24]
    with Pool(int(sys.argv[1])) as pl:
        for o in pl.imap_unordered(job, ids): print(json.dumps(o), flush=True)
