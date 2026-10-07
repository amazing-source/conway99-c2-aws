# T20 round 3: puts together the outputs of "stage1c.py ... <prefix>.part<i>of<n>.json part=i/n", i = 0..n-1.
# Checks that all parts saw the same enumeration (same numbers of N-configurations and of orbits) and that every
# part is present; the bases are written in the order of the ranks of their representatives.
# usage: python stage1_merge.py <prefix> <nparts> <outfile.json>
import sys, json
prefix, n, outfile = sys.argv[1], int(sys.argv[2]), sys.argv[3]
parts = [json.load(open("%s.part%dof%d.json" % (prefix, i, n))) for i in range(n)]
p0 = parts[0]
for i, p in enumerate(parts):
    assert p["part"] == i and p["nparts"] == n
    for k in ("graph", "profile", "ztype", "group_order", "rects", "nconfigs_labelled", "nconfig_orbits", "enum_nodes"):
        assert p[k] == p0[k], (k, i)
items = []
for p in parts:
    assert len(p["bases"]) == len(p["bases_rank"])
    assert all(r % n == p["part"] for r in p["bases_rank"])
    items += list(zip(p["bases_rank"], range(len(p["bases"])), p["bases"]))
items.sort(key=lambda t: (t[0], t[1]))
st = {}
for p in parts:
    for k, v in p["stats"].items():
        st[k] = st.get(k, 0) + v
out = {k: p0[k] for k in ("graph", "profile", "ztype", "group_order", "rects", "nconfigs_labelled", "nconfig_orbits",
                          "enum_nodes")}
out.update({"part": 0, "nparts": 1, "merged_from": n, "bases_rank": [t[0] for t in items],
            "tested": sum(p["tested"] for p in parts), "rejected_budget": sum(p["rejected_budget"] for p in parts),
            "rejected_psd_exact": sum(p["rejected_psd_exact"] for p in parts), "kept": sum(p["kept"] for p in parts),
            "n35": [sum(p["n35"][j] for p in parts) for j in range(3)], "stats": st,
            "rejected_hand_a2z": sum(p.get("rejected_hand_a2z", 0) for p in parts),
            "n35_with_choice": sum(p.get("n35_with_choice", 0) for p in parts),
            "kept_by_beta": {k: sum(p.get("kept_by_beta", {}).get(k, 0) for p in parts)
                             for k in sorted(set(k2 for p in parts for k2 in p.get("kept_by_beta", {})))},
            "seconds": sum(p["seconds"] for p in parts), "bases": [t[2] for t in items]})
assert out["kept"] == len(out["bases"])
assert out["n35"][0] == p0["nconfig_orbits"], "the parts do not tile the list of representatives"
json.dump(out, open(outfile, "w"), separators=(",", ":"))
print("%s profile %s%s: |G| = %d; rectangles %d; N-configurations %d, orbits under G %d   [merged from %d parts]" % (
    out["graph"], tuple(out["profile"]), (" z = %s" % (out["ztype"],)) if out["ztype"] else "", out["group_order"],
    out["rects"], out["nconfigs_labelled"], out["nconfig_orbits"], n))
print("   bases tested %d: rejected by budgets %d, by PSD (exact) %d, kept %d   stats %s" % (
    out["tested"], out["rejected_budget"], out["rejected_psd_exact"], out["kept"], st))
if out["ztype"]:
    print("   representatives %d; with at least one choice of N(z) n N(p) passing the counts and the hand filter: %d, "
          "of which rejected by PSD (exact) on the 35 vertices: %d; choices rejected by the hand filter a_2(z) <= 1: "
          "%d; kept bases by beta: %s" % (
              out["n35"][0], out["n35_with_choice"], out["n35"][2], out["rejected_hand_a2z"], out["kept_by_beta"]))
