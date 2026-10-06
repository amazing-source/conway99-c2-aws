# T18, structural attempt (agent report of 2026-10-06, saved by the main session)

**No hand proof closes profile (2,5,0).** But one structural fact, the rank bound of section 2, excludes the four B1 survivors
without any further enumeration, and is an exact test for every determined set of 23 orbits or more.

Facts of `T18_REPORT.md` used: A0, A5, A8, A13 / A14 a-c. Everything assumes n_3 = 0 (`lemma/t18/N3_REPORT.md`).
Notation: alpha = a_2; Z = X_0 minus {p} (8 vertices, 4 orbits); y(z) = a_0(z) on X_0; t = e(X_2) = e(X_0); 7E = 7 E_{-4} = 3I - A + J/9;
W = the ten X_1 neighbours of p; A_p = the four X_2 neighbours of p; iota = the fixed-point-free involution on the 42 outer orbits
(O_x -> orbit of the two common neighbours of x and sigma x).

## 0. Remark on T18_REPORT.md
Round 3 calls the four 47-vertex B1 configurations "a genuine open case" (positive semidefinite, rank 46 of 47). But
27I - 9A + J = 63 E_{-4} has rank 44, and its sigma-odd and sigma-even parts have rank 22 each. Rank 46 is impossible. See section 2.

## 1. A8 as three integer eigenvectors (proved)

**P1.** With n_3 = 0 the following satisfy A f = -4 f:
- psi = 1_S + 2 * 1_{X_0} - 2 * 1_{X_2} (= 7E 1_S, sigma-even, |psi|^2 = 126);
- chi = (psi + phi)/2 = 1_P + 1_{X_0} - 1_{X_2} (values in {0, +-1}, eighteen +1 and eighteen -1);
- rho = 2 - a_0 on X_0, 2 - alpha on X_1, 1 - alpha on X_2, 0 on S (= 7E(1_{X_0} - 1_S), sigma-even).
Moreover |rho|^2 = 126 - 14t and rho is orthogonal to phi, psi, chi.

Proof. Each x in S has 4 neighbours in S; from (A^2 1_S)(x) = 44 = 16 + 2 sum d(w) over its 10 outside neighbours, sum d = 14, so 4
of them are in X_2 and 6 in X_1. A psi = -4 psi class by class, using a_0 = alpha - 4, alpha - 1, alpha + 2 on X_0, X_1, X_2:
S: 4 - 8 = -4; X_0: 2(alpha - 4) - 2 alpha = -8; X_1: 2 + 2(alpha - 1) - 2 alpha = 0; X_2: 4 + 2(alpha + 2) - 2 alpha = 8.
For any 9-set C, zeta_C = 3 * 1_C - A 1_C + 1 satisfies A zeta_C = -4 zeta_C. For C = X_0: zeta = 1 on S, 4 - a_0 on X_0,
2 - alpha on X_1, -1 - alpha on X_2, and rho = zeta - psi. Norms: |zeta|^2 = 7(27 - 2t + 9); zeta.psi = 7 (1_{X_0}, psi) = 126;
so |rho|^2 = 252 - 14t - 252 + 126. rho.psi = 126 - 126 = 0; rho.phi = 0 (even against odd).

Remarks. The identity (*) of A8 is exactly |rho|^2 = 126 - 14t; equivalently
(**) sum over X_1 u X_2 of rho^2 = 90 - 6t - sum_{z in Z} y(z)^2. All vertex identities of A8 / A14 are
(L): sum_{u ~ v} rho(u) = -4 rho(v) for every v. 9 divides |S| = 18, which is why 7E 1_S is integral (special to T18).

## 2. The rank bound (proved; applied by exact computation)

**P2.** Let Y be a sigma-invariant vertex set, M_Y and N_Y the principal submatrices of 27I - 9A + J and 44I + 11A - 2J. Then
rank M_Y <= 44 with odd part <= 22 and even part <= 22; rank N_Y <= 54 with odd part <= 27 and even part <= 27.

Proof. 27I - 9A + J = 63 E_{-4} and 44I + 11A - 2J = 77 E_3, of ranks 44 and 54. sigma commutes with A; trace(sigma) = 1 and
trace(sigma A) = #{x : x ~ sigma x} = 14 give trace(sigma | V_3) = trace(sigma | V_{-4}) = 0, so the eigenspaces split 22 + 22 and
27 + 27. A principal submatrix has rank at most the rank of the matrix, and for sigma-invariant Y the odd and even parts of M_Y are
compressions of 63 E_{-4}(I -+ sigma)/2.

In frame terms: the 49 frame vectors live in dimension 22, so **the Gram matrix 3I - A^ of any 23 orbits is singular**.

**P3.** For a set Y of k orbits, let n_3(Y), n_{-4}(Y) be the dimensions of the sigma-odd 3-eigenvectors and (-4)-eigenvectors
supported in Y. Then n_3(Y) = k - 22 + n_{-4}(Y^c) and n_{-4}(Y) = k - 27 + n_3(Y^c). (Rank-nullity for n -> E(sum n_O (e_x - e_{sigma x})).)

Consequences for profile (2,5,0):

