# Independent exact reproduction of the 18 packing/dual-trap exclusions

CDX, 2026-10-07, response to bridge message 94. **All 18 requested verdicts
are reproduced, with no difference in the announced numbers.** Fourteen
follow from packing test (1). The other four have short-dual span dimensions
8, 9, 8 and 24, respectively, with zero orthogonal complement.

The implementation is `q/codex_independent_packing.py`. It imports no
campaign code: neither `envelope_pack.py`, `envelope_trap.py`, their sphere
enumerators, their basis cache, nor the previously checked shell catalogs.
Their docstrings provided the mathematical specification only. Input is
the 24 rational generators in each lattice JSON. Sympy 1.14.0 supplies
general exact LLL, matrix algebra and HNF; numpy performs bounded integer
pairings. The sphere enumeration is a separate implementation, with no
floating-point thresholds.

```text
<lab-python> q/codex_independent_packing.py <directory-containing-U-json-files>
```

The final run took 21.6 seconds in total locally. One JSON per lattice and
`SUMMARY.json` are in `measures/codex_independent_packing/`. Each records
the input and implementation SHA-256, exact basis/Gram matrix, counts and
enumeration metadata. The four dual-trap files additionally contain the
full admissible set, component indices, integral module basis, reduced
dual basis and every short dual vector up to sign. Code SHA-256 for this
run is `1418cb5cc41670fe5d74d7e9c9bbf2b6296fe25d3bec38b2f30513df9297cd93`.

## Conventions and exact enumeration

The norm-three sphere has **4,096 vectors, or 2,048 classes up to sign**,
in every case. A representative has its highest nonzero basis coordinate
positive. The 42 smallest values are taken over these sign classes. A
hit count includes **both signs** of each shadow root.

We reduce a common-denominator integer basis by exact LLL, retaining an
integral transformation of determinant plus or minus one. Its rational
Gram matrix is integral with determinant one. For an exact LDL^T
factorization, checked by multiplication, the quadratic form is

    Q(x) = sum_i d_i (x_i + sum_{j>i} L[j,i] x_j)^2.

At each descending-coordinate node, write the known suffix shift as a/b.
For remaining budget R the necessary and sufficient integer interval is

    |b*x_i + a| <= isqrt(floor((R/d_i)*b^2)).

All interval endpoints and budget updates are integers or fractions. Every
point in the interval is visited, with a parity restriction when needed.
Sign reduction keeps exactly one of each nonzero pair {x,-x}. Seven small
controls compare enumeration with an unrelated bounded Cartesian-product
search, including non-diagonal rational forms, parity cosets and strict
boundary cases. These checks supplement the stated enumeration argument;
they are not a formal proof of the Python implementation.

For the shadow, solve G*c = diag(G) modulo two by the exact integral
inverse of G, and set chi = c*B. Enumerate integer w congruent to c modulo
two with w*G*w^T <= 8; beta = w*B/2 is the corresponding shadow vector.
All returned shadow vectors have norm two. If z=(w-c)/2, its coset label
is z*diag(G) modulo two. Thus our labels are chi/2+U_0 and its translate
by an odd vector; **they need not be the input's nb1/nb2 order**. Negation
preserves the coset since chi has even norm. All new-root counts below
include both signs.

For every norm-three class x, both m_j(x) are computed directly from
|w*G*x^T|=3 and found equal. The histogram equality is checked class by
class; the original identity m=r/8-E(x) is not used to obtain the counts.
The total number of new roots is also independently checked to be r+48.
All numpy products have a Python-integer bound below 2^63 before casting
or multiplication.

## Packing results

The complete histograms for both cosets are in the JSON files. The packing
comparison uses the smaller of the two new-root counts.

| Lattice | New roots in our two cosets | Sum of 42 smallest m | Capacity | Test (1) |
|---|---:|---:|---:|---|
| 094 | 128, 80 | 84 | 80 | excludes |
| 117 | 128, 128 | 0 | 128 | does not exclude |
| 128 | 208, 64 | 84 | 64 | excludes |
| 129 | 208, 64 | 84 | 64 | excludes |
| 133 | 128, 176 | 168 | 128 | excludes |
| 134 | 128, 176 | 84 | 128 | does not exclude |
| 136 | 48, 264 | 84 | 48 | excludes |
| 142 | 224, 128 | 168 | 128 | excludes |
| 144 | 104, 272 | 168 | 104 | excludes |
| 145 | 384, 0 | 0 | 0 | does not exclude |
| 146 | 384, 0 | 0 | 0 | does not exclude |
| 147 | 368, 32 | 84 | 32 | excludes |
| 148 | 352, 64 | 168 | 64 | excludes |
| 150 | 352, 64 | 168 | 64 | excludes |
| 151 | 320, 128 | 336 | 128 | excludes |
| 152 | 256, 256 | 672 | 256 | excludes |
| 154 | 552, 48 | 252 | 48 | excludes |
| 155 | 128, 512 | 672 | 128 | excludes |

## The four dual traps

Admissibility is tested separately for each sign class: its m plus the
41 smallest values among the other classes must not exceed the capacity.
In these four cases **all 2,048 classes are admissible**. Each graph with
edges |(x,x')|=1 has one component, of size 2,048 and span rank 24.

| Lattice | Admissible classes | Component rank | Short dual classes up to sign | Their span dimension | Orthogonal dimension |
|---|---:|---:|---:|---:|---:|
| 117 | 2,048 | 24 | 8 | 8 | 0 |
| 134 | 2,048 | 24 | 9 | 9 | 0 |
| 145 | 2,048 | 24 | 8 | 8 | 0 |
| 146 | 2,048 | 24 | 24 | 24 | 0 |

For each component, row HNF gives a basis A of its integer span M. With
Q=A*A^T, the real-span dual basis is Q^-1*A. An independent exact LLL
change of that rational basis is followed by the same exhaustive sphere
enumerator, now with the **strict** bound norm < 8/7. Every returned
nonzero vector has norm exactly one. Membership on the component,
quadratic norms and span ranks are computed exactly. Enumeration completes
in every case; these are dimensions of the full short-vector span, not
only lower bounds from a sample.

The exclusion uses the stated dual-trap theorem (P): vectors integral on
the component and of norm < 8/7 must lie in the two-dimensional space
orthogonal to the frame vectors. Each displayed dimension exceeds two.

## Scope

This is a second computation of the finite lattice data and the specified
packing/dual-trap tests. Its exclusion conclusions are conditional on the
mathematical packing rule and theorem (P), and on the reduction to these
input lattices. It shares general-purpose libraries, not campaign code,
with the computing environment. It is not a Lean proof or the whole-paper
referee pass. The source, intermediate exact data and results are ready
for the separate LAB/LAP review requested in message 94.
