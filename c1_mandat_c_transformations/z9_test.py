"""Sanity checks of the nine-class system: (a) the 'old' part (a 3-unimodular lattice: classes 1,2,4 empty, class 3 =
class 0) must give exactly M_22(Gamma_0(7)), dimension 15; (b) dimension of the full space by leading exponents."""
import time
from fractions import Fraction as Fr
import z9theta as Z
N = 32
Mo = Z.Model(37, N)
ok, piv, free, _ = Mo.solve(); print("full system: free", len(free))
for side in ("T", "X"):
    res = Z.RHO if side == "T" else Z.SIG
    for k in (1, 2, 4):
        j = 0
        while (side, k, j) in Mo.index: Mo.eq({Mo.index[(side, k, j)]: Fr(1)}, 0, "old"); j += 1
    j = 0
    while (side, 0, j) in Mo.index:
        Mo.eq({Mo.index[(side, 0, j)]: Fr(1), Mo.index[(side, 3, j)]: Fr(-1)}, 0, "old"); j += 1
ok, piv, free, _ = Mo.solve(); print("old part (classes 1,2,4 empty, class 3 = class 0): consistent", ok, "free", len(free), "(expected 15)")
# (c) classes 1,2,4 empty but class 3 free: forms on the lattice pair L < L1 only
Mo = Z.Model(37, N)
for side in ("T", "X"):
    for k in (1, 2, 4):
        j = 0
        while (side, k, j) in Mo.index: Mo.eq({Mo.index[(side, k, j)]: Fr(1)}, 0, "c"); j += 1
ok, piv, free, _ = Mo.solve(); print("classes 1,2,4 empty, classes 0 and 3 free: consistent", ok, "free", len(free))
