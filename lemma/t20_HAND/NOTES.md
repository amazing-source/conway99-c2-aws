# T20, work package A (by hand): notes of the lab session (Claude, desktop), 2026-10-07

Notation of `lemma/T20_WORK.md` and of round 1 / round 2. Case I throughout: k = 0, S+ = {x_0..x_9} and S- = {y_i = sigma x_i} are
independent, S is disjoint from N[p], B is one of I.0 ... I.5 (x_i ~ y_j iff i ~_B j).

**Status.** Nothing here proves T20.

| Item | Content | Kind |
|---|---|---|
| H1 | structure of the X_3 orbit when n_3 = 2 | hand |
| H2 | list of the types (U ; V) of an X_3 vertex | computed, `x3_types.py` |
| H3 | perfect-matching identity in N(z) | hand |
| H4 | edge counts between the classes and two quadratic identities | hand |
| H5 | the base at p in the language of D7 roots | hand |
| H6 | a new exact rejection rule, the dual-norm test, with first consequences | hand; searches computed |
| H7 | determined set S u X_3 u X_0 for n_3 = 2: it is NOT contradictory | computed, `n3_base.py` |
| H8 | what transposes from the 04/10 lemma (norm 16) | remark |

Each hand statement is given with its full proof. The three scripts are tiny (seconds, exact integer / rational rejections).
They were written from the work page only and share no code with the project's engines.

## H0. Formulas used (re-derived)

For z outside S with d = d(z) (round 2, G0, with q = 0 in case I):

    a_1 + 2 a_2 + 3 a_3 = 20 - 5d,        a_0 = a_2 + 2 a_3 + 3d - 6.                                   (G0)

| Class | a_0 | a_1 |
|---|---|---|
| X_0 | a_2 + 2 a_3 - 6 | 20 - 2 a_2 - 3 a_3 |
| X_1 | a_2 + 2 a_3 - 3 | 15 - 2 a_2 - 3 a_3 |
| X_2 | a_2 + 2 a_3 | 10 - 2 a_2 - 3 a_3 |
| X_3 | a_2 + 2 a_3 + 3 | 5 - 2 a_2 - 3 a_3 |

For x in S+: (number of neighbours in X_2) + 2 (number in X_3) = 6.
Proof: the 9 other vertices of S+ are non-adjacent to x, so 18 = 4 * 3 + sum over the 10 outside neighbours w of (d(w) - 1).

## H1. The X_3 orbit when n_3 = 2 (hand)

