# Second referee report on `lemma/T18_PROOF.md`

Agent report of 2026-10-07 (night), saved by the main session. This referee read ONLY the consolidated text (not the working
reports, not the first referee's report), checked every hand statement line by line, and re-did every Computation with programs
written from the text alone. Programs and outputs: this folder (pure Python with numpy and flint, no solver; a rejection is an
integer vector with negative form in Python integers, or an exact characteristic polynomial).

## 1. Verdict

**No error that breaks the proof.** Every hand statement checks line by line, and every Computation (4.10, 7.3, 7.6, 8.4, 8.5, 8.6,
8.8) was reproduced with the referee's own programs, with every count equal.

## 2. Problems, most serious first (none is load-bearing; no ERROR in any hand statement or in any count checked)

1. **GAP (definition; closed by the referee's check).** Lines 663-680, 990-995, 1216-1219, 1261-1263: survivors are defined by "no
   PSD violation *is found*", which depends on the program, and "kept" is a floating-point decision. Soundness is not affected, since
   only exact rejections are used. Checked exactly (characteristic polynomial): all 5595 + 4977 + 196 stage-B triples and the 4
   survivors are PSD for both matrices. Fix: define survivors by "M1[Y] and M2[Y] are PSD" and say which lists were verified exactly.
2. **GAP (closed).** Lines 428-432, 1535-1538: the list of 16 classes came from one program. The referee's own enumeration gives the
   same result (section 5).
3. **GAP (closed) and PRESENTATION** (`types.json` and H16, lines 21-24, 1539-1549). Recomputed directly: for each of B0, B1, B2 the
   entries of `types.json` with d = 0, 1, 2 are exactly the types with no budget violation on the 21 vertices S u {p, w, sigma w}
   (81 / 72 / 198 / 126); neither the PSD filter nor the H16 filter plays any role there. The claim that the second implementations
   do not read the file is true (searched `r3_verify.py`, `c_mine.py`, everything in `t18_VERIF331`, `e331.py`, `d_stage.py`,
   everything in `t18_REFEREE`, `r4_stageD.py`, `r4_verifyD.py`, `r4_verifyC.py`, `r4_verifyC2.py`; the only occurrences are
   comments). The list of readers in item 6 is incomplete: `r2_ext2_bruteforce.py` also reads it, as do the unused `level1.py`,
   `level1_count.py`, `r2_gram.py`, `star.py`.
4. **GAP (minor, hand text).** Lemma 8.2 (line 1166) with (C2) (line 1188): all of X_2 x X_2 is "parameter H", including pairs
   between the two orbits of A_p. Lemma 8.1 (a) forces those to be non-adjacent, and (C2) does not record it. Harmless (such an edge
   gives the adjacent pair (p, a) two common neighbours). Computation 8.4 should say whether H ranges over those pairs; forcing them
   absent gives the same lists.
5. **PRESENTATION (reproducibility).** Computation 7.6 step 3 (lines 992-993): "a table" is not defined as a counted object. The
   counts 8639 / 27203 are reproduced when a table is an unordered set of three row-orbits {R, sigma R} plus a sigma-invariant G';
   rows may contain both vertices of an orbit of X_2'.
6. **PRESENTATION (overstatement).** Lines 1304-1305: "two complete exact implementations (E and C)" for each graph. For B0, E is
   complete only modulo the stabiliser reduction, which exists in one implementation. Closed here: recount gives 2667 orbits,
   closure, the same stabiliser orders (1 x85, 2 x36, 4 x9, 6, 8, 72); the referee's stage C treats all 5595 triples.
7. **PRESENTATION (imprecise remark).** Lines 1081-1087: cell room alone gives 1958 / 4332 / 1309; the numbers 1834 / 4096 / 1265 need
   a second condition (no vertex s_U of A_p with i in U and j in tau U, since w would then share p, x_i, y_j with it).
8. **PRESENTATION.** Lines 1569-1570: `_check_text_defs.py` and `_check_survivors.py` are in `lemma/t18_PROOF/`.
9. **PRESENTATION.** There is no 55-vertex set in the text; the stage-D outputs print "0 configurations on 55 vertices left", but
   (D1) covers only 48 and 49 vertices.
10. **PRESENTATION (appendix).** Lines 1291, 1679 give a `REPORT.md` as the location of the B0 result of E: point to
    `b0_stageC_done_*.jsonl` and `b0_stageC_survivors.json` (checked: 2667 lines, idx 0..2666 each once, no survivor, counters
    262850 / 170382 / 701270 / 340605 / 704789). Line 1294: the "sample of 29 triples" is a run that timed out after 29. Line 1300:
    the first of the four B2 runs of V timed out after 86 of 98 triples; the four runs tile as 86 + 43 + 43 + 24 = 196.
    `r3_finalB.out` reads 17 files and `13_B1_survivors_compare.out` reads 15, against the "14 files used".
11. **PRESENTATION (notation).** h_i is the inner indicator at line 301 and the profile count at line 570; c is an orbit index,
    c(v), and c_O; the letters B, C, E, V, R, H each name both a mathematical object and a program or stage; `r3_verify.py` uses the
    threshold -1e-6, not -1e-7.

Remarks that would simplify the text (the referee's own, not refereed): (a) rank M1[Y47] = 46 > 44 = rank M1 already excludes the
four survivors by Lemma 6.1 alone; Lemma 6.3, Proposition 6.4 and stage D are not needed for this. (b) The four survivors are two
graphs up to the stabiliser of the matching. (c) (D3) can be sharpened to 3 (a_2(z) - 4) <= 2t. (d) (F2), (F7), the degree cap of
(C2), (C3), (C4) and the cap of (D3) are never needed: runs without them give the same lists.

## 3. Hand statements

| Statement | Verdict |
|---|---|
| (1.1), spectrum, f = 54, g = 44 | correct |
| Lemma 2.1 (a)-(d), Corollary 2.2, remark on iota | correct; only "one fixed vertex" and "automorphism of order 2" are used |
| Proposition 3.1 | correct; claim, the four partitions of 9, three exclusions redone |
| (4.1)-(4.3), Lemma 4.2 | correct |
| Lemma 4.3 | correct (bound 90 redone) |
| Lemma 4.4 (I1), (I2) | correct |
| Lemma 4.5, Lemma 4.6 | correct |
| Lemma 4.7, cases A, B, C | correct; the split is exhaustive; (4.5)-(4.7) redone |
| Corollary 4.8 and remark | correct |
| Lemma 4.9, Corollary 4.11 | correct (4.11 uses "never 0" from Computation 4.10, as stated) |
| Lemma 5.1, (5.1), Lemma 5.2, Theorem 5.3 | correct |
| Lemma 5.4 (a)-(d), identity (*), t <= 9 | correct (864 - 2t, 576 - 2t, the sum 36 redone) |
| Lemma 5.5, Lemma 5.6, Proposition 5.7 | correct (30 = 30, 36 > 28) |
| Lemma 6.1 | correct: M1 = 63 E_{-4}, M2 = 77 E_3 |
| Lemma 6.2, (6.1) | correct |
| Lemma 6.3 | correct (traces 1, 14, 99; multiplicities 22/22 and 27/27) |
| Proposition 6.4 (a), (b) | correct; the entries of G_odd and G_even also checked numerically on the four survivors |
| Lemma 7.1, Lemma 7.2 (R1)-(R3), (7.1) | correct |
| Lemma 7.4 (a)-(f) | correct |
| Lemma 7.5: table, (F1)-(F6) | correct; every class pair covered |
| (F7): sum a_2 (a_2 - 1) <= 24 | correct; re-derived: p, z_0, sigma z_0 contribute 3 x 4 = 12 to (*) |
| Proposition 7.7 | correct given Computations 7.3, 7.6 |
| Lemma 8.1 (a)-(f) | correct |
| Lemma 8.2 | correct (see problem 4) |
| Lemma 8.3 (C1)-(C8), m(t) | correct (0, 2, 4, 6, 8, 14, 20, 26, 32, 42 redone) |
| Lemma 8.7 (D1), (D2), (D4) | correct |
| (D3): a_2(z) <= 4 + t | correct; re-derived: sum of c over X_0 is 2t and c(z) = c(sigma z) = a_2(z) - 4 |
| Remark on the kernel 4 e_p + 1_{N(p)} | correct (checked exactly) |
| Proposition 8.9, Theorem 9.1 | correct given the Computations |

Logical order: nothing is used before it is proved.

## 4. Determined sets

No class pair without a reason was found in any set that the proof uses (37, 39, 39/41 with one or two orbits of W, 45, 47, 48/49,
51 vertices; each class pair traced to a lemma or a listed parameter). A 55-vertex set is not in the text: for Y47 u (X_0 \ {p}) the
pairs z-z' in different orbits of X_0 \ {p} have neither a reason nor a parameter; nothing depends on it, since the enumeration
stops at 49.

## 5. Independent checks (the referee's own programs)

- **Computation 4.10** (`q9.py`): 1,024,380 labelled 4-regular graphs on 9 vertices, 16 classes, all connected; exactly 3 classes
  have codegrees <= 2 (5040 + 30240 + 20160 = 55440 labelled graphs, minimum codegree 1, isomorphic to B0, B1, B2); the other 13
  have maximum codegree 3 or 4.
- **Graph data and Computation 7.3** (`stage1.py`): |Aut| = 72 / 12 / 18, triangles 6 / 8 / 9; 99 rectangles, 63 usable;
  25514 / 13799 / 9229 matchings; 425 / 1259 / 528 orbits (also by Burnside).
- **Profile (3,3,1)** (`p331.py`, without (F2), (F7)):

| | B0 | B1 | B2 |
|---|---|---|---|
| pairs (tau, F), budgets on 25 vertices | 3510 | 7224 | 2406 |
| 39-vertex survivors | 383 | 481 | 7 |
| tables, budgets on 45 vertices | 8639 | 27203 | 0 |
| tables, PSD on 45 vertices | 23 | 164 | 0 |
| graphs on 51 vertices, budgets | 52 | 1839 | - |
| graphs on 51 vertices, PSD | 0 | 0 | - |

  With M1 alone (`p331_m1.py`): 887 / 672 / 7, then 102 / 190 / 0, then 0 / 10 / 0.
- **Stage B** (`stageB.py`): pairs (tau, F) with budgets on 23 vertices 5545 / 12366 / 4347, exactly PSD 4904 / 11509 / 3863;
  stage-B triples 5595 / 4977 / 196; all triples exactly PSD and budget-valid on Y37 (`exactB.py`).
- **Stage C** (`stageC.py`, all triples): B0: 0 survivors. B2: 0 survivors. B1: exactly 4, the graphs of Appendix B.
- **Computations 8.6 and 8.8** (`survivors.py`, from Appendix B alone): M1 PSD of rank 46, M2 PSD of rank 45;
  det G_odd = 47684, 47684, 874944, 874944; rank G_odd = 23; rank G_even = 23; stage D: 678, 678, 846, 846 pairs (849 without the
  cap); every oriented Z rejected exactly, already on 48 vertices, always by M1.
- **Counts spot-checked against the quoted output files** (18 groups, all agree): see the agent's list in `SPOTCHECK.txt` if present,
  among them `ref1_quartic9.out`, `verify_S.out`, `r2_stage1_*.out`, `v4_compare.out`, `r2_summary_*.out`, `v7_step4_*.out`,
  `r4_rank331.out`, `09_B0_check_complete.out`, `11_B1_check_complete.out`, `13_B1_survivors_compare.out`, `rows.out`.

## 6. Not checked by this referee

- The repository programs line by line; that the stored outputs were produced by the scripts now in place; the saved PSD
  certificates of the repository (own rejections were produced instead).
- Exact positive semidefiniteness of the 39- and 45-vertex survivors (only rejections matter).
- **Section 1.4 of the text (the lattice dictionary), H16, and the norm-20 case.**
