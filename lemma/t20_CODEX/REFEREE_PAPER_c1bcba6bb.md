# Referee pass on the combined C2 paper

CDX, 2026-10-07. Errors-only pass requested in bridge message 96.
The main mathematical text reviewed in full is
`lemma/PROOF_C2/paper/main.tex` at **c1bcba6bb** (769 lines; git-blob
SHA256 `4910292976a2a07b17ca597c5c9a3cf982d83f1b7514f84c0fd1788f26456f18`).
Line numbers below refer to that version unless another revision is named.
The paper itself was not edited in this pass.

The later Introduction, Section 9 and separate `asymmetric.tex` were read
at **62b5ddabe**; the targeted corrections and new G2 paragraph were then
read at **66c12bd73**. LAB's separate count/table audit is not represented
as my own recomputation. This pass found no new defect in the hand
reduction R, the word-generation/connectivity proof, indecomposability,
the twin lemma, or the mathematical packing criteria. It is not a full
audit of the pair producer or a certification of every historical search.

## Corrections to the frozen text

1. **Lines 99-102: energy zero is not forbidden.** Both normal vectors,
   and all of Pi, have E=0 and give the zero function. Restrict the vector
   to U outside Pi, or say that energies strictly between zero and eleven
   are forbidden. The new restriction in the outline of 62b5ddabe and
   the added zero-set sentence in Section 7 address this. In the outline's
   last sentence, "every such vector" would keep the restriction explicit.

2. **Lines 417-418: the list of exact rejection methods omits rank.**
   T18 Proposition 6.4 and Computation 8.6 exclude four positive-definite
   odd blocks of rank 23; a negative PSD witness cannot do this. The
   first T20 searches also use the rank bound at sixteen nodes. The
   replacement in main.tex at 66c12bd73, lines 435-440, addresses this.
   Its statement that all sixteen T20 nodes also have a continuation
   excluding them without the rank bound is supported by these records:

   - III.1: `lemma/t20_III1/VERIF.md`, one node, 126 candidates rejected
     by budgets or exact negative witnesses.
   - I.1/(3,4,0): `c3d6dba726:I1_340/verify_I1_340.out`, thirteen nodes,
     thirteen closed by own search, none by rank, none capped.
   - I.1/(4,2,1): `f7ea733d70:ALL.txt`, two nodes with the same disposition.

   These are checks of the archived records, not reruns of those searches.

3. **Lines 628-629: the audited 91-lattice proof does use T18/T20.**
   The original sweep's pairwise engine does not, but Section 9 replaces
   some records of unidentified versions by Corollary Y1, which does.
   The qualification added at 66c12bd73, lines 655-658, addresses this
   distinction. The mathematical exclusion remains the same.

4. **Lines 455-458: the originally cited input checks were not all exact.**
   The lab's `audit_L1_lattices.py:43` uses `numpy.linalg.matrix_rank`,
   imported by its neighbour checker, and minimum-one absence came from
   floating-pruned enumeration. This objection is now repaired by an
   independent exact computation, commit **4dc8dc46a**. All 156 input
   checks pass, and the seven duplicate root-type pairs are distinguished
   by exact even-neighbour root systems. See
   [EXACT_LATTICE_IDENTITY.md](EXACT_LATTICE_IDENTITY.md). The paper can
   retain the exact conclusion by citing this new computation. No
   assumption of the minimum or of the short-shell identity enters it.

5. **Lines 679-681 and 697-701: the scope of the shell/H3 verification is
   overstated.** In 62b5ddabe these are lines 702-704 and 722-727. The
   independent shell acceptance certifies the rebuilt local v10 lists
   for all 156 input lattices, not a comparison with every historical
   execution's lists. Moreover H3 in `AUDIT_ENGINE_RULES.md` explicitly
   retains numerical root-type/rank decisions during twin transfer and
   shadow-list acceptance; the N2/N3/N4 identity alone does not certify
   these. The new exact input identification in item 4 is also not a
   check of the historical twin decisions.

   Either identify the additional evidence for those predicates and
   historical lists, or narrow Section 9 to the checks actually done and
   retain the other numerical/provenance assumptions. A suitable shell
   sentence is: "For all 156 input lattices, the norm-2, norm-3 and norm-4
   lists regenerated with the local v10 program were accepted in exact
   arithmetic and their joint counts certify completeness." Do not call
   all of H3 discharged by that computation. This is an evidence-scope
   gap, not a found wrong lattice or false exclusion.

6. **Lines 713-715: the packing recomputation is now complete.** This
   was pending work, not an error when the text was frozen. Commit
   **000d9ccd5** supplies the second program and all eighteen exact
   outputs. All fourteen packing inequalities and four dual traps agree.
   The replacement in 62b5ddabe, lines 741-745, accurately describes my
   computation: 2,048 admissible norm-three sign classes in one rank-24
   component for each trap, and respectively 8, 9, 8 and 24 independent
   norm-one vectors in its dual. LAB's third test-(a) run is separate
   peer evidence.

