# T18 — report (2026-10-06, about 45 min of work)

**Status: T18 is NOT proved.** It is reduced, with complete proofs, to three explicit configurations
(S+ independent, no active h, orbit graph B one of three 4-regular graphs on 9 vertices). Everything else is excluded.

No solver was used: hand arguments, exhaustive backtracking, exact integer / rational arithmetic only.

## 0. Errors / corrections to the note (read first)

- Items 1, 2, 3, 4, 5 of section 3 of `LEMMA_TARGET_2026-10-06.md` are **correct** (re-derived, section A0).
- Item 4 stops too early: "e(S+) = 2 forces two disjoint edges and d(z) <= 1" is true but it is already a
  **contradiction** (82 edges must land on at most 81 outside vertices). So e(S+) = 2 is impossible (A2).
- Missing from the note: a **parity law** (A1) which kills pattern (ii) and e(S+) = 1 in two lines.
- The right PSD matrices are 3I - A + J/9 (= 7 E_{-4}) and 4I + A - (2/11) J (= 7 E_3); "A + 4I >= 0" is the weaker form.
  Scripts use 9(3I-A)+J and 11(4I+A)-2J.
- The "dictionary" of section 2 was used as given (only in A7 and in the lattice tests); not re-checked against project notes.

Notation: S+ = {x_0..x_8}, y_i = sigma x_i, S- = {y_i}; d+(v), d-(v) as in the task; for v outside S, d(v) = d+(v) = d-(v);
e = e(S+); Q = sum_{x in S+} d+(x)^2; k = number of active h = d+(inf).

## A. Proved

### A0. Checks of the given facts
- x ~ sigma x  =>  the unique common neighbour of x, sigma x is sigma-fixed, so it is inf. Conversely if x ~ inf and
  x not~ sigma x, the two common neighbours are inf and a second sigma-fixed vertex: impossible. So N(inf) = 7 edges {a_c, b_c}.
- x outside N[inf]: common neighbours of x, sigma x are {z, sigma z}; z in N(inf) would make x a common neighbour of the adjacent
  pair z, sigma z, i.e. x = inf. So z is a word vertex, x is never adjacent to both a_c and b_c, and O_x -> O_z is a
  fixed-point-free involution on the 42 word orbits.
- Item 1: (A phi)(x) = d+ - d-. Item 2: n_c = number of active words of star c; active c: n_c odd >= 3; inactive: n_c even;
  sum n_c = 2(9-k); k = 1,3,5 fail by parity, k = 4,6,7 by size. Item 3: e(S) = 4e + 36, 2 e(S) <= 90.
- Item 4, general form for |S+| = m: **sum_{z not in S} C(d(z),2) = m^2 - 7m - 7e - Q** (m = 9: 18 - 7e - Q). Also
  sum_{z not in S} d(z) = 10m - 4e (= 90 - 4e).
- Item 5: correct; the spectral condition is automatically satisfied by the 3 graphs that pass the codegree condition.

### A1. Parity law (new; holds for every sigma-odd {0,+-1}-valued (-4)-eigenfunction, any support size m)
> **e(S+) = C(k, 2) (mod 2).**

Proof. sigma pairs the vertices outside S other than inf, and d(sigma z) = d(z); so sum_{z not in S, z != inf} C(d(z),2) is even.
d(inf) = k. m^2 - 7m is even and Q = sum d+^2 = sum d+ = 2e = 0 (mod 2). Hence 7e + C(k,2) is even. QED.

For T18: k = 0 forces e even; k = 2 forces e odd.

### A2. e(S+) = 2 is impossible
Q = 4 (two disjoint edges) gives sum C(d,2) = 0, so d(z) <= 1 outside S; but sum d(z) = 90 - 8 = 82 > 81 = number of vertices
outside S. (Path: Q = 6, sum C(d,2) < 0.)

