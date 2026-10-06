# Referee check 4: stage B of profile (2,5,0) recounted from my own model (nothing of the repo is read or imported).
# Vertices: x_i = i, y_i = 9+i, p = 18, X_2 vertex of the deficient pair a = 19+a (N+ = DEF[a], N- = DEF[tau a], mate 19+tau a).
# What I proved by hand and use as FORCED adjacencies on S u {p} u X_2 (37 vertices):
#   S+ and S- independent, x_i ~ y_j iff B_ij; p has no neighbour in S; p ~ the 4 vertices of A_p (2 orbits F);
#   v ~ sigma v  iff v in A_p (x ~ sigma x iff x in N(p));  no edge between the two mate pairs of A_p (N(p) is a matching).
# Free: H = A[X_2], sigma-invariant.  Tests: common-neighbour budgets (count <= 2 - A_uv) on the whole partial graph
# (legitimate on a spanning subgraph), and float PSD of 9(3I-A)+J and 11(4I+A)-2J ONLY on sets whose adjacencies are all
# decided (S u {p} u the orbits already placed).  PSD here is floating point (threshold -1e-7): this is a count check, not a proof.
# Optional proven numerical conditions (A8/A14g) are evaluated on the leaves only and reported, not used for pruning.
import itertools, sys, time, json
import numpy as np

