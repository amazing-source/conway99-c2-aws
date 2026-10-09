"""LEMMA C (apex of a triangle through a positive), tested directly on the register.

p a positive, Q_p = {p} u N_N(p) (9 vertices), t_p = edges inside N_N(p), c_p = c_pq + c_pq' (common N-neighbours with the two other
positives), i_p = sum over y in S \ Q_p of C(e(y, N_N(p)), 2).
n0(p) = number of outside vertices, not adjacent to p, without neighbour in N_N(p) = Phi_S(1_Qp, 1) / 2 = 5 + 2 c_p - 3 t_p - i_p.
Lemma C:  (8 - 2 t_p) - (4 - c_p) <= 2 n0(p).
usage: lemmaC.py"""
import json, collections
import numpy as np
import parabola as PA
reg = [json.loads(l) for l in open("register/supports_open_4581.jsonl", encoding="utf-8")]
dead_AB = {json.loads(l)["id"] for l in open("lemma_witnesses.jsonl")}
viol = []; mism = 0; hist = collections.Counter()
for d in reg:
    A = np.zeros((28, 28), dtype=np.int64)
    for a, b in d["edges"]: A[a, b] = A[b, a] = 1
    adj, R, dv = PA.data(d); bad = []
    for p in range(3):
        Np = [x for x in range(3, 28) if A[p, x]]; assert len(Np) == 8
        tp = sum(A[x, y] for x in Np for y in Np) // 2
        cp = sum(sum(A[q, x] for x in Np) for q in range(3) if q != p)
        ip = sum((lambda e: e * (e - 1) // 2)(int(sum(A[y, x] for x in Np))) for y in range(28) if y != p and y not in Np)
        w = np.zeros(28, dtype=np.int64); w[p] = 1; w[Np] = 1
        n0 = PA.phi(w, 1, R, dv); assert n0 % 2 == 0; n0 //= 2
        mism += n0 != 5 + 2 * cp - 3 * tp - ip
        hist[(tp, cp, ip, n0)] += 1
        if (8 - 2 * tp) - (4 - cp) > 2 * n0: bad.append(p)
    if bad: viol.append((d["id"], d["delta"], bad))
print("formula n0 = 5 + 2c - 3t - i wrong on", mism, "positives of", 3 * len(reg))
print("supports violating Lemma C:", len(viol), " of which not killed by Lemmas A, B:", sum(1 for v in viol if v[0] not in dead_AB))
print("   by delta (new ones):", sorted(collections.Counter(v[1] for v in viol if v[0] not in dead_AB).items()))
print("   n0 < 0 (Lemma A itself):", sum(v for k, v in hist.items() if k[3] < 0))
json.dump([v for v in viol if v[0] not in dead_AB], open("lemmaC_new.json", "w"))
print("   sample ids of new ones:", [v[0] for v in viol if v[0] not in dead_AB][:20])