### A3. e(S+) = 1 is impossible (both patterns)
By A1 only k = 2 could occur; here is a direct proof for all cases. M_j = {i != j : x_j ~ y_i}.
- Plus edge x_0 ~ x_1 between two word orbits. |M_0| = |M_1| = 5. If 1 not in M_0 then M_0, M_1 are 5-subsets of {2..8}, they share
  >= 3 elements j, and each y_j is a common neighbour of the adjacent pair x_0, x_1: contradiction. So 1 in M_0, 0 in M_1;
  P = M_0\{1}, Q = M_1\{0} are 4-subsets of {2..8} with |P n Q| = 1 = {k}, P u Q = {2..8}.
  For j in P\{k}: common neighbours of x_j, x_0 give |M_j n P| + [j is h] <= 2; common neighbours of x_j, x_1 (y_0 is one) give
  |M_j n Q| <= 1; |M_j| = 4 - [j is h] then forces k not in M_j. Same for j in Q\{k}. So M_k is inside {0,1}, but |M_k| >= 3.
- Plus edge x_0 ~ a_c = x_7 (word - h). x_0 not~ y_7, |M_0| = 5 inside {1..6,8}; |M_7| = 4 inside {1..6}; they share >= 2 elements,
  each a common neighbour of the adjacent pair x_0, x_7: contradiction.

Machine confirmation (two independent enumerators, different algorithms): `enum_S.py`, `verify_S.py` give 0 structures for every
e = 1 and e = 2 case (outputs in section D).

### A4. Pattern (ii) (two active h) is impossible
A1 with k = 2 forces e odd, i.e. e = 1, excluded by A3. Directly for e = 0: sum over outside z of C(d,2) = 18, inf contributes
C(2,2) = 1, the other 80 vertices contribute an even number: 17 is odd.
Machine confirmation: `enum_S.py` finds 4 S-structures for pattern (ii), e = 0; `level1.py` proves exhaustively that none of
them admits a consistent family of outside neighbourhoods (6133, 20064, 54939, 67423 nodes, "NO LEVEL-1 SOLUTION").

### A5. Consequence: the only remaining case
> S+ is independent, S is disjoint from N[inf], and x_i ~ y_j iff i ~ j in a 4-regular graph B on 9 vertices in which any two
> vertices have at most 2 common neighbours. Up to isomorphism there are exactly **3** such B (all pass every S-level PSD test).

Enumeration: `enum_S.py` (row 0 fixed: 792 labelled, 3 classes) and `verify_S.py` (no symmetry breaking: 55440 labelled, 3 classes;
55440 = 9!/72 + 9!/12 + 9!/18 matches the automorphism orders below).

| | B (edges i~j, i.e. x_i ~ sigma x_j) | Aut | triangles | spectrum | codegrees (adjacent / non-adjacent pairs) |
|---|---|---|---|---|---|
| B0 = K3 x K3 (Paley 9) | 01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78 | 72 | 6 | 4, 1^4, (-2)^4 | adj: 18 x 1 / non: 18 x 2 |
| B1 | 01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78 | 12 | 8 | 4, 2, 1^2, (-1)^2, (-2)^3 | adj: 12 x 1, 6 x 2 / non: 6 x 1, 12 x 2 |
| B2 = C9(1,2) (circulant) | 01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78 | 18 | 9 | 4, (-2)^2, roots of t^3-3t-1 twice | adj: 9 x 1, 9 x 2 / non: 9 x 1, 9 x 2 |

### A6. Facts proved about any of the three survivors (e = 0, pattern (i))
- Every vertex z outside S with d(z) = k has sum_{w ~ z, w not in S} d(w) = 18 - 5k; hence d <= 3.
  With n_k = number of vertices outside S with d = k (inf included): n_0 = 9 - n_3, n_1 = 54 + 3 n_3, n_2 = 18 - 3 n_3,
  and n_3 is even (sigma). inf has d = 0; sum_c d(a_c) = 9.
