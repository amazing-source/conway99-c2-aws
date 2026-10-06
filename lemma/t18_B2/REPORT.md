# T18, graph B2 = C9(1,2): profile (2,5,0), plus a second run of profile (3,3,1)

Agent report of 2026-10-06 (22:29 to 23:27 local), saved by the main session. Notation of `lemma/t18/T18_REPORT.md`.
No solver: exhaustive backtracking and exact integer arithmetic. Scripts and outputs: this folder.

## Result

| Case of B2 | Outcome | Status |
|---|---|---|
| n_3 > 0 | does not occur | by hand (`lemma/t18/N3_REPORT.md`, re-read, correct) |
| profile (4,1,2) | impossible | by hand (A9, re-derived) |
| profile (3,3,1) | impossible | computed; two independent programs (round 2 and `e331.py`), same 7 intermediate configurations, 0 at the end |
| profile (2,5,0) | impossible | computed; stage 1 two programs, stage B two programs with identical sets, stage C three programs with 0 survivors each |

**B2 is therefore excluded**, with this status: hand reductions (A0-A10, A14, N3) plus exhaustive exact computations, each computed
step run by at least two programs sharing no code. Re-derived here: A8, A9, A10, A14; re-read: N3 and the rank bound (P2 of
`lemma/t18_STRUCT/REPORT.md`). Not re-derived here: A0-A5 (the reduction to the three graphs). T18 as a whole is not settled by this.

## Counts, profile (2,5,0), B2 (all 528 matchings)

| Stage | Object | Count | Programs |
|---|---|---|---|
| 1 | matchings of the 18 deficient pairs / orbits under Aut(B2), order 18 | 9229 / 528 | `r2_stage1.py`; `r3_verify.py stage1 2`, same numbers |
| B | pairs (tau, F) passing budgets and PSD on S u {p} u A_p (23 vertices) | 3863 = 3863 | both |
| B | triples (tau, F, H) on 37 vertices | 196 = 196, identical sets | `r3_p250.py` (50204 nodes), `r3_verify.py B250` (49067 nodes) |
| C | type solutions for W over the 74 pairs (tau, F) / passing on S u N[p] (33 vertices) | 11235 / 4227 | `r3_p250.py` and `c_mine.py`, same two numbers |
| C | configurations on S u {p} u X_2 u W (47 vertices) | 0 = 0 = 0 | `r3_p250.py`, `r3_verify.py C250`, `c_mine.py` |
| D | X_0 added (55 vertices) | nothing to extend | |

The 196 triples lie in 74 pairs (tau, F) and 53 matchings. t = e(X_2) is 2, 4, 6 for 6, 80, 110 triples.

Stage C, per program:

| Program | Search order | Work | Survivors |
|---|---|---|---|
| `r3_p250.py 2 {0,1} 2 560 BC` | W pair by pair, with 27/29-vertex neighbour tests and forced-orbit test | 11752 (triple, type solution) examined; 54354 rejections by budgets, 56237 by PSD certificate | 0 |
| `r3_verify.py C250 2 ...` | dual order, X_2 orbit by X_2 orbit | four runs of 86 + 43 + 43 + 24 = 196 triples; 825938 nodes | 0 |
| `c_mine.py 2 0 1 520 ...` (written here) | each mate pair of W alone on 39 vertices, then exact cover with a 41-vertex test for every two pairs | 4222 pair types; 39107 neighbour sets pass budgets, 1535 pass PSD; no cover reaches the 47-vertex test; 40845 PSD certificates | 0 |

## Rank bound versus budgets and semidefiniteness (B2, stage C)

- With budgets and PSD on 33, 39, 41 vertices everything dies before any 23-orbit set is complete: the rank bound has nothing to act on.
- With PSD kept on 33 and 39 vertices and budgets only on 41 and 47 (`C_NOPSD=41`): 4 budget-valid configurations on 47 vertices.
  All 4 are dead by the rank bound (odd Gram nonsingular, even part of rank > 22) and all 4 are also dead by PSD on 47 vertices.
- B1 survivors, own code (`rankbound.py`, `rank_B1_survivors.py`): odd Gram determinant 47684 for both #813 survivors and 874944 for
  both #975 survivors; odd rank 23 and even rank 23, against the bound 22. Agrees with the structural agent's numbers.

## Controls

- Positive control for `c_mine.py`: on the 170 stage-B triples of B1 matchings #813 and #975 it returns 4 survivors, the same four
  47-vertex graphs as `r3_p250.py`.
