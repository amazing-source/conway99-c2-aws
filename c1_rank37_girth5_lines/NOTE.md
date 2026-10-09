# Rank 37: a line whose graph has girth at least 5 is connected (computer-assisted)

Written 2026-10-08/09 by the laptop session. Hand derivation plus exhaustive finite searches (Python and C, standard
library only). **Not audited by a third party.** Nothing here excludes rank 37.

## Statement

Let Gamma be a srg(99,14,1,2), A its adjacency matrix, and suppose rank_7(A - 3I) = 37. Let T be a line (triangle) and
G(T) the cubic graph induced on the 36 neighbours of T. **If G(T) has no triangle and no 4-cycle, then G(T) is
connected.**

Equivalently: at rank 37 no line has a graph made of two components of 18 vertices of girth >= 5 (the profile called
"(6,6)" in the September notes). A component with one or two lines per layer always has a triangle or a 4-cycle
(`small_comp.py`: 0 of 2 and 0 of 216 normal forms), so a disconnected graph of girth >= 5 has exactly two components
with three lines per layer each.

With the September notes 125 and 126 of conway99-c1 (not re-proved here): in the world P = S = 0 every line then has a
connected graph, so the residual case "(6,6) everywhere" of note 126 par.3 ter does not occur at rank 37.

## Why a finite search decides it

1. Q = A - 3I + 3J has rank 36 mod 7 (the all-ones vector is in the row space of A - 3I and orthogonal to that of Q).
   Let V = F_7^99 / ker Q with the form Q, of dimension 36 and non-degenerate, and p_v the image of e_v:
   <p_v, p_v> = 0, <p_v, p_w> = 4 if v ~ w, 3 otherwise. For every vertex x, 4 p_x + sum of p_y over the neighbours y = 0.
2. For a line T the Gram matrix of the 36 vectors p_w, w in N(T), is M0 = 3J - H with H = 3I - G(T) the Laplacian. Its
   radical is R0 = ker_7 H cap {sum = 0}.
3. If G(T) = C1 + C2, the vector z0 = 1_C1 - 1_C2 is an integer 3-eigenvector of A (every far vertex has exactly 3
   neighbours in each component), so it is a true relation among the p_w. The other elements of R0 are the 7-torsion
   vectors of the two components (sum zero on their component). A torsion vector phi is a true relation exactly when
   it is "balanced": every far vertex has phi-sum 0 on its shadow.
4. Let Tr be the true relations and r = dim R0 - dim Tr. Then span{p_w} has dimension 36 - dim Tr and radical of
   dimension r, and since V is non-degenerate of dimension 36: dim R0 <= 2 dim Tr.
5. `balanced66.py` (lemma I, already in note 126 par.3 bis with its own check): a torsion vector carried by ONE
   component is never balanced. For each torsion vector, at least 24 (types 2, 3) or 12 (type 5) pairs {x, y} of the
   component lie in fewer admissible triples of phi-sum 0 than their number K[x][y] of common far neighbours.
   Hence the balanced torsion is the graph of an injective map between the torsion spaces of C1 and C2, and with
   point 4 the torsion ranks t1, t2 differ by at most 1.
6. The 7 isomorphism types of components (`comp66.py`: 288 normal forms, as in the lab's count; torsion rank 0 for
   types 0, 1, 4, 6, rank 1 for types 2, 3, rank 3 for type 5) leave four cases:

| case | true relations | radical of the span | residue | what a far vertex f carries |
|---|---|---|---|---|
| (0,0) | z0 | 0 | 1 | a scalar xi_f |
| (0,1) | z0 | phi (unbalanced) | 0 | a scalar alpha_f, and s_f = phi . n_f |
| (1,1) | z0, phi1 + lambda phi2 (lambda != 0) | phi1 | 1 | alpha_f, nu_f, s_f = phi1 . n_f; shadows with (phi1 + lambda phi2) . n = 0 |
| (3,3) | z0 and the graph of an isomorphism theta | 3 | 1 | shadows with sigma1(n) + M sigma2(n) = 0, M in GL_3(F_7) |