- Each of the 36 edges x_i ~ y_j has its triangle vertex w_ij outside S (the w_ij need not be pairwise distinct);
  for an outside w and j in N-(w), |N+(w) n B(j)| <= 1. z_i (common neighbours of x_i, y_i) are outside S, not in N(inf), and N+(z_i) n N-(z_i) = {i}.
- `rows.py` (graph filters + exact PSD on S u {inf, w, sigma w}, integer certificate for each rejection):
  d(a_c) <= 2 for all c in all three cases (B0: 12 graph-admissible types with d = 3, all 12 rejected by PSD; B1, B2: none);
  **B1: no outside vertex with d = 3 at all** (12 types, all rejected), so n = (9, 54, 18, 0);
  B0: 6 sigma-classes of d = 3 types remain (N+ a line, N- a parallel line); B2: 9 classes.
  Admissible d = 2 types: 99 sigma-classes (not adjacent to inf) and 63 (adjacent to inf) in each of the three cases.

### A7. Conditional on H16 (the 04/10 lemma: no non-zero sigma-odd integer (-4)-eigenfunction of squared norm <= 16)
With G the orbit Gram matrix and c = 1_T, every k c + G n (k in Z, n in Z^49) is such an eigenfunction, so
Q(k,n) = 9k^2 + 14k (n.1_T) + 7 n^T G n is never in {1..8}. Consequences:
- For every independent triple I of B and every inactive word orbit O: |sum_{i in I} (f_O, f_i)| <= 1
  (n = -1_I +- e_O gives Q(2,n) = 36 -+ 14 sum; B0, B1, B2 have 6, 4, 3 independent triples).
- B has no independent 4-set, no 5-set with <= 2 edges (true for B0, B1, B2: `latt_T.py` finds no value 1..8 on T;
  `check_iso.py`: independence number 3 for all three).
- (H16 does NOT give a second proof of e = 0: on a plus edge the state "x_i ~ x_j and x_i ~ y_j" is forced by A3, and then
  (f_i, f_j) = 0.)
This tool removed **nothing** beyond PSD in any test I ran (section C).

## B. Open (precise)

T18 is equivalent to excluding, for each B in {B0, B1, B2}:

> 9 word orbits {x_i, y_i}, S+ = {x_i} and S- = {y_i} independent, x_i ~ y_j iff i ~_B j, no vertex of S in N[inf].

For each of the three, a complete sigma-closed assignment of neighbourhoods in S to all 80 other vertices exists that gives every
pair of S u {inf} exactly its lambda/mu common neighbours (`level1.py`, example printed in `level1.out`): 7 h-pairs, quads, 44
vertices with d = 1, 8 vertices with d = 0. So the obstruction, if any, needs the adjacency **among** the outside vertices.
Not done: any search on that adjacency; a full count of level-1 solutions; the case analysis on d = 3 vertices for B0, B2.

What a continuation would have to use (untested): for every outside v and every s in S the number of outside neighbours of v
adjacent to s is forced, c_s(v) = (1 or 2) - |N(v) n N(s) n S|. Whether these forced counts, made mutually consistent
(u ~ v symmetric, lambda = 1, mu = 2 between outside vertices), can be satisfied is exactly the open question. The level-1
families are too many (more than 10^4 found per graph in 4 minutes, enumeration not finished) to be used as a first stage as is.

## C. Tried, did not work

- Exact PSD (E_{-4} and E_3) on S, on S u {inf}, on S u {inf, w, sigma w}: kills no S-structure, only the types listed in A6.
- Exact PSD + lattice test on S u {inf} u N(inf) (33 vertices, all adjacencies known), `ninf.py`. NOT exhaustive (time limit):
  B0: 59962 configurations examined in 420 s, 22666 rejected by PSD, 1620 by lambda/mu, 35654 survive;
  B1: 73324 examined, 41508 rejected, 31816 survive; B2 (60 s): 16723 examined, 11455 rejected, 5266 survive. Lattice test: 0 rejections.