- Its incremental budget test agrees with the full recount by matrix product on all 39107 sets.
- 15048 saved PSD certificates re-checked by `r3_verify.py certs`, 0 invalid.

## Stage D (second implementation `d_stage.py`; the other is `t18/r4_stageD.py`), run on the four B1 survivors

| B1 survivor | Orbits {Z, sigma Z} generated | Pass budgets on 49 vertices (`d_stage.py` / `r4_stageD.py`) | Pass PSD on 49 | On 55 vertices |
|---|---|---|---|---|
| #813, F = [2,9] | 2260 | 678 / 678 | 0 | 0 |
| #813, F = [3,6] | 2260 | 678 / 678 | 0 | 0 |
| #975, F = [1,2] | 2087 | 846 / 846 | 0 | 0 |
| #975, F = [3,6] | 2087 | 846 / 846 | 0 | 0 |

All 3048 rejections carry an integer certificate. So the four B1 survivors die at stage D in two implementations, independently of
the rank bound.

## Profile (3,3,1) for B2, second implementation (`e331.py`)

| Step | `e331.py` | Round 2 |
|---|---|---|
| configurations on S u {p} u X_2 u {z0, sigma z0} (39 vertices) | 7, in matching #385 | 7, in matching #385; identical labelled graphs up to z0 <-> sigma z0 |
| configurations on S u X_0 u X_2 (45 vertices) | 0 | 0 |

## Model of stage C, with proofs (n_3 = 0, profile (2,5,0))

Identities (A8): for z in X_d, 2 a_2 + a_1 = 18 - 5d and a_0 = a_2 + 3d - 4. N(p) = A_p u W.
- (C-a) N(p) induces the seven mate edges only.
- (C-b) W is five mate pairs w = (i ; j), sigma w = (j ; i), i != j; two mate pairs cannot have the same unordered type {i, j};
  x_i has exactly 2 - f_i neighbours in W, where f_i is the number of vertices of A_p adjacent to x_i.
- (C-c) K = N(w) n X_2 is disjoint from A_p, |K| >= 2, K contains no mate pair, N(sigma w) n X_2 = tau K.
- (C-d) k in X_2 outside A_p has exactly req(k) = 2 - |N(k) n A_p| neighbours in W.
- The induced graph on S u {p} u X_2 u W is determined by (tau, F, H, types, K_1..K_5).
- Tests: a pair has at most 2 - A_uv common neighbours in any vertex set; principal submatrices of 9(3I - A) + J and 11(4I + A) - 2J
  are positive semidefinite; budget tests on spanning subgraphs are legitimate (adding edges only raises counts and lowers caps).

## What exists in one implementation only (B2)

- Search stages: none (stage 1: 2 programs, stage B: 2, stage C: 3, profile (3,3,1): 2).
- Shared by all programs: the hand reductions A0-A10, A14, N3 and the models above; the file `r2_tau_2.json` (checked by the second
  stage-1 program). `c_mine.py` starts from the enumerator's stage-B triples, which are identical to the verifier's set.
- A PSD "kept" decision is float-based and is never used as a proof.

## Open, not done

- B0 and B1 are other agents' pieces. `c_mine.py` runs unchanged on them (about 1.3 to 1.7 s per triple on the two B1 matchings, so
  roughly 2 CPU-hours for the 4977 triples of B1; not run).

## Reproduction (each line under 10 minutes on the shared laptop)

```
python r3_p250.py 2 0 2 560 BC ; python r3_p250.py 2 1 2 560 BC
python r3_verify.py stage1 2 ; python r3_verify.py B250 2 0 1 540
python r3_verify.py compareB 2 r3_p250_2_0of2_BC.json r3_p250_2_1of2_BC.json
python r3_verify.py C250 2 0 2 550          (then R3V_SKIP / R3V_TAKE: 0/86 and 86/86 with part 1 of 2, 172/24 with part 0 of 1)
python c_mine.py 2 0 1 520 r3_p250_2_0of2_BC.json r3_p250_2_1of2_BC.json
C_NOPSD=41 python c_mine.py 2 {0,1} 2 500 r3_p250_2_0of2_BC.json r3_p250_2_1of2_BC.json
python e331.py 2 0 1 280 ; python e331_compare.py 2 r2_hfirst_2_0of1.json
python rank_B1_survivors.py
```
