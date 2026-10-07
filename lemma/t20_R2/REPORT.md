# T20, round 2 (07/10, 00:37 - 04:50 local)

Agent report, saved by the main session. Notation of `lemma/t20/T20_REPORT.md` (round 1). Scripts and outputs: this folder
(files over 400 kB and the abandoned partial runs are not in git).

**T20 is not proved.** Two of the nine configurations are excluded (III.0 and IIa.0, each by an exhaustive exact computation run by
two programs); seven are open (III.1 and the six graphs of case I). Neither T18 nor the 04/10 lemma is used. No solver.

| Configuration | Status | Point reached |
|---|---|---|
| III.0 (k = 4, hexagon) | **excluded, computed, two implementations** | 130,004 nodes, 0 configurations on S u N[p] u X_2. Tests independent; the model file `cases.py` is shared. |
| IIa.0 (k = 2) | **excluded: hand lemmas II.1-II.6 + computation, two fully independent programs** | 180 -> 87 types of N(p); then 45,497 nodes, 0 configurations on S u N[p] u X_2. |
| III.1 (k = 4, two triangles) | **open** | Same enumeration as III.0, but 21,165 tasks at depth 3 instead of 7,109. Estimated 5-7 CPU-hours; not completed (about 900 tasks done, no survivor). |
| I.0 - I.5 (k = 0) | **open** | By hand: no d = 3 vertex in N(p), n_3 in {0, 2}, profile (5,0,2) impossible. Left: profiles (3,4,0) and (4,2,1), each with n_3 = 0 or 2. |

So k = 2 is closed. k = 4 is closed except III.1.

## A. Hand arguments

For z outside S: d(z); a_j(z) = number of neighbours in X_j; q(z) = number of neighbours that are ends of a plus edge; type (U ; V) =
indices of N(z) n S+ and N(z) n S-. Used from round 1 A0: **(M)** N(p) is seven mate edges and induces a perfect matching; a vertex
other than p is never adjacent to both ends of a mate edge. A word z is not adjacent to sigma z, and N(z) n N(sigma z) has exactly 2
elements.

**G0 (identity).** For z outside S with d = d(z): the sum of d(w) over the neighbours w of z outside S is 20 - 5d - q(z), and

    a_0 - a_2 - 2 a_3 - 3 a_4 = 3d + q(z) - 6.

Proof. Count pairs (w, s), s in S, w in N(z) n N(s). By s: 2d * 1 + (20 - 2d) * 2 = 40 - 2d. By w: a neighbour in S has 4 + 2 d+
neighbours in S, a neighbour outside has 2 d(w); total 8d + 2q + 2 sum d(w). Then use sum a_j = 14 - 2d and
sum j a_j = 20 - 5d - q.

**G1 (bound).** Let T = N(z) n X_0. If z is a word, p not in T and T n sigma T in N(z) n N(sigma z), so 2|T| - 2 <= |X_0 minus p|.
If z in N(p), z not in S, then N(z) n N(sigma z) = {p}, so 2|T| - 1 <= |X_0|.

### Case II (k = 2, e = 1, Q = 2; plus edge x_2 x_3 in a quad)

- **II.1.** n_0 + n_3 + 3 n_4 + ... = 4 (round 1). d(p) = 2 and q(p) = 0.
- **II.2. d <= 3.** If d >= 4, G0 gives a_0 >= 3d - 6 >= 6 > 4 >= n_0.
- **II.3. n_3 = 0.** If d(z) = 3 then z != p and sigma z != z also has d = 3, so n_0 <= 2; but G0 gives a_0(z) >= 3. Hence n_0 = 4,
  n_1 = 54, n_2 = 21.
- **II.4. No vertex of N(p) outside S has d = 2 or d = 0.** G0 at p gives a_0(p) = a_2(p). Suppose f in N(p), f not in S, d(f) = 2.
  Its mate has d = 2 and is adjacent to f, and p in X_2, so a_2(f) >= 2 and G0 gives a_0(f) = a_2(f) + q(f) >= 2. By (M) the
  X_0-neighbours of f are words, at most one per sigma-orbit. So X_0 (4 vertices) is two word orbits and a_0(p) = 0. But
  a_2(p) >= 2. Contradiction. Hence a_2(p) = 0 = a_0(p): the ten inactive vertices of N(p) all have d = 1. Call them W. X_0 is two
  word orbits.
