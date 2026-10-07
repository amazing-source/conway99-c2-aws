# Case I, exploration for round 3 (NOT part of any proof): number of configurations of N(p), i.e. of "bases"
# S u N[p] (35 vertices), for the profiles (h2,h1,h0) = (3,4,0) and (4,2,1).
# N(p) = h2 X_2-pairs of type {U, V} (U, V disjoint deficient pairs of S+), h1 X_1-pairs of type {i, k} (i != k,
# types distinct), h0 X_0-pairs; every index 0..9 is covered exactly twice (x_i has exactly 2 neighbours in N(p)).
# Tests: budgets (exact count) and PSD of M1, M2 on the 35 vertices (FLOAT decision: exploration only).
# usage: python i_bases.py I.0 <time limit s>
import sys, json, itertools, time
import numpy as np
import cases
name = sys.argv[1]; tlim = float(sys.argv[2])
m, H = cases.structure(name)
A21 = cases.support_graph(m, H)
units = cases.deficient_units(A21)
upairs = sorted(units)
rects = [(U, V) for U in upairs for V in upairs if U < V and not set(U) & set(V)]
t0 = time.time()
I35 = np.eye(35)
res = {}
for (h2, h1, h0) in ((4, 2, 1), (3, 4, 0)):
    cnt = {"raw": 0, "budget": 0, "psd": 0, "kept": 0}
    good = []
    timeout = False

    def test(comb, xs):
        cnt["raw"] += 1
        A = np.zeros((35, 35)); A[:21, :21] = A21
        t = 0
        for (U, V) in comb:
            w, sw = 21 + 2 * t, 22 + 2 * t; t += 1
            A[w, sw] = A[sw, w] = A[w, 20] = A[20, w] = A[sw, 20] = A[20, sw] = 1
            for i in U: A[w, i] = A[i, w] = A[sw, 10 + i] = A[10 + i, sw] = 1
            for i in V: A[w, 10 + i] = A[10 + i, w] = A[sw, i] = A[i, sw] = 1
        for (i, k) in xs:
            w, sw = 21 + 2 * t, 22 + 2 * t; t += 1
            A[w, sw] = A[sw, w] = A[w, 20] = A[20, w] = A[sw, 20] = A[20, sw] = 1
            A[w, i] = A[i, w] = A[w, 10 + k] = A[10 + k, w] = A[sw, k] = A[k, sw] = A[sw, 10 + i] = A[10 + i, sw] = 1
        for _ in range(h0):
            w, sw = 21 + 2 * t, 22 + 2 * t; t += 1
            A[w, sw] = A[sw, w] = A[w, 20] = A[20, w] = A[sw, 20] = A[20, sw] = 1
        X = A @ A + A
        np.fill_diagonal(X, 0)
        if (X > 2.5).any():
            cnt["budget"] += 1; return
        if np.linalg.eigvalsh(9 * (3 * I35 - A) + 1)[0] < -1e-7 or np.linalg.eigvalsh(11 * (4 * I35 + A) - 2)[0] < -1e-7:
            cnt["psd"] += 1; return
        cnt["kept"] += 1
        good.append([[list(U), list(V)] for (U, V) in comb] + [[i, k] for (i, k) in xs])

    def x1(comb, need, xs, start):
        if len(xs) == h1:
            if not any(need):
                test(comb, xs)
            return
        i = next((j for j in range(10) if need[j]), None)
        if i is None:
            return
        for k in range(i + 1, 10):
            if need[k] and (i, k) not in xs:
                need[i] -= 1; need[k] -= 1
                x1(comb, need, xs + [(i, k)], 0)
                need[i] += 1; need[k] += 1

    def rec(start, comb, cov, used):
        global timeout
        if time.time() - t0 > tlim:
            timeout = True
            return
        if len(comb) == h2:
            need = [2 - c for c in cov]
            if sum(need) == 2 * h1:
                x1(comb, need, [], 0)
            return
        for a in range(start, len(rects)):
            U, V = rects[a]
            if any(cov[i] >= 2 for i in U + V):
                continue
            if used.get(U, 0) >= units[U] or used.get(V, 0) >= units[V]:
                continue
            for i in U + V: cov[i] += 1
            used[U] = used.get(U, 0) + 1; used[V] = used.get(V, 0) + 1
            rec(a, comb + [(U, V)], cov, used)       # the same rectangle may be used twice if both units have m = 2
            for i in U + V: cov[i] -= 1
            used[U] -= 1; used[V] -= 1
            if timeout:
                return
    rec(0, [], [0] * 10, {})
    print("%s profile %s: rectangles {U,V} available %d; configurations of N(p): %d; rejected by budgets %d, by PSD (float) %d, kept %d%s   [%.0f s]" % (
        name, (h2, h1, h0), len(rects), cnt["raw"], cnt["budget"], cnt["psd"], cnt["kept"], "  (TIME LIMIT: incomplete)" if timeout else "", time.time() - t0))
    sys.stdout.flush()
    res[str((h2, h1, h0))] = good
json.dump(res, open("i_bases_%s.json" % name.replace(".", "_"), "w"))
