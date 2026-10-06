# T18 — report (2026-10-06, about 45 min of work)

**Status: T18 is NOT proved.** It is reduced, with complete proofs, to three explicit configurations
(S+ independent, no active h, orbit graph B one of three 4-regular graphs on 9 vertices). Everything else is excluded.

(Later rounds are appended below: "Round 2" and "Round 3". Current state: table "Where T18 stands after round 3".)

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

---

# Round 3 (2026-10-06, 21:03 - 22:30): profile (2,5,0) for B1, and an independent verifier

**Status after round 3: T18 NOT proved, and B1 is NOT closed.** Profile (2,5,0) for B1 was enumerated for all 1259
matchings, and it is NOT killed by adding the ten X_1 neighbours of p: exactly 4 configurations on 47 vertices survive
(exactly PSD, all budgets satisfied). The independent verifier confirms stage 1 for the three graphs and, on the
completed part, stage B for B1 (identical sets). Nothing was run for B0, B2 in this round. Final numbers: "End of round 3".

## R3-0. Checks of what I was given
- "a_2(w) >= ..." for the ten X_1 neighbours w of p: a_2(w) >= 2 (A14 b). The rest of the coordinator's description of
  profile (2,5,0) is correct.
- Correction to my round-2 text: A11/A12 are "computed, one implementation", as the coordinator says; nothing in round 3
  re-verifies profile (3,3,1) (the verifier below covers stage 1 and profile (2,5,0) only).

## A (round 3). Proved by hand

### A14. Forced structure of profile (2,5,0) when n_3 = 0
p is in X_0 with a_2(p) = 4, a_1(p) = 10, a_0(p) = 0. Write A_p = N(p) n X_2, W = N(p) n X_1.
a. A_p = two adjacent mate pairs. N(p) induces a perfect matching (the 7 edges {a_c, b_c}), so a vertex of A_p has no
   neighbour in N(p) except its mate: no edge between the two pairs, no edge A_p - W.
b. W = five mate pairs w = (i ; j), sigma w = (j ; i), i != j. For w in X_1: a_0 = a_2 - 1 (A8) and p is an X_0-neighbour, so
   a_2(w) >= 2. No edge inside W except the five mate edges.
c. sum_{v ~ p} a_2(v) = 2 n_2 - a_2(p) = 32, hence  sum_{A_p} (a_2 - 1) + sum_W (a_2 - 2) = 8.
d. s in X_2 \ A_p is not adjacent to p; their two common neighbours lie in N(p):  |N(s) n A_p| + |N(s) n W| = 2.
e. z in X_0 \ {p} is not in N(p), not adjacent to its mate, and |N(z) n A_p| + |N(z) n W| = 2.
f. Hence S u {p} u X_2 (37 vertices) is completely determined by (tau, F, H) (F = the 2 orbits of A_p, H = A[X_2]), and
   S u {p} u X_2 u W (47 vertices) by (tau, F, H, the five types, the sets N(w) n X_2), with N(sigma w) n X_2 = tau(N(w) n X_2).
g. Conditions on H alone: a_2 <= 4 on X_2; t = e(H) <= 9; sum_{A_p}(a_2 - 1) <= 8; and from (*) with sum_{X_0 \ p}(a - 4) = 2t
   spread over 4 sigma-orbits:  sum_{X_2} a(a-1) + 2 min{ sum y_q^2 : y in N^4, sum y_q = t } <= 36.
h. Subsets used as intermediate tests (each completely determined, w of type (i ; j), k in X_2 \ A_p):
   S u {p} u A_p u {w, sigma w} u {k, tau k} with w ~ k (27 vertices), the same with NO edge between {w, sigma w} and
   {k, tau k} ("forced orbit": if it fails, N(w) must meet {k, tau k}), and the 29-vertex set with two neighbours.

## Computed in round 3 (exact tests; "one implementation" unless stated otherwise)

### A15. B1, profile (2,5,0): enumerator `r3_p250.py` (H-first, then W pair by pair)
Stage B = all (tau, F, H) on the 37 vertices; stage C = W added (47 vertices). Tests: budgets and exact PSD on every
completely determined subset met (A14 f, h). A rejection is a budget violation or an integer vector x with x^T M x < 0
(exact integer arithmetic); "kept" never means "proved PSD" inside the enumerator.

