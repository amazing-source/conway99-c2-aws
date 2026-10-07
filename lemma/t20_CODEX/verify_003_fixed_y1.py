"""Standalone exact verifier of the fixed-y1 root obstruction for 003.

Standard library only. No search code, root catalogue, floats or y2 enumeration.
The mathematical implication uses R, T18 and T20, as stated in the certificate.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def determinant(matrix):
    a = [[F(x) for x in row] for row in matrix]
    out = F(1)
    for c in range(len(a)):
        pivot = next((i for i in range(c, len(a)) if a[i][c]), None)
        if pivot is None:
            return F(0)
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            out = -out
        value = a[c][c]
        out *= value
        for i in range(c + 1, len(a)):
            factor = a[i][c] / value
            for j in range(c + 1, len(a)):
                a[i][j] -= factor * a[c][j]
            a[i][c] = F(0)
    return out


def verify(certificate, lattice=None, plan=None):
    source = certificate["lattice_input"]
    saved_plan = certificate["plan_input"]
    assert source["id"] == saved_plan["id"] == 3
    assert canonical_sha(source) == certificate["lattice_canonical_sha256"]
    assert canonical_sha(saved_plan) == certificate["plan_canonical_sha256"]
    if lattice is not None:
        assert canonical_sha(lattice) == certificate["lattice_canonical_sha256"], "Different lattice input"
    if plan is not None:
        assert canonical_sha(plan) == certificate["plan_canonical_sha256"], "Different plan input"
    generators = [[F(x) for x in row] for row in source["gens"]]
    basis = [[F(x) for x in row] for row in certificate["plan_basis"]]
    transform = certificate["plan_basis_in_input_generators"]
    assert len(generators) == len(basis) == len(transform) == 24
    assert all(len(row) == 24 for matrix in (generators, basis, transform) for row in matrix)
    assert all(type(x) is int for row in transform for x in row)
    assert matmul(transform, generators) == basis
    assert abs(determinant(transform)) == 1
    gram = matmul(basis, list(map(list, zip(*basis))))
    assert all(x.denominator == 1 for row in gram for x in row)
    assert determinant(gram) == 1
    strings = [[str(x) for x in row] for row in basis]
    # Precisely the plan producer's hash convention, independently computed.
    assert sha256(json.dumps(strings).encode()).hexdigest()[:16] == saved_plan["basis_sha"]
    assert saved_plan["plan"]["y1_orbits"] == len(saved_plan["y1_reps"]) == 182
    verified = []
    for witness in certificate["witnesses"]:
        index = witness["y1_index"]
        assert type(index) is int and 0 <= index < 182
        yc = saved_plan["y1_reps"][index]
        rc = witness["root_coefficients"]
        assert len(yc) == len(rc) == 24 and all(type(x) is int for x in yc + rc)
        y = matmul([yc], basis)[0]
        r = matmul([rc], basis)[0]
        assert y == list(map(F, witness["y1_ambient"]))
        assert r == list(map(F, witness["root_ambient"]))
        assert sum(x * x for x in y) == 7
        assert sum(x * x for x in r) == 2
        height = sum(x * z for x, z in zip(r, y))
        assert abs(height) == 2
        # Under R: 8 <= 14-height^2-b^2, with b an integer.
        possible_b = [b for b in range(-3, 4) if 14 - height * height - b * b >= 8]
        assert possible_b == [-1, 0, 1]
        assert {14 - height * height - b * b for b in possible_b} == {F(9), F(10)}
        verified.append(index)
    assert sorted(verified) == [158, 159, 162, 176, 181]
    assert list(range(182))[181::182] == [181]
    return {"verified": True, "y1_indices": sorted(verified), "last_job": "003:181:182",
            "root_norm": 2, "abs_root_y1_product": 2, "remaining_E_values": [9, 10],
            "dependencies": ["R-vi and R-vii", "T18", "T20"],
            "y2_enumeration_needed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("CERT_003_FIXED_Y1.json"))
    parser.add_argument("--lattice", type=Path)
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()
    cert = json.loads(args.certificate.read_text(encoding="utf-8"))
    result = verify(cert,
                    json.loads(args.lattice.read_text()) if args.lattice else None,
                    json.loads(args.plan.read_text()) if args.plan else None)
    # Negative controls exercise root data and attachment to the saved y1 list.
    from copy import deepcopy
    for field in ("root_coefficients", "y1_ambient"):
        bad = deepcopy(cert)
        bad["witnesses"][-1][field][0] = 999
        try:
            verify(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Corrupt {field} accepted")
    result["negative_controls_rejected"] = ["root_coefficients", "y1_ambient"]
    print(json.dumps(result))


if __name__ == "__main__":
    main()
