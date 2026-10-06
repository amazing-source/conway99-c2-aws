# Builds b0_stageC.py from r3_p250.py by textual edits (so that the stage-C code is the round-3 code, unchanged):
#  - the triples (tau, F, H) are read from b0_stageB_reps.json (orbit representatives of stage B) instead of being searched;
#  - one line is appended to a .jsonl log for every triple completed (resumable; a triple cut by the time limit is not logged).
src = open("r3_p250.py").read()
def rep(a, b, cnt=1):
    global src
    assert src.count(a) == cnt, (a, src.count(a))
    src = src.replace(a, b)
rep('si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])',
    'si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])\nREPFILE = os.environ.get("B0_REPS", "b0_stageB_reps.json")\nRUNTAG = os.environ.get("B0_RUNTAG", "run")')
rep('def process(ti, tau):', 'def process(ti, tau, GROUPS):')
rep('    for Forb in itertools.combinations(elig, 2):\n        if time.time() - t0 > tlimit:\n            return None\n',
    '    for Forb in sorted(GROUPS):\n        Forb = tuple(Forb)\n        assert all(o in elig for o in Forb)\n        if time.time() - t0 > tlimit:\n            return None\n')
rep('        if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):\n            continue\n',
    '        assert not any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a])\n')
rep('        if any(x > 2 for x in f):\n            continue\n', '        assert not any(x > 2 for x in f)\n')
rep('        if not type_sols:\n            continue\n', '        assert type_sols\n')
rep('        if not graph_ok(rows0, L0):\n            continue\n', '        assert graph_ok(rows0, L0)\n')
# replace the stage-B search by the given H
a = '        rec(0, rows0, L0, 0)\n        TOT["H_complete"] += len(Hs)\n'
b = ('        for (idx, Hrep) in GROUPS[Forb]:\n'
     '            rws = rows0[:]\n'
     '            for k in range(18):\n'
     '                for l in range(18):\n'
     '                    if (Hrep[k] >> l) & 1:\n'
     '                        add(rws, X2(k), X2(l))\n'
     '            assert all(((rws[X2(k)] >> 19) & ((1 << 18) - 1)) == Hrep[k] for k in range(18)), "H does not contain the mate edges of F"\n'
     '            assert graph_ok(rws, list(range(37))), "stage-B triple fails the 37-vertex test"\n'
     '            Hs.append((idx, rws))\n'
     '        TOT["H_complete"] += len(Hs)\n')
rep(a, b)
rep('        for rows in Hs:\n            degs', '        for (idx, rows) in Hs:\n            if time.time() - t0 > tlimit:\n                return None\n            TOT_before = dict(TOT); nsurv_before = len(SURV)\n            degs')
rep('            if t > 9 or fl > 8 or D + MINY2[t] > 36:\n                continue\n',
    '            assert not (t > 9 or fl > 8 or D + MINY2[t] > 36)\n')
a = '            if Hgot:\n                TOT["H_with_C_survivor"] += 1\n                found_any = True\n'
b = a + ('            if time.time() - t0 > tlimit:\n                del SURV[nsurv_before:]\n                return None\n'
         '            DONE.write(json.dumps({"idx": idx, "tau": ti, "F": list(Forb), "t": t, "survivors": SURV[nsurv_before:],\n'
         '                                   "delta": {k_: TOT[k_] - TOT_before[k_] for k_ in TOT if TOT[k_] != TOT_before[k_]}}, separators=(",", ":")) + chr(10))\n'
         '            DONE.flush()\n')
rep(a, b)
# main loop
i0 = src.index('my = [(q, r) for q, r in enumerate(reps) if q % nparts == part]')
main = r'''
ALLREPS = json.load(open(os.path.join(here, REPFILE)))
done = set()
for fn in os.listdir(here):
    if fn.startswith("b0_stageC_done_") and fn.endswith(".jsonl"):
        for line in open(os.path.join(here, fn)):
            line = line.strip()
            if line:
                done.add(json.loads(line)["idx"])
todo = [(idx, e) for idx, e in enumerate(ALLREPS) if idx not in done]
if os.environ.get("B0_ONLY_T"):
    todo = [(idx, e) for idx, e in todo if sum(bin(h).count("1") for h in e["H"]) // 2 == int(os.environ["B0_ONLY_T"])]
mine = [(idx, e) for (idx, e) in todo if idx % nparts == part]
TAG = f"{si}_{RUNTAG}_{part}of{nparts}"
LOG.tag = TAG
DONE = open(os.path.join(here, f"b0_stageC_done_{RUNTAG}_{part}of{nparts}.jsonl"), "a")
bytau = {}
for idx, e in mine:
    bytau.setdefault(e["tau"], {}).setdefault(tuple(e["F"]), []).append((idx, e["H"]))
TOT["tau"] = len(bytau)
timed_out = False
print(f"stage C on orbit representatives: {len(ALLREPS)} in file, {len(done)} already done, {len(mine)} for this process", flush=True)
for ti in sorted(bytau):
    r = process(ti, reps[ti], bytau[ti])
    if r is None:
        timed_out = True
        break
    TOT["tau_done"] += 1
    print(f"  [{time.time() - t0:.0f}s] tau #{ti} done; C_survivors so far {TOT['C_survivors']}; C_nodes {TOT['C_nodes']}", flush=True)
LOG.close(); DONE.close()
print(f"{name} profile (2,5,0) stage C on representatives, part {part}/{nparts}, tag {RUNTAG}: time {time.time() - t0:.1f}s timed_out={timed_out}")
print("  totals (include the work on a triple cut by the time limit):", TOT)
print("  PSD certificates written:", LOG.n, " survivors:", len(SURV))
'''
src = src[:i0] + main.lstrip("\n")
src = src.replace('# Round 3.  Profile (2,5,0)', '# B0 copy of r3_p250.py, generated by _make_stageC.py: stage C only, on given triples.\n# Round 3.  Profile (2,5,0)', 1)
open("b0_stageC.py", "w").write(src)
print("written", len(src))
