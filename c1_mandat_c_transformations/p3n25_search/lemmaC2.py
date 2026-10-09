"""LEMMA C, refined form.  For a positive p: U_p = N-neighbours x of p whose triangle with p leaves the support; apex z_x.
z_x can be adjacent to another positive q only if x !~ q, and at most 2 - c_pq apexes are adjacent to q.  An apex adjacent to p only
needs an exceptional neighbour, and the 6 outside neighbours of p see 2 n0(p) exceptional vertices in total.
Refined test:  |U_p| - (largest number of apexes that can be given a second positive)  <=  2 n0(p)."""
import json, collections, itertools
import numpy as np
import parabola as PA
reg = [json.loads(l) for l in open("register/supports_open_4581.jsonl", encoding="utf-8")]
dead_AB = {json.loads(l)["id"] for l in open("lemma_witnesses.jsonl")}
def test(d):
    A = np.zeros((28, 28), dtype=np.int64)
    for a, b in d["edges"]: A[a, b] = A[b, a] = 1
    adj, R, dv = PA.data(d); out = []
    for p in range(3):
        Np = [x for x in range(3, 28) if A[p, x]]
        U = [x for x in Np if not any(A[x, y] for y in Np)]
        w = np.zeros(28, dtype=np.int64); w[p] = 1; w[Np] = 1; n0 = PA.phi(w, 1, R, dv) // 2
        qs = [q for q in range(3) if q != p]; cap = [2 - int(sum(A[q, x] for x in Np)) for q in qs]
        el = [[x for x in U if not A[q, x]] for q in qs]
        best = 0
        for k1 in range(min(cap[0], len(el[0])) + 1):
            for X1 in itertools.combinations(el[0], k1):
                rest = [x for x in el[1] if x not in X1]
                best = max(best, k1 + min(cap[1], len(rest)))
        simple = len(U) - (cap[0] + cap[1])
        out.append((p, len(U), best, n0, len(U) - best > 2 * n0, simple > 2 * n0))
    return out
if __name__ == "__main__":
    import sys
    v1 = []; v2 = []
    for d in reg:
        o = test(d)
        if any(x[5] for x in o): v1.append(d["id"])
        if any(x[4] for x in o): v2.append((d["id"], d["delta"]))
    new = [v for v in v2 if v[0] not in dead_AB]
    print("simple form:", len(v1), "; refined form:", len(v2), "; refined, not killed by A, B:", len(new))
    print("   by delta (new):", sorted(collections.Counter(v[1] for v in new).items()))
    json.dump([v[0] for v in new], open("lemmaC2_new.json", "w"))
    for sid in (2503, 653, 2608, 4688, 2588, 4070, 5356, 1385):
        d = next(x for x in reg if x["id"] == sid); print("   level-2 death", sid, ":", test(d))
