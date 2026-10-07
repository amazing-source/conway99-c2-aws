"""Conversion step of the deferral sweep (C2 lab, 2026-10-07): which open lattices can be marked EXCLUDED, and what blocks the others.
DRY RUN unless --write. It never treats a DEFERRED pair as excluded on the strength of an unproved lemma.

  .venv/Scripts/python.exe scripts/cloud/convert_deferred.py <SWEEP_LAB json of import_sweep.py>
        [--assume T18,T20]            dry run only: pretend these lemmas are accepted (shows the end state)
        [--certs <dir> [<dir> ...]]   folders holding the stream certificates <lid>_<k>_<n>.json (q/qcert.py)
        [--golay-certs <file> ...]    certificates of the Golay lattices (cert_golay.py)
        [--no-cert]                   dry run only: do not require the certificates (they are counted as missing)
        [--write]                     update the tracker; refused with --assume or --no-cert

A lattice is excludable when ALL of these hold:
  1. swept: every y1 representative (stream) or every pair (Golay) is covered, nothing INCOMPLETE, no unknown verdict;
  2. every lemma its DEFERRED pairs rest on is accepted: data/finishC/lemmas_accepted.json, {"T18": {"reference": ..., "date": ...},
     "T20": {...}} (written by hand when the lemma is proved and independently checked; absent today);
  3. every record with DEFERRED pairs has its certificate: same stream sha256, ok = true, as many certified pairs as deferred ones;
  4. every twin class its records deferred pairs to consists of lattices that are excluded in the tracker or excludable here
     (fixed point, as scripts/stream_finish.py does);
  5. if y1 representatives are covered by a fixed-y1 certificate (field y1_cert of the import): T18 AND T20 are accepted, the file
     data/finishC/sweep/certs_y1/<file> has the sha256 recorded by the import, and the standalone checker q/check_cert_y1.py passes
     again here and lists every such representative."""
import sys, os, json, glob, collections, hashlib, subprocess
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(LAB, "scripts"))


def args_after(flag):
    if flag not in sys.argv: return []
    i = sys.argv.index(flag) + 1; out = []
    while i < len(sys.argv) and not sys.argv[i].startswith("--"): out.append(sys.argv[i]); i += 1
    return out


