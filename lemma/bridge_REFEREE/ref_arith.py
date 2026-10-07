"""Referee: arithmetic of the consequences (BRIDGE.md sections 0, 4 'coset reduction', 6.10). Pure integers.
A vector v of an integral lattice with y1, y2 orthogonal of norm 7 has data (N, a, b) = ((v,v), (v,y1), (v,y2)), with
a^2 + b^2 <= 7 N (Cauchy-Schwarz / Bessel) and E = 7N - a^2 - b^2.  v + m y1 + n y2 has data (N + 2ma + 2nb + 7m^2 + 7n^2, a + 7m, b + 7n)."""
import itertools


def red(x):                      # representative in [-3, 3] mod 7
    return (x + 3) % 7 - 3


def reduce(N, a, b):
    a0, b0 = red(a), red(b); m, n = (a0 - a) // 7, (b0 - b) // 7
    assert a + 7 * m == a0 and b + 7 * n == b0
    return N + 2 * m * a + 2 * n * b + 7 * m * m + 7 * n * n, a0, b0


print("squared norm of phi_v = 2E:  norm 2, Y=5: E=%d -> %d;  norm 2, Y=4: E=%d -> %d;  norm 3, Y=13: E=%d -> %d;  norm 4, (3,3): E=%d -> %d"
      % (14 - 5, 2 * (14 - 5), 14 - 4, 2 * (14 - 4), 21 - 13, 2 * (21 - 13), 28 - 18, 2 * (28 - 18)))
assert (2 * (14 - 5), 2 * (14 - 4), 2 * (21 - 13)) == (18, 20, 16)
vals = sorted({a * a + b * b for a in range(-3, 4) for b in range(-3, 4)})
print("values of a^2+b^2 with |a|,|b|<=3:", vals); assert vals == [0, 1, 2, 4, 5, 8, 9, 10, 13, 18]

table = {}
for E in range(0, 15):
    reps = set(); count = 0
    for N in range(0, 80):
        for a in range(-30, 31):
            for b in range(-30, 31):
                if 7 * N - a * a - b * b != E: continue
                count += 1
                N0, a0, b0 = reduce(N, a, b)
                assert 7 * N0 - a0 * a0 - b0 * b0 == E                       # E is invariant
                assert N0 * 7 == E + a0 * a0 + b0 * b0
                reps.add((N0, tuple(sorted((abs(a0), abs(b0))))))
    table[E] = sorted(reps)
    print("E = %2d: %5d triples (N<80,|a|,|b|<=30) -> reduced representatives (norm, {|a|,|b|}): %s" % (E, count, table[E]))
claimed = {8: [(3, (2, 3))], 9: [(2, (1, 2))], 10: [(2, (0, 2)), (4, (3, 3))], 11: [(3, (1, 3))], 12: [(2, (1, 1)), (3, (0, 3))],
           13: [(2, (0, 1)), (3, (2, 2))], 14: [(2, (0, 0))]}
for E, v in claimed.items(): assert table[E] == sorted(v), (E, table[E], v)
assert table[0] == [(0, (0, 0))]
assert all(N0 <= 3 for E in range(1, 8) for N0, _ in table[E])
print("table of section 4 (E = 8..14): CONFIRMED;  E = 0 -> only the zero class;  E = 1..7 -> representatives of norm <= 3:",
      {E: table[E] for E in range(1, 8)})
# section 6.10
for N in (3, 4):
    Y = 7 * N - 9
    sols = [(a, b) for a in range(-9, 10) for b in range(-9, 10) if a * a + b * b == Y]
    print("norm %d with E = 9 needs Y = %d: representations as a sum of two squares: %s" % (N, Y, sols)); assert not sols
sols5 = sorted({tuple(sorted((abs(a), abs(b)))) for a in range(-9, 10) for b in range(-9, 10) if a * a + b * b == 35 - 9})
print("norm 5 with E = 9 needs Y = 26: {|a|,|b|} in", sols5, "-> reduces to", {reduce(5, a, b) for a, b in ((1, 5), (5, 1), (-1, 5), (1, -5))})
assert sols5 == [(1, 5)] and all(reduce(5, a, b)[0] == 2 for a in (1, -1) for b in (5, -5))
# all (N, Y) with N <= 5 and E in 8..10
for E in (8, 9, 10):
    print("E = %d, norm <= 5: (norm, Y, {|a|,|b|}) =" % E,
          sorted({(N, 7 * N - E, tuple(sorted((abs(a), abs(b))))) for N in range(1, 6) for a in range(-6, 7) for b in range(-6, 7) if a * a + b * b == 7 * N - E}))
print("ARITHMETIC OK")