7. In every case V is the span of the p_w, plus a dual vector m for each radical direction, plus an anisotropic line
   <n> when the residue is 1. For a shadow n (a 0/1 vector on N(T)): s = phi . n, rhs = 3 + n - s beta (beta a functional
   with beta(phi) = 1, beta(Tr) = 0), M0 c = rhs, g(i, j) = c_i . rhs_j, and the far vertices satisfy
   - g(f, f) + 2 alpha_f s_f + c0 nu_f^2 = 0,
   - g(f, f') + alpha_f s_f' + alpha_f' s_f + c0 nu_f nu_f' = 3 + A_ff',
   - for a ball vertex u: sum of nu_f over its ten far neighbours = 0, and sum of alpha_f = -(4 beta_u + beta_t +
     beta_u' + beta_u1 + beta_u2) (t the apex of u, u' its mate, u1, u2 its two other neighbours in the ball).
   In case (0,0), with H^+ the inverse of H on the vectors of sum zero on each component, g = 6 - n^T H^+ n'.
   (`check_model.py` builds the Gram matrix of this model explicitly, finds rank 36 and the expected kernel, and
   compares the formulas on random pairs: 0 mismatch.)
8. A "star" is the set of the ten far neighbours of a ball vertex u. Its ten shadows are 6-sets through u, two points
   per layer, three in each component, no two mates, at most one G-neighbour of a member inside, at most two
   G-neighbours of an outside vertex inside; their sum is the row K e_u (numbers of common far neighbours); two of them
   (the "apexes", containing a transversal neighbour of u) are adjacent to no other, the eight others are matched in
   four adjacent pairs; adjacent ones meet only in u, non-adjacent ones in at most two points.

`starc.c` (case (0,0), with H^+) and `starg.c` (general, by solving M0 c = rhs) search exhaustively for such a star
with scalars satisfying point 7, for both square classes of c0. If no star exists at one vertex of a ball, the ball
cannot occur.

## Results

Vertex u = 0 of the first component, all 6 relative orders of the layers, both classes c0 = 1, 3.

| case | balls x parameters | runs | stars found | nodes (total / largest run) | log |
|---|---|---|---|---|---|
| (0,0) | 4 x 4 types x 6 orders x 2 | 192 | 0 | 144 714 378 / 1 217 880 | `sweep66.log` |
| (0,1), u in the torsion-free component | 4 x 2 x 6 | 48 | 0 | 79 195 150 / 2 137 326 | `sweep_01u.log` |
| (1,0), u in the torsion component (same balls, other side) | 2 x 4 x 6 | 48 | 0 | 83 525 532 / 2 028 723 | `sweep_10u.log` |
| (1,1) | 2 x 2 x 6 x 6 lambda x 2 | 288 | 0 | 216 096 662 / 1 045 138 | `sweep_11.log` |
| (3,3) | 1 ball x 33 784 128 matrices M, vertices u = 0, 1, 6 | | 0 matrix left | | `theta33_*.out` |

Case (3,3) (`theta33.c`, `theta33b.c`, `theta33c.c`; ball = type 5 + type 5, whose six orders of the layers are
equivalent because every permutation of the layers of type 5 is induced by an automorphism). A purely combinatorial
necessary condition is enough: for a balanced map M, at every ball vertex u there must be ten M-balanced shadows through
u with sum K e_u and pairwise intersections <= 2.
- u = 0: 33 784 128 matrices, 12 236 366 pass the coverage count, **25 588** admit such a family (`theta33_u0_full.out`,
  list in `good_u0.txt`);
- of these, **44** also admit one at u = 1 (`good_after_1.txt`);
- of these, **0** admit one at u = 6 (`theta33_u1_u6.out`).
So no balanced map exists, and case (3,3) is impossible without using the pair conditions mod 7.

## Checks

- Two independent formulations of case (0,0) (`starc.c` with the Green function H^+, `starg.c` by solving the linear
  system) give the same numbers of candidates and of search nodes on the instances compared (11 232 / 910 262 and
  9 936 / 588 998).
- Positive control (`test_plant.py`): a star planted in a true instance (a combinatorial star, a chosen matching and
  scalars, the mod-7 rows of its ten members rewritten to satisfy every condition) is found by `starc.exe`.
- Without the conditions mod 7 the same search finds a star in 221 nodes: the combinatorial conditions alone are
  satisfiable, the obstruction is the conjunction with point 7.
- Counts reproduced from the other sessions' notes: 288 labelled components, 144 with torsion rank 1 and 24 with
  rank 3, 612 admissible triples per component.

## Scope

- Hypotheses used: rank_7(A - 3I) = 37 (the dimension 36 of V), and girth >= 5 for the graph of the line considered.
- Not covered: lines whose graph has a triangle or a 4-cycle; connected lines (generic ones, and those with balanced
  7-torsion). Rank 37 is NOT excluded.
- One vertex per ball is tested; that is enough for the statement.

## Re-run

    python comp66.py                      # the 7 component types -> comp66_types.json
    gcc -O2 -o starc.exe starc.c ; gcc -O2 -o starg.exe starg.c ; gcc -O2 -o theta33b.exe theta33b.c ; gcc -O2 -o theta33c.exe theta33c.c
    python sweep66.py 0 sweep66.log       # case (0,0)
    python sweep_tors.py 01u 12 ; python sweep_tors.py 10u 12 ; python sweep_tors.py 11 12
    python balanced66.py ; python check_model.py ; python test_plant.py ; python small_comp.py
    python gen33.py 0 ; ./theta33b.exe par33_0.txt 0 40353607 good_u0.txt     # case (3,3), u = 0
    python gen33u.py 1 6 ; ./theta33c.exe u33_1.txt good_u0.txt good_after_1.txt ; ./theta33c.exe u33_6.txt good_after_1.txt good_after_6.txt

## Addendum 1 (09/10, 00:53 UTC): three components with two lines per layer ("(4,4,4)")

Statement, same status as above (computer-assisted, not audited): **at rank 37 no line has a graph made of three
triangle-free components with two lines per layer.** All 18 ordered-layer types of such components are used (with or
without 4-cycles of type I); none has 7-torsion, so the radical of the Gram is exactly the two component relations and
every far vertex carries a vector of a non-degenerate plane N0. Test (`fastr.c`, "rank mode"): the 10 x 10 matrix of a star,
Y_ii = -g(i,i), Y_ij = 3 + A_ij - g(i,j), must have rank <= 2 and zero row sums; the search chooses the ten shadows and the
partners and tracks the rank with a pivot block, so both classes of binary forms are covered by one run.
Balls: the 275 multisets of three ordered types up to a simultaneous permutation of the layers; vertex u = 0 of the first
component. Result: 275 of 275 without a star (`sweep_222r2.log`: 257 runs; `sweep_222r.log`: the 18 others, from a first
unreduced run; about 1.6e9 nodes, largest run 1.8e7). Driver `sweep222r2.py`, enumeration `enumc.c` / `multi.py`.

## Addendum 2 (09/10, written 02:55 UTC, completed as the runs end): lines without prism at rank 37

**Target statement B.** Let the 7-rank of A - 3I be 37 and let T be a line no edge of which lies in a prism
(equivalently: G(T) has no triangle and no 4-cycle of type I). Then G(T) is connected.
Status: computer-assisted, NOT audited (only the girth-5 part of the main note was audited, Codex note 224).
It is a local statement about one line; it excludes no rank.

**Fact A (by hand, any rank, no hypothesis on torsion).** If G(T) has components C_i with m_i lines per layer, then
z = m_j 1_{C_i} - m_i 1_{C_j} is an integer eigenvector of A for the eigenvalue 3, and every far vertex has exactly m_i
shadow points in C_i. Proof: (A - 3I) z vanishes on N(T) (C_i, C_j are unions of components of the cubic graph G(T) and
z vanishes on T) and on T (a vertex of T sees 2 m_i points of C_i and 2 m_j of C_j), so (A - 3I) z = e is supported on
the far set with e_f = z(n_f); and |e|^2 = z^T N N^T z = z^T K z with K = 12 I - G - G^2 + 2J - D (D = "same layer"),
G z = 3 z, J z = 0, D z = 0, hence |e|^2 = (12 - 3 - 9) |z|^2 = 0. (The lab and Codex have the general form: a zero-sum
eigenvector of an induced subgraph for the eigenvalue 3 is a global eigenvector; lab NOTE 17.77, Codex note 229.)
So the component relations are true relations at every rank; the dimension count alone only gave half of them.

**Why four profiles only.** A component with one line per layer always has a 4-cycle of type I (its two points of a
layer are mates, and the matching to the next layer closes the cycle), so without prism the numbers of lines per layer
of the components are (6), (3,3), (2,4) or (2,2,2).

**Cases** (each run = exhaustive star search at one near point, "dead" = no star; drivers and logs in this folder):

| profile | case (torsion ranks of the components) | runs | result | log |
|---|---|---|---|---|
| (2,2,2) | all 18 ordered types, 275 multisets up to the order of the layers (no torsion exists) | 275 | all dead | sweep_222r.log, sweep_222r2.log |
| (3,3) | (0,0): 2887 pairs, both classes of the residue | 2887 | all dead | sweep_33r_part0of1.log |
| (3,3) | (0,1): 1910 pairs | 1910 | all dead | sweep_33t_01.log |
| (3,3) | (1,1): 345 pairs x 6 balanced vectors x 2 classes | 4140 | all dead | sweep_33t_11.log |
| (3,3) | (1,2): 15 pairs x 48 balanced vectors | 720 | all dead | sweep_X12.log |
| (3,3) | (2,2): one pair, 2016 isomorphisms x 2 classes | 4032 | all dead | sweep_X22.log |
| (3,3) | (2,3): one pair, 114 912 injective maps, one per orbit of the automorphisms of the ball | 9726 | see below | sweep_X23.log |
| (3,3) | (3,3): one pair (girth 5), 33 784 128 isomorphisms | - | dead (main note, theta33) | theta33_*.out |
| (3,3) | (0,2), (0,3), (1,3) | 0 | impossible: the dimension count forces a balanced torsion vector carried by one component, excluded by lemma I | balanced_all.py |
| (2,4) | large component torsion-free | lab | see below | lab |
| (2,4) | large component of torsion rank 1 | lab | see below | lab |
| (2,4) | large component of torsion rank 2, 3, 4 | laptop | see below | sweep_48tp_T*.log |

**Three reductions found during the night (exact, each with its own check).**
1. *One ball per isomorphism class for (2,4)* (`actc.c`, `reps48.py`, `reps48.txt`). Re-reading the layers of the whole
   ball in another order sends (small type s, large type b) to (g.s, g.b); for a fixed s only the large types up to the
   stabiliser of s matter: 97 896 balls instead of 245 877 (torsion balls: 16 516 instead of 40 761). Checks: every
   image is found in the list, the six maps satisfy the group law, the C table is identical to the Python table of the
   (3,3) sweeps for m = 3, the torsion rank is constant on orbits; the lab rebuilt the files (same hashes) and checked
   400 + 400 random pairs with an independent graph-isomorphism test (all as predicted).
2. *Pair lemma for balanced torsion* (`pairt.c`, `pair48.py`; combinatorial, no rank condition). If B is a space of
   balanced torsion vectors, two near points a, b with K_ab = c > 0 lie together in exactly c shadows, so at least c
   admissible B-balanced 6-sets must contain both. For dim B = 1 this almost never excludes anything; for dim B = 2 it
   removes 95 to 99.6 % of the subspaces, and every subspace of dimension >= 3 on all the balls met. Two independent
   implementations (Python through the candidate lists, C by direct enumeration) give identical lists.
3. *Orbits under the automorphisms of the ball* (`orbits23.py`, `suborb.py`). An automorphism (it preserves each
   component; the layers may be permuted) sends a configuration with B balanced to one with g(B) balanced, so one
   subspace (or one balanced map) per orbit is searched. Checks: the action formula is verified on random maps by
   moving the vectors themselves; the pair test is asserted constant on every orbit in every run.
   `sweep48tp.py` = `sweep48t.py` with 2 and 3 in front; on two balls its verdict and its count of sub-cases agree with
   the unfiltered driver.

**Real conditions alone do not decide** (`realstar.c`, exploration): with only 0 <= 7 Pi <= 7 (valid at every rank) a star
is found at once on the two (2,2,2) balls tried. The exclusions above are properties of rank 37.
