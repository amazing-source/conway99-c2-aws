"""Coverage of the rigid-kernel audit H2, lattice by lattice (C2 lab, 2026-10-07). READS and REPORTS; writes only its json.

  .venv/Scripts/python.exe scripts/cloud/audit_coverage.py [--json out.json]

Sources of audit files (outputs of q/audit_rigid.py, one per job = chunk k/n of the pair stream of a lattice):
  lab     data/finishC/sweep/audit_rigid/<lid>_<k>_<n>.json          (lab PC, identity-only symmetry file)
  branch  audit/<lid>_<k>_<n>.json of every branch origin/run/* of the compute repo (machines of q/qaudit.py)
  001     aws_repo/measures/AUDIT_RIGID_golay_001.json               (Golay pair files, no chunk)
A file counts only if stream_ok (complete producer stream, hashed) and ok (every exposed pair EXCLUDED again by the general kernel).
The jobs are those of aws_repo/measures/AUDIT_RIGID_MANIFEST_2026-10-07.json (+ ..._003_extra_...).

Rule of coverage:
  * lattice with a plan (package symmetry file and plan; chunk k/n = the y1 representatives k, k+n, ... of the plan, whatever n):
    every representative is in the chunk of an accepted file, or is listed in a checked fixed-y1 certificate
    (data/finishC/sweep/certs_y1, q/check_cert_y1.py): then no frame has this y1 whatever the kernel did, PENDING T18 and T20.
    When no representative is covered twice, the pairs of the selected files must add up to the pairs of the sweep's records
    (manifest field pairs_expected_lattice) minus nothing: the certificate is used only where the audit has no file.
  * lattice without plan (identity-only symmetry file; the chunks k/n are relative to the producer's own list of y1): ONE source
    (the lab folder or one branch) must hold all the chunks 0..n-1 of one n. Files of different sources are never mixed: two
    machines may have used different symmetry files for the same lattice (077, 079, 080, 103 on 07/10).
Also reported: files of the same job from different sources with different stream sha256 (different symmetry files), the
versions of q/audit_rigid.py and of the engine, the exposed pairs and those that had reached a search."""
import sys, os, json, glob, subprocess, collections, hashlib
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); REPO = os.path.join(LAB, "aws_repo")
AT_RISK = "001 003 006 007 014 022 023 024 026 027 028 037 049 050 052 053 077 079 080 101 103 104 105 137 138".split()


def git(*a): return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True).stdout.decode("utf-8", "replace")


def y1_reps(lid):
    f = os.path.join(LAB, "data", "finishC", "sweep", "certs_y1", "cert_y1_%s.json" % lid)
    if not os.path.exists(f): return set(), None
    r = subprocess.run([sys.executable, "-I", os.path.join(REPO, "q", "check_cert_y1.py"), os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", lid + ".json"),
                        os.path.join(LAB, "data", "finishC", "stream", lid, "plan.json"), f], capture_output=True, text=True)
    if not (r.returncode == 0 and r.stdout.strip().splitlines()[-1:] == ["ok"]): return set(), None
    return {int(k) for k in json.load(open(f))["reps"]}, hashlib.sha256(open(f, "rb").read()).hexdigest()


