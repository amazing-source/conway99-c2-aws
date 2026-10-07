"""Acceptance of the re-run of the y1 representatives without code version (C2 lab, 2026-10-07). READS and REPORTS; written
before the records arrived.

  .venv/Scripts/python.exe scripts/cloud/rerun_713_check.py <manifest json (in aws_repo)> <branch> [<branch> ...] [--json out.json]

Records: results/<lid>_<k>_<n>.jsonl of the given branches origin/<branch> of the compute repository (machines of q/qaudit.py,
consumer "sweep"). For every job of the manifest:
  (a) a record exists; it passes every check of import_sweep.check (id and chunk = the job's, chunk_ok, engine = an engine of a lab
      package, verdict counts adding up to n_pairs, producer end line complete with the same sha256 and pair count, no unknown
      verdict) and it is DONE: chunk_done, no INCOMPLETE, no DEFERRED pair. A job found on two branches must give the same sha256.
Coverage, per lattice, from the accepted records only:
  (b) job with a plan and n = number of representatives of the plan: it covers the representative k;
  (c) job with a plan, the field "lll" and another n: it covers the representatives k, k+n, ... of that plan (the producer asserts
      that its basis is the plan's, so the indices mean the same on every machine);
  (d) job WITHOUT plan (identity file, y1 stage redone): its chunk is relative to the y1 list of the machine. The n chunks of a
      lattice are accepted as a tiling only if they all come from ONE branch (one machine: same reduced basis, same list); chunks
      spread over several machines are reported "tiling not verifiable" and the lattice is NOT accepted.
Result per lattice: "whole lattice re-covered" (every representative of the plan under (c), or a one-machine tiling under (d)), or
"representatives re-covered" with the list (b), compared with the list that had to be re-run (tier N of STREAM_RECOUNT minus the
fixed-y1 certificate); and the twin classes the new records defer pairs to, each of which must be excluded in the tracker.
Nothing is imported here."""
import sys, os, json, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import import_sweep as IS
LAB = IS.LAB; REPO = IS.REPO; SW = os.path.join(LAB, "data", "finishC", "sweep")


def git(*a): return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True).stdout.decode("utf-8", "replace")


