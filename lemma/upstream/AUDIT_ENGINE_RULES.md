# Section B: audit of the frame-engine rules

Reviewer: CDX, 2026-10-07. This is the section-B deliverable requested with
`AUDIT_REDUCTION.md`, following the single section-A pass in
`../t20_CODEX/REFEREE_REDUCTION.md`. No frame search or solver was run, and
no producer, engine, queue or historical result was modified. The later
T16 certificate verification is recorded separately below.

**The mathematical rules below do not use g or the index [Nmax:N].** The
replacement of `g in {18,20}` by A.4 does not invalidate them. This is
**not an unconditional validation of the executable or of the 156 exclusions**:
the completeness and certification holes below must be addressed, or shown
irrelevant to the covering records. In particular, a mathematically valid
constraint does not certify a solver's negative answer.

## Sources and scope

Line references `FD:` refer to `scripts/frame_dfs_next.py` in the local
`C:/home/researcher/Desktop/c2_experimental/c2_cloud_run_v10` package, SHA256
`1591aeeac9c0be5c529a2ff492e66d390138cd221cba2ab67aac81748de9b759`.
`HS`, `TT`, `PB`, `YP`, `Y2`, `EP` denote respectively the package's
`scripts/hstage_stream_next.py`, `scripts/twin_transfer.py`,
`scripts/pair_budget.py`, `c1/code/y_pairs.py`, `c1/code/y2_engine.py`,
`c1/code/envelope_pack.py`. Other local references are relative to
`C:/home/researcher/Desktop/c2_experimental`:

- `SHELL`: `external_runs/shell_theorems/conway99_shell_theorems/PROOFS.md`, sections 4, 5, 5.2 and 7 read for the twin rules. Its theta/moment theorems were **not** audited in this pass.
- `FLEX`: `external_runs/flex_boundary/conway99_flex_boundary/README.md`, sections 1-3 read for boundary points and endpoint confinement.
- `SYM2`: `scripts/make_frame_dfs_next.py`, proof in its opening docstring; `SYM3`: `scripts/sym3_patch.py`, opening proof.
- `CB`: `scripts/component_budget.py`; `EB`: `scripts/exact_budget.py`, read, not executed.
- `R`: section A of `AUDIT_REDUCTION.md` at master `c10bb83e1`; the associated referee report records its hash.

`AUDIT_ENGINE_SOURCES.json` pins the inspected files. The full DFS bitset
implementation, all numerical bounds, producer coverage, Gram-matrix identities,
historical environment switches and result provenance have not received a
complete executable audit here. Sections C-E retain those responsibilities.
`OK` below means the **stated mathematical rule** follows from the hypotheses;
it is subject to candidate-list completeness and correct arithmetic.

## One row per rule

All rows were reread by **CDX** in this pass. A proof may be the direct
derivation in the row; longer supporting arguments are below. No row asserts
an uninspected original C1 note was reread.

