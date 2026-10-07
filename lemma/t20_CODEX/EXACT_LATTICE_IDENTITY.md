# Exact identification of the 156 input lattices

CDX, 2026-10-07. Follow-up to lines 455-458 of
`lemma/PROOF_C2/paper/main.tex` at `c1bcba6bb`.

The original `scripts/analysis/audit_L1_lattices.py` uses a floating rank
at line 43, and floating-pruned short-vector enumeration for absence of
norm one. `audit_L1_neighbours.py` imports that rank computation. Thus
those scripts alone do not support the paper's phrase "in exact arithmetic".

`q/codex_exact_lattice_identity.py` now supplies a separate exact
recomputation, reusing only the rational enumerator and exact basis algebra
of `q/codex_independent_packing.py`. It imports none of the original
identification, producer or frame-search programs. It does not assume the
minimum or the short-shell theta identity in order to establish the minimum.

Run:

```text
<lab-python> q/codex_exact_lattice_identity.py <lab-root>/external_runs/structures_3eceb4d/U
```

All 156 checks passed in 26.968 seconds. For each input the program checks:

- An exact unimodular change of its 24 rational generators to a reduced
  basis; integral Gram matrix, determinant one and oddness.
- Exhaustive norm at most two enumeration using rational LDL bounds and
  integer square roots. There are no norm-one vectors. Every returned root
  is checked again in exact arithmetic, with no duplicates up to sign.
- Components of the root nonorthogonality graph and their exact ranks by
  rational row elimination. Rank and number of roots identify the ADE
  components. All input root labels and counts agree. Integer matrix
  products have an explicit bound below 2^63 before numpy is used.
- The root type has precisely seven double occurrences:
  016/017, 023/027, 056/058, 077/079, 082/085, 120/121, 145/146.
- For those fourteen inputs, exact characteristic-vector construction,
  exhaustive enumeration of twice the shadow roots, and the two shadow
  classes distinguished by the parity of the norm of their difference.
  The two even-neighbour root systems agree with the input labels, and
  their unordered pair distinguishes each of the seven double occurrences.

The complete output is `measures/codex_exact_lattice_identity.json`.
It retains every input hash, reduced basis, Gram matrix, root coordinate,
component rank, enumeration node count and, for the fourteen cases, shadow
root coordinates and neighbour types. Script SHA256:
`8479a4188b04f25e6843c5b1ac70c5aabe6201d4b2b0fe8a9894f092c393f27c`.
Reused enumerator SHA256:
`1418cb5cc41670fe5d74d7e9c9bbf2b6296fe25d3bec38b2f30513df9297cd93`.

Consequently these data are 156 pairwise non-isometric odd integral
unimodular rank-24 lattices without norm-one vectors. Given Borcherds'
classification count, they exhaust that classification. The count is an
external theorem, not a result of this program; the author's
[Chapter 17 text](https://math.berkeley.edu/~reb/papers/splag/splag.pdf),
page 2, identifies the 156 classes and their two even neighbours.

This verifies the input-lattice identification, including the uniqueness
of the root types used for 152 and 153. It does not certify historical
frame-search executions or every root-type decision made during twin
transfer. Neighbour systems were recomputed here only for the fourteen
inputs needed to distinguish the seven ambiguous pairs.
