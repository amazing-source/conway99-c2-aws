# Mathematical referee report on T20_PROOF.md

Codex, 2026-10-07. First pass of board item D3.

Reviewed text: commit `8510844a4a7294795d1307e1209b502acb95afef`, as present
on master `124ef688c` at the start of this review. SHA-256 of the reviewed
file: `8e223bfc2f4b0ccac5662ae3e27c0672e57f91d6515365e8598c09894353b487`.
All line references below refer to that version (2718 lines).

## Verdict and scope

The hand arguments in sections 1-10 support **Theorem 10.1 conditional on
the stated Computations**. I found one repairable sign error and a mismatch
between the documented split level and the mathematical level. I found no
hand argument that would invalidate the reduction to case I, n3=2, with
profiles (3,4,0) or (4,2,1). This is not a certification of the enumeration
implementations or of their complete run provenance.

Section 10 correctly stops at that reduction. It does not prove T20, and
it does not by itself exclude all 156 envelopes. The open section 9.B is
an explicitly declared remaining case, not an unnoticed gap. The lattice
dictionary, the earlier small-norm results, the per-pair certificates and
the final envelope conversion were outside this review.

I read all the hand proofs, the mathematical models, the completeness and
symmetry arguments, the computation statements and their caveats. I did not
read the first search engines or rerun the large searches. I am the author
of several lemmas in section 9.6 and of the independent route-A checker;
the rereading of those lemmas is therefore not a new independent authorship
check. The earlier lab review of them remains the other-reader check.

## Errors, in order of consequence

### E1. Sign error in the proof of Corollary 5.2 (line 744)

The sentence for d=4 says `0 = -q(z) + (a sum of non-negative terms)` and
then concludes that both terms vanish. That displayed equality has the
wrong sign. Equation (5.2) gives

    sum_{w ~ z, w outside S} d(w) = -q(z),

or equivalently `0 = q(z) + sum d(w)`. Since both terms on the right of
the latter equality are nonnegative, both vanish. This repairs the proof
immediately; the statement and all later uses remain valid.

### E2. Split parameter 3 is described as mathematical level 3

References: lines 1182-1183, 1202-1204, 2605-2606.

The text defines level t as t added X2 orbits (lines 998-1003). Its own
tables give 881/2156 nodes at level 3 and 7109/21165 at level 4 for
III.0/III.1. The prose nevertheless calls the 7109/21165 tasks a split at
level 3. The stored III.1 part-zero JSON confirms `split_depth: 3` and
`tasks_total: 21165`, with the part's selected tasks counted at index 4 of
`visited`. Thus the command's parameter is the level of the parents being
split; the task roots have four placed orbits.

Keep the recorded command parameter 3, but distinguish it from the level
of the task roots. This is a documentation correction, not evidence of
missing tasks or a change to the reported totals.

## Gaps in the computational audit and its wording

### G1. Source/output provenance and durable coverage remain unverified

References: lines 1213-1217, 2065-2073, 2494-2508, appendix A.3 and A.5.

The text explicitly admits that some per-base outputs and plan files are
only in session scratch directories, and that the source versions that
produced stored outputs were not verified. The inspected first III.1
result JSON records the engine name, task-list hash and counts, but not a
source digest. The nine cloud cases have substantially better described
coverage checks; the three laptop cases still rely on the working report
for their per-base accounting in this text.

This is a reproducibility gap between a mathematically exhaustive model
and the assertion that a particular completed execution implemented it.
It does not refute any count. Before the final exclusion is signed off,
archive or immutably identify the missing per-base results/plans, the
precise source revision, input-list hashes, commands and completion checks.
If an old source/result link cannot be recovered, identify a completed
replacement verification rather than silently attributing that result to
the current source tree. No wholesale rerun is requested by this report.

### G2. Plan-following needs an explicit contract; equal counts do not identify the kept decisions

References: lines 45-49, 1187-1192, 1401-1409, 2075-2082, 2482-2486.

Lemma 6.5 correctly allows any choice of the next **unfilled** unit. Thus
reading that choice from a first program's plan is mathematically sound
provided the second program, in its own current state:

1. checks that the proposed unit has positive remaining multiplicity;
2. generates every candidate of that unit using its own model/tests;
3. traverses every candidate that its own tests keep;
4. aborts on malformed/truncated input and never treats such an abort as
   a completed exclusion.

The text should state these as the verifier contract and cite where they
are checked. I have not inspected the engines to establish this contract.
The supplied III.1 report records negative controls for altered kept counts
and a deleted plan line, but does not report an invalid/already-filled-unit
control. That additional control would directly exercise the essential
first condition.

The phrase at lines 2483-2485 that counts verify the individual
kept/rejected decisions node by node is too strong: equally sized kept
sets need not contain the same candidates. This does **not** require
identical kept sets to prove the exclusion. A complete second traversal
of its own tree with valid unit choices suffices by Lemma 6.5. Say that
explicitly, and report equal counts as a cross-check rather than an
identity certificate for the states.

**Follow-up, bridge message 48 (lab Claude, 12:45 UTC).** The lab reviewer
reports checking the contract in `t20_R3_I/in_verify.py` for case I:
`assert U0 in remaining` at line 670; positive remaining multiplicities
maintained at lines 423-427 and 622-626; independent `gen_cands` and
`test_cands`, followed by recursion over the verifier's own `good` list at
lines 671-711; `next(plan)`, the depth assertion, and `assert left == 0`
(line 743) reject truncated, misaligned or surplus plan input. An assertion
aborts the part rather than certifying it. These references are the lab
reviewer's code inspection, **not an additional code audit by me**.

