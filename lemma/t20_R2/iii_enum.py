# T20 round 2, case III (k = 4): exhaustive enumeration of the determined set  Y = S u N[p] u X_2  (51 vertices).
#
# Hand facts used (report, section III): n_3 = 0, X_4 = {p}, X_0 = the six inactive inner vertices, |X_2| = 24;
# an X_2 vertex z is a word outside S, has type (U ; V) = (N(z) n S+ ; N(z) n S-), |U| = |V| = 2, U is a deficient
# unit of S+ and V a deficient unit of S+ (it is U(sigma z)); r(z) = number of active inner vertices adjacent to z;
# z has exactly 2 - r(z) neighbours in X_0 (two different pairs) and exactly 2 - r(z) neighbours in X_2; z is not
# adjacent to p nor to sigma z; every vertex of X_0 has exactly 4 neighbours in X_2; sigma is an automorphism.
#
# Search: the X_2 orbits {z, sigma z} are added one at a time; the orbit added is the one containing a vertex z
# whose U is the first deficient unit not yet covered.  Choices: V; N0 = N(z) n X_0 (up to the relabelling of the
# inactive pairs: an untouched pair is always the lowest untouched one, on its a-side); the edges between
# {z, sigma z} and the earlier orbits.  After each addition the induced graph on S u N[p] u (orbits so far) is
# completely known; tests: common-neighbour budgets and exact PSD certificates for M1, M2.
#
# usage: python iii_enum.py <III.0|III.1> <part> <nparts> <time limit s> [depth_split]
import sys, json, time, itertools
import numpy as np
import r2c
from r2c import N, PV, budgets_ok, psd_reject, STATS

name = sys.argv[1]
part = int(sys.argv[2]); nparts = int(sys.argv[3]); tlim = float(sys.argv[4])
t0 = time.time()
m, H = r2c.load_structs()[name]
A0 = r2c.base_graph(m, H)
r2c.check_base(A0, H)
Hs = set(H)
inact = [21, 22, 23, 24, 25, 26]           # a_4, b_4, a_5, b_5, a_6, b_6  (pairs (21,22), (23,24), (25,26))
NB = 27
# base graph on S u N[p]
AB = np.zeros((NB, NB), dtype=np.int64)
AB[:21, :21] = A0
for e in range(3):
    a, b = 21 + 2 * e, 22 + 2 * e
    AB[a, b] = AB[b, a] = 1
    AB[PV, a] = AB[a, PV] = 1
    AB[PV, b] = AB[b, PV] = 1
assert budgets_ok(AB)
assert AB[PV].sum() == 14

# deficient units of S+
units = []
for i in range(N):
    for j in range(i + 1, N):
        c = int((A0[i] * A0[j]).sum())
        need = (1 if A0[i, j] else 2) - c
        assert need >= 0
        units += [(i, j)] * need
assert len(units) == 24, len(units)
upairs = sorted(set(units))
mult = {u: units.count(u) for u in upairs}


def rcount(U, V):
    return sum(1 for i in U if i in Hs) + sum(1 for i in V if i in Hs)


def add_orbit(A, U, V, N0):
    """returns the adjacency matrix with a new orbit z = (U;V), sigma z = (V;U) appended (no edges to other
    outside-S vertices except X_0: z ~ N0, sigma z ~ sigma N0)"""
    n = A.shape[0]
    B = np.zeros((n + 2, n + 2), dtype=np.int64)
    B[:n, :n] = A
    z, sz = n, n + 1
    for i in U:
        B[z, i] = B[i, z] = 1
        B[sz, 10 + i] = B[10 + i, sz] = 1
    for i in V:
        B[z, 10 + i] = B[10 + i, z] = 1
        B[sz, i] = B[i, sz] = 1
    for u in N0:
        su = u + 1 if (u - 21) % 2 == 0 else u - 1
        B[z, u] = B[u, z] = 1
        B[sz, su] = B[su, sz] = 1
    return B


# admissible rectangles: (L) on S u N[p] u {z, sigma z} without X_0 neighbours is a spanning-subgraph test (valid)
single_cache = {}