- Level-1 enumeration plus test F1 (the 6 "free" outside neighbours of each x_i must be perfectly matched into pairs sharing no
  other neighbour in S u {inf}), `level1_count.py`. NOT exhaustive (240 s each, stopped by the time limit):
  B0: 12777 level-1 solutions found, 0 fail F1; B1: 15071, 0 fail; B2: 10005, 0 fail. Level 1 is far too loose.
- sigma-parity with weights: for g = (A a) restricted outside S, a any sigma-symmetric or antisymmetric integer vector on S,
  the edge-sum parity condition reduces to "(B^3 + B)_ii even", always true. Vacuous.
- Counting on the partition {S, D_0, D_1, D_2}: only e(D_0) = e(D_2) <= 9 (when n_3 = 0); no contradiction.
- Hand analysis of the hexagons of B0 (lines of K3 x K3): forced facts only, no contradiction.
- I could not locate `VERIF_CUBE_OBSTRUCTION_2026-10-04.md`, so I do not know how the 8-orbit analogues were killed; H16 is used
  only in A7, flagged conditional.

## D. Files (all in this folder) and exact outputs

- `enum_S.py` -> `structures.json`. Output:
  `(i) e=0: labelled 792, iso classes 3, killed by PSD 0, surviving 3` / `(ii) e=0: 56, 4, 0, 4` /
  `(i) e=1: 0` / `(ii) e=1 word-word: 0` / `(ii) e=1 word-h: 0` / `(i) e=2 disjoint: 0` / `(i) e=2 path: 0`.
- `verify_S.py` -> `verify_S.out`: all e=1 and e=2 cases `labelled 0`; `(ii) e=0: labelled 17640, iso classes 4`;
  `(i) e=0: labelled 55440, iso classes 3`.
- `show_structs.py` -> `show_structs.out` (edge lists, Aut, characteristic polynomials, codegrees; exact, sympy).
- `check_iso.py` -> `check_iso.out`: B0 isomorphic to K3 x K3, B2 isomorphic to C9(1,2), B1 to neither; independence numbers.
- `latt.py` (exact LDL, PSD test, Fincke-Pohst), `latt_T.py` -> `latt_T.out`, `test_fp.py` (cross-check against brute force).
- `rows.py` -> `rows.out`, `types.json` (admissible outside types per structure).
- `ninf.py` -> `ninf_*.out/json`. `level1.py` -> `level1.out`. `level1_count.py` -> `l1c_0_*.out`.

Caveat on rigour: the rejections by PSD are certified by exact integer vectors; "survives" only means "no certificate found".
The hand proofs A1-A4 do not depend on any script.

---

# Round 2 (2026-10-06, 20:02 - 21:10): adjacency among the vertices outside S

**Status after round 2: T18 still NOT proved.** New: two of the three profiles of N(inf) are excluded for B0, B1 and B2
(one by hand, one by exhaustive computation); the remaining profile (2,5,0) is not enumerated. See "Summary of round 2".

Notation of the 04/10 notes: p = inf, P = S+, Q = S-, X_d = vertices outside S with d = d, n_d = |X_d|;
for a vertex z, a_k(z) = number of neighbours in X_k (a = a_2, b = a_1, c = a_0 when n_3 = 0); t = e(X_2);
delta_c = d(a_c); h_k = number of the 7 pairs {a_c, b_c} with delta_c = k, so 2 h_2 + h_1 = 9, h_2 + h_1 + h_0 = 7,
i.e. h_2 = 2 + h_0, h_1 = 5 - 2 h_0. Profile (h_2, h_1, h_0) = (2,5,0), (3,3,1) or (4,1,2).

## R2-0. Checks of what I was given
- Coordinator items 1, 2, 3, 4, 5: correct (re-derived). Item 2 can be sharpened: t <= 9, not 16 (A8).
- Cube note sections 2-4, 7 and Wagner note sections 2-4: read and used as a model; their finite enumerations were not re-run.