**The enumeration is NOT complete.** Coverage after the first two launch rounds (each stopped by the 10-minute limit):
968 of the 1259 matchings completed, 291 not done (lists in `r3_coverage_B1.json`). On the 968 completed matchings:

| | count |
|---|---|
| triples (tau, F, H) passing stage B and the counting conditions A14 g | 2366 |
| stage-C survivors (configurations on 47 vertices) | **4**, in matchings #813 and #975 |

Raw counters, summed over the six runs (they include partial work on the 6 matchings interrupted by the time limit):
7939 pairs (tau, F); 106731 stage-B nodes; 2592 H; 230061 type solutions examined in stage C, 163248 of them dead by the
counting / forced-orbit tests (A14 h); 1105843 stage-C nodes; rejections: 570844 by budgets, 1162285 by PSD certificate;
0 cases where a float-negative matrix had no integer certificate.

**So profile (2,5,0) is NOT killed for B1 at the 47-vertex level: 4 configurations survive** (`r3_survivors.out`). For each of
them `r3_survivors.py` (independent code) confirms: support graph, X_2 types, N(p) = A_p u W, sigma-invariance, all budgets,
and both matrices are positive semidefinite EXACTLY (rational elimination; ranks 46 and 45 on 47 vertices).
They have t = e(X_2) = 4 (matching #813, F = [2,9] and [3,6]) and t = 2 (matching #975, F = [1,2] and [3,6]);
a_2 on W is 3 for six or eight vertices and 2 for the others.

### A16. Independent verifier `r3_verify.py` (no shared code; graphs re-entered as edge lists; numpy integer matrices)
1. **Stage 1, all three graphs** (different algorithm: last-index-first recursion, cell budgets recounted from scratch,
   rectangle admissibility recomputed from the 21-vertex single-type test, own automorphism search):
   B1: 99 rectangles, 13799 matchings, |Aut| 12, 1259 orbits; B0: 99, 25514, 72, 425; B2: 99, 9229, 18, 528.
   Identical to round 2, and the representatives stored in `r2_tau_<s>.json` are matchings of the verifier, pairwise
   inequivalent, one per orbit. **Stage 1 now has two agreeing implementations.**
2. **Stage B of profile (2,5,0), B1, all 1259 matchings** (orbits added in the reverse order, no pair prefilter, budgets by
   matrix products): 4977 triples (tau, F, H) in 121 s x 3. On the 968 matchings completed by the enumerator:
   verifier 2366 triples, enumerator 2366, **identical sets** (`r3_compare.out`). The 291 matchings not done by the
   enumerator carry 2611 triples, in 90 matchings.
   (The survivor set of stage B does not depend on the order of the search: budgets and PSD are hereditary.)
3. **Certificates**: 45000 PSD certificates saved (`r3cert_*.jsonl`, 24 MB in 6 files: the first 12000 of each first-round
   run, the first 3000 of each second-round run; vertex sets of 22 to 47 vertices). All 45000 re-checked: symmetric 0/1
   matrix, the first 18 vertices carry the support graph of B1, x^T M x < 0 in exact integer arithmetic; 0 invalid.
   The other PSD rejections (about 1.1 million) were not saved: the full set would be about 600 MB.
4. Stage C in the dual order (X_2 orbit by X_2 orbit) on the two matchings with survivors: see "End of round 3".

## B (round 3). Open, precisely

1. **B1, profile (2,5,0), n_3 = 0 (the only case left for B1):**
   a. the stage-C survivors on 47 vertices (4 found so far; list in the `survivors` field of the `r3_p250_1_*_BC.json` files);
   b. the matchings not yet enumerated at stage C (exact list and counts in "End of round 3").
   What is needed to close them ("stage D", NOT written): add the 8 vertices of X_0 \ {p} (4 sigma-orbits {z, sigma z}).
   Forced numbers for a given survivor: every s in X_2 has a_2(s) + 2 - [s in A_p] neighbours in X_0 \ {p}; every w in W has
   a_2(w) - 2; every z has a_2(z) >= 4, |N(z) n A_p| + |N(z) n W| = 2, no neighbour in S u {p}, z not~ sigma z,
   deg_{A[X_0]}(z) = a_2(z) - 4, sum over the 4 orbits of (a_2(z) - 4) = t. Then S u X_0 u X_2 u W (55 vertices) is determined.
2. B0, B2, profile (2,5,0), n_3 = 0: not run. `r3_p250.py 0 ...` and `r3_p250.py 2 ...` apply unchanged (A14 only uses
   n_3 = 0); stage B is cheap (B1: 2 minutes for all matchings in the verifier), stage C is the expensive part.
3. B0, B2, n_3 in {2, 4}: nothing done.
4. Profile (3,3,1) (round 2, A11/A12) is still "computed, one implementation": only its stage 1 is now double-checked.

## C (round 3). Tried, weak or failed

- Stage C in its first three versions was too slow (three 10-minute rounds lost): (i) plain W-pair-by-pair search with a
  full 39-vertex test per candidate set; (ii) plus the 27/29-vertex neighbour tests; (iii) plus a cache on the first pair.
  What finally helped: exact tests in numpy integer arithmetic, and the "forced orbit" test of A14 h (it kills about 70 %
  of the type solutions before any search). Even so the last 433 matchings are much denser than the first 826
  (10 to 50 matchings per 10 minutes per process), and the enumeration did not finish.
- Testing all type solutions of W on S u N[p] (33 vertices) before stage B: about 140 type solutions per (tau, F), 42 % pass,
  and no (tau, F) dies; it is now done only when stage B leaves some H.
- The hope that W would kill every H, as it killed all the Y-tables of profile (3,3,1), is false: 4 survivors.
- No time for: stage D, B0 and B2, n_3 > 0, a second implementation of profile (3,3,1), a complete second implementation
  of stage C.

## D (round 3). Files added

`r3_p250.py` (enumerator; the `_patch_r3*.py` files are the edits applied to it during the session, the final script is the
patched one), `r3_verify.py`, `r3_compare.py`, `r3_survivors.py`, `r3_summary.py`; outputs `r3_1_*_round1.out`, `r3_1_r2_*.out`,
`r3_1_r3_*.out`, `r3_p250_1_*.json` (totals, stage-B sets, survivors), `r3cert_*.jsonl` (certificates), `r3v_stage1_*.out`,
`r3v_B250_1_*.out/json`, `r3_compare.out`, `r3_coverage_B1.json`, `r3v_certs.out`, `r3_survivors.out`, `r3v_C250_*`.
Switches of `r3_p250.py`: R3_IDX (explicit list of matchings), R3_CERTCAP (number of certificates saved per run).

## End of round 3: final numbers for B1, profile (2,5,0)

Third launch round of the enumerator (2 processes, `r3_final.out`): 112 more matchings completed, no new survivor.

| after three launch rounds | |
|---|---|
| matchings completed by the enumerator (stages B and C) | 1080 of 1259 |
| stage-B triples (tau, F, H) on them: enumerator / independent verifier | 3498 / 3498, **identical sets** |
| stage-C survivors on them (47 vertices, exactly PSD, budgets exact) | **4** (matchings #813, #975) |
| matchings not done | 179; the verifier's stage B (complete on all 1259) gives 1479 triples on them, in 41 matchings; the other 138 have no stage-B triple |

Dual-order check of stage C (`r3_verify.py C250`, X_2 orbit by X_2 orbit, on matchings #813 and #975; stopped by its
time limit after 79 of their 170 triples, 1066592 nodes; `r3_compareC.out`): it finds 3 survivors, all three are survivors
of the enumerator, and it finds no survivor that the enumerator does not have; the 4th survivor of the enumerator lies
in a triple the verifier did not reach. So on the 78 triples fully processed by both programs the survivor sets agree.
This is a partial check: stage C as a whole still has one complete implementation.

A fourth launch round on the 41 remaining matchings that carry triples was started at 22:10 (3 processes, 440 s);
its outcome is in the last lines of this report ("Last round").

## Where T18 stands after round 3

| graph | profile (4,1,2) | profile (3,3,1) | profile (2,5,0), n_3 = 0 | n_3 > 0 |
|---|---|---|---|---|
| B1 | excluded, by hand (A9) | excluded, computed, one implementation (A11) | **open**: exactly 4 survivors on 47 vertices (stage C complete, see Final lines) | does not occur |
| B0 | excluded, by hand | excluded, computed, one implementation (A12) | not run | open (n_3 = 2, 4) |
| B2 | excluded, by hand | excluded, computed, one implementation (A12) | not run | open (n_3 = 2, 4) |

Double-checked by two independent programs: stage 1 for the three graphs; stage B of profile (2,5,0) for B1 on 1080
matchings; 45000 + saved certificates. Not double-checked: everything else computed.

## Last round (22:10 - 22:26)

Fourth launch (`r3_round4.out`): the 41 matchings carrying stage-B triples, 3 processes, 440 s. 38 of them completed
(997 triples), **no new stage-C survivor**; the time limit cut the three largest: #1089, #1091, #1092 (482 triples).
Fifth launch (started 22:18, 420 s): these three, plus the 138 matchings in which the verifier found no stage-B triple
(so that the enumerator also covers them). Outcome: see the final lines below.

**Final lines (22:23).** The fifth launch finished without time-out (`r3_round5.out`): all 1259 matchings of B1 are now
completed by the enumerator at stages B and C, and no further survivor appeared. Final comparison on everything
(`r3_finalB.out`):

| B1, profile (2,5,0), n_3 = 0, all 1259 matchings | |
|---|---|
| stage B, triples (tau, F, H) on 37 vertices: enumerator / independent verifier | 4977 / 4977, **identical sets** |
| stage C, configurations on 47 vertices (W added): enumerator | **exactly 4 survivors** (matchings #813 and #975) |
| saved PSD certificates, all re-checked by the verifier | 50000 in 14 files (26.5 MB), 0 invalid (`r3v_certs.out`, `r3v_certs2.out`) |

> **A17 (computed).** For B1 with profile (2,5,0): after adding W = N(p) n X_1, exactly 4 configurations on
> S u {p} u X_2 u W remain. Stage B is confirmed by two independent programs; stage C by one complete program, plus the
> dual-order check on 78 triples and the exact re-examination of the 4 survivors.
> **B1 is therefore reduced to these 4 explicit configurations, which need stage D (X_0), not written.**

Corrections to the text above, which was written while the runs were in progress: in A15 and in "End of round 3" the
coverage figures (968, then 1080 of 1259) are intermediate; item B.1.b (matchings not enumerated) is closed; in the
table "Where T18 stands", the B1 / (2,5,0) cell should read "open: exactly 4 survivors on 47 vertices".

---

# Round 4 (2026-10-06, 22:27 - 23:55): B1 only

Scope (coordinator, 22:31): B1 only; B2, B0, n_3 > 0 and profile (3,3,1) are handled by other agents; at most 2 processes.

**Status after round 4.** For B1 the last open profile (2,5,0) is now excluded: the X_0 stage kills each of the 4 survivors,
with two independent programs agreeing (A19). What is NOT double-checked for B1 is listed in the final table: stage C of
profile (2,5,0) (second implementation only partial, A20) and the whole of profile (3,3,1) (one implementation, round 2).
So "B1 is excluded" holds at the level "computed", not "proved"; T18 itself also needs B0 and B2 (other agents).

## R4-0. Checks of what I was given, and housekeeping
- `N3_REPORT.md` (n_3 = 0 by hand; a_0 <= 5; a_2 <= 3 on X_2, <= 6 on X_1, <= 8 on X_0 \ p): I read Lemma 1, Lemma 2, Theorem N3
  and the by-product; they agree with A8 and I found no error. Consequences for my text: A6 "d(a_c) <= 2" and "B1 has no
  d = 3 vertex" no longer depend on `rows.py`. My stage B used the weaker cap a_2 <= 4 on X_2 (a superset; harmless). The
  X_0 stage below did not need the new bounds: every candidate vertex of X_0 already fails.
- Before the scope change I had started B2: the verifier's stage B for B2 is complete (`r4v_B250_2.out`,
  `r3v_B250_2_0of1.json`: 196 triples (tau, F, H) for the 528 matchings, one implementation); the enumerator run on B2
  was stopped by me after 160 of 528 matchings and left no result file (`r4_B2_BC.out` is a partial log). Not my case any more.
- Other agents now run scripts with the same names on this machine. From 22:34 on I only wait for / stop processes by
  their PID. Files in this folder not listed in my "Files" sections are not mine.

## A (round 4)

### A18 (by hand). Forced numbers of the X_0 stage (profile (2,5,0), n_3 = 0)
Let Y47 = S u {p} u X_2 u W be a stage-C survivor and z in X_0 \ {p}. From A8 and A14:
z has no neighbour in S u {p} and is not adjacent to its mate; a_2(z) >= 4; |N(z) n A_p| + |N(z) n W| = 2;
every s in X_2 has a_0(s) = a_2(s) + 2 neighbours in X_0 (p is one of them iff s in A_p); every w in W has
a_0(w) = a_2(w) - 1 neighbours in X_0, p included; so a vertex of W with a_2 = 2 has no neighbour in X_0 \ {p}.
Hence Y47 u {z} (48 vertices) and Y47 u {z, sigma z} (49 vertices) are completely determined by Z = N(z) n (X_2 u W)
(sigma z sees the image of Z), and |X_0| = 9 requires 8 such vertices.

A general remark used below. If a completely determined set Y carries M = 9(3I-A)+J with M u = 0, then for every
vertex z outside Y:  9 * sum_{v ~ z, v in Y} u_v = sum_{v in Y} u_v   (a PSD matrix kills the vectors on which its
quadratic form vanishes). For Y containing N[p] the vector u = 4 e_p + 1_{N(p)} is always in the kernel
((3I - A + J/9) u = 0 in the whole graph), and the condition is just "z has 2 neighbours in N(p)".

### A19 (computed, TWO independent programs). The 4 survivors of B1 are impossible
For each of the 4 stage-C survivors, NO vertex of X_0 \ {p} can be added:

| survivor | t | candidate mate pairs {z, sigma z} passing the forced numbers and the budgets on 49 vertices | with no PSD violation |
|---|---|---|---|
| #813, F = [2,9] | 4 | 678 | **0** |
| #813, F = [3,6] | 4 | 678 | **0** |
| #975, F = [1,2] | 2 | 846 | **0** |
| #975, F = [3,6] | 2 | 846 | **0** |

- Program 1, `r4_stageD.py` (`r4_stageD_B1.out`): 6756 / 7868 generator nodes, 1712 / 2176 raw sets, 678 / 846 pass the budgets,
  every one is rejected by an integer vector x with x^T M x < 0; the 3048 certificates (one per candidate) are saved in
  `r4cert_stageD_B1.jsonl` and were re-checked by `r3_verify.py certs`: 3048 checked, 0 invalid, all on 49 vertices.
  (The later steps of the script - exact cover by 4 pairs, G = A[X_0], the 55-vertex test - were never reached.)
- Program 2, `r4_verifyD.py` (`r4_verifyD.out`; no shared code, own generator in decreasing order with the budgets
  recounted on 48 vertices after each addition): 1356 / 1356 / 1692 / 1692 oriented sets Z with an admissible mate
  (= 2 x 678, 2 x 846: the two generators agree); the budgets hold on all the 49-vertex graphs; an exact PSD violation
  is found for every one of them, **already on the 48 vertices Y47 u {z}**; 0 ambiguous floating-point cases.
  It also recomputes exactly (rational elimination) that M = 9(3I-A)+J on Y47 is PSD of rank 46 with kernel spanned by
  4 e_p + 1_{N(p)}: the kernel condition of A18 is therefore vacuous here, and the rejections are genuine eigenvalue
  violations, each with its certificate.

> So for B1 with profile (2,5,0), no configuration survives: stage 1 (2 implementations) -> 4977 triples at stage B
> (2 implementations, identical sets) -> 4 configurations at stage C (1 complete implementation; second one partial,
> A20) -> 0 at the X_0 stage (2 implementations).

### A19b (rank test; coordinator's argument, checked by my own exact computation). A second, simpler death of the 4 survivors
Argument (structural agent, `lemma\t18_STRUCT\REPORT.md` section 2; I re-derived the two facts it needs): 27I - 9A + J =
63 E_{-4} has rank 44; trace(sigma) = 1 and trace(sigma A) = 14 give trace 0 of sigma on V_3 and on V_{-4}, so sigma
splits V_{-4} as 22 + 22. Hence, for a sigma-invariant completely determined vertex set:
- the odd orbit matrix G_odd = 3I - A[R,R] + A[R, sigma R] (R = one vertex per non-fixed orbit) has rank <= 22;
- the even matrix (e_p and the e_v + e_{sigma v}) has rank <= 22.
A stage-C survivor has 47 vertices = p + 23 orbits. My script `r4_rank.py` (exact: rational elimination for the ranks,
fraction-free Bareiss for the determinant; no shared code; `r4_rank.out`) gives for the four survivors:

| survivor | odd part 23 x 23: rank, determinant | even part 24 x 24: rank |
|---|---|---|
| #813, F = [2,9] and F = [3,6] | 23, det = 47684 | 23 |
| #975, F = [1,2] and F = [3,6] | 23, det = 874944 | 23 |

Both exceed the bound 22: the four configurations are impossible. Same values as the structural agent's.
So the 4 survivors now die three ways: X_0 stage (A19, two programs), odd rank, even rank.

### A20 (computed). Stage C of profile (2,5,0), B1: second implementations
Three independent programs were used besides the enumerator `r3_p250.py` (none shares code with it; all start from the
verifier's own stage-B triples):
- v0 = `r3_verify.py C250` (dual order: X_2 orbit by X_2 orbit, full tests): correct but far too slow
  (about 10^6 nodes per 10 minutes; 117 triples of #813 / #975 in four runs);
- v1 = `r4_verifyC.py` (dual order, sigma-odd tests): too slow as well (29 triples in 620 s);
- v2 = `r4_verifyC2.py` (per W vertex: option table on 27 vertices, list FS of admissible N(w) n X_2 on 39 vertices; then
  exact cover of the requirements pair by pair; complete configurations get the full test). With sigma-odd tests in the
  cover stage it explodes on some triples (hundreds of complete configurations rejected only at the end); with the full
  test at every cover node (R4V_FULL=1) it is fast: 16 triples of #975 in 11 s.

Result on the two matchings that carry the survivors (`r4_compareC_final.out`):

| | |
|---|---|
| triples (tau, F, H) of #813 and #975 | 170 |
| completed by at least one second implementation | **170** (v0: 117, v1: 29, v2: 110) |
| enumerator survivors found again | 4 of 4: (813,[2,9]) by v0, v1, v2; (813,[3,6]) by v0; (975,[1,2]) by v0, v2; (975,[3,6]) by v2 |
| survivors of a second implementation unknown to the enumerator | 0 |
| enumerator survivors missed by an implementation that completed their triple | 0 |

So on #813 and #975 "exactly these 4 configurations survive stage C" is a two-implementation fact.
On the other 1257 matchings (4807 triples) the enumerator found no survivor; the second implementation v2 was started on
all 4977 triples at 23:35 and its coverage at the end of the session is given in "Final lines (round 4)".

### A21 (computed). The rank test on profile (3,3,1), B1 (coordinator's point 3)
In profile (3,3,1), Y = S u X_0 u X_2 has 22 non-fixed orbits, so the rank bound says nothing on Y; Y plus ONE mate pair
{w, sigma w} of W has 23 orbits and is completely determined (A10), so its odd matrix must be singular and its even matrix
(24 generators) must have rank <= 22. `r4_rank331.py` (`r4_rank331.out`; exact Bareiss determinant, exact ranks) on all the
Y-tables saved in round 2, with every type and every pair of X_2-neighbours allowed by the budgets on the 47 vertices:

| tables | number | candidates (type, neighbours) | pass budgets | odd matrix singular | both rank conditions | tables dead at the first pair: by rank / by PSD |
|---|---|---|---|---|---|---|
| passing PSD on Y (the complete list for B1, A11) | 164 | 295200 | 16334 | 2 | **0** | **164** / 162 |
| rejected by PSD on Y (saved samples only) | 15 | 27000 | 583 | 0 | **0** | **15** / 15 |

So the rank test alone kills every one of the 164 tables as soon as one pair of W is added (round 2 needed all three pairs
and PSD for 2 of them): for B1, step 4 of A11 ("Y u W: 0 left") is confirmed by a different test in different code.
It would also have made the PSD test on Y unnecessary on the 15 rejected samples; the 27203 - 164 - 15 other budget-valid
Y-tables were not saved, so this is not a re-proof of profile (3,3,1), only of its last step.
