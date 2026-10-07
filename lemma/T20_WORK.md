# T20: work page for the sessions attacking it together (07/10)

Goal: **prove T20**. Three sessions work on it at once (this laptop session, a second Claude session, a Codex session). The point
is to split the proof, not to re-verify each other: the only cross-check kept is the project's rule that every computed step
exists in two programs, and that falls out of the split below.

## 1. The statement, and why it is the last lock

G = strongly regular graph srg(99,14,1,2), adjacency A, spectrum 14, 3 (x54), -4 (x44). sigma = an automorphism of order 2 with
exactly one fixed vertex p.

> **T20.** There is no integer-valued function phi on the vertices with phi(sigma x) = -phi(x), A phi = -4 phi and
> sum phi(x)^2 = 20.

T18 (the same with 18) is proved: `lemma/T18_PROOF.md`. `lemma/BRIDGE.md` shows that a pair (y1, y2) of the search engine with a
root r such that (r,y1)^2 + (r,y2)^2 = 5, resp. 4, would give such a phi of squared norm 18, resp. 20. The fleet has swept all
156 envelopes; every one of the 13 remaining lattices holds pairs waiting on T20 (about 2.4 million in all). With T20 the
exclusion of the 156 is complete (modulo the lab's import). Without it those pairs must be searched one by one.

## 2. What is established (do not redo)

`lemma/t20/T20_REPORT.md` (round 1), `lemma/t20_R2/REPORT.md` (round 2), `lemma/t20_III1/` (round 3).

- phi takes values in {0, +-1} with ten vertices at +1 (S+ = {x_0..x_9}, S- = sigma S+), except patterns excluded by hand.
- k = number of active inner orbits (support orbits inside N(p)) is 0, 2 or 4, with e(S+) = 0, 1, 0.
- The support structures were enumerated (two programs): **nine configurations**.

| Configuration | Status |
|---|---|
| III.0 (k = 4) | excluded: computation, two programs |
| III.1 (k = 4) | computed, 0 configurations (one program); the independent verifier is running |
| IIa.0 (k = 2) | excluded: hand lemmas + computation, two independent programs |
| **I.0 ... I.5 (k = 0)** | **OPEN: this is the work** |

## 3. The open case: k = 0

S+ and S- are independent sets, S is disjoint from N[p], p has no neighbour in S. B = the graph on {0..9} with i ~ j iff
x_i ~ y_j: 4-regular, any two vertices have at most 2 common neighbours, connected, eigenvalues other than 4 in [-3, 3].
Six graphs (edge lists, automorphisms, spectra: round 1, section C):

| | edges of B | Aut |
|---|---|---|
| I.0 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79 | 16 |
| I.1 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78 | 4 |
| I.2 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89 | 10 |
| I.3 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79 | 4 |
| I.4 | 01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79 | 4 |
| I.5 = C10(1,2) | 01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89 | 20 |

Notation: for z outside S, d(z) = number of neighbours in S+ (= in S-); X_d = {z : d(z) = d}, n_d = |X_d|; a_j(z) = number of
neighbours of z in X_j. N(p) = seven mate edges {a_c, b_c}; delta_c = d(a_c) = d(b_c); h_j = number of c with delta_c = j;
profile = (h_2, h_1, h_0).

Known by hand (round 1 A10, round 2 G0, G1, I.1 - I.3):
- n_4 = 0; n_0 = 9 - n_3, n_1 = 40 + 3 n_3, n_2 = 30 - 3 n_3; p is in X_0; sum delta_c = 10.
- G0: for z outside S, a_0 - a_2 - 2 a_3 = 3 d(z) - 6 (no plus edge here), and the d-sum over the outside neighbours of z is
  20 - 5 d(z).
- No vertex of N(p) has d = 3. **n_3 is 0 or 2.** Profile (5,0,2) is impossible.
- **Left, for each of the six graphs: profiles (3,4,0) and (4,2,1), each with n_3 = 0 or n_3 = 2.**

## 4. What worked for T18 (the same toolbox)

`lemma/T18_PROOF.md`, sections 5 to 8. In short:
- Vertex sets whose induced graph is DETERMINED by a small amount of data (a matching of the deficient pairs of B, the pairs of
  N(p), ...), grown step by step; at each step two exact tests on the known induced graph Y:
  budgets (two vertices have at most 2 - [adjacent] common neighbours inside Y), and positive semidefiniteness of the principal
  submatrices of **both** M1 = 9(3I - A) + J = 63 E_{-4} and M2 = 11(4I + A) - 2J = 77 E_3.
- The **rank bound**: for sigma-invariant Y the sigma-odd part of M1[Y] has rank <= 22 and the even part <= 22, so the odd Gram
  3I - A^ of any 23 orbits is singular. It killed configurations that passed everything else.
- A five-line hand theorem removed n_3 > 0 entirely in T18 (Theorem 5.3). Here the same count only gives n_3 <= 2.
- Integer eigenvectors built from the support: psi = (3I - A + J/9) 1_S and relatives gave identities for free (in T18, 9 divides
  |S|; here |S| = 20, so the analogue needs care).

## 5. Work packages

**A. By hand (second Claude session).** Every sub-case removed by hand halves the computation.
1. n_3 = 2: the two vertices of X_3 form one orbit {z, sigma z}, z a word, with |N(z) n X_0| >= 3 and 2 |T| - 2 <= 6. Find the
   contradiction, or at least pin the structure down (T, the type (U ; V) of z) so that the X_3 orbit can be put in the base.
2. Profiles: derive everything forced at p for (3,4,0) and (4,2,1): the X_2 / X_1 / X_0 neighbours of p, the values of a_2 on
   N(p), equality cases. In T18 the analogue of the tighter profile was fully rigid.
3. Any structural identity special to norm 20 (the vectors psi, chi, rho of `lemma/t18_STRUCT/REPORT.md` section 1 with |S| = 20).
Output: complete written proofs, in a file `lemma/t20_HAND/NOTES.md`.

**B. Enumeration, graphs I.3, I.4, I.5 (Codex session).** Write your own enumerator from this page and round 1 section C: base
S u N[p] for a profile (the seven pairs of N(p) with their types), then the orbits of X_2 one by one, exact tests at every node,
exhaustive. No SAT / CP / ILP / LP solver; rejections must be exact (a count, an integer vector with negative form, an exact
rank); a float test may only "keep". Report node counts per level and the number of complete configurations.
Output: `lemma/t20_CODEX/`.

**C. Enumeration, graphs I.0, I.1, I.2 (this laptop session).** Same, with the round-2 engine (`lemma/t20_R2/eng5.py`,
`cases.CaseIN`), extended to n_3 = 2. An agent started on it at 09:30 UTC (scratchpad `t20_R3_I`).
Heavy runs can go on AWS machines: ask this session.

When B and C have both finished a graph each, they swap one graph: that is the second program, with no extra round.

## 6. Rules of the project

- No SAT, CP, ILP or LP solver anywhere.
- A hand statement is written with its full proof. A computed statement says what is enumerated, why it is exhaustive, how
  symmetry is used, and gives the counts.
- Say plainly what is proved, what is computed, what is open. Nothing of T20 enters the search engine before it is complete.
- Python on this laptop: `%TEMP%\claude\C--Users-RESEARCHER-Desktop-Nouveau\aa6b3504-976d-4158-b7e9-dd8eff8d22bb\scratchpad\pkgfull\.venv\Scripts\python.exe`
  (numpy, python-flint). The laptop is slow (about a third of nominal speed) and has 15 GB of RAM: at most 6 heavy processes.
