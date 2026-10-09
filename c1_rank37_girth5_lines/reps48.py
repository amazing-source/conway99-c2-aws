"""One ball per isomorphism class for the profile (4,8) without type-I 4-cycle.
The balls of sweep48.py are (s, b): small type s in REPS (one per orbit of the six orders of the layers on the 7 small
types), large type b among the 81 959 ordered types.  Re-reading the layers of the whole ball in another order sends
(s, b) to (g.s, g.b); so for a fixed s the large types only matter up to the stabiliser of s.  "No star" is a property
of the isomorphism class of the ball, whatever the test vertex.
Needs: types_m2.txt, types_m4_p0.txt, actc.exe (gcc -O2 -o actc.exe actc.c).
Writes act22_c.txt, act48.txt (six images per type) and reps48.txt (lines: s b orbit-size).
Checks: every image is in the list, the six maps form a group action, orbit sizes add up."""
import itertools, subprocess, hashlib
from collections import Counter
from sweep48 import REPS

perms = list(itertools.permutations(range(3)))
comp = lambda s, t: perms.index(tuple(perms[s][perms[t][j]] for j in range(3)))
load = lambda p: [list(map(int, l.split())) for l in open(p) if l.strip()]

if __name__ == "__main__":
    for m, src, dst in ((2, "types_m2.txt", "act22_c.txt"), (4, "types_m4_p0.txt", "act48.txt")):
        res = subprocess.run(["./actc.exe", str(m), src, dst], capture_output=True, text=True).stdout.strip()
        print(res); assert res.endswith("not found in the list 0")
        act = load(dst)
        assert all(r[0] == i for i, r in enumerate(act))
        assert all(act[act[b][s]][t] == act[b][comp(s, t)] for b in range(len(act)) for s in range(6) for t in range(6))
    small_all = load("types_m2.txt"); p0 = [i for i, v in enumerate(small_all) if v[12] == 0]
    a2 = load("act22_c.txt"); a4 = load("act48.txt"); out = []
    for s in REPS:
        stab = [g for g in range(6) if a2[p0[s]][g] == p0[s]]
        reps = [b for b in range(len(a4)) if b == min(a4[b][g] for g in stab)]
        sizes = Counter(len({a4[b][g] for g in stab}) for b in reps)
        assert sum(k * v for k, v in sizes.items()) == len(a4)
        print(f"small type {s}: stabiliser of order {len(stab)}, large types up to it {len(reps)}, orbit sizes {dict(sorted(sizes.items()))}")
        out += [(s, b, len({a4[b][g] for g in stab})) for b in reps]
    open("reps48.txt", "w", newline="\n").write("".join(f"{s} {b} {k}\n" for s, b, k in out))
    print("balls up to isomorphism:", len(out), "instead of", len(REPS) * len(a4))
    for p in ("act48.txt", "reps48.txt"):
        print(p, "sha256", hashlib.sha256(open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:16])
