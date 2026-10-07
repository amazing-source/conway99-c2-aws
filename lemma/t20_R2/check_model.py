# cross-check of the model code: the base graphs and the deficient units used by the engines (cases.py) against an
# independent construction from the edge lists PRINTED in T20_REPORT.md section C (typed in here by hand).
import numpy as np, itertools
import cases
REPORT = {
 "III.0": ("07 08 09 15 16 19 24 26 28 34 35 37 48 49 57 58 67 69", "", [0, 1, 2, 3]),
 "III.1": ("07 08 09 15 16 19 24 26 28 34 35 37 48 49 56 57 67 89", "", [0, 1, 2, 3]),
 "IIa.0": ("07 08 09 13 15 16 23 24 26 28 29 35 37 39 45 46 48 57 68 79", "23", [0, 1]),
}
DEF = {   # deficient pairs printed in the report: (m = 2 pairs, m = 1 pairs)
 "III.0": ("49 58 67", "07 08 09 14 15 18 25 26 27 34 36 39 47 48 57 59 68 69"),
 "III.1": ("58", "05 06 07 14 18 19 25 26 27 34 38 39 45 46 47 49 59 67 68 69 78 79"),
 "IIa.0": ("45 67", "01 04 05 06 08 16 18 19 29 38 47 49 57 58 69 78"),
}
def build(minus, plus, H):
    A = np.zeros((21, 21), dtype=np.int64)
    def e(u, v): A[u, v] = A[v, u] = 1
    for w in minus.split():
        i, j = int(w[0]), int(w[1]); e(i, 10 + j); e(j, 10 + i)
    for w in plus.split():
        i, j = int(w[0]), int(w[1]); e(i, j); e(10 + i, 10 + j)
    for i in H: e(i, 10 + i); e(20, i); e(20, 10 + i)
    return A
for name, (minus, plus, H) in REPORT.items():
    A = build(minus, plus, H)
    if name.startswith("III"):
        prob = cases.CaseIII(name)
        B = np.zeros((27, 27), dtype=np.int64); B[:21, :21] = A
        for a in (21, 23, 25):
            for (u, v) in ((a, a + 1), (20, a), (20, a + 1)):
                B[u, v] = B[v, u] = 1
        same = (B == prob.AB).all()
        nb = 27
    else:
        prob = cases.CaseIIaN(name, [(2, 3), (2, 4), (4, 5), (6, 7), (8, 9)])
        same = (A == prob.AB[:21, :21]).all()
        nb = 21
    units = {}
    for w in DEF[name][0].split(): units[(int(w[0]), int(w[1]))] = 2
    for w in DEF[name][1].split(): units[(int(w[0]), int(w[1]))] = 1
    print("%s: base graph identical on the first %d vertices: %s; deficient units identical to the report's table: %s; "
          "sigma is an automorphism of the base: %s" % (name, nb, same, units == prob.units,
          all(prob.AB[u, v] == prob.AB[prob.sig[u], prob.sig[v]] for u in range(prob.AB.shape[0]) for v in range(prob.AB.shape[0]))))
