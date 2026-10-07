"""The table of the 156 lattices for the proof document (C2 lab, 2026-10-07). GENERATED: reads the tracker and the checked reports,
asserts their consistency, writes a markdown table and a json. It recomputes nothing and paraphrases nothing: the numbers are those
of the reports, the method is the group below, and the tracker's own text for each lattice is reproduced verbatim in an appendix.

  .venv/Scripts/python.exe scripts/cloud/lattice_table.py <out.md> <out.json>

Inputs (lab PC, data/finishC): finishC_tracker.json; sweep/STREAM_RECOUNT, SWEEP_LAB, CERT_CENSUS, AUDIT_COVERAGE,
SHELL_COUNTS_EXACT, RECONCILE_RECORDS (all *_2026-10-07.json); sweep/certs/cert_golay_00{1,2}.json; lemmas_accepted.json.
Assertions (the script fails rather than print a table that disagrees with a report): 156 lattices, all excluded; the method groups
partition 0..155; every lattice of a stream group has a report without problem; for the deferral lattices every record with deferred
pairs has a good certificate and the certified pairs equal the deferred ones; the 25 lattices of the rigid-kernel audit are covered
with no exposed pair left; the shell check is ok for all 156."""
import sys, os, json, hashlib, time, collections
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); FC = os.path.join(LAB, "data", "finishC"); SW = os.path.join(FC, "sweep")


def ids(s):
    out = []
    for t in s.replace(",", " ").split():
        if "-" in t: a, b = t.split("-"); out += list(range(int(a), int(b) + 1))
        else: out.append(int(t))
    return out


GROUPS = [   # code, short name, lattices
    ("SD", "stream sweep, engine v10, with pairs resting on T18 / T20 (certified)", ids("3 5-9 11-15")),
    ("GD", "Golay pair files, with pairs resting on T18 / T20 (certified)", ids("1 2")),
    ("G", "Golay pair blocks", ids("4 10")),
    ("O", "lattice 000: 141 pair classes (86 LP certificates, 55 searched)", ids("0")),
    ("H", "h-stage sweep on pair lists, lab PC, 28-29/09", ids("44 72 96 97 105 106 108 116 119 120 121 127 130")),
    ("F", "frame_dfs with Lemma U+ on the Gamma-reduced pairs, lab PC, 27/09", ids("87 111 122-126 131 135 137-141")),
    ("H3", "three h-stage readings on C1's pairs", ids("115 132")),
    ("P", "packing argument (C1)", ids("94 128 129 133 136 144 147 148 150 154")),
    ("EP", "criterion (E) and packing", ids("117 134 142")),
    ("SP", "Sol 0836 and packing", ids("145 146 151 152 155")),
    ("So", "Sol 0836, and Theorem R A.9 (U indecomposable)", ids("153")),
    ("B", "budget identity, hand proof (LATTICE_143.md)", ids("143")),
]
F4 = {"140": "run/q-i-02aa613ee361fbc10", "135": "run/q-i-02aa613ee361fbc10", "141": "run/q-i-02aa613ee361fbc10", "064": "run/q-i-011dce74cd612fc52"}
AT_RISK_NOT_ENGINE = {"117", "152"}


def load(name): return json.load(open(os.path.join(SW, name + "_2026-10-07.json")))
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def n(x): return "{:,}".format(x)


