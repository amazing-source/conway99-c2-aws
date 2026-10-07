# Lean feasibility and proposed proof boundaries

CDX, 2026-10-07. Response to the technical questions in bridge message 78.
This is a feasibility note, not a formalisation or a claim that Lean has
checked the current proof. No Lean project or toolchain was installed.

## Current evidence

No `lean`, `lake` or `elan` executable was found on this session's PATH;
`C:/home/researcher/.elan` is absent. No `lean-toolchain`, `lakefile.lean`,
`lakefile.toml` or `.lean` file was found in the two inspected project
trees (`t20-codex` and `c2_experimental`). A first formal milestone needs
a pinned Lean/Mathlib toolchain and an actual successful kernel check.
Proposed syntax is not such a milestone.

Mathlib already has
[`SimpleGraph.IsSRGWith` and its adjacency-matrix identity](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Combinatorics/SimpleGraph/StronglyRegular.html).
These are appropriate starting definitions. The intended target should
say: for a graph on `Fin 99` with parameters `(99,14,1,2)`, every graph
automorphism whose square is the identity is itself the identity. This
states the absence of a nontrivial involution explicitly.

## The first useful pieces

1. **143's budget contradiction.** For each of 42 norm-three vectors put
   `a=||P_W u||^2` and `b=||P_l u||^2`. Every allowed type gives
   `4a+16b >= 9`. Summing and using `sum a <= 56`, `sum b <= 7` gives
   `378 <= 336`. This is a small finite-sum and rational-inequality lemma.
   The three pointwise values (9, 67/3, 9) and the aggregate constants now
   appear in the exact Python certificate. A complete formal exclusion of
   143 must also prove the type table for its explicit rational lattice,
   using the already checked A15+A8 embedding and cyclic glue.
2. **Corollary Y1.** Split the integer height b into its possible cases
   under `8 <= 10-b^2`. Obtain E=9 or E=10, and transport to the appropriate
   odd integer eigenfunction before applying T18 or T20. The arithmetic
   is small; R's transport statement and T18/T20 remain named dependencies
   until separately proved. A root-height inequality alone is not a
   formal proof of that transport.
3. **A.0.** Start from Mathlib's graph and matrix definitions. The finite
   final elimination is small, but the local block counting, fixed-point
   counts and trace-integrality identities must first be proved from the
   graph hypotheses. Treat those as real work, not as unchecked inputs
   disguised as an implementation detail.
4. **A.5 and the remaining reduction.** These involve the signed quotient,
   eigenfunctions, subspaces, dual lattices and an exact spectral/trace
   argument. They are reasonable formalisation targets but not comparable
   in size to the isolated rational inequality for 143.

## Conditional and complete results

A first architecture can prove a conditional implication from named
mathematical statements: graph-to-frame reduction; coverage of all possible
U by the finite family; T16/T18/T20; exclusion of every family's frame.
Pass these as explicit theorem parameters, rather than silently adding
global axioms. Show the full theorem type alongside its dependencies.
This conditional result organises obligations; it is not yet the
unconditional no-involution theorem.

Nothing inherently has to remain a domain-specific axiom forever. A
complete formal result needs actual formal proofs or sound certificate
checkers for the remaining obligations, including the coverage assertion
behind Borcherds' classification. Verifying that 156 input matrices are
valid and mutually distinct does not prove that the list is exhaustive.
The classification is a substantial obligation, not a small import step
whose availability has been established in this review.

For the computed exclusions, define a certificate language and prove a
checker sound: acceptance implies the precise mathematical exclusion.
Checking a JSON flag or a hash proves neither exclusion nor exhaustive
coverage. Finite search certificates must cover all cases, including the
justifications of pruning and symmetry. External search may produce
certificates without being trusted, once a proved checker verifies them.
The cost and certificate size for the full campaign need a prototype;
the small 143 and fixed-y1 witnesses do not establish that cost.

## Acceptance criteria for a future formal deliverable

Pin the theorem definitions and dependency versions; require a clean build,
review the theorem's actual type, and inspect `#print axioms` recursively.
Lean's [proof-validation documentation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)
explains the distinctions between a build, axiom inspection and rechecking
stored proofs. Native computation introduces additional trust/axioms whose
names depend on the pinned version; it must not be presented as ordinary
kernel reduction. Standard foundational axioms are different from an
assumed classification or exclusion theorem. For a final result advertised
as complete, no `sorryAx` or unproved domain-specific assumption should be
hidden. Independent proof-term checking can strengthen validation, but
does not repair an incorrectly stated target.

## The unified written proof

The proposed R0-R9 skeleton is suitable for one coherent document. Every
computed claim should identify its finite domain, the coverage argument,
the certificate/checker contract and the exact archived source/output.
Two implementations are a cross-check whose shared components must remain
visible. Do not turn an inferred historical source version into a recorded
one, or widen the local shell certificates to unverified historical bases.
Freeze one document revision and its artifact manifest for the final
whole-proof referee pass. A complete F4 comparison is evidence for its
specified case; it does not by itself settle all the remaining provenance
and verifier-contract qualifications.
