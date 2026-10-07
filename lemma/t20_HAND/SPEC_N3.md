# T20, case I, branch n_3 = 2: specification of the enumeration (for a second, independent program)

Lab session (Claude, desktop), 2026-10-07. This page is self-contained: a program written from it alone, without reading
`n3_cases.py`, `eng5.py` or `eng5z.py`, is the second program for the branch n_3 = 2.
Every statement of the model is proved here or in `NOTES.md` (H0, H1). Nothing here is a result: the claim to be tested is at the end.

## 1. Setting

G is a strongly regular graph with parameters (99, 14, 1, 2), adjacency matrix A: A^2 = 12 I - A + 2 J.
sigma is an automorphism of order 2 with exactly one fixed vertex p.

Facts (M), from the project model:
- For v != p: v ~ sigma v if and only if v is in N(p). N(p) is seven disjoint "mate edges" {a, sigma a}. Such vertices are **inner**.
- A vertex w outside N[p] is a **word**: w is not adjacent to sigma w, and w has exactly two neighbours in N(p), in two different
  mate edges.
- lambda = 1: two adjacent vertices have exactly one common neighbour. mu = 2: two non-adjacent vertices have exactly two.
- Consequence: a vertex other than p is never adjacent to both ends of a mate edge (they already share p).

Case I of T20: S+ = {x_0, ..., x_9}, S- = {y_i = sigma x_i}, both independent, S = S+ u S- disjoint from N[p], and
x_i ~ y_j if and only if i ~ j in a 4-regular graph B on {0, ..., 9}. B is one of six graphs I.0 ... I.5 (edge lists in section 6).

For q outside S, d(q) = |N(q) n S+| = |N(q) n S-|. X_d = {q outside S : d(q) = d}; a_j(q) = |N(q) n X_j|. p is in X_0.

    a_1 + 2 a_2 + 3 a_3 = 20 - 5d,        a_0 = a_2 + 2 a_3 + 3d - 6.                                   (G0)

(Proof: evaluate A^2 1_{S+} at q.) Here n_3 = |X_3| = 2, so |X_0| = 7, |X_1| = 46, |X_2| = 24.

Profile: h_j = number of mate edges of N(p) inside X_j. Two profiles remain: (h_2, h_1, h_0) = (3, 4, 0) and (4, 2, 1).

## 2. The base (29 vertices)

Y_0 = S u {p} u X_3 u X_0', with X_3 = {z, z' = sigma z} and X_0' = X_0 minus {p} (six vertices, three sigma-orbits).

Proved facts (NOTES H1):
1. z is a word; z is not adjacent to z' nor to p. z ~ x_i for i in U, z ~ y_j for j in V, |U| = |V| = 3 (then z' ~ y_i for i in U,
   z' ~ x_j for j in V). |U n V| <= 1.
