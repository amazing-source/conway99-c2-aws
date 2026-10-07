# Referee report on the upstream reduction, section A

Reviewer: CDX, 2026-10-07. Single pass, errors only, as requested.

Reviewed `lemma/upstream/AUDIT_REDUCTION.md` at master `c10bb83e1`
(section A introduced in `f115663b7`), lines 26-150. File SHA256:
`e60cc3280ef0a3a922239859de595a84c031d13dd2a7b77d14dc37e82a5b6044`.

**No mathematical error found in section A.** This includes Theorem R,
the oddity and Witt-class calculation (lines 80-98), the lower bound for
the dual minimum (107-119), the integral unimodular gluing, primitivity
and absence of norm-one vectors (124-133), and the two consequences in
A.8 (145-150). No assumption `g in {18,20}` is needed in these steps.

This report does not validate the search engine, pair coverage, the
identity of the input lattices, or the historical exclusion records
(sections B-E). Borcherds' classification and the oddity formula remain
cited external theorems, not new proofs in this report. The vector `c`
at lines 83-88 is read in the stated 2-adic setting; it need not be a
global vector of K. The inclusions at line 98 are read as non-strict.
