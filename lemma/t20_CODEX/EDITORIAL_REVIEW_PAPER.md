# Editorial comparison of the C2 paper and asymmetry note

CDX, 7 October 2026. Concrete review of **9d9094241**, not e22cfc57f.
Line numbers below refer to that frozen TeX source. Estimates are lines of
typeset prose, not additional pages. This is an editorial review, not a new
mathematical certification. No research computation or recertification was
launched; no paper source was edited or made public.

**Answer now:** yes, the comparison is done to the bounded extent stated
below. The draft already has an introduction, outline, standard references,
MSC, keywords, two useful figures, a methods table, computing environment,
error discussion and concluding remarks. Do not add these a second time.
The main remaining improvements are precision of the claims, the reader's
route through the computational argument, and a concise account of what is
independently checked. More general background will not settle the open
transfer obligation.

## Sources actually compared

| Primary source | Portion read for this comparison | Useful benchmark |
|---|---|---|
| [Cesarz--Woldar, 2025](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf) | Abstract, introduction/outline, preliminaries and figures, Corollaries 3.13 and 4.15 | Their abstract explicitly distinguishes proof without computer; earlier results and their own contribution are separated; the local figures introduce notation used immediately afterwards. They do **not** exclude order 7. |
| [Crnkovic--Maksimovic, 2020](https://cdm.ucalgary.ca/article/download/62323/54015/204856) | Sections 4.5 and 7, construction description and tables | An explicit sequence of construction/refinement steps, case counts, named GAP/Mathematica software, and a concrete account of difficult cases and machine time. Theorems 7.2 and 7.3 give precise citation targets. |
| [Lam--Thiel--Swiercz, 1989](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/EBD5E851090B1983978BBC6FE18D2A3F/S0008414X00002534a.pdf/div-class-title-the-non-existence-of-finite-projective-planes-of-order-10-div.pdf) | Sections 2--4, especially pp. 1118--1122 | The mathematical reduction leads to a short staged description of the search; tables report intermediate completions; named VAX/CRAY hardware and computing time are given. Correctness concerns are discussed explicitly, rather than made to disappear by saying the runs agree. |
| [Bright et al., 2021](https://ojs.aaai.org/index.php/AAAI/article/download/16483/16290) | Sections 4--6, certificate and results discussion | They explain what each certificate proves, including symmetry exclusions, and distinguish checked search certificates from a formal proof of the entire mathematics. Generation, verification, hardware and resource measures are stated separately; they also report discrepancies in earlier intermediate counts. |
| [Conway--Sloane, 1990](https://neilsloane.com/doc/Me157.pdf) | Introduction and Section 2, pp. 385--386 | Explicit conventions, precise formula references and a declared proof-sketch/announcement scope. A short announcement is not the right model for omitting details from this long computational proof. |

Makhnev--Minakova's original Russian paper was inspected in the earlier
mathematical bibliography pass; it was not reread in full for this editorial
note. Behbahani's [official thesis record](https://spectrum.library.concordia.ca/id/eprint/976720/)
and abstract are accessible, but the full PDF again failed to open here.
No full-thesis comparison or new verification of the Behbahani--Lam article
is claimed. The edition-specific locations in Serre, Humphreys, Nikulin and
SPLAG below are recommendations or already printed references, not a claim
that those whole books were opened in this pass.

## Priority corrections: where / change / length

| Where | What to change | Length |
|---|---|---|
| Main abstract, lines 61--70; Section 9, lines 825--837; conclusion 936--937 | Bring the explicitly outstanding transfer recertification into the opening account of the **present draft's** status. A caveat only at the end does not resolve the tension with an unconditional completed-proof announcement. State exactly which computational conclusion still rests on unrecertified transfers. Do not describe the draft as an independently certified exclusion of all 156 classes. | 2--3 lines in abstract or immediately after the theorem; replace, not accumulate caveats |
| Asymmetric, abstract and item (B), lines 34--37 and 61--65 | Keep the theorem's existing conditional form and carry that condition into the abstract and C2 status cell. The C2 dependency includes the transfer issue, not merely lack of journal refereeing/formalisation. Replace the unqualified claim that each lemma has independent programs by “verified as described in Section 9 of [C2]”, because the T20 implementation independence is partial. | 3--4 lines total |
| Main Section 9, lines 899--901 | Replace “cannot affect” by a statement of the actual protection: separate checking tests the mathematical validity of a certificate; repeated runs test reproducibility of the chosen computation. Neither proves the completeness of the input enumeration or removes common software errors. Do not promise that hardware error is impossible. | Replace 3 lines with 4 |
| Main Section 9, lines 895--899 | “Would show” suggests an audit must detect every mathematical error. Use “The written derivations and source review address errors in the mathematical pruning rules.” Scope the following sentence to the portions actually checked. | Replace 2--3 lines |
| Main Section 9, lines 859--865 | “Each was discharged” conflicts with the limited historical scope subsequently acknowledged. Say the five issues were investigated and name which have complete replacement certificates versus verification only for rebuilt lists. Point to the existing transfer paragraph without reopening its mathematics here. | Replace 3--4 lines |
| Main Section 9 summary, lines 903--910 | Add the twin-root arithmetic and well-founded target dependencies as a separate item. The present four-item summary omits the one issue singled out as open later. | 2--3 lines |
| Main abstract, lines 65--69 | The alternatives “witness or exhaustive search” omit transfer, which is a major route in Section 8.4. Add “or transfer to another admissible lattice”, with its Section 9 qualification. | 1 line |
| Main introduction, lines 81--83 | Replace “first studied by Wilbrink” with “An early structural study is due to Wilbrink”. CW's introduction records Biggs in 1969 and Conway by 1975; the present priority wording is too strong. | Replace 1 line |
| Main introduction, lines 88--94 | Pin [CW] to Corollaries **3.13 and 4.15**, [CM] to Theorems **7.2 and 7.3**. Keep the correct distinction between order-7 cyclicity and nonexistence. Do not copy another paper's numbering for [MM] without checking the edition: the earlier primary pass found different numbering. | No extra paragraph; 1--2 citation lines |
| Main abstract and Section 8.2 heading, lines 560ff; conclusion 927--930 | Replace “without enumeration” by “without enumerating normal pairs”. Packing still uses enumerated short vectors and computed invariants. Replace “elementary” for the entire lattice reduction by “proved in the text from the cited lattice theorems”. For the eigenfunction lower bound say **nonzero**, and include the dual-minimum bound together with T16/T18/T20. | 3--4 replacements, at most 3 extra lines |
| Main Section 9, lines 816, 857--858 and 917 | “Refereed”, “party” and “referee reports” can suggest external human review. Use “reviewed in separate sessions”, “a separate reviewer” with the AI provenance explicitly identified once, and “internal review reports”. Preserve the existing acknowledgement and exact program-independence distinctions. | 2--3 replacements |
| Main abstract availability sentence; Section 9 reproducibility | In a private working draft say the material is **retained in the accompanying private repository**. Links can remain as requested. “Available” without qualification currently suggests readers can retrieve it. Any future public release is a later author decision, not an action recommended for tonight. | Replace 1--2 lines |

Two ready replacements for the author:

> This draft records a computer-assisted exclusion campaign. The remaining
> validation obligation concerns transfers to twin lattices, as specified
> in Section 9; the corresponding recertification has not been completed.

> Separately checked certificates and repeated runs provide different
> safeguards. Certificate checking verifies the recorded mathematical
> witness, while repeated runs test reproducibility; neither by itself
> establishes completeness of the input enumeration.

## Reader support and computational presentation

| Where | What to add or change | Length |
|---|---|---|
| Section 2, after the lattice definition, lines 172--176 | Define integral, unimodular, odd/even, primitive sublattice, discriminant group and discriminant bilinear form. State that norm means squared length and roots here always have norm 2. The current one-paragraph notation section jumps too quickly to discriminant forms. | 7--10 lines |
| After Section 8.4's four methods, before results | Give a compact algorithm in mathematical prose: enumerate a normal-pair representative; test a positive witness; certify a transfer if a valid target/descent is available; otherwise enumerate partial frames; report unresolved limits separately. Label this the *logical certification procedure*, not a claim that it reproduces the historical branch order. CM Section 4.5 is the model for making stages legible. | 8--10 lines |
| Section 9, before “The three lemmas” | Replace some repeated prose by a small verification table: object / method of checking / coverage / remaining reliance. Rows: input lattices, short shells, pair enumeration, positive witnesses, T lemmas, frame search, twin transfer. Do not use a single yes/no “verified” column. | About 8 table rows; remove equivalent repetitions |
| Section 9, computing environment, lines 886--892 | Add the operating system and the verified reference environment used for the final checkers, including SymPy for the independent exact identification/packing programs. Keep unknown historical CPU details marked unknown. Separate elapsed job-hours, core-hours and verification cost; do not add unlike totals. | 3--5 lines or a compact supplementary table |
| Section 9 reproducibility, lines 916--918 | Name one stable entry point for a reader, the exact archive/commit, required inputs, checker commands, and expected summary. Distinguish inexpensive checks from a full rerun; put individual file hashes and campaign history in the supplement. Do not promise “records of every run” if interrupted or superseded runs are not all archived. | 5--7 lines plus a supplementary manifest |
| Table of methods, lines 751--756 | Reconcile the wording “main enumeration” on 91+13 rows with its defined scope of 102 lattices. The 13 include 001/002 with special pair generators. Say this explicitly; do not suggest the same enumerator handles all 104. Keep the 141 odd-Leech *classes* visibly different from pair counts. | 2-line table note |
| Appendix A | Separate final proof route from historical method code. Historical H/F/H3/S/SD/GD labels and dates do not tell a reader why a row is excluded. Keep an archive-code column only in the supplement. Normalize repeated root factors, e.g. a3^2 a3 -> a3^3 and a1^4 a1^4 -> a1^8, without changing the stored data. | New short legend, 4--6 lines; regenerate the table through its generator |
| Asymmetric, item (C), lines 69--87 | Move the long Lean declaration, CI commands, axiom list and commit history into a small verification appendix or repository note. Keep a two-sentence statement of theorem scope, toolchain/pinned artifact and the fact that this editorial review did not rebuild it. Mathematical readers should reach the prime-by-prime argument without reading a CI log. | Main text 4--6 lines; retain details in supplement |

The current manuscript already exceeds the older papers in several kinds
of provenance detail. The improvement is to organise that detail around
mathematical obligations. Bright et al. is a useful modern comparison for
certificate scope and resource reporting, not a reason to assert that our
uncertified searches meet their certificate standard. Add that reference
only where discussing this specific distinction (2--3 lines), without a
claim that the methods are identical.

## Standard facts: precise additions instead of a generic reading list

| Fact / location | Recommended treatment | Length |
|---|---|---|
| Projection of a unimodular lattice onto the dual of a primitive sublattice, main 308--310 | Supply the short proof: an integer functional on primitive K extends to Z^49 because the quotient is free; unimodularity represents it by an ambient integer vector; orthogonal projection represents the restricted functional. This removes an otherwise unreferenced standard step. | 3 lines |
| Quadratic/bilinear forms over F7, main 339--341 and 394--395 | Keep the Serre reference now present; explicitly specify characteristic not 2 and dimension/determinant classification, then use the displayed determinant character. Verify the printed section locator against the cited edition before finalising the bibliography. | 1--2 lines |
| Gluing, main 396--398 | Keep Nikulin and SPLAG, but say **discriminant bilinear form modulo Z** here: the lattices need not be even. Add the graph-of-anti-isometry construction and the integrality/index argument already used. Do not silently invoke a theorem only stated for even lattices and quadratic forms modulo 2Z. | 3--4 lines |
| Oddity formula, main 335--337 | Keep SPLAG Chapter 15; pin its formula/section in the actual third edition and define the sign notation used in the Jordan symbol. Do not invent a locator from another edition. | 2--3 lines |
| Shadow and the four cosets, definition in Section 6 | Cite CS90 Section 2, p. 386, for the four-coset/theta-series description. Explain the rank-24 parity condition for the two even neighbours; cite Borcherds's classification chapter for its use here. The shadow notation should not be introduced as if it were project-specific. | 2--3 lines |
| Root components / dominant weights, Section 8.3 | Cite the standard ADE classification and Weyl chamber background in Humphreys; the stabiliser reference in Section 1.12 is already present. State that only isometries preserving the full lattice, including glue, are used. | 1--2 lines; most of the latter point is already present |
| Short-vector enumeration, Section 8.3 | Fincke--Pohst is now cited. Add the exact completeness obligation for branch bounds; “exact final tests” alone certify retained vectors, not absence of missed vectors. Refer to the separate shell-count argument where it supplies completeness. | 2--3 lines |
| Theta coefficients, main 531--532 | Refer to CS90's theta and shadow expansions, then either display the rank-24 coefficient comparison in the supplement or point directly to its derivation. The identity specialised to this rank is our use of the source, not a theorem printed verbatim in CS90. | 2 lines plus the existing derivation link |

## Terminology to remove or clarify

| Current term | Reader-facing replacement |
|---|---|
| stream sweep | enumeration of normal pairs |
| engine | search program / enumeration program, according to function |
| records | run summaries, execution logs, or certificates: choose the actual object |
| package / v10 | archived program version, pinned in the supplement |
| done / closed | traversal completed / excluded by the stated criterion; these are different |
| final tracker status | recorded campaign status; never use it as a substitute for a proof |
| S, SD, GD, H, F, H3, EP, SP | mathematical method name or proposition number in the paper; retain codes in the artifact manifest |
| identity symmetry | no reduction by diagram automorphisms; Weyl reduction may still be used |
| witness / certificate | define witness as the mathematical object and certificate as its finite representation with checking conditions |
| independent | specify independent source code, independently reconstructed input, different algorithm, or separate execution |

## Figures and tone

Both existing figures help. I inspected the **pinned rendered PDF pages 3
and 5**, not only the TikZ source. Labels and captions are legible and the
figures fit the page. Keep the local two-block picture: it directly explains
why the columns of C have the form e_i +/- e_j, much as CW's local diagrams
support their notation. No third decorative figure is needed.

Figure 1's caption should say “The upper chain through Theorem 6.1 is proved
by hand” instead of “The left column is proved by hand”: the visible left
branch also includes the packing exclusions, whose invariants were
computed. Change the 20-lattice box to “without normal-pair enumeration”.
This takes **two label/caption replacements**, no new figure. The logical
status qualification at the beginning of the draft also applies to its
terminal “contradiction” box.

Do not imitate LTS's 1989 epistemological language word for word or add
apologetic prose everywhere. State the result, the finite reductions, the
actual checks, and the outstanding obligation plainly. Conversely, avoid
“fully verified”, “computer-free” for computed packing data, and
“independent” for merely separate executions. The current asymmetry note's
separation of published statements, manuscripts, and formalisation is
useful; retain it while reducing the implementation detail in its main text.

## Coverage and what remains outside this note

All requested editorial categories (a)--(f) have concrete recommendations
above. This is not a line-by-line comparison with every bibliography item.
Missing: the full Behbahani thesis/BL article comparison, edition-specific
book-locator verification, and a renewed whole-paper mathematical referee
pass. No C3/C7 Lean rebuild, twin recertification, or validation of the newly
reported 044 result was performed. These limits are not repaired by editing
the prose. This note is ready for use on the private draft now.

Pinned input SHA256:

- main.tex: `35a1dfb8b1de39d0d6a89bc09ebdf8cca8c572fbcc1e3c5f10ce3e0175c50cdd`
- asymmetric.tex: `e8ecd10c9e2200eca7c5d472b5213deff467d41704084fdc58f039ae19daf8be`
- main.pdf: `0814486cc8e5255b7b872cf7cc0dc127599d684cf42046cda953d50206bd4248`
- asymmetric.pdf: `e2db7fd700c5accc7e679362851549de84577978f611b604800b045e194fa515`

## Addendum (g)--(h): wording and attribution at 599670f41

Response to message 113, with priority over further polishing. The updated
main source was obtained from the repository and compared to the reviewed
version; asymmetric.tex is byte-identical. The requested passages were read
against the primary sources below. The original Russian MM argument and
Borcherds's complete three-page author copy were reopened for this pass.

**Finding:** no remaining passage in these targeted comparisons was found
to reproduce distinctive source prose or a proof paragraph by paragraph.
That is a bounded editorial finding, not a guarantee about all literature.
There **are known results and a known proof device that need more local
credit**, as detailed below. A citation does not make copied wording one's
own; conversely the same theorem, formula or conventional symbol is not
evidence that the prose was copied.

| Passage at 599670f41 | Primary comparison and finding | Action |
|---|---|---|
| Main 82--102, history and literature | CW pp. 379--380; MM p. 95; CM Section 7. The factual sequence overlaps because it recounts the same earlier results. The revised prize/history sentence points explicitly to CW and does not follow its Biggs/Guy sentences. No further distinctive copied wording was found here. | Keep the source attribution. At 90--91, **still remove** “made the first study”: replace with “gave an early structural study”. This is an unsupported priority claim, not a wording-overlap finding. |
| Main 188--237, Proposition 3.1 and its proof | [MM, Theorem 1, p. 96; Proposition 2 and its lemmas, pp. 98--99; character argument, pp. 100--101](https://www.mathnet.ru/php/getFT.phtml?jrnid=dm&option_lang=eng&paperid=144&what=fullt). MM first classifies fixed subgraphs, then excludes cases using an integral eigenspace character. Our proof counts block types using s_p,r_p,t_p and filters numerical possibilities. It is not a paragraph-wise translation, but neither the fixed-point result nor the character-integrality idea is new. | Put “The fixed-point assertion is [MM, Theorem 1]; the following direct argument uses the same character-integrality obstruction” immediately before the proposition (2 lines). Existing credit in the outline, 122--124, is correct but too remote. |
| Main 219--223, trace congruence | MM p. 100 has the 54-dimensional character (4f+a1-18)/7. Our 44-dimensional trace (3f-a1+11)/7 is the complementary eigenspace expression: the two sum to f-1. | Add “[MM, p. 100]” at the character-integrality step (one citation). Do not claim this device as a new argument. This is attribution of a method, not a demand to change a necessary formula. |
| Main 239--249 and Figure 2, blocks/outer vertices | CW Section 2, pp. 380--381, labels the 14 neighbours and the 84 second neighbours using their unique inner pair. Our involution-specific two-block figure and signed columns organise that standard description for a different purpose. No distinctive copied prose/figure arrangement was found. The new local credit already identifies the shared construction. | Keep CW Section 2 attribution. Wilbrink's full text was not opened in this pass: do not imply it was newly checked here. No extra synonym rewrite needed. |
| Main 457--462, Definition 6.5 | CS90 Section 2, p. 386, introduces the index-two even sublattice and four cosets of its dual. Our quotient notation, characteristic-vector description and norm-two application are conventional mathematical formulations, not a close rendering of that paragraph. The citation is already present. | Sharpen it to “[CS90, Section 2, p. 386]”; add the rank-24 even-neighbour explanation/reference suggested above. No copied-sentence rewrite found necessary. |
| Main 571--595, packing proposition | Compared to CS90's theta/shadow argument and [Borcherds, Chapter 17, author copy pp. 1--3](https://math.berkeley.edu/~reb/papers/splag/splag.pdf). Neither contains this 42-word disjoint-hit criterion or the frame-specific 8/7 dual-span obstruction in the passages read. No matching proof wording or uncited version of this proposition found in these sources. | Keep the direct derivation from the frame lemmas. This observation is not a literature-wide novelty claim. |
| Main 417--418, 558--564, classification/identification; Appendix A | Borcherds's chapter, p. 2, supplies the 156-class list and its even-neighbour description. The manuscript attributes classification to Borcherds and distinguishes the exact check of its own input data. | Make the appendix caption explicitly say that root-system data/classification are from Borcherds, while IDs 000--155 are the project's numbering. This is especially useful if a reader encounters the table without Section 8.1 (1--2 lines). |
| Asymmetric, 34--130 | The note's prime-by-prime assembly and status table do not reproduce the compared sources' presentation. Its historical ingredients are individually attributed. | Keep the conditional statement; retain the caveats from the first part of this review. No additional text-copying concern found in the compared passages. |

**Correction to one earlier presentation suggestion:** Borcherds explains
on p. 2 that repeated/grouped components can encode automorphism orbits.
Thus do not blindly normalise the appendix's repeated root factors. If its
column denotes only the abstract ADE root type, simplify and say that orbit
grouping is suppressed; if the grouping is retained, explain its source and
meaning. This distinction also explains how two equal root systems can
appear with different typographical grouping.

The two concrete credit additions are the local MM theorem/method citation
and the explicit attribution in the appendix caption. The classical block
description and shadow definition already have citations in this version.
No other uncredited result matching the selected source passages was found.
I have not verified priority of the packing proposition across all prior
literature, or compared the unavailable full Behbahani/BL texts. The earlier
claim that the original MM text was not reread applies only to the first
(a)--(f) pass; its relevant pp. 95--101 were inspected for this addendum.

Main source SHA256 at 599670f41:
`d38bbd27550a0ef8d527616d380edf882d5f3a4b897f1490156d63481e830254`.
Asymmetric source retains the SHA256 stated above.

### Caption clarification, message 116

The three-page author copy of Borcherds's chapter explains the meaning of
component grouping but **does not include Table 17.1 itself**. I have not
compared the 156 displayed strings against that printed table. The source
filename `borcherds_odd24.json` does not certify a faithful transcription
of its notation or grouping. Our exact identification checks certify the
abstract ADE types, not the original author's component-orbit grouping.
Accordingly, do not write “as in his table” or “the grouping is his” on the
basis of this review. The grouping may agree; that comparison remains undone.

A supported replacement is:

> The 156 isometry classes are those of Borcherds's classification [Bor].
> Root-system labels are reproduced from the input data, retaining their
> grouping of equal components. The identifiers 000--155 are used in this
> work. The displayed grouping has not been checked against Borcherds's
> printed table.

Alternatively, display canonical ADE types without grouping, label the
column accordingly, and retain the original input strings in the data
archive. No orbit interpretation of the current grouping is certified here.
