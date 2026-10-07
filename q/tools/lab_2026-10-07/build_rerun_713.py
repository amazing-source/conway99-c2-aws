"""Manifest of the re-run of the y1 representatives whose only records carry no code version (C2 lab, 2026-10-07).

  .venv/Scripts/python.exe scripts/cloud/build_rerun_713.py          (writes into aws_repo/; nothing is launched)

The list: for each stream lattice, the representatives of tier N of sweep/STREAM_RECOUNT (covered only by records without code
version) that are NOT listed in the checked fixed-y1 certificate sweep/certs_y1_rerun/cert_y1_<lid>.json. One job per
representative, in the format of q/qaudit.py with "consumer": "sweep": chunk k/n with n = the number of y1 representatives of the
plan, so that the chunk is exactly the representative k.
Two kinds of lattices:
  A. in the basis cache of package v10 (lll_cache.json) and with plan and symmetry file in the package: the package's own files;
     the lab plan is checked to be byte-identical to the package's.
  B. not in the cache: the producer runs through q/producer_lll.py with the lab PC's reduced basis (measures/rerun_713/lll_lab.json,
     checked here: its sha is the plan's basis_sha), an identity-only symmetry file, and a plan that is the lab plan with the
     symmetry fields set for that file (same y1 representatives, same order, same basis). With the identity file the y2 of a y1
     are taken up to sign only: a superset of the Gamma-reduced list, complete for that y1; and the y1 representatives are those
     of the lab's Gamma-orbits, so the orbit is covered.
Order of the jobs: round robin over the lattices, so that a share i/N of the list is a mix. Sample: one job in 50, drawn with
random.Random(713), completed if needed so that both kinds occur; written apart."""
import sys, os, json, hashlib, random
from fractions import Fraction as F
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); REPO = os.path.join(LAB, "aws_repo"); PKG = os.path.join(LAB, "c2_cloud_run_v10")
SW = os.path.join(LAB, "data", "finishC", "sweep"); sys.path.insert(0, os.path.join(PKG, "c1", "code"))


def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def dump(obj, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="ascii", newline="\n") as f: json.dump(obj, f)


def main():
    import y_pairs as YP
    R = json.load(open(os.path.join(SW, "STREAM_RECOUNT_2026-10-07.json"))); cache = json.load(open(os.path.join(PKG, "c1", "code", "lll_cache.json")))
    per = {}; lll = {}; kinds = {}
    for l, v in sorted(R.items()):
        if not v["reps_N"]: continue
        cov = set(json.load(open(os.path.join(SW, "certs_y1_rerun", "cert_y1_%s.json" % l)))["covered"])
        reps = [i for i in v["reps_N"] if i not in cov]
        if not reps: continue
        lp = os.path.join(LAB, "data", "finishC", "stream", l, "plan.json"); P = json.load(open(lp)); NR = len(P["y1_reps"]); assert NR == v["y1_reps"]
        gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", l + ".json")))["gens"]
        B0 = YP.to_int_basis(gens); key = hashlib.sha256(json.dumps([[str(F(x)) for x in row] for row in B0]).encode()).hexdigest()
        B = YP.lll(B0); Bs = [[str(x) for x in row] for row in B]
        assert hashlib.sha256(json.dumps(Bs).encode()).hexdigest()[:16] == P["basis_sha"], "the lab basis of %s is not the basis of its plan" % l
        pp = os.path.join(PKG, "data", "finishC", "stream", l, "plan.json"); gd = os.path.join(PKG, "gamma", l)
        if key in cache and os.path.exists(pp):
            assert sha16(pp) == sha16(lp), l; g = [f for f in os.listdir(gd) if f.endswith(".json")]; assert len(g) == 1
            assert sha16(os.path.join(gd, g[0])) == P["gamma_sha"], "package symmetry file of %s is not the plan's" % l
            job = {"gamma": "gamma/%s/%s" % (l, g[0]), "plan": "data/finishC/stream/%s/plan.json" % l}; kinds[l] = "A"
        else:
            lll[key] = [[str(F(x)) for x in row] for row in B]
            gi = os.path.join(REPO, "q", "audit_data", "gamma_%s_identity.json" % l)
            if not os.path.exists(gi):
                dump({"id": int(l), "gamma_order": 1, "matrices": [[[int(i == j) for j in range(24)] for i in range(24)]]}, gi)
            P2 = {"id": P["id"], "plan": dict(P["plan"], gamma=1, gamma_converted=False, note="lab plan of %s with an identity-only symmetry file (rerun_713)" % l),
                  "gamma_sha": sha16(gi), "basis_sha": P["basis_sha"], "y1_reps": P["y1_reps"]}
            dump(P2, os.path.join(REPO, "measures", "rerun_713", "plan_%s.json" % l))
            job = {"gamma": "repo:q/audit_data/gamma_%s_identity.json" % l, "plan": "repo:measures/rerun_713/plan_%s.json" % l, "lll": "repo:measures/rerun_713/lll_lab.json"}; kinds[l] = "B"
        per[l] = [dict(job, lid=l, k=i, n=NR, batch=4, consumer="sweep", kind=kinds[l]) for i in reps]
    dump(lll, os.path.join(REPO, "measures", "rerun_713", "lll_lab.json"))
    jobs = []; queues = {l: list(v) for l, v in per.items()}
    while any(queues.values()):
        for l in sorted(queues):
            if queues[l]: jobs.append(queues[l].pop(0))
    rng = random.Random(713); idx = sorted(rng.sample(range(len(jobs)), max(1, len(jobs) // 50)))
    for want in ("A", "B"):
        if not any(jobs[i]["kind"] == want for i in idx): idx.append(next(i for i in rng.sample(range(len(jobs)), len(jobs)) if jobs[i]["kind"] == want))
    what = ("re-run with package v10 of the y1 representatives of the stream lattices whose only records have no code version and that have no fixed-y1 "
            "certificate (scripts/cloud/build_rerun_713.py; lists from measures/STREAM_RECOUNT_2026-10-07.json and measures/cert_y1_rerun). One representative "
            "per job (chunk k/n, n = representatives of the plan), consumer = the package's sweep consumer. kind A: package plan and symmetry file. kind B: "
            "q/producer_lll.py with the lab basis, identity-only symmetry file, lab plan adapted (measures/rerun_713).")
    dump({"what": what, "per_lattice": {l: {"kind": kinds[l], "jobs": len(v), "y1_reps": v[0]["n"]} for l, v in sorted(per.items())}, "jobs": jobs},
         os.path.join(REPO, "measures", "RERUN_713_MANIFEST_2026-10-07.json"))
    dump({"what": "SAMPLE of RERUN_713_MANIFEST: one job in 50 drawn with random.Random(713) (+ one of each kind if missing); to measure the cost per stage first",
          "indices_in_the_manifest": sorted(idx), "jobs": [jobs[i] for i in sorted(idx)]}, os.path.join(REPO, "measures", "RERUN_713_SAMPLE_2026-10-07.json"))
    print("jobs %d in %d lattices; kind A %d jobs (%s); kind B %d jobs (%s); sample %d jobs: %s" % (
        len(jobs), len(per), sum(j["kind"] == "A" for j in jobs), " ".join(l for l in sorted(per) if kinds[l] == "A"),
        sum(j["kind"] == "B" for j in jobs), " ".join(l for l in sorted(per) if kinds[l] == "B"), len(idx), [(jobs[i]["lid"], jobs[i]["k"]) for i in sorted(idx)]))


if __name__ == "__main__":
    main()