def main():
    jobs = []
    for f in ("AUDIT_RIGID_MANIFEST_2026-10-07.json", "AUDIT_RIGID_MANIFEST_003_extra_2026-10-07.json"):
        jobs += json.load(open(os.path.join(REPO, "measures", f)))["jobs"]
    info = {}
    for j in jobs: info.setdefault(j["lid"], j)
    files = collections.defaultdict(list)                                 # lid -> [(source, d)]
    for f in glob.glob(os.path.join(LAB, "data", "finishC", "sweep", "audit_rigid", "*_*_*.json")):
        d = json.load(open(f)); files["%03d" % d["id"]].append(("lab", d))
    nb = 0
    for b in git("branch", "-r", "--list", "origin/run/*").split():
        names = [x for x in git("ls-tree", "--name-only", b + ":audit").split() if x.endswith(".json") and not x.startswith("SUMMARY")] if git("ls-tree", "-d", "--name-only", b, "audit").strip() else []
        if not names: continue
        nb += 1
        for x in names:
            try: d = json.loads(git("show", "%s:audit/%s" % (b, x)))
            except ValueError: continue
            if "counts" in d and "n_pairs" in d and "sha256" in d and not d.get("kind"): files["%03d" % d["id"]].append((b.replace("origin/", ""), d))
    out = {}; print("branches with audit files: %d" % nb)
    print("%-4s %-34s %5s %10s %8s %8s %7s %6s | %s" % ("lid", "source", "files", "pairs", "rigid", "zero-cand", "exposed", "notex", "coverage"))
    for lid in AT_RISK:
        if lid == "001":
            d = json.load(open(os.path.join(REPO, "measures", "AUDIT_RIGID_golay_001.json")))
            good = bool(d.get("ok") and d.get("stream_ok")); c = d["counts"]
            out[lid] = {"covered": good, "source": "Golay pair files", "pairs": d["n_pairs"], "counts": c, "exposed_not_excluded_again": d["exposed_not_excluded_again"]}
            print("%-4s %-34s %5d %10d %8d %8d %7d %6d | %s" % (lid, "Golay pair files", 1, d["n_pairs"], c["rigid"], c["with_zero_candidate"], c["exposed"], d["exposed_not_excluded_again"], "COVERED" if good else "NOT COVERED"))
            continue
        F = [(s, d) for s, d in files.get(lid, []) if d.get("stream_ok") and d.get("ok") and d.get("chunk")]
        bad = [(s, d.get("chunk")) for s, d in files.get(lid, []) if not (d.get("stream_ok") and d.get("ok"))]
        bysha = collections.defaultdict(set)
        for s, d in F: bysha[tuple(d["chunk"])].add(d["sha256"])
        differ = sorted(k for k, v in bysha.items() if len(v) > 1)
        j = info.get(lid, {}); o = {"files_accepted": len(F), "files_not_ok": bad[:20], "same_job_different_stream": differ[:20]}
        if j.get("plan"):
            NR = len(json.load(open(os.path.join(LAB, "data", "finishC", "stream", lid, "plan.json")))["y1_reps"]); cov = [0] * NR; sel = []; seen = set()
            for s, d in sorted(F, key=lambda t: (t[1]["chunk"][1], t[1]["chunk"][0], t[0])):
                k, n = d["chunk"]
                if (k, n) in seen or all(cov[i] for i in range(k, NR, n)): continue
                seen.add((k, n)); sel.append((s, d))
                for i in range(k, NR, n): cov[i] += 1
            yc, ysha = y1_reps(lid); by_cert = [i for i in range(NR) if not cov[i] and i in yc]; miss = [i for i in range(NR) if not cov[i] and i not in yc]
            dbl = sum(1 for x in cov if x > 1); pairs = sum(d["n_pairs"] for _, d in sel)
            exp = j.get("pairs_expected_lattice"); tot_ok = dbl > 0 or by_cert or pairs == exp
            good = not miss and bool(tot_ok)
            cv = ("COVERED" if good else "NOT COVERED") + ": %d of %d y1 representatives by audit files" % (NR - len(miss) - len(by_cert), NR)
            if by_cert: cv += "; %d by the fixed-y1 certificate, PENDING T18 and T20: %s" % (len(by_cert), by_cert)
            if miss: cv += "; MISSING %s" % (miss[:12],)
            if not by_cert and not dbl: cv += "; pairs %s the sweep's %s" % ("=" if pairs == exp else "DIFFER from", exp)
            if dbl: cv += "; %d representatives twice" % dbl
            src = "plan, %d source(s)" % len({s for s, _ in sel})
            o.update(kind="plan", y1_reps=NR, by_certificate=by_cert, certificate_sha256=ysha if by_cert else None, missing=miss, covered_twice=dbl, pairs_expected=exp)
        else:
            best = None
            for s in sorted({s for s, _ in F}):
                for n in sorted({d["chunk"][1] for s2, d in F if s2 == s}):
                    mine = {d["chunk"][0]: d for s2, d in F if s2 == s and d["chunk"][1] == n}
                    if set(mine) == set(range(n)) and (best is None or s == "lab"): best = (s, [(s, mine[k]) for k in range(n)])
            sel = best[1] if best else []; good = bool(best); pairs = sum(d["n_pairs"] for _, d in sel)
            src = best[0] if best else "-"
            cv = ("COVERED: all %d chunks from one source" % len(sel)) if good else "NOT COVERED: no single source has all the chunks (%s)" % (
                sorted(collections.Counter((s, d["chunk"][1]) for s, d in F).items()),)
            o.update(kind="identity", other_complete_sources=sorted({s for s in {s for s, _ in F} if s != src and
                     any(set(d["chunk"][0] for s2, d in F if s2 == s and d["chunk"][1] == n) == set(range(n)) for n in {d["chunk"][1] for s2, d in F if s2 == s})}))
        c = collections.Counter()
        for _, d in sel:
            for k, v in d["counts"].items(): c[k] += v
        reached = sum(1 for _, d in sel for e in d.get("exposed", []) if "stage 1" in str(e.get("verdict_general_kernel")) or (e.get("nodes") or 0) > 0)
        o.update(covered=good, source=src, files_selected=len(sel), pairs=pairs, counts=dict(c), exposed_not_excluded_again=sum(d["exposed_not_excluded_again"] for _, d in sel),
                 exposed_listed=sum(len(d.get("exposed", [])) for _, d in sel), exposed_with_search_nodes=reached, coverage=cv,
                 audit_rigid_sha256=sorted({d.get("audit_rigid_sha256") for _, d in sel}), engine_sha256=sorted({d.get("engine_sha256") for _, d in sel}))
        out[lid] = o
        print("%-4s %-34s %5d %10d %8d %8d %7d %6d | %s%s%s" % (lid, src[:34], len(sel), pairs, c["rigid"], c["with_zero_candidate"], c["exposed"], o["exposed_not_excluded_again"], cv,
                                                            "; files not ok: %d" % len(bad) if bad else "", "; same job, different streams: %d" % len(differ) if differ else ""))
    print("covered: %d of %d lattices at risk treated by the engine; not covered: %s" % (sum(1 for v in out.values() if v["covered"]), len(AT_RISK), [l for l in AT_RISK if not out[l]["covered"]]))
    if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