def main():
    outmd, outjs = sys.argv[1], sys.argv[2]
    T = json.load(open(os.path.join(FC, "finishC_tracker.json")))["lattices"]; byid = {"%03d" % v["id"]: v for v in T}
    assert len(T) == 156 and sorted(byid) == ["%03d" % i for i in range(156)] and all(v["status"] == "excluded" for v in T)
    ASE = load("STREAM_RECOUNT"); SWL = load("SWEEP_LAB")["lattices"]; CC = load("CERT_CENSUS"); AC = load("AUDIT_COVERAGE")
    SH = load("SHELL_COUNTS_EXACT"); RR = load("RECONCILE_RECORDS"); LA = json.load(open(os.path.join(FC, "lemmas_accepted.json")))
    GC = {l: json.load(open(os.path.join(SW, "certs", "cert_golay_%s.json" % l))) for l in ("001", "002")}
    grp = {}
    for code, name, L in GROUPS:
        for i in L: assert "%03d" % i not in grp, i; grp["%03d" % i] = code
    stream = [l for l in byid if l not in grp]; assert len(stream) == 91 and sorted(stream) == sorted(ASE), "stream group differs from the stream report"
    for l in stream: grp[l] = "S"
    assert sorted(grp) == sorted(byid) and all(SH[l]["ok"] and SH[l]["N3"] == 4096 for l in byid) and sorted(LA) == ["T18", "T20"]
    assert CC["records"] == CC["good"] and not CC["missing"] and not CC["not_good"] and not CC["disagree"]
    assert all(v["covered"] and v["exposed_not_excluded_again"] == 0 for v in AC.values()) and len(AC) == 25
    rcl = {l: c for c, L in RR["classes"].items() for l in L}; rows = []; tot = collections.Counter()
    for l in sorted(byid):
        v = byid[l]; g = grp[l]; r = {"id": l, "roots": v["roots"], "nb": "%s, %s" % (v["nb1"], v["nb2"]), "N2": SH[l]["N2"], "method": g,
                                      "pairs": None, "search": None, "T18": None, "T20": None, "cert": "", "h2": "", "rec": "", "eng": "", "by": v.get("by", ""),
                                      "reviewed_by": v.get("reviewed_by", [])}
        if g == "S":
            a = ASE[l]; assert a["ok"] and a["covered"] == a["y1_reps"] and not a["covered_twice"] and a["defer_T18"] == 0 and a["defer_T20"] == 0, l
            t = a["by_tier"]; r.update(pairs=a["pairs"], search=a["excl_search"])
            r["eng"] = "package" if t["P"] == a["y1_reps"] else "; ".join(x for x in ("package %d" % t["P"] if t["P"] else "", "lab version %d" % t["L"] if t["L"] else "",
                                                                                     "no version %d" % t["N"] if t["N"] else "") if x) + " of %d y1" % a["y1_reps"]
        elif g == "SD":
            o = SWL[l]; assert o["kind"] == "stream" and not o["not_covered"] and not o["incomplete"], l
            c = CC["per_lattice"].get(l, [0, 0, 0, 0, 0]); recs = len(o["deferral_records"])
            assert c[0] == c[1] == recs and c[2] == o["defer_T18"] and c[3] + c[4] == o["defer_T20"], (l, c, recs)
            r.update(pairs=o["pairs"], search=o["excl_search"], T18=o["defer_T18"], T20=o["defer_T20"], cert="%d of %d records" % (c[1], recs), eng="package")
            if o.get("y1_cert"): r["cert"] += "; y1 %s by Corollary Y1" % o["y1_cert"]["reps"]
        elif g == "GD":
            o = SWL[l]; c = GC[l]; assert o["kind"] == "golay" and not o["not_covered"] and not o["incomplete"], l
            assert c["ok"] is True and c["pairs_total"] == o["pairs"] and c["T18"]["certified"] == o["defer_T18"] and c["T20"]["certified"] == o["defer_T20"], l
            r.update(pairs=o["pairs"], T18=o["defer_T18"], T20=o["defer_T20"], cert="every deferred pair", eng="package")
        if l in AC:
            a = AC[l]; r["h2"] = "%s exposed, all excluded again" % n(a["counts"].get("exposed", 0))
            if a.get("by_certificate"): r["h2"] += "; y1 %s by Corollary Y1" % a["by_certificate"]
        elif l in AT_RISK_NOT_ENGINE: r["h2"] = "at risk, but no search used"
        r["rec"] = {"A": "machine branches", "B": "lab PC%s" % (" (part on machine branches)" if RR["lattices"].get(l, {}).get("reps_covered_by_records_in_compute_repo") else ""),
                    "C": "lab PC", "D": "no pair record"}.get(rcl.get(l), "machine branches" if g in ("SD", "GD") else "?")
        if l in F4: r["rec"] += "; enumeration compared (F4)"
        for k in ("pairs", "search", "T18", "T20"):
            if r[k] is not None: tot[k] += r[k]
        tot[g] += 1; rows.append(r)
    assert all(r["rec"] != "?" for r in rows)
    srcs = {x: sha(os.path.join(SW, x + "_2026-10-07.json")) for x in ("STREAM_RECOUNT", "SWEEP_LAB", "CERT_CENSUS", "AUDIT_COVERAGE", "SHELL_COUNTS_EXACT", "RECONCILE_RECORDS")}
    srcs["finishC_tracker.json"] = sha(os.path.join(FC, "finishC_tracker.json")); srcs["lemmas_accepted.json"] = sha(os.path.join(FC, "lemmas_accepted.json"))
    L = ["# The 156 lattices: what excludes each (generated table)", "",
         "Generated by `q/tools/lab_2026-10-07/lattice_table.py` on %s from the lab tracker and the checked reports; not edited by hand." % time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
         "Inputs (sha256, 16 hex): " + "; ".join("%s %s" % kv for kv in sorted(srcs.items())) + ".", "",
         "Method codes:", ""]
    L += ["- **S** (91 lattices): stream sweep: every pair (y_1, y_2) of the producer passed through the engine."] + ["- **%s** (%d): %s." % (c, len(x), nm) for c, nm, x in GROUPS]
    L += ["", "Columns: N2 = number of roots (exact shell check); pairs = pairs of the sweep's records; search = pairs excluded by a frame search (the others: "
          "excluded at once by a witness vector, swap-covered, or transferred to a twin lattice); T18, T20 = pairs excluded through the bridge by these lemmas, "
          "each with an exact certificate; engine = code version of the records that cover the y_1 representatives: \"package\" = an engine archived in a package of the "
          "campaign, \"lab version\" = a lab-PC version of 28-29/09 of the stream wrapper (same core frame_dfs.py as package v1) that is not archived, \"no version\" = "
          "records without recorded code version; H2 = rigid-kernel audit (only the 27 lattices where the hole can occur); records = where the pair records are. "
          "An empty cell means: not applicable, or no checked report gives the number (then see the tracker text in the appendix).", "",
          "| id | roots | neighbours | N2 | method | pairs | search | T18 | T20 | certificates | engine | H2 audit | records |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x: "" if x is None else n(x)
    for r in rows:
        L.append("| %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (r["id"], r["roots"].replace("|", "/"), r["nb"], r["N2"], r["method"], f(r["pairs"]), f(r["search"]),
                                                                                     f(r["T18"]), f(r["T20"]), r["cert"], r["eng"], r["h2"], r["rec"]))
    L += ["", "Totals over the rows that have the number: pairs %s; excluded by search %s; through T18 %s; through T20 %s. Lattices per method: %s." % (
        n(tot["pairs"]), n(tot["search"]), n(tot["T18"]), n(tot["T20"]), ", ".join("%s %d" % (c, tot[c]) for c in ["S"] + [g[0] for g in GROUPS])), "",
          "## Appendix: the tracker's text for each lattice, verbatim", "",
          "Field `by` of `finishC_tracker.json` (history of the entry, oldest first, parts separated by ` | `; a leading `open` is the entry's first state), then `reviewed_by`.", ""]
    for r in rows: L += ["**%s** (%s). %s  \nReread by: %s." % (r["id"], r["roots"], r["by"], ", ".join(r["reviewed_by"]) or "nobody recorded"), ""]
    open(outmd, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    json.dump({"inputs": srcs, "rows": rows, "totals": dict(tot)}, open(outjs, "w"), indent=1)
    print("rows %d; per method %s; pairs %s, search %s, T18 %s, T20 %s" % (len(rows), {c: tot[c] for c in ["S"] + [g[0] for g in GROUPS]}, n(tot["pairs"]), n(tot["search"]), n(tot["T18"]), n(tot["T20"])))


if __name__ == "__main__":
    main()