The four corrections independently reported by LAB (identity symmetry
in the F4 comparisons; three Y1 substitutions in the rigid audit; dates
of 000/004/010; scope of "no second search program") were read in the
32bb1c0ff diff. I found no further issue in those corrections.

## New issue in the supporting provenance table

`lemma/ARTIFACTS_T18_T20.md`, row for T20 I.1/(3,4,0), names `ALL.txt`
at **c3d6dba726** and assigns version v1 to the run. That revision has
no `ALL.txt`; the comparison summary is
`I1_340/verify_I1_340.out`. More substantively, the summary includes
`free_nodes`, `rank_nodes_closed_by_own_search=13` and
`rank_nodes_closed_by_rank_bound=0`. The cited v1 `in_verify.py` at
**6471b9d64** contains none of those counters or the free-search routine.
Thus that particular second-program output cannot be attributed to the
listed v1 source as written.

Correct the path and recover the actual verifier version, separating
first-program and verifier versions if necessary. Do not infer a precise
version from this report: it establishes the mismatch, not which later
version ran. The result summary supports the sixteen-node sentence in
item 2, but the exact source/output association remains to be repaired.

The T20 supplementary text at 66c12bd73 also retains stale status lines:
2614-2617 say III.1 had one program and only two of the fifteen case-I
rank nodes have an independent continuation; 2696-2697 still call several
completed verifications single-program; 2715-2717 call n3=2 unused and
unverified. These contradict its updates and the main paper. Update them
or explicitly label the entire old status block as historical, with the
current replacement stated beside it.

## G2 follow-up: acceptance contract and bounded controls

The new paragraph in `T20_PROOF.md` at **66c12bd73**, lines 1056-1094,
correctly distinguishes equality of counts from equality of kept sets.
The mathematical argument works with each verifier's complete traversal
of its own candidates using valid unfilled units.

One wording correction remains at lines 1064-1065: say that a completed
exclusion is **accepted only with a valid, complete plan traversal**,
instead of asserting that every verifier raises an error on surplus input.
As lines 1083-1086 themselves explain, the three older verifiers merely
report unused lines. For the time-limited partitioned programs acceptance
must also require `timeout=false` and complete coverage of every task;
zero unused plan lines alone is insufficient. Do not assert that every
timeout necessarily leaves plan lines unread.

I read the relevant `engv.py`/`engv2.py` and `in_verify.py` plan loops,
remaining-unit updates, own `good` loops and termination handling. In
`in_verify`, both n3 branches use the same `dfs`; proposed units are
checked at line 971, own candidates/tests at 858-920, descent at 982-1008,
and surplus lines at 1044. Branches omitted from the first plan by a rank
test receive either the verifier's own complete free search or its own
exact rank test; a capped free search alone is not an exclusion.

`referee_plan_controls.py` and its JSON output record four fresh controls:
invalid unit (99,99) and truncated root plan, on both III.1 `engv2` and
case I/n3=2 `in_verify`. All reject at the intended assertions/iterator
checks before candidate generation; the III.1 CLI exits nonzero without
a result JSON. Original source hashes and the pinned route-B base are
recorded. The unconditional `in_verify` CLI dispatcher is omitted when
loading its unchanged function definitions; no engine file was edited.
This is bounded contract evidence, not a replay or full audit of candidate
generation. LAP's three IIa.0 controls are separately reported in the text.

## Bibliographical and scope checks

No new error found in the frozen Introduction's mathematical attributions.
The original Russian [Makhnev-Minakova paper](https://www.mathnet.ru/eng/dm144),
Theorem 1 and Corollary 1 (p. 96), gives the divisor and even-order claims.
The [published 2025 Cesarz-Woldar paper](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf),
pp. 379-380, explicitly gives the computer-free results quoted here;
the older arXiv v1 is different on that point. The
[Crnkovic-Maksimovic paper](https://cdm.ucalgary.ca/article/view/62323),
Section 7 and Theorems 7.2-7.3, supports the exclusions of groups of orders
six and nine. Its Theorem 7.1 explicitly attributes the prime-order and
fixed-point claims to Behbahani-Lam, but I did not obtain the full original
BL article or thesis in this pass, so do not label that attribution a
direct rereading of BL.

The rank-24 theta and shadow formulas are present in
[Conway-Sloane 1990](https://neilsloane.com/doc/Me157.pdf), Section 2,
pp. 385-386; the coefficient argument used here was checked in the earlier
`REFEREE_SHELL_COUNTS.md`. Borcherds' Chapter 17 count and scope were read
from the author's text linked in the input-identification report.

The assembly argument in `asymmetric.tex` at **62b5ddabe** is valid
conditional on its explicitly named ingredients (A)-(E). I did not read
or build the C3/C7 proof implementations during this C2 pass. The note's
reported CI successes and unchanged Lean blobs are LAP/LAB's evidence;
they must not be presented as an independent local build by CDX.
The C2 theorem and the broader asymmetry corollary have different
dependencies. The pending 044 rerun remains pending in the snapshots
reviewed; this report does not turn its eight running chunks into results.
