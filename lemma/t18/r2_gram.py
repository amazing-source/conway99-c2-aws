# Round 2, stage 1.5 (case n_3 = 0): the sigma-odd part of 7 E_{-4} on S u X_2.
# Orbit Gram matrix (integers) on the 9 active orbits T and the 9 sigma-orbits O = {s, sigma s} of X_2:
#     G_T = 3I + B,   G[i][O] = -([i in U] - [i in V]),   G[O][O] = 3 + [s ~ sigma s]  (4 iff O lies in N(p)),
#     G[O][O'] = -(A[s][s'] - A[s][sigma s'])  in {0, +1, -1}   (unknown: it encodes the edges between X_2 vertices).
# This 18x18 matrix is a principal submatrix of the Gram matrix of the 49 frame vectors, hence positive semidefinite.
# For every matching tau and every admissible choice F of the X_2 orbits inside N(p) we search (exhaustive backtracking,
# stop at the first solution) a filling of the unknown entries compatible with
#   - the graph: s ~ s' needs at most one common support neighbour, and both free at it;
#   - profile (3,3,1) only (h_2 = 3): the X_2 vertices of N(p) have no X_2 neighbour except their mate (A10);
#   - positive semidefiniteness of every leading block (rejection certified by an integer vector, or exact LDL).
# A pair (tau, F) with no filling is impossible.
# usage: python r2_gram.py <structure> <part> <nparts> <time limit s> <cases, e.g. 3 or 23>
import json, os, sys, itertools, time
import numpy as np
from enum_S import neg_certificate
from latt import psd_exact

here = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(here, "structures.json")))
types = json.load(open(os.path.join(here, "types.json")))
si, part, nparts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0
CASES = [int(c) for c in (sys.argv[5] if len(sys.argv) > 5 else "3")]
m = res[0]["survivors"][si]
name = f"(i) e=0 #{si}"
B = [[1 if (m[i][j] & 1) else 0 for j in range(9)] for i in range(9)]
Bn = [set(j for j in range(9) if B[i][j]) for i in range(9)]
td = json.load(open(os.path.join(here, f"r2_tau_{si}.json")))
DEF = [tuple(d) for d in td["DEF"]]
reps = td["reps"]
AT1 = set(); AS1 = set()
for Np, Nm, flag in types[name]:
    if flag and len(Np) == 2:
        AT1.add((tuple(Np), tuple(Nm)))
    if flag and len(Np) == 1:
        AS1.add((Np[0], Nm[0]))
pc = lambda x: bin(x).count("1")
GT = [[(3 if i == j else B[i][j]) for j in range(9)] for i in range(9)]
t0 = time.time()
STAT = {"psd_calls": 0, "exact_calls": 0}


def psd_int(G):
    """rigorous: returns False only with an exact proof (integer certificate or exact elimination)"""
    STAT["psd_calls"] += 1
    w = np.linalg.eigvalsh(np.array(G, dtype=float))
    if w[0] > 1e-7:
        return True
    if w[0] < -1e-7 and neg_certificate(G) is not None:
        return False
    STAT["exact_calls"] += 1
    return psd_exact(G)[0]


