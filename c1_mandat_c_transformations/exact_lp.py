"""Exact feasibility of a system  c0_i + cf_i . x >= 0  (x free, rational data), by a phase-1 simplex in Fractions on
the Farkas system:   lam >= 0,  sum_i lam_i cf_i = 0,  sum_i lam_i c0_i = -1.
Returns ("infeasible", lam) with an exact certificate (checked), or ("feasible", x) with an exact point (checked).
The basis has only (number of variables + 1) rows, so the tableau is small; Bland's rule prevents cycling."""
from fractions import Fraction as Fr


def solve(G):
    m = len(G); nf = len(G[0][1]); R = nf + 1
    # rows: for k < nf: sum lam_i cf_i[k] = 0 ; row nf: sum lam_i (-c0_i) = 1
    T = [[Fr(G[i][1][k]) for i in range(m)] for k in range(nf)] + [[-Fr(G[i][0]) for i in range(m)]]
    rhs = [Fr(0)] * nf + [Fr(1)]
    # scale each structural column by a positive rational to keep numbers small (does not change feasibility)
    scale = []
    for i in range(m):
        s = max([abs(T[r][i]) for r in range(R)] + [Fr(0)])
        scale.append(Fr(1) / s if s else Fr(1))
        for r in range(R): T[r][i] *= scale[i]
    for r in range(R): T[r] += [Fr(int(r == q)) for q in range(R)]       # artificial columns m..m+R-1
    basis = [m + r for r in range(R)]
    ncol = m + R
    def reduced():
        # phase-1 cost: 1 on artificials; reduced cost of column j = c_j - sum_r c_B[r] T[r][j]
        return [(Fr(1) if j >= m else Fr(0)) - sum(T[r][j] for r in range(R) if basis[r] >= m) for j in range(ncol)]
    it = 0
    while True:
        it += 1
        rc = reduced()
        ent = next((j for j in range(m) if rc[j] < 0), None)               # Bland: smallest index, structural columns only
        if ent is None: break
        best = None
        for r in range(R):
            if T[r][ent] > 0:
                ratio = rhs[r] / T[r][ent]
                if best is None or ratio < best[0] or (ratio == best[0] and basis[r] < basis[best[1]]): best = (ratio, r)
        assert best is not None, "unbounded phase 1 (impossible)"
        r = best[1]; pv = T[r][ent]
        T[r] = [x / pv for x in T[r]]; rhs[r] /= pv
        for q in range(R):
            if q != r and T[q][ent] != 0:
                f = T[q][ent]; T[q] = [x - f * y for x, y in zip(T[q], T[r])]; rhs[q] -= f * rhs[r]
        basis[r] = ent
        if it > 200000: raise RuntimeError("too many pivots")
    infeas = sum(rhs[r] for r in range(R) if basis[r] >= m)
    if infeas == 0:
        lam = [Fr(0)] * m
        for r in range(R):
            if basis[r] < m: lam[basis[r]] = rhs[r] * scale[basis[r]]
        # exact check of the certificate
        assert all(l >= 0 for l in lam)
        assert all(sum(lam[i] * G[i][1][k] for i in range(m)) == 0 for k in range(nf))
        assert sum(lam[i] * G[i][0] for i in range(m)) == -1
        return "infeasible", lam, it
    # feasible: the artificial columns hold B^{-1}; phase-1 duals y = c_B B^{-1} satisfy  y . col_i <= 0 for all i and y . b > 0
    y = [sum(T[r][m + q] for r in range(R) if basis[r] >= m) for q in range(R)]
    # y_k (k<nf), y_nf: for every i: sum_k y_k cf_i[k] - y_nf c0_i <= 0 (after scaling), and y_nf = y.b > 0  ->  x = -y[:nf]/y_nf
    assert y[nf] > 0
    x = [-y[k] / y[nf] for k in range(nf)]
    assert all(G[i][0] + sum(G[i][1][k] * x[k] for k in range(nf)) >= 0 for i in range(m)), "point check failed"
    return "feasible", x, it


if __name__ == "__main__":
    # two small self-tests
    print(solve([(Fr(-1), [Fr(1)]), (Fr(3), [Fr(-1)])])[0])          # x >= 1, x <= 3
    print(solve([(Fr(-3), [Fr(1)]), (Fr(1), [Fr(-1)])])[0])          # x >= 3, x <= 1
