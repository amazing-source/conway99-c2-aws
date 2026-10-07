# Independent re-check of saved PSD certificates (pure Python integers; no numpy; no import of the engines).
# A record: {"block": "M1odd"|"M2odd"|"M1even"|"M2even", "c": block vector, "q": claimed value, "sig": involution,
#            "A": adjacency rows as 0/1 strings}.
# Checks: A symmetric 0/1 with zero diagonal; sig an involutive automorphism of A; the first 21 vertices carry the
# support graph S u {p} of the named structure; the lifted integer vector x satisfies x^T M x < 0 with
# M = M1 = 9(3I-A)+J or M2 = 11(4I+A)-2J, and x^T M x = 18 q (M1odd), 22 q (M2odd), q (even blocks).
# usage: python check_certs.py <structure name, e.g. III.0> file1.jsonl [file2 ...]
import sys, json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def support(name):
    d = {}
    for fn in ("structures_I.json", "structures_III_IIb_IIa.json"):
        d.update(json.load(open(os.path.join(HERE, fn))))
    case, idx = name.split(".")
    rec = d[case][int(idx)]
    m, H = rec["m"], rec["H"]
    E = set()
    for i in range(10):
        for j in range(i + 1, 10):
            if m[i][j] & 1:
                E.add((i, 10 + j)); E.add((j, 10 + i))
            if m[i][j] & 2:
                E.add((i, j)); E.add((10 + i, 10 + j))
    for i in H:
        E.add((i, 10 + i)); E.add((20, i)); E.add((20, 10 + i))
    return {tuple(sorted(e)) for e in E}


name = sys.argv[1]
SUP = support(name)
tot = bad = 0
sizes = {}
blocks = {}
for fn in sys.argv[2:]:
    for line in open(fn):
        rec = json.loads(line)
        tot += 1
        A = [[int(ch) for ch in row] for row in rec["A"]]
        n = len(A)
        sig = rec["sig"]
        ok = all(len(r) == n for r in A)
        ok = ok and all(A[i][i] == 0 for i in range(n))
        ok = ok and all(A[i][j] == A[j][i] and A[i][j] in (0, 1) for i in range(n) for j in range(n))
        ok = ok and all(sig[sig[v]] == v for v in range(n))
        ok = ok and all(A[i][j] == A[sig[i]][sig[j]] for i in range(n) for j in range(n))
        ok = ok and all((A[i][j] == 1) == ((i, j) in SUP) for i in range(21) for j in range(i + 1, 21))
        ok = ok and all(sig[i] == 10 + i for i in range(10)) and sig[20] == 20
        reps = [v for v in range(n) if sig[v] > v]
        fixed = [v for v in range(n) if sig[v] == v]
        c = [int(t) for t in rec["c"]]
        x = [0] * n
        blk = rec["block"]
        if blk.endswith("odd"):
            ok = ok and len(c) == len(reps)
            for j, v in enumerate(reps):
                x[v] = c[j]; x[sig[v]] = -c[j]
        else:
            ok = ok and len(c) == len(fixed) + len(reps)
            for j, v in enumerate(fixed):
                x[v] = c[j]
            for j, v in enumerate(reps):
                x[v] = c[len(fixed) + j]; x[sig[v]] = c[len(fixed) + j]
        sx = sum(x)
        xx = sum(t * t for t in x)
        xAx = 0
        for i in range(n):
            if x[i]:
                Ai = A[i]
                xAx += x[i] * sum(Ai[j] * x[j] for j in range(n))
        if blk.startswith("M1"):
            val = 9 * (3 * xx - xAx) + sx * sx
            fac = 18 if blk.endswith("odd") else 1
        else:
            val = 11 * (4 * xx + xAx) - 2 * sx * sx
            fac = 22 if blk.endswith("odd") else 1
        ok = ok and val < 0 and val == fac * int(rec["q"])
        if not ok:
            bad += 1
        sizes[n] = sizes.get(n, 0) + 1
        blocks[blk] = blocks.get(blk, 0) + 1
print("structure %s: %d certificates checked, %d invalid" % (name, tot, bad))
print("  by number of vertices:", dict(sorted(sizes.items())))
print("  by block:", dict(sorted(blocks.items())))
