"""Theta series of an odd unimodular lattice of rank 24 without vector of norm 1 (exact integer arithmetic, no dependency).

Variable q = exp(pi i tau): the coefficient of q^n is the number N_n of vectors of norm n.
theta_L = theta_3^24 + a1 theta_3^16 D + a2 theta_3^8 D^2 + a3 D^3,  D = Delta_8 = q prod (1 - q^(2m-1))^8 (1 - q^(4m))^8.
N_1 = 0 fixes a1 = -48; N_2 and N_3 fix a2 and a3. Output:  N4 = 196560 - 24 N2 - 24 N3,  N5 = 276 N3,  N7 = 11178 N3.
Used by lemma/upstream/AUDIT_REDUCTION.md (hole H3 of AUDIT_ENGINE_RULES.md: exact count of the norm-4 shell X4).
Controls: odd Leech lattice (N2 = 0, N3 = 4096) and D12+ + D12+ (N2 = 528, N3 = 4096; N4 counted directly = 85584).

This script takes N3 as an INPUT: it does not prove its value (remark of the referee of LATTICE_143.md, 07/10).
The value N3 = 4096 for every such lattice is a theorem of shadow theory (Conway-Sloane, "A new upper bound for the minimum of an
integral lattice of determinant one", 1990): the theta series of the shadow is
    sum_r a_r (-1)^r 16^(-r) theta_2^(24-8r) theta_4^(8r),
whose constant term is -a3 / 4096 (only r = 3 has no factor theta_2); the shadow of an ODD lattice does not contain 0, so
a3 = 0, i.e. N3 = 16192 - 48 * 252 = 4096 and N4 = 98256 - 24 N2. The same series gives a2 = N2 + 48 vectors of norm 2 in the
shadow (the "new roots"). The script checks these two consequences as assertions below.
"""
N = 8


def mul(a, b):
    c = [0] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if i + j <= N:
                    c[i + j] += x * y
    return c


def pw(a, k):
    r = [1] + [0] * N
    for _ in range(k):
        r = mul(r, a)
    return r


th3 = [0] * (N + 1)
th3[0] = 1
m = 1
while m * m <= N:
    th3[m * m] += 2
    m += 1
D = [0, 1] + [0] * (N - 1)
for m in range(1, N + 2):
    for e in (2 * m - 1, 4 * m):
        if e <= N:
            f = [0] * (N + 1)
            f[0] = 1
            f[e] = -1
            D = mul(D, pw(f, 8))
b0, b1, b2, b3 = pw(th3, 24), mul(pw(th3, 16), D), mul(pw(th3, 8), pw(D, 2)), pw(D, 3)
a1 = -b0[1]


def series(n2, n3):
    a2 = n2 - b0[2] - a1 * b1[2]
    a3 = n3 - b0[3] - a1 * b1[3] - a2 * b2[3]
    return [b0[k] + a1 * b1[k] + a2 * b2[k] + a3 * b3[k] for k in range(N + 1)]


if __name__ == "__main__":
    c00, c10, c01 = series(0, 0), series(1, 0), series(0, 1)
    for k in (4, 5, 7):
        print(f"N{k} = {c00[k]} + ({c10[k] - c00[k]}) N2 + ({c01[k] - c00[k]}) N3")
    assert series(0, 4096)[:6] == [1, 0, 0, 4096, 98256, 1130496]            # odd Leech lattice
    assert series(528, 4096)[4] == 2 * 7944 + 264 * 264 == 85584             # D12+ + D12+, direct count
    # shadow theory: a3 = 0 forces N3 = 4096, whatever N2; then N4 = 98256 - 24 N2 and a2 = N2 + 48
    assert b0[3] + a1 * b1[3] == 4096 and b2[3] == 0
    assert all(series(n2, 4096)[4] == 98256 - 24 * n2 for n2 in (0, 48, 312, 528, 1104))
    assert all(n2 - b0[2] - a1 * b1[2] == n2 + 48 for n2 in (0, 312, 528))
    print("controls OK")
