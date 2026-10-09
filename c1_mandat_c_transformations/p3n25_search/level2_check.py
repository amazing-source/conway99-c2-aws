"""INDEPENDENT CHECK of the level-2 certificates.  Uses only the edge list of the support (no code of the search).

For a support S (28 vertices: positives 0, 1, 2; negatives 3..27) inside an srg(99,14,1,2), an outside vertex z has a neighbourhood B in
S with:  (i) |B inter N| - |B inter P| = 4  (z is a zero of the vector 2/9 + 1_P - 1_N);  (ii) every vertex of B has at most one
neighbour in B  (lambda = 1);  (iii) every vertex of S outside B has at most two neighbours in B  (mu = 2);  (iv) two vertices of B have
r >= 1, where r(s,t) = (1 if s ~ t else 2) - (common neighbours of s, t inside S)  (z is a common neighbour outside S).
The certificate names a pair {s,t} with r(s,t) >= 1.  The check: enumerate ALL sets B containing s, t with (i)-(iv); for each one build
the 29 x 29 adjacency matrix A' of S u {z} and evaluate the witness:
   Lemma A:   w^T (12 I + 2 J - A' - A'^2) w - (2a+1) (14 sum(w) - 1^T A' w) + 70 a (a+1)  <  0 ;
   Lemma B:   with r', dZ' computed from A', X = N(v) minus u:   u !~ v:  sum_X r'(u,x) > 2 (dZ'(u) - r'(u,v)) + min(r'(u,v), #{x in X: r'(v,x) = 1})
                                                                 u ~ v:   sum_X r'(u,x) > dZ'(u) - r'(u,v).
If every B is refuted, the pair has no common neighbour outside: the support is impossible.      usage: level2_check.py register.jsonl certs.jsonl"""
import sys, json
import numpy as np

def blocks_through(A, r, s0, t0):
    """all B containing s0, t0 with (i)-(iv), by exhaustive depth-first enumeration over the 28 vertices"""
    out = []; order = [s0, t0] + [v for v in range(28) if v not in (s0, t0)]
    def ok_partial(B):
        for x in B:
            if sum(A[x][y] for y in B) > 1: return False
        return True
    def rec(i, B):
        if i == 28:
            if sum(1 for x in B if x >= 3) - sum(1 for x in B if x < 3) != 4: return
            for x in range(28):
                if x not in B and sum(A[x][y] for y in B) > 2: return
            out.append(sorted(B)); return
        v = order[i]
        if i >= 2: rec(i + 1, B)
        if all(r[v][y] >= 1 for y in B) and sum(A[v][y] for y in B) <= 1:
            B2 = B + [v]
            if ok_partial(B2) and sum(1 for x in B2 if x < 3) <= 3 and sum(1 for x in B2 if x >= 3) <= 7: rec(i + 1, B2)
    rec(0, [])
    return out

def refuted(A, B, wit):
    A2 = np.zeros((29, 29), dtype=np.int64); A2[:28, :28] = A
    for x in B: A2[28, x] = A2[x, 28] = 1
    if wit["k"] == "A":
        w = np.array(wit["w"] + [wit["h"]], dtype=np.int64); a = wit["a"]
        M = 12 * np.eye(29, dtype=np.int64) + 2 - A2 - A2 @ A2
        phi = int(w @ M @ w) - (2 * a + 1) * int(14 * w.sum() - A2.sum(axis=0) @ w) + 70 * a * (a + 1)
        return phi < 0
    u, v = wit["u"], wit["v"]
    C = A2 @ A2; rr = np.where(A2 == 1, 1, 2) - C; dz = 14 - A2.sum(axis=1)
    X = [x for x in range(29) if A2[v, x] and x != u]
    lhs = sum(int(rr[u, x]) for x in X)
    if A2[u, v]: return lhs > int(dz[u] - rr[u, v])
    return lhs > 2 * int(dz[u] - rr[u, v]) + min(int(rr[u, v]), sum(1 for x in X if rr[v, x] == 1))

if __name__ == "__main__":
    reg = {}
    for line in open(sys.argv[1], encoding="utf-8"):
        d = json.loads(line); reg[d["id"]] = d
    good = bad = 0
    for line in open(sys.argv[2]):
        c = json.loads(line); d = reg[c["id"]]
        A = np.zeros((28, 28), dtype=np.int64)
        for x, y in d["edges"]: A[x, y] = A[y, x] = 1
        assert A[:3, :3].sum() == 0 and all(A[p].sum() == 8 for p in range(3))            # three independent positives with 8 negative neighbours
        C = A @ A; r = (np.where(A == 1, 1, 2) - C).tolist(); s, t = c["pair"]
        assert s != t and r[s][t] >= 1
        Bs = blocks_through(A.tolist(), r, s, t)
        wit = {tuple(w["B"]): w for w in c["blocks"]}
        ok = all(tuple(B) in wit and refuted(A, B, wit[tuple(B)]) for B in Bs)
        good += ok; bad += not ok
        print(f"support {c['id']}: pair {c['pair']}, r = {r[s][t]}; {len(Bs)} admissible blocks enumerated, {len(wit)} witnesses given; all refuted: {ok}", flush=True)
    print(f"certificates checked: {good} valid, {bad} invalid")