- **II.5. Types of W.** w in W has type (i ; k), its mate (k ; i). i, k are words (M). i != k, else x_i is a second common neighbour
  of w and sigma w. Two pairs of W never have the same unordered type, else two non-adjacent vertices share p, x_i, y_k. A word x_i
  has exactly 2 common neighbours with p, so exactly 2 - r_i neighbours in W (r_i = neighbours among x_0, y_0, x_1, y_1). For
  IIa.0: r = 0 for i = 2, 4 and r = 1 for i = 3, 5, 6, 7, 8, 9. So the five types form a simple graph on {2..9} with degrees
  (2,1,2,1,1,1,1,1): 180 graphs.
- **II.6. X_2 minus p.** Let s be such a vertex. s is a word, not adjacent to p or sigma s (II.4). It has exactly 2 - r(s) neighbours
  in W, never two mates. G0: a_2(s) = a_0(s) - q(s), and G1 gives a_0(s) <= 3, so at most 3 - q(s) neighbours in X_2 minus p. A
  vertex w of W has a_2(w) = a_0(w) + 3 - q(w) with a_0(w) <= 2, and p is one of its X_2-neighbours: at most 4 - q(w) neighbours in
  X_2 minus p. The 20 deficient units of S+ are exactly the sets N(s) n S+, one per s.
- By-product, not used: X_0 contains no 4-cycle (x = -1 on S u {p}, -2 on x_2, x_3, y_2, y_3, +2 on the 4-cycle gives
  x^T (9(3I - A) + J) x = 1323 - 1656 + 289 = -44).

### Case III (k = 4): model, from round 1 A9 and G0

- X_4 = {p}; X_0 = the six inactive inner vertices; n_3 = 0; |X_2| = 24.
- A vertex s of X_2 is a word, not adjacent to p or sigma s. With r(s) = number of active inner neighbours: exactly 2 - r(s)
  neighbours in X_0 (different pairs) and, by G0, exactly 2 - r(s) neighbours in X_2.
- A vertex of X_0 has exactly 4 neighbours in X_2. The 24 units are the sets N(s) n S+.

### Case I (k = 0)

- **I.1. No vertex of N(p) has d = 3.** Such a z has its mate in X_3, so G0 gives a_0 >= 3 + 2 = 5. G1 gives
  2 * 5 - 1 <= |X_0| = 9 - n_3 <= 7. Contradiction. So delta_c <= 2 for all six graphs.
- **I.2. n_3 in {0, 2}.** For z in X_3 (a word), G0 gives |T| >= 3 and G1 gives 2|T| - 2 <= 8 - n_3, so n_3 <= 4. If n_3 = 4: X_0
  minus p is two orbits O_1, O_2, and each T is a full orbit plus one vertex. Two X_3 orbits cannot contain the same full orbit. So
  T(z) = O_1 u {v} and T(z') = O_2 u {u'}. Then z, z' share exactly v and u'; z, sigma z' share v and sigma u'; z, sigma z share
  O_1; z', sigma z' share O_2. None of these pairs has a further common neighbour in S. So U, V, U', V' are four pairwise disjoint
  3-subsets of {0..9}: 12 > 10.
- **I.3. Profile (5,0,2) is impossible.** Let u_1, sigma u_1, u_2, sigma u_2 be the X_0 vertices of N(p). G0 gives
  a_2(u) = a_0(u) + 6 - 2 a_3(u) >= 8 - 2 a_3(u). Their X_2-neighbours lie outside A_p = N(p) n X_2 (10 vertices), by (M). Mates
  share only p; u_1 and u_2 share p and one more vertex. So the union of the four X_2-neighbourhoods has at least sum a_2 - 4
  elements. n_3 = 0: 28 > 20. n_3 = 2: sum a_3 <= 4, so 20 > 14.
- **Left for each of the six graphs:** profiles (3,4,0) and (4,2,1), with n_3 = 0 or n_3 = 2.

## B. Computations