REP = {
 "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
 "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
 "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}
name = sys.argv[1]
part, nparts = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
TLIM = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
B = np.zeros((9, 9), dtype=np.int64)
for w in REP[name].split():
    i, j = int(w[0]), int(w[1]); B[i, j] = B[j, i] = 1
Bn = [set(np.nonzero(B[i])[0]) for i in range(9)]
DEF = [(a, b) for a in range(9) for b in range(a + 1, 9) if len(Bn[a] & Bn[b]) == 1]
n = 18

def r1(U, V):
    if len(set(U) & set(V)) > 1: return False
    if any(sum(B[i][j] for j in V) > 1 for i in U): return False
    if any(sum(B[i][j] for i in U) > 1 for j in V): return False
    return True
OK = [[a != b and r1(DEF[a], DEF[b]) for b in range(n)] for a in range(n)]
req = 2 - B
cover = np.zeros((9, 9), dtype=np.int64)
tau = [-1] * n
sols = []
def rec():
    a = -1
    for k in range(n - 1, -1, -1):
        if tau[k] == -1:
            a = k; break
    if a < 0:
        sols.append(tuple(tau)); return
    for b in range(a):
        if tau[b] == -1 and OK[a][b]:
            U, V = DEF[a], DEF[b]
            for i in U:
                for j in V:
                    cover[i, j] += 1; cover[j, i] += 1
            if (cover <= req).all():
                tau[a] = b; tau[b] = a
                rec()
                tau[a] = -1; tau[b] = -1
            for i in U:
                for j in V:
                    cover[i, j] -= 1; cover[j, i] -= 1
rec()
auts = [q for q in itertools.permutations(range(9)) if all(B[q[i], q[j]] == B[i, j] for i in range(9) for j in range(i + 1, 9))]
idx = {d: k for k, d in enumerate(DEF)}
gd = [[idx[tuple(sorted((q[a], q[b])))] for (a, b) in DEF] for q in auts]
seen = set(); reps = []
for s in sorted(sols):
    if s in seen: continue
    reps.append(s)
    for g in gd:
        img = [0] * n
        for a in range(n): img[g[a]] = g[s[a]]
        seen.add(tuple(img))
print(f"{name}: matchings {len(sols)}, orbits {len(reps)}", flush=True)

NV = 37
Iall = np.eye(NV)
def psd(A, idxs):
    sub = A[np.ix_(idxs, idxs)].astype(float); m = len(idxs)
    M1 = 9 * (3 * np.eye(m) - sub) + 1.0
    if np.linalg.eigvalsh(M1)[0] < -1e-7: return False
    M2 = 11 * (4 * np.eye(m) + sub) - 2.0
    return np.linalg.eigvalsh(M2)[0] > -1e-7
OFF = 1 - np.eye(NV, dtype=np.int64)
def budget_ok(A):
    C = A @ A
    return not ((C > 2 - A) & (OFF == 1)).any()

stats = dict(tauF_budget=0, tauF_psd=0, nodes=0, leaves=0, leaves_A14g=0)
triples = []
t0 = time.time()
timed_out = False
for ti, s in enumerate(reps):
    if ti % nparts != part: continue
    if time.time() - t0 > TLIM:
        timed_out = True; print("TIME LIMIT at matching index", ti, flush=True); break
    A0 = np.zeros((NV, NV), dtype=np.int64)
    A0[0:9, 9:18] = B; A0[9:18, 0:9] = B
    for a in range(n):
        for i in DEF[a]: A0[19 + a, i] = A0[i, 19 + a] = 1
        for j in DEF[s[a]]: A0[19 + a, 9 + j] = A0[9 + j, 19 + a] = 1
    orbs = [a for a in range(n) if a < s[a]]
    usable = [a for a in orbs if not (set(DEF[a]) & set(DEF[s[a]]))]
    for F in itertools.combinations(usable, 2):
        A = A0.copy()
        for a in F:
            for c in (a, s[a]):
                A[18, 19 + c] = A[19 + c, 18] = 1
            A[19 + a, 19 + s[a]] = A[19 + s[a], 19 + a] = 1
        base = list(range(19)) + [19 + c for a in F for c in (a, s[a])]
        # budgets on the 23 determined vertices (as in ref2) and on the whole partial graph
        sub = A[np.ix_(base, base)]
        Cs = sub @ sub
        if ((Cs > 2 - sub) & (np.eye(len(base), dtype=np.int64) == 0)).any(): continue
        stats["tauF_budget"] += 1
        if not psd(A, base): continue
        stats["tauF_psd"] += 1
        if not budget_ok(A): continue
        rest = [a for a in orbs if a not in F]
        Ap = [c for a in F for c in (a, s[a])]
        def place(k, placed, A):
            stats["nodes"] += 1
            if k == len(rest):
                stats["leaves"] += 1
                H = A[19:37, 19:37]
                a2 = H.sum(1); t = int(H.sum()) // 2
                e1 = int(sum(a2[c] - 1 for c in Ap))
                best = min(sum(y * y for y in ys) for ys in itertools.product(range(t + 1), repeat=4) if sum(ys) == t) if t <= 9 else 10**9
                g_ok = (a2.max() <= 4) and t <= 9 and e1 <= 8 and int((a2 * (a2 - 1)).sum()) + 2 * best <= 36
                stats["leaves_A14g"] += g_ok
                triples.append((ti, tuple(F), tuple(int(x) for x in np.packbits(H.astype(np.uint8)).tolist()), t, int(a2.max()), bool(g_ok)))
                return
            a = rest[k]; b = s[a]
            cands = placed[:]            # earlier X_2 deficient-pair indices (both vertices of each placed orbit)
            def choose2(i, A):
                if i == len(cands):
                    idxs = list(range(19)) + [19 + c for c in placed] + [19 + a, 19 + b]
                    if psd(A, idxs):
                        place(k + 1, placed + [a, b], A)
                    return
                u = cands[i]
                choose2(i + 1, A)
                A2 = A.copy()
                A2[19 + a, 19 + u] = A2[19 + u, 19 + a] = 1
                A2[19 + b, 19 + s[u]] = A2[19 + s[u], 19 + b] = 1
                if budget_ok(A2):
                    choose2(i + 1, A2)
            choose2(0, A)
        place(0, Ap[:], A)
el = time.time() - t0
print(f"{name} part {part}/{nparts}: {stats}  time {el:.0f}s  timed_out={timed_out}", flush=True)
from collections import Counter
print("   leaves by t:", dict(Counter(x[3] for x in triples)), " max a_2 on X_2:", dict(Counter(x[4] for x in triples)),
      " A14g true/false:", dict(Counter(x[5] for x in triples)))
print("   matchings carrying triples:", len(set(x[0] for x in triples)), " pairs (tau,F):", len(set((x[0], x[1]) for x in triples)))
json.dump({"name": name, "part": part, "nparts": nparts, "timed_out": timed_out, "stats": {k: int(v) for k, v in stats.items()},
           "reps": reps, "DEF": DEF, "triples": triples}, open(f"ref4_stageB_{name}_{part}of{nparts}.json", "w"))
