"""Merge of the part files of q/ypairs_c2.py run with YP_PART="k/N" (C2 lab, 2026-10-07; fallback of F4 without fork).

  python ypairs_merge.py <out.json> <part file 0> ... <part file N-1>

Checks: N files with part = [k, N], k = 0 .. N-1 once each; same source, basis, n_admissible_lines, n_y1_orbits and norm7_lines in
all; the y1 indices of file k are exactly k, k + N, ... below n_y1_orbits; the pair counts per y1 add up to the pairs of the file.
Output: the same file as the sequential ypairs_c2.py (pairs in the order of the y1 index). Exit 1 on any failed check."""
import sys, json
out = sys.argv[1]; P = [json.load(open(f)) for f in sys.argv[2:]]; N = len(P)
ok = sorted(p["part"] for p in P) == [[k, N] for k in range(N)]
P.sort(key=lambda p: p["part"][0]); h = P[0]
for k, p in enumerate(P):
    ok &= all(p[x] == h[x] for x in ("source", "basis", "n_admissible_lines", "n_y1_orbits", "norm7_lines"))
    ok &= [t for t, _ in p["y1_counts"]] == list(range(k, h["n_y1_orbits"], N)) and sum(c for _, c in p["y1_counts"]) == len(p["pairs"])
if not ok: print("MERGE FAILED: parts inconsistent"); sys.exit(1)
by = {}
for p in P:
    i = 0
    for t, c in p["y1_counts"]: by[t] = p["pairs"][i:i + c]; i += c
assert sorted(by) == list(range(h["n_y1_orbits"]))
pairs = [q for t in range(h["n_y1_orbits"]) for q in by[t]]
json.dump({"source": h["source"], "basis": h["basis"], "coords": "coefficients in 'basis'", "n_admissible_lines": h["n_admissible_lines"],
           "n_y1_orbits": h["n_y1_orbits"], "pairs": pairs, "merged_parts": N}, open(out, "w"))
print("norm-7 lines %d, admissible %d; merged %d parts: y1 orbits %d, pairs %d" % (h["norm7_lines"], h["n_admissible_lines"], N, h["n_y1_orbits"], len(pairs)))
