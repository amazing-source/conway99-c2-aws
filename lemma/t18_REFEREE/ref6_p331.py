# Referee check 6: profile (3,3,1) from my own model (nothing of the repo is read).
# Forced structure that I proved by hand (equality in A9):
#   A_p = 3 mate pairs of X_2 in N(p), each with a_2 = 1 (no X_2-neighbour except the mate);
#   {z0, s z0} = N(p) n X_0: z0 ~ p, z0 ~ s z0, no neighbour in S, a_2(z0) = 6, A_z0 = N(z0) n X_2 takes exactly one vertex
#   in each of the 6 orbits of X_2 outside A_p, N(s z0) n X_2 = tau A_z0; z0 not~ A_p.
#   Vertices: x_i = i, y_i = 9+i, p = 18, X_2 = 19..36, z0 = 37, sigma z0 = 38.   Y1 = these 39 vertices (all adjacencies decided).
# Step 45 (only run when asked): the 6 other vertices of X_0 (3 orbits), vertices 39..44:
#   no neighbour in S u {p, z0, s z0}; z not~ sigma z; exactly 2 neighbours in A_p; a_2(z) >= 4;
#   every s in A_p has exactly 2 neighbours among the six; every s in X_2 \ A_p exactly deg_H(s) + 1;
#   G = A[the six], sigma-invariant, deg_G(z) = a_2(z) - 4.
# Tests: budgets (partial graphs allowed) and float PSD of both matrices on determined sets only.  Count check, not a proof.
import itertools, sys, time, json, os
M1ONLY = os.environ.get('REF_M1ONLY') == '1'   # test 9(3I-A)+J only (to check the remark that two matrices are needed)
import numpy as np