def y1_ok(lid, yc):
    f = os.path.join(LAB, "data", "finishC", "sweep", "certs_y1", yc["file"])
    if not os.path.exists(f) or hashlib.sha256(open(f, "rb").read()).hexdigest() != yc["sha256"]: return False
    r = subprocess.run([sys.executable, "-I", os.path.join(LAB, "aws_repo", "q", "check_cert_y1.py"), os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", lid + ".json"),
                        os.path.join(LAB, "data", "finishC", "stream", lid, "plan.json"), f], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip().splitlines()[-1:] == ["ok"] and set(yc["reps"]) <= {int(k) for k in json.load(open(f))["reps"]}


def main():
    import twin_transfer as TT
    S = json.load(open(sys.argv[1]))["lattices"]
    assume = set((args_after("--assume") or [""])[0].split(",")) - {""}; nocert = "--no-cert" in sys.argv; write = "--write" in sys.argv
    assert not (write and (assume or nocert)), "--write needs the real lemma file and the real certificates"
    lf = os.path.join(LAB, "data", "finishC", "lemmas_accepted.json"); accepted = json.load(open(lf)) if os.path.exists(lf) else {}
    lemmas = set(accepted) | assume
    trk = os.path.join(LAB, "data", "finishC", "finishC_tracker.json"); T = json.load(open(trk)); byid = {"%03d" % v["id"]: v for v in T["lattices"]}
    cls_of = collections.defaultdict(set)
    for v in T["lattices"]: cls_of[TT.parse(v["roots"]) if v["nroots"] else ()].add("%03d" % v["id"])
    certs = {}
    for d in args_after("--certs"):
        for f in glob.glob(os.path.join(d, "*_*_*.json")):
            try: c = json.load(open(f))
            except Exception: continue
            if "chunk" in c and "sha256" in c: certs[("%03d" % c["id"], c["chunk"][0], c["chunk"][1], c["sha256"])] = c
    gcert = {}
    for f in args_after("--golay-certs"):
        c = json.load(open(f)); gcert["%03d" % c["id"]] = c
    block = {}
    for lid, o in S.items():
        b = []
        if o.get("not_covered") or o.get("incomplete"): b.append("not swept (%s not covered, %s incomplete)" % (o.get("not_covered"), o.get("incomplete")))
        n18, n20 = o.get("defer_T18", 0), o.get("defer_T20", 0)
        if n18 and "T18" not in lemmas: b.append("T18 not accepted (%d pairs)" % n18)
        if n20 and "T20" not in lemmas: b.append("T20 not accepted (%d pairs)" % n20)
        yc = o.get("y1_cert")
        if yc:
            for t in ("T18", "T20"):
                if t not in lemmas and not any(x.startswith(t + " not accepted") for x in b):
                    b.append("%s not accepted (fixed-y1 certificate, %d y1 representatives)" % (t, len(yc["reps"])))
            if not y1_ok(lid, yc): b.append("fixed-y1 certificate missing, changed or not passing its checker")
        if o["kind"] == "golay":
            c = gcert.get(lid)
            good = (c is not None and c.get("ok") is True and c["pairs_total"] == o["pairs"] and c["T18"]["certified"] == n18 and c["T20"]["certified"] == n20
                    and c["state"]["not_covered"] == 0 and c["state"]["incomplete_or_other"] == 0)
            if (n18 or n20) and not good: b.append("Golay certificate missing or not matching")
        else:
            miss = 0
            for k, n, sha, t18, t20, *rest in o.get("deferral_records", []):
                c = certs.get((lid, k, n, sha)); t20n = rest[0] if rest else 0
                if not (c is not None and c.get("ok") is True and c.get("stream_ok") is True and c["T18"]["certified"] == t18 and c["T20"]["certified"] == t20
                        and (c.get("T20_norm4") or {}).get("certified", 0) == t20n): miss += 1
            if miss: b.append("certificates missing: %d of %d records" % (miss, len(o.get("deferral_records", []))))
        block[lid] = b
    if nocert: block = {l: [x for x in b if "ertificate" not in x] for l, b in block.items()}
    can = set()
    while True:
        new = set()
        for lid, o in S.items():
            if lid in can or block[lid]: continue
            pend = [k for k in o.get("twin_all", []) if any(byid[m]["status"] != "excluded" and m not in can for m in cls_of.get(eval(k), {"?"}) if m in byid)
                    or not cls_of.get(eval(k))]
            if not pend: new.add(lid)
        if not new: break
        can |= new
    nex = sum(v["status"] == "excluded" for v in T["lattices"])
    print("lemmas accepted: %s%s; certificates %s" % (sorted(accepted) or "none", " (+ assumed for this dry run: %s)" % sorted(assume) if assume else "",
                                                     "NOT required (dry run)" if nocert else "required"))
    for lid in sorted(S, reverse=True):
        o = S[lid]
        if lid in can: st = "EXCLUDABLE"
        else:
            b = list(block[lid])
            if not b:
                pend = sorted({m for k in o.get("twin_all", []) for m in cls_of.get(eval(k), set()) if m in byid and byid[m]["status"] != "excluded" and m not in can})
                b.append("twin classes of lattices not yet excludable: %s" % pend)
            st = "blocked: " + "; ".join(b)
        print("  %s  %s" % (lid, st))
    print("tracker now: %d excluded of %d; with the excludable ones: %d" % (nex, len(T["lattices"]), nex + len(can)))
    if write and can:
        import shutil, time
        shutil.copy(trk, os.path.join(LAB, "logs", "finishC_tracker_before_convert_%s.json" % time.strftime("%m%d_%H%M")))
        for lid in sorted(can):
            o = S[lid]; v = byid[lid]; v["status"] = "excluded"; v.setdefault("reviewed_by", []).append("C2"); v.pop("status_note", None)
            v["by"] = (v.get("by", "") + " | 10/2026 C2 deferral sweep (engine v10): %d pairs; every pair EXCLUDED at once or by search, swap-covered, "
                       "twin-deferred to envelopes excluded since, or DEFERRED and then excluded by the lemmas %s (%d pairs pending T18: %s; %d pending T20: %s) "
                       "through the bridge, each with an exact certificate (norms 7, orthogonality, witness root)." % (
                           o["pairs"], sorted(accepted), o.get("defer_T18", 0), accepted.get("T18", {}).get("reference"), o.get("defer_T20", 0),
                           accepted.get("T20", {}).get("reference")))
            if o.get("y1_cert"):
                v["by"] += (" %d y1 representatives (%s) carry no pair record: U has a root r with (r,y1) = +-2, so E(r) = 10 - (r,y2)^2 for every y2 and "
                            "T18 or T20 applies (fixed-y1 lemma; certificate %s, sha256 %s, checked by q/check_cert_y1.py)." % (
                                len(o["y1_cert"]["reps"]), o["y1_cert"]["reps"], o["y1_cert"]["file"], o["y1_cert"]["sha256"][:16]))
        json.dump(T, open(trk, "w"), indent=1); print("tracker written: %s" % sorted(can))


if __name__ == "__main__":
    main()