| Rule / code location | Statement and why it follows from R | Written proof / reviewer / status |
|---|---|---|
| Normal norms and orthogonality; FD:186-187, Y2:191 | Norms 7 and mutual orthogonality are R-i. Early consumer traps run before these assertions, so input certification remains necessary. | R-i; CDX, OK rule; certificate caveat already in `../BRIDGE.md`. |
| Root pair filter; YP header, Y2:201-203 | For a root a, E(a)=14-Y>=8, hence Y<=6 and Y in {0,1,2,4,5}; neither root is in J, whose minimum is 7. | R-vi; CDX, OK. |
| Norm-three pair filter; YP header, Y2:197-199 | E(x)=21-Y>=8 gives Y<=13: each height is at most 3, and both cannot be 3. | R-vi; CDX, OK. |
| New-root pair filter; FD:188-190, Y2:192-195 | At a shadow root beta, the two y and 42 u have half-odd pairings. The baseline energy is 11 of 14; one absolute 3/2 costs 2, and absolute 5/2 costs 6. | R-v and A.8; CDX, OK. |
| Exact dual trap represented by root/norm-three filters | A nonzero short vector of K*=proj_K U has a lift with normal heights in [-3,3], of norm <8/7+18/7<4; it is a root or norm-three vector. | R-vi and primitive J; SHELL section 4, line 234; CDX, OK. |
| Weyl dominance / diagram subgroup reduction | Reflections in norm-two roots preserve integral U; a chamber representative and the stabilizer chamber lose no orbit. Only checked lattice automorphisms may be used for further quotienting. | R is isometry invariant; `AUDIT_REDUCTION.md` C, YP/Y2 headers; CDX, OK principle, enumeration coverage belongs to C. |
| Swap; HS:44-48,86-89 | R is symmetric in the two normals. Root energy and the sorted two shadow-coset hit counts are isometry/sign invariants. Retain I(y1)<=I(y2), with the opposite order covered by the complete producer. | `AUDIT_REDUCTION.md` C(3); CDX, OK conditional on C's coverage. |
| Characteristic trap; FD:1415-1428 | For characteristic z of norm 16, 42 odd word squares and the parity of the h contribution give E(z)>=46, hence Y<=66. | R-v; R A.8:149-150; CDX, OK. |
| Optional MIN97 / Y=13; FD:1431-1453 | A norm-three witness with Y=13 has E=8 and gives an odd integer eigenfunction of norm 16. **R-vi allows E=8**; excluding it additionally requires T16. | R-vii plus the separately reviewed cube/Wagner proof; CDX, OK with T16, see H5 and `../t20_CODEX/REFEREE_T16_PROOF.md`. |
| Candidate h/u norms and perpendicularity; FD:191-194 | The chosen h must be among norm-four vectors perpendicular to y; the u among norm-three vectors perpendicular to y. | R-i, R-ii; CDX, OK; shell completeness H3. |
| h-admissibility at shadow roots; FD:192-193 | The remaining energy 3 at beta allows only integer h heights 0,+/-1. | R-v, A.8; CDX, OK. |
| Candidate sign representatives; FD:134-140 | Changing the sign of a word is a choice of orbit representative; changing an h sign interchanges Same/Opp labels. Each D7 pair still has one line of each kind. | R-ii..iv up to these gauge choices; CDX, OK. |
| Exact/flex coverage targets; FD:199-204 | A y-hit has h coverage 1 and no word hitter; with no eligible word hitter coverage is 3; otherwise it is 1 or 3. | R-v, A.8; CDX, OK. |
| Boundary points; FD:1456-1472 | Characteristic z with norm 16 and Y=58 satisfies 4 sum a_i^2+sum(b_u^2-1)=12. Thus h coverage is 3 with no hitter, or 1 with exactly one word of absolute height 3. Any witness subset is safe. | R-v; FLEX section 2; CDX, OK. |
| Optional WPRUNE; FD:1473-1490 | For Y>=50, 4 sum a_i^2+sum(b_u^2-1)=70-Y, with sum a_i^2 odd and >=1: no word height >=5; h height bounds 2 at Y=58 and 4 at Y=50 are safe (larger infeasible Y cannot host a frame). | R-v and parity as A.8; code comment; CDX, OK. |
| Endpoint confinement, signed or unsigned; FD:1533-1544 | If u hits a point s, both s and s-u have one signed-unit h footprint; their difference is u's D7 footprint. A covering h must be one of its two endpoints, with the stated sign. | R-iii, R-v; FLEX section 3; CDX, OK. |
| Pairwise h compatibility; FD:1298-1325,1370-1412 | Chosen h are orthogonal, cannot share an exact target-1 point, and require nonempty Same and Opp word cells for their pair. | R-ii, R-iii and A.8; code docstrings; CDX, OK. |
| Word validity / Lemma U+; FD:1016-1020,1193-1203 | Delete words with forbidden h products, more than two endpoints, a y-hit, or a hit at a point already covered twice. Such violations cannot be repaired by adding h. | R-iii, A.8 and boundary lemma; CDX, OK. |
| Empty cells; FD:1205-1216 (and parallel kernels) | Each chosen h pair needs a Same and an Opp word, orthogonal to all other chosen h; deleting a branch with either cell empty is necessary. | R-iii, the complete D7 column set; CDX, OK. |
| Common-zero and star counts; FD:1217-1226 | With l h remaining, l(l-1) distinct words have both endpoints among them; each chosen h needs 2l words with its other endpoint still unchosen. | R-iii; CDX, OK. |
| Coverage capacity and saturation; FD:1079-1103,1236-1245 | Remaining required covers cannot exceed remaining h or candidates through the point; saturated points forbid further covering h. A flex point without a still-valid hitter must reach 3. | A.8/boundary and monotone word validity; CDX, OK. |
| Flex leaf hitter; FD:1052-1066 | Coverage 1 needs an actual word hitter with exactly two h endpoints; if none remains the leaf cannot extend. | R-iii, A.8/boundary; CDX, OK. |
| General branching / sibling deletion; FD:1133-1137,1175-1188,1248-1253 | Branch on a required point; every completion has a first chosen remaining member through it. If no point is pending, branch on all remaining h. Delete only explored sibling candidates. | Finite subset enumeration and the required-cover rules; CDX, OK principle. |
| Generic non-flex branching; FD:349-365 | If no point is pending before depth 7, best stays -1 but through[best] is still used. This needs an extra impossibility/precondition proof. | No such proof found in inspected sources; CDX, **HOLE H2**. |
| Reflection symmetry at depth 0; FD:1551-1575 | Fix y1,y2 and an exact target-1 point. Its unique covering h can be moved to a representative of its reflection orbit; exact coordinate checks prevent false hash edges. | R is isometry invariant; FD comment and SYM2 preamble; CDX, OK. |
| Reflection symmetry at depth 1; FD:1578-1601 and dfs_general_u2 | Also fix the first h and an uncovered target-1 point; the same unique-cover argument applies. Earlier target-1 siblings cannot occur in a completion containing the selected h. | SYM2 opening proof; CDX, OK. |
| Reflection symmetry at later depths; FD:1106-1174,1246 | Only along paths previously branching at target-1 points, reflections fixing all chosen h and the next such point preserve completions. symok is disabled after other branchings. Missing reflection edges only refine orbits. | SYM3 opening proof; CDX, OK. |
| Lemma Z; FD:255-258,449-452 | Sum R-iv: 3 sum h is an even integral combination of u, since every C column has even sum. Hence sum h is in 2U. Sign changes of h do not affect this. | R-iii, R-iv; direct proof here; CDX, OK. |
| Local star sums; FD:252-312,433-507 | For each h, its 12 endpoint words oriented to pair +1 must sum to 3h. Partial shadow-height sums must reach the target with remaining odd increments +/-1 and at most one additional +/-2 at a flex point. | R-iv and A.8/boundary; FD docstrings; CDX, OK. |
| Joint cells, distinct words and hitter counts; FD:1659-1706 | Choose one word per Same/Opp cell, 42 distinct lines, with all seven star equations and exactly one hitter on each coverage-1 flex point. | R-iii, R-iv, A.8; CDX, OK constraints; enumeration cap is **HOLE H1**. |
| Final T identity and frame operator; FD:1709-1722 | With word Gram G_u=3I-T, polarized F gives G_u^2+C^t C=7G_u, i.e. T^2+T=12I-C^t C. Coefficient outer products must sum to 7G^-1. | R-v and R-iii; CDX, OK. |
| Node and stored-leaf limits; FD:1049,1077,1255,1640,1653 | A node stop yields INCOMPLETE; leaf overflow raises an assertion and the consumer records INVALID. Neither is an exclusion. This does not cover the separate joint cap. | Code control flow, HS assertion handler; CDX, OK contract under normal assertions. |
| Lattice component budgets; CB header and model | Trace F on each root component and its perpendicular space: total projected energy is 7 times dimension. Candidate type counts and relaxed nonnegative normal energies must meet these budgets; root normal energy <=3 rank follows by summing Y(root)<=6. | R-v, R-vi; CB opening proof; CDX, OK model, solver/certificate **HOLE H4**. |
| Pair root-class budgets; PB pair_test | Sum F over roots sharing (component,Y): h/u energy equals (14-Y) times the class size; trace the remaining orthogonal space and require 42 u,7 h. | R-v, R-vi; PB docstring; CDX, OK model, solver/certificate **HOLE H4**. |
| Packing and packing-admissible words; EP:80-132 | The 42 actual word hit sets are disjoint in each shadow coset, so their hit counts fit. The 42 smallest counts give a lower bound; fixing one candidate uses the other 41 smallest. Equality of the two coset hit counts follows by beta -> x-beta after orienting a hit positively. | R-v, A.8; EP header and derivation below; CDX, OK rule, numerical completeness H3. |
| Packing connectivity/span/dual trap; EP:133-164 | The actual word graph is connected; all words must lie in one candidate component of rank >=22. Every sufficiently short dual vector of its integer span lies in the normal plane; its span plus the perpendicular space has dimension <=2. | R-ii..vii, R A.5; EP comments and algebra below; CDX, OK mathematical rule. |
| Twin construction and transfer; TT, HS:90-95 | Replacing the normal residue gluing by R=[[2,2],[-2,2]] preserves K and all frame vectors, yields another odd unimodular U with no units. Transfer is valid only when **all** classes of the computed root type are excluded. | R-i, R-v, R-vi; SHELL sections 4,5,7; CDX, OK conditional on certified target exclusions. |
| Twin root catalogue; TT:31-43 | Reduced normal residues transform precisely (norm,Y)=(2,0),(2,5),(3,8),(3,9),(4,18) into twin roots; every twin root has Y in {0,1,2,4,5}. | R-vi, primitive J; SHELL section 5.2; CDX, OK mathematics; numeric root/rank classification is subject to H3. |
| Twin deferral; HS:95 | Strictly greater root count gives a well-founded dependency. A deferred pair is excluded only after every possible target class is excluded. chunk_done records traversal, not discharge of that dependency. | Twin theorem; SHELL section 7; CDX, OK conditional rule. |
| Twin canonical rule; HS:96-100 | Only for a root type unique in the 156-list, move to its twin pair when the intrinsic normal/root key strictly decreases. R^2 mod7 is a signed normal permutation, so twinning back cannot produce an endless descent. | SHELL section 5.1 plus HS kkey/own_unique checks; CDX, OK conditional on D's identification and C's coverage. |

