# T20 — report, round 1 (2026-10-06, 22:20 - 23:35)

**Status: T20 is NOT proved.** It is reduced to **nine explicit configurations** on the support S (six with no active
inner orbit, one with two, two with four). Everything else is excluded: the values +-2 and +-3, the pattern with a +-2 on
an inner orbit, every e(S+) >= 2, and the word-inner plus edge are excluded **by hand**; the list of nine is **computed**
(two independent programs, in agreement on all four cases, B1 and B2).

No solver was used: hand arguments, exhaustive backtracking, exact integer / rational arithmetic only.
Neither T18 nor the 04/10 lemma is used anywhere in this report.

## 0. Read first: one discrepancy in the task I was given

The task text says "sum of phi(x)^2 = 40 (20 per side)". Everything else in it (norm 10/7 in the dual of the frame lattice,
"m = 10 positive vertices", the four root patterns "10 outer / 2 + 8 / 4 + 6 / one +-2 and 6 outer") and
`LEMMA_TARGET_2026-10-06.md` section 2 ("T20: none of squared norm 20") say:

> **T20: no integer phi with phi o sigma = -phi, A phi = -4 phi and sum_x phi(x)^2 = 20** (10 per side; orbit vector c with
> |c|^2 = 10; N = 10/7).

**This is the statement treated here.** (Same factor 2 in the task text for the 04/10 lemma, "<= 32" for 16, and for T18,
"36" for 18.) If squared norm 40 (N = 20/7) was really meant, nothing below applies to it.

Notation: p the fixed vertex; orbit vector c_O = phi(x), O = {x, sigma x}; G = 3I - A^ the orbit Gram (4 on the 7 inner
orbits, 3 on the 42 outer ones, off-diagonal entries in {0, +-1}), G c = 7 c. For a {0,+-1}-valued phi: S+ = {phi = 1} =
{x_0..x_9}, y_i = sigma x_i, S- = {y_i}, S = S+ u S-; d+(v), d-(v) = numbers of neighbours in S+, S-; for v outside S,
d(v) = d+(v) = d-(v); e = e(S+); Q = sum_{S+} d+(x)^2; k = number of active inner orbits = d(p);
X_d = {z outside S : d(z) = d}, n_d = |X_d| (p included); "word" = outer orbit / vertex outside N[p].
M_j = {i != j : x_j ~ y_i}. "Minus edge" i-j: x_i ~ y_j (and x_j ~ y_i); "plus edge" i-j: x_i ~ x_j (and y_i ~ y_j).

## A. Proved by hand

### A0. Facts used (re-derived, as in T18 A0)
- x ~ sigma x iff x in N(p); N(p) = 7 edges {a_c, b_c} and induces a perfect matching (an edge p-a_c has the single common
  neighbour b_c). A vertex z != p is never adjacent to both a_c and b_c. A word has exactly 2 neighbours in N(p) (mu = 2
  with p), in two different pairs.
- A word x may be adjacent to both z and sigma z (then z, sigma z are the two common neighbours of x, sigma x: a "quad");
  an inner x may not.
- Eigen-equation: (A phi)(x) = -4 phi(x). For {0,+-1} values: d-(x) = d+(x) + 4 on S+, d+(z) = d-(z) outside S.

### A1. Values: only {0, +-1} on outer orbits, {0, +-1, +-2} on inner ones; no +-3; no +-2 on an outer orbit
At a vertex x of value c != 0, sum_{w ~ x} phi(w) = -4c. If x is inner, sigma x contributes -c and no other orbit
contributes twice; if x is outer, an orbit contributing twice contributes 0. Hence
**sum_{O' != O} |c_{O'}| >= 3|c_O| (O inner), >= 4|c_O| (O outer).**
The multisets of |c| with sum of squares 10 are {3,1}, {2,2,1,1}, {2,1^6}, {1^10}:
- {3,1}: needs >= 9, has 1. Impossible.
- {2,2,1,1}: needs >= 6, has 4. Impossible.
- {2,1^6}: needs >= 6 (inner) or >= 8 (outer), has 6. So the 2 sits on an inner orbit and all six +-1 orbits are joined
  to it with the right sign (they are outer: inner orbits are mutually orthogonal). Excluded in A2.
- {1^10}: k inner orbits and 10 - k outer ones, A3.

