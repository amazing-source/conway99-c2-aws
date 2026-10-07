# The bridge "vector of the envelope -> sigma-odd integer (-4)-eigenfunction" (route (C), 2026-10-07)

> **Referee's corrections merged on 07/10** (`lemma/bridge_REFEREE/REPORT.md`; verdict: no error that breaks the theorem or its
> application): the per-pair certificate required by H4 (section 6, point 13), the false sentence about INVALID removed, the
> status of H5 (now Theorem R of `lemma/upstream/AUDIT_REDUCTION.md`), hypothesis (G) added to Lemma 3, "the converse is not
> available". The status of T20 is the one of `lemma/T20_BOARD.md`, not the word "open" of the first version.


Folder: `SP\bridge` (SP = session scratchpad). Scripts and outputs are listed in section 7. No SAT / CP / ILP / LP solver was used.

## 0. Verdict

**PROVED**, for the statement of section 4 (Bridge Theorem and Corollary T18), with exactly the hypotheses under which the 04/10
filter "norm-3 x with Y = 13" is sound, and no other.

- Root r of U with (r,y1)^2 + (r,y2)^2 = 5  =>  the pair (y1,y2) of U does not host the frame of a srg(99,14,1,2) with an
  involution fixing one vertex. This uses the Bridge Theorem (proved here by hand, five short lemmas) and T18
  (`REPO\lemma\T18_PROOF.md`, taken as given).
- Root r with (r,y1)^2 + (r,y2)^2 = 4: the same Bridge Theorem gives an eigenfunction of squared norm 20. The bridge half is
  proved; the conclusion needs **T20** (state on 07/10: every configuration closed by a first program, second programs and text
  being completed: `lemma/T20_BOARD.md`). These pairs stay pending until T20 is proved and checked.
- The constant is derived, not copied: sum_x phi_v(x)^2 = 2 E(v), E(v) = 7 N(v) - (v,y1)^2 - (v,y2)^2. So Y = 13 at norm 3 gives
  16, Y = 5 at norm 2 gives 18, Y = 4 at norm 2 gives 20.
- The dictionary of `LEMMA_TARGET_2026-10-06.md` sections 1-2 is correct. It agrees with the project's own dossiers of 04/10
  (quotes in section 2). One remark of its section 2 is incomplete (section 6, point 9) and has no consequence.

Three things are NOT covered by this verdict and are listed in section 9: (a) the upstream lemma that every such graph produces a
triple (U, y1, y2) of the campaign, whose sources are not on this machine (it is assumed by every verdict of the campaign, the
04/10 filter included, and the bridge adds nothing to it); (b) T20; (c) one check the quick variant of the deferral rule does not
make and that must be made when the DEFERRED pairs are converted (norms 7 and orthogonality of y1, y2; `certify.py` does it).

## 1. Sources

