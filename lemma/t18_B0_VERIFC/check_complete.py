# t18_B0_VERIFC / check_complete.py -- BOOKKEEPING ONLY (no search, no test of the proof): completeness of a set of c_mine.py runs.
# It rebuilds, from the same input files, the list c_mine.py works on (sorted set of (tau, sorted F, H), read from the field
# "H_stageB", else "H"; restricted to C_TAUS-style matchings if <taus> is given) and then, for every c_mine_<s>_<p>of<n><tag>.json
# found in <run dir>:
#   - a part with timed_out == True is listed and NOT counted;
#   - a counted part must have: s, part, nparts equal to its file name; totals.triples == length of the list;
#     "done" == the (tau, F) of the list items number q with q % n == p, in the same order and the same number
#     (so the part processed exactly the triples of index q = p mod n, each to the end);
#     len(survivors) == totals.survivors; its .out file ends with "done <that number>, timed_out False"; its .err file is empty.
# Then: the index sets of the counted parts must be pairwise disjoint and their union must be 0..N-1 (every triple once, none twice).
# usage: python check_complete.py <run dir> <s> <expected number of triples> <expected number of matchings> <taus: - | a,b> <input json ...>
import json, sys, os, re, glob

rd = os.path.abspath(sys.argv[1]); s = int(sys.argv[2]); EXP = int(sys.argv[3]); EXPM = int(sys.argv[4])
taus = None if sys.argv[5] == "-" else set(int(x) for x in sys.argv[5].split(","))
tag = "" if taus is None else "_t" + sys.argv[5].split(",")[0]
files = sys.argv[6:]
items = []
for fn in files:
    d = json.load(open(fn))
    fld = "H_stageB" if "H_stageB" in d else "H"
    print(f"input {os.path.basename(fn)}: timed_out {d['timed_out']}, field {fld}, {len(d[fld])} entries")
    for e in d[fld]:
        items.append((e["tau"], tuple(sorted(e["F"])), tuple(e["H"])))
raw = len(items)
items = sorted(set(items))
if taus is not None:
    items = [it for it in items if it[0] in taus]
N = len(items)
nm = len(set(it[0] for it in items))
print(f"triples read {raw}, distinct{'' if taus is None else ' and in matchings ' + sys.argv[5]} {N}, in {nm} matchings, "
      f"{len(set((t, F) for t, F, _ in items))} pairs (tau, F)")
problems = []
if N != EXP:
    problems.append(f"number of triples {N} differs from the expected {EXP}")
if nm != EXPM:
    problems.append(f"number of matchings {nm} differs from the expected {EXPM}")

pat = re.compile(rf"^c_mine_{s}_(\d+)of(\d+){re.escape(tag)}\.json$")
found = []
for fn in sorted(os.listdir(rd)):
    m = pat.match(fn)
    if m:
        found.append((int(m.group(2)), int(m.group(1)), fn))
found.sort()
cover = [[] for _ in range(N)]
tot_done = 0; tot_surv = 0; survivors = []; counters = {}; rows_out = []; not_counted = []
for n, p, fn in found:
    d = json.load(open(os.path.join(rd, fn)))
    base = os.path.join(rd, fn[:-5])
    outtxt = open(base + ".out").read() if os.path.exists(base + ".out") else ""
    errsize = os.path.getsize(base + ".err") if os.path.exists(base + ".err") else -1
    mo = re.search(r"c_mine B(\d+) part (\d+)/(\d+): (\d+) triples in this part, done (\d+), timed_out (\w+), (\d+)s", outtxt)
    if d["timed_out"]:
        not_counted.append(f"{fn}: timed_out True, done {len(d['done'])} (NOT counted)")
        continue
    idx = [q for q in range(N) if q % n == p]
    exp_done = [[items[q][0], list(items[q][1])] for q in idx]
    ok = True
    def need(c, msg):
        global ok
        if not c:
            ok = False
            problems.append(f"{fn}: {msg}")
    need(d["s"] == s and d["part"] == p and d["nparts"] == n, "s/part/nparts differ from the file name")
    need(d["totals"]["triples"] == N, f"totals.triples {d['totals']['triples']} != {N}")
    need(d["done"] == exp_done, f"'done' list differs from the expected triples of index = {p} mod {n} ({len(d['done'])} vs {len(exp_done)})")
    need(d["totals"]["triples_done"] == len(exp_done), "totals.triples_done differs")
    need(len(d["survivors"]) == d["totals"]["survivors"], "len(survivors) != totals.survivors")
    need(mo is not None, ".out file has no final line")
    if mo:
        need((int(mo.group(1)), int(mo.group(2)), int(mo.group(3))) == (s, p, n), ".out final line: other s/part/nparts")
        need(int(mo.group(4)) == len(exp_done) and int(mo.group(5)) == len(exp_done), ".out final line: counts differ")
        need(mo.group(6) == "False", ".out final line says timed_out True")
    need(errsize == 0, f".err file size {errsize}")
    if not ok:
        not_counted.append(f"{fn}: FAILED a check (NOT counted)")
        continue
    for q in idx:
        cover[q].append(fn)
    tot_done += len(d["done"]); tot_surv += len(d["survivors"])
    for e in d["survivors"]:
        survivors.append(e)
    for k, v in d["totals"].items():
        counters[k] = counters.get(k, 0) + v
    rows_out.append((n, p, len(exp_done), int(mo.group(7)), len(d["survivors"])))
print(f"part files found: {len(found)}; counted: {len(rows_out)}; not counted: {len(not_counted)}")
for x in not_counted:
    print("   ", x)
print("counted parts (part/nparts: triples processed, seconds reported by c_mine.py, survivors):")
for n, p, k, sec, sv in rows_out:
    print(f"   {p}/{n}: {k} triples, {sec}s, {sv} survivors")
never = [q for q in range(N) if len(cover[q]) == 0]
twice = [q for q in range(N) if len(cover[q]) > 1]
print(f"sum of processed triples over the counted parts: {tot_done}; list length {N}; "
      f"triples in no counted part: {len(never)}; triples in more than one counted part: {len(twice)}")
if never:
    print("    indices not processed (first 20):", never[:20], " parts needed (index mod n):",
          sorted(set((q % found[0][0]) for q in never)) if found else "")
if twice:
    print("    indices processed twice (first 20):", [(q, cover[q]) for q in twice[:20]])
complete = (not never) and (not twice) and tot_done == N and not problems
print(f"sum of the reported seconds over the counted parts: {sum(r[3] for r in rows_out)}")
drop = ("triples", "type_solutions", "type_solutions_ok33", "tauF_with_triples")
print("counters summed over the counted parts (the 'first time per (tau,F) in a process' counters type_solutions, "
      "type_solutions_ok33, tauF_with_triples and the constant 'triples' are left out, they are not additive over parts):")
print("   ", {k: v for k, v in counters.items() if k not in drop})
print(f"SURVIVORS on 47 vertices, counted parts: {tot_surv}")
dist = set(tuple(e["rows"][:47]) for e in survivors)
print(f"   distinct 47-vertex graphs among them: {len(dist)}; matchings: {sorted(set(e['tau'] for e in survivors))}")
for e in sorted(survivors, key=lambda e: (e["tau"], e["F"], e["types"])):
    print(f"   matching #{e['tau']}, F = {e['F']}, types {e['types']}")
for x in problems:
    print("PROBLEM:", x)
print(f"COMPLETE: {complete}  (expected {EXP} triples in {EXPM} matchings; processed {tot_done}, each exactly once: {not never and not twice})")