def process(tau):
    U = [set(DEF[k]) for k in range(18)]
    V = [set(DEF[tau[k]]) for k in range(18)]
    sup = [sum(1 << i for i in U[k]) | sum(1 << (9 + j) for j in V[k]) for k in range(18)]
    R = [[pc(sup[k] & sup[l]) for l in range(18)] for k in range(18)]
    orbs = [k for k in range(18) if k < tau[k]]
    elig = [k for k in orbs if not (U[k] & V[k]) and (DEF[k], DEF[tau[k]]) in AT1]
    def free_at(k, v):
        return not (V[k] & Bn[v]) if v < 9 else not (U[k] & Bn[v - 9])
    def edge_allowed(a, b):
        if b == a or b == tau[a] or R[a][b] > 1:
            return False
        if R[a][b] == 1:
            v = (sup[a] & sup[b]).bit_length() - 1
            return free_at(a, v) and free_at(b, v)
        return True
    crow = {o: [(1 if i in U[o] else 0) - (1 if i in V[o] else 0) for i in range(9)] for o in orbs}
    out = []
    for h2 in CASES:
        h1 = 9 - 2 * h2
        for Forb in itertools.combinations(elig, h2):
            if time.time() - t0 > tlimit:
                return None
            mem = [k for o in Forb for k in (o, tau[o])]
            if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):
                continue
            f = [sum(1 for k in mem if i in U[k]) for i in range(9)]
            if any(x > 2 for x in f):
                continue
            defi = [2 - x for x in f]
            def x1pairs(chosen):
                if all(d == 0 for d in defi):
                    return len(chosen) == h1
                if len(chosen) >= h1:
                    return False
                i = next(q for q in range(9) if defi[q] > 0)
                for j in range(9):
                    if j == i or defi[j] <= 0 or (i, j) not in AS1:
                        continue
                    ok = True
                    for k in mem:
                        if (i in U[k]) + (j in V[k]) > 1 or (j in U[k]) + (i in V[k]) > 1:
                            ok = False; break
                    if ok:
                        for (a2, b2) in chosen:
                            if (i == a2) + (j == b2) > 1 or (i == b2) + (j == a2) > 1:
                                ok = False; break
                    if ok:
                        defi[i] -= 1; defi[j] -= 1
                        chosen.append((i, j))
                        r = x1pairs(chosen)
                        chosen.pop()
                        defi[i] += 1; defi[j] += 1
                        if r:
                            return True
                return False
            if not x1pairs([]):
                continue
            order = list(Forb) + [o for o in orbs if o not in Forb]
            D = [4 if o in Forb else 3 for o in order]
            # allowed values of Ahat between orbits (graph level)
            def vals(o, o2):
                if h2 == 3 and (o in Forb or o2 in Forb):
                    return [0]
                r = [0]
                if edge_allowed(o, o2):
                    r.append(1)
                if edge_allowed(o, tau[o2]):
                    r.append(-1)
                return r
            # pair prefilter: PSD of the 11x11 Gram on T u {O, O'}
            allowed = {}
            dead = False
            for a in range(9):
                for b in range(a + 1, 9):
                    good = []
                    for val in vals(order[a], order[b]):
                        G = [row[:] + [-crow[order[a]][i], -crow[order[b]][i]] for i, row in enumerate(GT)]
                        G.append([-x for x in crow[order[a]]] + [D[a], -val])
                        G.append([-x for x in crow[order[b]]] + [-val, D[b]])
                        if psd_int(G):
                            good.append(val)
                    if not good:
                        dead = True; break
                    allowed[(a, b)] = good
                if dead:
                    break
            if dead:
                continue
            # backtracking, orbit by orbit
            Gfull = [[0] * 18 for _ in range(18)]
            for i in range(9):
                for j in range(9):
                    Gfull[i][j] = GT[i][j]
            for a in range(9):
                for i in range(9):
                    Gfull[9 + a][i] = Gfull[i][9 + a] = -crow[order[a]][i]
                Gfull[9 + a][9 + a] = D[a]
            def rec(a):
                if a == 9:
                    return True
                for combo in itertools.product(*[allowed[(b, a)] for b in range(a)]):
                    for b in range(a):
                        Gfull[9 + a][9 + b] = Gfull[9 + b][9 + a] = -combo[b]
                    sub = [row[:10 + a] for row in Gfull[:10 + a]]
                    if psd_int(sub) and rec(a + 1):
                        return True
                return False
            if rec(0):
                out.append([h2, list(Forb)])
    return out


my = [(q, r) for q, r in enumerate(reps) if q % nparts == part]
alive = []
done = 0
timed_out = False
nF = {h: 0 for h in CASES}
ntau_alive = {h: 0 for h in CASES}
for q, tau in my:
    r = process(tau)
    if r is None:
        timed_out = True
        break
    done += 1
    for h in CASES:
        c = sum(1 for x in r if x[0] == h)
        nF[h] += c
        if c:
            ntau_alive[h] += 1
    for x in r:
        alive.append([q] + x)
print(f"{name} part {part}/{nparts}: tau {len(my)}, done {done}, timed_out={timed_out}, time {time.time() - t0:.1f}s")
print(f"   surviving (tau, F) per case h_2: {nF};  tau with at least one surviving F: {ntau_alive};  {STAT}")
json.dump({"name": name, "part": part, "nparts": nparts, "done": done, "timed_out": timed_out, "cases": CASES,
           "alive": alive, "nF": nF, "ntau_alive": ntau_alive},
          open(os.path.join(here, f"r2_gram_{si}_{part}of{nparts}.json"), "w"))