A rejection is a common-neighbour count on a completely known induced graph, or an integer vector with negative form for M1 or M2
evaluated in Python integers, or exact rational elimination (never needed). "Kept" is a floating-point decision and proves nothing.
The rank bound is implemented (exact, flint) but never fired: every branch dies before 23 orbits.

Search (both cases): a node is a completely known sigma-invariant graph (base plus t orbits of X_2). One uncovered unit U is chosen;
some vertex z of X_2 outside the node has N(z) n S+ = U; all its data are enumerated (V, its neighbours in the base outside S, one
of four edge patterns to each earlier orbit, within the degree bounds). Every candidate is kept or rejected exactly. No node at the
last level means no configuration.

**B1. III.0**: base S u N[p] (27 vertices), 12 orbits to place. Symmetry: the 48 relabellings of X_0.

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Nodes | 1 | 13 | 116 | 881 | 7,109 | 30,102 | 54,327 | 31,126 | 6,086 | 243 | 0 |

Total 130,004 nodes; 4,094,709 candidates; 671,315 rejected by budgets, 3,293,391 by PSD certificate, 130,003 kept; **0 complete**;
no time-out. `eng3.py` and `eng4.py` give identical numbers. Independent verifier `engv.py` (candidate generation rewritten, full
budget recount): same kept count at all 130,004 nodes, 0 complete. 15,000 saved certificates re-checked by a pure-Python checker: 0
invalid.

**B2. IIa.0.** Step 1: of the 180 type graphs of II.5, on S u N[p] (31 vertices): 63 rejected by budgets, 30 by PSD certificate,
**87 kept** (two programs, identical lists). Step 2: for each of the 87, base S u N[p], 10 orbits of X_2.

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| Nodes | 87 | 520 | 3,148 | 11,451 | 18,324 | 10,279 | 1,640 | 48 | 0 |

Total 45,497 nodes; 898,945 candidates; **0 complete** (`eng5.py`). Second program `iian_verify.py` shares no code and builds its own
model: same kept count at all 45,497 nodes, 0 complete. 6,358 saved certificates re-checked: 0 invalid.

**B3. III.1: not a result.** 21,165 tasks at depth 3. 159 sampled tasks all die, about 80 nodes per task, so roughly 1.7 million
nodes. Two launches were stopped (the laptop was throttled to about one core); about 900 tasks done, no survivor.

**B4. Explorations (prove nothing).** Case I with N(p) in the base, graph I.0: profile (4,2,1) has 1,784,786 configurations of N(p),
of which 48,587 pass budgets and a float PSD test. Profile (3,4,0) was not finished. 81 sampled bases all die in 0.3 - 2.1
CPU-seconds each.

## C. Open, and next step

- **III.1.** Run the six parts with `OPENBLAS_NUM_THREADS=1` on a machine that is not throttled:
  `run_eng5.py III.1 <i> 6 <limit> 3 e5_III1 setwise plan certs=2500`, then `summary_parts.py e5_III1 6` (checks no time-out, equal
  task-list hash, 0 complete). Aut(III.1) has order 4; using it would roughly halve the work. For a second implementation,
  `engv2.py` exists but has not been validated on a full run; check it against `v_III0_0of3.out` first.
- **Case I.** Put N(p) in the base, as for IIa. Per graph and profile, enumerate the configurations of N(p) with exact certificates
  and Aut(B) reduction, then run `eng5.py` with `cases.CaseIN` (written, n_3 = 0 only). The n_3 = 2 variant needs the X_3 orbit
  added to the base; it is not written. From the I.0 sample the cost is under one CPU-second per base, so a few CPU-hours per graph
  after symmetry reduction.

## D. Notes on rigour and process

- The first version of `iii_enum.py` applied a PSD test to a non-induced subgraph and wrongly reported 0 survivors in 0.2 s. It was
  caught and fixed; nothing from it is used.
- The fast engine selects with float64 products of 0/1 matrices; every budget rejection it uses is recounted in int64.
- 82 of the 87 IIa certificate files (about 1.6 GB) were deleted to save disk; five are kept (not in git).
- The laptop ran at about a third of its clock speed during the night (screensaver, 1.2 GHz of 3.6): heavy enumerations for T20
  should run elsewhere.
