"""Exact lattice/glue checks for the hand exclusion of 143 (CDX, 2026-10-07).

Usage: python referee_143_checks.py <v10 package> [out.json]
SymPy performs all acceptance arithmetic. The engine proposes a reduced basis
and short roots only; no claim of completeness of its enumeration is used.
The exact basis identity, two A chains, primitive orthogonal vector and glue
classes certify all possible norm-three types without a theta-series count.
"""
import collections
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

import sympy as S


def main():
    pkg = Path(sys.argv[1]).resolve()
    source = pkg / "external_runs/structures_3eceb4d/U/143.json"
    rec = json.loads(source.read_text())
    assert rec["id"] == 143
    original = S.Matrix([[S.Rational(x) for x in row] for row in rec["gens"]])
    assert original.shape == (24, 24)
    original_gram = original * original.T
    assert all(x.q == 1 for x in original_gram) and original_gram.det() == 1

    sys.path.insert(0, str(pkg / "scripts"))
    import frame_dfs_next as FD
    proposed_basis, proposed_gram = FD.setup_lattice(rec["gens"], Fraction(1))
    basis = S.Matrix([[S.Rational(str(x)) for x in row] for row in proposed_basis])
    change = basis * original.inv()
    assert all(x.q == 1 for x in change) and abs(change.det()) == 1
    gram = basis * basis.T
    assert gram == S.Matrix(proposed_gram.tolist())

    # Positive norm-two proposals, exactly accepted in this proved lattice basis.
    roots = set()
    for proposal in FD.short(proposed_gram, 2):
        doubled = [int(x) for x in proposal]
        assert all(x % 2 == 0 for x in doubled)
        root = tuple(x // 2 for x in doubled)
        if not any(root):
            continue
        vector = S.Matrix([root])
        assert (vector * gram * vector.T)[0] == 2
        if next(x for x in root if x) > 0:
            roots.add(root)
    simples = sorted(r for r in roots if not any(
        tuple(a - b for a, b in zip(r, s)) in roots for s in roots))
    assert len(simples) == 23
    simple_matrix = S.Matrix(simples)
    cartan = simple_matrix * gram * simple_matrix.T
    assert all(cartan[i, i] == 2 for i in range(23))
    assert all(cartan[i, j] in (0, -1) for i in range(23) for j in range(i))
    neighbors = {i: [j for j in range(23) if cartan[i, j] == -1] for i in range(23)}
    remaining = set(range(23))
    chains = {}
    while remaining:
        endpoint = min(i for i in remaining if len(neighbors[i]) == 1)
        chain = []
        current = endpoint
        while True:
            assert current in remaining
            chain.append(current)
            remaining.remove(current)
            following = [j for j in neighbors[current] if j in remaining]
            assert len(following) <= 1
            if not following:
                break
            current = following[0]
        assert len(chain) not in chains
        chains[len(chain)] = S.Matrix([simples[i] for i in chain])
    assert set(chains) == {8, 15}
    assert cartan.det() == 144

    null = (simple_matrix * gram).nullspace()
    assert len(null) == 1
    scale = math.lcm(*(int(x.q) for x in null[0]))
    integral = [int(x * scale) for x in null[0]]
    divisor = math.gcd(*integral)
    z = S.Matrix([x // divisor for x in integral])
    assert math.gcd(*(int(x) for x in z)) == 1
    assert (z.T * gram * z)[0] == 144
    assert simple_matrix * gram * z == S.zeros(23, 1)
    assert abs(simple_matrix.col_join(z.T).det()) == 144
    heights = gram * z
    assert math.gcd(*(int(x) for x in heights)) == 1

    # The discriminant class of a weight of A_n is sum j*(x,alpha_j) mod n+1.
    # Check the claimed cyclic glue relation on EVERY lattice basis vector.
    units = {}
    for n, chain in chains.items():
        classes = gram * chain.T * S.Matrix(range(1, n + 1))
        candidates = [u for u in range(n + 1) if math.gcd(u, n + 1) == 1 and
                      all((classes[i] - u * heights[i]) % (n + 1) == 0 for i in range(24))]
        assert len(candidates) == 1
        units[n] = candidates[0]
        # Verify the root second-moment identity directly, using all positive
        # interval roots of the proved A chain, not the producer's root list.
        intervals = S.Matrix([list(sum((chain[j, :] for j in range(a, b)), S.zeros(1, 24)))
                              for a in range(n) for b in range(a + 1, n + 1)])
        moment = 2 * intervals.T * intervals * gram
        h2 = 2 * (n + 1)
        assert moment * moment == h2 * moment
        assert moment.rank() == n and gram * moment == moment.T * gram
    assert units[15] in (5, 11) and units[8] in (2, 7)

    # Every vector has integral height t. Orthogonal decomposition bounds
    # |t| <= 20 at norm three. Within each A-class the excess norm is even.
    possible = []
    table = collections.Counter()
    minima = {}
    for t in range(-20, 21):
        i, j = units[15] * t % 16, units[8] * t % 9
        p15, p8, pl = S.Rational(i * (16 - i), 16), S.Rational(j * (9 - j), 9), S.Rational(t*t, 144)
        minimum = p15 + p8 + pl
        assert minimum.q == 1
        minima[str(t)] = int(minimum)
        excess = 3 - minimum
        if excess >= 0 and excess % 2 == 0:
            assert excess == 0
            possible.append(t)
            table[(str(p8), str(pl))] += math.comb(16, i) * math.comb(9, j)
    assert possible == [-13, -9, -3, 3, 9, 13]
    assert table == {("2", "1/16"): 2688, ("0", "9/16"): 1120, ("8/9", "169/144"): 288}
    assert sum(table.values()) == 4096
    assert S.Rational(14 * 9, 16) == S.Rational(63, 8) > 7
    linear_values = {",".join(k): 4*S.Rational(k[0]) + 16*S.Rational(k[1]) for k in table}
    assert all(value >= 9 for value in linear_values.values())
    assert 42 * 9 == 378 > 336 == 4 * 56 + 16 * 7
    result = {
        "id": 143, "verified": True,
        "source_canonical_sha256": hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "basis_change_determinant": int(change.det()), "input_gram_determinant": 1,
        "simple_chain_ranks": sorted(chains), "root_lattice_determinant": 144,
        "primitive_z_coefficients": [int(x) for x in z], "z_norm": 144,
        "glue_index": 144, "glue_units": {str(k): v for k, v in units.items()},
        "possible_norm3_heights": possible,
        "norm3_types_and_signed_counts": {",".join(k): v for k, v in sorted(table.items())},
        "class_minima_for_abs_height_at_most_20": minima,
        "second_moment_projector_identities_verified": True,
        "linear_budget_certificate": {
            "weights_W_and_line": [4, 16],
            "values_on_norm3_types": {key: str(value) for key, value in sorted(linear_values.items())},
            "lower_bound_for_42_vectors": 378,
            "upper_bound_from_Rv": 336,
        },
        "norm3_enumeration_or_theta_count_used": False,
        "dependencies": ["R-ii (42 norm-three vectors)", "R-v", "A_n discriminant classes and their minimal weights"],
    }
    print(json.dumps(result, indent=2))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