So **the general case adds nothing to the root case**: +-3 anywhere and +-2 on an outer orbit are impossible for
|c|^2 = 10. T20 in general is equivalent to T20 for the root-type patterns.

### A2. The pattern "one inner orbit at +-2, six outer orbits at +-1" is impossible
Let x in N(p), phi(x) = 2, phi(sigma x) = -2, and x_1..x_6 (phi = 1), y_i = sigma x_i (phi = -1) the rest of the support.
At x: the neighbours other than p (0) and sigma x (-2) must sum to -6, and x is adjacent to at most one vertex of each
orbit; so x ~ y_1, ..., y_6 and x is adjacent to no x_i. By sigma, sigma x ~ x_1, ..., x_6.
Take x_1. It is not adjacent to x (it is adjacent to sigma x and is not p). So x_1 and x have exactly two common
neighbours; sigma x is one of them; hence x_1 has at most one neighbour among y_1..y_6 (all of them are neighbours of x).
Then sum_{w ~ x_1} phi(w) >= phi(sigma x) - 1 = -3 > -4. Contradiction. QED.
(Uses only lambda = 1, mu = 2 and the eigen-equation. No assumption.)

### A3. Patterns of active inner orbits for {0,+-1} values: k in {0, 2, 4}
n_c = number of active words in star c. Eigen-equation at a_c: n_c = phi(a_c) (mod 2), n_c >= 3 |phi(a_c)|. Each active
word meets exactly 2 stars: sum_c n_c = 2(10 - k). So k is even and 3k <= 2(10 - k): **k in {0, 2, 4}**, and for k = 4
there is equality: every active inner orbit has exactly 3 active words, every inactive inner orbit has none.

### A4. Counting identities (m = 10) and e(S+) <= 1
General form (T18 A0, re-derived): sum_{z not in S} C(d(z),2) = m^2 - 7m - 7e - Q = **30 - 7e - Q**, and
sum_{z not in S} d(z) = 10m - 4e = **100 - 4e**; there are 79 vertices outside S.
Since C(d,2) - (d - 1) = C(d-1,2) >= 0:

> **n_0 + n_3 + 3 n_4 + 6 n_5 + ... = 9 - 3e - Q.**     (#)

With Q >= 2e this gives 5e <= 9: **e <= 1** (the bound from A <= 14 E_0 + 3 (I - E_0) is only e <= 3:
8e + 80 <= 60 + 4400/99). For e = 1: Q = 2 and the right side of (#) is 4. For e = 0 it is 9.

### A5. Parity law (T18 A1, any m): e = C(k,2) (mod 2)
Hence **(k, e) in {(0,0), (2,1), (4,0)}**: cases I, II, III below.

### A6. Identity for a vertex outside S
For z outside S, counting the paths of length 2 from z to S (deg_S(w) = 4 + 2 d+(w) for w in S):

> sum_{w ~ z, w not in S} d(w) = 20 - 5 d(z) - q(z),   q(z) = number of neighbours of z that are ends of a plus edge.

So d(z) <= 4 for every z outside S, and a vertex with d = 4 has q = 0 and its six outside neighbours in X_0.

**n_4 = 0 in cases I and II; n_4 = 1 (only p) in case III.** Case II: (#) gives 3 n_4 <= 4 and n_4 is even (d(p) = 2).
Case I: p is in X_0, so (#) gives 3 n_4 <= 8, n_4 even; n_4 = 2 would give n_0 <= 3, but a vertex with d = 4 has six
neighbours in X_0. Case III: A9. (The scan B4 finds the same: no admissible type with d = 4.)
At p (q(p) = 0, because by A7 no inner vertex is an end of a plus edge): sum over the inactive pairs of delta_c
= (20 - 5k)/2, where delta_c = d(a_c) = d(b_c): 10 (k = 0), 5 (k = 2), 0 (k = 4).

### A7. Case II, plus edge between a word and an inner vertex: impossible
Let x_0 (word) ~ x_c (inner, value +1), c' the other active inner orbit, W' the 7 other active words.
x_0 is not adjacent to y_c (A0), x_c is adjacent to no vertex of orbit c'. So M_c is a 4-subset of W' (d-(x_c) = 5 with
y_c), M_0 is a 5-subset of W' u {c'}. An index of M_0 n M_c gives a common neighbour of the adjacent pair x_0, x_c:
|M_0 n M_c| <= 1, so M_0 u M_c = W' u {c'}, c' in M_0, M_0 n M_c = {u}. Put U = M_c \ {u} (3 words).
For j in U: |M_j| = 4, c in M_j, 0 not in M_j (j is not in M_0), and M_j \ {c} lies in M_0 u M_c.
x_j, x_c are not adjacent and already share y_c: |M_j n M_c| <= 1. x_j, x_0 are not adjacent: |M_j n M_0| <= 2.
So 3 = |M_j n M_0| + |M_j n M_c| - [u in M_j] <= 3 - [u in M_j]: u is not in M_j and j has **exactly one**
minus-neighbour in U \ {j}. The minus relation is symmetric, so the 3-set U carries a perfect matching. Contradiction. QED.
(Confirmed by both enumerators: 0 structures.)

### A8. Case II, plus edge between two words x_0 ~ x_1: the quad is forced
|M_0| = |M_1| = 5. If 1 not in M_0, both are 5-subsets of the 8 other orbits and share >= 2 indices, i.e. two common
neighbours of an adjacent pair. So **x_0 ~ y_1 and x_1 ~ y_0**: the four vertices form the 4-cycle
x_0 - x_1 - y_0 - y_1 - x_0. Unlike m = 9 (T18 A3) the count then has one unit of slack and I did not close it by hand;
the enumeration (B1) leaves exactly one structure.

### A9. Case III (k = 4, e = 0): forced structure
- By A3 each of the 6 active words x_j is adjacent to exactly two of the four b_c, and each a_c to exactly three y_j.
  Two a_c, a_c' already share p, so they share at most one y_j; 6 words, 6 pairs: **the words are the edges of K4 on the
  four active inner orbits** (a_c ~ y_j iff c in j).
- The word-word minus graph W (j ~ j' iff x_j ~ y_j') is 2-regular on the 6 edges of K4, so it is C6 or 2 C3.
  Rule: for a word j and c in j, at most one W-neighbour of j contains c. Indeed a_c and x_j are non-adjacent, b_c is a
  common neighbour (x_j ~ b_c, a_c ~ b_c), and each j' in N_W(j) containing c gives another one (y_j').
- 2 C3 by hand: a 3-set of edges of K4 is a star (rule violated), a triangle (its complement is a star) or a Hamiltonian
  path, whose complement is the complementary Hamiltonian path: one class, **III.1**. For C6 the enumeration gives one class,
  **III.0** (the hexagon 23-02-13-03-12-01: alternately "share a vertex" and "disjoint").
- Counts: p has d = 4; by A3 the six inactive inner vertices have d = 0. (#) reads n_0 + n_3 + 3 n_4 = 9 with n_0 >= 6,
  n_4 >= 1: **n_4 = 1 (only p), n_3 = 0, X_0 = the six inactive inner vertices, n_2 = 24, n_1 = 48.**
  All 72 words outside S have d in {1, 2}.
- Path counts from a vertex of S (38 - deg_S): each active a_c has 9 neighbours outside S u {p}: 3 with d = 2, 6 with d = 1;
  each active word x_j has 10: 6 with d = 2, 4 with d = 1. Each inactive inner vertex has 12 word neighbours: 4 with d = 2,
  8 with d = 1; exactly one of them is adjacent to each of the 8 active inner vertices, and 4 go to the other inactive pairs.
  For c != c' exactly one word outside S is adjacent to a_c and b_c' (none to a_c and a_c').
  With alpha, beta, gamma = numbers of X_2 words having 2, 1, 0 active inner neighbours: alpha = gamma, beta = 24 - 2 alpha.
  For a word w outside S: a_2(w) = (number of inactive inner neighbours) + 3 [d(w) = 1].
  All these counts are mutually consistent: no contradiction at this level.

### A10. Case I (k = 0, e = 0)
B (i ~ j iff x_i ~ y_j) is a 4-regular graph on 10 vertices without loops in which any two vertices have at most 2 common
neighbours; S is disjoint from N[p]; p is in X_0; sum_c delta_c = 10.
(#): n_0 = 9 - n_3 - 3 n_4, n_1 = 40 + 3 n_3 + 8 n_4, n_2 = 30 - 3 n_3 - 6 n_4; n_3, n_4 even, n_0 odd.
Exact PSD of 9(3I-A)+J and 11(4I+A)-2J on S is equivalent to: B connected and every eigenvalue other than 4 in [-3, 3].

Profile at p (uses n_4 = 0, proved in A6): for z in X_d, a_0 = omega + 3d - 6 with
omega = a_2 + 2 a_3. Summing omega over N(p) (A^2 = 12I - A + 2J on the indicators of X_2, X_3) and bounding below
(neighbour of p in X_2: omega >= 1; in X_1: >= 4; in X_0: >= 8; in X_3: >= 2) gives, with h_j = number of pairs with
delta_c = j:  **h_2 + 4 h_3 + n_3 / 2 <= 7**. With sum delta = 10 this leaves
(h_3, h_2, h_1, h_0) = (0,3,4,0), (0,4,2,1), (0,5,0,2), (1,1,5,0), (1,2,3,1).

### A11. Case II (k = 2, e = 1), remaining structure
(#): n_0 = 4 - n_3 - 3 n_4, n_1 = 54 + 3 n_3 + 8 n_4, n_2 = 21 - 3 n_3 - 6 n_4; p is in X_2 (n_2 odd, n_0, n_3 even).
The five inactive pairs have sum delta_c = 5; each active inner orbit has exactly 3 active words.

## B. Computed (exhaustive; exact arithmetic)

Definition used by the programs (file header of `t20_common.py`): an **S-structure** is a sigma-invariant graph on the
21 vertices S u {p} with (E) d-(x_i) = d+(x_i) + 4 and (L) adjacent pairs have <= 1 common neighbour, non-adjacent
pairs <= 2, p adjacent exactly to the inner x_i, y_i (those with x_i ~ y_i). Isomorphism = permutation of the 10 orbits.

### B1. Enumeration of the S-structures (`t20_enum.py` + `t20_kernel.py`, outputs `enum_I.out`, `enum_III_IIb_IIa.out`)

| case | labelled structures | classes | orbit-stabiliser check |
|---|---|---|---|
| I: k = 0, e = 0, row 0 of B fixed to {1,2,3,4} | 27720 (1,841,249 nodes) | **6** | 27720 = sum 10!/(126 Aut) = 1800+7200+2880+7200+7200+1440 |
| IIa: k = 2, e = 1, plus edge word-word | 2880 (6,414,667 nodes) | **1** | 2880 = 2*2*6!/1 |
| IIb: k = 2, e = 1, plus edge word-inner | 0 (1,463,867 nodes) | 0 | (hand proof A7) |
| III: k = 4, e = 0 | 10080 (469,755 nodes) | **2** | 10080 = 4! 6! (1/3 + 1/4) |

### B2. Second program (`t20_verify.py`)
No shared code with B1: pure Python, reverse pair order, inner orbits on the highest labels, row 9 fixed instead of row 0
in case I, every structure found re-tested from scratch with A @ A and A phi = -4 phi. It has no isomorphism test: the
labelled structures are sorted by an isomorphism invariant (traces of the powers of the weighted orbit matrix) and the
counts are compared with |G| / |Aut| of the classes of B1. Agreement therefore confirms the number of labelled
structures and their split over the classes; the automorphism orders themselves come from B1 only.

| case | result | file |
|---|---|---|
| I | 27720 labelled, 6 invariants, counts 1800 / 2880 / 7200 / 7200 / 7200 / 1440: **agreement** | `verify_III_I.out` |
| III | 10080 labelled, 2 invariants, counts 5760 / 4320: **agreement** | `verify_III_I.out` |
| IIb | 0 structures (10,596,116 nodes with the plus edge on orbits 0, 9; 731,934 nodes with it on orbits 7, 9): **agreement** | `verify_II.out`, `verify_IIb.out` |
| IIa | 2880 labelled, 1 invariant (plus edge on orbits 6, 7; 3,208,774 nodes): **agreement**. The run with the plus edge on orbits 0, 1 was cut by its time cap and gave nothing. | `verify_IIa.out` |

(The number of labelled structures of a case does not depend on which labels carry the plus edge, so the relabelled runs
"IIa2", "IIb2" count the same thing; they are only faster.)

### B3. Exact PSD tests (`t20_common.psd_exact`, rational elimination) on S u {p}, 21 vertices
All nine survivors: 9(3I-A)+J is positive definite (rank 21), 11(4I+A)-2J is positive semidefinite of rank 20 (its kernel
is phi). For III.0 and III.1 also on S u N[p] (27 vertices, completely determined by A9): both matrices are PSD, of rank
26 and 25 respectively, for both structures. (So 9(3I-A)+J is singular there: one forced kernel vector on S u N[p],
which every extension must respect; not exploited.) **PSD kills nothing at the S level.**

### B4. First scan of the vertices outside S (`t20_survivors.py` -> `survivors.out`)
Types (N(z) n S+, N(z) n S-) with d(z) = d, rule (L) on S u {p, z, sigma z} (23 vertices), then exact PSD; classes under sigma.

| structure | d = 4 | d = 3, z not in N(p): pass (L) / pass PSD | d = 3, z in N(p) |
|---|---|---|---|
| I.0 | 0 | 4 / 4 | 0 |
| I.1 | 0 | 23 / 23 | 1 / 1 |
| I.2 | 0 | 15 / 15 | 0 |
| I.3 | 0 | 12 / 12 | 0 |
| I.4 | 0 | 12 / 12 | 0 |
| I.5 | 0 | 25 / 25 | 10 / 10 |
| IIa.0 | 0 | 6 / 6 | 0 |
| III.0 | 0 | 3 / 0 | 0 |
| III.1 | 0 | 8 / 4 | 0 |

Consequences: no type with d = 4 (also proved by hand, A6); delta_c <= 2 for I.0, I.2, I.3, I.4 and IIa.0 (so h_3 = 0
there: profiles (3,4,0), (4,2,1), (5,0,2) of (h_2, h_1, h_0) only); delta_c = 3 is possible only for I.1 and I.5.
(In case III, n_3 = 0 is already proved by hand, A9.) Status of the d = 3 columns: the "pass (L)" numbers are counted
by two programs (`t20_types_check.py`, see "Last lines"); the PSD column by one.

## C. The nine survivors (the starting point of round 2)

Orbits 0..9. "Minus edges" ij: x_i ~ y_j and x_j ~ y_i. Inner orbit c: x_c ~ y_c, p ~ x_c, y_c. Nothing else is adjacent in
S u {p} except the listed plus edge.

**Case I — no active inner orbit, S+ and S- independent, S disjoint from N[p]; B = minus graph (4-regular)**

| | edges of B | Aut | triangles | characteristic polynomial of B | codegrees adjacent / non-adjacent pairs |
|---|---|---|---|---|---|
| I.0 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79 | 16 | 4 | (t-4)(t-1)^2(t+1)(t^2+t-4)(t^2+2t-1)^2 | 0:8, 1:12 / 0:1, 2:24 |
| I.1 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78 | 4 | 6 | (t-4)(t+2)(t^2-2)(t^3-4t+2)(t^3+2t^2-2t-2) | 0:3, 1:16, 2:1 / 1:8, 2:17 |
| I.2 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89 | 10 | 5 | t(t-4)(t^4+2t^3-4t^2-5t+5)^2 | 0:5, 1:15 / 1:5, 2:20 |
| I.3 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79 | 4 | 6 | (t-4)(t-1)(t+1)^2(t^2-3)(t^2+t-4)(t^2+2t-1) | 0:4, 1:14, 2:2 / 0:1, 1:6, 2:18 |
| I.4 | 01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79 | 4 | 8 | (t-4)(t-1)(t+1)^4(t^2-5)(t^2+t-4) | 0:2, 1:12, 2:6 / 0:3, 1:8, 2:14 |
| I.5 = C10(1,2) | 01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89 | 20 | 10 | t(t-4)(t+1)^4(t^2-5)^2 | 1:10, 2:10 / 0:5, 1:10, 2:10 |

(I.5 is isomorphic to the circulant C10(1,2), `names.out`: the analogue of B2 = C9(1,2) of T18. The other five are none of
the 4-valent circulants on Z_10.)

**Case II — two active inner orbits 0, 1; one plus edge 2-3 between two words, in a quad (x_2 ~ x_3, x_2 ~ y_3)**

| | minus edges | plus edge | Aut |
|---|---|---|---|
| IIa.0 | 07 08 09 13 15 16 23 24 26 28 29 35 37 39 45 46 48 57 68 79 | 23 | 1 |

(The triangle on the plus edge is x_2, x_3, y_9.)

**Case III — four active inner orbits 0, 1, 2, 3; words 4..9 = edges of K4: 4 = {2,3}, 5 = {1,3}, 6 = {1,2}, 7 = {0,3},
8 = {0,2}, 9 = {0,1}; S+ and S- independent**

| | minus edges | word-word graph W | Aut |
|---|---|---|---|
| III.0 | 07 08 09 15 16 19 24 26 28 34 35 37 48 49 57 58 67 69 | hexagon 4-8-5-7-6-9 | 3 |
| III.1 | 07 08 09 15 16 19 24 26 28 34 35 37 48 49 56 57 67 89 | triangles 4-8-9 and 5-6-7 | 4 |

Machine-readable: `structures_I.json`, `structures_III_IIb_IIa.json` (field m: 10 x 10 matrix of states, bit 1 = minus,
bit 2 = plus; field H: inner orbits).

Forced data to start round 2 from:

| | d(p) | N(p) | n_0, n_1, n_2, n_3, n_4 | sum over outside neighbours of z of d |
|---|---|---|---|---|
| I.0 - I.5 | 0 | sum delta_c = 10 over 7 pairs; profiles in A10 | 9 - n_3, 40 + 3 n_3, 30 - 3 n_3, n_3 even <= 8, 0 (by hand) | 20 - 5 d(z) |
| IIa.0 | 2 | 2 active pairs + 5 pairs with sum delta_c = 5, delta_c <= 2 (computed) | 4 - n_3, 54 + 3 n_3, 21 - 3 n_3, n_3 in {0,2,4}, 0 (by hand) | 20 - 5 d(z) - q(z) |
| III.0, III.1 | 4 | 4 active pairs + 3 pairs with no neighbour in S | 6, 48, 24, 0, 1 (all by hand) | 20 - 5 d(z) |

Deficient pairs of S+ (`t20_deficiency.py` -> `deficiency.out`; m_ij = number of common neighbours of x_i, x_j outside
S u {p}; these are the pairs the vertices of X_2 and X_3 must realise, and by sigma the same pairs of S-):

| | total | pairs with m = 2 | pairs with m = 1 |
|---|---|---|---|
| I.0 | 30 | 01 02 18 26 39 45 47 58 67 | 03 04 17 19 25 29 34 36 38 59 68 79 |
| I.1 | 30 | 01 02 19 | 03 04 17 18 25 26 27 28 34 35 36 38 39 45 46 47 49 57 58 59 67 68 69 78 |
| I.2 | 30 | 01 02 17 26 67 | 03 04 18 19 25 29 34 35 36 38 39 45 47 48 49 57 58 59 68 89 |
| I.3 | 30 | 01 02 39 45 47 | 03 04 15 16 18 19 26 27 28 29 34 36 38 56 58 59 67 68 78 79 |
| I.4 | 30 | 01 28 39 47 56 | 02 03 05 07 14 16 18 19 25 27 29 34 35 38 46 48 57 68 69 79 |
| I.5 | 30 | 05 17 29 38 46 | 01 02 06 08 12 16 18 26 28 34 35 37 39 45 47 49 57 59 68 79 |
| IIa.0 | 20 | 45 67 | 01 04 05 06 08 16 18 19 29 38 47 49 57 58 69 78 |
| III.0 | 24 | 49 58 67 | 07 08 09 14 15 18 25 26 27 34 36 39 47 48 57 59 68 69 |
| III.1 | 24 | 58 | 05 06 07 14 18 19 25 26 27 34 38 39 45 46 47 49 59 67 68 69 78 79 |

Totals agree with the hand counts: 30 = n_2 + 3 n_3 (case I), 20 = (n_2 - 1) + 3 n_3 (case II, p excluded), 24 = n_2
(case III). In case III every pair is realised by vertices of X_2 exactly (n_3 = 0): each a_c lies in 3 deficient
units, each word in 6, as found in A9.

## D. Open, precisely

T20 is equivalent to excluding the nine configurations of section C. For each of them the obstruction, if any, is not
visible on S u {p} (exact PSD passes) and, for case III, not on S u N[p] either.

Suggested order for round 2 (the method of T18 round 2: X_2 = the vertices realising the deficient pairs, matched by sigma;
then determined vertex sets, common-neighbour budgets and exact PSD):
1. **Case III** first: everything is forced (n_3 = 0, n_4 = 1, X_0 = N(p) \ S, n_2 = 24, the counts of A9), only two
   structures, and S u N[p] is already determined. The 24 vertices of X_2 realise the deficient pairs of S+ and of S-.
2. **IIa.0**: one structure with trivial automorphism group; n_0 <= 4; p in X_2.
3. **Case I**: six graphs, five profiles at p each; this is the analogue of T18's B0, B1, B2 and will cost about as much.

Not done in this round: any search on the vertices outside S beyond the type scan B4; the deficient-pair matchings;
hand classification of the six graphs of case I, of the structure IIa.0 and of the hexagon of case III (these are
computed, B1/B2); a second implementation of the PSD column of B4. The entries "X_..." of `t20_enum.py` (combinations
excluded by the parity law, for information) were not run.

## E. Tried, did not work / remarks

- Lattice translation c -> c - G e_O (norm 10 - 14 c_O + 7 G_OO): for an inner orbit at 2 it gives norm 10 again (the
  reflected vector), never something shorter; so the pattern of A2 cannot be reduced to a shorter-vector lemma, and the
  direct proof A2 is what closes it.
- Exact PSD on S u {p} and on S u N[p]: no rejection (B3).
- Case III counting (A9): every identity I tried is satisfied (alpha = gamma, beta = 24 - 2 alpha remains free).
- Case IIa by hand: the argument of T18 A3 has one unit of slack for m = 10 (8 other orbits instead of 7).
- Process note: the first version of `t20_enum.py` (pure Python, inner orbits last) was too slow and one run exceeded the
  10-minute limit by about 30 s before I stopped it; it produced nothing that is used. The final enumerator uses a numba kernel.

## F. Files (all in this folder)

- `T20_REPORT.md` (this file).
- `t20_common.py`: definition of S-structures, graph builder, (L) test, exact PSD (`psd_exact`), negative-vector certificate,
  isomorphism / automorphism counting, edge lists.
- `t20_kernel.py`, `t20_enum.py` -> `enum_I.out`, `enum_III_IIb_IIa.out` (final), `enum_III_IIb.out` (earlier run, same
  numbers), `structures_I.json`, `structures_III_IIb_IIa.json`.
- `t20_verify.py` -> `verify_III_I.out`, `verify_II.out` (IIb complete, then cut by the time cap: "exit 124"),
  `verify_IIa.out`, `verify_IIb.out` (`verify.out` holds only the exit line of the first version of the verifier,
  which chose whole rows at once: a wrong feasibility test made it find nothing, and once that was fixed it was too slow
  and I stopped it; no result quoted here comes from it).
- `t20_types_check.py` -> `types_check.out` (independent recount of the types of B4 passing the graph rule).
- `t20_survivors.py` -> `survivors.out` (characteristic polynomials, codegrees, PSD ranks, type scan B4).
- `t20_names.py` -> `names.out` (I.5 = C10(1,2)).
- `t20_deficiency.py` -> `deficiency.out` (deficient pairs of S+).

Caveat on rigour: "PSD-ok" / "pass" never proves existence of anything; the hand proofs A1-A9 do not depend on any script;
the list of nine depends on B1 (and B2 where it agrees).

## Last lines (23:27)

- `t20_types_check.py` (independent code, Python sets, no sigma quotient) recounts the types of B4 that pass the graph
  rule: d = 4: 0 for the nine structures; d = 3, classes under sigma, z not in N(p) / z in N(p):
  I.0 4 / 0, I.1 23 / 1, I.2 15 / 0, I.3 12 / 0, I.4 12 / 0, I.5 25 / 10, IIa.0 6 / 0, III.0 3 / 0, III.1 8 / 0.
  **Identical to the "pass (L)" columns of B4** (`types_check.out`).
- Both enumerators agree on the four cases (B1, B2). All runs quoted finished inside their time caps except the
  verifier run of IIa with the plus edge on orbits 0, 1 (cut, replaced by the relabelled run).

### What a reviewer should re-check first
1. Section 0 (which statement is meant).
2. A2 (five lines) and A7 (ten lines): they remove a whole pattern and a whole sub-case with no computation.
3. A4 - A6: the identity (#), e <= 1, n_4 = 0.
4. That the definition of an S-structure in `t20_common.py` (conditions (E) and (L) on S u {p}) is exactly what A0 - A3
   justify; the nine survivors are the output of that definition, nothing more.