2. p has no neighbour in S. No vertex of X_0 has a neighbour in S.
3. p ~ x (x in X_0') if and only if x is inner. X_0' contains h_0 inner orbits: none, or exactly one. An inner orbit is a mate
   edge; a word orbit is a non-edge.
4. T = N(z) n X_0' and N(z') n X_0' = sigma T. Exactly one of three cases:
   - (i): T has one vertex in each of the three orbits. (Then N(z) n N(z') is {x_i, y_i} with U n V = {i}, or an orbit of X_1.)
   - (ii): U n V is empty; T = both vertices of one orbit O_0, one vertex of a second orbit O_1, none of the third, O_2.
   - (iii): U n V is empty; T = both vertices of one orbit O_0 and one vertex of each of the two others.
   In (ii) and (iii) the orbit O_0 is a word orbit, and its two vertices have no common neighbour other than z and z'.
5. alpha = a_2(z) is 0 in cases (i), (ii) and 1 in case (iii). a_3(z) = 0.
6. Between two different orbits {c, sigma c}, {e, sigma e} of X_0' the edges form sigma-orbits: "direct" (c ~ e and
   sigma c ~ sigma e) and "cross" (c ~ sigma e and sigma c ~ e), each present or not: four patterns per pair of orbits.
7. For x in X_0', with a_0(x) = [x ~ p] + |N(x) n X_0'| and a_3(x) = [x ~ z] + [x ~ z']:
   a_2(x) = a_0(x) + 6 - 2 a_3(x) and a_1(x) = 8 - 2 a_0(x) + a_3(x) >= 0.

So the induced graph on Y_0 is determined by: B; the type (U ; V); the case with T; which orbit is inner (or none); the 2^6 edge
patterns between the three orbits. A program must enumerate **all** of these (symmetry reduction is optional; see section 5).

Tests on a base (all are necessary conditions):
- **Budget.** In any vertex set whose induced graph is known, two adjacent vertices have at most 1 common neighbour inside the
  set and two non-adjacent vertices at most 2.
- **Degrees.** a_1(x) >= 0 in fact 7, i.e. a_0(x) <= 4 if a_3(x) <= 1 and a_0(x) <= 5 if a_3(x) = 2.
- **Semidefiniteness.** M1 = 9 (3I - A) + J and M2 = 11 (4I + A) - 2J are positive semidefinite on all 99 vertices
  (they are 63 and 77 times the projectors on the eigenspaces -4 and 3). So their principal submatrices on a known induced graph
  are positive semidefinite. A rejection must be exact: an integer vector x with x^T M x < 0 computed in integers, or exact
  rational elimination. A floating-point test may only keep.

Reference counts of the first program (types up to Aut(B) x (z <-> z'), orbits of X_0' labelled, T normalised as above):

| Graph | labelled | after budget + degrees | after semidefiniteness | classes under all relabellings |
|---|---|---|---|---|
| I.0 | 640 | 186 | 136 | 44 |
| I.1 | 4608 | 1356 | 712 | 227 |
| I.2 | 1536 | 452 | 262 | 87 |
| I.3 | 2176 | 638 | 365 | 121 |
| I.4 | 2432 | 718 | 439 | 146 |
| I.5 | 1536 | 452 | 225 | 75 |

## 3. The orbits of X_2

X_2 has 24 vertices in 12 sigma-orbits. For s in X_2: U_s = {i : s ~ x_i}, V_s = {j : s ~ y_j}, |U_s| = |V_s| = 2, and
U_{sigma s} = V_s.

**Units.** x_i and x_j (i != j) are not adjacent, so they have exactly two common neighbours. Those in S are the y_l with l a
common B-neighbour of i and j. z is one if i, j are both in U; z' is one if both are in V. All the others are in X_2
(a common neighbour outside S has d >= 2, and X_3 = {z, z'}). So the number of s in X_2 with U_s = {i, j} is exactly

    need(i, j) = 2 - codeg_B(i, j) - [i, j in U] - [i, j in V],

and the sum of need over all pairs is 24. s -> U_s is a bijection from X_2 onto the units counted with multiplicity.

**Data of an orbit {s, sigma s}** (everything else follows by sigma):
- U_s and V_s. V_s != U_s.
- [s ~ p]: s is inner or a word. An inner s has s ~ sigma s and U_s n V_s empty.
- [s ~ z], [s ~ z']: never both. (N(z) n N(z') does not meet X_2: NOTES H1 (b).) So a_3(s) is 0 or 1.
- W = N(s) n X_0'.
- for every other orbit {t, sigma t} of X_2: [s ~ t] and [s ~ sigma t].

**Exact numbers.**
- p has exactly 2 h_2 neighbours in X_2: the h_2 inner orbits of X_2. h_2 = 3 if X_0' has no inner orbit, 4 if it has one.
- z has exactly alpha neighbours in X_2, and so has z'.
- x in X_0' has exactly a_0(x) + 6 - 2 a_3(x) neighbours in X_2 (fact 7).
- s in X_2: a_0(s) = [s ~ p] + |W|, and by (G0) a_2(s) = a_0(s) - 2 a_3(s), a_1(s) = 10 - 2 a_2(s) - 3 a_3(s) >= 0. Hence:
  - |W| >= 2 a_3(s) - [s ~ p] and a_2(s) <= 5 if a_3(s) = 0, a_2(s) <= 3 if a_3(s) = 1;
  - the number of neighbours of s in the eleven **other** orbits of X_2 is exactly |W| - 2 a_3(s), for a word and for an inner
    vertex alike (an inner s has one more neighbour in X_0, namely p, and one more in X_2, namely sigma s).
- An inner s is adjacent to no inner vertex of X_0' and to at most one end of each word orbit of X_0'. A word s is not adjacent
  to both ends of the inner orbit of X_0'. (All three follow from the budget test with p in the set.)

**Complete configuration** on a base: twelve orbits with their data such that the induced graph on the 29 + 24 vertices passes
the budget and semidefiniteness tests, every unit {i, j} is realised exactly need(i, j) times, and every exact number above holds.

## 4. Why a search over units is exhaustive

Suppose G exists with this base. Take any state made of the base and k < 12 orbits of X_2 of G with their true data. Some unit has
fewer realisations among the placed vertices than its need; pick one, {i, j}, by any rule. In G an unplaced vertex s has
U_s = {i, j}. Its true data is one of the finitely many candidates (V_s, [s ~ p], [s ~ z], [s ~ z'], W, the two bits to each
placed orbit). The state with the orbit of s added is again made of true orbits, so it passes every necessary test, with the
exact numbers read as upper bounds while the configuration is incomplete. By induction the search reaches a complete
configuration. So: **if for every base the exhaustive search finds no complete configuration, the branch n_3 = 2 of case I is
impossible.** The rule choosing the unit is free. A candidate may be rejected only by an exact computation.

## 5. Symmetry (optional)

The following relabellings preserve the model, so one base per class is enough: an automorphism of B applied to the indices of
S+ and S- together; the exchange z <-> z'; a permutation of the three orbits of X_0'; the exchange of the two vertices inside an
orbit of X_0'. The first program takes the types (U ; V) up to Aut(B) x (z <-> z') first, then one representative per class of
bases under all the relabellings. A second program may skip any of this at the price of redundant work.

## 6. Data

Edges of B (two digits = one edge):

    I.0: 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79
    I.1: 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78
    I.2: 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89
    I.3: 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79
    I.4: 01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79
    I.5: 01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89

## 7. Hand lemmas that a program may assume, if it says so

They are proved in `lemma/t20_CODEX/PROFILE_421.md` and NOTES H10, and checked by a second reader. A base violating one of them
may be discarded and counted separately.
- Profile (4,2,1): the inner orbit of X_0' has no edge to the two other orbits of X_0'.
- Profile (4,2,1): the inner orbit of X_0' has a_3 = 1 (each of its two vertices is adjacent to exactly one of z, z').

## 8. What the second program must report

For each graph: the number of bases generated, kept after each test, and (if symmetry is used) the classes; for each base
searched: nodes per level, number of complete configurations, and whether it ran to the end. The claim to confirm or refute:

**For every base of the six graphs the search ends with no complete configuration.**

First program (`eng5z.py` on the bases of `n3_cases.py`), state on 07/10 at 11:30 UTC: 168 of 700 classes closed, none with a
complete configuration, deepest level 7 of 12; the rest is running.
