# Referee report on `lemma/BRIDGE.md`

Agent report of 2026-10-07 (night), saved by the main session. Scripts and outputs (the referee's own, exact arithmetic): this folder.

## 1. Verdict

**No error that breaks the Bridge Theorem or its application** to "root with Y = 5 => the pair hosts no graph frame". The conclusion
is conditional on T18, on a per-pair check of H4, and on the upstream model, which is outside the text.

## 2. Problems, most serious first

1. **GAP (operational; the text acknowledges it): H4 on the quick deferral path** (section 5 H4, sections 8, 9.5). Confirmed by
   reading and by execution: with `Q_DEFER_NODES=0`, `defer_consumer.search` returns DEFERRED without ever reaching `pair_setup`. An
   invalid pair (y2 replaced by y2 + r; norms 7 and 5) came back as `DEFERRED (pending T18 ...)`. The theorem is false without H4.
   Fix: make the conversion certificate mandatory, and state it in ambient coordinates (y1, y2, r in U; y.y = 7; y1.y2 = 0;
   r.r = 2; Y = 5), because the engine's basis comes from a CPU-dependent float LLL and a coefficient-vector certificate is tied to
   one basis.
2. **ERROR in the description of the engine (no effect on the theorem)**: section 6 point 13 and the H4 row. "The engine would answer
   INVALID for such a pair" is false in general: `FD.search` returns `EXCLUDED (char-vector trap)` and, with `FD_MIN97=1`,
   `EXCLUDED (dual min 9/7 ...)` before `pair_setup`; the consumer's twin-transfer, swap and twin-canon filters also come before it.
   Demonstrated: a pair with (y1,y2) = 1 got `EXCLUDED (char-vector trap)`. So "asserted by the engine in pair_setup" covers only
   pairs that reach `pair_setup`; the engine's own 04/10-filter verdicts do not check H4 either. The campaign's norm guarantee rests
   on the producer, not on the engine.
3. **UNVERIFIED, outside the text: the upstream model behind H5.** Assumed: every srg(99,14,1,2) with such an involution yields one
   of the 156 envelopes U and a pair (y1,y2) of the enumerated lists, with its 49 frame vectors in U, orthogonal to y1, y2, with
   Gram exactly 3I - S. The text says so and the 04/10 filter makes the same assumption. The quotes from the dossiers and the engine
   headers are accurate. The entry formula for S is the author's reconstruction; it is forced, and consistent with the engine's star
   sums and T^2 + T = 12I - C^T C.
4. **PRESENTATION: H5 in the table of section 5.** H5 is the hypothesis being refuted, not one to be "guaranteed"; the real external
   assumption (item 3) should be its own row.
5. **PRESENTATION: Lemma 3 is stated "under (U), (F)" but needs (G)** (H^2 = 7H and rank 22 come from Lemmas 1-2).
6. **PRESENTATION: the "Conversely ..." sentences of the corollaries** are vacuous under (G),(U),(F) and pure arithmetic under (U)
   alone; they are the only place where "y1, y2 in U" (H3) is used. H3 is not needed for the theorem or for the exclusion.
7. **UNVERIFIED: section 6 point 7, "The converse is false in general"**: no engine frame that fails to come from a graph is
   exhibited. Write "the converse is not available". Harmless.
8. **PRESENTATION: section 2, "K* = pi(U) because U is unimodular and Zy1+Zy2 is primitive"**: surjectivity needs only U unimodular;
   primitivity gives det K = 49. Not used by the bridge.
9. **PRESENTATION: H2 row and `certify.py`.** `setup_lattice` checks the determinant in floating point; rank 24, integrality and
   positive definiteness hold exactly by construction; unimodularity is not used. `certify.certificate` receives integer coefficient
   vectors and does not itself test membership; the exact ambient-to-coefficient conversion is the caller's job.
10. **PRESENTATION: section 7, "a glue vector g that has a component on the normals"** is true for the 243-vertex graph only.
11. **Robustness: `defer_consumer._RG` is keyed by `id(L)`**: sound only because each process loads one lattice (true for both job
    kinds).
12. **UNVERIFIED side remarks, not needed**: "the producer's filters remove E = 1..7" (0 occurrences on the 400 pairs of 011, producer
    not audited); "by construction in the producer" for H4 (only grepped); "the twin holds the same frame" (imported claim).

## 3. Lemmas and hypotheses

| Item | Verdict |
|---|---|
| Orbits, S, diagonal (-1 on the 7 inner orbits, 0 on the 42 outer) | Correct |
| Lemma 0 (x ~ sigma x iff x ~ p; 14 such vertices) | Correct |
| Lemma 1: A lift(a) = lift(Sa) at x_i, sigma x_i and p; S symmetric; S^2 + S = 12I | Correct |
| Multiplicities 22 and 27 | Correct (tr P = 1, tr PA = 14; cross-check tr S = -7 = 22 (-4) + 27 * 3) |
| Lemma 2: H = 3I - S, H^2 = 7H, rank 22, norms 4 and 3 | Correct (tr H = 154 = 7 * 22) |
| Lemma 3 (tight frame) | Correct. Needs rank 24, positive definiteness, y1, y2 of norm 7 and orthogonal, frame orthogonal to them, Gram 3I - S, and (G). Nothing else about U is used |
| Lemma 4: (pi(v), pi(v)) = E(v)/7 | Correct; needs exactly H4 |
| Theorem (1)-(4) | Correct. Integrality uses only v, f_i in U and U integral. Constant 2 correct |
| Corollary T18 | Correct given T18; T18's statement matches phi_v exactly |
| Arithmetic: 18, 20, 16; coset table E = 8..14; no norm-3 or norm-4 vector with E = 9 | Correct under (U) alone. Not needed for the exclusion |
| Corollaries T20, H16 | Bridge half correct. T20 is open. The H16 graph lemma was not refereed |
| H1 | Needed; the same as T18's hypotheses |
| H2 | Needed (integral, positive definite, rank 24). Guarantee adequate |
| H3 | Not needed for the theorem; it identifies the pair. Guarantee adequate (exact membership tests) |
| H4 | **Needed and essential. Guarantee inadequate on the quick path (items 1-2)** |
| H5 | The hypothesis refuted; the upstream part is outside the text |
| H6 | Needed. Adequate: `R @ G @ y` in int64 on integer coefficient vectors; rows of R selected by exact norm; one per +- pair |
| H7 | Needed; taken as given |
| H8 | T20 pairs only; open |
| Direction | The text concludes only "no graph frame in this pair", nothing stronger |

## 4. Numerical checks (the referee's own scripts)

- `ref_graphs.py`: Paley(9) and the 243-vertex srg(243,22,1,2), built from scratch, x -> -x. Analogous constants c = r - s, frame Gram
  rI - S, E = cN - Y, claims A phi = s phi and sum phi^2 = 2E (for 99: 3, -4, 7). On 300 random lattice vectors per graph: integer
  a_i, Sa = sa, A phi_v = s phi_v at every vertex including p, sum a^2 = E, sum phi^2 = 2E, phi = 0 iff E = 0. Controls: S with zero
  diagonal fails in 50/50 cases; the even lift fails in every case; an extra orthogonal dimension gives sum a^2 < E in 100/100;
  non-orthogonal normals break the E formula in 72-75 of 100.
- `ref_arith.py`: brute force over (N, a, b): the table for E = 8..14 and all claims of section 6.10 confirmed.
- `ref_engine.py`: lattice 011 and its 400 pairs in ambient coordinates: G = B B^T, exact det 1, positive definite; all pairs in U,
  norm 7, orthogonal; `defer_consumer.witness` agrees with the ambient Y on 400/400 pairs (T18 279, T20 113, none 8); the Y = 13
  filter fires on 363 pairs, the other 37 split into 19 with minimum E = 9 and 18 with minimum E = 10.

## 5. Not checked

T18 itself and T20; the 04/10 graph lemma and the Wagner re-run; the upstream reduction graph -> (U, y1, y2) and the completeness of
the 156 lattices and of the pair lists; the producers beyond a grep; the twin-transfer claim; the other 155 lattices and the golay
pair files. No 99-vertex graph exists to test on: the numerical check validates the dictionary and constants on the 9- and
243-vertex analogues only.