Accordingly, the case-I n3=0 implementation contract now has a positive
peer inspection behind it. What remains for this item is to put the
contract and references in the proof text, inspect the corresponding
III.1 and n3=2 verifiers, and record the proposed invalid-unit negative
control. The statement about equal counts not identifying kept sets is
unchanged. This follow-up does not certify an unfinished n3=2 run.

### G3. Preserve the actual scope of independence for III.1

The update banner at lines 4-6 should carry the qualification from
`t20_III1/VERIF.md`: the verification independently checks budgets, PSD
and bookkeeping, but shares `cases.py` and parts of the enumeration
skeleton/candidate-generation loops. Its own report says this explicitly.
Accordingly, describe it as a second verification implementation with
those shared components, rather than implying two independently authored
enumerations of the whole model. The same care already appears for III.0
at lines 1198-1200.

This is a limitation of the verification claim, not a newly discovered
counterexample. The symmetry argument in Lemma 7.3 itself is sound.

## Unclear or stale passages

- **C1: status is split between the banner and the body.** The III.1 and
  I.1/(3,4,0) verification updates in lines 3-11 must eventually be folded
  into sections 0, 7, 9.A and 10 and appendix A. Statements that n3=2 has
  no second program (lines 55, 2113, 2333, 2389) should now say that an
  independently written route-A checker exists and matches all base
  counts, but no complete second exclusion exists. Route A has been
  abandoned on cost; the route-B implementation is a separate pending
  task. None of these status corrections closes section 9.B.
- **C2: paths and document format.** Line 28 still calls this file `.txt`.
  The transcription script referred to as being in the document's folder
  (lines 614-615, 2521-2525, 2592) is actually at
  `lemma/t20_PROOF/_check_text_data.py`, not alongside
  `lemma/T20_PROOF.md`. Use the actual path.
- **C3: labelled versus unlabelled determined bases.** In Lemmas 8.7 and
  9.18, unordered pair types determine the base up to freely renaming the
  inner vertices. This suffices for the proof, but a sentence fixing the
  order of the types and the representative row of each unordered type
  would reconcile it with the explicitly labelled definition at lines
  871-875. All these renamings commute with sigma and lose no configuration.

## Positive checks and independent small data check

The following steps were re-derived, rather than accepted from their labels:

- The involution facts and mate common-neighbour argument (section 2).
- All four square partitions of 10 and the elimination of the value 2
  using the equality case of Lemma 3.1 (section 3).
- The three support counts, parity law, mixed inner/outer plus-edge
  contradiction, K4 incidence model, and orbit-size exhaustion of the
  support representatives (section 4).
- G0, class sizes, the X0-neighbour bounds and unit multiplicities
  (section 5), subject to the local sign repair E1.
- Both spectral projectors, both sigma rank bounds, the distinction
  between partial-graph budget tests and determined-subgraph PSD tests,
  the true-configuration induction, and the stabilizer argument of
  Lemma 7.3. Stabilizers fixing N0 sets preserve both rows because they
  commute with sigma; using a smaller pointwise stabilizer is safe.
- The case II reductions, the 180 W-type graphs, and all caps in the
  three closed-case models. In particular the weaker program caps K4
  are still necessary conditions; weakening them does not harm an
  exhaustive exclusion.
- All section 9 hand lemmas, including n3 in {0,2}, profile exclusion,
  cells, Q0/Q2, isolation, the extremal-edge proof, and the triangle
  attachment. The alpha and epsilon terms in (9.10)-(9.11) cancel as
  claimed. The stronger bound a0(s)<=4 in Lemma 9.23 is valid.
- The conditional dual-norm rule of Lemma 10.2: N is integral, its
  residues are {0,3,5,6} modulo 7, so excluding positive N<10 requires
  only E14. The text correctly does not use this conditional rule in
  its closed-case proof.

`referee_text_checks.py` reads the edge lists printed in the reviewed
text. It imports none of the enumeration engines and independently checks:

- all nine representatives satisfy the support eigen-equation and budgets;
- their automorphism orders are 16,4,10,4,4,20; 1; 3,4;
- every displayed unit list and its multiplicities agree with direct
  common-neighbour counts;
- the orbit-size arithmetic for the classification totals agrees;
- every row sum and total of the twelve-case stage-1/stage-2 tables agrees:
  17396042 configurations, 3130401 orbits, 615405 bases, 15762181 search
  nodes, and 15 rank rejections in the first computation.

The output is `referee_text_checks.json`, including the reviewed text's
SHA-256. This adds an independently authored check of the nine printed
automorphism orders; it is **not** a third exhaustive support enumeration
and does not validate the large search totals beyond their arithmetic.
Unused characteristic polynomials and graph-name identifications were
not checked.

## Next review boundary

The current mathematical pass is complete, with the repairs and audit
conditions above. When section 9.B is replaced by a completed route-B
argument and its artifacts, that addition and the resulting section-10
conclusion require a new pass. This report must not be cited as approval
of an unwritten n3=2 exclusion or of the final 156-envelope conversion.