Read in full:
- `SP\dossiers\DOSSIER_WAGNER_2026-10-04\`: `C2_WAGNER_BORNE_9_SUR_7.txt` (W), `LEMME_EGALITE_8_SUR_7_C2.txt` (EG),
  `C2_PROLONGEMENT_SUPPORT16_PREUVE_CUBE.txt` (CUBE), `LIRE_DOSSIER_WAGNER.txt`, `VERIFIER_PAIRES_011_Y13.py`.
- `SP\dossiers\DOSSIER_COUPES_123_2026-10-04\C2_COUPES_123_PREUVES_2026-10-04.txt` (COUPES).
- `SP\dossiers\C2_REPRISE_CONSTRUCTIVE_2026-10-04\outputs\C2_REPRISE_CONSTRUCTIVE_2026-10-04.txt` (REPRISE).
- Engine: `SP\pkgfull\scripts\frame_dfs_next.py` (header, `setup_lattice`, `lattice_data`, `pair_setup`, `pair_setup_fast`,
  `char_trap`, `min97_witness`, `search`, `joint`, `full_check`), `hstage_stream_next.py`, `golay_pairs_job.py`, `twin_transfer.py`,
  `o24_dfs.py` (header).
- Producer and C1 code: `SP\pkgfull\c1\code\y_pairs.py`, `y2_engine.py`, `y_pairs_gamma.py` (headers and filters);
  `SP\pkgfull\external_runs\c1_96a94fe\code\envelope_trap.py`, `envelope_pack.py`, `h_stage.py`, `frame_pipeline.py`, `u_stage.py`.
- `REPO\q\defer_consumer.py` (whole file), `REPO\q\par_consumer.py` (deferral part), `REPO\LEMMA_TARGET_2026-10-06.md`,
  `REPO\lemma\T18_PROOF.md` (sections 0, 1, 2, 3, 9), `REPO\lemma\t20\T20_REPORT.md` (head).

**Not on this machine** (cited by the sources above as the place where the link graph <-> frame <-> envelope is established):
`MODEL.md`, `TASK.md`, `AUDIT_STATUS.md`, `HANDOVER_2026-10-04.md`, `notes/56_PROMPT_ASTRA_ROUTE_C_28_09.md` section 1.1,
`AUDIT_NORME1_ET_METRIQUES.md`, the C1 notes 139-145 (trap criterion, frame identity at a new root, Lemma Z, Lemma U+),
`work/VERIF_CUBE_OBSTRUCTION_2026-10-04.md`. A search of SP and of `Desktop\Nouveau` found none of them. EG says of its own inputs:
"Elle s'appuie sur le raccord externe entre le graphe et son cadre, notamment le Gram 3I-S et l'identité de cadre serré de
constante 7." In section 4 both facts are re-proved from the definitions, so the bridge does not depend on those missing files.
What does depend on them is stated in section 9, point 1.

Notation clashes between the sources (no mathematical disagreement was found):
- The frame lattice is called L in W and in `min97_witness`, N in the C1 code ("N-perp (dim 2)") and in EG ("min N*"), while N
  is the signed 42 x 42 matrix in REPRISE and in "candidat signé N" (W). In the engine's code `L` is the dictionary of lattice data.
- K is U cap {y1,y2}^perp in `min97_witness`; in W section 8 "K*" is the lattice of the witness route of note 54 (another object);
  in the result records "K" is the number of y-hits.
- E(v) = 7 N(v) - Y(v) is the notation of LEMMA_TARGET. In the engine and in the result records, "E" is E(y) = sum over the
  positive roots alpha of (alpha,y)^2 (`envelope_pack.py`; field "E" of `sample_search`). They are unrelated.
- Sign of C: `h_stage.py` has "(u_o,h_c) = -C_co"; REPRISE has (u_v, h_i) = +R_vi. This is the choice h -> -h and changes nothing.
- W calls U "une enveloppe intégrale de dimension 24"; the engine requires more (unimodular, `setup_lattice`). The bridge only
  uses "integral of rank 24".

## 2. The model, with its sources

**The graph side.** Gamma is a srg(99,14,1,2) with adjacency matrix A, sigma an automorphism of order 2 with exactly one fixed
vertex p.
- COUPES section 1: "On suppose un vrai SRG(99,14,1,2) d'adjacence A : A²+A=12I+2J. sigma fixe seulement p. N(p) est formé des
  sept paires adjacentes intérieures, numérotées 1..7. Les 42 autres orbites sont extérieures, non adjacentes à leur mate. Une
  cellule {i,j} contient deux orbites extérieures, donc quatre sommets : chacun voit un sommet de la paire intérieure i et un de
  la paire j."
- The 49 orbits are the pairs {x, sigma x}, x != p: 7 inner (inside N(p), x ~ sigma x), 42 outer.

**The signed orbit matrix S.** Choose a representative x_i in each orbit O_i, i = 1..49, and put

    S_ij = A(x_i, x_j) - A(x_i, sigma x_j)          (so S_ii = -A(x_i, sigma x_i): -1 on inner orbits, 0 on outer ones).

- EG section 1: "Leur Gram est H=3I-S, où S est la matrice de l'adjacence sur le secteur impair de l'involution."
- EG section 3: "Écrivons S=[-I,C;C^t,T]. Chaque colonne de C a deux valeurs non nulles, dans {+1,-1}."
- COUPES section 7: "Si M est le quotient signé sur les 49 orbites, H=3I-M et Ma=-4a pour le relevé impair de F, donc Ha=7a."
- The sources never write the entry formula. It is forced: "the matrix of the adjacency on the odd sector" in the basis
  e_x - e_{sigma x} is the matrix above (Lemma 1 of section 4), and its diagonal is the -I of EG's block form. Changing a
  representative x_i to sigma x_i changes the sign of row and column i.

**The frame vectors (h, u).** 49 vectors f_i with Gram matrix H = 3I - S: 7 vectors h of norm 4 (inner orbits) and 42 vectors u of
norm 3 (outer orbits), in a space of dimension 22.
- EG section 1: "Les vecteurs du cadre sont f_i : sept h de norme 4 et quarante-deux u de norme 3. [...] On a H²=7H et
  somme_i f_i f_i^t = 7 I sur l'espace physique de dimension 22. Les h sont orthogonaux entre eux ; les produits hors diagonale
  sont dans {0,+1,-1}. Chaque u a exactement deux produits non nuls avec les h, chacun égal à +1 ou -1."
- W header: "L est le réseau engendré par le cadre physique de dimension 22, sept h de norme 4 et quarante-deux u de norme 3.
  Cette assertion porte sur le cadre d'un VRAI graphe, et non sur chaque candidat signé N isolé."
- Engine, `frame_dfs_next.py` header: "h: norm 4, orthogonal to y1 and y2 [...]; u (words): norm 3, orthogonal to y1 and y2.
  V(h, u) = (h, u) is in {0, +-1, +-2}; "Good" means no |V| = 2", and at the end "L7 joint (42 distinct words),
  T^2 + T = 12 I - C^T C, and sum over the 51 frame vectors of x x^T = 7 G^-1". `full_check` builds T = -(Gram of the u, off the
  diagonal) and C from the signs of (u, h), and tests exactly these two identities. `o24_dfs.py` header: "STAR SUMS:
  3 h_c + sum_o C_co u_o = 0". With S = [-I, C; C^T, T] these are the blocks of S^2 + S = 12 I and of the tight-frame identity,
  so the engine's "frame" is a family with Gram 3I - S' for a signed matrix S' of the same shape. Engine and dossiers agree.
- A concrete model (LEMMA_TARGET section 2, checked here): f_O = sqrt(7/2) E_{-4}(e_x - e_{sigma x}), E_{-4} = (27I - 9A + J)/63.
  Write d_O = e_x - e_{sigma x}. Then d_O^T J d_O' = 0, d_O^T d_O' = 2 [O = O'] and, sigma being an automorphism,
  d_O^T A d_O' = 2 (A_xy - A_{x, sigma y}). So (f_O, f_O') = (7/2)(1/63)(27 * 2 [O = O'] - 9 * 2 (A_xy - A_{x, sigma y}))
  = 3 [O = O'] - (A_xy - A_{x, sigma y}), which is 3I - S (on the diagonal: 3 + A_{x, sigma x}).

**U, y1, y2.** U is one of the 156 odd unimodular lattices of rank 24 with no vector of norm 1; y1, y2 are two orthogonal vectors
of U of norm 7 ("les normales"); the frame of a solution lies in U and is orthogonal to both.
- `envelope_trap.py` header: "U = odd unimodular, dim 24, min >= 2, given by generators (rational vectors in R^24)".
  `setup_lattice` asserts 24 basis vectors, an integral Gram matrix and |det| = 1; `lattice_data` asserts that there is no norm-1
  vector. `pair_setup` asserts (y,y) = 7 for both and (y1,y2) = 0.
- W section 9: "U est une enveloppe intégrale de dimension 24, y1,y2 sont orthogonaux de norme 7. Les vecteurs du cadre d'une
  solution appartiendraient à U et à l'orthogonal des deux normales."
- EG section 6: "Les h et u appartiennent à U et sont orthogonaux aux normales. L'intégralité de U implique (v,h),(v,u) entiers ;
  v est donc dans le dual du réseau du cadre."
- `frame_pipeline.py` header: "y in H-perp (y is orthogonal to N, which contains the h), |y|^2 = 7".
- The 51 vectors (7 h, 42 u, y1, y2) satisfy sum x x^T = 7 on U (x) R: the 49 frame vectors give 7 on {y1,y2}^perp (Lemma 3
  below) and y1 y1^T + y2 y2^T is 7 on span(y1,y2) because (y_j,y_j) = 7. This is the engine's identity "(F)".
- **Silent point.** No file on this machine says how U is obtained from the graph, nor proves that the 156 lattices and the
  pair lists are complete. The sources only state the result: the frame of a solution lies in U cap {y1,y2}^perp. (The
  "Lemma U" / "U+" of the engine, switch FD_LEMMA_U, is something else: a pruning rule on the words u at the new roots, C1
  notes/145. It plays no role in the bridge.)

**L, K, L*.** L = Z-span of the 49 frame vectors (rank 22, integral, 7 L* inside L: REPRISE section 2, "Leur Gram est entière,
donc 7L* est contenu dans L et det L est une puissance de 7"). K = U cap {y1,y2}^perp contains L, so K* is inside L*.
- `min97_witness` docstring: "min L* >= 9/7 for the frame lattice L of a real graph [...]. L lies in K = U cap {y1,y2}^perp, so
  K* = pi(U) is in L*. A norm-3 x of U with (x,y1)^2 + (x,y2)^2 = 13 projects to a vector of norm 3 - 13/7 = 8/7: the pair is
  impossible."
- K* = pi(U) holds because U is unimodular and Z y1 + Z y2 is primitive in U (a rank-2 overlattice of index 7 would be
  unimodular, hence Z^2, and U has no norm-1 vector). Checked on data: det K = 49 on 13 pairs of lattice 011 (section 7).
- E(v)/7 = (pi(v), pi(v)) for v in U: this is the norm of the vector pi(v) of K*, hence of L*.

**Definition used below.** "The pair (y1, y2) of U comes from a 99-graph" means: there are Gamma, sigma as above, representatives
x_i, and vectors f_1, ..., f_49 of U, all orthogonal to y1 and y2, with (f_i, f_j) = 3 delta_ij - S_ij. This is the hypothesis
under which W section 9 and EG section 6 prove the 04/10 filter (the three sentences quoted above), and nothing more.

## 3. The 04/10 filter and its proof, as the sources give it

**Statement (W section 9; `min97_witness`).** If the pair (y1,y2) of U comes from a 99-graph, U has no vector x of norm 3 with
(x,y1)^2 + (x,y2)^2 = 13.

**Proof, in the order of the sources, each step checked.**

F1 (W section 9, EG section 6). Put a = (x,y1), b = (x,y2), v = x - (a y1 + b y2)/7. Then
(v,v) = 3 - 2(a^2+b^2)/7 + (7a^2 + 7b^2)/49 = 3 - 13/7 = 8/7, and v is orthogonal to y1, y2. *Checked* (uses (y_j,y_j) = 7, (y1,y2) = 0).

F2. For every frame vector f_i: (v, f_i) = (x, f_i) because f_i is orthogonal to y1, y2; it is an integer because x and f_i are
in U and U is integral. So v is in L*. *Checked.* Note that x does not have to be in L or in K.

F3 (W section 8; EG section 2). "Pour v dans L*, les coefficients a_i=(v,f_i) sont entiers et somme a_i²=7v²", "Ha=7a, Sa=-4a".
*Checked*: this is Lemma 3 of section 4 (tight frame of constant 7 on the 22-dimensional space, which needs H^2 = 7H and
rank H = 22, i.e. Lemmas 1-2). Here sum a_i^2 = 8.

F4 (EG section 2). No |a_i| >= 2: if |a_i| = 2 the other coefficients have sum of squares 4, hence sum of absolute values <= 4,
while row i of Ha = 7a needs |sum_{j != i} H_ij a_j| = (7 - H_ii)|a_i| = 6 (an h) or 8 (a u) with |H_ij| <= 1. So a is in
{0,+1,-1}^49 with exactly eight non-zero entries. *Checked.*

F5 (EG section 2). "Son relevé au graphe vaut a_i sur un représentant, -a_i sur son mate, et 0 au sommet fixe. Il vérifie Af=-4f."
*Checked*: Lemma 1 of section 4, including the equation at the fixed vertex. So f is an integer sigma-odd (-4)-eigenfunction with
eight +1 and eight -1: squared norm 16.

F6 (the graph lemma of 04/10, "H16": no such f). Structure of the sources' proof and what was checked here:
- EG section 3, number k of active h is 0 or 2: C a_u = -3 a_h, column sums of C even, 3k <= 2(8-k). *Checked line by line.*
- EG section 4, P = {f = 1} is independent (D = m(m-7) - 7e - sum d_i^2 >= 0 with m = 8). *Checked line by line* (the sum
  sum_i [C(d_i,2) + C(d_i+4,2)] = sum d_i^2 + 6e + 6m was recomputed).
- EG section 5, k = 2 impossible (the 8 x 8 matrix B with two diagonal entries). *Checked line by line*, both cases.
- CUBE section 8, the complement of B is cubic and triangle-free on 8 vertices ((B^2)_ij = 2 C_ij + (C^2)_ij was recomputed
  from B = J - I - C), hence the cube or the Wagner graph. *Checked.*
- CUBE sections 2-6, the cube is impossible (|X0| = 11, |X1| = 64, |X2| = 8; b + 2a = 16 - 5d; the 4-cycle of deficient pairs;
  "at least 10, at most 8"). *Checked line by line.* CUBE section 7 (t = 1 and the two profiles A, B, used by W). *Checked.*
- W sections 3-6, the Wagner graph is impossible: structural part read (W section 2 re-derived: t = 1, a_p = 2, the budget 8
  and the two profiles), finite part computed by the dossier's enumerators. *Re-run here in a copy*
  (`SP\bridge\wagner_rerun\`): same counts and same records as the dossier, verifier passes (section 7). The enumerators'
  code was not audited line by line.
F6 is not needed by the bridge; it is the lemma that plays for E = 8 the role T18 plays for E = 9.

F7. Contradiction with F5-F6: the pair does not come from a 99-graph. QED

Two remarks on the sources.
- W concludes with "contrairement à la borne 9/7". The bound min L* >= 9/7 also needs the older bound min L* >= 8/7, which W
  calls an external input ("ENTRÉE EXTERNE : la borne min L*>=8/7 est celle du dossier"). The filter does not need it: v has norm
  exactly 8/7 and only "no vector of L* of norm exactly 8/7" (F3-F6) is used.
- The filter is a statement about the frame of a REAL graph (W header, EG "Portée"). It does not say that the pair admits no
  frame in the engine's sense. See section 6, point 7.

## 4. The bridge theorem

**Setting.**
(G) Gamma is a srg(99,14,1,2) with adjacency matrix A; sigma is an automorphism of Gamma with sigma^2 = 1 and exactly one fixed
    vertex p; O_1..O_49 are the orbits of size 2, x_i a representative of O_i; S is the matrix of section 2.
(U) U is a lattice of rank 24: a free Z-module of rank 24 with a positive definite symmetric bilinear form with integer values.
    y1, y2 are in U with (y1,y1) = (y2,y2) = 7 and (y1,y2) = 0.
(F) f_1, ..., f_49 are in U, (f_i, y_1) = (f_i, y_2) = 0 for all i, and (f_i, f_j) = 3 delta_ij - S_ij.

For v in U put N(v) = (v,v), Y(v) = (v,y1)^2 + (v,y2)^2, E(v) = 7 N(v) - Y(v), a_i(v) = (v, f_i), and let phi_v be the function
on the 99 vertices with phi_v(x_i) = a_i(v), phi_v(sigma x_i) = -a_i(v), phi_v(p) = 0.

**Bridge Theorem.** Under (G), (U), (F), for every v in U:
1. phi_v takes integer values and phi_v(sigma x) = -phi_v(x) for every vertex x;
2. A phi_v = -4 phi_v (at every vertex, p included);
3. sum over the 99 vertices of phi_v(x)^2 = 2 E(v), and E(v) = sum_i a_i(v)^2 = 7 (pi(v), pi(v)), where pi is the orthogonal
   projection onto {y1,y2}^perp;
4. phi_v = 0 if and only if E(v) = 0, if and only if v is in the plane R y1 + R y2.

**Corollary T18.** Under (G), (U), (F), U has no vector v with E(v) = 9. In particular U has no root r ((r,r) = 2) with
(r,y1)^2 + (r,y2)^2 = 5. Conversely every v in U with E(v) = 9 is r + m y1 + n y2 with r such a root and m, n integers, so the
roots with Y = 5 detect every vector with E = 9. (Uses T18.)

**Corollary T20 (conditional on T20; its state is in `lemma/T20_BOARD.md`).** Under (G), (U), (F), U has no v with E(v) = 10; in particular no root with
(r,y1)^2 + (r,y2)^2 = 4 and no vector of norm 4 with |(v,y1)| = |(v,y2)| = 3; and every v with E(v) = 10 is one of these two
kinds up to Z y1 + Z y2.

**Corollary Y1 (fixed normal; Codex, 07/10; conditional on T18 and T20; text and first certificate: `lemma/t20_CODEX/FIXED_Y1_003.md`).**
Under (G), (U), (F), every root r of U has |(r,y1)| <= 1 and |(r,y2)| <= 1.
*Proof.* a = (r,y1) and b = (r,y2) are integers and E(r) = 14 - a^2 - b^2. A root is not in Z y1 + Z y2 (minimum 7), so
E(r) >= 8 ((R-vi) of `upstream/AUDIT_REDUCTION.md`): a^2 + b^2 <= 6. If |a| = 2 then b^2 <= 2 and E(r) = 10 - b^2 is 9 (b = +-1)
or 10 (b = 0): excluded by Corollary T18, resp. Corollary T20. The same with a and b exchanged. QED
This is the root-witness rule read at the level of ONE normal: if U has a root r with (r,y1) = +-2, then no frame of U has this
y1, **whatever y2**. The statement is invariant under Aut(U) and under the sign of y1. So a chunk of the sweep that consists of
the pairs of one y1 representative with such a root is covered without producing its y2: neither the completeness of the y2
enumeration, nor the swap rule, nor any search is used for it. Certificate per representative: `q/cert_y1.py` (y1 of the plan in
ambient coordinates, in U, of norm 7; r in U of norm 2; (r,y1) = +-2; hashes of the plan and of its basis), checked by the
standalone `q/check_cert_y1.py`. Used for 003:181:182, the only y1 representative of the campaign without a record (96 of the
182 representatives of 003 have such a root; the 95 others are covered by their own records and do not use it).

**Corollary H16 (the 04/10 filter).** Same with E(v) = 8: no vector of norm 3 with Y = 13; every v with E(v) = 8 is of this kind
up to Z y1 + Z y2.

### Proof

**Lemma 0 (T18_PROOF Lemma 2.1(a), re-proved).** For x != p: x ~ sigma x if and only if x ~ p. Hence exactly 14 vertices are
adjacent to their mate.
*Proof.* C = N(x) cap N(sigma x) is sigma-invariant. If x ~ sigma x then |C| = 1 (lambda = 1), so C is a fixed vertex: C = {p}
and x ~ p. If x ~ p then sigma x ~ p, so p is in C; if x were not adjacent to sigma x, |C| = 2 (mu = 2), C = {p, c}, and c
would be a second fixed vertex. QED

**Lemma 1 (S is A on the odd functions).** For a in R^49 let lift(a) be the function with values a_i on x_i, -a_i on sigma x_i,
0 on p. Then lift is a linear bijection from R^49 onto the space Odd of functions with phi o sigma = -phi,
sum_x lift(a)(x)^2 = 2 sum_i a_i^2, and

    A lift(a) = lift(S a).

S is symmetric, S^2 + S = 12 I, and its eigenvalues are -4 with multiplicity 22 and 3 with multiplicity 27.
*Proof.* An odd function vanishes at p (phi(p) = -phi(p)) and is determined by its values on the x_i: lift is a bijection, and
the norm identity is clear. Let phi = lift(a).
- At x_i: (A phi)(x_i) = A(x_i,p) * 0 + sum_j [A(x_i,x_j) - A(x_i,sigma x_j)] a_j = (S a)_i. The term j = i is
  [A(x_i,x_i) - A(x_i,sigma x_i)] a_i = S_ii a_i: the mate of an inner vertex is a neighbour and contributes -a_i.
- At sigma x_i: A(sigma x_i, y) = A(x_i, sigma y), so (A phi)(sigma x_i) = sum_z A(x_i,z) phi(sigma z) = -(A phi)(x_i).
- At p: A(p, sigma x_j) = A(sigma p, x_j) = A(p, x_j), so (A phi)(p) = sum_j [A(p,x_j) - A(p,sigma x_j)] a_j = 0.
So A phi = lift(S a). Symmetry: S_ji = A(x_j,x_i) - A(x_j,sigma x_i) = A(x_i,x_j) - A(sigma x_j, x_i) = S_ij.
An odd function has sum zero (the values on each orbit cancel), so Odd is orthogonal to the constants and lies in V_3 + V_{-4},
where (A - 3)(A + 4) = 0 (from A^2 = 12 I - A + 2J). Hence (S - 3)(S + 4) = 0, i.e. S^2 + S = 12 I.
Multiplicities: let P be the permutation matrix of sigma. trace P = 1 and trace(PA) = #{x : x ~ sigma x} = 14 (Lemma 0). P
commutes with A and fixes the constant vector. With t_3, t_4 the traces of P on V_3 (dimension 54) and V_{-4} (dimension 44):
1 + t_3 + t_4 = 1 and 14 + 3 t_3 - 4 t_4 = 14, so t_3 = t_4 = 0. P is an involution, so its (-1)-eigenspace in V_{-4} has
dimension (44 - 0)/2 = 22 and in V_3 dimension 27 (total 49). QED

**Lemma 2.** H = 3I - S is symmetric with integer entries, H^2 = 7H, H is positive semidefinite of rank 22, its (7)-eigenspace is
ker(S + 4I). H_ii = 4 on the 7 inner orbits and 3 on the 42 outer ones.
*Proof.* H has eigenvalues 3 - (-4) = 7 (22 times) and 3 - 3 = 0 (27 times). H_ii = 3 + A(x_i, sigma x_i) and Lemma 0. QED

**Lemma 3 (tight frame).** Under (G), (U), (F), let W = {y1,y2}^perp in U (x) R (dimension 22). Then the f_i span W, and for every
w in W, with a = ((w, f_i))_i:   sum_i (w,f_i)^2 = 7 (w,w)   and   S a = -4 a.
*Proof.* The f_i lie in W and their Gram matrix H has rank 22 = dim W, so they span W. Let T(w) = sum_i (w,f_i) f_i on W. For
all j, k: (T f_j, f_k) = sum_i H_ji H_ik = (H^2)_jk = 7 H_jk = (7 f_j, f_k). The f_k span W, so T f_j = 7 f_j; the f_j span W, so
T = 7 on W. Then sum_i (w,f_i)^2 = (T w, w) = 7 (w,w), and (H a)_j = sum_i H_ji (w,f_i) = (w, T f_j) = 7 a_j, i.e. S a = -4 a. QED

**Lemma 4 (projection).** For v in U, w = pi(v) = v - ((v,y1) y1 + (v,y2) y2)/7 is in W, (w,w) = N(v) - Y(v)/7 = E(v)/7, and
(v, f_i) = (w, f_i) for all i.
*Proof.* (y_j,y_j) = 7, (y1,y2) = 0, (f_i,y_j) = 0. QED

*Proof of the theorem.* Let v be in U, a = a(v). By Lemma 4, a_i = (pi(v), f_i); a_i is an integer because v and f_i are in U
and the form is integral: this is (1), together with the definition of phi_v = lift(a). By Lemma 3 applied to w = pi(v),
S a = -4 a and sum a_i^2 = 7 (pi(v),pi(v)) = E(v). By Lemma 1, A phi_v = lift(S a) = -4 phi_v: this is (2); and
sum_x phi_v(x)^2 = 2 sum a_i^2 = 2 E(v): this is (3). For (4): phi_v = 0 iff a = 0 iff pi(v) is orthogonal to all f_i iff
pi(v) = 0 (the f_i span W) iff E(v) = 0. QED

*Proof of the corollaries.* If E(v) = 9, phi_v is an integer sigma-odd function with A phi_v = -4 phi_v and squared norm 18:
impossible by T18 (stated for arbitrary integer values, `T18_PROOF.md` section 1.3 and Proposition 3.1). A root with Y = 5 has
E = 14 - 5 = 9. Same for E = 10 and T20 (Y = 4 at norm 2: 14 - 4; (3,3) at norm 4: 28 - 18), and for E = 8 and H16 (Y = 13 at
norm 3: 21 - 13).
Which vectors have a given E (**coset reduction**): E(v) depends only on v modulo Z y1 + Z y2, and adding m y1 + n y2 adds
(7m, 7n) to ((v,y1),(v,y2)). So every class contains a v_0 with |(v_0,y1)| <= 3 and |(v_0,y2)| <= 3, and
N(v_0) = (E + (v_0,y1)^2 + (v_0,y2)^2)/7 is an integer. The possible values of a^2 + b^2 with |a|, |b| <= 3 are
0, 1, 2, 4, 5, 8, 9, 10, 13, 18. Hence:

| E | a^2 + b^2 = -E mod 7 | reduced representative (norm; {abs(a), abs(b)}) |
|---|---|---|
| 8 | 13 | norm 3, {2,3} |
| 9 | 5 | norm 2, {1,2} |
| 10 | 4 or 18 | norm 2, {0,2}; or norm 4, {3,3} |
| 11 | 10 | norm 3, {1,3} |
| 12 | 2 or 9 | norm 2, {1,1}; or norm 3, {0,3} |
| 13 | 1 or 8 | norm 2, {0,1}; or norm 3, {2,2} |
| 14 | 0 | norm 2, {0,0} (a root orthogonal to y1, y2) |

For E = 1..7 the same computation gives representatives of norm at most 3 (this is the producer's remark in `y_pairs.py`: "a
short dual vector lifts to v in U with |v|^2 < 26/7"); the producer's root and norm-3 filters remove them. QED

### What the proof uses and what it does not

- **Used on the lattice side:** U integral of rank 24 (positive definite); y1, y2 in U of norm 7 and orthogonal; the f_i in U,
  orthogonal to y1 and y2, with Gram 3I - S. Rank 24 is used once and is essential: it gives W = span(f_i). If the frame did not
  span {y1,y2}^perp one would only get sum a_i^2 <= E(v), and E(v) = 9 would exclude nothing.
- **Used on the graph side:** A^2 = 12 I - A + 2J, sigma an involutive automorphism with exactly one fixed vertex. Nothing else.
- **Not used:** U unimodular, U odd, min U >= 2, that r is a root, that the pair passed any other filter (characteristic trap,
  twin transfer, 9/7, pair set-up, the producer's filters), that the engine did not decide the pair, the bound min L* >= 8/7,
  the 04/10 lemma, that the values of phi_v are in {0, +1, -1}.
- **It is an eigenfunction, not a projection of one:** a(v) lies in the image of w -> ((w,f_i))_i, which is exactly ker(S + 4I).
- **Remark (not needed).** w -> ((w,f_i))_i is a bijection from L* onto the integer vectors of ker(S + 4I), with
  sum a_i^2 = 7 (w,w) (inverse: a -> sum a_i f_i / 7). So "min L* >= m/7" is equivalent to "every non-zero integer sigma-odd
  (-4)-eigenfunction has squared norm >= 2m": the boxed equivalence of LEMMA_TARGET section 2 is correct.

## 5. Every hypothesis, and where it is guaranteed

| # | Hypothesis | Where it is guaranteed |
|---|---|---|
| H1 | Gamma is a srg(99,14,1,2); sigma is an automorphism of order 2 with exactly one fixed vertex | Case "C2" of the project; the same hypotheses as T18 (`T18_PROOF.md` sections 1.1-1.2) and as the dossiers of 04/10 |
| H2 | U is an integral positive definite lattice of rank 24 | `setup_lattice`: `len(B) == 24`, Gram integral, abs(det) = 1, asserted for every lattice loaded; the basis is a basis of a lattice of Q^24 with a positive scale, and `ldl` takes a Cholesky factor of G |
| H3 | y1, y2 are vectors of U | exact membership test in `hstage_stream_next.py` (else INVALID) and in `golay_pairs_job.py` (`conv`) |
| H4 | (y1,y1) = (y2,y2) = 7, (y1,y2) = 0 | By construction in the producer (`y_pairs.py`, `y2_engine.py`). Asserted by the engine in `pair_setup` / `pair_setup_fast`. **Not asserted for a pair deferred by the quick variant** (`Q_DEFER_NODES=0`) of `defer_consumer.py`, which returns DEFERRED before the engine's `search` and so before `pair_setup`. To be re-checked at conversion (`SP\bridge\certify.py`) |
| H5 | The pair "comes from a 99-graph": 49 vectors of U orthogonal to y1, y2 with Gram 3I - S | This is not a property the engine checks; it is the definition of what an exclusion means. Sources: W section 9, EG section 6, `min97_witness`, `frame_pipeline.py`. Same hypothesis as the 04/10 filter |
| H6 | The witness: r in U, (r,r) = 2, (r,y1)^2 + (r,y2)^2 = 5 | `defer_consumer.witness`: exact int64 products R G y; the rows of R have norm 2 by the exact selection of `lattice_data`. One witness suffices; completeness of R is not needed |
| H7 | T18 for arbitrary integer values | `REPO\lemma\T18_PROOF.md`, Theorem 9.1 with Proposition 3.1 (hand statements plus six finite computations; its own caveats are in its section 9.3). Taken as given here |
| H8 (T20 pairs only) | T20 | **Open** (`REPO\lemma\t20\T20_REPORT.md`: nine configurations left after round 1) |

## 6. Adversarial section

1. **The fixed vertex.** The orbit vector a says nothing at p. The lift sets phi(p) = 0, which is forced by oddness, and the
   eigen-equation at p holds because N(p) is a union of orbits on which phi sums to zero (Lemma 1). At an inner vertex the mate
   is a neighbour: this is the diagonal -1 of S, without which the equation fails. Checked numerically at every vertex on two
   real graphs (section 7).
2. **Eigenvalue 3 instead of -4.** The complementary matrix 4I + S is also 7 times a projector (onto the odd part of V_3), with
   norms 3 on the 7 inner orbits and 4 on the 42 outer ones and rank 27. The engine's frame has 7 vectors of norm 4, 42 of norm
   3, in dimension 22 = 24 - 2: only 3I - S fits. On the srg(243,22,1,2): frame Gram 4I - S has norms (5, 4) and rank 55,
   the complement has norms (4, 5) and rank 66 (section 7).
3. **The even sector.** V_{-4} also has a 22-dimensional sigma-even part. Its frame is not integral (norms 29/9 - A_{x,sx} in
   the same normalisation), so it cannot be the engine's frame.
4. **Proper sublattice, integrality.** phi_v is integral because v and the f_i are in the integral lattice U. v does not have
   to be in L, in K or in the Z-span of anything; L may be a proper sublattice of K. What a proper sublattice costs is the
   converse (an integer eigenfunction need not come from a vector of U), which is not used.
5. **Signs and oddness.** (F) is stated for a choice of representatives. Replacing x_i by sigma x_i changes the sign of row and
   column i of S, so the realisation becomes (sigma x_i, -f_i), a_i becomes -a_i, and phi_v is the same function. The numerical
   check uses random representatives. The frame is built on e_x - e_{sigma x}, so the lift is odd by construction; the even
   lift is not an eigenfunction (negative control of section 7).
6. **The factor between E and the squared norm.** sum_i a_i^2 = E(v) exactly (tight frame of constant 7 and (w,w) = E/7); the
   lift doubles it. For norm 3, Y = 13 this gives 16 = 8 + 8, which is the "huit sommets +1, huit sommets -1" of W. For the
   root with Y = 5: 18 = 9 + 9. T20_REPORT section 0 records that a task text once said 32 / 36 / 40; those are wrong by a
   factor 2, and T18_PROOF and T20_REPORT treat the right values 18 and 20.
7. **"Comes from a 99-graph" versus "admits a frame in the engine's sense".** Graph => engine frame: the f_i of a graph satisfy
   the identity (F), from which the engine's conditions are derived according to its header (C1 notes 140-145, not on this
   machine; not needed by the bridge). The converse is not available: an engine frame is a
   signed matrix S' with S'^2 + S' = 12 I and the right shape, and a graph needs in addition the even sector (the matrix D of
   the model, "Q = |N| + 2D" in REPRISE; "T4 reste le lemme de travail du dossier pour reconstruire ce graphe depuis une
   solution (N,D)", EG). T18 uses lambda = 1 and mu = 2 of the real graph. So the bridge proves "no GRAPH frame in this pair",
   not "no engine frame in this pair". The campaign needs exactly the first: it argues "a graph would give a pair (U, y1, y2)
   hosting its frame; no pair does". Verdicts obtained by the 04/10 filter are already of this kind (W: "paire impossible pour
   EX"), and so is every lattice status that used a twin transfer from them. A T18 exclusion must keep its own verdict text and
   must not be reported as a completed search.
8. **Rank.** See section 4: the equality sum a_i^2 = E(v) needs span(f_i) = {y1,y2}^perp, which holds because 22 + 2 = 24.
9. **Values +-2.** LEMMA_TARGET section 2 says that for a root r all |(u,r)| <= 1 "so the 0/+-1-valued cases of T18 and T20
   already remove the pairs". For a word u this is right (norm of u - r would be 1). For an h it is not: (h,r) = +-2 is
   possible (h - r is then a root). This has no consequence: T18 is proved for arbitrary integers (Proposition 3.1: nine values
   +-1 is the only pattern of squared norm 18), and T20_REPORT treats the pattern "one inner orbit at +-2 and six outer".
10. **Does the rule miss or over-reach?** By the coset reduction, the roots with Y = 5 detect exactly the vectors with E = 9:
    no vector of norm 3 or 4 has E = 9 (Y would be 12 or 19, not sums of two squares), and a vector of norm 5 with E = 9 is
    r +- y_j. The rule does not over-reach: it fires only on an exact root with Y = 5 (label T18) or, failing that, Y = 4
    (label T20). It under-reaches for T20 only: a pair whose vectors with E = 10 are all of norm 4 with (3,3) is searched and
    not deferred (LEMMA_TARGET section 1: 180 pairs of 016). That is harmless.
11. **Symmetry reductions.** The property "U has a root with Y = 5" is invariant under Aut(U), signs and the swap of y1, y2, so
    it is compatible with the producer's reductions. The twin envelope "holds the same frame" (`twin_transfer.py`), so the
    bridge may be applied in U or in its twin.
12. **Is the pair's being undecided by the engine needed?** No. The theorem holds for every pair with such a root, also for
    pairs the engine excludes otherwise (on the 400 pairs of 011, 279 have a root with Y = 5, most of them also a Y = 13
    witness).
13. **The missing norm check.** See H4. With (y,y) different from 7 or (y1,y2) different from 0 the formula for E is false and the theorem does
    not apply; the engine's `pair_setup` asserts the norms, but its immediate tests and the consumer's filters come before it, and
    the quick deferral path answers DEFERRED without it: the norm guarantee of the campaign rests on the producer. So the
    conversion of a DEFERRED pair into an exclusion requires a per-pair certificate in ambient coordinates (y1, y2, r in U;
    (y,y) = 7; (y1,y2) = 0; (r,r) = 2; (r,y1)^2 + (r,y2)^2 = 5): `lemma/bridge/certify.py`.

I found no way to break the theorem. The only links that are not proved in this folder are outside it: H5 as a statement about
all graphs (section 9, point 1; proved since then: Theorem R of `lemma/upstream/AUDIT_REDUCTION.md`, whose item (R-vii) is this
Bridge Theorem), T18 itself, and T20. H5 for a given pair is the hypothesis being refuted, not an assumption.

## 7. Numerical checks

All exact integer / rational arithmetic. Python: `SP\pkgfull\.venv\Scripts\python.exe`.

**`graph_check.py` -> `graph_check.out.txt`, `graph_check.out.json`.** Two real graphs with lambda = 1, mu = 2 and an involution
with one fixed vertex: Paley(9) = srg(9,4,1,2) and the srg(243,22,1,2) of Berlekamp, van Lint and Seidel (cosets of the ternary
Golay code), both with x -> -x. General parameters: c = r - s = sqrt(4k - 7); frame Gram r I - S; E(v) = c N(v) - Y(v).
- Checked: A^2 = (k-2) I - A + 2J; sigma is an automorphism with one fixed vertex; trace(P_sigma A) = k; S symmetric,
  S^2 + S = (k-2) I; H = r I - S, H^2 = c H, rank H = trace(H)/c = half of the multiplicity of s (Paley: 2 of 4; BvLS: 55 of
  110); norms r + 1 on the k/2 inner orbits and r on the others; the h pairwise orthogonal; every u meets exactly two h; one
  "Same" and one "Opp" cell per pair of h.
- An integral lattice U' = span(f_i) + Z y1 + Z y2 + Z g was built from the Gram matrix only, with (y_j,y_j) = c and a glue
  vector g that has a component on the normals (BvLS: N(g) = 28, (g,y2) = 3). For 300 random v in U' per graph (191 of them
  with a glue component for BvLS): a_i = (v,f_i) are integers, sum a_i^2 = E(v), A phi_v = s phi_v at every vertex including
  the fixed one, sum phi_v^2 = 2 E(v). All hold (BvLS: 296 vectors with E > 0, 168 distinct values of E).
- Negative controls: the even lift (a_i on both vertices of an orbit) fails to be an s-eigenfunction in 296 of 296 cases; the
  complementary Gram S - s I has the other norm pattern (inner 4, outer 5, rank 66 for BvLS).
- Limits: these are not the 99-graph, and U' is not a unimodular envelope. The check validates the dictionary (definition of S,
  diagonal, fixed vertex, constant, eigenvalue), which is the part that could have been wrong.

**`engine_check.py` -> `engine_check.out.txt`, `engine_check.out.json`.** The package's own `lattice_data`, `min97_witness`, and the
deferral rule's own `witness()` (imported from `REPO\q\defer_consumer.py`), on lattice 011 and the 400 historical pairs of the
dossier (`SOURCE_011_SAMPLE_PAIRS.json`). Nothing written outside `SP\bridge` (numba cache redirected, no .pyc).
- `lattice_data`: G equals the Gram matrix of B recomputed in rationals; det G = 1 (Bareiss); R, X3, X4 have norms 2, 3, 4
  exactly; 56 roots, 4096 vectors of norm 3, 96,912 of norm 4, 52 new-root pairs.
- R, X3, X4 are integer coefficient vectors, one per +- pair, so they are vectors of U. S2 is different: its rows are 2 beta
  with (2 beta, 2 beta) = 8 and 2 beta congruent to a characteristic vector modulo 2U, so beta is a norm-2 vector of the shadow
  ("new root"), not a vector of U. The deferral rule reads R only; the bridge never uses S2.
- Y: `min97_witness` and `defer_consumer.witness` both compute (X G y1)^2 + (X G y2)^2 with X the coefficient rows and y1, y2
  the coefficient vectors, i.e. (x,y1)^2 + (x,y2)^2 in the form of U.
- The 400 pairs: y1, y2 in U exactly, norms 7, orthogonal.
- E(v) = 7 (pi(v),pi(v)) in exact rationals in ambient coordinates, and 7 pi(v) is a vector of U orthogonal to y1, y2 (312 vectors).
- det(U cap {y1,y2}^perp) = 49 on the 13 pairs sampled, so pi(U) = K*.
- Over all vectors of norm <= 4 and all 400 pairs: E in 1..7 never occurs (the producer's trap); E = 8 only as (norm, Y) = (3,13)
  or (4,20); E = 9 only as (2,5); E = 10 only as (2,4) or (4,18). Counts of classes with E <= 12 are in the json.
- Coset structure at norm 5 (1,130,496 vectors) on 5 pairs: #{norm 5, E = 9} = #{roots, Y = 5}, each such vector is r +- y_j
  explicitly; #{norm 5, E = 10} = #{roots, Y = 4} + 2 #{norm 4, Y = 18}; #{norm 4, Y = 20} = #{norm 3, Y = 13}.
- `min97_witness` fires on 363 pairs, the same 363 as the dossier's independent witness file. On the 37 others: Emin = 9 for 19
  (a root with Y = 5: the rule answers DEFERRED T18) and Emin = 10 for 18 (root with Y = 4: DEFERRED T20; 9 of them also have a
  norm-4 vector with (3,3)). All 37 had been searched to the end historically and were EXCLUDED (stage 1 empty), with
  19,700,287 and 14,394,651 nodes: consistent with the theorem, and not a proof of anything.

**`certify.py` -> `certify.out.txt`.** The exact certificate of section 8, self-tested on the same 400 pairs (T18: 279, T20: 113,
none: 8) and on an invalid pair (rejected).

**`wagner_rerun\`.** Copies of the dossier's scripts, run here (the originals are untouched):
- `ENUMERER_WAGNER_PROFIL_B.py`: completed, 105 matchings, 31 admissible, 76 marked, 16 matrices C, 32 partial graphs, 32
  certificates: the numbers of W section 4.
- `VERIFIER_PAIRES_011_Y13.py`: completed, 363 witnesses verified.
- `ENUMERER_WAGNER_PROFIL_A.py`: the first run was stopped by the script's own 180 s cap (the laptop was throttled about 15
  times that night: the verifier, 6 s in the dossier, took 90 s). A copy with the cap raised to 1800 s and nothing else changed
  (`ENUMERER_WAGNER_PROFIL_A_cap1800.py`) completed in 1229 s: 105 matchings, 31 admissible, 76 marked, 48 matrices C, 640
  partial graphs, 400 closed by e + f >= 2, 240 neighbourhood checks, 0 four-cliques: the numbers of W sections 4 and 6.
- The two regenerated certificate files have the same `counts` and the same `records` as the dossier's files; the only
  differences are the timing and two provenance fields added in the dossier (`compare_A.txt`, `compare_B.txt`).
- `VERIFIER_WAGNER_CERTIFICATS.py` on the regenerated files, and separately on the dossier's files (`wagner_verify_shipped\`):
  240 obstructions of profile A and 32 of profile B verified, 6,544 candidate orbits recomputed.
So the computed part of the 04/10 lemma is reproduced on this machine with the dossier's own programs. This is a re-run, not
an independent implementation, and the bridge does not depend on it.

## 8. What this means for the DEFERRED pairs

- A pair recorded "DEFERRED (pending T18: root r with (r,y1)^2+(r,y2)^2 = 5)" may be counted as excluded, in the sense "does
  not host the frame of a real graph", on the strength of the Bridge Theorem and T18, **provided H4 is checked for it**. The
  budget variant of the rule (Q_DEFER_NODES > 0) has already made that check (the engine's `pair_setup` ran); the quick variant
  (Q_DEFER_NODES = 0, used since 07/10) has not.
- Recommended conversion, one exact certificate per pair: recompute from the record (y1, y2 are kept in `not_excluded`) that
  y1, y2 are in U, (y1,y1) = (y2,y2) = 7, (y1,y2) = 0, and exhibit a root r with (r,r) = 2 and (r,y1)^2 + (r,y2)^2 = 5.
  `certify.certificate(G, y1, y2, R)` does this in Python integers and returns the witness. A verdict text of its own, for
  example "EXCLUDED (T18: root r with Y=5)", keeps these apart from the completed searches (section 6, point 7).
- A pair recorded "DEFERRED (pending T20 ...)" stays pending until T20 is proved. The bridge half is ready for it.

## 9. Weak points that could not be closed here

1. **The upstream reduction is not on this machine.** That every srg(99,14,1,2) with such an involution yields one of the 156
   envelopes U and a pair (y1, y2) of the producer's lists with its frame inside U cap {y1,y2}^perp (MODEL.md, T4, the C1
   notes, completeness of the pair enumeration) could not be read, let alone checked. A short attempt to derive the existence
   of U from the frame alone did not succeed: L (+) <7> (+) <7> has a unimodular overlattice only if its 7-adic discriminant
   form is hyperbolic, and that needs an argument about the frame that I do not have. The bridge does not need it and inherits
   it exactly as the 04/10 filter and every other verdict do. Hypothesis H5 is quoted from W, EG and the engine, which agree.
2. **T20 is open.** Nothing about the T20 pairs follows yet.
3. **T18 was not refereed again here.** I checked its statement, its hypotheses on sigma, and Proposition 3.1 (four lines). The
   rest is taken as given, with the caveats of its own section 9.3.
4. **The 04/10 graph lemma (H16)** is not needed by the bridge. Its hand parts were checked (section 3, F6) and its computed
   part was re-run with the dossier's own programs (section 7); I did not audit those programs line by line, and the
   structural text of W sections 3-6 that justifies what they enumerate was read, not re-derived.
5. **H4 on the quick deferral path** (section 5): an operational gap, closed by a re-check at conversion, not by the rule itself.
6. **The numerical checks are on other graphs** (9 and 243 vertices) and on an artificial integral lattice, because no 99-graph
   and no envelope of a real graph are available. They test the dictionary, not the campaign.