Assume n_3 = 2: X_3 = {z, z'}, z' = sigma z. By round 2 (I.1) z is a word; so z !~ z', z !~ p, and N(z) n N(z') has exactly 2
elements. |X_0| = 7; put X_0' = X_0 \ {p} (6 vertices, three sigma-orbits) and T = N(z) n X_0, T' = sigma T = N(z') n X_0.

**(a) a_3(z) = 0 and (a_0, a_1, a_2)(z) is (3, 5, 0) or (4, 3, 1).**
z !~ z' gives a_3(z) = 0. (G0) gives a_0 = a_2 + 3, a_1 = 5 - 2 a_2, so a_2 <= 2. T lies in X_0' (z !~ p), and T n T' lies in
N(z) n N(z'), so 2|T| - 2 <= |T u T'| <= 6: |T| <= 4, so a_2 <= 1.

**(b) N(z) n N(z') is one sigma-orbit {w, sigma w}** (it is sigma-invariant, has 2 elements, and p is not in it). Exactly one of:

| | N(z) n N(z') | Consequences |
|---|---|---|
| (i-S) | {x_i, y_i} | U n V = {i}; T n T' is empty; \|T\| = 3; a_2(z) = 0 |
| (i-X1) | an orbit {r, sigma r} of X_1 | U n V and T n T' are empty; \|T\| = 3; a_2(z) = 0 |
| (ii) | an orbit {u, sigma u} of X_0' | U n V is empty; \|T\| = 3; a_2(z) = 0; T = {u, sigma u, v} |
| (iii) | an orbit {u, sigma u} of X_0' | U n V is empty; \|T\| = 4; a_2(z) = 1; T = {u, sigma u, v, w}, v and w in the two other orbits |

Proof.
- If the orbit is in S it is {x_i, y_i} with i in U n V (z ~ x_i iff i in U, z' ~ x_i iff i in V), and conversely an index of U n V
  gives two common neighbours. So |U n V| <= 1, and |U n V| = 1 exactly in case (i-S).
- If it is in X_2, then a_2(z) >= 2, against (a).
- It is not in X_3.
- If T n T' is empty then |T| = 3 (|T| = 4 forces |T n T'| >= 2). T n T' is sigma-invariant without fixed point, so it has 0 or 2
  elements; if 2, it is the common orbit.

**(c) In cases (ii) and (iii) the common orbit {u, sigma u} is a word orbit**, and u, sigma u have no common neighbour other than
z, z'. (z != p is not adjacent to both ends of a mate edge; u !~ sigma u have exactly 2 common neighbours.)

**(d) In cases (i-S) and (i-X1) T is a transversal of the three orbits of X_0'** (one vertex in each), and T' is the complementary
transversal: every vertex of X_0' has a_3 = 1. In (ii): a_3 = 2 on {u, sigma u}, 1 on {v, sigma v}, 0 on the third orbit. In (iii):
a_3 = 2 on {u, sigma u}, 1 on the four others.

**(e) For x in X_0':** a_2 = a_0 + 6 - 2 a_3 and a_1 = 8 - 2 a_0 + a_3. Hence a_0(x) <= 4 if a_3(x) <= 1, and a_0(x) <= 5 if
a_3(x) = 2. In (ii), (iii): a_0(u) <= 2 (u is adjacent to at most one end of each of the two other orbits, by (c) and sigma, and
not to sigma u nor p).

**(f) Number of inner orbits in X_0'** = h_0: none for profile (3,4,0), exactly one for (4,2,1). The other orbits are word orbits.

## H2. The types (U ; V) of an X_3 vertex (computed: `x3_types.py`)

Rules (L) on S u {z, z'}:
- |U n V| <= 1;
- |B(i) n V| <= 1 for i in U, <= 2 otherwise; the same with U, V exchanged;
- any two indices of U (of V) have at most one common B-neighbour.

Then the odd Gram [[3I + B, b], [b^T, 3]], b = 1_V - 1_U, must be positive semidefinite. With 3I + B invertible (true for the six
graphs) this is rho = 3 - b^T (3I + B)^(-1) b >= 0. rho is the squared norm of the component of the frame vector of z orthogonal
to the ten support vectors.

Classes under Aut(B) x (z <-> z'); all of them have rho > 0:

| Graph | Classes | U V \|U n V\| e(U) e(V) e(U,V) rho |
|---|---|---|
| I.0 | 1 | 034 179 0 3 3 2 3/2 |
| I.1 | 9 | 034 178 0 3 3 3 7/5; 034 258 0 3 1 3 333/455; 034 278 0 3 1 3 51/65; 257 268 1 2 2 3 9/7; 257 368 0 2 3 2 557/455; 257 678 1 2 2 3 101/91; 258 345 1 1 2 3 583/455; 278 349 0 1 1 3 3/5; 368 457 0 3 3 2 11/7 |
| I.2 | 3 | 034 189 0 3 3 2 17/11; 034 589 0 3 2 2 37/33; 345 389 1 2 2 3 7/11 |
| I.3 | 4 | 034 156 0 3 1 3 29/48; 034 159 0 3 2 2 5/4; 159 168 1 2 2 3 31/24; 159 368 0 2 3 2 5/4 |
| I.4 | 5 | 025 279 1 1 2 3 9/8; 027 035 1 1 2 3 17/16; 035 169 0 2 2 2 1; 035 279 0 2 2 2 1; 279 348 0 2 2 2 1 |
| I.5 | 3 | 012 168 1 2 2 3 3/2; 012 579 0 2 2 2 1; 016 359 0 1 1 3 1/2 |

e(U), e(V) = B-edges inside U, V; e(U,V) = B-edges between U and V = edges x_i y_j inside N(z).

To compare with round 1 B4: that table counts classes under sigma only (4, 23 + 1, 15, 12, 12, 25 + 10) and includes N(p)-types.

Read off the table (computed facts): **e(U,V) is 2 or 3; e(U) >= 1 and e(V) >= 1; |U n V| = 1 implies e(U,V) = 3.**

**Hand proof of e(U) >= 1 when U n V is empty.** Let F_i be the frame vector of orbit i (representative x_i), f_z that of z,
v = (1/7) sum F_i the dual vector of phi: (F_i, F_j) = 3 delta_ij + B_ij, (f_z, F_i) = [i in V] - [i in U], |v|^2 = 10/7,
(v, F_i) = 1, (v, f_z) = 0. For g = f_z + sum_{i in U} F_i: |g|^2 = 6 + 2 e(U), (v, g) = 3, so
|g - 2v|^2 = 2 e(U) - 2/7, which is negative if e(U) = 0. Integer certificate: coefficients 7 [i in U] - 2 on the support, 7 on z.

## H3. The matching in N(z) (hand)

lambda = 1: each of the 14 neighbours of z has exactly one neighbour inside N(z). N(z) = x_U u y_V u T u R (u {q}), with
R = N(z) n X_1 and q the X_2-neighbour in case (iii). Vertices of T have no neighbour in S. Let f = number of edges inside T and
g = number of edges inside R (inside R u {q} in case (iii)). The edges inside x_U u y_V are the e(U,V) edges x_i y_j. Counting the
vertices that must find their partner in R (R u {q}):

    cases (i), (ii):  5 = (6 - 2 e(U,V)) + (3 - 2f) + 2g,   i.e.  e(U,V) + f - g = 2;
    case (iii):       4 = (6 - 2 e(U,V)) + (4 - 2f) + 2g,   i.e.  e(U,V) + f - g = 3.

With H2: in cases (i), (ii), e(U,V) = 2 gives f = g and e(U,V) = 3 gives g = f + 1 >= 1 (a triangle z r r' with r, r' in X_1); in
case (iii), e(U,V) = 3 gives f = g and e(U,V) = 2 gives f = g + 1 >= 1 (an edge inside T).

A vertex r of R whose partner is x_i (i in U) has x_i as its S+ neighbour and its S- neighbour y_b with b not in V. A vertex of R
whose partner is not in S has its two S-neighbours outside x_U u y_V.

## H4. Edge counts and quadratic identities (hand)

t = e(X_2); e(X_i, X_j) = number of edges between X_i and X_j. Summing (G0) over each class:

**n_3 = 0** (n_0, n_1, n_2 = 9, 40, 30):

    e(X_0) = t - 27,   e(X_0,X_2) = 2t,   e(X_0,X_1) = 180 - 4t,   e(X_1,X_2) = 300 - 4t,   e(X_1) = 4t.

So **t >= 27**: X_2 carries at least 27 edges. This is the opposite of norm 16, where e(X_2) <= 1.

Counting the pairs (s, s') of X_2 through their common neighbours (sum over all v of |N(v) n X_2|^2 = 2160 - 2t; each vertex of S
has exactly 6 neighbours in X_2):

    sum_{X_0} (a_2 - 6)^2 + sum_{X_1} (a_2 - 4)(a_2 - 5) + sum_{X_2} (a_2 - 2)(a_2 - 3) = 44.                 (Q0)

The three sums are >= 0, and on X_0, a_2 - 6 = a_0. So **sum over X_0 of a_0^2 <= 44**, and with sum_{X_0} a_0 = 2 e(X_0):
e(X_0) <= 9, **27 <= t <= 36**. (Q0) is the analogue of (*) of T18 5.4; it says that all but a few vertices have a_2 in {2, 3}
on X_2 and in {4, 5} on X_1.

Proof of (Q0): sum over outside vertices of a_2^2 = 2160 - 2t - 720. sum a_2 is 2t on X_0, 300 - 4t on X_1, 2t on X_2. Expand:
the terms in t cancel (-2 - 24 + 36 - 10) and the constant is 1440 + 324 - 2700 + 800 + 180 = 44.

**n_3 = 2** (7, 46, 24; alpha = a_2(z), 0 or 1; eps = |U n V|):

    e(X_0,X_3) = 6 + 2 alpha,  e(X_2,X_3) = 2 alpha,  e(X_1,X_3) = 10 - 4 alpha,  e(X_0) = t + 4 alpha - 15,
    e(X_0,X_2) = 2t + 4 alpha,  e(X_1,X_2) = 240 - 4t - 6 alpha,  e(X_0,X_1) = 122 - 4t - 14 alpha,  e(X_1) = 90 + 4t + 12 alpha.

    sum_{X_0} (a_2 - 5)^2 + sum_{X_1} (a_2 - 3)(a_2 - 4) + sum_{X_2} (a_2 - 1)(a_2 - 2) = 55 - 16 eps.         (Q2)

(The vertices x_i, y_i with i in U n V have 2 neighbours in X_3, hence 2 in X_2; the other neighbours of X_3 in S have 4; the rest
6. This gives the term 16 eps.) On X_0', a_2 - 5 = a_0 + 1 - 2 a_3; at p, (a_2 - 5)^2 = (2 h_2 - 5)^2 = 1 or 9.

## H5. The base at p in the language of D7 roots (hand)

For c = 1..7 let h_c be the frame vector of the inner orbit {a_c, b_c} (representative a_c). The h_c are pairwise orthogonal of norm
4. Put R_ic = (F_i, h_c) = [x_i ~ b_c] - [x_i ~ a_c]. Each x_i is a word: it has exactly two neighbours in N(p), in two different
pairs. So **r_i = (R_ic)_c is a root of D7** (two entries +-1), and:

- (R1) sum_i r_i = 0. At every coordinate c there are delta_c entries +1 and delta_c entries -1 (d(a_c) = d(b_c) = delta_c). The
  ten roots form a multigraph on the 7 coordinates with degrees 2 delta_c: (4,4,4,2,2,2,2) for profile (3,4,0),
  (4,4,4,4,2,2,0) for (4,2,1).
- (R2) r_i != +-r_j for i != j. Equivalently a_c, a_c' (c != c') have at most one common neighbour in S and so do a_c, b_c'
  (they already share p). So a cell {c, c'} carries at most the two "sisters" e_c + e_c' and e_c - e_c' (up to sign).
- (R3) for i != j let s_ij = number of c with R_ic = R_jc != 0 and o_ij = number of c with R_ic = -R_jc != 0;
  (r_i, r_j) = s_ij - o_ij. Then (B^2)_ij + s_ij <= 2 (common neighbours of x_i, x_j) and o_ij <= 2 - B_ij (common neighbours of
  x_i, y_j; they have none in S).
- (R4) for x_i ~ a_c (R_ic = -1): at most one j in B(i) has R_jc = +1. For R_ic = +1: at most one j in B(i) has R_jc = +1 (b_c is
  already a common neighbour of x_i and a_c). For R_ic = 0: at most two. The same holds with all signs exchanged (b_c in place
  of a_c). Reason: a_c ~ y_j iff b_c ~ x_j iff R_jc = +1.
- (R5) Positive semidefiniteness on the 17 orbits (support and N(p)) is exactly: 10 I + 4 B - P is positive semidefinite, where
  P_ij = (r_i, r_j) for i != j and P_ii = 0 (Schur complement of the block 4 I_7).

So a configuration of N(p) is a labelling of the ten vertices of B by ten D7 roots with (R1)-(R5). The deficient pairs with a
common neighbour in N(p) are the pairs with s_ij >= 1.

## H6. A new exact rejection rule: the dual-norm test (hand; searches computed)

**Fact.** Let L be the lattice of the 49 frame vectors f_O (odd orbit Gram G = 3I - A^, G^2 = 7G). u in L* gives the integer
vector a_O = (u, f_O); it satisfies G a = 7a and sum a_O^2 = 7 |u|^2, i.e. it is a sigma-odd integer (-4)-eigenfunction of squared
norm 14 |u|^2 on the vertices; and conversely. The squared norms 2, ..., 14 (AUDIT_NORME1), 16 (lemma of 04/10) and 18 (T18)
are excluded. So **L* has no non-zero vector u with 7 |u|^2 <= 9.**

**Rule.** Let v in L* be the vector of phi (c_O = (v, f_O), sum c^2 = 10). For an integer k and an integer vector m on the orbits,
u = k v - sum m_O f_O is in L* and

    7 |u|^2 = N(k, m) := 10 k^2 + 7 ( m^T G m - 2 k c^T m ).

**So N(k, m) is 0 or >= 10. A pair (k, m) with 1 <= N(k, m) <= 9 is an exact certificate of impossibility.** N(k, m) only involves
the Gram of the orbits in the support of m: it can be evaluated on any sigma-invariant determined set Y. k and 7 - k give the same
cosets (7v is in L): k = 1, 2, 3 suffice. Positive semidefiniteness alone gives N(k, m) >= 0. The values 1..9 are what is new
(k = 1: N = 3; k = 2: N = 5; k = 3: N = 6, the only residues possible).

**Dependency (remark of Codex, 07/10; checked).** The only forbidden values that can occur, 3, 5 and 6, are all <= 7. So the
rule needs only the old bound min L* >= 8/7 (AUDIT_NORME1), **not** the 04/10 lemma and **not** T18. A rejection by this rule
does not make T20 depend on T18.

With m = 1_I on support orbits and +1 on outside orbits w (representatives), and s_I(w) = |{i in I : w ~ x_i}| - |{i in I : w ~ y_i}|:

    m^T G m - 2k c^T m = (3 - 2k) |I| + 2 e_B(I) + sum_w (3 - 2 s_I(w)) + 2 sum_{w < w'} (f_w, f_w'),
    (f_w, f_w') = [w ~ sigma w'] - [w ~ w'].

Consequences by hand:
- (D1) k = 3, I a B-independent 4-set: N = 90 - 84 = 6. **B has no independent set of size 4.** (True for the six graphs: they
  all have independence number 3; the test adds nothing on S alone, see below.)
- (D2) k = 2, I a B-independent triple, two outside orbits w, w' with s_I = 2 each: N = 40 - 21 - 14 + 14 (f_w, f_w'). So
  (f_w, f_w') = 1: **w ~ sigma w'** (the value 0 gives N = 5, the value -1 gives N = -9).
- (D3) a vertex with three neighbours x_a, x_b, x_c, {a, b, c} B-independent, and no neighbour among y_a, y_b, y_c, is impossible
  (k = 3: N = 6; this is H2's e(U) >= 1 again).

Searches (`dual_test_S.py`, `dual_test_X3.py`; m in {-1,0,1,2}^10, coefficient of z in {-2..2}, k = 1, 2, 3):
**no certificate** on S for the six graphs (smallest N > 0: 10, 19, 13 or 20), and none on S u {orbit of z} for the 25 types of H2
(smallest values 10, 12 or 19, 13 or 20). So the test does not fire at these two levels. It is offered as an additional exact
filter for the enumerations on larger determined sets (S u N[p], then the orbits of X_2), where it has not been tried.

## H7. n_3 = 2: the determined set Y = S u {z, z'} u X_0 is not contradictory (computed: `n3_base.py`)

By H1 the induced graph on these 29 vertices is determined by:
- the type (U ; V);
- the case (i) / (ii) / (iii), with T normalised;
- which orbit of X_0' is inner (none or one);
- the edges between the three orbits of X_0' (two possible edge orbits per pair of orbits: 2^6).

Tests: budgets, the degree bounds of H1 (e), the exact common-neighbour statements of H1 (b), (c), and M1[Y], M2[Y] positive
semidefinite (rejection by an explicit integer vector, checked in Python integers).

Labelled configurations kept (orbits of X_0' not quotiented; types up to Aut(B) x (z <-> z')):

| Graph | labelled | after budgets + degrees | after PSD |
|---|---|---|---|
| I.0 | 640 | 186 | 136 |
| I.1 | 4608 | 1356 | 712 |
| I.2 | 1536 | 452 | 262 |
| I.3 | 2176 | 638 | 365 |
| I.4 | 2432 | 718 | 439 |
| I.5 | 1536 | 452 | 225 |

A few (type, case) are excluded at this level:
- I.1, 034 178, cases (ii), (iii);
- I.5, 016 359, case (i).

Several are reduced to one configuration:
- I.1, 278 349, case (i);
- I.2, 345 389, case (i);
- I.3, 034 156, case (i).

**n_3 = 2 survives here.** The list is the base to put under the X_2 enumeration for the variant n_3 = 2. One program only.

## H8. What transposes from the lemma of 04/10 (norm 16)

- The frame of the argument (classes X_d, path count, profiles at p) is the same. The decisive facts are not: in norm 16,
  e(X_2) <= 1 and |X_0| = 11 > |X_2| = 8, so X_0 had to see few vertices of X_2 many times (cube: 10 > 8) or the perfect matching
  in N(x) could not be completed (Wagner). Here e(X_2) >= 27 and |X_2| = 30 >> |X_0| = 9: the double counts have slack (H4), as
  round 1 A10 found (16 or 12 units of slack at p).
- The two tools still give exact statements: the identity "A^2 on an indicator, evaluated at a vertex" (used for H4 and at p) and
  the perfect matching induced on N(v) (H3). Neither closes a case by itself here.
- What is new and specific to this stage: the three earlier lemmas can be used as a rejection rule (H6).

## Open after these notes

- n_3 = 2 is not excluded by hand. Its local structure is H1-H3 and its base is H7.
- The profiles at p: no rigidity found by hand beyond round 1 A10 and round 2 I.3. H5 gives the exact reformulation; (Q0) is the
  tightest global identity found.

## H9. The n_3 = 2 branch as an enumeration (set up 07/10; the run is on AWS, see `lemma/cloud/jobs/t20_n3.sh`)

**Bases.** `n3_cases.py`: the determined set Y = S u {p} u {z, z'} u X_0' of H7, in the engine's vertex order, one representative
per class under Aut(B) x (z <-> z') x (permutations and flips of the three orbits of X_0').

| Graph | labelled, after tests | classes | profile (3,4,0) | profile (4,2,1) |
|---|---|---|---|---|
| I.0 | 136 | 44 | 25 | 19 |
| I.1 | 712 | 227 | 130 | 97 |
| I.2 | 262 | 87 | 51 | 36 |
| I.3 | 365 | 121 | 70 | 51 |
| I.4 | 439 | 146 | 85 | 61 |
| I.5 | 225 | 75 | 44 | 31 |

Profile (3,4,0) = no inner orbit in X_0' (h_2 = 3); profile (4,2,1) = one inner orbit (h_2 = 4).

**Model** (class `CaseIN3`; proofs of the numbers: H0, H1). The search places all twelve orbits of X_2, the h_2 inner pairs
included. Exact targets:

- p has 2 h_2 neighbours in X_2;
- z and z' have alpha neighbours in X_2 (alpha = 1 in case (iii), else 0);
- x in X_0' has a_0(x) + 6 - 2 a_3(x) neighbours in X_2;
- a vertex s of X_2 with W = N(s) n X_0' has exactly |W| - 2 a_3(s) neighbours in the other orbits of X_2, with |W| >= 2 a_3(s)
  and a_2(s) <= 5 - 2 a_3(s).
  Proof: a_0(s) = |W| + [s inner], a_2(s) = a_0(s) - 2 a_3(s) by (G0), and an inner s has its mate in X_2.
- An inner s has no inner neighbour in X_0' (N(p) induces a matching) and at most one end of each word orbit of X_0'; a word s is
  not adjacent to both ends of the inner orbit.

A configuration is complete when the twelve orbits are placed and every target is met exactly.

**Engine.** `eng5z.py` = the laptop session's `eng5.py` with inner orbits (zz = 1) allowed; generated by `mk_eng5z.py` (ten
replacements, each matched exactly once). An orbit is inner iff p is in its tuple N0. For inner candidates the float selection is
bypassed: budgets and semidefiniteness go through the exact routines with zz = 1.

Checks:
- eng5 and eng5z give identical counts and the same task-list sha1 on III.0, part 0 of 60, split depth 3.
- `check_inner.py`: 3000 random rows on I.0 (1442 inner): `budget_fail` and `psd_fail` with zz = 1 agree with a from-scratch count
  on the child graph and with its eigenvalues.

The dual-norm test (H6) is not used: an exclusion of n_3 = 2 by this run does not depend on T18 or on the 8/7, 9/7 lemmas.

**Status.** Not run to the end here. First base of I.0 locally: 11,729 nodes in 120 s, nodes per level
[1, 2, 62, 620, 1884, 4306, 4164, 690, 0, ...], no complete configuration, time limit reached. One program only.
