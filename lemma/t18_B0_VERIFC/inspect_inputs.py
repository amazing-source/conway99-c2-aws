# t18_B0_VERIFC / inspect_inputs.py -- read-only look at the stage-B json files (no search, no test of the proof).
# For every file: top-level keys with a short description, and counts of the triple list c_mine.py would read
# (field "H_stageB", else "H"), exactly as c_mine.py reads it: (tau, sorted F, H) tuples.
# usage: python inspect_inputs.py <json files ...>
import json, sys, os


def short(v):
    if isinstance(v, list):
        if v and all(isinstance(x, int) for x in v):
            return f"list[{len(v)}] of int, min {min(v)}, max {max(v)}, first {v[:8]}"
        return f"list[{len(v)}]" + (f", first item type {type(v[0]).__name__}" if v else "")
    if isinstance(v, dict):
        s = json.dumps(v)
        return f"dict[{len(v)}] " + (s if len(s) < 700 else s[:700] + " ...")
    s = json.dumps(v)
    return s if len(s) < 300 else s[:300] + " ..."


for fn in sys.argv[1:]:
    d = json.load(open(fn))
    print("=" * 100)
    print(os.path.basename(fn))
    for k, v in d.items():
        print(f"   {k}: {short(v)}")
    field = "H_stageB" if "H_stageB" in d else ("H" if "H" in d else None)
    print(f"   -> field c_mine.py reads: {field}")
    if field is None:
        continue
    L = d[field]
    if L:
        print(f"   -> keys of one entry: {sorted(L[0].keys())}; len(H) of first entry: {len(L[0]['H'])}")
    items = [(e["tau"], tuple(sorted(e["F"])), tuple(e["H"])) for e in L]
    taus = sorted(set(t for t, _, _ in items))
    print(f"   -> entries {len(items)}, distinct triples {len(set(items))}, distinct (tau,F) {len(set((t, F) for t, F, _ in items))}, "
          f"distinct matchings {len(taus)}" + (f", tau range {taus[0]}..{taus[-1]}" if taus else ""))
    print(f"   -> survivors field: {len(d['survivors']) if 'survivors' in d else 'absent'}")
