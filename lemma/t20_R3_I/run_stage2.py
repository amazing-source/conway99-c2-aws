# T20 round 3, case I: STAGE 2.  For every base of a stage-1 file (index = part mod nparts) the engine eng6
# enumerates the orbits of X_2 outside N(p) to exhaustion (model: cases6.CaseIN6).
# One line per base in <prefix>_<part>of<nparts>.jsonl (resumable: bases already present are skipped);
# at the end <prefix>_<part>of<nparts>.sum.json.
# usage: python run_stage2.py <stage1.json> <part> <nparts> <time limit per base, s> <prefix> [certs=N] [first=K] [width=W]
import sys, json, time, os, hashlib, traceback
import eng6, cases6

s1file, part, nparts, tlim, prefix = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
certs = 0
first = None
width = 0
for a in sys.argv[6:]:
    if a.startswith("certs="):
        certs = int(a[6:])
    if a.startswith("first="):
        first = int(a[6:])
    if a.startswith("width="):
        width = int(a[6:])
s1 = json.load(open(s1file))
name = s1["graph"]
ztype = tuple(tuple(t) for t in s1["ztype"]) if s1.get("ztype") else None
bases = s1["bases"]
profile = s1["profile"]
sha = hashlib.sha1(json.dumps(bases, sort_keys=True).encode()).hexdigest()
outname = "%s_%dof%d.jsonl" % (prefix, part, nparts)
done = {}
if os.path.exists(outname):
    for line in open(outname):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if not r.get("timeout") and not r.get("error"):
            done[r["i"]] = r
f = open(outname, "a")
t00 = time.time()
mine = [i for i in range(len(bases)) if i % nparts == part]
if first is not None:
    mine = mine[:first]
nbases = len(bases)
bases = {i: bases[i] for i in mine}          # only the bases of this part are kept in memory
del s1


def trim(v):
    v = list(v)
    while len(v) > 1 and v[-1] == 0:
        v.pop()
    return v

for i in mine:
    if i in done:
        continue
    t0 = time.process_time()
    rec = {"i": i}
    try:
        prob = cases6.CaseIN6(name, bases[i], ztype)
        if prob.impossible:
            rec.update({"timeout": False, "impossible": prob.impossible, "complete": 0, "visited": [], "kept": [],
                        "cand": [], "rej_b": [], "rej_p": [], "rej_rank": [], "stats": {}})
        else:
            out = eng6.run(prob, 0, 1, tlim, 99, "%s_c%d_b%d" % (prefix, part, i), save_certs=certs,
                           files=bool(certs), plan="mem", width=width)
            rec.update({"timeout": out["timeout"], "complete": len(out["survivors"]), "visited": trim(out["visited"]),
                        "kept": trim(out["kept"]), "cand": trim(out["candidates"]),
                        "rej_b": trim(out["rejected_budget"]), "rej_p": trim(out["rejected_psd"]),
                        "rej_rank": trim(out["rejected_rank"]), "stats": out["stats"], "plan": out["plan"]})
            if out["survivors"]:
                rec["survivors"] = out["survivors"]
    except Exception:
        rec["error"] = traceback.format_exc()
    rec["cpu"] = round(time.process_time() - t0, 3)
    f.write(json.dumps(rec) + "\n")
    f.flush()
    if not rec.get("timeout") and not rec.get("error"):
        done[i] = rec
f.close()
ok = [done[i] for i in mine if i in done]
L = max([len(r["visited"]) for r in ok] + [1])


def tot(key):
    return [sum(r[key][l] for r in ok if len(r[key]) > l) for l in range(L)]


summ = {"stage1": s1file, "graph": name, "profile": profile, "ztype": ztype, "bases_sha1": sha,
        "nbases": nbases, "part": part, "nparts": nparts, "mine": len(mine), "finished": len(ok),
        "unfinished": [i for i in mine if i not in done], "first": first,
        "complete": sum(r["complete"] for r in ok), "impossible": sum(1 for r in ok if r.get("impossible")),
        "visited": tot("visited"), "candidates": tot("cand"), "rejected_budget": tot("rej_b"),
        "rejected_psd": tot("rej_p"), "kept": tot("kept"), "rejected_rank": tot("rej_rank"),
        "max_depth": max([max([l for l in range(len(r["visited"])) if r["visited"][l]] + [0]) for r in ok] + [0]),
        "cpu": round(sum(r["cpu"] for r in ok), 1), "wall": round(time.time() - t00, 1), "engine": "eng6",
        "width": width}
st = {}
for r in ok:
    for k, v in r["stats"].items():
        st[k] = st.get(k, 0) + v
summ["stats"] = st
json.dump(summ, open("%s_%dof%d.sum.json" % (prefix, part, nparts), "w"))
print(json.dumps({k: v for k, v in summ.items() if k != "unfinished"}))
print("unfinished:", len(summ["unfinished"]))