def single_ok(U, V, N0):
    key = (U, V, N0)
    r = single_cache.get(key)
    if r is None:
        if set(U) & set(V) & Hs:
            r = False
        elif len(set(U) & set(V)) > 1:
            r = False
        else:
            B = add_orbit(AB, U, V, N0)
            if not budgets_ok(B):
                STATS.add("single_budget"); r = False
            elif psd_reject(B, "single") is not None:
                STATS.add("single_psd"); r = False
            else:
                r = True
        single_cache[key] = r
    return r


rect_cache = {}


def add_orbit21(U, V):
    B = np.zeros((23, 23), dtype=np.int64)
    B[:21, :21] = A0
    z, sz = 21, 22
    for i in U:
        B[z, i] = B[i, z] = 1
        B[sz, 10 + i] = B[10 + i, sz] = 1
    for i in V:
        B[z, 10 + i] = B[10 + i, z] = 1
        B[sz, i] = B[i, sz] = 1
    return B


def rect_ok(U, V):
    """type (U;V) alone on the induced (completely known) graph S u {p, z, sigma z}, 23 vertices"""
    key = (U, V)
    r = rect_cache.get(key)
    if r is None:
        if set(U) & set(V) & Hs or len(set(U) & set(V)) > 1:
            r = False
        else:
            B = add_orbit21(U, V)
            if not budgets_ok(B):
                STATS.add("rect_budget"); r = False
            elif psd_reject(B, "rect") is not None:
                STATS.add("rect_psd"); r = False
            else:
                r = True
        rect_cache[key] = r
    return r


pair_cache = {}
# pattern: 0 none, 1 z~z' (and sz~sz'), 2 z~sz' (and sz~z'), 3 both


def pair_ok(o1, o2, pat):
    key = (o1, o2, pat)
    r = pair_cache.get(key)
    if r is None:
        B = add_orbit(AB, *o1)
        B = add_orbit(B, *o2)
        z1, s1, z2, s2 = NB, NB + 1, NB + 2, NB + 3
        if pat & 1:
            B[z1, z2] = B[z2, z1] = 1; B[s1, s2] = B[s2, s1] = 1
        if pat & 2:
            B[z1, s2] = B[s2, z1] = 1; B[s1, z2] = B[z2, s1] = 1
        if not budgets_ok(B):
            STATS.add("pair_budget"); r = False
        elif psd_reject(B, "pair") is not None:
            STATS.add("pair_psd"); r = False
        else:
            r = True
        pair_cache[key] = r
    return r


def n0_choices(k, T, cnt):
    """canonical choices of N0 (k vertices of X_0 in different pairs); T = number of touched pairs; cnt = X_2-degrees"""
    out = []
    if k == 0:
        return [((), T)]
    touched = [v for v in inact[:2 * T]]
    if k == 1:
        for v in touched:
            out.append(((v,), T))
        if T < 3:
            out.append(((21 + 2 * T,), T + 1))
        return out
    for a in range(len(touched)):
        for b in range(a + 1, len(touched)):
            va, vb = touched[a], touched[b]
            if (va - 21) // 2 != (vb - 21) // 2:
                out.append(((va, vb), T))
    if T < 3:
        for v in touched:
            out.append(((v, 21 + 2 * T), T + 1))
    if T < 2:
        out.append(((21 + 2 * T, 23 + 2 * T), T + 2))
    return out


def sig_x0(u):
    return u + 1 if (u - 21) % 2 == 0 else u - 1


survivors = []
nodes = [0] * 13
timeout = False
leafcount = 0
task_counter = [0]
SPLIT_DEPTH = int(sys.argv[5]) if len(sys.argv) > 5 else 1


