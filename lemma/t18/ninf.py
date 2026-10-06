# N(inf)-configurations.  For one S-structure, enumerate all ways to attach the inactive pairs (a_c, b_c)
# of N(inf) to S (their neighbourhoods in S), then test the fully determined graph on
#     S u {inf} u N(inf)      (33 vertices in pattern (i), 29 in pattern (ii))
# Filters:
#   - each type admissible (graph filters of rows.py, plus G4: two neighbours s, s' of w in Base must still
#     need a common neighbour)
#   - every word orbit x_i has exactly 2 neighbours in N(inf), never a_c and b_c together
#   - a_c, a_c' (c != c') : non adjacent, inf is one of their 2 common neighbours -> at most 1 common neighbour in S
#     (same for a_c, b_c')
#   - exact PSD of 63 E_{-4} and 77 E_3 on the whole determined graph (integer certificates)
#   - [conditional on H16] lattice test on T u {inactive h orbits}
# usage: python ninf.py <case index in structures.json> <structure index> [time limit seconds]
import json, os, sys, itertools, time
from latt import lattice_test, G_T_of
from enum_S import neg_certificate
from rows import base_adj

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
ci, si = int(sys.argv[1]), int(sys.argv[2])
tlimit = float(sys.argv[3]) if len(sys.argv) > 3 else 500.0
case = res[ci]
m = case["survivors"][si]
h = case["h"]
name = f"{case['name']} #{si}"
adj = base_adj(m, h)
GT = G_T_of(m, h)
words = [i for i in range(9) if i not in h]
n_inactive = 7 - len(h)
need = {i: 2 - sum(1 for c in h if m[i][c] & 1) for i in words}


def lam_mu(u, v):
    return 1 if v in adj[u] else 2


def admissible_h_types():
    out = []
    for d in (1, 2, 3):
        for Np in itertools.combinations(words, d):
            for Nm in itertools.combinations(words, d):
                if set(Np) & set(Nm):
                    continue
                if min(Np) > min(Nm):
                    continue            # a_c / b_c swap: the smallest orbit is on the + side
                N = set(Np) | set(9 + j for j in Nm) | {18}
                ok = True
                for s in range(19):
                    c = len(N & adj[s])
                    if s in N:
                        if c > 1: ok = False; break
                    else:
                        if c > 2: ok = False; break
                if not ok or (N & adj[18]):
                    continue
                # G4: pairs inside N must still need a common neighbour outside Base
                for s, t in itertools.combinations(sorted(N), 2):
                    if len(adj[s] & adj[t]) + 1 > lam_mu(s, t):
                        ok = False; break
                if not ok:
                    continue
                out.append((Np, Nm))
    return out


TYPES = admissible_h_types()
print(name, ": admissible types of an inactive a_c (up to a_c/b_c swap):",
      {d: sum(1 for t in TYPES if len(t[0]) == d) for d in (1, 2, 3)})
print("  needs per word orbit:", need)
sys.stdout.flush()


def compatible(t1, t2):
    p1, m1 = set(t1[0]), set(t1[1])
    p2, m2 = set(t2[0]), set(t2[1])
    if len(p1 & p2) + len(m1 & m2) > 1:
        return False
    if len(p1 & m2) + len(m1 & p2) > 1:
        return False
    return True


def full_tests(rows):
    """rows: list of (Np, Nm) for the non-trivial inactive c; returns (psd_ok, lattice_result)"""
    k = n_inactive
    rows = list(rows) + [((), ())] * (k - len(rows))
    n = 19 + 2 * k
    A = [[0] * n for _ in range(n)]
    for u in range(19):
        for v in adj[u]:
            A[u][v] = 1
    for c, (Np, Nm) in enumerate(rows):
        a, b = 19 + 2 * c, 20 + 2 * c
        A[a][b] = A[b][a] = 1
        A[a][18] = A[18][a] = 1
        A[b][18] = A[18][b] = 1
        for i in Np:
            A[a][i] = A[i][a] = 1
            A[b][9 + i] = A[9 + i][b] = 1
        for j in Nm:
            A[a][9 + j] = A[9 + j][a] = 1
            A[b][j] = A[j][b] = 1
    # exact lambda/mu upper bounds on the whole determined graph
    nb = [set(v for v in range(n) if A[u][v]) for u in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            c = len(nb[u] & nb[v])
            if c > 2 or (A[u][v] and c > 1):
                return "local", None
    M1 = [[9 * (3 * (u == v) - A[u][v]) + 1 for v in range(n)] for u in range(n)]
    M2 = [[11 * (4 * (u == v) + A[u][v]) - 2 for v in range(n)] for u in range(n)]
    if neg_certificate(M1) is not None or neg_certificate(M2) is not None:
        return "psd", None
    # lattice test on T u inactive h
    W = 9 + k
    GW = [[0] * W for _ in range(W)]
    for i in range(9):
        for j in range(9):
            GW[i][j] = GT[i][j]
    for c, (Np, Nm) in enumerate(rows):
        GW[9 + c][9 + c] = 4
        for i in Np:
            GW[9 + c][i] = GW[i][9 + c] = -1
        for j in Nm:
            GW[9 + c][j] = GW[j][9 + c] = 1
    r = lattice_test(GW, [1] * 9 + [0] * k, words[0])
    return "ok", r


t0 = time.time()
stats = {"covers": 0, "local": 0, "psd": 0, "lattice_short": 0, "lattice_degenerate": 0, "survive": 0}
seen = set()
survivors = []
timed_out = False


def rec(rows, rem):
    global timed_out
    if timed_out:
        return
    if time.time() - t0 > tlimit:
        timed_out = True
        return
    todo = [i for i in words if rem[i] > 0]
    if not todo:
        key = frozenset(rows) if len(set(rows)) == len(rows) else tuple(sorted(rows))
        if key in seen:
            return
        seen.add(key)
        stats["covers"] += 1
        status, r = full_tests(rows)
        if status != "ok":
            stats[status] += 1
            return
        if r is None:
            stats["survive"] += 1
            survivors.append(sorted(rows))
        elif r[0] == "degenerate":
            stats["lattice_degenerate"] += 1
            survivors.append(sorted(rows))
        elif r[0] == "notPSD":
            stats["psd"] += 1
        else:
            stats["lattice_short"] += 1
        return
    if len(rows) >= n_inactive:
        return
    i = todo[0]
    for t in TYPES:
        Np, Nm = t
        for sw in (0, 1):
            tt = (Np, Nm) if sw == 0 else (Nm, Np)
            if i not in tt[0] and i not in tt[1]:
                continue
            # canonical orientation of each row is the one stored in TYPES (min orbit on + side);
            # the swap is the relabelling a_c <-> b_c, so only sw == 0 is needed.
            if sw == 1:
                continue
            if any(rem[j] <= 0 for j in Np + Nm):
                continue
            if not all(compatible(t, r) for r in rows):
                continue
            for j in Np + Nm:
                rem[j] -= 1
            rows.append(t)
            rec(rows, rem)
            rows.pop()
            for j in Np + Nm:
                rem[j] += 1


rec([], dict(need))
print(f"  time {time.time() - t0:.1f}s  timed_out={timed_out}")
print("  stats:", stats)
for s in survivors[:20]:
    print("   survivor:", s)
json.dump({"name": name, "stats": stats, "timed_out": timed_out, "survivors": survivors},
          open(os.path.join(here, f"ninf_{ci}_{si}.json"), "w"))