## A (round 2). Proved

### A8. Counting identities for m = 9 (e = 0, pattern (i))
For z in X_d:  3 a_3 + 2 a_2 + a_1 = 18 - 5d  and  a_0 = a_2 + 2 a_3 + 3d - 4.
(Round-1 identity sum_{w ~ z, w outside S} d_w = 18 - 5d, and deg = 14.)
When n_3 = 0 (always for B1): |X_0| = 9, |X_1| = 54, |X_2| = 18;
X_0: a >= 4, c = a - 4;  X_1: a >= 1, c = a - 1, b = 13 - 2a;  X_2: a <= 4, c = a + 2, b = 8 - 2a;
e(X_0) = e(X_2) = t, e(X_0, X_2) = 36 + 2t, sum of a over X_0, X_1, X_2 = 36 + 2t, 144 - 4t, 2t, sum of a^2 = 576 - 2t, hence

> (*)  sum_{X_0} (a-4)^2 + sum_{X_1} (a-2)(a-3) + sum_{X_2} a(a-1) = 36,   and so  h_2 <= t <= 9.

(t <= 9: sum_{X_0}(a-4) = 2t and Cauchy-Schwarz on 9 terms. t >= h_2: the h_2 pairs of N(p) in X_2 are edges of X_2.)
For every vertex v: sum_{w ~ v} a_2(w) = 12 [v in X_2] + 2 n_2 - a_2(v)   (A^2 = 12I - A + 2J applied to the indicator of X_2).

### A9. h_0 <= 1; more precisely 4 h_0 + n_3 <= 4   (all three graphs)
Put omega(w) = a_2(w) + 2 a_3(w). At p: sum_{w ~ p} omega(w) = (2 n_2 - a_2(p)) + 2 (2 n_3 - a_3(p)) = 36 - 2 n_3 - 2 h_2
(n_2 = 18 - 3 n_3, a_2(p) = 2 h_2, a_3(p) = 0 by A6). Lower bounds from a_0 = omega + 3d - 4:
- a neighbour of p in X_2 is adjacent to its mate, which is in X_2: omega >= 1;
- a neighbour of p in X_1 has p as X_0-neighbour: a_0 >= 1, omega >= 2;
- a neighbour of p in X_0 has p and its mate as X_0-neighbours: a_0 >= 2, omega >= 6.
So 2 h_2 + 4 h_1 + 12 h_0 <= 36 - 2 n_3 - 2 h_2, i.e. 28 + 8 h_0 <= 36 - 2 n_3.  QED.

Consequences:
- **Profile (4,1,2), i.e. the multiset (2,2,2,2,1,0,0) of the delta_c, is impossible for B0, B1 and B2.**
- Profile (3,3,1) forces n_3 = 0 and equality everywhere (A10). Profile (2,5,0) forces n_3 <= 4.

### A10. Forced structure of profile (3,3,1) (then n_3 = 0)
Equality in A9 gives: the 6 vertices of A_p := N(p) n X_2 have a = 1 (no X_2-neighbour except the mate) and c = 3;
the 6 vertices of N(p) n X_1 have a = 2, c = 1; the pair {z_0, sigma z_0} = N(p) n X_0 has a = 6, c = 2.
z_0 ~ p and z_0 ~ sigma z_0 give A_{z_0} n A_p = A_{z_0} n A_{sigma z_0} = empty, so
**X_2 = A_p + A_{z_0} + A_{sigma z_0} (disjoint, 6 + 6 + 6)**: A_{z_0} takes one vertex in each of the 6 orbits of X_2 outside N(p).
Each of the other 6 vertices of X_0 sees exactly 2 vertices of A_p (12 incidences needed, at most 2 each).
Hence Y1 = S u {p} u X_2 u {z_0, sigma z_0} (39 vertices) is completely determined by (tau, F, H, A_{z_0}), where tau is the
matching of the 18 deficient pairs, F the 3 orbits of X_2 in N(p), H = A[X_2].

