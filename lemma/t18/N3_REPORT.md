# T18: no outside vertex with d = 3 (proved by hand, 2026-10-06)

Result of the agent in charge of the cases n_3 > 0; the proof below was re-read line by line in the main session.
Notation of `T18_REPORT.md`: S = S+ u S- is the support, both sides independent, S disjoint from N[p] (A5), so every vertex of S has
exactly 4 neighbours in S. For z outside S, d(z) = number of its neighbours in S+ = number in S-; X_k = {z outside S : d(z) = k},
n_k = |X_k|. Each X_k is sigma-invariant.

**Lemma 1.** For z outside S with d(z) = d, the sum of d(w) over the neighbours w of z outside S is 18 - 5d.

Proof. Count the pairs (w, s) with s in S, w ~ z, w ~ s.
- Over s: the 2d neighbours of z in S give 1 each (lambda = 1), the other 18 - 2d give 2 each (mu = 2). Total 36 - 2d.
- Over w: the 2d neighbours of z in S give 4 each; an outside neighbour gives 2 d(w). Total 8d + 2 sum d(w).

So sum d(w) = 18 - 5d, and d <= 3. For d = 3, z has 8 neighbours outside S with sum of d equal to 3, so at least 5 of them are in X_0.

**Lemma 2.** n_0 = 9 - n_3, n_1 = 54 + 3 n_3, n_2 = 18 - 3 n_3.

Proof. sum n_k = 81; sum d(z) = 9 x 10 = 90; sum C(d(z), 2) = 18 (the 36 pairs of S+ are non-adjacent and have 72 common neighbours,
none in S+, and S- supplies 9 x C(4,2) = 54). Solve.

**Theorem N3. X_3 is empty**, for B0, B1 and B2 (the argument uses neither B nor the profile at p nor any semidefiniteness test).

Proof. Let z be in X_3. Then z' = sigma z is in X_3 and z' != z (the only fixed vertex is p and d(p) = 0). So n_3 >= 2 and
|X_0| <= 7. By Lemma 1, T = N(z) n X_0 and T' = N(z') n X_0 each have at least 5 elements, inside X_0, so |T n T'| >= 3.
But two distinct vertices have at most 2 common neighbours. Contradiction.

**Consequences.**
- (n_0, n_1, n_2, n_3) = (9, 54, 18, 0) for the three graphs.
- "d(a_c) <= 2" and "B1 has no d = 3 vertex", obtained by computation in round 1, are now proved by hand; A9 reads h_0 <= 1.
- The stage-1 matchings of the 18 deficient pairs (B0: 425 orbits, B1: 1,259, B2: 528) describe X_2 completely.
- **What is left of T18: the profile (2,5,0) at p, for B0, B1 and B2. Nothing else.**

**By-product (by hand, uses |X_0| = 9).** For z outside S, z != p, let T = N(z) n X_0. T n sigma T is inside N(z) n N(sigma z), so:
z in N(p): 2|T| - 1 <= 9; z not in N(p): 2|T| - 2 <= 8; z in X_0 and not adjacent to p: 2|T| - 2 <= 6.
Hence a_0 <= 5 for every outside z != p, and a_0 <= 4 on X_0 minus N[p]; with a_0 = a_2 + 3d - 4: a_2 <= 3 on X_2, a_2 <= 6 on X_1,
a_2 <= 8 on X_0 minus p in profile (2,5,0).

Arithmetic guard (not part of the proof): `n3_check.py` in the session scratchpad (`t18_N3`), exact integers, all checks passed.
