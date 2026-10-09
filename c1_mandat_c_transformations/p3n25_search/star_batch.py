"""star engine on a list of supports.   usage: star_batch.py ids.json out.jsonl pool_size cp_workers"""
import sys, json, time, random
from multiprocessing import Pool
import p3n25_ilp as I, star as ST
FN = "register/supports_open_4581.jsonl"; CW = int(sys.argv[4]) if len(sys.argv) > 4 else 2
def job(sid):
    d = I.load(FN, sid); rng = random.Random(1000 + sid); out = {"id": sid, "delta": d["delta"], "pos": []}; t0 = time.time()
    for p in range(3):
        S = ST.Star(d, p); st, it, sol = S.run(rng, tl=300, workers=CW)
        out["pos"].append({"p": p, "u": S.u, "status": st, "cuts": S.cuts})
        if st == "no star": break
    out["dead"] = any(x["status"] == "no star" for x in out["pos"]); out["t"] = round(time.time() - t0, 1)
    return out
if __name__ == "__main__":
    ids = json.load(open(sys.argv[1])); done = set()
    try: done = {json.loads(l)["id"] for l in open(sys.argv[2])}
    except FileNotFoundError: pass
    ids = [i for i in ids if i not in done]
    with Pool(int(sys.argv[3])) as pl, open(sys.argv[2], "a") as out:
        for o in pl.imap_unordered(job, ids, chunksize=1):
            out.write(json.dumps(o) + "\n"); out.flush()
