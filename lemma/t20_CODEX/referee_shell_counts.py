"""Exact theta-coefficient and archived shell-count checks (CDX, 2026-10-07).

No lattice enumeration: this checks the count identities and the 156-row
report, not the membership/distinctness/provenance of its underlying lists.
The theta-space and shadow formulas are cited in REFEREE_SHELL_COUNTS.md.
"""
import hashlib
import json
from pathlib import Path
import runpy

TOP = 28  # Work in t=q^(1/4), through q^7.


def product(a, b):
    c = [0] * (TOP + 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b[:TOP + 1 - i]):
            c[i + j] += x * y
    return c


def power(a, exponent):
    result = [1] + [0] * TOP
    for _ in range(exponent):
        result = product(result, a)
    return result


def main():
    here = Path(__file__).resolve().parent
    report_path = here.parents[1] / "measures/SHELL_COUNTS_2026-10-07.json"
    report = json.loads(report_path.read_text())
    assert set(report) == {f"{i:03d}" for i in range(156)}
    theta2, theta3, theta4 = ([0] * (TOP + 1) for _ in range(3))
    for m in range(-8, 9):
        if (2*m + 1)**2 <= TOP:
            theta2[(2*m + 1)**2] += 1
        if 4*m*m <= TOP:
            theta3[4*m*m] += 1
            theta4[4*m*m] += 1 if m % 2 == 0 else -1
    delta16 = product(power(theta2, 4), power(theta4, 4))
    assert all(x % 16 == 0 for x in delta16)
    delta = [x // 16 for x in delta16]
    # Independent check against the product definition in the cited paper.
    delta_product = [0] * (TOP + 1)
    delta_product[4] = 1
    for m in range(1, 8):
        for exponent in (4*(2*m - 1), 16*m):
            if exponent <= TOP:
                factor = [0] * (TOP + 1)
                factor[0], factor[exponent] = 1, -1
                delta_product = product(delta_product, power(factor, 8))
    assert delta == delta_product
    basis = [product(power(theta3, 24 - 8*r), power(delta, r)) for r in range(4)]
    assert all(not coefficient for row in basis for k, coefficient in enumerate(row) if k % 4)
    basis = [row[::4] for row in basis]

    def series(n2, n3):
        a = [1, -basis[0][1]]
        a.append(n2 - basis[0][2] - a[1]*basis[1][2])
        a.append(n3 - sum(a[r]*basis[r][3] for r in range(3)))
        return [sum(a[r]*basis[r][k] for r in range(4)) for k in range(8)]

    c0, c2, c3 = series(0, 0), series(1, 0), series(0, 1)
    affine = {str(k): [c0[k], c2[k] - c0[k], c3[k] - c0[k]] for k in (4, 5, 7)}
    assert affine == {"4": [196560, -24, -24], "5": [0, 0, 276], "7": [0, 0, 11178]}
    assert basis[0][3] - 48*basis[1][3] == 4096
    assert basis[2][3] == 0 and basis[3][3] == 1
    assert basis[0][1] == 48
    production = runpy.run_path(str(here.parent / "upstream/theta_odd24.py"))
    assert all(series(n2, n3) == production["series"](n2, n3)[:8]
               for n2, n3 in ((0, 0), (1, 0), (0, 1)))

    residuals = {}
    for lid, row in sorted(report.items()):
        assert all(type(row[f"N{k}"]) is int and row[f"N{k}"] >= 0 and row[f"N{k}"] % 2 == 0
                   for k in (2, 3, 4))
        n2, n3, n4 = (row[f"N{k}"] for k in (2, 3, 4))
        residuals[lid] = 196560 - 24*n2 - 24*n3 - n4
        assert residuals[lid] == 0
        assert row["expected_N4"] == n4 and row["ok"] is True
        assert n3 == 4096 and 2*row["shadow_pairs"] == n2 + 48
    # A missing-vector deficit is nonnegative. This positive linear form
    # vanishes only when all deficits vanish; no finite sampling is a proof
    # of that elementary implication, which is given explicitly in the note.
    out = {
        "verified": True, "lattices_checked": len(report),
        "shell_report_canonical_sha256": hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "theta_basis_coefficients_q0_through_q7": basis,
        "affine_coefficients_in_1_N2_N3": affine,
        "max_absolute_archived_residual": max(map(abs, residuals.values())),
        "shadow_a3_relation": "a3=N3-4096; zero shadow constant gives a3=0",
        "expected_norm7_lines": 11178*4096//2,
        "underlying_shell_lists_rechecked": False,
        "lattice_enumeration_run": False,
    }
    print(json.dumps(out, indent=2))
    here.joinpath("referee_shell_counts.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
