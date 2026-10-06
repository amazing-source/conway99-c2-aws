# t18_B2 / e331_compare.py -- compares the 39-vertex configurations (Y1) of e331.py with the survivors saved by the
# round-2 program r2_hfirst.py (read-only from ../t18).  Graphs are compared as labelled graphs on the common numbering
# (support 0..17, p 18, X_2 19..36, z0 37, sigma z0 38), up to the exchange of the names z0 <-> sigma z0.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
s = int(sys.argv[1])
mine = json.load(open(os.path.join(HERE, f"e331_{s}_0of1.json")))
theirs = json.load(open(os.path.join(HERE, "..", "t18", sys.argv[2])))
reps = json.load(open(os.path.join(HERE, f"r2_tau_{s}.json")))["reps"]
def swap(rows):
    def sw(x):
        b37, b38 = (x >> 37) & 1, (x >> 38) & 1
        return (x & ~((1 << 37) | (1 << 38))) | (b37 << 38) | (b38 << 37)
    r = [sw(x) for x in rows]
    r[37], r[38] = r[38], r[37]
    return tuple(r)
def canon(rows):
    rows = tuple(rows[:39])
    return min(rows, swap(rows))
A = set(canon(e["rows"]) for e in mine["Y1"])
B = set(canon(e["rows"]) for e in theirs["survivors"])
print(f"B{s}, profile (3,3,1), 39-vertex configurations: e331.py {len(mine['Y1'])} ({len(A)} distinct up to z0 <-> sigma z0), "
      f"r2_hfirst.py {len(theirs['survivors'])} ({len(B)} distinct); identical sets: {A == B}; "
      f"only e331 {len(A - B)}, only r2_hfirst {len(B - A)}")
print("   matchings: e331", sorted(set(e["tau"] for e in mine["Y1"])), " r2_hfirst",
      sorted(set(reps.index(e["tau"]) if isinstance(e["tau"], list) else e["tau"] for e in theirs["survivors"])))
print("   e331 totals:", mine["totals"])
print("   r2_hfirst totals:", theirs["totals"])