| Determined set | Orbits | Constraint |
|---|---|---|
| Stage B: S u {p} u X_2 | 18 + p | none |
| Stage C: S u {p} u X_2 u W (47 vertices) | 23 + p | odd part of M_Y singular; even part of nullity >= 2 |
| Stage D (55 vertices) | 27 + p | odd nullity >= 5, even nullity >= 6 for M_Y; even nullity >= 1 for N_Y |

When a determined set has an odd Gram of rank exactly 22, every further orbit O must satisfy b_O^T G^+ b_O = 3 exactly (4 for a pair
of N(p)), not just <= 3. For profile (3,3,1), Y u W (25 orbits): odd nullity >= 3 is required (an independent check, not run).

**Computed** (`rank_survivors.py`, exact rational elimination on the rows of `t18\r3_p250_1_*_BC.json`). For each of the four B1
survivors (matchings #813 and #975):

| Matrix | Total rank | Odd part | Even part |
|---|---|---|---|
| 27I - 9A + J | 46 of 47 | 23 of 23 (bound 22) | 23 of 24 (bound 22) |
| 44I + 11A - 2J | 45 of 47 | 22 of 23 (bound 27) | 23 of 24 (bound 27) |

Second route (`rank_survivors_check2.py`): the 23 x 23 odd Gram 3I - A^ has determinant 47684 (#813) and 874944 (#975) by Bareiss in
integers, and rank 23 modulo two primes. Its smallest eigenvalue is about 0.011, which is why semidefiniteness alone does not see it.

> **The four survivors of B1 are excluded by P2 alone.** This re-checks the last step only; the list of survivors is still the
> enumeration of the B1 agent.

## 3. Hand lemmas for profile (2,5,0) (proved; they do not close the case)

**P4.** p is isolated in X_0. Between two different orbits of Z there are 0, 2 or 4 edges, 4 exactly when iota exchanges them.
Hence t = 2 q_1 + 4 q_2 is even, and y is constant on orbits.

**P5. t != 8, so t in {2, 4, 6}.** (t = 8 gives |rho|^2 = 14; rho(p) = 2 uses 4; on N(p), rho <= 0 with sum -8 and rho(sigma v) =
rho(v); a value <= -2 costs at least 12 with its mate; so all are 0 or -1 with squares 8, leaving 2 outside N[p]; but (L) at a
vertex of N(p) with rho = -1 needs three units outside.)

| t | y per orbit of Z | sum over X_1 u X_2 of rho^2 |
|---|---|---|
| 2 | (1,1,0,0) | 74 |
| 4 | (1,1,1,1) / (2,1,1,0) / (2,2,0,0) | 58 / 54 / 50 |
| 6 | (2,2,2,0) / (3,1,1,1) / (2,2,1,1) / (3,2,1,0) | 30 / 30 / 34 / 26 |

**P6. alpha <= 2 on X_2.** Hence e_1 := sum_{A_p}(alpha - 1) in {0, 2, 4}, with 8 + e_1 edges between A_p and Z and 8 - e_1 between W and Z.

**P7. alpha in {2, 3, 4} on W.**

**P8 (reformulation at p; not exploited).** The 9 orbits of the support are the edges of a multigraph Theta on the 7 pairs of N(p)
with degrees (4,4,2,2,2,2,2), no loop, multiplicity <= 2; with N the 9 x 7 matrix (f_i, h_c): N N^T = 2I + Theta^+- and
semidefiniteness on S u N[p] in the odd sector reads 10I + 4B - Theta^+- >= 0.

Check against data (`check_lemmas_stageB.py`): in the 5,595 + 4,977 + 196 stage-B triples of B0, B1, B2, t is in {2, 4, 6}, alpha on
A_p is (1,1,1,1) or (1,1,2,2), max alpha on X_2 is <= 2. P5-P6 are consistent with the enumerations and remove nothing more.

## 4. Promising but open
1. **Use P2 inside the enumerators.** At stage C, with 22 independent vectors placed, the fifth W-pair is determined: its row b must
   satisfy b^T G^{-1} b = 4 exactly.
2. A structural proof would have to show that the odd Gram of T u X_2 u W is never singular; no hand route found (mod 2, 3, 7
   reductions give nothing usable).
3. P3 at stage B: a real configuration carries at least 4 independent odd and 3 independent even (-4)-eigenvectors supported in
   Z u X_1; not turned into a contradiction.
4. t = 2 is the most rigid case (X_2 = two mate edges plus 14 isolated vertices); a hand treatment looks possible but long.

## 5. Tried, failed
Aggregate vertex Z at stage B (rejects 0 of the 5,595 / 4,977 / 196 triples); deflated inequalities; the lattice route (H16) with the
new vectors; parities of edge counts; Krein parameters (none vanishes); the quotient form of E_{-4} on {p}, A_p, W, S, Z; the cube
double count; t = 6 by (**) and (L); e_1 = 4.

## 6. Files
In the session scratchpad `t18_STRUCT\`: `rank_survivors.py` / `.out`, `rank_survivors_check2.py` / `.out`,
`check_lemmas_stageB.py` / `.out`, `aggZ_stageB.py`.
