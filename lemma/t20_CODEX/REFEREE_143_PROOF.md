# Referee report: the hand exclusion of lattice 143

CDX, 2026-10-07. Reviewed the note and `budget_143.py` at master `48ad0cee7`,
and (R-ii), (R-v) in `../upstream/AUDIT_REDUCTION.md`.

**Accepted for the supplied lattice 143.** The two-subspace contradiction
is valid. A fresh run of the author's script reproduced all three types and
their counts. In addition, the exact glue check described below proves that
these are all possible norm-three types, without relying on completeness of
a floating-point short-vector enumeration or on a theta-series count. This
exclusion uses neither a solver, a pair search, nor T16, T18 or T20.

## The two-line argument

(R-v) is explicitly an identity for every real vector, so it can be summed
over an orthonormal basis of any real subspace V. This gives

    sum_f ||P_V f||^2 = 7 dim V.

The 42 vectors u have norm three by (R-ii). Dropping the other nine
nonnegative terms gives `sum_u ||P_V u||^2 <= 7 dim V`. No information
about those nine vectors, or about mutual inner products of the u, is needed.

For the A8 subspace W, a vector of the third type has squared projection 2.
Hence at most 28 of the 42 u have that type. At least 14 have squared
projection at least 9/16 onto the one-dimensional root complement l. Thus

    7 >= sum_u ||P_l u||^2 >= 14 * 9/16 = 63/8 > 7,

a contradiction. Ignoring the positive contribution of the third type to
l only weakens the lower bound and is legitimate.

For an A8 root system, the operator `sum_alpha alpha alpha^T` is 18 times
the orthogonal projector onto W: invariance and irreducibility make its
restriction scalar, and its trace is `2*72=144=18*8`. The supplementary
checker also verifies the corresponding projector identity by exact
matrix arithmetic; the same check gives the factor 32 for A15.

## Fresh computational checks

Commands, run with the lab's Python environment containing NumPy, Numba and
SymPy (package is `C:/home/researcher/Desktop/c2_experimental/c2_cloud_run_v10`):

```text
python lemma/upstream/budget_143.py <package> lemma/t20_CODEX/referee_143_budget_run.json
python lemma/t20_CODEX/referee_143_checks.py <package> lemma/t20_CODEX/referee_143_checks.json
```

The first completed in about 1.6 seconds, with the expected counts
`1120, 288, 2688`. The second completed in about 2.7 seconds. It uses
the engine only to propose a reduced basis and some roots; all acceptance
arithmetic is over exact SymPy integers/rationals. It does not enumerate
norm-three vectors. Its assertions verify:

- The original 24 generators have integral Gram matrix of determinant one.
  The proposed basis is related to them by an integral matrix of determinant
  -1, so it defines exactly the same lattice.
- Accepted norm-two vectors contain two orthogonal simple chains of types
  A8 and A15. Their root lattice M has determinant 144.
- The integral coefficient vector z perpendicular to both chains is
  primitive, has norm 144, and the height map `x -> (x,z)` is surjective
  onto Z (its coefficients have gcd one).
- `[U : M + Z z] = 144`, checked by an exact determinant. Thus
  `M = ker(x -> (x,z))`: the larger kernel would give a strictly smaller
  index, whereas the height map identifies its quotient modulo Z z with
  `Z/144`.
- On every lattice basis vector, the discriminant classes are
  `5t mod 16` in A15 and `7t mod 9` in A8, where `t=(x,z)`.
  Here 7 is -2 modulo 9, as allowed in the author's note.
- The only possible heights at norm three are `t=+-3,+-9,+-13`, and their
  projection types and signed multiplicities are exactly the stated table.

The exact source lattice is pinned by its canonical JSON SHA256
`ca8120583791801d840ad5c8990b3d4ebbe8c6a591544b0df5c00efce5f94f6d`.
The output records the primitive z, glue units, all 41 class minima and the
other assertions. No cloud job, queue or exclusion tracker was modified.

## Why the glue check supplies completeness

The lattice A_n is the set of integer vectors of coordinate sum zero in
R^(n+1). A dual class i is represented by an integer vector of coordinate
sum i minus `i/(n+1)` in every coordinate. For `0 <= i <= n`, its minimal
norm is `i(n+1-i)/(n+1)`, attained at the `binomial(n+1,i)` choices of i
coordinates equal to one. Other norms in that class differ by a
nonnegative even integer. The class of a weight is
`sum_j j*(x,alpha_j) mod (n+1)` for a consistently ordered simple chain.

For each integer height t, the exact checks show that the whole slice of U
is one translate of M, with the two specified discriminant classes.
Consequently its minimal norm is

    m(t) = i(16-i)/16 + j(9-j)/9 + t^2/144,
    i = 5t mod 16, j = 7t mod 9.

A norm-three vector must have `|t| <= 20` and `3-m(t)` a nonnegative even
integer. Checking those 41 integers gives only `+-3,+-9,+-13`, each with
`m(t)=3`. There are therefore no excited weights to consider. The binomial
multiplicities give respectively `2688,1120,288`, summing to 4096.
This proves completeness from the lattice glue, not from a presumed shell
count. It also proves that no extra root is hidden outside M: for nonzero
`|t| <= 16` the minimum is at least three, while the height-zero slice is M.

The author's hand cross-check, including its elimination of glue unit
`+-3 mod 16` by an extra root at height five, is consistent. The new check
instead reads the actual glue units directly on the supplied basis, so
does not require knowing beforehand that the proposed roots were complete.

## Scope and wording

The statement that the h and y are unused means that their specific norms
and products are unused; their nonnegative contributions are still dropped
from the common identity (R-v). The proof is sound with this interpretation.

`theta_odd24.py` alone does **not** establish `N3=4096`: its function
`series(n2,n3)` takes N3 as an input and derives later coefficients. The
note's attribution of norm-three completeness to that script should be
replaced by the glue argument above, or by a separate theorem fixing N3
for this family. This is a citation/dependency correction, not an obstacle
to the present exclusion, because the exact glue argument supplies the
needed completeness independently.

For lattice 143 this removes reliance on the old component-budget solver
record and on the outcome of its v10 run. It does not certify the remaining
pair-budget records, the other lattice inputs, or the entire 156-lattice
campaign. H4 can be discharged for **this lattice-level record** only.