REP = {
 "B0": "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
 "B1": "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
 "B2": "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}
name = sys.argv[1]
part, nparts = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
TLIM = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
DO45 = len(sys.argv) > 5 and sys.argv[5] == "45"
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
tau = [-1] * n; sols = []
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
                tau[a] = b; tau[b] = a; rec(); tau[a] = -1; tau[b] = -1
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

NV = 45
OFF = 1 - np.eye(NV, dtype=np.int64)
def psd(A, idxs, which=3):
    sub = A[np.ix_(idxs, idxs)].astype(float); m = len(idxs)
    ok1 = np.linalg.eigvalsh(9 * (3 * np.eye(m) - sub) + 1.0)[0] > -1e-7
    if which == 1 or M1ONLY: return ok1
    return ok1 and np.linalg.eigvalsh(11 * (4 * np.eye(m) + sub) - 2.0)[0] > -1e-7
def budget_ok(A):
    C = A @ A
    return not ((C > 2 - A) & (OFF == 1)).any()

stats = dict(tauF_budget=0, tauF_psd=0, nodes=0, complete_H=0, tested39=0, surv39=0, surv39_M1only=0,
             C_completions=0, tables45_budget=0, tables45_psd=0)
surv = []
t0 = time.time(); timed_out = False
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
    for F in itertools.combinations(usable, 3):
        A = A0.copy()
        for a in F:
            for c in (a, s[a]):
                A[18, 19 + c] = A[19 + c, 18] = 1
            A[19 + a, 19 + s[a]] = A[19 + s[a], 19 + a] = 1
        Ap = [c for a in F for c in (a, s[a])]
        base = list(range(19)) + [19 + c for c in Ap]
        sub = A[np.ix_(base, base)]; Cs = sub @ sub
        if ((Cs > 2 - sub) & (np.eye(len(base), dtype=np.int64) == 0)).any(): continue
        stats["tauF_budget"] += 1
        if not psd(A, base): continue
        stats["tauF_psd"] += 1
        if not budget_ok(A): continue
        rest = [a for a in orbs if a not in F]
        def finish(A):
            # z0 = 37, sigma z0 = 38; first orbit of `rest`: its smaller index is in A_z0 (z0 <-> sigma z0 symmetry)
            for bits in itertools.product((0, 1), repeat=5):
                side = (0,) + bits
                A2 = A.copy()
                A2[37, 38] = A2[38, 37] = 1
                A2[18, 37] = A2[37, 18] = 1; A2[18, 38] = A2[38, 18] = 1
                for q, a in enumerate(rest):
                    k = a if side[q] == 0 else s[a]
                    A2[37, 19 + k] = A2[19 + k, 37] = 1
                    A2[38, 19 + s[k]] = A2[19 + s[k], 38] = 1
                if not budget_ok(A2): continue
                stats["tested39"] += 1
                idxs = list(range(39))
                if psd(A2, idxs, 1): stats["surv39_M1only"] += 1
                if psd(A2, idxs):
                    stats["surv39"] += 1
                    surv.append((ti, tuple(F), A2.copy()))
                    if DO45: ext45(A2, Ap, rest)
        def ext45(A, Ap, rest):
            H = A[19:37, 19:37]
            degH = H.sum(1)
            needs = {}
            for c in range(18):
                needs[c] = 2 if c in Ap else int(degH[c]) + 1
            # choose Z for the representative of each of the 3 orbits; mate gets tau Z.
            # the three orbits are interchangeable: impose Z_1 < Z_2 < Z_3 (as sorted tuples) is NOT used; plain search,
            # tables counted as ordered triples divided by the symmetries is avoided: we only need existence / zero.
            def orbit_level(o, A, rem):
                if o == 3:
                    if any(rem.values()): return
                    stats["C_completions"] += 1
                    # G on the six vertices 39..44 (reps 39, 41, 43; mates 40, 42, 44)
                    a2 = [int(A[39 + q, 19:37].sum()) for q in range(6)]
                    pairs = [(0, 1), (0, 2), (1, 2)]
                    for gb in itertools.product((0, 1), repeat=6):
                        A2 = A.copy()
                        for t, (u, v) in enumerate(pairs):
                            if gb[2 * t]:      # z_u ~ z_v and mates
                                A2[39 + 2 * u, 39 + 2 * v] = A2[39 + 2 * v, 39 + 2 * u] = 1
                                A2[40 + 2 * u, 40 + 2 * v] = A2[40 + 2 * v, 40 + 2 * u] = 1
                            if gb[2 * t + 1]:  # z_u ~ sigma z_v and sigma z_u ~ z_v
                                A2[39 + 2 * u, 40 + 2 * v] = A2[40 + 2 * v, 39 + 2 * u] = 1
                                A2[40 + 2 * u, 39 + 2 * v] = A2[39 + 2 * v, 40 + 2 * u] = 1
                        dg = A2[39:45, 39:45].sum(1)
                        if any(int(dg[q]) != a2[q] - 4 for q in range(6)): continue
                        if not budget_ok(A2): continue
                        stats["tables45_budget"] += 1
                        if psd(A2, list(range(45))): stats["tables45_psd"] += 1
                    return
                z, sz = 39 + 2 * o, 40 + 2 * o
                later = 2 - o
                def vert_level(c, A, rem, size, inAp):
                    if c == 18:
                        if size < 4 or inAp != 2: return
                        # every remaining need must be coverable by the later orbits (each later orbit gives <= 2 per vertex:
                        # one from z, one from sigma z)
                        if any(r > 2 * later for r in rem.values()): return
                        orbit_level(o + 1, A, rem)
                        return
                    vert_level(c + 1, A, rem, size, inAp)
                    if rem[c] > 0 and rem[s[c]] > 0 and (c not in Ap or inAp < 2):
                        A2 = A.copy()
                        A2[z, 19 + c] = A2[19 + c, z] = 1
                        A2[sz, 19 + s[c]] = A2[19 + s[c], sz] = 1
                        if budget_ok(A2):
                            rem2 = dict(rem); rem2[c] -= 1; rem2[s[c]] -= 1
                            vert_level(c + 1, A2, rem2, size + 1, inAp + (c in Ap))
                vert_level(0, A, rem, 0, 0)
            orbit_level(0, A, dict(needs))
        # A_p vertices have no X_2-neighbour except the mate: candidates for H-edges are the placed NON-A_p vertices only
        def place_noAp(k, placed, A):
            stats["nodes"] += 1
            if k == len(rest):
                stats["complete_H"] += 1
                finish(A); return
            a = rest[k]; b = s[a]
            cands = placed[:]
            def choose(i, A):
                if i == len(cands):
                    idxs = base + [19 + c for c in placed] + [19 + a, 19 + b]
                    if psd(A, idxs): place_noAp(k + 1, placed + [a, b], A)
                    return
                u = cands[i]
                choose(i + 1, A)
                A2 = A.copy()
                A2[19 + a, 19 + u] = A2[19 + u, 19 + a] = 1
                A2[19 + b, 19 + s[u]] = A2[19 + s[u], 19 + b] = 1
                if budget_ok(A2): choose(i + 1, A2)
            choose(0, A)
        place_noAp(0, [], A)
el = time.time() - t0
print(f"{name} part {part}/{nparts}: {stats}  time {el:.0f}s timed_out={timed_out}", flush=True)
print("   39-vertex survivors lie in", len(set(x[0] for x in surv)), "matchings and", len(set((x[0], x[1]) for x in surv)), "pairs (tau,F)")
json.dump({"name": name, "DEF": DEF, "reps": reps, "stats": {k: int(v) for k, v in stats.items()}, "timed_out": timed_out,
           "surv39": [(ti, list(F), [int(x) for x in np.packbits(A.astype(np.uint8)).tolist()]) for ti, F, A in surv]},
          open(f"ref6_p331_{name}_{part}of{nparts}" + ("_M1only" if M1ONLY else "") + ".json", "w"))