## Algebra supporting the packing row

These are explicit checks of the reductions used by the source, not additional
unannounced hypotheses. Write M=Z-span of the 42 actual words. R-iv gives
3h_i in M. Polarizing F and applying it to a word gives
`sum_i C_io h_i = -4u_o + sum_{p != o}(u_o,u_p)u_p` in M.
The two D7 columns for {i,j} therefore give h_i+h_j and h_i-h_j in M,
hence 2h_i in M and then h_i in M. Thus M is the whole 49-vector frame
lattice N. This step is necessary: integrality on only the words must not
silently be identified with integrality on all 49 generators.

If its word graph were disconnected, its Gram matrix would split into
orthogonal blocks. The T identity would force C_A^t C_B=0 between different
components. D7 root lines on pairs with exactly one shared endpoint have
nonzero inner product. That adjacency graph on all 42 D7 lines is connected
(also connecting the plus and minus lines via a third endpoint), a contradiction.

For a candidate component M' containing N, a vector w integral on M'
projects to N* in the frame space. If ||w||^2<8/7, A.5 forces this projection
to vanish. The short dual vectors and span(M')^perp therefore all lie in
the two-dimensional normal plane. Their spans are orthogonal, giving the
dimension test used by EP. No determinant/index restriction on N is used.

For packing, orient a hit beta of a norm-three x so (x,beta)=3/2.
Then x-beta is a shadow root in the other shadow coset, also pairing 3/2
with x; this is an involutive bijection of hit lines. The actual packing
inequality needs these directly counted hits, not the optional theta
identity `m=r/8-E`. EP records that latter identity but does not assert it.

## Holes and required evidence

### H1. Silent cap on joint solutions

FD:1659 sets `cap=1000`; FD:1688 stops recursing after that many joint-star
solutions. `search` (1643-1655) checks only those solutions with `full_check`
and can return `EXCLUDED ... (F) fails` with `complete=True`. The first 1000
failures do not exclude a later solution. No bound of 1000 is proved in
the inspected source, and no incomplete flag is returned by `joint`.
The stored `joint_star_sums` field counts leaves with at least one joint
solution, not how many solutions were enumerated at each leaf.

This is a hole in the general executable's completeness contract, not a
claim that a covering run hit the cap. Archived evidence that every relevant
pair died before joint enumeration, or that every entered joint call was
exhausted below the cap, can establish irrelevance for particular records.
An engine repair alone would not retrospectively validate old records.

**Follow-up, LAB bridge message 52 (2026-10-07 13:33 UTC): not exercised
according to LAB's census.** LAB reports checking 17,676 stream/Golay
record files, 356 lab-local result files and 57 O24 class records, with
zero occurrences of the only affected exclusion verdict, `joint star sums,
but (F) fails`. The reported joint-stage exclusions are twelve pairs with
an empty joint list (eight in 001, four in 002); an empty list cannot have
hit the cap. LAB's importer now classifies any `but (F) fails` verdict as
`other`, refusing it, in commit `1dde18702`; CDX inspected that guard.
The census itself is peer evidence, not an independent CDX recount, and
its durable output/path has been requested. Thus H1 is a real code hole
reported unexercised in the stored exclusions, with a guard against future
acceptance; it is not evidence that those exclusions are wrong.

### H2. Generic kernel assumes a pending point exists

FD:349 initializes `best=-1`; only a positive remaining target changes it.
FD:365 nevertheless reads `through[best]`, even if all targets are already
met and fewer than seven h are chosen. The general kernels correctly have
an all-candidates fallback. Saturation has normally removed all candidates
through the final point, so this generic branch may terminate early.

No inspected proof shows that a genuine completion cannot have remaining
h with zero footprint on all supplied points. The generic kernel is selected
by absence of flex points (FD:1548,1604), which is not itself that proof.
A proof of the additional precondition, or recorded absence of zero-footprint
h candidates in each relevant run, could discharge this hole. No actual
graph or missed genuine frame is asserted here.

**Follow-up, message 52: H2 remains open, with reduced scope.** LAB derives
the shadow-root energy operator from the two even neighbours' root
operators. For norm-four h, the sum over signed new roots of (beta,h)^2 is
`8(H1+H2)-4 sum_j h_j ||P_j h||^2 >= 8|H1-H2|`. CDX checked this algebra
and the equality criterion: zero footprint requires H1=H2=H and h entirely
in components of U with Coxeter number H. The expression counts nonzero
pairings only for admissible h (all nonzero heights have absolute value 1);
the zero criterion holds without that restriction. LAB's table calculation
therefore rules out zero footprints for 129 lattices. CDX has not independently
recomputed the table or the Niemeier input data.

LAB's stated potentially affected list has 27 IDs:
`001,003,006,007,014,022,023,024,026,027,028,037,049,050,052,053,077,079,080,101,103,104,105,117,137,138,152`.
Removing the two said to be excluded without the engine, 117 and 152,
leaves **25**, not the 24 stated in that message. Message 56 corrects this:
001 (Golay) was omitted from that count and is audited separately.
The reported zero exposed pairs among 63,825 sampled searched pairs is
sampling, not a proof. LAB proposes complete pair-stream exposure checks
and general-kernel searches for the exposed cases; no such run was performed
or authorized by CDX through this report.

**Follow-up, message 56:** `measures/AUDIT_RIGID_MANIFEST_2026-10-07.json`
now records the non-Golay jobs, and `q/audit_rigid.py` provides the exposure
check and general-kernel re-search. CDX read that consumer but did not run it.
The archived `measures/AUDIT_RIGID_golay_001.json` reports a complete stream
of 117,068 pairs: 117,050 general, 18 rigid and exposed. All 18 recorded
rechecks exit at the characteristic-vector trap before the kernel. CDX
checked these counts and verdicts in the JSON; the recorded engine hash
prefix matches the inspected engine. This is evidence for 001, not an
independent replay or a completion of the remaining 24 lattice audits.
H2 remains open globally.

**Follow-up, message 68: archived coverage, not a new engine replay.** CDX
read `measures/AUDIT_COVERAGE_2026-10-07.json` and the coverage collector
archived at `q/tools/lab_2026-10-07/audit_coverage.py`. The report records
22 of the 25 lattices covered; 003, 022 and 026 remain incomplete. Every
entry has `exposed_not_excluded_again=0`. For the twelve complete plan
entries using neither fixed-normal certificates nor overlapping chunks,
the recorded audited pair totals equal the sweep totals. These are checks
of the archived report, not independently regenerated streams or searches.

For **003**, 174 of 182 first-normal representatives have accepted audit
files (`stream_ok && ok`); five more, `[157,162,174,176,181]`, are disposed
of by the separately checked fixed-normal certificate, **conditional on
T18 and T20**. The remaining representatives are `[2,3,180]`. The report
keeps these dispositions separate: it does not invent audit files or pair
counts for a theorem-covered representative. Its 17,279,427 actually
audited pairs include 313 exposed pairs, all recorded as re-excluded.
The 172 selected files can cover 174 representatives because a chunk may
contain several representatives. This H2 audit coverage is distinct from
the complete first-normal coverage of the original 003 sweep.

The collector checks coverage of the plan's residue-class representatives;
for identity-based streams it requires all chunks from one source. It
does not itself certify the provenance of every input/plan/engine used by
those files, or the validity of every engine verdict. Those obligations
and the other holes in this report remain. The reported engine hash prefix
is `1591aeeac9c0be5c`, agreeing with the inspected engine. No jobs, manifests,
or exclusion-tracker records were changed by this review.

Snapshot SHA256 pins (file bytes):

- Coverage report, LF checkout: `65f13c00438f1923b9cbe1bc1ec1ee72af5c53fe48c4ddc679f994e98ec74fe4`.
  The lab's CRLF copy has SHA256
  `720b7fd152026441d86d0bb961c99127fede220990c5fefde8389a1c2ed20738`;
  the texts agree after CRLF-to-LF normalization.
- Archived collector: `a957667ea0e10ed1b46cebb689b0892467647a3a6012046d92f6063f7cf4c856`.

### H3. Exhaustive numerical catalogues are not certified by exact acceptance

FD:69-131 prunes Fincke-Pohst branches with floating Cholesky/LDL data and
fixed tolerances, then checks each returned vector's norm exactly. That
proves acceptance, not exhaustiveness. FD:153-154 checks norm-three and
shadow-root counts; it does **not** check completeness of X4, the h-candidate
shell. SHELL section 8 documents count certification for a 078 archive,
not all inputs used by the campaign. The numerical rank/root-type operations
in TT also need exact or certified evidence when used for transfers.

Thus the formal completeness justification is missing from the inspected
engine alone. Exact shell/count certificates for every relevant input,
or a certified enclosing enumeration, could close it without redoing all
frame searches. No vector actually missed by floating arithmetic was found
or claimed. Fast floating dot products likewise need their stated
small-integer bound or an exact comparison for the used data.

LAB confirms the missing norm-four assertion in message 52 and is looking
for complete shell-count certification. SHELL section 1.1 gives the claimed
count `49128-12r` for norm-four lines; its theta derivation was outside this
audit, and agreement with that count has not been checked here for every
used lattice.

**Follow-up, message 56:** LAB archived
`measures/SHELL_COUNTS_2026-10-07.json` and reports exact norm checks on the
engine's returned norm-four vectors. CDX read all 156 entries (000-155)
and checked that each has `N3=4096`, `ok=true`, and
`N4=expected_N4=98256-24*N2`, the signed version of the cited line count.
Thus the recorded counts agree for all 156, rather than just the earlier
078 example. This resolves the missing norm-four count comparison **at the
level of the archived result**, subject to the theta count, distinctness of
the enumerated vectors and provenance tying the measured input/source to
the covering runs. CDX did not re-enumerate these shells or audit the theta
derivation; the measurement script was not found in the inspected q/measures
sources. This evidence does not by itself certify every floating dot product
or numerical rank/root-type decision mentioned above.

### H4. Budget model versus negative solver verdict

PB returns `EXCLUDED (pair budget)` solely for HiGHS `status==2`; CB makes
the same inference. These necessary integer/rational models are correct,
but the inspected calls produce no exact infeasibility certificate.
`FD_PREBUDGET` is opt-in, so first establish whether any covering record
relied on it. For lattice-level budgets, EB implements an exact finite
enumeration of a weaker necessary condition; its code is present, but this
pass has not validated a complete run or its type-table provenance for 143.
That missing evidence must not be replaced by the solver's status string.
Nothing was run during this audit, including EB (whose import also executes CB).

Message 52 reports 12,620 `EXCLUDED (pair budget)` pairs in lab-local files
and none in the cloud records LAB counted. Thus this issue is not merely a
question about an unused option. LAB is checking whether exact re-checks
exist; CDX has not validated them, and H4 remains open.

### H5. The 9/7 rule needs a separate support-16 theorem

R and A.5 give 8/7, not 9/7. R-vii turns the Y=13 norm-three witness into
a norm-16 eigenfunction; its exclusion is exactly the additional cube/Wagner
result cited by FD:1432 and `../BRIDGE.md`. This pass did not referee that
proof. Record it as a separate reviewed dependency before counting any
`FD_MIN97=1` or corresponding quick-deferral exclusion. This is not a
new objection to the already stated bridge dependency, nor evidence of an
incorrect cube/Wagner theorem.

**Follow-up, message 56: separate T16 referee pass completed.** See
`../t20_CODEX/REFEREE_T16_PROOF.md`. No blocking mathematical error was found
in the hand proof or coverage sources. A fresh exact check validated all
240 A and 32 B certificate obstructions, including a necessary Hall-witness
membership check omitted by the received verifier. All shipped witnesses
satisfy that check; the verifier repair and an index wording correction are
recorded in the report. H5's separate-dependency requirement is discharged
by T16 plus this review; the rule still does not follow from R alone.

## Answer to the index question

No inspected rule requires `g=18`, `g=20`, or `[Nmax:N]` equal to 1 or 7.
The determinant 49 of the **primitive normal complement** follows from
unimodularity of U and primitive J=7I2. It is used in the twin mathematics,
not as a restriction on the original frame lattice. Primitivity and
the same lower dual bound follow from R. Retaining the holes above is
compatible with accepting the new all-g reduction.