def dfs(A, orbs, degs, cnt, T, remaining):
    """orbs: list of (U, V, N0); degs: list of [deg_H(z_t)] (same for sigma z_t); cnt: dict X_0 vertex -> X_2 degree"""
    global timeout
    t = len(orbs)
    if timeout:
        return
    if time.time() - t0 > tlim:
        timeout = True
        return
    if t == 12:
        # exact final conditions
        if any(degs[i] != 2 - rcount(orbs[i][0], orbs[i][1]) for i in range(12)):
            STATS.add("final_degH"); return
        if any(cnt[v] != 4 for v in inact):
            STATS.add("final_x0deg"); return
        STATS.add("complete")
        survivors.append({"orbs": [[list(o[0]), list(o[1]), list(o[2])] for o in orbs],
                          "A": ["".join(map(str, r)) for r in A.tolist()]})
        return
    U0 = min(remaining)                      # first uncovered unit
    rem2 = dict(remaining)
    rem2[U0] -= 1
    if rem2[U0] == 0:
        del rem2[U0]
    for V in sorted(rem2):
        if V == U0:
            continue
        rem3 = dict(rem2)
        rem3[V] -= 1
        if rem3[V] == 0:
            del rem3[V]
        if not rect_ok(U0, V):
            continue
        r = rcount(U0, V)
        tgt = 2 - r
        for N0, T2 in n0_choices(tgt, T, cnt):
            if any(cnt[u] >= 4 for u in N0) or any(cnt[sig_x0(u)] >= 4 for u in N0):
                continue
            if t < SPLIT_DEPTH:
                pass
            if not single_ok(U0, V, N0):
                continue
            onew = (U0, V, N0)
            # allowed patterns against each earlier orbit
            allowed = []
            ok = True
            for i in range(t):
                room_i = (2 - rcount(orbs[i][0], orbs[i][1])) - degs[i]
                pats = []
                for pat in (0, 1, 2, 3):
                    need = bin(pat).count("1")
                    if need > room_i or need > tgt:
                        continue
                    if pair_ok(orbs[i], onew, pat):
                        pats.append(pat)
                if not pats:
                    ok = False
                    break
                allowed.append(pats)
            if not ok:
                STATS.add("no_pattern")
                continue
            cnt2 = dict(cnt)
            for u in N0:
                cnt2[u] += 1
                cnt2[sig_x0(u)] += 1
            if t == SPLIT_DEPTH - 1 or (SPLIT_DEPTH == 0 and t == 0):
                pass
            # enumerate edge patterns to earlier orbits with total degree <= tgt
            def rec(i, used, choice):
                if timeout:
                    return
                if i == t:
                    # task split
                    if t == SPLIT_DEPTH:
                        task_counter[0] += 1
                        if (task_counter[0] - 1) % nparts != part:
                            return
                    nodes[t] += 1
                    B = add_orbit(A, U0, V, N0)
                    z, sz = B.shape[0] - 2, B.shape[0] - 1
                    d2 = list(degs)
                    for q, pat in enumerate(choice):
                        zq, sq = NB + 2 * q, NB + 2 * q + 1
                        if pat & 1:
                            B[z, zq] = B[zq, z] = 1; B[sz, sq] = B[sq, sz] = 1
                        if pat & 2:
                            B[z, sq] = B[sq, z] = 1; B[sz, zq] = B[zq, sz] = 1
                        d2[q] += bin(pat).count("1")
                    if not budgets_ok(B):
                        STATS.add("budget_L%d" % t); return
                    if psd_reject(B, "L%d" % t) is not None:
                        STATS.add("psd_L%d" % t); return
                    # degree feasibility: an orbit with missing H-degree needs later orbits; the number of later
                    # orbits is 11 - t
                    if t == 11:
                        pass
                    dfs(B, orbs + [onew], d2 + [used], cnt2, T2, rem3)
                    return
                for pat in allowed[i]:
                    need = bin(pat).count("1")
                    if used + need > tgt:
                        continue
                    rec(i + 1, used + need, choice + [pat])
            rec(0, 0, [])


cnt0 = {v: 0 for v in inact}
dfs(AB, [], [], cnt0, 0, dict(mult))
out = {"name": name, "part": part, "nparts": nparts, "timeout": timeout, "nodes": nodes,
       "stats": STATS.c, "survivors": survivors, "seconds": time.time() - t0,
       "single_cache": len(single_cache), "pair_cache": len(pair_cache), "split_depth": SPLIT_DEPTH,
       "tasks": task_counter[0]}
fn = "iii_%s_%dof%d.json" % (name.replace(".", "_"), part, nparts)
json.dump(out, open(fn, "w"))
print(name, "part", part, "of", nparts, "timeout", timeout, "seconds %.1f" % (time.time() - t0))
print("nodes per level:", nodes)
print("stats:", STATS)
print("complete configurations on 51 vertices:", len(survivors))
print("tasks at split depth %d: %d" % (SPLIT_DEPTH, task_counter[0]))