def main():
    import twin_transfer as TT
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; man = json.load(open(os.path.join(REPO, args[0])))["jobs"]; branches = args[1:]
    ST, GO = IS.engines(); PAR = IS.wrapper_shas("q/par_consumer.py"); DEF = IS.wrapper_shas("q/defer_consumer.py"); CL = TT.classes()
    have = collections.defaultdict(dict)                                  # (lid, k, n) -> {branch: record}
    for b in branches:
        for x in git("ls-tree", "--name-only", "origin/%s:results" % b).split():
            if not x.endswith(".jsonl"): continue
            p = x[:-6].split("_")
            try: key = (p[0], int(p[1]), int(p[2]))
            except (ValueError, IndexError): continue
            rec = None
            for l in git("show", "origin/%s:results/%s" % (b, x)).splitlines():
                if '"verdicts"' in l:
                    try: rec = json.loads(l)
                    except ValueError: pass
            if rec is not None: have[key][b] = rec
    R = json.load(open(os.path.join(SW, "STREAM_RECOUNT_2026-10-07.json")))
    per = collections.defaultdict(lambda: {"jobs": 0, "accepted": 0, "problems": [], "reps": set(), "pairs": 0, "noplan": collections.defaultdict(set), "n_noplan": None,
                                            "twins": collections.Counter(), "verdicts": collections.Counter()})
    for m in man:
        l = m["lid"]; key = (l, m["k"], m["n"]); o = per[l]; o["jobs"] += 1; got = have.get(key, {})
        if not got: o["problems"].append("%s %d/%d: no record" % key); continue
        if len({d.get("sha256") for d in got.values()}) > 1: o["problems"].append("%s %d/%d: two branches, different streams" % key); continue
        b, d = sorted(got.items())[0]; bad = IS.check(d, l, m["k"], m["n"], ST, GO, PAR, DEF)
        if bad: o["problems"].append("%s %d/%d: %s" % (key + ("; ".join(bad)[:150],))); continue
        if IS.open_state(d) != "done": o["problems"].append("%s %d/%d: not done (%s)" % (key + ({IS.cls(v): c for v, c in d["verdicts"].items()},))); continue
        o["accepted"] += 1; o["pairs"] += d["n_pairs"]; o["twins"].update(d.get("twin_deferred") or {})
        for v, c in d["verdicts"].items(): o["verdicts"][IS.cls(v)] += c
        if m.get("plan"):
            pf = os.path.join(REPO, m["plan"][5:]) if m["plan"].startswith("repo:") else os.path.join(LAB, "c2_cloud_run_v10", m["plan"])
            NR = len(json.load(open(pf))["y1_reps"]); o["NR"] = NR
            if m["n"] != NR and not m.get("lll"): o["problems"].append("%s %d/%d: chunk of a plan in a basis that is not pinned" % key); continue
            o["reps"].update(range(m["k"], NR, m["n"]))
        else:
            o["noplan"][b].add(m["k"]); o["n_noplan"] = m["n"]
    out = {}; nok = 0
    print("%-4s %5s %8s %10s | %s" % ("lid", "jobs", "accepted", "pairs", "result"))
    for l in sorted(per):
        o = per[l]; need = None; res = "?"; ok = False
        if l in R:
            cov = set(json.load(open(os.path.join(SW, "certs_y1_rerun", "cert_y1_%s.json" % l)))["covered"]) if os.path.exists(os.path.join(SW, "certs_y1_rerun", "cert_y1_%s.json" % l)) else set()
            need = sorted(i for i in R[l]["reps_N"] if i not in cov)
        if o["n_noplan"]:
            full = [b for b, ks in o["noplan"].items() if ks == set(range(o["n_noplan"]))]
            if full: ok = not o["problems"]; res = "whole lattice re-covered: %d chunks of an identity run, all from one machine (%s)" % (o["n_noplan"], full[0])
            else: res = "NOT ACCEPTED: tiling not verifiable (chunks without plan spread over %s)" % ({b: len(ks) for b, ks in o["noplan"].items()},)
        elif "NR" in o and o["reps"] == set(range(o["NR"])):
            ok = not o["problems"]; res = "whole lattice re-covered: every one of the %d representatives of the plan" % o["NR"]
        elif need is not None:
            miss = sorted(set(need) - o["reps"]); ok = not miss and not o["problems"]
            res = "representatives re-covered: %d of the %d to re-run%s" % (len(set(need) & o["reps"]), len(need), "" if not miss else "; MISSING %s" % miss[:10])
        pend = sorted(k for k in o["twins"] if CL.get(eval(k), {"?"}) != {"excluded"})
        if pend: ok = False; res += "; twin classes not excluded: %d" % len(pend)
        if o["problems"]: res += "; problems: %d, e.g. %s" % (len(o["problems"]), o["problems"][0])
        nok += ok
        out[l] = {"ok": bool(ok), "jobs": o["jobs"], "accepted": o["accepted"], "pairs": o["pairs"], "result": res, "problems": o["problems"], "to_rerun": need,
                  "reps_covered": sorted(o["reps"]), "verdict_classes": dict(o["verdicts"]), "twin_classes": sorted(o["twins"])}
        print("%-4s %5d %8d %10d | %s%s" % (l, o["jobs"], o["accepted"], o["pairs"], "OK: " if ok else "", res))
    print("lattices accepted: %d of %d; jobs %d, records accepted %d; pairs of the accepted records %d" % (
        nok, len(per), sum(o["jobs"] for o in per.values()), sum(o["accepted"] for o in per.values()), sum(o["pairs"] for o in per.values())))
    if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
