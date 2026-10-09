"""Rank 43, scenario S0: no root (b1 = a7 = 0) and no vector of L1 of norm 16..24.  Then theta_L1 is determined
(a13 = 2632) and, by the class-level relations (w49.py), the vectors of each norm are equally distributed among the
8 classes of their circle.  Integrality test: a_n must be divisible by 8 for every n not divisible by 7."""
from fractions import Fraction as Fr
from thetalp import Theta
import exact_lp
T = Theta(43, 84, standard=False)
# solve the 7 free coordinates from a7 = ... = a12 = 0 and b1 = 0  (a7 = b1 at rank 43), exactly
import mf7
rows = [T.a[n][1:] + [-T.a[n][0]] for n in range(7, 13)] + [T.b[1][1:] + [-T.b[1][0]]]
red, piv, _ = mf7.rref(rows)
assert piv == list(range(7)), piv
c = [red[i][7] for i in range(7)]
val = lambda f: f[0] + sum(f[1 + i] * c[i] for i in range(7))
a = [val(T.a[n]) for n in range(85)]; b = [val(T.b[n]) for n in range(13)]
print("a7..a13:", [str(x) for x in a[7:14]], " b1..b4:", [str(x) for x in b[1:5]])
bad = []
for n in range(13, 85):
    x = a[n]
    assert x.denominator == 1 and x >= 0, (n, x)
    if n % 7 and int(x) % 8: bad.append((n, int(x), int(x) % 8))
    if n % 7 == 0: assert a[n] == b[n // 7], (n, a[n], b[n // 7])
print("all a_n (13 <= n <= 84) are non-negative integers; a_7k = b_k checked")
print("norms 2n with a_n not divisible by 8 (n not divisible by 7):", bad[:20], "..." if len(bad) > 20 else "")
print("a_n / 8 for n = 13..27:", [(n, str(Fr(a[n], 8))) for n in range(13, 28) if n % 7])
