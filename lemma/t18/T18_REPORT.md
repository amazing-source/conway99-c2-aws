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
