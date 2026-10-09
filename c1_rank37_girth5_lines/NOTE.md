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
