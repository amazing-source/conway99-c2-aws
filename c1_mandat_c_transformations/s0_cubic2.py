"""S0 cubic: are there exact linear relations among the cubic sums of the RIGID low layers (all entries in c/9 + {-1,0,1})?"""
import sys, time
from fractions import Fraction as Fr
import s0_cubic as SC, z9theta as Z, mf7
N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
C = SC.build(N); free, expr = SC.reduce(C)
RHO, SIG = Z.RHO, Z.SIG
expo = lambda nm: (RHO if nm[0] == "T" else SIG)[nm[1]] + 9 * nm[2]
top = lambda nm: nm[0] != "x" and expo(nm) > 9 * (N - 9)
inner = [t for t, f in enumerate(free) if not top(f)]
E = lambda side, c, num9: expr[(side, c, (num9 - (RHO if side == "T" else SIG)[c]) // 9)]
low = [("X", 2, e) for e in (77, 86, 95, 104, 113, 122, 131, 140)] + [("X", 1, e) for e in (89, 98, 107, 116, 125)] + \
      [("X", 4, e) for e in (110, 119, 128, 137)] + [("X", 3, e) for e in (117, 126, 135)]
for nm in low:
    e = E(*nm)
    bad = [t for t in e if t not in inner]
    print(f"{nm[0]}{nm[1]}[{nm[2]}/9] (L-norm {2*nm[2]}/9): depends on {len(e)} free sums" + (f"  (!! {len(bad)} truncation-edge ones)" if bad else ""),
          {f"{free[t][0]}{free[t][1]}[{expo(free[t])}/9]": str(v) for t, v in sorted(e.items())} if len(e) <= 4 else "")
rig = [("X", 2, e) for e in (77, 86, 95, 104, 113, 122)] + [("X", 1, 89)]
rows = [[E(*nm).get(t, Fr(0)) for t in inner] for nm in rig]
red, piv, T = mf7.rref(rows)
print("rank of the 7 rigid layers in the 14 free cubic sums:", len(piv))
