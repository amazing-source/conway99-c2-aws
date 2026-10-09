"""Rank of the matrix of zonal theta vectors of A_8 (rows: functionals, columns: classes 0..4) at tau = rho, i, generic."""
import cmath, numpy as np
import a8
funcs = [(0, "r"), (4, "r"), (6, "r"), (6, "w"), (8, "r"), (8, "w"), (10, "r"), (10, "w"), (12, "r"), (12, "w")]
def mat(tau, fs):
    M = np.zeros((len(fs), 5), dtype=complex)
    for a, (m, pole) in enumerate(fs):
        for k in range(5):
            M[a, k] = sum(float(v) * cmath.exp(2j * cmath.pi * tau * E18 / 18) for E18, v in a8.series(k, m, pole, 30))
    return M
for name, tau in (("rho", cmath.exp(2j * cmath.pi / 3)), ("i", 1j), ("generic", 0.31 + 1.17j)):
    M = mat(tau, funcs)
    # scale rows to compare singular values
    M = M / np.abs(M).max(axis=1, keepdims=True)
    sv = np.linalg.svd(M, compute_uv=False)
    print(f"tau = {name}: singular values {np.array2string(sv, precision=3)}")
    sv6 = np.linalg.svd(M[:6], compute_uv=False)
    print(f"        first six functionals only: {np.array2string(sv6, precision=3)}")