### A11. B1, exhaustive computations (exact; every PSD rejection is certified by an integer vector)
B1 has no d = 3 vertex (A6), so n_3 = 0 and A8-A10 apply.

1. `r2_stage1.py 1` (matchings of the deficient pairs, tests (i), (i'), (iii) of the Wagner note plus the single-type PSD test):
   18 deficient pairs, 99 admissible rectangles {U,V}, **13799 matchings tau, 1259 orbits under Aut(B1)** (Wagner: 31).
2. Profile (3,3,1), `r2_hfirst.py` on all 1259 representatives (3 parts, 130 s, 130 s, 10 s). Counts, summed:

   | stage | count |
   |---|---|
   | (tau, F) passing the N(p) tests (two vertices of A_p share <= 1 support neighbour, every P_i seen <= 2 times, the 3 pairs of N(p) n X_1 exist) | 7224 |
   | after budgets + PSD on S u {p} u A_p u (one or two more orbits of X_2) | 750 |
   | complete H | 927 |
   | (H, A_{z_0}) tested on Y1 (39 vertices) | 4416 |
   | **survivors (tau, F, H, A_{z_0})** | **481**, in 55 matchings, 76 pairs (tau, F) |

   Rejections: 17226 by common-neighbour budgets, 16750 by PSD with an integer certificate, 0 by exact elimination alone.
   The violated matrix is 9(3I-A)+J, in its sigma-odd part (`r2_diag.out`).
3. Extension of the 481 survivors to Y = S u X_0 u X_2 (45 vertices; the 3 remaining orbits of X_0 and G = A[X_0]),
   `r2_stage2.py` restricted to them (R2_SURV), budgets + exact PSD on Y: see R2-RESULT below.
4. `r2_ext2.py`: the 6 vertices W = N(p) n X_1 are added to every PSD-surviving Y-table. Y u W (51 vertices) is completely
   determined by the 3 types (i_c ; j_c) and by the 2 neighbours of each w_c in X_2 (each vertex of X_2 outside A_p is adjacent to
   exactly one vertex of W: it has 2 common neighbours with p, one is z_0 or sigma z_0, none is in A_p). See R2-RESULT below.

Cross-checks: `r2_check_example.py` (independent rebuild of rejected tables: 0 budget violations, the forced kernel vector
3*1_S - 1_{X_0} + 1_{X_2} of 9(3I-A)+J is reproduced exactly); `r2_hfirst_check.py` (exact rational elimination agrees with the
integer certificates on Y1); `r2_hfirst_check2.py` (the Y-tables found by the X_0-first program `r2_stage2.py` restrict to
configurations that the PSD-free run of the H-first program lists: 3 of 3).

**R2-RESULT for B1 (steps 3 and 4), exhaustive, no time-out:**

| step | count |
|---|---|
| matchings / pairs (tau, F) / configurations entering step 3 | 55 / 76 / 481 |
| completions C (the 3 other orbits of X_0) | 93684 |
| Y-tables passing the common-neighbour budgets on Y (45 vertices) | 27203 |
| rejected by PSD on Y (integer certificate) | 27039 |
| **Y-tables passing budgets and PSD** | **164** (in 9 matchings) |
| step 4: type solutions for W / nodes | 2060 / 124992 |
| rejected in step 4 by budgets / by PSD certificate / by exact elimination alone | 119016 / 5918 / 0 |
| **configurations on Y u W left** | **0** |

> **A11. For B1, profile (3,3,1) is impossible.** With A9: for B1 the multiset of the delta_c is (2,2,1,1,1,1,1), i.e.
> exactly two of the seven pairs {a_c, b_c} have delta_c = 2, five have delta_c = 1, none has delta_c = 0; a_2(p) = 4, t >= 2.

Status of A11: exhaustive computer enumeration (hand reduction A8-A10 + scripts above). Steps 2, 3, 4 each exist in one
implementation only, written during this session; the cross-checks listed above are partial. Every rejection is exact
(budget count or integer vector with negative quadratic form); "passing PSD" is never used as a proof of anything.

### A12. Same pipeline for B2 and B0 (profile (3,3,1) forces n_3 = 0 by A9, so A10 applies verbatim)
- Stage 1 (case n_3 = 0): B0: 25514 matchings, 425 orbits under Aut (order 72); B2: 9229 matchings, 528 orbits (order 18).
- **B2**: step 2 (`r2_hfirst.py 2`, all 528): 2406 pairs (tau, F), 114 after the pair tests, 16 complete H, 121 tested on Y1,
  **7 survivors, in one matching**; step 3 on these: 44 completions C, **0 Y-tables pass the budgets**.
  > **For B2, profile (3,3,1) is impossible** (same status as A11). B2 keeps only profile (2,5,0), with n_3 in {0, 2, 4}.
- **B0**: step 2 (`r2_hfirst.py 0`, all 425): 3510 pairs (tau, F), 624 after the pair tests, 1618 complete H, 3810 tested on Y1,
  383 survivors in 50 matchings. Steps 3-4: see R2-RESULT-B0 at the end of this section.

## B (round 2). Open, precisely

1. **Profile (2,5,0) for all three graphs** (delta = (2,2,1,1,1,1,1)): p has exactly 4 neighbours in X_2 (two adjacent mate pairs),
   10 in X_1, none in X_0; no vertex of X_0 lies in N(p). Not enumerated. Known restrictions when n_3 = 0: identity (*),
   2 <= t <= 9, sum over N(p) of a_2 = 32 (so sum_{4 X_2 neighbours}(a-1) + sum_{10 X_1 neighbours}(a-2) = 8).
   Size of what remains for B1 at the first stages: 1259 matchings up to Aut(B1); in a partial run of `r2_gram.py`
   (258 of the 1259 matchings, stopped by the time limit) 1262 pairs (tau, F) with |F| = 2 passed the sigma-odd Gram test,
   in 235 matchings. The H-first stage for this profile (the determined set is S u {p} u X_2, 37 vertices, with H free on all
   9 orbits and A_p vertices allowed further X_2-neighbours) is not written.
2. **n_3 > 0** (only B0 and B2, only profile (2,5,0), n_3 = 2 or 4): nothing done beyond A9; the matching description of X_2
   must then be replaced by 18 - 3 n_3 vertices of X_2 plus n_3 vertices of X_3 (types: B0 6 classes, B2 9 classes, A6).
3. (closed) B0, profile (3,3,1): excluded, see R2-RESULT-B0.

## C (round 2). Tried, weak or failed

- "Star" test `star.py` (S u {inf} u N(x_I) u N(y_I), 37 determined vertices, budgets + PSD): B1, I = 0: 1905 level-1 stars;
  8 examined in 97 s, 7 alive (2862 completions pass). Abandoned.
- X_0-first enumeration of Y-tables (`r2_stage2.py` unrestricted): correct but slow: profile (3,3,1), B1: 14 matchings in 580 s
  (11270 Y-tables, all rejected by PSD); the first version (all profiles at once) did not finish one trial in 200 s.
  It is now used only restricted to the survivors of the H-first stage.
- sigma-odd Gram completion on T u X_2 alone (`r2_gram.py`): keeps most pairs (tau, F) (trial on 13 matchings: 124 pairs
  alive for h_2 = 2, 38 for h_2 = 3). The full graph tests of `r2_hfirst.py` are much stronger.
- The cube double count does not transfer: here the pairs of X_2 have a budget of 198 - t common neighbours outside S and the
  X_0 vertices need only sum C(a,2) >= 54 + 8t of it; with (*) this leaves 2 <= t <= 9.

## D (round 2). Files added (same folder)

`r2_stage1.py` (-> `r2_tau_<s>.json`, `r2_stage1_<s>.out`), `r2_hfirst.py` (-> `r2hf_*.out`, `r2_hfirst_<s>_*.json`),
`r2_stage2.py` (-> `r2ext*.out`, `r2_stage2_*_surv*.json`), `r2_ext2.py` (-> `r2_ext2_*.out`), `r2_summary.py` (-> `r2_summary_1.out`),
`r2_gram.py`, `star.py`, checks `r2_check_example.py`, `r2_hfirst_check.py`, `r2_hfirst_check2.py`, `r2_diag.py`,
`r2_ext2_bruteforce.py`; B0 / B2 outputs: `r2_stage1_0.out`, `r2_stage1_2.out`, `r2hf_0_all.out`, `r2hf_2_all.out`,
`r2ext_0_g*.out`, `r2ext_2.out`, `r2_ext2_B0.out`, `r2_summary_0.out`
(the `_patch_*.py` files are the edits applied to `r2_stage2.py` / `r2_hfirst.py` during the session; the final scripts are
the patched ones). Environment switches: R2_SURV (restrict `r2_stage2.py` to H-first survivors), R2_IDX (explicit matchings),
R2_CAP (number of survivors saved), R2_NOPSD (cross-check mode).

## R2-RESULT-B0 (steps 3 and 4 for B0, exhaustive, no time-out)

| step | count |
|---|---|
| matchings / pairs (tau, F) / configurations entering step 3 | 50 / 95 / 383 |
| completions C | 23155 |
| Y-tables passing the budgets on Y | 8639 |
| rejected by PSD on Y (integer certificate) | 8616 |
| Y-tables passing budgets and PSD | 23 (in 9 matchings) |
| step 4: type solutions for W / nodes | 242 / 14520 |
| rejected in step 4 by budgets / by PSD certificate / by exact elimination alone | 14165 / 355 / 0 |
| **configurations on Y u W left** | **0** |

> **For B0, profile (3,3,1) is impossible** (same status as A11).

## Summary of round 2

> **A13 (A9 + A11 + A12).** For each of B0, B1, B2 the neighbourhood of inf has profile (2,5,0): exactly two pairs
> {a_c, b_c} with delta_c = 2, five with delta_c = 1, none with delta_c = 0. Equivalently a_2(inf) = 4, no vertex of X_0 is
> adjacent to inf, and n_3 = 0 (B1) or n_3 in {0, 2, 4} (B0, B2).

Proof status: (4,1,2) by hand (A9); (3,3,1) by the exhaustive computation above (A10 + scripts), for the three graphs.
T18 itself stays open: profile (2,5,0) is not enumerated for any of the three graphs (section B, items 1 and 2;
item 3 is closed by R2-RESULT-B0).

### Additional cross-check of step 4 (`r2_ext2_bruteforce.py` -> `r2_bf_B0.out`, `r2_bf_B1.out`, `r2_bf_B1b.out`)
Nine PSD-surviving Y-tables (3 of B0, 6 of B1) were re-done without any pruning: 15 type candidates x 5760 complete
assignments = 86400 graphs on 51 vertices per table, budgets by integer matrix multiplication. Budget-valid graphs:
12, 12, 2 (B0) and 39, 39, 39, 0, 0, 0 (B1); PSD-valid: 0 in all nine. Same conclusion as `r2_ext2.py`.
This checks the search code, not the modelling (A10 and the description of W), which rests on the arguments written above.

### What a reviewer should re-check first
1. A9 (five lines, by hand) and the equality case A10.
2. That Y1, Y and Y u W are completely determined as claimed (A10, step 4): every "no other neighbour" used there comes
   from an equality a = 1, a = 2, c = 1, c = 2 or c = 3 forced in A10.
3. The three scripts `r2_hfirst.py`, `r2_stage2.py` (R2_SURV mode), `r2_ext2.py`: single implementations.
