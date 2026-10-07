# T20: no sigma-odd integer (-4)-eigenfunction of squared norm 20 on a srg(99,14,1,2)

> **State of this text (main session, 07/10, 14:10 UTC).**
> 1. Every case of the proof is now closed: the last one, case I with n_3 = 2, is section 9.B.6 (Computation 9.29, two
>    programs, written on 07/10 at 14:00 UTC). **Section 9.B.6 has not yet had its referee pass**; until it has, read
>    Theorem 10.2 as "proved, last section awaiting review".
> 2. III.1 has a second verification: a verifier re-traversed the whole tree (1,628,864 nodes, same counts per level, same
>    kept count at every node, 0 complete), and the single node the first program rejected by the rank bound is also dead
>    without it (`lemma/t20_III1/VERIF.md`). Scope of its independence, as that report says: its budget test, its PSD test and
>    its bookkeeping are its own; it shares the model file `cases.py` and parts of the enumeration skeleton and of the
>    candidate-generation loops with the first program. Sections 0.2, 7.3, 7.4, 10.2 and 10.3 still say "one program".
> 3. Case I, n_3 = 0: the second program (`in_verify.py`, no code shared with the first) is complete on eleven of the twelve
>    cases: stage 1 identical, stage 2 agreeing at every node, 0 complete configurations; where the first program used the
>    rank bound, the second closes the node by its own search. I.1 (3,4,0): 7,279,961 nodes, branch
>    `lemma-run/t20_I1_340-i-019e86d399c17954f`; the ten others on the branches `lemma-run/t20_Iv_{B,C,D,E,H,I,J}-*`. The last
>    case, I.1 (4,2,1), is running (`lemma/T20_BOARD.md`, line C2). Sections 0.2, 9.A and 10.2 still give the earlier counts.
> 4. Corrections of the referee report `lemma/t20_CODEX/REFEREE_T20_PROOF.md` merged on 07/10: E1 (sign in the proof of
>    Corollary 5.2), E2 (split parameter 3 means tasks of level 4), C2 (paths), G3 (item 2 above). Still to merge: G1, G2, C3.

## Proof text, state of 2026-10-07. Every case is closed; the last section (9.B.6) awaits its referee pass.

Self-contained proof text, written on 2026-10-07 from the working reports of the repository `conway99-c2-aws`
(`lemma/T20_WORK.md`, `lemma/T20_BOARD.md`, `lemma/t20/T20_REPORT.md`, `lemma/t20_R2/REPORT.md`, `lemma/t20_III1/`,
`lemma/t20_R3_I/REPORT.md`, `lemma/t20_HAND/NOTES.md`, `lemma/t20_HAND/SPEC_N3.md`, `lemma/t20_CODEX/*.md`), in the
same form as `lemma/T18_PROOF.md`. The working reports are sources, not part of the proof: every hand statement used
below is proved below, from the definitions. The finite computations are described precisely (what is enumerated, by
which tests, with which result, by how many programs), and for each of them the programs and their output files are
listed in appendix A.

**This text does not prove T20.** It proves, by hand statements and finite computations, Theorem 10.1: a
configuration, if there is one, has no active inner orbit (k = 0), has exactly two outside vertices with three
neighbours in S+ (n_3 = 2), and has profile (3,4,0) or (4,2,1). The exclusion of that last sub-case is Computation 9.29
(section 9.B.6, two programs).

(This file is `lemma/T20_PROOF.md`; its working files are in `lemma/t20_PROOF/`.)

## 0. Front matter

### 0.1 GAP boxes

**GAP boxes in this document: none.** Every hand statement was re-derived while it was written, and no step was
found that could not be justified. This sentence is about the hand proofs only. It says nothing about the
finite computations (section 10.2) or about what has not been independently
verified (section 10.4). Four points of section 10.4 deserve to be known before reading:

- several proofs of this text are not in the working reports and were written for it (list in section 10.4,
  item 12). Nobody but their author has read them;
- a "kept" decision of a positive-semidefiniteness test is a floating-point decision in every enumeration program. It
  is never used as a proof: only rejections are used, and they are exact (section 6.3). Every number of "nodes",
  "bases" or "kept" candidates printed below is therefore the size of a kept list of the named program, not a number
  of survivors in the mathematical sense, unless the text says otherwise;
- in every search (Computations 7.4, 8.9, 9.20) that has a second program, the second program re-traverses the
  search tree of the first one:
  it reads, at every node, which unit the first program chose, regenerates and tests all candidates of that unit
  with its own code, and stops if its number of kept candidates differs. It does not choose the units by itself
  (sections 7.4, 8.4, 9.A.5);
- the rank bound (Proposition 6.4) is used by the computations: at 1 node of configuration III.1 and at 15 nodes of
  the graph I.1 (section 10.3).

### 0.2 What is NOT covered

1. **Case k = 0, n_3 = 2** (section 9.B): closed on 07/10 by Computation 9.29 (two programs). The section has not
   yet been refereed.
2. **Computed lines that have one program only at the time of writing** (state of the sources: `T20_BOARD.md` and
   `lemma/t20_R3_I/REPORT.md` of 07/10; runs in progress are not anticipated):
   - configuration III.1 (Computation 7.5): one program; the independent verifier is running;
   - case k = 0, n_3 = 0 (Computations 9.19 and 9.20): two programs, both complete, for the two cases I.0 (4,2,1)
     and I.5 (4,2,1) only. For I.0 (3,4,0) the second program has done stage 1 (identical lists) and stage 2 on 372 of
     the 11,150 bases. For the nine other cases there is the first program only; the second program is running.
3. The lattice context (section 1.4), the three earlier small-norm statements (squared norms <= 14, 16 and 18) and
   the "dual-norm rule" built on the first of them: not used, not proved here (section 10.3).

### 0.3 Notation and conventions

- `u` between two sets is the union, `n` the intersection, `\` the difference; `|T|` is the number of elements.
- `x ~ y` means "x and y are adjacent"; `x not~ y` means "x and y are not adjacent".
- `N(x)` is the set of neighbours of x, `N[x] = N(x) u {x}`.
- `C(a,2) = a(a-1)/2`. `[P]` is 1 if the statement P is true and 0 otherwise.
- `I` is the identity matrix, `J` the all-ones matrix, `1_T` the indicator vector of a vertex set T, `e_x = 1_{x}`.
- For a matrix M and a vertex set Y, `M[Y]` is the principal submatrix on Y; for two lists R, R' of vertices,
  `A[R,R']` is the submatrix with rows R and columns R'.
- "PSD" means positive semidefinite.
- For two vertex sets X, Y: `e(X)` is the number of edges with both ends in X, `e(X,Y)` the number of edges with one
  end in X and the other in Y (X, Y disjoint).
- A vertex of N(p) is called **inner**; a vertex outside N[p] is called a **word** (the name used by all the working
  reports). An orbit {x, sigma x} is inner or a word orbit accordingly.
- Labels in square brackets such as [A7], [G0], [II.4], [C6], [H1] are the names of the same statements in the
  working reports. They are given only so that a reader of those reports can find the correspondence (appendix B);
  no proof below refers to them.
- A statement marked **Computation** is the result of a finite enumeration by programs. A statement marked
  **Lemma**, **Proposition**, **Theorem** or **Corollary** without that word is proved by hand in the text, except
  that the final statements of the cases (Corollary 4.13, Propositions 7.6, 8.10, 9.21, Theorem 10.1) combine hand
  statements with Computations and say so.
- Letters with several uses. The working reports use the letters W, R, T, U, t, s, c, Q, H for several objects each.
  In this text:
  - `W` is the set N(p) n X_1 (section 8: ten vertices; section 9: 2 h_1 vertices). The set called W in the report on
    profile (4,2,1) is called `L` here (Theorem 9.14).
  - `R` is a set of orbit representatives (section 6.4 only), and in section 9.B.4 the set N(z) n X_1. The set
    X_0 \ N[p], called Q or R in the reports, is called `R_0` here.
  - `T` is always N(z) n X_0 for the vertex z under discussion. The triangle called T in one report is `Delta` here.
  - `U(s)`, `V(s)` are the two index sets of the type of a vertex (section 5.5); `U`, `V` without argument are those
    of the vertex z of X_3 in section 9.B.
  - `t` is the level of a node in a search (number of orbits placed). The number of edges inside X_2, called t in the
    reports, is written e(X_2).
  - `s`, `s'` are vertices of X_2. The numbers called s(w) in one report are `rho(w)` here.
  - `c`, `c'` index the seven orbits {a_c, b_c} of N(p). `kappa_O` are the absolute values of section 3.
  - `Q` is the number sum d+(x)^2 of section 4. The identities called (Q0), (Q2) in the reports are (9.6) and (9.11).
  - `K` is the set of inner indices of the support (section 4.1); the reports call it H.
  - `E_0, E_3, E_{-4}` are the projectors of section 1.1; `e` is the number of edges inside S+.
- The nine support configurations keep the names of the working reports: I.0, ..., I.5, IIa.0, III.0, III.1. "Case
  I", "case II", "case III" are the three cases of Corollary 4.5 (k = 0, 2, 4).
- Programs are called by their file names.


## 1. Setting and statement

### 1.1 The graph

Throughout, G is a strongly regular graph with parameters (99, 14, 1, 2): it has 99 vertices, every vertex has
exactly 14 neighbours, two adjacent vertices have exactly 1 common neighbour (lambda = 1), and two distinct
non-adjacent vertices have exactly 2 common neighbours (mu = 2). Whether such a graph exists is Conway's 99-graph
problem; everything below is about a hypothetical G. A is its adjacency matrix.

The (x,y) entry of A^2 is the number of common neighbours of x and y, so

    A^2 = 14 I + 1 * A + 2 (J - I - A) = 12 I - A + 2 J.                                        (1.1)

A 1 = 14 * 1 (1 = all-ones vector). On the orthogonal complement of 1, (1.1) reads A^2 + A - 12 I = 0, i.e.
(A - 3I)(A + 4I) = 0, so the other eigenvalues are 3 and -4. If f and g are their multiplicities, f + g = 98 and
trace A = 0 = 14 + 3f - 4g, hence f = 54 and g = 44:

    eigenvalue 14 (multiplicity 1), 3 (multiplicity 54), -4 (multiplicity 44).

V_3 and V_{-4} are the eigenspaces, and E_0 = J/99, E_3, E_{-4} the orthogonal projectors on the three eigenspaces:
E_0 + E_3 + E_{-4} = I and A = 14 E_0 + 3 E_3 - 4 E_{-4}.

### 1.2 The involution

sigma is an automorphism of G such that sigma^2 is the identity and sigma has **exactly one fixed vertex**, called p.

This is all that is assumed about sigma. Nothing is assumed about other automorphisms of G, and nothing from the
lattice or "frame" picture that motivated the lemma is used.

For a vertex x != p the vertex sigma x is called the **mate** of x. The sets {x, sigma x} with x != p are the 49
**orbits**; {p} is the fixed orbit. An edge {x, sigma x} is called a **mate edge**. A vertex set Y is
**sigma-invariant** if sigma Y = Y. A function phi on the vertices is **sigma-odd** if phi(sigma x) = -phi(x) for
every vertex x; then phi(p) = 0.

### 1.3 Statement

> **T20.** Let G be a strongly regular graph with parameters (99,14,1,2) and sigma an automorphism of G of order 2
> with exactly one fixed vertex. There is no function phi from the vertex set of G to the integers such that
> (i) phi(sigma x) = -phi(x) for every vertex x, (ii) A phi = -4 phi, (iii) sum over all 99 vertices of
> phi(x)^2 = 20.

A triple (G, sigma, phi) satisfying the hypotheses is called a **configuration**. T20 says that no configuration
exists. **It is not proved here.** What is proved is the following chain; the last line is where it stops.

    phi integer-valued
      -> section 3 (hand):  phi takes the values 0, +1, -1 only; S+ = {phi = +1} has 10 vertices
      -> section 4 (hand + Computation 4.12): the number k of vertices of S+ in N(p) is 0, 2 or 4; the support, with
                            the vertex p, is one of nine explicit graphs: I.0 ... I.5 (k = 0), IIa.0 (k = 2),
                            III.0, III.1 (k = 4)
      -> section 7 (hand model + Computations 7.4, 7.5): III.0 and III.1 are impossible
                            (III.1: one program at the time of writing)
      -> section 8 (hand lemmas + Computations 8.8, 8.9): IIa.0 is impossible
      -> section 9 (hand):  for I.0 ... I.5 the number n_3 of outside vertices with three neighbours in S+ is 0 or
                            2, and the neighbourhood of p has profile (3,4,0) or (4,2,1)
      -> section 9.A (hand model + Computations 9.19, 9.20): n_3 = 0 is impossible for the six graphs and the two
                            profiles (two programs for two of the twelve cases, one for the others)
      -> section 9.B (hand model + Computation 9.29): n_3 = 2 is impossible for the six graphs and the two
                            profiles (two programs)

Section 5 contains the general facts on the vertices outside the support, and section 6 the tests used by the
computations (common-neighbour budgets, two PSD matrices, a rank bound) and the form of the searches, with their
proofs.

### 1.4 Context (not part of the lemma)

In the project, T20 is the graph form of a statement about a lattice (`LEMMA_TARGET_2026-10-06.md`, section 2, and
`lemma/BRIDGE.md`): T18 is the same statement with squared norm 18 (`lemma/T18_PROOF.md`), and according to
`lemma/T20_WORK.md` T20 is what remains to complete the exclusion of the 156 envelopes of the search. That
dictionary and that bridge are **outside this document**: what is treated here is the graph statement of section
1.3 and nothing else.

One remark on the statement itself (round 1, section 0): the task text given to the first working session said
"sum of phi(x)^2 = 40 (20 per side)". Everything else in the project says squared norm 20 on the 99 vertices, i.e.
10 on each of S+ and S-, and this is the statement treated in all the working reports and here. Nothing below
applies to squared norm 40.

The theorem T18 is not used anywhere in this text (section 10.3). Some general facts are common to the two texts
(Lemma 2.1, section 6.1, 6.2, 6.4); they are proved again here, so that this text stands alone.


## 2. Basic facts about sigma  [round 1, A0; (M) of round 2]

**Lemma 2.1.** Let x be a vertex, x != p.

(a) x ~ sigma x if and only if x ~ p.

(b) N(p) consists of 7 orbits {a_c, b_c}, c = 1..7, with b_c = sigma a_c; the 7 mate edges {a_c, b_c} are the only
    edges with both ends in N(p). In other words N(p) induces a perfect matching, made of mate edges.

(c) For c = 1..7 the only common neighbour of a_c and b_c is p. Hence no vertex other than p is adjacent to both
    a_c and b_c.

(d) If x is outside N[p], then x not~ sigma x, and N(x) n N(sigma x) = {z, sigma z} for a vertex z which is outside
    N[p] (and z != sigma z).

*Proof.* (Identical to T18_PROOF, Lemma 2.1.) Let C = N(x) n N(sigma x). Since sigma is an automorphism and an
involution, sigma C = N(sigma x) n N(x) = C: the set C is sigma-invariant. Also x != sigma x, because p is the only
fixed vertex.

(a) If x ~ sigma x, then |C| = 1 (lambda = 1); a sigma-invariant set with one element consists of a fixed vertex,
so C = {p} and x ~ p. Conversely let x ~ p. Then sigma x ~ sigma p = p, so p is in C. If x were not adjacent to
sigma x we would have |C| = 2 (mu = 2), C = {p, c} with c != p, and sigma c would be an element of C other than
sigma p = p, i.e. sigma c = c: a second fixed vertex, which does not exist. So x ~ sigma x.

(b) If a is in N(p) then sigma a is in N(p) (sigma p = p), a != sigma a, and a ~ sigma a by (a). So N(p) is a union
of orbits, 14/2 = 7 of them, each carrying a mate edge. The pair a, p is adjacent, so a and p have exactly one common
neighbour; a common neighbour of a and p is exactly a neighbour of a inside N(p). Hence a has exactly one neighbour
in N(p), and it is sigma a.

(c) In the proof of (a) we saw that C = {p} when x ~ sigma x; apply it to x = a_c.

(d) x is not adjacent to p, so x not~ sigma x by (a) and |C| = 2. p is not in C (x not~ p). A sigma-invariant
2-set that does not contain the fixed vertex is an orbit: C = {z, sigma z}, z != sigma z. If z were in N(p), then
by (c) the only common neighbour of z and sigma z would be p; but x is a common neighbour of z and sigma z (z and
sigma z are both in C, hence both adjacent to x), so x = p, a contradiction. And z != p. So z is outside N[p]. QED

**Corollary 2.2.** Every word x (vertex outside N[p]) has exactly 2 neighbours in N(p).

*Proof.* x and p are distinct and non-adjacent, so they have exactly 2 common neighbours, and the common neighbours
of x and p are the neighbours of x in N(p). QED

**Corollary 2.3.**

(a) The two neighbours in N(p) of a word lie in two different orbits of N(p).

(b) Let w be in N(p) and let {q, sigma q} be an orbit other than {w, sigma w}. If the orbit is inner, w is adjacent
    to neither q nor sigma q. If it is a word orbit, w is adjacent to at most one of q, sigma q.

(c) Let x be a word and {q, sigma q} an orbit with q != x, sigma x. If x ~ q and x ~ sigma q, then {q, sigma q} is a
    word orbit and N(q) n N(sigma q) = {x, sigma x}.

*Proof.* (a) By Lemma 2.1 (c) no vertex other than p is adjacent to both a_c and b_c. (b) The first statement is
Lemma 2.1 (b). For the second, suppose w ~ q and w ~ sigma q with q a word. Applying sigma to w ~ q gives
sigma w ~ sigma q. So sigma q is adjacent to both w and sigma w, the two ends of a mate edge of N(p), and
sigma q != p: this contradicts Lemma 2.1 (c). (c) x is adjacent to both q and sigma q and x != p, so by Lemma 2.1 (c)
the orbit is not inner; it is a word orbit, q not~ sigma q, and q, sigma q have exactly two common neighbours. x is
one of them, and so is sigma x (apply sigma to x ~ q and to x ~ sigma q). QED

Corollaries 2.2 and 2.3 are used many times below, often without mention, in the form "a word has exactly two
neighbours in N(p), in two different pairs" and "an inner vertex is adjacent to at most one end of each word orbit".


## 3. From integer values to the values 0, +1, -1  [round 1, A1, A2]

For an orbit O = {x, sigma x} put kappa_O = |phi(x)| = |phi(sigma x)|, an integer >= 0. As phi(p) = 0, hypothesis
(iii) reads: sum over the 49 orbits of 2 kappa_O^2 = 20, i.e.

    sum_O kappa_O^2 = 10.                                                                        (3.1)

**Lemma 3.1.** Let O be an orbit with kappa_O = kappa > 0. Then

    sum over the orbits O' != O of kappa_O'  >=  3 kappa  if O is inner,      >=  4 kappa  if O is a word orbit.

If O is inner and equality holds, then for x in O with phi(x) = kappa and for every orbit O' != O with
kappa_O' > 0, x is adjacent to exactly one vertex y of O', and phi(y) = -kappa_O'.

*Proof.* Choose x in O with phi(x) = kappa > 0. The eigen-equation at x is

    -4 kappa = sum over the neighbours y of x of phi(y).

Sort the neighbours of x by orbit. The neighbour p (if x ~ p) contributes 0. An orbit O' = {y, sigma y} different
from O contributes 0 if x is adjacent to none of its two vertices, +-kappa_O' if x is adjacent to exactly one of
them, and phi(y) + phi(sigma y) = 0 if x is adjacent to both; in all cases at least -kappa_O', with equality (when
kappa_O' > 0) only if x is adjacent to exactly one vertex of O' and that vertex has the value -kappa_O'. If O is
inner, sigma x is a neighbour of x (Lemma 2.1 (a)) and contributes -kappa; hence
-4 kappa >= -kappa - sum_{O' != O} kappa_O'. If O is a word orbit, sigma x is not a neighbour of x, and
-4 kappa >= - sum_{O' != O} kappa_O'. In the inner case, equality in the sum forces equality in every term. QED

**Lemma 3.2 [A2].** There is no configuration in which one orbit has kappa = 2, six orbits have kappa = 1 and the
others have kappa = 0.

*Proof.* The other orbits sum to 6 < 8, so by Lemma 3.1 the orbit O with kappa = 2 is inner, and equality holds in
Lemma 3.1 (6 = 3 * 2). Let x be in O with phi(x) = 2, so x is in N(p), sigma x ~ x and phi(sigma x) = -2. Name the
vertices of the six other orbits of the support x_1, ..., x_6 (phi = +1) and y_i = sigma x_i (phi = -1). By the
equality case of Lemma 3.1, x is adjacent to y_1, ..., y_6 and to none of x_1, ..., x_6. Applying sigma, sigma x is
adjacent to x_1, ..., x_6.

Consider x_1. It is adjacent to sigma x, and it is not p, so by Lemma 2.1 (c) it is not adjacent to x. Hence x_1 and
x are distinct and non-adjacent: they have exactly two common neighbours. One of them is sigma x (sigma x ~ x_1 and
sigma x ~ x). All of y_1, ..., y_6 are neighbours of x, so at most one of them is a neighbour of x_1. The
eigen-equation at x_1 reads -4 = sum over the neighbours w of x_1 of phi(w). The neighbours of x_1 with a non-zero
value are among sigma x (value -2), x_2, ..., x_6 (value +1 each) and y_1, ..., y_6 (value -1 each, at most one of
them is a neighbour); x is not a neighbour. So the sum is at least -2 - 1 = -3 > -4. Contradiction. QED

The proof uses only lambda = 1, mu = 2 and the eigen-equation.

**Proposition 3.3.** Let phi be an integer-valued sigma-odd function with A phi = -4 phi and sum phi(x)^2 = 20.
Then phi takes only the values 0, +1, -1, and the set S+ = {x : phi(x) = +1} has exactly 10 vertices. Moreover
S- = {x : phi(x) = -1} = sigma S+, and p is in neither.

*Proof.* By (3.1) the multiset of the non-zero values kappa_O is one of

    {3,1},   {2,2,1,1},   {2,1,1,1,1,1,1},   {1,1,1,1,1,1,1,1,1,1}

(the ways of writing 10 as a sum of squares 9, 4, 1). Lemma 3.1 excludes the first two:

    {3,1}:       kappa = 3, the others sum to 1  <  9;
    {2,2,1,1}:   kappa = 2, the others sum to 4  <  6.

The third is excluded by Lemma 3.2. So exactly 10 orbits have kappa_O = 1 and the other 39 have kappa_O = 0. In each
of the 10 orbits one vertex has phi = +1 and its mate has phi = -1. QED

So the general integer case adds nothing to the case of values 0, +1, -1. From now on a configuration is a triple
(G, sigma, phi) with phi as in Proposition 3.3, and

    S+ = {phi = +1} (10 vertices),   S- = sigma S+ = {phi = -1},   S = S+ u S-  (the support, 20 vertices).

There are 99 - 20 = 79 vertices outside S, and p is one of them.


## 4. The support

### 4.1 Notation and the eigen-equation

For a vertex v let d+(v) = |N(v) n S+| and d-(v) = |N(v) n S-|. Since sigma exchanges S+ and S-,

    d+(sigma v) = d-(v)   and   d-(sigma v) = d+(v)   for every vertex v.                          (4.1)

(A phi)(v) = d+(v) - d-(v), so A phi = -4 phi says exactly:

    d-(x) = d+(x) + 4   for x in S+;                                                             (4.2)
    d+(v) = d-(v)       for v outside S; this common value is written d(v).                      (4.3)

By (4.1), d(sigma v) = d(v) for v outside S. Three numbers are attached to the configuration:

    k = d(p) = the number of vertices of S+ in N(p);
    e = the number of edges with both ends in S+;
    Q = sum over x in S+ of d+(x)^2.

An orbit {a_c, b_c} of N(p) is **active** if phi(a_c) != 0. Then exactly one of a_c, b_c is in S+ and the other is
in S-, so k is the number of active orbits of N(p), S n N(p) has 2k vertices and S \ N(p) has 20 - 2k vertices.
p is not in S.

Label S+ = {x_0, ..., x_9} and put y_i = sigma x_i, so S- = {y_0, ..., y_9}. Call the index i **inner** if x_i is in
N(p) and **outer** otherwise; K is the set of inner indices (|K| = k), and eps_i = 1 if i is inner, 0 if i is outer.
By Lemma 2.1 (a),

    x_i ~ y_i  if and only if  i is inner.                                                       (4.4)

For an index j let M_j = {i != j : x_j ~ y_i}. Applying sigma, x_j ~ y_i if and only if x_i ~ y_j, so

    i is in M_j  if and only if  j is in M_i.                                                    (4.5)

d-(x_j) = |M_j| + eps_j by (4.4), so by (4.2)

    |M_j| = d+(x_j) + 4 - eps_j.                                                                 (4.6)

A pair {i, j} with x_i ~ y_j (i in M_j) is called a **minus edge**, and a pair {i, j} with x_i ~ x_j (equivalently
y_i ~ y_j) a **plus edge**; e is the number of plus edges.

### 4.2 k is 0, 2 or 4  [A3]

**Lemma 4.1.** k is in {0, 2, 4}. If k = 4, then every active inner vertex has exactly 3 neighbours in S \ N(p), and
no inactive inner vertex has a neighbour in S.

*Proof.* Fix c. By Lemma 2.1 (b) the neighbours of a_c are p, b_c and 12 words; call the latter the outer
neighbours of a_c. The eigen-equation at a_c is

    -4 phi(a_c) = phi(p) + phi(b_c) + (sum of phi over the 12 outer neighbours) = 0 - phi(a_c) + (that sum),

so the sum of phi over the outer neighbours of a_c is -3 phi(a_c). Let n_c be the number of outer neighbours of
a_c that lie in S. As phi is +-1 on S and 0 elsewhere,

    n_c = phi(a_c) (mod 2)   and   n_c >= 3 |phi(a_c)|.

So n_c is odd and >= 3 if the orbit c is active, and n_c is even otherwise. By sigma, b_c has the same number n_c of
outer neighbours in S.

Now count the pairs (s, v) with s in S \ N(p), v in N(p), s ~ v. By Corollary 2.2 each s contributes 2, so the
number is 2 (20 - 2k). Counting by v it is sum over c of 2 n_c. Hence sum_c n_c = 20 - 2k.

Parity: sum_c n_c = k (mod 2) and 20 - 2k is even, so k is even. Size: sum_c n_c >= 3k, so 20 - 2k >= 3k and
k <= 4. Hence k is 0, 2 or 4. If k = 4, then sum_c n_c = 12 = 3k, so n_c = 3 for the four active orbits and n_c = 0
for the three inactive ones; an inactive inner vertex has the neighbours p, its mate (not in S) and 12 words, none
of them in S. QED

### 4.3 Three counting identities  [A4]

**Lemma 4.2.** With the sums taken over all vertices z outside S (p included, with d(p) = k), and with n_d the
number of z outside S with d(z) = d:

    (I1)   sum_z C(d(z), 2) = 30 - 7e - Q;
    (I2)   sum_z d(z)       = 100 - 4e;
    (I3)   sum_z C(d(z) - 1, 2) = n_0 + n_3 + 3 n_4 + 6 n_5 + ... = 9 - 3e - Q.

*Proof.* (I2). A vertex x of S+ has d+(x) neighbours in S+, d+(x) + 4 in S-, hence 10 - 2 d+(x) outside S. Summing
over S+, the number of edges between S+ and the outside of S is 100 - 2 * 2e = 100 - 4e, and it is also
sum_z d+(z) = sum_z d(z).

(I1). Count the triples ({x, x'}, v) where {x, x'} is a pair of distinct vertices of S+ and v is a common neighbour
of x and x'. There are C(10,2) = 45 pairs; the e adjacent ones have 1 common neighbour and the others 2, so the
number of triples is 90 - e. Counting by v: a vertex v contributes C(d+(v), 2). For v = x in S+ this is
C(d+(x), 2). For v = sigma x in S- it is C(d-(x), 2) = C(d+(x) + 4, 2) by (4.1) and (4.2). For v = z outside S it is
C(d(z), 2). Since C(d,2) + C(d+4,2) = d^2 + 3d + 6,

    90 - e = sum_{x in S+} (d+(x)^2 + 3 d+(x) + 6) + sum_z C(d(z),2) = Q + 6e + 60 + sum_z C(d(z),2).

(I3). C(d,2) - (d - 1) = (d-1)(d-2)/2 = C(d-1, 2), which is 1, 0, 0, 1, 3, 6 for d = 0, 1, 2, 3, 4, 5. There are 79
vertices outside S, so (I1) - (I2) + 79 gives sum_z C(d(z)-1, 2) = (30 - 7e - Q) - (100 - 4e) + 79 = 9 - 3e - Q. QED

### 4.4 e is at most 1

**Lemma 4.3.** e <= 1. If e = 1, then Q = 2.

*Proof.* Q = sum d+(x)^2 >= sum d+(x) = 2e. The left side of (I3) is >= 0, so 0 <= 9 - 3e - Q <= 9 - 5e and e <= 1.
If e = 1, the two ends of the unique edge inside S+ have d+ = 1 and the other eight vertices have d+ = 0. QED

*Remark.* The bound obtained from A <= 14 E_0 + 3 (I - E_0), which gave e <= 2 for squared norm 18, gives only
e <= 3 here; (I3) is what is used.

### 4.5 The parity law, and the three cases  [A5]

**Lemma 4.4.** e = C(k,2) (mod 2).

*Proof.* The complement of S is sigma-invariant and p is its only fixed vertex, so the 78 vertices z != p outside S
are paired by sigma, with d(sigma z) = d(z). Hence sum_{z outside S, z != p} C(d(z),2) is even, and by (I1)
30 - 7e - Q = C(k,2) (mod 2). Finally Q = sum d+(x)^2 = sum d+(x) = 2e = 0 (mod 2). So 7e + C(k,2) is even. QED

**Corollary 4.5.** The pair (k, e) is one of

    (0, 0)  (case I),      (2, 1)  (case II),      (4, 0)  (case III).

*Proof.* Lemmas 4.1 and 4.3 leave k in {0, 2, 4} and e in {0, 1}; C(0,2) = 0, C(2,2) = 1 and C(4,2) = 6, so by Lemma
4.4 e is even for k = 0 and k = 4, and odd for k = 2. QED

### 4.6 Case II: where the plus edge is  [A7, A8]

In case II there are two inner indices and eight outer ones, and exactly one plus edge {a, b}:
d+(x_a) = d+(x_b) = 1 and d+ = 0 on the other eight vertices of S+.

**Lemma 4.6.** In case II the two ends of the plus edge are not both inner.

*Proof.* If a and b were both inner, x_a and x_b would be adjacent vertices of N(p). By Lemma 2.1 (b) the only edges
inside N(p) are mate edges, so x_b would be the mate of x_a; but the mate of x_a is y_a, which is in S-. QED

**Lemma 4.7 [A7].** In case II the plus edge does not join an outer index and an inner index.

*Proof.* Suppose it does. Name the indices so that the plus edge is {0, c} with 0 outer and c inner; let c' be the
other inner index and W' the set of the seven other outer indices. By (4.6):
|M_0| = 5, |M_c| = 1 + 4 - 1 = 4, and |M_j| = 4 for j in W'.

- c is not in M_0: otherwise x_0 would be adjacent to x_c and to its mate y_c, which Lemma 2.1 (c) forbids because
  x_0 != p. By (4.5), 0 is not in M_c.
- c' is not in M_c: x_c and y_c' are two vertices of N(p) that are not mates, so they are not adjacent (Lemma
  2.1 (b)).

So M_c is a 4-subset of W' and M_0 is a 5-subset of W' u {c'}, a set of 8 elements. For i in M_0 n M_c the vertex
y_i is a common neighbour of the adjacent vertices x_0 and x_c, which have only one. So |M_0 n M_c| <= 1, hence
|M_0 u M_c| >= 8, and therefore

    M_0 u M_c = W' u {c'},     M_0 n M_c = {u} for one index u of W',     c' is in M_0.

Put U_0 = M_c \ {u}, a set of three outer indices. Let j be in U_0. Then j is in M_c and not in M_0; by (4.5), c is
in M_j and 0 is not in M_j. M_j has 4 elements, none of which is j or 0; so M_j \ {c} is a 3-subset of
W' u {c'} = M_0 u M_c.

- x_j and x_c are not adjacent (the only plus edge is {0, c}). y_c is a common neighbour of them (x_c ~ y_c by (4.4),
  and x_j ~ y_c because c is in M_j), and so is y_i for every i in M_j n M_c; these vertices are distinct (c is not
  in M_c). Hence 1 + |M_j n M_c| <= 2, i.e. |M_j n M_c| <= 1.
- x_j and x_0 are not adjacent, and y_i is a common neighbour for every i in M_j n M_0. Hence |M_j n M_0| <= 2.
- c is in neither M_0 nor M_c, and M_0 n M_c = {u}, so

      3 = |M_j \ {c}| = |M_j n M_0| + |M_j n M_c| - [u in M_j] <= 2 + 1 - [u in M_j].

  Hence u is not in M_j and |M_j n M_c| = 1. As u is not in M_j and j is not in M_j, the set M_j n M_c is contained
  in U_0 \ {j}: the index j has exactly one minus-neighbour in U_0 \ {j}.

By (4.5) the relation "i is in M_j" is symmetric. So it defines a graph on the 3-set U_0 in which every vertex has
degree exactly 1. A graph has an even number of vertices of odd degree. Contradiction. QED

**Lemma 4.8 [A8].** In case II let {a, b} be the plus edge (a, b outer, by Lemmas 4.6 and 4.7). Then x_a ~ y_b and
x_b ~ y_a: the four vertices x_a, x_b, y_a, y_b induce the 4-cycle x_a - x_b - y_a - y_b - x_a.

*Proof.* |M_a| = |M_b| = 5 by (4.6). Suppose b is not in M_a. By (4.5), a is not in M_b. Then M_a and M_b are
5-subsets of the 8 indices other than a and b, so |M_a n M_b| >= 2: two vertices y_i are common neighbours of the
adjacent vertices x_a and x_b, which have only one. So b is in M_a and a is in M_b. The edges are x_a x_b,
x_b y_a, y_a y_b (the image of x_a x_b) and y_b x_a; x_a not~ y_a and x_b not~ y_b by (4.4). QED

Lemma 4.8 is not needed for what follows (the enumeration of section 4.9 does not assume it and finds it); it is
stated because the working reports describe case II by it.

### 4.7 Case III: the words of the support are the edges of K4  [A9, first part]

**Lemma 4.9.** In case III let K be the set of the four inner indices.

(a) For c in K, the neighbours of x_c in S are y_c and exactly three vertices y_j with j outer.

(b) For j outer, the two neighbours of x_j in N(p) are y_c and y_c' for two distinct indices c, c' of K. Put
    kappa(j) = {c, c'}. For c in K and j outer: x_c ~ y_j if and only if c is in kappa(j).

(c) kappa is a bijection from the six outer indices onto the six 2-subsets of K.

(d) The six inactive inner vertices have no neighbour in S.

*Proof.* (d) is the last statement of Lemma 4.1. (a) By Lemma 4.1, x_c has exactly 3 neighbours in S \ N(p). By the
proof of Lemma 4.1 the sum of phi over them is -3 phi(x_c) = -3, so all three are in S-. Inside N(p) the only
neighbour of x_c is its mate y_c. (b) x_j is a word: it has exactly two neighbours in N(p), in two different orbits
(Corollaries 2.2, 2.3). By (d) they are active inner vertices, i.e. vertices x_c or y_c with c in K. As e = 0, x_j has
no neighbour in S+. So they are y_c and y_c' with c != c'. Applying sigma, y_j ~ x_c if and only if x_j ~ y_c.
(c) By (a) every c of K lies in kappa(j) for exactly three outer j. Let c != c' be in K. The vertices x_c and x_c'
are in N(p), they are not mates, so they are non-adjacent and have exactly two common neighbours, one of which is p.
For every j with kappa(j) = {c, c'} the vertex y_j is a common neighbour. So at most one j has kappa(j) = {c, c'}.
There are six outer indices and six 2-subsets of K. QED

### 4.8 Case I: the orbit graph B  [A10, first part]

**Lemma 4.10.** In case I (k = 0, e = 0):

(a) S+ and S- are independent sets;
(b) no vertex of S is in N[p]; in particular d(p) = 0;
(c) x_i not~ y_i for every i;
(d) every vertex of S has exactly 4 neighbours in S, and they are on the other side: d-(x_i) = 4, d+(x_i) = 0.

Define a graph B on the index set {0, ..., 9} by: i ~_B j if and only if x_i ~ y_j. Then B is a well-defined simple
graph, it is 4-regular, and any two distinct indices i, j have at most 2 common neighbours in B. For i != j the
number of common neighbours of x_i and x_j that lie in S is exactly the codegree codeg_B(i,j) = |B(i) n B(j)|,
where B(i) is the set of B-neighbours of i. For all i, l (i = l allowed), x_i and y_l have no common neighbour in S.

*Proof.* (a) e = 0, and S- = sigma S+. (b) k = 0 says that no vertex of S+ is in N(p); apply sigma for S-; p is not
in S. (c) is (4.4) with all indices outer. (d) is (4.2) with d+ = 0. The relation ~_B is symmetric by (4.5), and
there is no loop by (c). The B-neighbours of i are the indices j with y_j in N(x_i), and d-(x_i) = 4, so B is
4-regular. Let i != j. The vertices x_i and x_j are distinct and non-adjacent, so they have exactly 2 common
neighbours in G. Their common neighbours inside S are in S- (S+ is independent), and y_l is a common neighbour
exactly when l is in B(i) n B(j). So codeg_B(i,j) <= 2. Finally a common neighbour of x_i and y_l inside S would be
in S+ and adjacent to x_i, or in S- and adjacent to y_l; both are excluded by (a). QED

### 4.9 Support structures and their enumeration  [round 1, B1, B2]

**Definition.** Let K be a subset of {0, ..., 9} and P a set of 2-subsets of {0, ..., 9}. A **support structure of
type (K, P)** is a graph on the 21 vertices x_0, ..., x_9, y_0, ..., y_9, p such that:

- (S1) it is invariant under the involution that exchanges x_i and y_i for every i and fixes p;
- (S2) p ~ x_i and p ~ y_i and x_i ~ y_i if i is in K; none of the three if i is not in K;
- (S3) for i != j: x_i ~ x_j if and only if {i, j} is in P;
- (S4) (the eigen-equation) for every i: (number of j != i with x_i ~ y_j) + [i in K] = (number of j with
  {i, j} in P) + 4;
- (S5) (the budgets) two adjacent vertices have at most 1 common neighbour among the 21 vertices, and two distinct
  non-adjacent vertices at most 2.

By (S1) the adjacencies between two orbits i != j are given by two bits: "minus" (x_i ~ y_j and x_j ~ y_i) and
"plus" (x_i ~ x_j and y_i ~ y_j). So a support structure of type (K, P) is the same thing as a set of minus edges.
Two support structures are **isomorphic** if one is obtained from the other by a permutation of the ten indices
(applied to the x_i and to the y_i together); such a permutation carries the type (K, P) to its image.

**Lemma 4.11.** In a configuration, with any labelling S+ = {x_0, ..., x_9}, y_i = sigma x_i, the induced subgraph
of G on S u {p} is a support structure of type (K, P), where K is the set of inner indices and P the set of plus
edges. Moreover, after a suitable relabelling of the ten orbits of the support, the type is one of

    case I:    K empty,          P empty;
    case IIa:  K = {0, 1},       P = {{2, 3}};
    case III:  K = {0, 1, 2, 3}, P empty.

*Proof.* (S1): sigma is an automorphism exchanging x_i and y_i and fixing p. (S2): p ~ x_i iff x_i is in N(p) iff
i is in K; p ~ y_i likewise by sigma; x_i ~ y_i iff i is in K by (4.4). (S3) is the definition of P. (S4) is (4.6).
(S5): a common neighbour inside S u {p} is a common neighbour in G, and G has lambda = 1 and mu = 2. For the types:
by Corollary 4.5 the pair (k, e) is (0,0), (2,1) or (4,0). In case II the plus edge joins two outer indices (Lemmas
4.6, 4.7). Relabel so that the inner indices come first and, in case II, the plus edge is {2, 3}. QED

The type K = {0, 1}, P = {{0, 2}} (plus edge between an inner and an outer index) is called IIb in the working
reports; by Lemma 4.7 it does not occur, and the programs confirm that it has no support structure.

> **Computation 4.12.** The numbers of labelled support structures of the following types are:
>
> | type | labelled support structures |
> |---|---|
> | I, with the additional normalisation "the minus-neighbours of the index 0 are 1, 2, 3, 4" | 27720 |
> | IIa: K = {0,1}, P = {{2,3}} | 2880 |
> | IIb: K = {0,1}, P = {{0,2}} | 0 |
> | III: K = {0,1,2,3}, P empty | 10080 |
>
> Up to isomorphism there are exactly six support structures of type I, one of type IIa and two of type III. They
> are listed in section 4.10 under the names I.0, ..., I.5, IIa.0, III.0, III.1.

*Why the list is complete, given the counts.* Let G_0 be the group of the permutations of the ten indices that
preserve the type: all 10! permutations for type I, 2 * 2 * 6! = 2880 for IIa (exchange of the two inner indices,
exchange of 2 and 3, permutations of 4..9) and 4! * 6! = 17280 for III. The labelled structures of a type that are
isomorphic to a given one, with automorphism group of order a inside G_0, are |G_0| / a in number; for type I with
the normalisation of the table they are 10! / (126 a), because the C(9,4) = 126 possible sets of minus-neighbours
of the index 0 are permuted transitively by the permutations fixing 0 (each class is 4-regular at 0). With the
orders a of section 4.10:

    type I:    10!/126 * (1/16 + 1/4 + 1/10 + 1/4 + 1/4 + 1/20) = 1800 + 7200 + 2880 + 7200 + 7200 + 1440 = 27720;
    type IIa:  2880 / 1 = 2880;
    type III:  17280 * (1/3 + 1/4) = 5760 + 4320 = 10080.

The nine graphs of section 4.10 are support structures of their types, they are pairwise non-isomorphic (the six
of type I have six different tables of codegrees; III.0 and III.1 differ by the graph on the outer indices), and
their classes already account for the totals of the table. So there is no other class. This argument uses, as
computed data, the four totals and the nine orders a.

Programs (two, written separately):

- `lemma/t20/t20_enum.py` with `t20_kernel.py` and `t20_common.py` (enumerator 1): backtracking over the 45 pairs of
  orbits with an incremental test of (S5) and degree pruning for (S4); every structure found is re-checked; the
  structures are sorted into isomorphism classes and the automorphism orders computed. Results: 27720 (1,841,249
  search nodes), 2880 (6,414,667), 0 (1,463,867), 10080 (469,755) labelled structures; 6, 1, 0, 2 classes, with the
  orders 16, 4, 10, 4, 4, 20; 1; 3, 4; the count |G_0| / a is checked for every class (`enum_I.out`,
  `enum_III_IIb_IIa.out`).
- `lemma/t20/t20_verify.py` (enumerator 2; no shared code: pure Python, the pairs in the reverse order, the inner
  orbits on the highest labels, for type I the minus-neighbours of the index 9 fixed instead of those of 0; every
  structure found is re-tested from scratch with A @ A and A phi = -4 phi). Results: 27720, 2880, 0, 10080 labelled
  structures (`verify_III_I.out`, `verify_IIa.out`, `verify_II.out`, `verify_IIb.out`). It has **no isomorphism
  test**: it sorts the labelled structures by an invariant (traces of powers of a weighted orbit matrix) and finds
  6, 1, 2 distinct invariants with the multiplicities 1800 / 2880 / 7200 / 7200 / 7200 / 1440, 2880, and
  5760 / 4320, equal to the numbers |G_0| / a predicted from enumerator 1.

So the four totals come from two programs; the nine automorphism orders come from enumerator 1 only. (For this
text they were recomputed, together with the conditions (S1)-(S5), the codegrees and the units of section 4.10, by
the transcription script `lemma/t20_PROOF/_check_text_data.py`; it is a check of the printed data, not a
third enumeration.) Two details of the runs: for type IIa the verifier was run with the plus edge on the labels
6, 7 (3,208,774 nodes); its run with the plus edge on the labels 0, 1 was cut by its time limit and gave nothing.
For type IIb it was run twice (plus edge on the labels 0, 9: 10,596,116 nodes; on 7, 9: 731,934 nodes), with 0
structures both times. The number of labelled structures of a type does not depend on which labels carry the plus
edge.

**Corollary 4.13 (hand statements + Computation 4.12).** In a configuration, after a suitable labelling of the ten
orbits of the support, the induced subgraph of G on S u {p} is one of the nine graphs I.0, ..., I.5, IIa.0, III.0,
III.1 of section 4.10. Once this is arranged, the labellings that give exactly the same graph differ by the
automorphisms of the structure.

*Proof.* Lemma 4.11 and Computation 4.12. QED

### 4.10 The nine configurations  [round 1, section C]

The vertices are x_0..x_9, y_0..y_9, p. A minus edge "ij" means x_i ~ y_j and x_j ~ y_i. An inner index c means
x_c ~ y_c, p ~ x_c, p ~ y_c. Nothing else is adjacent in S u {p}, except the plus edge of IIa.0.

**Case I: no inner index; the minus edges are the edges of B (Lemma 4.10).**

| | edges of B | automorphisms | triangles | codegrees of adjacent pairs | codegrees of non-adjacent pairs |
|---|---|---|---|---|---|
| I.0 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79 | 16 | 4 | 8 pairs with 0, 12 with 1 | 1 with 0, 24 with 2 |
| I.1 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78 | 4 | 6 | 3 with 0, 16 with 1, 1 with 2 | 8 with 1, 17 with 2 |
| I.2 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89 | 10 | 5 | 5 with 0, 15 with 1 | 5 with 1, 20 with 2 |
| I.3 | 01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79 | 4 | 6 | 4 with 0, 14 with 1, 2 with 2 | 1 with 0, 6 with 1, 18 with 2 |
| I.4 | 01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79 | 4 | 8 | 2 with 0, 12 with 1, 6 with 2 | 3 with 0, 8 with 1, 14 with 2 |
| I.5 | 01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89 | 20 | 10 | 10 with 1, 10 with 2 | 5 with 0, 10 with 1, 10 with 2 |

Characteristic polynomials of B (identification only; not used):

    I.0:  (t-4)(t-1)^2(t+1)(t^2+t-4)(t^2+2t-1)^2
    I.1:  (t-4)(t+2)(t^2-2)(t^3-4t+2)(t^3+2t^2-2t-2)
    I.2:  t(t-4)(t^4+2t^3-4t^2-5t+5)^2
    I.3:  (t-4)(t-1)(t+1)^2(t^2-3)(t^2+t-4)(t^2+2t-1)
    I.4:  (t-4)(t-1)(t+1)^4(t^2-5)(t^2+t-4)
    I.5:  t(t-4)(t+1)^4(t^2-5)^2

According to `names.out`, I.5 is isomorphic to the circulant graph C10(1,2) and the five others are none of the
4-valent circulants on 10 vertices (not used).

**Case II: inner indices 0, 1; plus edge {2, 3}.**

| | minus edges | plus edge | automorphisms |
|---|---|---|---|
| IIa.0 | 07 08 09 13 15 16 23 24 26 28 29 35 37 39 45 46 48 57 68 79 | 23 | 1 |

In IIa.0 the minus edge 23 is present, as Lemma 4.8 says; the common neighbour of x_2 and x_3 is y_9.

**Case III: inner indices 0, 1, 2, 3; the outer indices 4..9 are the 2-subsets of {0,1,2,3} (Lemma 4.9):
kappa(4) = {2,3}, kappa(5) = {1,3}, kappa(6) = {1,2}, kappa(7) = {0,3}, kappa(8) = {0,2}, kappa(9) = {0,1}.**

| | minus edges | minus edges between outer indices | automorphisms |
|---|---|---|---|
| III.0 | 07 08 09 15 16 19 24 26 28 34 35 37 48 49 57 58 67 69 | the hexagon 4-8-5-7-6-9 | 3 |
| III.1 | 07 08 09 15 16 19 24 26 28 34 35 37 48 49 56 57 67 89 | the two triangles 4-8-9 and 5-6-7 | 4 |

**Units.** For i < j let

    need(i, j) = 2 - [x_i ~ x_j] - (the number of common neighbours of x_i and x_j in S u {p}).              (4.7)

It is the number of common neighbours of x_i and x_j outside S u {p}; a pair with need > 0 is called a **deficient
pair** or a **unit**. For case I, need(i,j) = 2 - codeg_B(i,j) (Lemma 4.10). The units of the nine structures
(`deficiency.out`; recomputed by `_check_text_data.py`):

| | total | pairs with need = 2 | pairs with need = 1 |
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

(The totals are forced: for case I, the sum over the 45 pairs of 2 - codeg_B is 90 - 10 * C(4,2) = 30.)

*Remark (not used).* On S u {p}, for each of the nine structures, the matrix M1 of section 6.1 is positive definite
and M2 is positive semidefinite of rank 20, exactly (`enum_I.out`, `enum_III_IIb_IIa.out`). So the two PSD tests
exclude nothing at the level of the support.


## 5. The vertices outside the support

From here on a configuration is in one of the three cases of Corollary 4.5, and e <= 1.

### 5.1 The classes X_d

For d >= 0 let X_d be the set of vertices z outside S with d(z) = d, i.e. with exactly d neighbours in S+ and d in
S- (see (4.3)), and n_d = |X_d|. Each X_d is sigma-invariant, because d(sigma z) = d(z). p is in X_k. For a vertex v
and an integer j let

    a_j(v) = |N(v) n X_j|.

A vertex of S is called a **plus end** if it is an end of an edge inside S+ or of an edge inside S-. There is no
plus end in cases I and III, and there are four in case II (x_a, x_b, y_a, y_b for the plus edge {a, b}). For a
vertex z let q(z) be the number of neighbours of z that are plus ends. A vertex w of S has exactly

    4 + 2 [w is a plus end]                                                                      (5.1)

neighbours in S: for w = x in S+ this is d+(x) + d-(x) = 2 d+(x) + 4 by (4.2), and d+(x) is 1 for a plus end and 0
otherwise (e <= 1); for w in S- apply sigma.

### 5.2 The path-count identity  [G0; round 1, A6]

**Lemma 5.1.** Let z be outside S with d(z) = d. Then

    sum over the neighbours w of z outside S of d(w) = 20 - 5d - q(z),                           (5.2)

i.e. a_1(z) + 2 a_2(z) + 3 a_3(z) + 4 a_4(z) + ... = 20 - 5d - q(z), and

    a_0(z) - a_2(z) - 2 a_3(z) - 3 a_4(z) - ... = 3d + q(z) - 6.                                 (5.3)

*Proof.* Count the pairs (w, s) with s in S, w ~ z and w ~ s. For a fixed s (s != z since z is outside S) the
number of w is the number of common neighbours of z and s: 1 if s ~ z, 2 otherwise. z has 2d neighbours in S, so
the count is 2d + 2 (20 - 2d) = 40 - 2d. For a fixed neighbour w of z the number of s is the number of neighbours
of w in S: 4 + 2 [w is a plus end] if w is in S, by (5.1), and d+(w) + d-(w) = 2 d(w) if w is outside S. So

    40 - 2d = 4 * 2d + 2 q(z) + 2 sum_{w ~ z, w outside S} d(w),

which is (5.2). The degree of z is 14 = 2d + a_0 + a_1 + a_2 + ...; subtracting this from (5.2) gives
sum_j (j - 1) a_j = 6 - 3d - q(z), which is (5.3). QED

**Corollary 5.2.** Every vertex outside S has d <= 4. A vertex z outside S with d(z) = 4 has q(z) = 0 and its six
neighbours outside S are in X_0.

*Proof.* The left side of (5.2) is >= 0, so 5d <= 20. If d = 4 the equation reads
0 = q(z) + (the sum of d(w) over the neighbours w of z outside S), a sum of two non-negative terms: so
q(z) = 0 and every neighbour of z outside S has d = 0; there are 14 - 8 = 6 of them. QED

### 5.3 The sizes of the classes

**Lemma 5.3.**

(I) In case I: X_4 is empty, p is in X_0, n_3 is even, and

        n_0 = 9 - n_3,     n_1 = 40 + 3 n_3,     n_2 = 30 - 3 n_3.

(II) In case II: X_4 is empty, p is in X_2, and

        n_0 = 4 - n_3,     n_1 = 54 + 3 n_3,     n_2 = 21 - 3 n_3.

(III) In case III: X_4 = {p}, X_3 is empty, X_0 is the set of the six inactive inner vertices, n_2 = 24 and
      n_1 = 48. In particular every vertex of X_1 u X_2 is a word.

*Proof.* By Corollary 5.2, n_d = 0 for d >= 5, so (I3) reads n_0 + n_3 + 3 n_4 = 9 - 3e - Q. A class X_d that does
not contain p has an even number of elements (it is sigma-invariant and p is the only fixed vertex).

(I) e = 0, Q = 0: n_0 + n_3 + 3 n_4 = 9. p is in X_0 (k = 0), so n_3 and n_4 are even. If n_4 >= 2, then n_0 <= 3;
but a vertex of X_4 has six neighbours in X_0 (Corollary 5.2). So n_4 = 0 and n_0 = 9 - n_3. Then
n_0 + n_1 + n_2 + n_3 = 79 and, by (I2), n_1 + 2 n_2 + 3 n_3 = 100; solving, n_2 = 30 - 3 n_3 and n_1 = 40 + 3 n_3.

(II) e = 1, Q = 2 (Lemma 4.3): n_0 + n_3 + 3 n_4 = 4. p is in X_2 (k = 2), so n_4 is even, hence n_4 = 0 and
n_0 = 4 - n_3. By (I1), n_2 + 3 n_3 = 30 - 7 - 2 = 21. Then n_1 = 79 - n_0 - n_2 - n_3 = 54 + 3 n_3. (Check with
(I2): n_1 + 2 n_2 + 3 n_3 = 96 = 100 - 4.)

(III) e = 0, Q = 0: n_0 + n_3 + 3 n_4 = 9. p is in X_4 (k = 4), so n_4 >= 1. The six inactive inner vertices are
outside S and have no neighbour in S (Lemma 4.1), so they are in X_0 and n_0 >= 6. Hence n_3 + 3 n_4 <= 3:
n_4 = 1, n_3 = 0, n_0 = 6. So X_4 = {p} and X_0 is the set of the six inactive inner vertices. Then
n_1 + n_2 = 79 - 6 - 1 = 72 and, by (I2), n_1 + 2 n_2 + 4 = 100; so n_2 = 24 and n_1 = 48. Finally
N(p) consists of the eight active inner vertices, which are in S, and of X_0; so no vertex of X_1 u X_2 is in N(p),
and none is p. QED

### 5.4 A bound on the neighbours in X_0  [G1]

**Lemma 5.4.** Let z be a vertex outside S, z != p, and T = N(z) n X_0.

(a) If z is a word, then p is not in T, T u sigma T is contained in X_0 \ {p}, and

        2 |T| - 2 <= |X_0 \ {p}|.

(b) If z is in N(p), then 2 |T| - 1 <= |X_0|.

*Proof.* sigma T = N(sigma z) n X_0, because X_0 is sigma-invariant. T n sigma T is contained in
N(z) n N(sigma z). (a) z not~ p, so p is in neither T nor sigma T. z and sigma z are distinct and non-adjacent
(Lemma 2.1 (a)), so |N(z) n N(sigma z)| = 2 and |T u sigma T| >= 2 |T| - 2. (b) N(z) n N(sigma z) = {p} by Lemma
2.1 (c), so |T u sigma T| >= 2 |T| - 1, and T u sigma T is contained in X_0. QED

### 5.5 Types, and the units  [round 1, section C; C2]

For a vertex s outside S, the **type** of s is the pair (U(s) ; V(s)), where

    U(s) = {i : s ~ x_i},      V(s) = {l : s ~ y_l};      |U(s)| = |V(s)| = d(s).

Applying sigma: U(sigma s) = V(s) and V(sigma s) = U(s).

**Lemma 5.5.** Let s be a vertex outside S, s != p.

(a) U(s) n V(s) contains no inner index. If s is in N(p), then U(s) n V(s) is empty. If s is a word, then
    |U(s) n V(s)| <= 1. In particular U(s) != V(s) when d(s) >= 2.

(b) Suppose that every vertex outside S u {p} has d <= 2. Then for every pair {i, j} of distinct indices, the
    number of vertices s of X_2 \ {p} with U(s) = {i, j} is exactly need(i, j) (see (4.7)); every vertex of
    X_2 \ {p} is counted for exactly one pair; and the sum of need over all pairs is |X_2 \ {p}|.

*Proof.* (a) Let i be in U(s) n V(s): s ~ x_i and s ~ y_i. If i is inner, s is adjacent to both ends of a mate edge
of N(p) and s != p, against Lemma 2.1 (c). So i is outer. Applying sigma, sigma s ~ y_i and sigma s ~ x_i: x_i and
y_i are common neighbours of s and sigma s. If s is in N(p), the only common neighbour of s and sigma s is p
(Lemma 2.1 (c)): impossible, so U(s) n V(s) is empty. If s is a word, N(s) n N(sigma s) has exactly two elements,
so at most one index i has {x_i, y_i} contained in it. If d(s) >= 2 and U(s) = V(s), then |U(s) n V(s)| >= 2.

(b) The vertices x_i and x_j have exactly 2 - [x_i ~ x_j] common neighbours, so exactly need(i, j) of them are
outside S u {p}. A vertex outside S u {p} adjacent to x_i and x_j has d >= 2, hence d = 2 by the hypothesis: it is
in X_2 \ {p} and its neighbours in S+ are exactly x_i and x_j. Conversely a vertex s of X_2 \ {p} has exactly two
neighbours in S+ and is a common neighbour of them outside S u {p}. QED

The hypothesis of (b) holds in case III (Lemma 5.3), in case II (Lemma 8.3 below) and in case I when n_3 = 0.


## 6. The tests used by the computations

A computation of sections 7, 8 and 9 enumerates the possible induced subgraphs of G on certain vertex sets and
discards those that violate a necessary condition. Three kinds of necessary conditions are used: budgets, the two
PSD matrices, and (at a few nodes, section 10.3) the rank bound. **Both PSD matrices of 6.1 are used.**

### 6.1 Two positive-semidefinite matrices

    M1 = 9 (3I - A) + J = 27 I - 9 A + J,          M2 = 11 (4I + A) - 2J = 44 I + 11 A - 2 J.

**Lemma 6.1.** M1 = 63 E_{-4} and M2 = 77 E_3. Both are PSD, M1 has rank 44 and M2 has rank 54. For every vertex set
Y the principal submatrices M1[Y] and M2[Y] are PSD.

*Proof.* (Identical to T18_PROOF, Lemma 6.1.) M1 and M2 are polynomials in A and J, so they act as scalars on the
three eigenspaces. On the all-ones vector (A = 14, J = 99): M1 = 27 - 126 + 99 = 0 and M2 = 44 + 154 - 198 = 0. On
V_3 (A = 3, J = 0): M1 = 27 - 27 = 0 and M2 = 44 + 33 = 77. On V_{-4} (A = -4, J = 0): M1 = 27 + 36 = 63 and
M2 = 44 - 44 = 0. A principal submatrix of a PSD matrix is PSD. QED

M1[Y] and M2[Y] depend only on the induced subgraph of G on Y: with A_Y its adjacency matrix,
M1[Y] = 27 I - 9 A_Y + J and M2[Y] = 44 I + 11 A_Y - 2J (I and J of size |Y|).

A **PSD violation** on Y is an integer vector x indexed by Y with x^T M1[Y] x < 0 or x^T M2[Y] x < 0. Checking a
given violation is one integer computation. Since M1[Y] and M2[Y] have integer entries, a PSD violation on Y exists
if and only if M1[Y] or M2[Y] is not PSD (a real vector with negative quadratic form can be replaced by a rational
vector close to it, and then multiplied by a common denominator). So "there is no PSD violation on Y" and "M1[Y] and
M2[Y] are both PSD" are the same statement about the graph on Y, and it does not depend on any program.

### 6.2 The common-neighbour budget

**Lemma 6.2.** Let Y be a vertex set and let H' be a graph on Y all of whose edges are edges of G (a spanning
subgraph of the induced subgraph G[Y]). Then for any two distinct vertices u, v of Y,

    |N_H'(u) n N_H'(v)| <= 2 - [u ~ v in H'].

*Proof.* (Identical to T18_PROOF, Lemma 6.2.) N_H'(u) n N_H'(v) is contained in N(u) n N(v), which has 1 element if
u ~ v in G and 2 otherwise. If u ~ v in H' then u ~ v in G and the bound is 1. If u not~ v in H' the bound 2 holds
in both cases. QED

A pair u, v violating the inequality is a **budget violation**. The point of allowing a spanning subgraph is that a
partially specified graph (some adjacencies not yet decided and provisionally absent) may be rejected by a budget
violation: adding edges can only increase the numbers of common neighbours and decrease the bound. A PSD violation,
on the contrary, is meaningful only on a vertex set all of whose adjacencies are decided.

### 6.3 Determined sets, and what a computation proves

Let D be some data extracted from a configuration (for instance the types of the vertices of N(p)). A vertex set Y
(described in terms of the configuration, e.g. "S u N[p]") is **determined by D** if the induced subgraph G[Y],
with the names of its vertices, can be written down from D alone. For every determined set used below, the text
gives a table that says, for every pair of classes of vertices of Y, whether the adjacency is a parameter in D or
is forced, and by which lemma.

The computations have the following form. A finite list of candidate data D is defined: all values of the
parameters that satisfy the forced numbers named in the text. For a candidate D, write G_D for the graph on Y built
from D.

**Definition (survivor).** A candidate D is a **survivor** if G_D has no budget violation and the matrices M1[Y]
and M2[Y] of G_D are both PSD. This is a property of D alone: it does not refer to a program, to the order of the
tests or to a numerical threshold. The data of a configuration satisfy the forced numbers, which are proved in the
text, and pass both tests by Lemmas 6.1 and 6.2. Hence:

    the data D of any configuration are a survivor.                                              (6.1)

*What a program does.* A program **rejects** a candidate D only when it has an exact witness that D cannot be the
data of a configuration. There are four kinds of witnesses:

- a budget violation on G_D, or on a partial graph, i.e. a graph on a subset of Y all of whose edges are edges of
  G_D (section 6.2);
- a PSD violation on Y, or on a subset of Y all of whose adjacencies are decided;
- a forced number proved in the text that fails (in the searches below these are upper bounds, "caps", on numbers of
  neighbours, and the multiplicities of the units);
- a violation of the rank bound of section 6.4 on a sigma-invariant subset of Y all of whose adjacencies are
  decided.

The candidates that a program does not reject form its **kept list**. The data of a configuration admit no witness
of any of the four kinds: a principal submatrix of a PSD matrix is PSD (Lemma 6.1), a graph all of whose edges are
edges of G has no budget violation (Lemma 6.2), the forced numbers are proved, and so is the rank bound (Proposition
6.4). Hence, for every program whose rejections are exact:

    the data D of any configuration belong to the kept list.                                     (6.2)

(6.2) rests on exact rejections only, and it is all that the exclusions of this text use: every exclusion below
has the form "the kept list of the last step is empty".

*Exactness of the rejections.* According to their sources (for the parts read for this text; see section 10.4,
item 2) and their headers, in all the enumeration programs a rejection is exact: a budget violation is an integer
count (the fast engines select with floating-point products of 0/1 matrices and recount every budget rejection in
64-bit integers); a PSD violation is an integer vector whose quadratic form is evaluated in Python integers, or,
when no such vector is found, an exact rational elimination; a rank is an exact integer rank (python-flint). The
quadratic form is often evaluated on a "sigma-block": for x = sum c_v (e_v - e_{sigma v}) one has
x^T M1 x = 18 c^T G_odd c with the matrix G_odd of Proposition 6.4, and x^T M2 x = 22 c^T (7I - G_odd) c (because
M1 + (9/11) M2 = 63 I - (7/11) J and J x = 0); for x = sum c_v (e_v + e_{sigma v}) + c_p e_p the form is that of
the "even block". A block vector with negative form is a PSD violation on the vertices.

*"Kept" decisions.* A candidate for which no violation is found is kept; this "kept" rests on a floating-point
eigenvalue or Schur complement (tolerances of about 10^-7 to 10^-9) and **is not a proof of positive semidefiniteness
and is never used as one**: keeping too much can only make the kept list larger, which is harmless by (6.2).

Consequently, in this text:

- a number of survivors would be a property of the mathematics; **no list of this text has been verified to consist
  of survivors exactly**, except the nine support structures on S u {p} (remark at the end of section 4.10) and,
  according to round 1, the two base graphs of case III on S u N[p] (both matrices exactly PSD, of rank 26 and 25);
- every count of "bases", "nodes", "kept" or "candidates" printed in sections 7, 8, 9 is a count of one named
  program. Counts of nodes depend, in addition, on the rule by which the program chooses the next unit (section
  6.5). Two programs can be compared on such counts only if they treat the same units in the same order; this is
  how the second programs are built (section 0.1).

### 6.4 The rank bound  [C9; T18_PROOF 6.4]

Let P be the permutation matrix of sigma (P e_x = e_{sigma x}). P is symmetric, P^2 = I, and P commutes with A
(sigma is an automorphism) and with J.

**Lemma 6.3.** trace(P E_{-4}) = 0 and trace(P E_3) = 0. Hence sigma acts on V_{-4} with the eigenvalues +1 and -1,
each with multiplicity 22, and on V_3 with the eigenvalues +1 and -1, each with multiplicity 27.

*Proof.* (Identical to T18_PROOF, Lemma 6.3.) trace P is the number of fixed vertices, 1. trace(PA) =
sum_x A_{x, sigma x} is the number of vertices x with x ~ sigma x, which is |N(p)| = 14 by Lemma 2.1 (a).
trace(PJ) = 99. By Lemma 6.1,

    trace(P E_{-4}) = (27 * 1 - 9 * 14 + 99) / 63 = 0,       trace(P E_3) = (44 * 1 + 11 * 14 - 2 * 99) / 77 = 0.

P preserves V_{-4} and V_3 and has eigenvalues +-1 there; the trace is the difference of the two multiplicities,
and their sums are 44 and 54. QED

**Proposition 6.4 (rank bound).** Let Y be a sigma-invariant vertex set, and let R be a set containing exactly one
vertex of each orbit {x, sigma x} contained in Y (x != p).

(a) (odd part) The |R| x |R| integer matrix

        G_odd = 3 I - A[R,R] + A[R, sigma R]     (entry (x,y): 3 [x = y] - [x ~ y] + [x ~ sigma y])

    has rank at most 22. In particular, if |R| >= 23 then every 23 x 23 principal minor of G_odd is 0.

(b) (even part) Let the vectors g_x = e_x + e_{sigma x} (x in R), together with g_p = e_p if p is in Y, be the
    "even generators". The matrix G_even with entries g^T M1 g' has rank at most 22. Explicitly, for x != y in R:
    G_even(x,y) = 4 - 18 ([x ~ y] + [x ~ sigma y]),  G_even(x,x) = 58 - 18 [x ~ sigma x],
    G_even(p,x) = 2 - 18 [p ~ x],  G_even(p,p) = 28.

*Proof.* (Identical to T18_PROOF, Proposition 6.4.) (a) For x in R put u_x = e_x - e_{sigma x}. Since M1 commutes
with P, M1(sigma x, sigma y) = M1(x, y) and M1(sigma x, y) = M1(x, sigma y), so

    u_x^T M1 u_y = 2 (M1(x,y) - M1(x, sigma y)) = 2 (27 [x = y] - 9 [x ~ y] + 9 [x ~ sigma y]) = 18 G_odd(x,y)

(the terms +1 coming from J cancel, and x = sigma y does not happen for x, y in R). On the other hand
M1 = 63 E_{-4} and E_{-4} is a symmetric idempotent, so u_x^T M1 u_y = 63 (E_{-4} u_x) . (E_{-4} u_y): the matrix
18 G_odd is 63 times the Gram matrix of the vectors E_{-4} u_x. These vectors lie in V_{-4} and satisfy
P E_{-4} u_x = E_{-4} P u_x = - E_{-4} u_x, so they lie in the (-1)-eigenspace of sigma on V_{-4}, which has
dimension 22 by Lemma 6.3. A Gram matrix of vectors in a space of dimension 22 has rank at most 22.

(b) The same computation with g_x: g^T M1 g' = 63 (E_{-4} g) . (E_{-4} g'), and the vectors E_{-4} g lie in the
(+1)-eigenspace of sigma on V_{-4}, of dimension 22. The explicit entries are 2 (M1(x,y) + M1(x, sigma y)),
M1(p,x) + M1(p, sigma x) and M1(p,p). QED

G_odd and G_even depend only on the induced subgraph on Y and on sigma. So for a sigma-invariant determined set Y,
"rank G_odd > 22" or "rank G_even > 22" is a contradiction, checked by one exact integer rank. Positive
semidefiniteness does not see this condition: G_odd can be positive definite. The proposition is a general fact
about G and sigma. It is stated and proved in T18_PROOF as well, but it does not depend on the theorem T18.

### 6.5 The search over units  [round 2, section B; SPEC_N3, section 4]

All the enumerations of sections 7, 8 and 9 have the same form. It is described here once, with the proof that it
is exhaustive.

**Setting.** In a configuration let

- Y_0 be a sigma-invariant vertex set containing S u {p} (the **base**);
- F be a sigma-invariant set of vertices outside Y_0, each of which has exactly two neighbours in S+ (the **free
  vertices**); F is a union of n orbits, since p is in Y_0;
- for every pair {i, j} of indices, m(i, j) be the number of vertices f of F with U(f) = {i, j}; these numbers are
  assumed to be known from the graph on Y_0 (they are the multiplicities of the units, minus the units realised
  inside Y_0).

A **state of level t** is a labelled graph with an involution, on |Y_0| + 2t vertices: the graph on Y_0, and t
further orbits {f, sigma f}, each with the adjacency of f to all the earlier vertices (that of sigma f follows by
the involution). The adjacency between two different added orbits {f, sigma f} and {f', sigma f'} is invariant
under the involution, so it is one of four **patterns**: the two bits [f ~ f'] (then sigma f ~ sigma f') and
[f ~ sigma f'] (then sigma f ~ f'). A state is **true** if it is the induced subgraph of G on Y_0 and t orbits of
F, with the involution sigma.

A **model** is a finite list of conditions on a state that are proved to hold for every true state (for instance:
"f is adjacent to exactly two vertices of N(p), in two different pairs", "V(f) != U(f)", "f has at most 5
neighbours among the other added orbits").

A **search** is a tree of states. Its root is the graph on Y_0. Let N be a node of level t < n. A unit {i, j} is
chosen, by any rule, among the pairs for which fewer than m(i, j) of the 2t added vertices have U = {i, j}. The
**candidates** of N are all the states of level t + 1 obtained from N by adding one orbit {f, sigma f} with
U(f) = {i, j} and satisfying the model. The children of N are the candidates that are not rejected, a rejection
being an exact witness in the sense of section 6.3.

**Lemma 6.5.** Suppose that the graph on Y_0 of a configuration is the root of a search. Then, whatever the rule
that chooses the units, the search has a true node at every level t <= n. In particular it has a node of level n.

*Proof.* By induction on t. The root is true. Let N be a true node of level t < n. Such a pair {i, j} exists: the
2t added vertices are fewer than the 2n = sum of m(i, j) vertices of F. Let {i, j} be the unit chosen at N. Exactly
m(i, j) vertices of F have U = {i, j}, and fewer than m(i, j) of them are among the added vertices of N; so some
vertex f of F with U(f) = {i, j} is not in N, and neither is sigma f. The induced subgraph of G on the vertices of
N together with f and sigma f is a state of level t + 1; it is true, so it satisfies the model, and it is a
candidate of N. It admits no exact witness (section 6.3). So it is a child of N. QED

Three remarks.

- *The rule is free.* The first programs choose the unit by a floating-point look-ahead (the unit with the fewest
  candidates that seem to survive). Nothing is concluded from this look-ahead: at the chosen unit all candidates are
  generated, and each is kept or rejected exactly.
- *Tests on parts of a candidate.* A candidate may be rejected by a witness on a subset of its vertices on which all
  adjacencies are decided, for instance the base and the new orbit alone, or the base and two orbits with their
  pattern (the "single" and "pair" tests of the engines). These are witnesses of the kinds of section 6.3.
- *Unit of the mate.* For the new orbit {f, sigma f}, U(sigma f) = V(f) (section 5.5). So the orbit uses one
  realisation of the unit U(f) and one of the unit V(f), and a true candidate has V(f) != U(f) (Lemma 5.5 (a)) and
  V(f) among the units that still have a realisation outside N and different from f. The engines enumerate V(f)
  among these units only.

By Lemma 6.5 and (6.2): **if a search whose rejections are exact has no node of level n, then no configuration has
the root as its graph on Y_0.**


## 7. Case III (k = 4): the configurations III.0 and III.1

In this section the configuration is in case III. By Corollary 4.13 the ten orbits of the support are labelled so
that the graph on S u {p} is III.0 or III.1: the inner indices are K = {0, 1, 2, 3}, and the outer indices 4..9 are
the 2-subsets kappa(j) of K (section 4.10).

### 7.1 The model  [A9; round 2, case III]

**Lemma 7.1.**

(a) X_4 = {p}; X_3 is empty; X_0 is the set of the six inactive inner vertices (three mate edges); |X_2| = 24,
    |X_1| = 48; every vertex of X_1 u X_2 is a word.

(b) Let s be in X_2 and r(s) = |U(s) n K| + |V(s) n K|, the number of neighbours of s among the eight active inner
    vertices. Then s not~ p, s not~ sigma s, r(s) <= 2, and s has exactly 2 - r(s) neighbours in X_0; if there are
    two, they are not mates. Moreover s has exactly 2 - r(s) neighbours in X_2.

(c) Every vertex of X_0 has exactly 4 neighbours in X_2. Its other neighbours are p, its mate and 8 vertices of X_1.

(d) For every pair {i, j} of indices, exactly need(i, j) vertices s of X_2 have U(s) = {i, j} (the units of III.0,
    resp. III.1, in section 4.10; 24 in all). For s in X_2: V(s) = U(sigma s), V(s) != U(s), |U(s) n V(s)| <= 1 and
    U(s) n V(s) contains no inner index.

*Proof.* (a) is Lemma 5.3 (III). (b) s is a word by (a), so s not~ p and s not~ sigma s (Lemma 2.1 (a)), and s has
exactly two neighbours in N(p), in two different orbits (Corollaries 2.2, 2.3). N(p) consists of the eight active
inner vertices x_c, y_c (c in K) and of X_0. The neighbours of s among the former are the x_c with c in U(s) and the
y_c with c in V(s): r(s) of them. So the other 2 - r(s) are in X_0, in different orbits. By (5.3) with d = 2 and
q = 0: a_0(s) - a_2(s) - 2 a_3(s) - 3 a_4(s) = 0; a_3(s) = 0 because X_3 is empty and a_4(s) = [s ~ p] = 0. So
a_2(s) = a_0(s) = 2 - r(s).

(c) Let u be in X_0. By Lemma 2.1 (b) its neighbours in N[p] are p and its mate. So a_0(u) = 1 (the mate; the other
vertices of X_0 are inner) and a_4(u) = 1 (p); a_3(u) = 0. By (5.3) with d = 0, q = 0:
1 - a_2(u) - 3 = -6, so a_2(u) = 4. By (5.2), a_1(u) + 2 * 4 + 4 * 1 = 20, so a_1(u) = 8.

(d) By (a) every vertex outside S u {p} has d <= 2, so Lemma 5.5 (b) applies; X_2 does not contain p. The rest is
section 5.5 and Lemma 5.5 (a). QED

### 7.2 The determined sets and the search

    Y_0 = S u N[p] = S u {p} u X_0      (20 + 1 + 6 = 27 vertices).

The free vertices are F = X_2 (24 vertices, n = 12 orbits), with the multiplicities m(i, j) = need(i, j).

**Lemma 7.2.** Y_0 is determined by the support structure (III.0 or III.1). A state of level t (section 6.5) is
determined by the support structure and, for each added orbit {s, sigma s}: the sets U(s), V(s), the set
N0(s) = N(s) n X_0, and one pattern to each earlier orbit. Every adjacency is given by the following list.

| pair of classes | adjacency | reason |
|---|---|---|
| S u {p} with S u {p} | the support structure | Corollary 4.13 |
| X_0 with p | all adjacent | X_0 is contained in N(p) |
| X_0 with X_0 | the three mate edges only | Lemma 2.1 (b) |
| X_0 with S | none | Lemma 5.3 (III) (d = 0) |
| s with S+, with S- | x_i for i in U(s), y_l for l in V(s) | parameters U(s), V(s) |
| s with p | none | Lemma 7.1 (b) |
| s with sigma s | not adjacent | Lemma 7.1 (b) |
| s with X_0 | exactly N0(s) | parameter N0(s) |
| sigma s with anything | the images under sigma: U and V exchanged, N0 replaced by sigma N0 | sigma is an automorphism |
| two different added orbits | one of the four patterns | parameter |

The **model** (conditions satisfied by every true state):

- (T1) U(s) is the unit chosen at the node; V(s) is a unit different from U(s) (Lemma 7.1 (d));
- (T2) r(s) = |U(s) n K| + |V(s) n K| <= 2; N0(s) has exactly 2 - r(s) elements, not two mates (Lemma 7.1 (b));
- (T3) s has at most 2 - r(s) neighbours among the other added orbits (Lemma 7.1 (b));
- (T4) every vertex of X_0 has at most 4 neighbours among the added vertices (Lemma 7.1 (c));
- (T5) at level 12 the numbers of (T3) and (T4) are exactly 2 - r(s) and 4.

*Proof.* The table is a restatement of the lemmas quoted. In a true state the added vertices are vertices of X_2,
so the numbers of Lemma 7.1 (b), (c), which count neighbours in the whole of X_2, are upper bounds for the
neighbours among the added vertices, and are attained when all 12 orbits are added. QED

**Symmetry.** Let H_0 be the group of the 3! * 2^3 = 48 permutations of the six names of the vertices of X_0 that
permute the three mate pairs and commute with the exchange of mates. By the table, the vertices of X_0 have the
same neighbours in Y_0 up to these permutations (p and the mate), so every element of H_0, extended by the identity
on S u {p}, is an automorphism of the graph on Y_0 commuting with the involution. The programs use it as follows: at
a node N let H_N be the subgroup of the elements of H_0 that fix the set N0(s') of every added orbit of N (as a
set in the runs of III.1; pointwise in the runs of III.0, which gives a smaller subgroup). A candidate is omitted if
the sorted list of its N0(s) is not the lexicographically smallest among its images under H_N.

**Lemma 7.3.** With this rule, Lemma 6.5 holds in the following form: if a configuration has the support structure
III.0 (resp. III.1), then the search with root the graph on Y_0 has a node of every level t <= 12.

*Proof.* The names of the six vertices of X_0 are not fixed by the configuration: any naming compatible with the
mate pairs makes the root true. We show by induction on t that there are a node N of level t and a naming of X_0
for which N is true. Let N and the naming be given, t < 12, and let f be as in the proof of Lemma 6.5. Choose g in
H_N such that g(N0(f)) is lexicographically smallest, and rename the vertices of X_0 by g. An element of H_N fixes
the set N0(s') of every added vertex s' of N, and, as it commutes with the exchange of mates, also the set
sigma N0(s') of its mate; it fixes S u {p}. So it is an automorphism of the labelled graph N that moves only
vertices of X_0, and N is still true for the new naming. For the new naming the candidate defined by f has the
smallest N0, so it is not omitted; as in Lemma 6.5 it is a child of N, and it is true. QED

### 7.3 The two computations

> **Computation 7.4 (III.0).** For the support structure III.0, the search of section 7.2 (root: the 27 vertices of
> Y_0; model (T1)-(T5); symmetry rule with the pointwise stabilisers; rejections by budget violations and PSD
> violations) has no node of level 10. With the rule of the first program for the choice of the units, the numbers
> of nodes are:
>
> | level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
> |---|---|---|---|---|---|---|---|---|---|---|---|
> | nodes | 1 | 13 | 116 | 881 | 7,109 | 30,102 | 54,327 | 31,126 | 6,086 | 243 | 0 |
>
> Total: 130,004 nodes and 4,094,709 candidates, of which 671,315 are rejected by a budget violation, 3,293,391 by a
> PSD violation, and 130,003 are kept. No rejection by the rank bound. No time-out.

> **Computation 7.5 (III.1).** For the support structure III.1, the same search (symmetry rule with the setwise
> stabilisers; rejections by budget violations, PSD violations and the rank bound) has no node of level 10. With
> the rule of the program for the choice of the units, the numbers of nodes are:
>
> | level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
> |---|---|---|---|---|---|---|---|---|---|---|---|
> | nodes | 1 | 13 | 208 | 2,156 | 21,165 | 132,172 | 492,124 | 764,789 | 211,921 | 4,315 | 0 |
>
> Total: 1,628,864 nodes and 75,949,406 candidates, of which 17,487,147 are rejected by a budget violation and
> 56,833,395 by a PSD violation. Exactly one candidate of a node of level 9 passes the budget and PSD tests; it is
> rejected by the rank bound: on its 47 vertices (23 orbits and p) the 23 x 23 matrix G_odd of Proposition 6.4 has
> rank 23. No time-out.
>
> **Status at the time of writing: one program.**

**Proposition 7.6 (hand statements + Computations 4.12, 7.4, 7.5).** There is no configuration in case III.

*Proof.* Suppose there is one. By Corollary 4.13 its graph on S u {p} is III.0 or III.1 after a suitable labelling.
By Lemma 7.2 its graph on Y_0 is the root of the search, and by Lemma 7.3 the search has a node of level 12. This
contradicts Computation 7.4 or 7.5, by (6.2). QED

Status: hand part (Lemmas 4.1, 4.9, 5.1, 5.3-5.5, 7.1-7.3, Corollary 5.2, Proposition 6.4) plus Computations 4.12,
7.4, 7.5. For III.1 the conclusion depends on Proposition 6.4 (one node) and on a single program.

### 7.4 Programs, counts, and what the second implementation is

All the programs of this section are in `lemma/t20_R2`; the model (the base graph, the units, the group H_0 and the
options (T2)) is in the file `cases.py` (class `CaseIII`), which **all of them import**. `check_model.py` compares
the base graphs and the units of `cases.py` with a construction from the edge lists of section 4.10 typed in by
hand, and finds them identical for III.0, III.1 and IIa.0 (`check_model.out`).

*III.0.*

- `eng3.py` and `eng4.py` (the first engine and a faster version of it; `eng4.py` writes the "plan": one line per
  node with the unit chosen, the number of candidates and the number kept). Each was run in 3 parts with split parameter 3
  (the nodes of level 3 are split: the 7,109 tasks are their children, of level 4): the numbers of the table and all the other counters of Computation 7.4 are identical for the two
  (`summary_III0.out`). In these engines the choice of the unit uses a floating-point look-ahead; at the chosen unit
  all candidates are generated; a budget rejection is recounted in 64-bit integers and a PSD rejection is an integer
  vector on a sigma-block evaluated in Python integers (or exact rational elimination).
- `engv.py` (the verifier): the candidate generation is rewritten, the budgets are recounted on the whole graph for
  every candidate, and the PSD test uses full eigen-decompositions of the sigma-blocks, with an integer vector (or
  an exact rational elimination) for every rejection. It reads the unit of every node from the plan of `eng4.py`
  and stops with an error if its number of kept candidates differs from the plan. Result: the plan is followed to
  the end ("lines left unread 0, nodes with a different candidate count 0"), the same kept count at all 130,004
  nodes, no node of level 10 (`v_III0_{0,1,2}of3.out`).
- 15,000 saved PSD certificates were re-checked by `check_certs.py`, a pure-Python checker that imports no engine
  (it re-checks that the stored graph is symmetric, that the stored involution is an automorphism, that the first
  21 vertices carry III.0, and the value of the quadratic form): 0 invalid; 11,136 on the odd block of M1, 3,812 on
  the even block of M1, 49 and 3 on the blocks of M2 (`check_certs_III0.out`).

The working report counts this as "two implementations", with the remark "tests independent; the model file
`cases.py` is shared". That is the precise status: two engines whose candidate generation and tests were written
separately, one model file, and the second engine follows the units chosen by the first.

*III.1.* `eng5.py` (a third version of the first engine, same model `cases.CaseIII`), run in 8 parts with split parameter
3 (the nodes of level 3 are split): 21,165 tasks, of level 4, in every part, the same hash of the ordered task list in the 8 parts, no time-out
(`lemma/t20_III1/summary_III1.out`, `e5_III1_{0..7}of8.json`). Counters by level, for the record:

    nodes            1, 13, 208, 2156, 21165, 132172, 492124, 764789, 211921, 4315, 0
    candidates       13, 212, 2939, 46605, 610429, 5386769, 25315888, 36337095, 8134160, 115296
    rejected budget  0, 0, 453, 6631, 112662, 1068846, 5747479, 8759108, 1763545, 28423
    rejected PSD     0, 4, 330, 18809, 365595, 3825799, 18803620, 27366066, 6366300, 86872
    kept             13, 208, 2156, 21165, 132172, 492124, 764789, 211921, 4315, 1
    rejected rank    0, 0, 0, 0, 0, 0, 0, 0, 0, 1

The per-part logs, the plan files and the sampled certificates of this run are not in git (they are in the session
scratchpad, according to `lemma/t20_III1/README.md`). According to the same file and to `T20_BOARD.md` (line C1),
the independent verifier (`engv.py` / `engv2.py`, to be validated on III.0 first) over the whole tree, with a
separate examination of the node rejected by rank, **is running at the time of writing**; nothing of it is used
here.

*Counters that depend on the program.* "Candidates" are counted after the cached single and pair tests of the
engine, and the numbers of nodes depend on the units chosen. They are reproducible by a program that follows the
same plan, not by an arbitrary second program.

*Remark (not used).* For III.0 and III.1 both matrices are exactly PSD on Y_0, with ranks 26 (M1) and 25 (M2)
(round 1, B3): nothing is excluded on the base alone.


## 8. Case II (k = 2): the configuration IIa.0

In this section the configuration is in case II. By Corollary 4.13 the orbits of the support are labelled so that
the graph on S u {p} is IIa.0: the inner indices are 0 and 1, the plus edge is {2, 3}, and the four plus ends are
x_2, x_3, y_2, y_3. They are words, so q(p) = 0, and for a vertex z outside S

    q(z) = |U(z) n {2, 3}| + |V(z) n {2, 3}|.

### 8.1 The hand lemmas  [II.1 - II.6]

**Lemma 8.1 [II.1].** n_0 + n_3 = 4, X_4 is empty, d(p) = 2 and q(p) = 0.

*Proof.* Lemma 5.3 (II), and the lines above. QED

**Lemma 8.2 [II.2].** Every vertex outside S has d <= 3.

*Proof.* Corollary 5.2 gives d <= 4 and Lemma 5.3 (II) gives X_4 empty. (Directly, as in the working report: if
d(z) >= 4, then (5.3) gives a_0(z) >= 3d - 6 >= 6, but a_0(z) <= n_0 <= 4.) QED

**Lemma 8.3 [II.3].** X_3 is empty. Hence n_0 = 4, n_1 = 54, n_2 = 21, and every vertex outside S has d in
{0, 1, 2}.

*Proof.* Suppose d(z) = 3. Then z != p (d(p) = 2), so sigma z != z, and d(sigma z) = 3: n_3 >= 2 and
n_0 = 4 - n_3 <= 2. But (5.3) gives a_0(z) = a_2(z) + 2 a_3(z) + 3 * 3 + q(z) - 6 >= 3, and a_0(z) <= n_0.
Contradiction. The sizes are those of Lemma 5.3 (II) with n_3 = 0. QED

**Lemma 8.4 [II.4].** No vertex of N(p) \ S has d = 2 or d = 0. Consequently:

- the ten vertices of N(p) \ S all have d = 1; call their set W (five mate pairs), so N(p) = {x_0, y_0, x_1, y_1} u W;
- a_2(p) = a_0(p) = 0;
- X_0 consists of four words, forming two word orbits.

*Proof.* (5.3) at p (d = 2, q = 0, a_3 = a_4 = 0) gives a_0(p) = a_2(p).

Suppose f is in N(p) \ S with d(f) = 2. Its mate sigma f has d = 2 and is adjacent to f, and p is in X_2 and is
adjacent to f. So a_2(f) >= 2, and (5.3) at f (d = 2) gives a_0(f) = a_2(f) + q(f) >= 2. The neighbours of f in
N[p] are p and sigma f (Lemma 2.1 (b)), both in X_2; so the neighbours of f in X_0 are words, and f is adjacent to
at most one vertex of each word orbit (Corollary 2.3 (b)). Hence X_0 contains at least two word orbits; as
|X_0| = 4 (Lemma 8.3), X_0 is exactly two word orbits. Then no vertex of X_0 is in N(p), i.e. a_0(p) = 0. But
a_2(p) >= 2 (f and sigma f). This contradicts a_0(p) = a_2(p).

So no vertex of N(p) \ S has d = 2, i.e. a_2(p) = 0, hence a_0(p) = 0: no vertex of N(p) \ S has d = 0. By Lemma 8.3
the ten vertices of N(p) \ S have d in {0, 1, 2}, so d = 1. X_0 has four elements, none in N[p] (p is in X_2); it
is sigma-invariant without fixed vertex, so it is two orbits, and they are word orbits. QED

**Lemma 8.5 [II.5] (the types of W).** Let w be in W. Then w has exactly one neighbour x_i in S+ and one neighbour
y_l in S-; write (i ; l) for its type. Then:

(a) sigma w has type (l ; i); i and l are outer indices; i != l;
(b) two different mate pairs of W never have the same unordered type {i, l};
(c) for every outer index i, the number of mate pairs of W whose unordered type contains i is 2 - r_i, where r_i is
    the number of neighbours of x_i among x_0, y_0, x_1, y_1.

So the five unordered types are the edges of a simple graph on the eight outer indices {2, ..., 9} in which the
index i has degree 2 - r_i. For IIa.0: r_i = 0 for i = 2, 4 and r_i = 1 for i = 3, 5, 6, 7, 8, 9; so the degrees are
(2, 1, 2, 1, 1, 1, 1, 1) for i = 2, ..., 9, and there are exactly **180** such graphs.

*Proof.* d(w) = 1 by Lemma 8.4. (a) The type of sigma w is given by section 5.5. Inside N(p) the only neighbour of
w is its mate (Lemma 2.1 (b)), which is not in S; so w is adjacent to none of x_0, y_0, x_1, y_1, and i, l are outer.
i != l by Lemma 5.5 (a) (w is in N(p), so U(w) n V(w) is empty). (b) Suppose two different mate pairs have the same
unordered type; replacing one vertex by its mate, there are w, w' in different mate pairs, both of type (i ; l).
They are distinct vertices of N(p) that are not mates, so they are non-adjacent, and they have the three common
neighbours p, x_i, y_l. Contradiction. (c) x_i is a word: it has exactly two neighbours in N(p) (Corollary 2.2),
r_i of them among x_0, y_0, x_1, y_1 and 2 - r_i in W. In a mate pair of W of unordered type {i, l}, exactly one
vertex is adjacent to x_i (the one of type (i ; l)); a mate pair whose type does not contain i has no neighbour
of x_i. So 2 - r_i mate pairs have i in their type.

For IIa.0 (section 4.10): x_i ~ y_0 exactly for i = 7, 8, 9 (minus edges 07, 08, 09) and x_i ~ y_1 exactly for
i = 3, 5, 6 (minus edges 13, 15, 16); no x_i with i outer is adjacent to x_0 or x_1 (the only plus edge is {2,3}).
So r_i = 1 for i = 3, 5, 6, 7, 8, 9 and r_i = 0 for i = 2, 4. Count of the graphs with degree 2 at the vertices 2
and 4 and degree 1 at the six others: if 2 ~ 4, choose the other neighbour of 2 (6 ways), the other neighbour of 4
(5 ways) and a perfect matching of the four remaining vertices (3 ways): 90; if 2 not~ 4, choose the two neighbours
of 2 (15 ways), the two neighbours of 4 among the four remaining vertices (6 ways), and join the last two: 90. QED

**Lemma 8.6 [II.6] (the vertices of X_2 other than p).** Let s be in X_2, s != p, and
r(s) = |U(s) n {0,1}| + |V(s) n {0,1}|, the number of neighbours of s among x_0, y_0, x_1, y_1.

(a) s is a word: s not~ p and s not~ sigma s. It has exactly 2 - r(s) neighbours in W, never two mates; in
    particular r(s) <= 2.
(b) a_2(s) = a_0(s) - q(s) and a_0(s) <= 3. So s has at most 3 - q(s) neighbours in X_2 \ {p}; in particular
    q(s) <= 3.
(c) A vertex w of W has a_0(w) <= 2 and a_2(w) = a_0(w) + 3 - q(w); p is one of its neighbours in X_2. So w has at
    most 4 - q(w) neighbours in X_2 \ {p}.
(d) For every pair {i, j} of indices exactly need(i, j) vertices s of X_2 \ {p} have U(s) = {i, j} (the units of
    IIa.0 in section 4.10; 20 in all). V(s) = U(sigma s), V(s) != U(s), |U(s) n V(s)| <= 1.

*Proof.* (a) By Lemma 8.4 the vertices of N(p) \ S have d = 1, and the vertices of N(p) n S are not outside S; so s
is not in N(p), and s != p: s is a word. It has exactly two neighbours in N(p) = {x_0, y_0, x_1, y_1} u W, in two
different orbits (Corollaries 2.2, 2.3). (b) (5.3) with d = 2 and a_3 = a_4 = 0 (Lemmas 8.2, 8.3):
a_0(s) - a_2(s) = q(s). By Lemma 5.4 (a), 2 a_0(s) - 2 <= |X_0 \ {p}| = 4, so a_0(s) <= 3. s not~ p, so all its
neighbours in X_2 are in X_2 \ {p}. (c) X_0 is two word orbits (Lemma 8.4) and w is adjacent to at most one vertex
of each (Corollary 2.3 (b)): a_0(w) <= 2. (5.3) with d = 1: a_0(w) - a_2(w) = 3 + q(w) - 6. w ~ p and p is in X_2.
(d) By Lemmas 8.2 and 8.3 every vertex outside S has d <= 2, so Lemma 5.5 (b) applies; the sum of need is
|X_2 \ {p}| = 20. The rest is section 5.5 and Lemma 5.5 (a). QED

### 8.2 The determined sets and the search

    Y_0 = S u N[p] = S u {p} u W      (20 + 1 + 10 = 31 vertices).

The free vertices are F = X_2 \ {p} (20 vertices, n = 10 orbits), with m(i, j) = need(i, j). The vertices of X_0
are **not** in the vertex sets of this section.

**Lemma 8.7.** Y_0 is determined by IIa.0 and by the five unordered types of the mate pairs of W (a graph as in
Lemma 8.5; its edges may be named in any order, the vertices of W having no other names). A state of level t is
determined by these data and, for each added orbit {s, sigma s}: U(s), V(s), the set N_W(s) = N(s) n W and one
pattern to each earlier orbit.

| pair of classes | adjacency | reason |
|---|---|---|
| S u {p} with S u {p} | IIa.0 | Corollary 4.13 |
| W with p | all adjacent | W is contained in N(p) |
| W with W | the five mate edges only | Lemma 2.1 (b) |
| W with x_0, y_0, x_1, y_1 | none | Lemma 2.1 (b) |
| W with the rest of S | the pair of type {i, l}: one vertex adjacent to x_i and y_l only, its mate to x_l and y_i only | parameter (Lemma 8.5) |
| s with S+, with S- | x_i for i in U(s), y_l for l in V(s) | parameters |
| s with p; s with sigma s | not adjacent | Lemma 8.6 (a) |
| s with W | exactly N_W(s) | parameter |
| sigma s with anything | the images under sigma | sigma is an automorphism |
| two different added orbits | one of the four patterns | parameter |

The **model**:

- (P1) U(s) is the unit chosen at the node; V(s) is a unit different from U(s) (Lemma 8.6 (d));
- (P2) r(s) <= 2 and q(s) <= 3; N_W(s) has exactly 2 - r(s) elements, not two mates (Lemma 8.6 (a), (b));
- (P3) s has at most 3 - q(s) neighbours among the other added orbits (Lemma 8.6 (b));
- (P4) every w of W has at most 4 - q(w) neighbours among the added vertices (Lemma 8.6 (c)).

(P3) and (P4) are upper bounds only; no equality is required at level 10 (the exact numbers involve X_0, which is
not in the vertex set).

*Proof.* Restatement of the lemmas quoted; the bounds of Lemma 8.6 (b), (c) count neighbours in the whole of
X_2 \ {p}, hence bound the neighbours among the added vertices. QED

### 8.3 The two computations

> **Computation 8.8 (step 1: the neighbourhood of p).** Of the 180 graphs of Lemma 8.5, giving 180 graphs on the 31
> vertices of Y_0: 63 have a budget violation, 30 have no budget violation and a PSD violation, and 87 are kept.

> **Computation 8.9 (step 2).** For each of the 87 graphs on Y_0 kept in step 1, the search of section 8.2 (model
> (P1)-(P4); no symmetry rule; rejections by budget violations and PSD violations) has no node of level 8. With the
> rule of the first program for the choice of the units, the numbers of nodes, summed over the 87 roots, are:
>
> | level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
> |---|---|---|---|---|---|---|---|---|---|
> | nodes | 87 | 520 | 3,148 | 11,451 | 18,324 | 10,279 | 1,640 | 48 | 0 |
>
> Total: 45,497 nodes and 898,945 candidates, of which 201,918 are rejected by a budget violation, 651,617 by a PSD
> violation, and 45,410 are kept. No rejection by the rank bound. No time-out.

**Proposition 8.10 (hand statements + Computations 4.12, 8.8, 8.9).** There is no configuration in case II.

*Proof.* Suppose there is one. By Corollary 4.13 its graph on S u {p} is IIa.0 after a suitable labelling. By
Lemmas 8.4, 8.5 and 8.7 its graph on Y_0 is one of the 180 graphs, and by (6.2) it is one of the 87 kept in step 1.
By Lemmas 8.6, 8.7 and 6.5 the search with this root has a node of level 10, which contradicts Computation 8.9. QED

Status: hand part (Lemmas 4.6, 4.7, 5.1, 5.3-5.5, 8.1-8.7, Corollary 5.2) plus Computations 4.12, 8.8, 8.9. The rank
bound is not used.

### 8.4 Programs and counts

All in `lemma/t20_R2`.

*Step 1.* `iia_w.py` (which uses the tool file `r2c.py`) lists the 180 graphs, builds the 31-vertex graphs and
tests them; it writes the 87 kept type sets to `iia_w.json`. `iian_verify.py types` does the same with its own
code: "type sets with the right degrees: 180; rejected by budgets 63, by PSD (exact) 30, kept 87; identical to the
list of the first program: True; certificates: integer vector 30, exact elimination 0" (`iian_verify_types.out`).
So the 93 rejections are exact in two programs, and the two kept lists are the same list. Whether each of the 87
graphs is exactly PSD on Y_0 has not been recorded; it is not needed.

*Step 2.*

- First program: `eng5.py` with the model `cases.CaseIIaN` (base S u N[p], caps only), one run per type set
  (`run_iian.py`), each run writing its plan; totals in `summary_IIa.out`: the table of Computation 8.9; deepest
  level with a node: 7; between 1 and 3,054 nodes per type set; 2 type sets have no child of the root.
- Second program: `iian_verify.py follow`. It imports nothing from the engines or from `cases.py`: it rebuilds
  IIa.0 from the structure file, builds its own base, its own units, its own candidates (with pair budgets as the
  only pre-filter) and its own tests (budget recount on the whole graph; integer vector for every PSD rejection). It
  reads the unit of every node from the plan of the first program and stops if its number of kept candidates
  differs. Result (`iian_verify_0_30.out`, `_30_38`, `_38_44`, `_44_66`, `_66_87`): 3,147 + 12,275 + 1,729 + 13,073 +
  15,273 = 45,497 nodes, the same kept count at every node (45,410 in all), no plan line left, 0 complete. Its
  candidates are more numerous than those of the first program (1,067,833, of which 230,683 rejected by budgets and
  791,740 by a PSD violation, all by integer vectors), because its pre-filter is weaker; its outputs show these
  differences as "candidate-count mismatches", which are not disagreements. (The sums of this paragraph were made
  for this text from the five output files.)
- 6,358 saved certificates of the first program (those of 5 of the 87 type sets; the certificate files of the other
  82, about 1.6 GB, were deleted to save disk) were re-checked by `check_certs.py`: 0 invalid
  (`check_certs_IIa.out`).

The two programs of step 2 share no code. They share: the structure file `structures_III_IIb_IIa.json` (the graph
IIa.0), the list `iia_w.json` (which the second program compares with its own list in step 1), the hand model
(Lemmas 8.4-8.6), and the units chosen by the first program.


## 9. Case I (k = 0): the graphs I.0, ..., I.5

In this section the configuration is in case I. By Lemma 4.10 and Corollary 4.13: S+ = {x_i} and S- = {y_i} are
independent, S is disjoint from N[p], x_i ~ y_j if and only if i ~_B j, and B is one of the six graphs I.0, ..., I.5
of section 4.10. There is no plus end, so q(z) = 0 for every z. By Lemma 5.3 (I): X_4 is empty, p is in X_0, n_3 is
even, and

    n_0 = 9 - n_3,     n_1 = 40 + 3 n_3,     n_2 = 30 - 3 n_3.

For z outside S with d = d(z), (5.2) and (5.3) read

    a_1 + 2 a_2 + 3 a_3 = 20 - 5d,        a_0 = a_2 + 2 a_3 + 3d - 6,                               (9.1)

that is:

| class of z | a_0 | a_1 |
|---|---|---|
| X_0 | a_2 + 2 a_3 - 6 | 20 - 2 a_2 - 3 a_3 |
| X_1 | a_2 + 2 a_3 - 3 | 15 - 2 a_2 - 3 a_3 |
| X_2 | a_2 + 2 a_3 | 10 - 2 a_2 - 3 a_3 |
| X_3 | a_2 + 2 a_3 + 3 | 5 - 2 a_2 - 3 a_3 |

N(p) is disjoint from S and consists of the 7 orbits {a_c, b_c} (Lemma 2.1), called the **pairs** of N(p). Put
delta_c = d(a_c) = d(b_c).

Sections 9.1 and 9.2 reduce the case to four sub-cases (two profiles, n_3 = 0 or 2). Sections 9.3 to 9.6 contain the
other hand statements established so far; it is said in each place whether the enumeration of section 9.A uses
them. Section 9.A treats n_3 = 0, section 9.B treats n_3 = 2.

### 9.1 No inner vertex with d = 3; n_3 is 0 or 2  [I.1, I.2]

**Lemma 9.1 [I.1].** No vertex of N(p) has d = 3. So delta_c is in {0, 1, 2} for every c, and every vertex of X_3
is a word.

*Proof.* Suppose z is in N(p) with d(z) = 3. Its mate sigma z is in X_3 and is adjacent to z, so a_3(z) >= 1, and
(9.1) gives a_0(z) = a_2(z) + 2 a_3(z) + 3 >= 5. By Lemma 5.4 (b), 2 a_0(z) - 1 <= |X_0|, so |X_0| >= 9. But
|X_0| = 9 - n_3 and n_3 >= 2 (z and sigma z). Contradiction. Every vertex outside S has d <= 3 (Corollary 5.2 and
X_4 empty), so delta_c <= 2. A vertex of X_3 is not in N(p), and it is not p (d(p) = 0). QED

**Lemma 9.2 [I.2].** n_3 is 0 or 2.

*Proof.* Let z be in X_3 and T(z) = N(z) n X_0. By (9.1), |T(z)| = a_0(z) >= 3. z is a word (Lemma 9.1), so by
Lemma 5.4 (a), 2 |T(z)| - 2 <= |X_0 \ {p}| = 8 - n_3. Hence n_3 <= 4, and n_3 is even. Suppose n_3 = 4.

Then |X_0 \ {p}| = 4 and |T(z)| = 3 for every z in X_3. The set X_0 \ {p} is sigma-invariant without fixed vertex,
so it consists of two orbits O_1, O_2, and T(z), a 3-subset of it that does not contain p, contains one of the two
orbits entirely and one vertex of the other. If T(z) contains the orbit {u, sigma u}, then z is adjacent to u and
to sigma u, so by Corollary 2.3 (c) this is a word orbit and N(u) n N(sigma u) = {z, sigma z}. X_3 consists of two
orbits {z, sigma z} and {z', sigma z'}. T(sigma z) = sigma T(z) contains the same full orbit as T(z). T(z) and T(z')
cannot contain the same full orbit {u, sigma u}: N(u) n N(sigma u) would be both {z, sigma z} and {z', sigma z'}.
So, with suitable names,

    T(z) = O_1 u {v} with v in O_2,          T(z') = O_2 u {u'} with u' in O_1,
    T(sigma z) = O_1 u {sigma v},            T(sigma z') = O_2 u {sigma u'}.

The four vertices z, sigma z, z', sigma z' are distinct, and:

- z and z' have the common neighbours v and u';
- z and sigma z' have the common neighbours v and sigma u';
- z and sigma z have the two vertices of O_1 as common neighbours; z' and sigma z' the two vertices of O_2.

Two distinct vertices have at most two common neighbours, so none of these four pairs has a common neighbour in S.
Let (U ; V) be the type of z and (U' ; V') that of z'; the four sets have 3 elements, sigma z has the type (V ; U)
and sigma z' the type (V' ; U'). An index in U n U' gives a common neighbour x_i of z and z'; in V n V', a common
neighbour y_l of z and z'; in U n V' or in V n U', a common neighbour of z and sigma z'; in U n V, a common
neighbour of z and sigma z; in U' n V', a common neighbour of z' and sigma z'. So U, V, U', V' are four pairwise
disjoint 3-subsets of {0, ..., 9}: 12 > 10. Contradiction. QED

### 9.2 The profiles; profile (5,0,2) is impossible  [A10, I.3]

For j = 0, 1, 2 let h_j be the number of c with delta_c = j. So N(p) n X_j consists of h_j pairs. Notation used in
the whole section:

    A_p = N(p) n X_2   (2 h_2 vertices, the "A-pairs"),      W = N(p) n X_1   (2 h_1 vertices, the "W-pairs"),
    Z_p = N(p) n X_0   (2 h_0 vertices, the "Z-pairs"),      X_2' = X_2 \ A_p,
    R_0 = X_0 \ N[p] = X_0 \ ({p} u Z_p)     (the words of X_0).

**Lemma 9.3.** sum_c delta_c = 10. Hence

    h_2 = 3 + h_0,      h_1 = 4 - 2 h_0,                                                          (9.2)

and (h_2, h_1, h_0) is one of (3,4,0), (4,2,1), (5,0,2). This triple is the **profile** of the configuration.

*Proof.* Each of the 10 vertices of S+ is a word, so it has exactly 2 neighbours in N(p) (Corollary 2.2). Hence
sum over v in N(p) of d+(v) = 20, i.e. 2 sum_c delta_c = 20. So h_1 + 2 h_2 = 10 and h_0 + h_1 + h_2 = 7 (Lemma
9.1), which gives (9.2), and h_1 >= 0 forces h_0 in {0, 1, 2}. QED

**Proposition 9.4 [I.3].** Profile (5,0,2) is impossible, for the six graphs and for n_3 = 0 and n_3 = 2.

*Proof.* Let the profile be (5,0,2), and let u_1, sigma u_1, u_2, sigma u_2 be the four vertices of Z_p. For each of
them, (9.1) gives a_2 = a_0 + 6 - 2 a_3, and a_0 >= 2 (p and the mate); so a_2(u) >= 8 - 2 a_3(u). Inside N(p) a
vertex is adjacent only to its mate (Lemma 2.1 (b)), so the neighbours of these four vertices in X_2 lie in
X_2' = X_2 \ A_p, a set of 30 - 3 n_3 - 10 elements.

The four sets N(u) n X_2 have small intersections: two mates have only p as a common neighbour (Lemma 2.1 (c)), so
the sets of u_1 and sigma u_1 are disjoint, and so are those of u_2 and sigma u_2; a vertex of {u_1, sigma u_1} and a
vertex of {u_2, sigma u_2} are non-adjacent and have p as a common neighbour, hence at most one common neighbour in
X_2. There are four such pairs. So the union of the four sets has at least (sum of a_2 over the four vertices) - 4
elements.

If n_3 = 0, then a_3 = 0 and the union has at least 32 - 4 = 28 elements; but |X_2'| = 20.
If n_3 = 2, let X_3 = {z, sigma z}. A vertex other than p is not adjacent to both u_1 and sigma u_1 (Lemma 2.1 (c)),
so z has at most one neighbour in each of the two pairs, and so has sigma z: the sum of a_3 over the four vertices
is at most 4. Hence the union has at least 32 - 8 - 4 = 20 elements; but |X_2'| = 14. QED

So two profiles remain, (3,4,0) and (4,2,1), each with n_3 = 0 or n_3 = 2.

### 9.3 General statements on the types (both values of n_3)  [C1, C2, C3, C4]

Lemmas 9.5, 9.6 and 9.8 are used by the enumerations. Lemma 9.7 is used only as vocabulary, in Lemmas 9.11, 9.12.

**Lemma 9.5 [C1, H0].** Let x be a vertex of S. Then x has 4 neighbours in S and 10 outside S, none of them in X_0,
and

    (number of neighbours of x in X_2) + 2 (number of neighbours of x in X_3) = 6.                (9.3)

If n_3 = 0, x has exactly 6 neighbours in X_2 and 4 in X_1.

*Proof.* Let x be in S+ (apply sigma for S-). It has 4 neighbours in S, all in S- (Lemma 4.10), hence 10 outside S,
each with d >= 1. Count the pairs (w, s) with s in S+ \ {x}, w ~ x and w ~ s: each of the 9 vertices s is
non-adjacent to x, so the count is 18. A neighbour w of x in S- has 3 neighbours in S+ other than x; a neighbour w
outside S has d(w) - 1. So 18 = 12 + sum over the 10 outside neighbours w of (d(w) - 1), and d(w) is 1, 2 or 3. QED

**Lemma 9.6 [C2].**

(a) For all indices i, l (i = l allowed) the vertices x_i and y_l have exactly 2 - [i ~_B l] common neighbours, and
    all of them are outside S. Equivalently: exactly 2 - [i ~_B l] vertices s outside S have i in U(s) and l in
    V(s).

(b) For every s outside S: every index of U(s) has at most one B-neighbour in V(s), and every index of V(s) has at
    most one B-neighbour in U(s).

(c) For every s outside S, s != p: U(s) n V(s) is empty if s is in N(p), and has at most one element if s is a word.

(d) If s is outside S and i != j are in U(s), then {i, j} is a deficient pair of B (codeg_B(i,j) <= 1).

(e) If n_3 = 0: for every pair {i, j}, exactly need(i, j) = 2 - codeg_B(i, j) vertices s of X_2 have U(s) = {i, j}
    (30 in all; the units of section 4.10), and V(s) = U(sigma s) != U(s).

*Proof.* (a) x_i and y_l are distinct, and adjacent if and only if i ~_B l (for i = l they are not adjacent, by
Lemma 4.10 (c)). So they have 2 - [i ~_B l] common neighbours, none of which is in S (Lemma 4.10). (b) Let i be in
U(s). For l in V(s) n B(i) the vertex y_l is adjacent to s and to x_i: it is a common neighbour of the adjacent
pair s, x_i, which has only one. The second half is the same with the adjacent pair s, y_l. (c) is Lemma 5.5 (a)
(there is no inner index). (d) s is a common neighbour of x_i and x_j outside S, and they have codeg_B(i,j) common
neighbours in S and 2 in all. (e) Lemma 5.5 (b): if n_3 = 0 every vertex outside S has d <= 2, and p is not in
X_2. QED

**Lemma 9.7 [C3] (slots).** Let w, w' be vertices of N(p) in two different pairs. They have exactly two common
neighbours: p, and a second one, written slot(w, w'), which is a word. The map {w, w'} -> slot(w, w') is a
bijection from the 84 sets {w, w'} of this kind onto the 84 words, and sigma slot(w, w') = slot(sigma w, sigma w').
For two different pairs c, c' of N(p) (a **cell**), the four words slot(w, w'), w in pair c, w' in pair c', form
two word orbits; every word orbit lies in exactly one cell. The 12 word-neighbours of a vertex w of N(p) are the
words slot(w, w'), w' outside the pair of w.

*Proof.* w and w' are not mates, so they are non-adjacent (Lemma 2.1 (b)) and have exactly two common neighbours.
p is one. The other is not in N(p): a vertex of N(p) is adjacent, inside N(p), only to its mate, and it cannot be
the mate of both. So it is a word. Conversely a word has exactly two neighbours in N(p), in two different pairs
(Corollaries 2.2, 2.3), so it is slot(w, w') for exactly one set {w, w'}. There are C(14,2) - 7 = 84 such sets and
99 - 15 = 84 words. sigma maps common neighbours of w, w' to common neighbours of sigma w, sigma w'. A cell contains
the four sets {a_c, a_c'}, {b_c, b_c'}, {a_c, b_c'}, {b_c, a_c'}, exchanged two by two by sigma. A vertex w of N(p)
has the neighbours p, sigma w and 12 words; each of these words has w as one of its two neighbours in N(p). QED

**Lemma 9.8 [C4] (the types of the pairs of N(p)).** Let {w, sigma w} be a pair of N(p), with delta = d(w).

(a) If delta = 2 (an A-pair): the type of w is (U ; V) with U, V two disjoint 2-sets, and that of sigma w is
    (V ; U). U and V are deficient pairs of B; every index of U has at most one B-neighbour in V, and every index of
    V at most one B-neighbour in U. The unordered pair {U, V} is called the type of the pair.
    If delta = 1 (a W-pair): the type of w is (i ; l) with i != l, that of sigma w is (l ; i); the unordered pair
    {i, l} is the type of the pair.
    If delta = 0 (a Z-pair): w and sigma w have no neighbour in S.

(b) Every index 0..9 lies in exactly two of the seven sets attached to the pairs: U u V for an A-pair, {i, l} for a
    W-pair, the empty set for a Z-pair.

(c) Two vertices of N(p) in two different pairs have at most one common neighbour in S.

(d) In particular no two pairs of N(p) have the same type.

*Proof.* (a) U(w) n V(w) is empty by Lemma 9.6 (c); the types of the mates are exchanged (section 5.5); U and V are
deficient pairs by Lemma 9.6 (d), applied to w and to sigma w; the condition on B-neighbours is Lemma 9.6 (b).
(b) x_i is a word: it has exactly two neighbours in N(p), in two different pairs. In the pair {w, sigma w}, w ~ x_i
iff i is in U(w), and sigma w ~ x_i iff i is in V(w); as U(w) n V(w) is empty, the pair contains a neighbour of x_i
iff i is in U(w) u V(w), and then exactly one. (c) Two such vertices are non-adjacent and have p as a common
neighbour. (d) Two pairs with the same type would contain two vertices with the same type, i.e. with 4 (A-pairs)
or 2 (W-pairs) common neighbours in S. QED

### 9.4 n_3 = 0: the neighbourhoods of N(p), the words of X_2, the cells  [C4, C5, C6, C7]

In this subsection n_3 = 0, so (n_0, n_1, n_2) = (9, 40, 30) and a_3 = 0 everywhere. Lemmas 9.9 and 9.10 give the
upper bounds used by the enumeration of section 9.A. Lemmas 9.11 and 9.12 are not used by it.

For w in N(p) let rho(w) = |N(w) n R_0|. R_0 consists of 8 - 2 h_0 words, in 4 - h_0 orbits.

**Lemma 9.9 [C4].** Let n_3 = 0 and w in N(p), delta = d(w). Then rho(sigma w) = rho(w) <= 4 - h_0, and the 12
word-neighbours of w are distributed as follows.

| kind of the pair of w | in S | in R_0 | in X_2' | in X_1 \ W | bound on rho(w) |
|---|---|---|---|---|---|
| A (delta = 2) | 4 | rho | rho | 8 - 2 rho | 4 - h_0 |
| W (delta = 1) | 2 | rho | 4 + rho | 6 - 2 rho | 3 |
| Z (delta = 0) | 0 | rho | 8 + rho | 4 - 2 rho | 2 |

Moreover the sum of rho over the seven pairs (one value per pair) is

    sum_c rho(a_c) = 8 - 2 h_0.                                                                   (9.4)

Consequently a vertex of A_p has at most 4 - h_0 neighbours in X_2', a vertex of W at most 7, a vertex of Z_p at
most 10.

*Proof.* |X_0| = 9 and X_0 = {p} u Z_p u R_0, so |R_0| = 8 - 2 h_0; R_0 is sigma-invariant and consists of words.
rho(sigma w) = rho(w) by sigma, and w is adjacent to at most one vertex of each word orbit (Corollary 2.3 (b)), so
rho(w) <= 4 - h_0. The neighbours of w are p, sigma w, delta vertices of S+, delta of S-, and 12 - 2 delta words
outside S. Its neighbours in X_0 are p, its mate if delta = 0, and rho(w) vertices of R_0; so
a_0(w) = 1 + [delta = 0] + rho(w). By (9.1), a_2(w) = a_0(w) + 6 - 3 delta and a_1(w) = 20 - 5 delta - 2 a_2(w).
The mate is the only neighbour of w in N(p); it is in X_2, X_1 or X_0 according to delta.

- delta = 2: a_2 = 1 + rho, of which the mate; so rho neighbours in X_2'. a_1 = 8 - 2 rho, all words.
- delta = 1: a_2 = 4 + rho, all in X_2'. a_1 = 7 - 2 rho, of which the mate; so 6 - 2 rho >= 0 and rho <= 3.
- delta = 0: a_2 = 8 + rho, all in X_2'. a_1 = 4 - 2 rho >= 0, so rho <= 2.

In each line the four numbers add up to 12. For (9.4): every vertex of R_0 is a word and has exactly two
neighbours in N(p), so sum over the 14 vertices w of N(p) of rho(w) is 2 |R_0| = 16 - 4 h_0, and rho takes the
same value on the two vertices of a pair. QED

**Lemma 9.10 [C5].** Let n_3 = 0 and s in X_2'. Then s is a word, s not~ p, s not~ sigma s; s has exactly two
neighbours in N(p), in two different pairs; and a_2(s) = a_0(s) <= 5. So s has at most 5 - |N(s) n A_p| neighbours
in X_2'.

*Proof.* s is not in N(p) and s != p (d(p) = 0), so s is a word; Corollaries 2.2, 2.3 and Lemma 2.1 (a).
a_2(s) = a_0(s) by (9.1). By Lemma 5.4 (a), 2 a_0(s) - 2 <= |X_0 \ {p}| = 8. QED

The kinds of the cells of Lemma 9.7 are named after the kinds of their two pairs: AA, AW, WW, AZ, WZ. By Lemma 9.7
every orbit of X_2' and every orbit of the support lies in exactly one cell.

**Lemma 9.11 [C6] (profile (4,2,1), n_3 = 0).** There are 6 cells AA, 8 cells AW, 1 cell WW, 4 cells AZ and 2 cells
WZ, and X_2' consists of 11 orbits. Let n_XY be the number of orbits of X_2' in the cells of kind XY, rho_Z the
value of rho on the Z-pair, rho_W the sum of the values of rho on the two W-pairs, and c the number of orbits of
the support in the cell WW. Then c <= 1, rho_Z + rho_W <= 1, and (n_AA, n_AW, n_WW, n_WZ, n_AZ) is one of

    rho_Z = 0, rho_W = 0:   (0,1,2,3,5) with c = 0;   (0,2,1,4,4) with c = 0 or 1;   (1,0,2,4,4) with c = 0;
    rho_Z = 0, rho_W = 1:   (0,1,2,4,4) with c = 0;
    rho_Z = 1, rho_W = 0:   (0,0,2,4,5) with c = 0.

*Proof.* The numbers of cells follow from 4 A-pairs, 2 W-pairs, 1 Z-pair; |X_2'| = 30 - 8 = 22.

For a pair with vertices w, sigma w, the number of orbits of X_2' lying in the cells that contain this pair is the
number of neighbours of w in X_2': an orbit of such a cell is {slot(w, w'), slot(sigma w, sigma w')} for some w',
and exactly its first vertex is adjacent to w. Summing this over the pairs of each kind, with the numbers of
Lemma 9.9 and (9.4) (the sum of rho over the four A-pairs is 6 - rho_Z - rho_W):

    Z-pair:        n_AZ + n_WZ = 8 + rho_Z;
    W-pairs:       n_AW + 2 n_WW + n_WZ = 8 + rho_W;
    A-pairs:       2 n_AA + n_AW + n_AZ = 6 - rho_Z - rho_W.

Also n_WZ <= 4 (the two cells WZ carry four word orbits) and n_WW <= 2 - c (the cell WW carries two word orbits, c
of which are in the support). c <= 1: if the orbits of x_i and of x_j, i != j, were both in the cell WW, the two
W-pairs would both have the type {i, j} (each contains a neighbour of x_i and one of x_j), against Lemma 9.8 (d).

The third equation minus the first gives 2 n_AA + n_AW = n_WZ - 2 - 2 rho_Z - rho_W; substituting n_AW in the
second gives n_WW - n_AA = 5 + rho_W + rho_Z - n_WZ. As n_WW <= 2 and n_AA >= 0: n_WZ >= 3 + rho_Z + rho_W, and
n_WZ <= 4 gives rho_Z + rho_W <= 1.

- rho_Z = rho_W = 0, n_WZ = 3: 2 n_AA + n_AW = 1, so n_AA = 0, n_AW = 1; n_WW = 2 (so c = 0); n_AZ = 5.
- rho_Z = rho_W = 0, n_WZ = 4: 2 n_AA + n_AW = 2 and n_WW = 1 + n_AA; n_AZ = 4. Either (n_AA, n_AW) = (0, 2) and
  n_WW = 1, or (1, 0) and n_WW = 2 (so c = 0).
- rho_W = 1, rho_Z = 0: n_WZ = 4, 2 n_AA + n_AW = 1, so (0, 1); n_WW = 2; n_AZ = 4.
- rho_Z = 1, rho_W = 0: n_WZ = 4, 2 n_AA + n_AW = 0; n_WW = 2; n_AZ = 5. QED

(The same list is printed by the script `hand_cells.py`, output `lemma/t20_R3_I/hand_cells.out`. By Corollary 9.15
below, rho_Z = 0, so the last line does not occur.)

**Lemma 9.12 [C7] (profile (3,4,0), n_3 = 0).** There are 3 cells AA, 12 cells AW and 6 cells WW, and X_2' consists
of 12 orbits. Let rho_A be the sum of the values of rho on the three A-pairs (0 <= rho_A <= 8) and c the number of
orbits of the support in the cells WW. Then

    n_AW = rho_A - 2 n_AA,      n_WW = 12 - rho_A + n_AA >= 4,      n_AA + c <= rho_A.

*Proof.* |X_2'| = 30 - 6 = 24. As in the proof of Lemma 9.11, with Lemma 9.9 and (9.4) (the sum of rho over the
seven pairs is 8, so over the four W-pairs it is 8 - rho_A):

    A-pairs:   2 n_AA + n_AW = rho_A;        W-pairs:   n_AW + 2 n_WW = 16 + (8 - rho_A).

This gives the two equalities; n_WW >= 4 because rho_A <= 8. The six cells WW carry 12 word orbits, of which n_WW
are in X_2' and c in the support: n_WW + c <= 12. QED

### 9.5 n_3 = 0: edge counts and a quadratic identity  [H4, C8]

Not used by the enumeration of section 9.A. Used by Theorem 9.16.

**Lemma 9.13.** Let n_3 = 0. Then

    e(X_0) = e(X_2) - 27,   e(X_0, X_2) = 2 e(X_2),   e(X_0, X_1) = 180 - 4 e(X_2),
    e(X_1, X_2) = 300 - 4 e(X_2),   e(X_1) = 4 e(X_2),                                            (9.5)

and

    sum_{X_0} (a_2 - 6)^2 + sum_{X_1} (a_2 - 4)(a_2 - 5) + sum_{X_2} (a_2 - 2)(a_2 - 3) = 44.       (9.6)

Each of the three sums is >= 0. On X_0, a_2 - 6 = a_0. Hence sum_{X_0} a_0^2 <= 44, e(X_0) <= 9 and
27 <= e(X_2) <= 36.

*Proof.* Sum the lines of the table of (9.1), with a_3 = 0, over each class. On X_2: sum a_2 = 2 e(X_2); sum a_0 =
e(X_0, X_2) = 2 e(X_2); sum a_1 = e(X_1, X_2) = 300 - 4 e(X_2). On X_0: sum a_0 = 2 e(X_0) = e(X_0, X_2) - 6 * 9, so
e(X_0) = e(X_2) - 27; sum a_1 = e(X_0, X_1) = 180 - 2 e(X_0, X_2). On X_1: sum a_1 = 2 e(X_1) =
15 * 40 - 2 e(X_1, X_2) = 8 e(X_2).

For (9.6): the sum over all 99 vertices v of |N(v) n X_2|^2 is the number of triples (v, s, s') with s, s' in X_2 and
v adjacent to both, i.e. the sum over the ordered pairs (s, s') of X_2 of |N(s) n N(s')|: 14 for each of the 30
pairs with s = s', and 2 - [s ~ s'] for each of the 30 * 29 ordered pairs with s != s'. Total
420 + 1740 - 2 e(X_2) = 2160 - 2 e(X_2). Each of the 20 vertices of S has exactly 6 neighbours in X_2 (Lemma 9.5)
and contributes 36. So the sum of a_2^2 over the 79 outside vertices is 1440 - 2 e(X_2). Then, with the sums of
a_2 over the classes (2 e(X_2) on X_0, 300 - 4 e(X_2) on X_1, 2 e(X_2) on X_2) and the sizes 9, 40, 30:

    left side of (9.6) = (1440 - 2 e(X_2)) - 12 * 2 e(X_2) + 36 * 9 - 9 (300 - 4 e(X_2)) + 20 * 40
                          - 5 * 2 e(X_2) + 6 * 30
                       = (1440 + 324 - 2700 + 800 + 180) + (-2 - 24 + 36 - 10) e(X_2) = 44.

For an integer a, (a - 4)(a - 5) >= 0 and (a - 2)(a - 3) >= 0. On X_0, a_0 = a_2 - 6 by (9.1). So
sum_{X_0} a_0^2 <= 44; by the Cauchy-Schwarz inequality on the 9 terms, (2 e(X_0))^2 = (sum_{X_0} a_0)^2 <= 9 * 44 =
396, so 2 e(X_0) <= 19 and e(X_0) <= 9. Finally e(X_0) >= 0 gives e(X_2) >= 27. QED

### 9.6 Profile (4,2,1): the inner pair of X_0 is isolated; n_3 = 0: e(X_0) <= 8  [PROFILE_421, EDGE_BOUND]

These statements come from the Codex session (`lemma/t20_CODEX/PROFILE_421.md`, `EDGE_BOUND.md`); according to those
files each was re-read line by line by the lab session. They are **not used** by the enumeration of section 9.A.
Theorem 9.14 holds for n_3 = 0 and for n_3 = 2 and is meant for section 9.B.

**Theorem 9.14 [PROFILE_421].** Let the profile be (4,2,1) (n_3 = 0 or 2), and let u, u' = sigma u be the two
vertices of Z_p. Then no vertex of R_0 is adjacent to u or to u'. Consequently the subgraph induced on X_0 is the
disjoint union of the triangle {p, u, u'} and of the subgraph induced on R_0, with no edge between them.

*Proof.* R_0 = X_0 \ {p, u, u'} consists of 6 - n_3 words. Let nu = |N(u) n R_0|; by sigma, |N(u') n R_0| = nu.
We must show nu = 0.

The neighbours of u in N[p] are p and u' (Lemma 2.1 (b)), both in X_0. So a_0(u) = 2 + nu, and every neighbour of u
in X_2 is a word: the set A_u = N(u) n X_2 is contained in X_2'. sigma A_u = N(u') n X_2, and A_u n sigma A_u is
empty because the only common neighbour of the mates u, u' is p (Lemma 2.1 (c)). Put beta = a_3(u) = a_3(u')
(beta = 0 if n_3 = 0). By (9.1), |A_u| = a_2(u) = a_0(u) + 6 - 2 a_3(u) = 8 + nu - 2 beta. X_2' has
30 - 3 n_3 - 8 = 22 - 3 n_3 elements. Let

    L = X_2' \ (A_u u sigma A_u),      a sigma-invariant set with   |L| = 22 - 3 n_3 - 2 (8 + nu - 2 beta).

So |L| = 6 - 2 nu if n_3 = 0, and |L| = 4 beta - 2 nu if n_3 = 2.

If n_3 = 2, write X_3 = {z, z'} with z' = sigma z. Then beta <= 1: if u ~ z and u ~ z', then (applying sigma to
u ~ z') u' ~ z, so z is adjacent to both u and u', and z != p, against Lemma 2.1 (c). If beta = 0, then
|L| = -2 nu >= 0 gives nu = 0, as wanted. So for n_3 = 2 we may assume beta = 1, and name z, z' so that u ~ z; then
u' ~ z', u not~ z' and u' not~ z.

Suppose nu > 0 and choose v in R_0 adjacent to u. v is a word. v is not adjacent to u' (Lemma 2.1 (c), v != p).
Put gamma = a_3(v) (gamma = 0 if n_3 = 0; gamma <= 2). a_0(v) >= 1. By (9.1), a_2(v) = a_0(v) + 6 - 2 gamma. Of the
two neighbours of v in N(p), one is u, which is in X_0; so at most one neighbour of v is in A_p, and

    |N(v) n X_2'| >= a_0(v) + 5 - 2 gamma.

The vertices u and v are adjacent, so they have exactly one common neighbour; every vertex of N(v) n A_u is one.
The vertices u' and v are distinct and non-adjacent, so they have exactly two common neighbours; u is one of them
(u ~ u' and u ~ v) and is not in X_2; every vertex of N(v) n sigma A_u is one. So |N(v) n A_u| <= 1 and
|N(v) n sigma A_u| <= 1. If n_3 = 2: when v ~ z, the vertex z is the common neighbour of u and v, so N(v) n A_u is
empty; when v ~ z', the vertex z' is the second common neighbour of u' and v, so N(v) n sigma A_u is empty. In all
cases

    |N(v) n A_u| + |N(v) n sigma A_u| <= 2 - gamma.

The neighbours of v in X_2' are in A_u, in sigma A_u or in L. Hence
a_0(v) + 5 - 2 gamma <= 2 - gamma + |N(v) n L| <= 2 - gamma + |L|.

- n_3 = 0 (gamma = 0, |L| = 6 - 2 nu): a_0(v) + 2 nu <= 3. As a_0(v) >= 1 and nu >= 1, a_0(v) = nu = 1 and all the
  inequalities are equalities: |L| = 4 and v is adjacent to all four vertices of L.
- n_3 = 2, beta = 1 (|L| = 4 - 2 nu): a_0(v) + 2 nu - gamma <= 1. As a_0(v) >= 1, nu >= 1 and gamma <= 2,
  a_0(v) = nu = 1, gamma = 2, and all the inequalities are equalities: |L| = 2 and v is adjacent to both vertices of
  L. Moreover gamma = 2 means v ~ z and v ~ z'.

L is sigma-invariant, so sigma v is adjacent to every vertex of L as well (apply sigma to v ~ l). For n_3 = 2,
sigma v is adjacent to sigma z = z' and to sigma z' = z. So v and sigma v have at least four common neighbours: the
four vertices of L if n_3 = 0, the two vertices of L and z, z' if n_3 = 2. But v is a word, so v and sigma v are
distinct, non-adjacent, and have exactly two common neighbours. Contradiction. Hence nu = 0. QED

The proof uses (9.1), the sizes of the classes, the profile, and lambda = 1, mu = 2. No enumeration.

**Corollary 9.15.** In profile (4,2,1), with u in Z_p and beta = a_3(u) (beta = 0 if n_3 = 0, beta <= 1 if n_3 = 2):

    a_0(u) = 2,      a_2(u) = 8 - 2 beta,      a_1(u) = 4 + beta,      rho(u) = 0.

Every vertex of R_0 has its two neighbours in N(p) in A_p u W. For n_3 = 0, the line "rho_Z = 1" of Lemma 9.11 does
not occur.

*Proof.* nu = 0 in the proof above; a_1(u) = 20 - 2 a_2(u) - 3 a_3(u) by (9.1). QED

**Theorem 9.16 [EDGE_BOUND].** Let n_3 = 0 (profile (3,4,0) or (4,2,1)). Then e(X_0) <= 8 and e(X_2) <= 35.

*Proof.* By Lemma 9.13, e(X_0) <= 9 and e(X_2) = e(X_0) + 27; so it is enough to exclude e(X_0) = 9.

By (9.1) with a_3 = 0: a_2 = a_0 + 6 on X_0, a_2 = a_0 + 3 on X_1, a_2 = a_0 on X_2. Substituting in (9.6):

    sum_{X_0} a_0^2 + sum_{X_1} (a_0 - 1)(a_0 - 2) + sum_{X_2} (a_0 - 2)(a_0 - 3) = 44.

By (9.5), sum_{X_1} a_0 = e(X_0, X_1) = 180 - 4 e(X_2) = 72 - 4 e(X_0). As (a - 1)(a - 2) = a (a - 1) - 2a + 2 and
|X_1| = 40, the middle sum is sum_{X_1} a_0 (a_0 - 1) - 2 (72 - 4 e(X_0)) + 80. Hence

    sum_{X_0} a_0^2 + sum_{X_1} a_0 (a_0 - 1) + sum_{X_2} (a_0 - 2)(a_0 - 3) = 108 - 8 e(X_0).       (9.7)

The second and third sums are >= 0. Suppose e(X_0) = 9. Then sum_{X_0} a_0 = 18, so by the Cauchy-Schwarz inequality
sum_{X_0} a_0^2 >= 18^2 / 9 = 36, which is the whole right side of (9.7). So there is equality everywhere:

    a_0 = 2 on X_0;      a_0 is 0 or 1 on X_1;      a_0 is 2 or 3 on X_2.

Put D_0 = {v in X_1 : a_0(v) = 0}, D_1 = X_1 \ D_0, F_3 = {v in X_2 : a_0(v) = 3}, F_2 = X_2 \ F_3. Then
|D_1| = sum_{X_1} a_0 = 72 - 36 = 36 and |D_0| = 4; sum_{X_2} a_0 = e(X_0, X_2) = 2 e(X_2) = 72, so
2 |F_2| + 3 |F_3| = 72 with |F_2| + |F_3| = 30: |F_3| = 12 and |F_2| = 18.

Consider the integer vector psi = 3 * 1_{X_0} - A 1_{X_0} + 1 (1 = all-ones vector). By (1.1), A 1 = 14 * 1 and
J 1_{X_0} = 9 * 1:

    A psi = 3 A 1_{X_0} - (12 * 1_{X_0} - A 1_{X_0} + 18 * 1) + 14 * 1 = -4 (3 * 1_{X_0} - A 1_{X_0} + 1) = -4 psi.

(No small-norm statement is applied to psi; it only encodes a counting identity at each vertex.) Its value at a
vertex v is 3 [v in X_0] - |N(v) n X_0| + 1, that is

    2 on X_0,    1 on S (no vertex of X_0 has a neighbour in S),    1 on D_0,    0 on D_1,    -2 on F_3,    -1 on F_2.

For a vertex v and a set Y write d_Y(v) = |N(v) n Y|.

Let v be in D_0. It has 2 neighbours in S, none in X_0, and by (9.1) a_2(v) = 3 neighbours in X_2 and
a_1(v) = 15 - 6 = 9 in X_1. The equation (A psi)(v) = -4 psi(v) = -4 reads

    -4 = 2 * 1 + (-2 d_{F_3}(v) - (3 - d_{F_3}(v))) + d_{D_0}(v),      i.e.   d_{F_3}(v) - d_{D_0}(v) = 3.

As d_{F_3}(v) <= 3, we get d_{F_3}(v) = 3 and d_{D_0}(v) = 0. So D_0 is independent and e(D_0, F_3) = 4 * 3 = 12.

Let v be in F_3. It has 4 neighbours in S, 3 in X_0, a_2(v) = 3 in X_2 and a_1(v) = 10 - 6 = 4 in X_1. The equation
(A psi)(v) = -4 psi(v) = 8 reads

    8 = 4 * 1 + 3 * 2 + (-2 d_{F_3}(v) - (3 - d_{F_3}(v))) + d_{D_0}(v),      i.e.   d_{D_0}(v) - d_{F_3}(v) = 1.

So each of the 12 vertices of F_3 has at least one neighbour in D_0; as e(D_0, F_3) = 12, each has exactly one, and
d_{F_3}(v) = 0: F_3 is independent. Then the 3 neighbours in X_2 of each vertex of F_3 are in F_2:
e(F_3, F_2) = 36. Each of the 18 vertices of F_2 has a_2 = a_0 = 2 neighbours in X_2, 36 in all, and these are
already accounted for by the edges between F_3 and F_2. So F_2 is independent.

Now h_2 >= 3, so there is a mate edge {a, sigma a} inside A_p, a subset of X_2. X_0 is sigma-invariant, so
a_0(a) = a_0(sigma a): the two adjacent vertices a, sigma a are both in F_3 or both in F_2, which are independent
sets. Contradiction. QED

*Remark.* Expanding (a_0 - 2)^2 in (9.7) (sum_{X_0} a_0 = 2 e(X_0)) gives the identity

    sum_{X_0} (a_0 - 2)^2 + sum_{X_1} a_0 (a_0 - 1) + sum_{X_2} (a_0 - 2)(a_0 - 3) = 16 (9 - e(X_0)),    (9.8)

and the theorem says that its right side is not 0.

**Corollary 9.17.** Let n_3 = 0.

(a) Profile (3,4,0): p has no neighbour in X_0, e(X_0) is even, so e(X_0) is in {0, 2, 4, 6, 8} and e(X_2) in
    {27, 29, 31, 33, 35}.

(b) Profile (4,2,1): e(X_0) = 3 + e(R_0), e(R_0) is in {0, 2, 4}, e(X_0) <= 7 and e(X_2) <= 34. The graph induced on
    the six vertices of R_0 (three word orbits) is one of: no edge; two disjoint edges and two isolated vertices; a
    4-cycle and two isolated vertices; two disjoint paths with three vertices.

*Proof.* Let Y be a sigma-invariant set of words. sigma permutes the edges inside Y and fixes none of them: an edge
{a, b} with sigma {a, b} = {a, b} would have sigma a = b (no vertex of Y is fixed), i.e. a ~ sigma a, which is false
for a word. So e(Y) is even, and the edges inside Y form edge orbits {a, b}, {sigma a, sigma b} of two disjoint
edges, a and b being in two different orbits of Y.

(a) Z_p is empty, so p has no neighbour in X_0 and the edges inside X_0 are the edges inside R_0 = X_0 \ {p}, a set
of words. With Theorem 9.16 and (9.5). (b) By Theorem 9.14 the edges inside X_0 are the three edges of the triangle
{p, u, u'} and the edges inside R_0. So e(R_0) = e(X_0) - 3 <= 5 and it is even. R_0 consists of three word orbits;
an edge orbit joins two of them, as a matching of two disjoint edges. There are at most two edge orbits. None: no
edge. One: two disjoint edges. Two between the same two orbits: the complete bipartite graph on the two orbits, a
4-cycle. Two between two different pairs of orbits: the two pairs share one orbit, each of whose two vertices gets
one edge of each edge orbit, and the result is two disjoint paths with three vertices. QED


### 9.A  n_3 = 0: the enumeration  [round 3]

In this subsection n_3 = 0. There are twelve cases: B is one of the six graphs, and the profile (h_2, h_1, h_0) is
(3,4,0) or (4,2,1).

#### 9.A.1 The determined sets, and the configurations of N(p)

    Y_0 = S u N[p]      (20 + 1 + 14 = 35 vertices).

The free vertices are F = X_2' = X_2 \ A_p: 30 - 2 h_2 words, i.e. n = 12 orbits for profile (3,4,0) and n = 11
orbits for profile (4,2,1).

**Definition (N-configuration).** Fix B. An **A-type** is an unordered pair {U, V} of disjoint deficient pairs of B
such that every index of U has at most one B-neighbour in V and every index of V at most one B-neighbour in U (the
working reports call it a rectangle). A **W-type** is an unordered pair {i, l} of distinct indices. A type has two
**rows**, the sets of neighbours in S of the two vertices of a pair of that type: x_U u y_V and x_V u y_U for
{U, V}; {x_i, y_l} and {x_l, y_i} for {i, l}. Two types are **compatible** if each row of the first has at most one
vertex in common with each row of the second. An **N-configuration** for the profile (h_2, h_1, h_0) is a set of
h_2 A-types and h_1 W-types, pairwise compatible, such that every index 0..9 lies in exactly two of the sets
U u V, {i, l} of its types. (The h_0 Z-pairs carry no data.)

**Lemma 9.18.** Let n_3 = 0.

(a) The types of the pairs of N(p) form an N-configuration for the profile of the configuration.

(b) Y_0 is determined by B and this N-configuration. A state of level t (section 6.5) is determined by these data
    and, for each added orbit {s, sigma s}: U(s), V(s), the set N_p(s) = N(s) n N(p), and one pattern to each
    earlier orbit. Every adjacency is given by the following list.

| pair of classes | adjacency | reason |
|---|---|---|
| S+ with S+, S- with S- | none | Lemma 4.10 (a) |
| S+ with S- | x_i ~ y_j iff i ~_B j | definition of B |
| p with S | none | Lemma 4.10 (b) |
| p with N(p) | all adjacent | definition |
| N(p) with N(p) | the seven mate edges only | Lemma 2.1 (b) |
| an A-pair of type {U, V} with S | one vertex adjacent to x_U and y_V only, its mate to x_V and y_U only | parameter (Lemma 9.8) |
| a W-pair of type {i, l} with S | one vertex adjacent to x_i and y_l only, its mate to x_l and y_i only | parameter (Lemma 9.8) |
| a Z-pair with S | none | delta = 0 |
| s with S+, with S- | x_i for i in U(s), y_l for l in V(s) | parameters |
| s with p; s with sigma s | not adjacent | Lemma 9.10 |
| s with N(p) | exactly N_p(s) | parameter |
| sigma s with anything | the images under sigma | sigma is an automorphism |
| two different added orbits | one of the four patterns | parameter |

(c) The multiplicities are m(i, j) = need(i, j) - [{i, j} is one of the two deficient pairs of an A-type of the
    N-configuration], where need(i, j) = 2 - codeg_B(i, j). The **model**:

- (K1) U(s) is the unit chosen at the node; V(s) is a unit different from U(s);
- (K2) N_p(s) consists of two vertices of N(p) lying in two different pairs;
- (K3) s has at most 5 - |N_p(s) n A_p| neighbours among the other added orbits;
- (K4) a vertex of A_p has at most 4 - h_0 neighbours among the added vertices, a vertex of W at most 8 - h_0, a
  vertex of Z_p at most min(10, 12 - h_0).

  (K3) and (K4) are upper bounds only; no equality is required at the last level.

(d) Aut(B) acts on the N-configurations (through its action on the indices), and in a configuration with orbit
    graph B one may assume, after relabelling the ten orbits of the support, that the N-configuration is any
    chosen representative of its orbit under Aut(B).

*Proof.* (a) Lemma 9.8: (a) gives the A-types and W-types, (b) the condition on the indices, (c) the compatibility
(two vertices of N(p) in different pairs have at most one common neighbour in S; applied to the four choices of one
vertex in each pair). (b) The table restates the lemmas quoted; the vertices of N(p) have no names other than their
types, and by Lemma 9.8 (d) the types are pairwise different. (c) By Lemma 9.6 (e) exactly need(i, j) vertices of
X_2 have U = {i, j}; those in A_p are the vertices of the A-pairs, and a deficient pair is U(w) for at most one
vertex w of N(p) (Lemma 9.8 (c)). (K1): Lemma 9.6 (e). (K2), (K3): Lemma 9.10 (the neighbours of s in X_2 are in
A_p or in X_2'). (K4): Lemma 9.9, which gives the bounds 4 - h_0, 7 and 10; the bounds written in (K4) are those
used by the programs, and they are weaker or equal (7 <= 8 - h_0 because h_0 <= 1; a Z-pair exists only if
h_0 = 1, and then min(10, 12 - h_0) = 10). (d) A relabelling of the ten orbits by an element g of Aut(B) keeps B
and replaces every type by its image under g. QED

#### 9.A.2 Stage 1

> **Computation 9.19 (stage 1).** For each graph B and each of the two profiles: the number of A-types, the number
> of N-configurations, and the number of their orbits under Aut(B) are in the table below. For one representative
> of each orbit, the graph on the 35 vertices of Y_0 is built and tested (budget violations, PSD violations); the
> representatives that are kept are called the **bases**.
>
> | graph | Aut(B) | A-types | profile | N-configurations | orbits under Aut(B) | bases (kept) |
> |---|---|---|---|---|---|---|
> | I.0 | 16 | 114 | (4,2,1) | 178,768 | 11,322 | 3,022 |
> | I.0 | 16 | 114 | (3,4,0) | 1,229,304 | 77,391 | 11,150 |
> | I.1 | 4 | 161 | (4,2,1) | 722,524 | 180,920 | 56,300 |
> | I.1 | 4 | 161 | (3,4,0) | 3,508,550 | 878,137 | 219,589 |
> | I.2 | 10 | 140 | (4,2,1) | 412,875 | 41,441 | 13,925 |
> | I.2 | 10 | 140 | (3,4,0) | 2,301,905 | 230,609 | 55,573 |
> | I.3 | 4 | 146 | (4,2,1) | 506,294 | 126,655 | 32,022 |
> | I.3 | 4 | 146 | (3,4,0) | 2,663,180 | 666,032 | 112,368 |
> | I.4 | 4 | 144 | (4,2,1) | 495,024 | 124,367 | 21,561 |
> | I.4 | 4 | 144 | (3,4,0) | 2,606,408 | 653,570 | 76,509 |
> | I.5 | 20 | 140 | (4,2,1) | 435,540 | 22,111 | 2,710 |
> | I.5 | 20 | 140 | (3,4,0) | 2,335,670 | 117,846 | 10,676 |
>
> Totals: 17,396,042 N-configurations, 3,130,401 orbits, 615,405 bases.

The numbers of A-types, of N-configurations and of orbits are defined by the mathematics alone. The numbers of
bases are sizes of kept lists (floating-point "kept").

#### 9.A.3 Stage 2

> **Computation 9.20 (stage 2).** For each of the twelve cases and each of its bases, the search of section 6.5 with
> root the graph on Y_0 and the model (K1)-(K4) (no symmetry rule; rejections by budget violations, PSD violations,
> and, in the first program, the rank bound) has no node of level 6. With the rule of the first program for the
> choice of the units, the numbers of nodes, summed over the bases of each case, are:
>
> | case | nodes of level 0, 1, 2, ... | total | deepest level | rejected by the rank bound |
> |---|---|---|---|---|
> | I.0 (4,2,1) | 3022, 13440, 15198, 1843, 8 | 33,511 | 4 | 0 |
> | I.0 (3,4,0) | 11150, 59758, 118717, 56938, 3904, 37 | 250,504 | 5 | 0 |
> | I.1 (4,2,1) | 56300, 275161, 597528, 416434, 60366, 1128 | 1,406,917 | 5 | 2 |
> | I.1 (3,4,0) | 219589, 1360986, 3182403, 2207350, 304035, 5598 | 7,279,961 | 5 | 13 |
> | I.2 (4,2,1) | 13925, 78932, 188838, 125200, 14706, 172 | 421,773 | 5 | 0 |
> | I.2 (3,4,0) | 55573, 377489, 940441, 613858, 65549, 777 | 2,053,687 | 5 | 0 |
> | I.3 (4,2,1) | 32022, 115957, 179576, 89609, 10602, 218 | 427,984 | 5 | 0 |
> | I.3 (3,4,0) | 112368, 507111, 894928, 484271, 56282, 988 | 2,055,948 | 5 | 0 |
> | I.4 (4,2,1) | 21561, 72554, 97281, 41986, 3998, 28 | 237,408 | 5 | 0 |
> | I.4 (3,4,0) | 76509, 340792, 520484, 237910, 24232, 395 | 1,200,322 | 5 | 0 |
> | I.5 (4,2,1) | 2710, 10243, 11541, 2944, 86 | 27,524 | 4 | 0 |
> | I.5 (3,4,0) | 10676, 63403, 150861, 120573, 20662, 467 | 366,642 | 5 | 0 |
>
> Totals: 15,762,181 nodes; no node of level 6 or more (11 or 12 orbits are needed); 15 candidates rejected by the
> rank bound, all for the graph I.1: they are candidates of nodes of level 5 that pass the budget and PSD tests; on
> their 47 vertices (23 orbits and p) the 23 x 23 matrix G_odd of Proposition 6.4 has rank 23. No time-out.

**Proposition 9.21 (hand statements + Computations 4.12, 9.19, 9.20).** There is no configuration in case I with
n_3 = 0.

*Proof.* Suppose there is one. By Corollary 4.13 its orbit graph B is one of I.0, ..., I.5 after a suitable
labelling; by Lemma 9.3 and Proposition 9.4 its profile is (3,4,0) or (4,2,1). By Lemma 9.18 (a), (d) the types of
the pairs of N(p) form an N-configuration, which may be taken to be the representative of its orbit under Aut(B);
by Lemma 9.18 (b) and (6.2) the graph on Y_0 is one of the bases of Computation 9.19. By Lemma 9.18 (c) and Lemma
6.5 the search with this root has a node of level 11 or 12. This contradicts Computation 9.20, by (6.2). QED

Status: hand part (Lemmas 4.10, 5.1, 5.3-5.5, 9.1-9.3, Corollary 5.2, Proposition 9.4, Lemmas 9.5, 9.6, 9.8-9.10,
9.18, and Proposition 6.4 for the graph I.1) plus Computations 4.12, 9.19, 9.20. **For ten of the twelve cases the
two computations rest on one program at the time of writing** (section 9.A.5).

#### 9.A.4 Remarks on the two computations

- The table of Computation 9.20 is `lemma/t20_R3_I/final_table.out`, which the working report says was recomputed
  from the stage-1 files and from the per-base result lines of the runs.
- In stage 1 the tests of the definition of an N-configuration (compatibility, the condition on the A-types) are
  budget conditions on subsets of Y_0; the test on the 35 vertices then adds the whole budget count and the two PSD
  matrices. In the summaries read for this text (the nine cases of the cloud run, file `ALL.txt` of its branch) no
  representative is rejected by a budget violation on the 35 vertices; all the rejections are PSD violations.
- The first program places the vertices of X_2' only. The vertices of R_0 = X_0 \ N[p] and of X_1 \ W are never in
  a vertex set. Every search stops after at most 5 orbits of the 11 or 12, so the global statements of sections
  9.4 to 9.6 (cells, edge counts, Theorems 9.14 and 9.16) could not have been used as tests and are not.
- *The rank nodes.* Without the rank bound, the 15 candidates of I.1 would be nodes of level 6 and the first
  program would have to search below them. The second program does this: it does not reject such a node by rank
  at once, but explores the subtree below it with its own tests and its own choice of the units; according to its
  header, only if such an exploration reached its cap (20,000 nodes or 3,600 CPU seconds) or found a complete
  configuration would it reject the node by an exact rank computation of its own, counted separately. It has been
  run, at the time of the working report, on the single base that holds the two rank nodes of I.1 (4,2,1) (base
  number 12632): in the words of the report, "both nodes die at once (4 candidates, all rejected by budget
  counts)". For the 13 rank nodes of I.1 (3,4,0) nothing but the rank bound is available at the time of writing.

#### 9.A.5 Programs, and the number of programs of each case

All in `lemma/t20_R3_I`; the cloud outputs are on the git branches named below (appendix A.5).

**First program.** Stage 1: `stage1c.py` (with the tool file `r3lib.py`, and `eng.py` for the PSD test), run in
parts and merged by `stage1_merge.py`. It lists the A-types and W-types, generates every N-configuration exactly
once, keeps one representative per orbit under Aut(B) (the smallest image) and checks that the sizes of the orbits
of the representatives add up to the total; each representative is then tested on the 35 vertices (exact budget
count; integer vector for a PSD rejection). Stage 2: `run_stage2.py` with the engine `eng6.py` and the model
`cases6.py` (class `CaseIN6`); according to its header, `eng6.py` is the engine `eng5.py` of sections 7 and 8 "with
lazy single-orbit certificates"; the two give identical counters on 16 bases of I.0 (4,2,1) (`cmp_eng5_I0_421.out`).
The unit is chosen by a look-ahead restricted to three units (option `width=3` in the driver `cloud_case.sh`).
`summary2.py` checks that the parts tile the list of bases, that no base timed out or raised an error, and that all
parts used the same list (hash).

- I.0 (4,2,1), I.0 (3,4,0), I.5 (4,2,1) were run on the laptop ("COMPLETE: True" according to the working report;
  the per-base files are in the session scratchpad, not in git).
- The nine other cases were run on one cloud machine (job `t20_I_rest`, 128 parts per case, first program only).
  The result files of its branch were re-counted on the laptop by `check_cloud.py`, without using the summary
  written by the job: for each of the nine cases, 128 parts of 128 present, every base index exactly once and in
  its part, no time-out, no error, the hash of the list of bases recomputed and equal in every part, 0 complete
  configurations (`cloud_check_t20_I_rest.out`). For six of these cases the list of bases had also been computed on
  the laptop: identical lists (`cloud_vs_laptop_stage1.out`); this is the same program run twice, or an earlier
  version of it, not a second program.

**Second program.** `in_verify.py`. According to its header it imports nothing from the engines, from `cases6.py`,
`r3lib.py` or `stage1c.py`: it has its own model, its own enumeration of the N-configurations (A-types first, then
the W-types as a graph with prescribed degrees), its own computation of Aut(B), its own budget counts and its own
PSD test (integer vector on a sigma-block, or exact rational elimination). Stage 1 is compared with the stage-1
file of the first program. Stage 2 re-traverses the search trees of the first program: the unit of every node is
read from the plan stored with the results, all candidates of that unit are regenerated and tested, and the number
kept must equal the plan's. Below a node that the first program rejected by rank it searches by itself (section
9.A.4).

State of the second program **at the time of the working report** (`lemma/t20_R3_I/REPORT.md`):

| case | stage 1 | stage 2 |
|---|---|---|
| I.0 (4,2,1) | identical numbers and identical list of bases | complete: 3,022 bases, 33,511 nodes, same kept count at every node, 1,144,830 certificates |
| I.5 (4,2,1) | identical numbers and identical list of bases | complete: 2,710 bases, 27,524 nodes, same kept count at every node, 1,088,445 certificates |
| I.0 (3,4,0) | identical numbers and identical list of bases | 372 of the 11,150 bases |
| I.1 (4,2,1) | - | one base (number 12632, the one with the two rank nodes) |
| the eight other cases | - | - |

So **two of the twelve cases have two programs**, and ten have one. According to the working report and to
`T20_BOARD.md` (lines C2, C3, C4) the second program is running on all twelve cases (cloud jobs `t20_Iv_B` to
`t20_Iv_F`, and `t20_I1_340`), and one part of I.1 (4,2,1) has to be re-run with the corrected version of the
verifier; nothing of these runs is used here.

What the two programs share: the hand model (Lemmas 9.6, 9.8, 9.9, 9.10, 9.18), the structure file
`structures_I.json` (the six graphs), and the units chosen by the first program. They share no code.

*Sample of certificates.* `sample_certs_I0_421.jsonl` contains ten rejection records of I.0 (4,2,1), at levels 0
to 4, each with the complete graph concerned and an integer vector of small support; `check_sample.py` re-checks
them from the records alone (the graph is symmetric, sigma is an automorphism, the support is B, no budget
violation, and the value of the quadratic form). The runs themselves were made without saving their certificates
(the driver `cloud_case.sh` passes no certificate option to the first program; the second program only counts its
certificates).


### 9.B  n_3 = 2: the hand lemmas, and the enumeration  [round 3]

Sections 9.B.1 to 9.B.5 are hand lemmas on this sub-case. Section 9.B.6 is the enumeration that excludes it
(Computation 9.29, Proposition 9.30); it uses Lemma 9.22 (a) and Lemma 9.23 only. Sections 9.B.3 to 9.B.5 are kept
for the record and are used by nothing.

Throughout 9.B: n_3 = 2, so (n_0, n_1, n_2) = (7, 46, 24);

    X_3 = {z, z'} with z' = sigma z;     (U ; V) is the type of z (|U| = |V| = 3), and (V ; U) that of z';
    X_0' = X_0 \ {p}   (six vertices, three orbits);     T = N(z) n X_0,   T' = sigma T = N(z') n X_0;
    alpha = a_2(z) = a_2(z');      eps = |U n V|.

From the earlier sections, the following apply to this sub-case as they stand: Lemmas 9.1 to 9.3 and Proposition
9.4 (the profile is (3,4,0) or (4,2,1)), Lemma 9.5 with (9.3), Lemma 9.6 (a)-(d), Lemmas 9.7 and 9.8, Theorem 9.14
and Corollary 9.15. Lemmas 9.6 (e), 9.9 to 9.13, Theorem 9.16 and Corollary 9.17 are statements for n_3 = 0 and do
not apply.

#### 9.B.1 The orbit X_3  [H1]

**Lemma 9.22.**

(a) z is a word; z not~ z' and z not~ p; N(z) n N(z') is one word orbit {w, sigma w}. a_3(z) = 0, T is contained in
    X_0', and (a_0, a_1, a_2)(z) is (3, 5, 0) or (4, 3, 1). In particular alpha is 0 or 1 and |T| = 3 + alpha.

(b) eps <= 1, and exactly one of the following four cases holds.

| case | the orbit N(z) n N(z') | consequences |
|---|---|---|
| (i-S) | {x_i, y_i} for an index i | U n V = {i}; T n T' is empty; alpha = 0; \|T\| = 3 |
| (i-X1) | an orbit of X_1 | U n V is empty; T n T' is empty; alpha = 0; \|T\| = 3 |
| (ii) | an orbit {u, sigma u} of X_0' | U n V is empty; alpha = 0; T = {u, sigma u, v} |
| (iii) | an orbit {u, sigma u} of X_0' | U n V is empty; alpha = 1; T = {u, sigma u, v, v_2}, with v and v_2 in the two other orbits of X_0' |

(c) In cases (ii) and (iii) the orbit {u, sigma u} is a word orbit and N(u) n N(sigma u) = {z, z'}.

(d) In cases (i-S) and (i-X1), T contains exactly one vertex of each of the three orbits of X_0' and T' is the
    complementary set: a_3 = 1 on X_0'. In case (ii): a_3 = 2 on {u, sigma u}, 1 on {v, sigma v}, 0 on the third
    orbit. In case (iii): a_3 = 2 on {u, sigma u} and 1 on the four other vertices.

(e) For x in X_0': a_2(x) = a_0(x) + 6 - 2 a_3(x) and a_1(x) = 8 - 2 a_0(x) + a_3(x). Hence a_0(x) <= 4 if
    a_3(x) <= 1, and a_0(x) <= 5 if a_3(x) = 2. In cases (ii) and (iii), a_0(u) <= 2.

(f) X_0' contains exactly h_0 inner orbits (none for profile (3,4,0), one for profile (4,2,1)); the others are word
    orbits.

*Proof.* (a) z is a word by Lemma 9.1; Lemma 2.1 (a), (d) give z not~ z', z not~ p and the word orbit. The only
other vertex of X_3 is z', so a_3(z) = 0. By (9.1), a_0(z) = a_2(z) + 3 and a_1(z) = 5 - 2 a_2(z). z not~ p, so T is
contained in X_0'. By Lemma 5.4 (a), 2 |T| - 2 <= |X_0'| = 6, so |T| <= 4 and a_2(z) <= 1.

(b) The orbit {w, sigma w} lies in S, in X_0', in X_1 or in X_2 (it is not in X_3, and it does not contain p).

- If it is in S, it is {x_i, y_i} for an index i; z ~ x_i means i in U, and z ~ y_i means i in V. Conversely every
  index of U n V gives the two common neighbours x_i, y_i of z and z' (z' ~ x_i iff i in V, z' ~ y_i iff i in U).
  So eps <= 1, and eps = 1 exactly when the orbit is in S.
- It is not in X_2: z would have two neighbours in X_2, against (a).
- T n T' = N(z) n N(z') n X_0 is sigma-invariant and has no fixed vertex, so it is empty or it is the whole orbit
  {w, sigma w}. If the orbit is in S or in X_1, T n T' is empty, so 2 |T| <= 6: |T| = 3 and alpha = 0. If the
  orbit is {u, sigma u} in X_0', then T n T' = {u, sigma u}; for |T| = 3 this is case (ii); for |T| = 4,
  T = {u, sigma u, v, v_2}, and v, v_2 are not mates (otherwise they would be in T n T' too), so they are in the two
  other orbits: case (iii).

(c) Corollary 2.3 (c), applied to the word z and the orbit {u, sigma u}.

(d) In cases (i-S), (i-X1): T and T' = sigma T are disjoint 3-subsets of the 6-set X_0', so T' is the complement of
T, and T contains no two mates. Cases (ii), (iii): read off T and T' = sigma T.

(e) (9.1) with d = 0: a_2 = a_0 + 6 - 2 a_3 and a_1 = 20 - 2 a_2 - 3 a_3 = 8 - 2 a_0 + a_3 >= 0. In cases (ii),
(iii), u is a word, so u not~ p and u not~ sigma u; and u is adjacent to at most one vertex of each of the two other
orbits of X_0': if u ~ v and u ~ sigma v, then sigma u ~ sigma v and sigma u ~ v, so v would be a common neighbour
of u and sigma u other than z, z', against (c).

(f) The inner vertices of X_0 are those of Z_p. QED

#### 9.B.2 The units and the exact numbers for X_2  [SPEC_N3, section 3]

**Lemma 9.23.**

(a) For every pair {i, j} of distinct indices, the number of vertices s of X_2 with U(s) = {i, j} is exactly

        need_z(i, j) = 2 - codeg_B(i, j) - [i, j in U] - [i, j in V],                              (9.9)

    and the sum of need_z over all pairs is 24. In particular the three pairs inside U and the three pairs inside
    V are deficient pairs of B. For s in X_2: V(s) = U(sigma s) != U(s).

(b) No vertex of X_2 is adjacent to both z and z'; so a_3(s) is 0 or 1 for s in X_2. No vertex of N(p) is adjacent
    to both z and z'.

(c) For s in X_2, with W_s = N(s) n X_0': a_0(s) = [s ~ p] + |W_s| <= 4, a_2(s) = a_0(s) - 2 a_3(s), and
    a_1(s) = 10 - 2 a_2(s) - 3 a_3(s). The number of neighbours of s in X_2 other than its mate is exactly
    |W_s| - 2 a_3(s), whether s is a word or an inner vertex.

(d) p has exactly 2 h_2 neighbours in X_2 (the vertices of A_p); z and z' have alpha neighbours in X_2 each; a
    vertex x of X_0' has exactly a_0(x) + 6 - 2 a_3(x).

(e) A vertex of A_p is adjacent to no vertex of Z_p and to at most one vertex of each word orbit of X_0'. A word
    of X_2 is not adjacent to both vertices of Z_p.

(f) Let w be in N(p), delta = d(w), rho(w) = |N(w) n R_0| and a_3(w) in {0, 1}. Then rho(w) <= 3 - h_0, and the
    number of neighbours of w in X_2' is rho(w) - 2 a_3(w) if delta = 2, 4 + rho(w) - 2 a_3(w) if delta = 1, and
    8 + rho(w) - 2 a_3(w) if delta = 0; in the last case it is also at most (20 - 3 a_3(w)) / 2.

*Proof.* (a) x_i and x_j are non-adjacent and have exactly two common neighbours, codeg_B(i,j) of them in S (Lemma
4.10). A common neighbour outside S has d >= 2, so it is in X_2 or it is z or z'; z is one iff i, j are in U, and z'
iff i, j are in V. The sum over the 45 pairs of 2 - codeg_B is 30 (section 4.10); the three pairs inside U and the
three pairs inside V are six different pairs, because eps <= 1. As need_z >= 0, these six pairs have codeg_B <= 1.
The last statement is section 5.5 and Lemma 5.5 (a).

(b) N(z) n N(z') is an orbit that is not in X_2 (Lemma 9.22 (b)) and is a word orbit (Lemma 9.22 (a)).

(c) The neighbours of s in X_0 are p (iff s is in N(p)) and the vertices of W_s. By Lemma 5.4, 2 a_0(s) - 2 <= 6
if s is a word and 2 a_0(s) - 1 <= 7 if s is in N(p); in both cases a_0(s) <= 4. The two formulas are (9.1) with
d = 2. If s is a word, its mate is not a neighbour and a_2(s) = |W_s| - 2 a_3(s). If s is in N(p), then
a_2(s) = 1 + |W_s| - 2 a_3(s), and its mate, which is in X_2, is one of these neighbours.

(d) The neighbours of p are the vertices of N(p). For z: (a) of Lemma 9.22. For x: Lemma 9.22 (e).

(e) Lemma 2.1 (b), Corollary 2.3 (b) and Lemma 2.1 (c).

(f) |X_0| = 7, so R_0 has 6 - 2 h_0 vertices, in 3 - h_0 word orbits, and rho(w) <= 3 - h_0 by Corollary 2.3 (b).
a_3(w) <= 1 by (b). As in the proof of Lemma 9.9, a_0(w) = 1 + [delta = 0] + rho(w), and by (9.1)
a_2(w) = a_0(w) + 6 - 3 delta - 2 a_3(w); the mate of w is in X_2 iff delta = 2. For delta = 0,
a_1(w) = 20 - 2 a_2(w) - 3 a_3(w) >= 0. QED

*Remark on the bounds of the working files.* `SPEC_N3.md` and NOTES H9 state the bound on a_2(s) in the form
"a_2(s) <= 5 if a_3(s) = 0 and a_2(s) <= 3 if a_3(s) = 1" (from a_1(s) >= 0). The bound of (c), a_0(s) <= 4, i.e.
a_2(s) <= 4 - 2 a_3(s), is stronger; it is the one written in the header of `lemma/t20_R3_I/cases6.py`. Both are
valid. The bounds of (f) are those of the same header.

#### 9.B.3 Profile (4,2,1): the inner pair of X_0  [PROFILE_421, TRIANGLE_REDUCTION]

By Theorem 9.14 (which covers n_3 = 2), in profile (4,2,1) the two vertices u, u' of Z_p have no neighbour in R_0,
and by Corollary 9.15, a_0(u) = 2, a_2(u) = 8 - 2 beta, a_1(u) = 4 + beta with beta = a_3(u) <= 1.

**Lemma 9.24 [TRIANGLE_REDUCTION].** In profile (4,2,1) with n_3 = 2, beta = 1: each of u, u' is adjacent to exactly
one of z, z' (after exchanging the names z, z' if necessary: z ~ u and z' ~ u').

*Proof.* Let Delta = {p, u, u'}, a triangle. A vertex outside Delta has at most one neighbour in Delta: two of them
would be adjacent, and it would be a second common neighbour of this adjacent pair, which already has the third
vertex of Delta. For t in Delta let Gamma_t = N(t) \ Delta (12 vertices); the three sets are disjoint, and their
union Gamma has 36 vertices. A vertex v outside Delta u Gamma is non-adjacent to each t of Delta, so it has exactly
two common neighbours with t; they are neighbours of t, and they are not in Delta (v has no neighbour in Delta); so
v has exactly two neighbours in each Gamma_t, six in Gamma.

No vertex of Gamma is in S (the vertices of Delta are in X_0 and have no neighbour in S), and none is in X_0 (the
neighbours of p in X_0 are u and u'; those of u are p and u', by Theorem 9.14; likewise for u').

Suppose beta = 0. Then z is adjacent to neither u nor u' (a_3(u) = a_3(u') = 0), nor to p. So z is outside
Delta u Gamma and has six neighbours in Gamma. None of them is in S or in X_0, and none is z' (z not~ z'). So
a_1(z) + a_2(z) >= 6. But by (9.1), a_1(z) + a_2(z) = 5 - a_2(z) <= 5. Contradiction. So beta >= 1, and beta <= 1 was
shown in the proof of Theorem 9.14. QED

In the cases of Lemma 9.22 this says: in profile (4,2,1) the inner orbit Z_p of X_0' is not the orbit with a_3 = 0
of case (ii), and it is not the orbit {u, sigma u} of cases (ii), (iii) (which is a word orbit).

#### 9.B.4 The matching in N(z)  [H3]

**Lemma 9.25.** Let R = N(z) n X_1 (5 - 2 alpha vertices), and let e(U, V) be the number of pairs (i, l) with i in
U, l in V and i ~_B l, f the number of edges inside T, and g the number of edges inside R u (N(z) n X_2). Then

    e(U, V) + f - g = 2 + alpha.

*Proof.* Every neighbour v of z has exactly one neighbour inside N(z), namely the unique common neighbour of the
adjacent pair z, v. So N(z) induces a perfect matching on its 14 vertices: the 3 vertices x_i (i in U), the 3
vertices y_l (l in V), the 3 + alpha vertices of T, and the 5 - alpha vertices of R u (N(z) n X_2). The edges inside
x_U u y_V join an x_i to a y_l (S+ and S- are independent): there are e(U, V) of them. The vertices of T have no
neighbour in S. So 6 - 2 e(U, V) vertices of x_U u y_V and 3 + alpha - 2f vertices of T have their partner in
R u (N(z) n X_2), and the other vertices of this set are matched among themselves:

    5 - alpha = (6 - 2 e(U, V)) + (3 + alpha - 2f) + 2g.   QED

#### 9.B.5 Edge counts and a quadratic identity  [H4]

**Lemma 9.26.**

    e(X_0, X_3) = 6 + 2 alpha,   e(X_2, X_3) = 2 alpha,   e(X_1, X_3) = 10 - 4 alpha,
    e(X_0) = e(X_2) + 4 alpha - 15,   e(X_0, X_2) = 2 e(X_2) + 4 alpha,   e(X_1, X_2) = 240 - 4 e(X_2) - 6 alpha,
    e(X_0, X_1) = 122 - 4 e(X_2) - 14 alpha,   e(X_1) = 90 + 4 e(X_2) + 12 alpha,                      (9.10)

and

    sum_{X_0} (a_2 - 5)^2 + sum_{X_1} (a_2 - 3)(a_2 - 4) + sum_{X_2} (a_2 - 1)(a_2 - 2) = 55 - 16 eps.    (9.11)

Each of the three sums is >= 0. On X_0', a_2 - 5 = a_0 + 1 - 2 a_3; at p, (a_2 - 5)^2 = (2 h_2 - 5)^2, which is 1
for profile (3,4,0) and 9 for profile (4,2,1).

*Proof.* By Lemma 9.22 (a), each of z, z' has 3 + alpha neighbours in X_0, alpha in X_2, 5 - 2 alpha in X_1 and none
in X_3: this gives the first line. Summing the lines of the table of (9.1) over the classes: on X_2,
e(X_0, X_2) = sum a_0 = 2 e(X_2) + 2 e(X_2, X_3) and e(X_1, X_2) = sum a_1 = 10 * 24 - 4 e(X_2) - 3 e(X_2, X_3); on
X_0, 2 e(X_0) = sum a_0 = e(X_0, X_2) + 2 e(X_0, X_3) - 6 * 7 and
e(X_0, X_1) = sum a_1 = 20 * 7 - 2 e(X_0, X_2) - 3 e(X_0, X_3); on X_1,
2 e(X_1) = sum a_1 = 15 * 46 - 2 e(X_1, X_2) - 3 e(X_1, X_3).

For (9.11): as in the proof of Lemma 9.13, the sum over all 99 vertices v of |N(v) n X_2|^2 is
24 * 14 + 24 * 23 * 2 - 2 e(X_2) = 1440 - 2 e(X_2). A vertex x_i has [i in U] + [i in V] neighbours in X_3, hence
6 - 2 ([i in U] + [i in V]) neighbours in X_2 by (9.3): 2 for the eps indices of U n V, 4 for the 6 - 2 eps indices
in exactly one of U, V, and 6 for the 4 + eps others; the same holds for y_i. So S contributes
2 (4 eps + 16 (6 - 2 eps) + 36 (4 + eps)) = 480 + 16 eps, and z, z' contribute 2 alpha^2 = 2 alpha. The sum of
a_2^2 over X_0 u X_1 u X_2 is therefore 960 - 2 e(X_2) - 16 eps - 2 alpha. With the sums of a_2 over the classes
(2 e(X_2) + 4 alpha on X_0, 240 - 4 e(X_2) - 6 alpha on X_1, 2 e(X_2) on X_2) and the sizes 7, 46, 24:

    left side of (9.11) = (960 - 2 e(X_2) - 16 eps - 2 alpha) - 10 (2 e(X_2) + 4 alpha) + 25 * 7
                           - 7 (240 - 4 e(X_2) - 6 alpha) + 12 * 46 - 3 * 2 e(X_2) + 2 * 24
                        = (960 + 175 - 1680 + 552 + 48) + (-2 - 20 + 28 - 6) e(X_2) + (-2 - 40 + 42) alpha - 16 eps
                        = 55 - 16 eps.

The products (a - 3)(a - 4) and (a - 1)(a - 2) are >= 0 for an integer a. On X_0', a_2 = a_0 + 6 - 2 a_3 (Lemma
9.22 (e)); a_2(p) = 2 h_2. QED

#### 9.B.6 The enumeration: N(p) and the orbit X_3 in the base  [SPEC_ROUTE_B_N3]

The determined set is the one of section 9.A with the orbit X_3 added:

    Y_z = S u N[p] u {z, z'}      (20 + 1 + 14 + 2 = 37 vertices).

The free vertices are F = X_2' = X_2 \ A_p: 24 - 2 h_2 words, i.e. n = 9 orbits for profile (3,4,0) and n = 8 orbits
for profile (4,2,1). The set X_0' is not in the vertex set, and the four cases of Lemma 9.22 (b) are not separated:
only Lemma 9.22 (a) and Lemma 9.23 are used, and they hold in every case. Sections 9.B.3 to 9.B.5 are not used.

The **attachment** of z is the set N_p(z) = N(z) n N(p).

**Lemma 9.27.** Let n_3 = 2.

(a) The types of the pairs of N(p) form an N-configuration for the profile (definition of 9.A.1).

(b) N_p(z) consists of two vertices lying in two different pairs of N(p), and N_p(z') = sigma N_p(z). At most one
    of the two vertices is in A_p.

(c) Y_z is determined by B, the type (U ; V) of z, the N-configuration and N_p(z). A state of level t (section 6.5)
    is determined by these data and, for each added orbit {s, sigma s}: U(s), V(s), N_p(s) = N(s) n N(p), the two
    bits [s ~ z], [s ~ z'], and one pattern to each earlier orbit. Every adjacency is given by the list of Lemma
    9.18 (b), in which the line "s with p; s with sigma s" holds because s is a word, together with:

| pair of classes | adjacency | reason |
|---|---|---|
| z with S+, with S- | x_i for i in U, y_l for l in V | parameter (the type of z) |
| z with p; z with z' | not adjacent | Lemma 9.22 (a) |
| z with N(p) | exactly N_p(z) | parameter |
| s with z, with z' | the two bits, not both 1 | parameters; Lemma 9.23 (b) |
| z' with anything | the images under sigma | sigma is an automorphism |

(d) The multiplicities are m_z(i, j) = need_z(i, j) - [{i, j} is one of the two deficient pairs of an A-type of the
    N-configuration], with need_z as in (9.9); their sum is 24 - 2 h_2. The **model**:

- (Z1) U(s) is the unit chosen at the node; V(s) is a unit different from U(s);
- (Z2) N_p(s) consists of two vertices of N(p) lying in two different pairs;
- (Z3) s is adjacent to at most one of z, z';
- (Z4) with a_3(v) = [v ~ z] + [v ~ z']: a vertex s of an added orbit has at most 4 - 2 a_3(s) - |N_p(s) n A_p|
  neighbours among the other added orbits; z has at most 1 - |N_p(z) n A_p| neighbours among the added vertices; a
  vertex w of N(p) has at most 3 - h_0 - 2 a_3(w) neighbours among the added vertices if w is in A_p,
  7 - h_0 - 2 a_3(w) if w is in W, and min(11 - h_0 - 2 a_3(w), floor((20 - 3 a_3(w)) / 2)) if w is in Z_p.

  (Z4) consists of upper bounds only; no equality is required at the last level.

(e) Aut(B) acts on the data of (c) through the indices, and the exchange of the names z and z' replaces (U ; V) by
    (V ; U) and N_p(z) by sigma N_p(z), without changing the N-configuration. So one may assume that the type of z
    is a chosen representative of its class under Aut(B) and the exchange, and then that the N-configuration is
    any chosen representative of its orbit under the group G_z of the automorphisms of B preserving {U, V}. The two
    vertices of a Z-pair carry the same data, so for a Z-pair one of its two vertices is enough in N_p(z).

*Proof.* (a) Let w be in N(p). d(w) <= 2 (no vertex of N(p) has d = 3: section 9.1), and w is not adjacent to x_i
together with y_i: then sigma w would be adjacent to y_i and x_i, and x_i would be adjacent to both vertices of a
pair of N(p), which already have the common neighbour p. If d(w) = 2, with w adjacent to x_U and y_V: U and V are
disjoint; the two vertices of x_U have the common neighbour w outside S, so need_z(U) >= 1 and U is a deficient
pair, and likewise V; for i in U, the adjacent vertices x_i and w have at most one common neighbour, so i has at
most one B-neighbour in V, and likewise with U and V exchanged. Two vertices of N(p) in two different pairs are
non-adjacent and have the common neighbour p, so they have at most one common neighbour in S: this is the
compatibility. Every x_i is a word and has exactly two neighbours in N(p), in two different pairs (section 2):
every index lies in exactly two of the sets.

(b) z is a word (Lemma 9.22 (a)), so it has exactly two neighbours in N(p), in two different pairs (section 2). A
vertex of A_p adjacent to z is a neighbour of z in X_2, and z has at most one (Lemma 9.22 (a): alpha <= 1).

(c) The lines of Lemma 9.18 (b) concern S, N[p] and the added orbits; each is proved as there, with statements
that hold for n_3 = 2 as well (the list at the beginning of 9.B) and the fact that the added vertices are words.
The five new lines carry their reasons.

(d) By Lemma 9.23 (a) the number of vertices s of X_2 with U(s) = {i, j} is need_z(i, j); a vertex of A_p of type
{U', V'} is one of them for {i, j} = U', and its mate for {i, j} = V'. So the vertices of X_2' realise every pair
exactly m_z times, and the sum is 24 - 2 h_2. (Z1): V(s) = U(sigma s) is a unit, different from U(s) (Lemma 9.23
(a)). (Z2): s is a word. (Z3): Lemma 9.23 (b). (Z4): for s, Lemma 9.23 (c): the neighbours of s in X_2 are the
vertices of N_p(s) n A_p and its neighbours in X_2', and their number is |W_s| - 2 a_3(s) <= 4 - 2 a_3(s); for z,
Lemma 9.22 (a) (alpha <= 1); for w, Lemma 9.23 (f) with rho(w) <= 3 - h_0.

(e) The relabellings preserve every statement used. QED

**Lemma 9.28 (what the computation proves).** Suppose that a configuration in case I with n_3 = 2 exists, with
orbit graph B. Then, after relabelling, the type of z is one of the representatives of Computation 9.29 (a), the
N-configuration is one of the representatives of (b) for that type and the profile, and the base given by them
and by N_p(z) passes the budget test and has positive semidefinite matrices M1, M2 on Y_z. From that base, the
search over units of section 6.5, with the model (Z1)-(Z4), reaches a state of level n (n = 9 or 8), whatever the
rule choosing the unit.

*Proof.* The graph on S u {p, z, z'} is determined by B and the type of z, and it is an induced subgraph of G, so
it passes the budget test (section 6.2): the type is in the list of Computation 9.29 (a) up to the relabelling of
Lemma 9.27 (e). Lemma 9.27 (a), (b) give the form of the data, and (c) the fact that Y_z and every state are
determined sets (section 6.3), so the tests of section 6 apply to them and the true ones pass. The true orbits of
X_2' satisfy (Z1)-(Z4) by Lemma 9.27 (d), and a state made of the base and of true orbits, not all of them, has a
unit realised fewer than m_z times; so the argument of section 6.5 applies as in section 9.A. QED

**Computation 9.29 (two programs; folder `lemma/t20_R3_I`).** For the six graphs:

(a) *Types of z.* The ordered pairs (U ; V) of 3-subsets, U != V, for which the graph on the 23 vertices
    S u {p, z, z'} passes the budget test number 8, 46, 30, 24, 24, 50 for I.0, ..., I.5; they form 1, 9, 3, 4, 5, 3
    classes under Aut(B) and the exchange, 25 in all (representatives: `SPEC_ROUTE_B_N3.txt`, section 8; computed
    by `ztypes.py`; the same list was obtained independently in the lab's notes H2).

(b) *Stage 1: the bases.* For each of the 25 types and each of the two profiles (50 cases): all N-configurations
    (1,173,102 for profile (4,2,1) and 12,557,760 for profile (3,4,0), over the 25 types), one representative per
    orbit under G_z (686,675 and 7,461,476), and for each representative all the attachments: two vertices of
    N(p) in two different pairs, one vertex only for a Z-pair (84 of them, 72 when there is a Z-pair). A base is
    rejected by the budget test on the 37 vertices, or by an integer vector with negative form for M1 or M2;
    otherwise it is kept. (The last sentence of Lemma 9.27 (b) is implemented as a separate filter and rejects
    nothing: such attachments already fail the budget test.) Bases kept:

| graph | types | profile (4,2,1) | profile (3,4,0) |
|---|---|---|---|
| I.0 | 1 | 27 | 199 |
| I.1 | 9 | 5,059 | 30,909 |
| I.2 | 3 | 1,420 | 8,138 |
| I.3 | 4 | 1,153 | 9,743 |
| I.4 | 5 | 751 | 5,791 |
| I.5 | 3 | 147 | 1,191 |
| all | 25 | 8,557 | 55,971 |

    The 64,528 bases are 64,498 classes under G_z and the exchange (8,552 and 55,946): in eight cases some
    N-configurations have a stabiliser and a class is listed twice. The type 034;178 of I.1 has no base in either
    profile.

(c) *Stage 2: the search.* From each of the 64,528 bases, the search over units with the model (Z1)-(Z4), the
    budget test and the semidefiniteness test at every node. Numbers of nodes with 0, 1, 2, 3 added orbits:

        profile (4,2,1):    8,557 /  1,494 /   190 /   8
        profile (3,4,0):   55,971 / 17,994 / 2,646 / 108

    86,968 nodes in all. **No node has four added orbits; no state of level n is reached.** No time limit was
    reached, no base was abandoned, and the rank bound of section 6.4 was never used.

*The two programs.* First program: `stage1c.py` with the option `z=` and `stage1_merge.py` (stage 1), `cases6.py`,
`eng6.py`, `run_stage2.py` (stage 2); its coverage is recomputed from its output files by `check_n3.py`
(`n3_check.out`: one stage-1 file and one stage-2 part per case, every base index exactly once, the hash of the
base list recomputed, no time-out, no error). Second program: `in_verify.py`, modes `basesz`, `follow`, `mergez`:
its own enumeration of the N-configurations and of the attachments and its own tests; it shares no code with the
first program. It finds the same classes of bases in the 50 cases, and it re-traverses the 86,968 nodes with the
unit chosen by the first program and finds the same number of kept candidates at every node (`n3_verify.out`, one
line per case). The two programs share the model, which is this section and `SPEC_ROUTE_B_N3.txt`. Everything ran
on one laptop (about 7 CPU-hours); `python n3_all.py <out> <workers> both 340 421` reproduces both programs.

*What is exact.* Every rejection, in both programs, is exact: a common-neighbour count in integers, or an integer
vector x with x^T M x < 0 evaluated in integers (second program: 1,950,773 such vectors in stage 1, for 362,754,336
attachments tested, and 1,978,816 in stage 2; exact rational elimination was needed 0 times). A floating-point
test is only used to keep a base or a candidate. So the statement "no state of level n" rests on exact
rejections; the floating-point decisions affect only the sizes of the kept lists. What the comparison of the two
programs shows is this. Stage 2: the second program makes its own complete traversal, taking at each node the unit
chosen by the first program (a valid remaining unit), generating and testing all the candidates of that unit with
its own code; it finds the same number of kept candidates at every node, and no complete configuration. Stage 1:
the canonical classes of the kept bases are compared separately, and they are the same in the 50 cases.

**Proposition 9.30 (hand statements + Computations 4.12, 9.29).** There is no configuration in case I with
n_3 = 2.

*Proof.* By Lemma 9.28, a configuration would give, for its graph B (one of I.0, ..., I.5) and its profile
((3,4,0) or (4,2,1), section 9.2), a kept base of Computation 9.29 (b) from which the search reaches a state of
level n = 9 or 8. By Computation 9.29 (c) no search reaches level 4. QED

#### 9.B.7 The other route (not used)

Route A (lab session; `lemma/t20_HAND/SPEC_N3.md`, `n3_cases.py`, engine `eng5z.py`) takes the base
S u {p} u X_3 u X_0' (29 vertices, 700 classes of bases) and places the twelve orbits of X_2. It was stopped on 07/10
with 183 classes closed by search (0 complete configurations) and is used by nothing in this text. The computed
statements of NOTES H7, H9, H10 are not used either.



## 10. Conclusion and status

### 10.1 Conclusion as it stands today

**Theorem 10.1 (hand statements + Computations 4.12, 7.4, 7.5, 8.8, 8.9, 9.19, 9.20).** Let G and sigma be as in
section 1, and let phi be an integer-valued sigma-odd function with A phi = -4 phi and sum phi(x)^2 = 20. Then:

1. phi takes the values 0, +1, -1 only, and S+ = {phi = +1} has 10 vertices;
2. k = 0: S+ and S- are independent and no vertex of the support is in N[p];
3. after a suitable labelling, the orbit graph B is one of I.0, ..., I.5;
4. n_3 = 2: exactly two vertices outside S, forming one orbit {z, sigma z}, have three neighbours in S+, and
   (n_0, n_1, n_2) = (7, 46, 24);
5. the profile of N(p) is (3,4,0) or (4,2,1).

*Proof, given the Computations.* 1 is Proposition 3.3. By Corollary 4.5 the configuration is in case I, II or III;
case III is impossible by Proposition 7.6 and case II by Proposition 8.10. So it is in case I, which is 2 (Lemma
4.10), and 3 is Corollary 4.13. By Lemma 9.2, n_3 is 0 or 2, and n_3 = 0 is impossible by Proposition 9.21; the
sizes are those of Lemma 5.3 (I). 5 is Lemma 9.3 with Proposition 9.4. QED

**Theorem 10.2 (T20; Theorem 10.1 + Computation 9.29).** There is no integer-valued sigma-odd function phi with
A phi = -4 phi and sum phi(x)^2 = 20.

*Proof.* By Theorem 10.1 such a function would give a configuration in case I with n_3 = 2, and there is none by
Proposition 9.30. QED

State of the verification on 07/10, 14:10 UTC: Computation 9.29 has two programs sharing the model and no code;
section 9.B.6 has not been refereed yet; Computation 7.5 (III.1) has a second verification with shared components;
Computations 9.19 / 9.20 have a second program on eleven of the twelve cases, the twelfth running (see the note at
the top of this text).

### 10.2 What is proved by hand, what is computed, what is open

| statement | content | nature | programs at the time of writing |
|---|---|---|---|
| Lemma 2.1, Corollaries 2.2, 2.3 | sigma and N(p) | hand | - |
| Lemmas 3.1, 3.2, Proposition 3.3 | integer values => 0, +1, -1, ten at +1 | hand | - |
| Lemmas 4.1-4.4, Corollary 4.5 | k in {0,2,4}; counting identities; e <= 1; parity; three cases | hand | - |
| Lemmas 4.6-4.8 | case II: the plus edge joins two words, in a 4-cycle | hand | - |
| Lemmas 4.9, 4.10, 4.11 | case III: words = edges of K4; case I: B; support structures | hand | - |
| Computation 4.12 | the nine support structures | computed | 2 for the four totals (no shared code); the automorphism orders, on which the completeness of the list rests, from the first program only (recomputed by the transcription script of this text) |
| Lemmas 5.1, 5.3-5.5, Corollary 5.2 | path count; sizes of the classes; bound on X_0; units | hand | - |
| Lemmas 6.1, 6.2, 6.3, Proposition 6.4, Lemma 6.5 | the two PSD matrices, the budget, the rank bound, the search | hand | - |
| Lemmas 7.1-7.3 | model, determined sets and symmetry of case III | hand | - |
| Computation 7.4 | III.0: no node of level 10 | computed | 2 implementations (`eng3.py` / `eng4.py`, and the verifier `engv.py`), tests written separately, one shared model file; the second follows the units of the first |
| Computation 7.5 | III.1: no node of level 10 | computed | **1** (`eng5.py`); the rank bound at 1 node; verifier running |
| Lemmas 8.1-8.7 | case II: n_3 = 0, N(p), types of W, X_2, determined sets | hand | - |
| Computation 8.8 | IIa.0, step 1: 180 -> 87 | computed | 2, identical lists |
| Computation 8.9 | IIa.0, step 2: no node of level 8 | computed | 2 sharing no code; the second follows the units of the first |
| Lemmas 9.1-9.3, Proposition 9.4 | case I: n_3 in {0, 2}; profiles (3,4,0), (4,2,1) | hand | - |
| Lemmas 9.5, 9.6, 9.8, 9.9, 9.10, 9.18 | case I, n_3 = 0: model and determined sets | hand | - |
| Lemmas 9.7, 9.11, 9.12, 9.13, Theorems 9.14, 9.16, Corollaries 9.15, 9.17 | slots and cells; edge counts; isolation of the inner pair of X_0; e(X_0) <= 8 | hand; **not used** by any computation | - |
| Computation 9.19 | case I, n_3 = 0, stage 1 | computed | 2 for I.0 (4,2,1), I.0 (3,4,0), I.5 (4,2,1) (identical lists); **1** for the nine other cases |
| Computation 9.20 | case I, n_3 = 0, stage 2: no node of level 6 | computed | 2 for I.0 (4,2,1) and I.5 (4,2,1); **1** for the ten other cases (second program: 372 of 11,150 bases of I.0 (3,4,0), one base of I.1 (4,2,1)); the rank bound at 15 nodes of I.1, first program |
| Lemmas 9.22-9.26 | case I, n_3 = 2: the orbit X_3, units, a_3(u) = 1, two identities | hand | - |
| Computation 9.29, Proposition 9.30 | case I, n_3 = 2: from the 64,528 bases no search reaches level 4 | computed | 2 (one laptop; shared model, no shared code; the second program follows the unit chosen by the first) |

Nobody outside the working sessions has refereed the hand part. The working reports say that the hand lemmas of the
Codex session (here Theorems 9.14, 9.16, Lemma 9.24, Corollary 9.17) were re-read line by line by the lab session.
For this text every hand statement was derived again; see section 10.4, item 12, for the proofs that exist only
here.

### 10.3 Dependencies

**T18.** The theorem T18 (no configuration of squared norm 18) is **not used**: no proof of this text invokes it,
and no program of the T20 folders reads a file of the T18 folders. (Checked for this text by searching the sources
of `lemma/t20`, `t20_R2`, `t20_R3_I`: no program opens a file outside its own folder, and the names "T18" and "H16"
occur in two places only: a comment of `in_verify.py` that cites Proposition 6.4 of T18_PROOF as "a general fact
on the graph and sigma", and the header of `t20_R2/latt9.py`, an exploratory script that looks for small values of
the form of Lemma 10.2 below on the support alone; it found none, it is not mentioned in the round 2 report, and no
computed line uses it.) The general facts that the two texts have in common (Lemma 2.1, Lemmas 6.1-6.3, Proposition
6.4) are proved here.

**The earlier small-norm statements.** The lemma of 04/10 (no configuration of squared norm 16), the statement
called AUDIT_NORME1 (none of squared norm <= 14) and the statement H16 of the T18 working reports are **not used**.

**The rank bound (Proposition 6.4)** is used by:

- Computation 7.5 (III.1): 1 candidate, in the only program;
- Computation 9.20, graph I.1: 2 candidates for profile (4,2,1) and 13 for profile (3,4,0), in the first program.
  The second program replaces it by a search below the node; at the time of writing this has been done for the 2
  candidates of profile (4,2,1) only (section 9.A.4).

It is not used in Computations 7.4, 8.8, 8.9, 9.19, nor in the ten other cases of Computation 9.20 (no rank
rejection occurs there). Its proof (section 6.4) uses Lemma 2.1 (a) and Lemma 6.1 only.

**Both PSD matrices** are used by every search (the counters of the runs show rejections on M1 and on M2).

**The dual-norm rule** (NOTES H6) is **not used**: by no statement of sections 2 to 9, and by no program of a
closed line (round 3 report: "T18, the 04/10 lemma and the dual-norm test are not used anywhere"; NOTES H9: not
used by the engine of the n_3 = 2 run either). It is recorded here because it may be used for section 9.B, and
because its dependency must be stated exactly. In graph language:

**Lemma 10.2 (dual-norm rule; conditional; not used).** Let phi be the function of a configuration, k an integer
and g an integer-valued sigma-odd function on the vertices. Put

    psi = k phi - (3I - A) g,        N(k, g) = 10 k^2 + (7/2) (g^T (3I - A) g - 2k phi^T g).

Then psi is an integer-valued sigma-odd function with A psi = -4 psi and sum psi(x)^2 = 2 N(k, g); N(k, g) is a
non-negative integer, congruent to 3 k^2 modulo 7, and it can be computed from the induced subgraph of G on the
support of g and from the values of g on S. Consequently, **if** the following statement holds,

    (E14)   every non-zero integer-valued sigma-odd function psi with A psi = -4 psi has sum psi(x)^2 >= 16,

then N(k, g) is never one of 1, 2, ..., 9: a pair (k, g) with 1 <= N(k, g) <= 9 is a contradiction.

*Proof.* A commutes with the permutation matrix of sigma, so (3I - A) g is sigma-odd, and psi is integer-valued and
sigma-odd. By (1.1), (A + 4I)(3I - A) = 12 I - A - A^2 = -2J, and J g = 0 because a sigma-odd function has sum 0; so
A (3I - A) g = -4 (3I - A) g, and A psi = -4 psi. (3I - A) phi = 7 phi, and
(3I - A)^2 = 9I - 6A + A^2 = 7 (3I - A) + 2J, so g^T (3I - A)^2 g = 7 g^T (3I - A) g. Hence

    sum psi^2 = 20 k^2 - 14 k phi^T g + 7 g^T (3I - A) g = 2 N(k, g).

sum psi^2 is even (psi is sigma-odd and psi(p) = 0) and >= 0, so N is a non-negative integer. Modulo 7:
2 N = sum psi^2 = 20 k^2 = 6 k^2, so N = 3 k^2, which is 0, 3, 5 or 6 modulo 7. So among 1, ..., 9 the only possible
values of N are 3, 5, 6 and 7, i.e. sum psi^2 = 6, 10, 12 or 14, with psi != 0: all excluded by (E14). QED

So the rule depends on (E14) only: on the statement for squared norms <= 14 (which the working reports call
AUDIT_NORME1, or "min L* >= 8/7" in the lattice language), **not** on the lemma of 04/10 (squared norm 16) and
**not** on T18 (squared norm 18), because 8 and 9 are not congruent to 0, 3, 5 or 6 modulo 7. (E14) is not proved
in this text, and its identification with the lattice statement rests on the dictionary of section 1.4, which is
outside this text.

The statements of the working reports that use the rule, and therefore (E14), are: NOTES H6 (D1), (D2), (D3), and
Propositions 1, 2 and Corollary 3 of `lemma/t20_CODEX/HAND.md` with the computed tables of that file. **None of
them is used here.** (The "hand proof of e(U) >= 1" in NOTES H2 does not use the rule: it exhibits a vector with
negative form, i.e. a PSD violation. It is not used here either.)

### 10.4 What has not been independently verified, and other caveats

1. **Floating-point "kept" decisions.** In the engines (`eng3.py`, `eng4.py`, `eng5.py`, `eng6.py`, `engv.py`,
   `iian_verify.py`, `in_verify.py`, and the PSD test of `eng.py` used by `stage1c.py`) a candidate is kept when a
   floating-point eigenvalue or Schur complement is above a tolerance (10^-7 in `eng5.py`, `iian_verify.py`,
   `in_verify.py`; 10^-7 on the even blocks and 2 * 10^-9 on the doubled odd block in `eng.py`), according to the
   sources read or to the headers and working reports for the others. This is never used as a proof of
   semidefiniteness. A rejection requires an exact witness (section 6.3). When the floating-point test is negative
   and no integer vector is found, the engines decide by exact rational elimination; the verifiers report how
   often: 0 times in the outputs read (`iian_verify_*.out`, `iian_verify_types.out`: "exact elimination 0"). No
   positive statement of semidefiniteness is needed for Theorem 10.1: by (6.2) the exclusions use exact rejections
   only.
2. **The programs were not audited line by line.** For this text the following were read in full:
   `t20_R2/eng.py`, `t20_R2/cases.py`, `t20_R2/iia_w.py`, `t20_R3_I/cases6.py`; in part: `t20_R2/eng5.py` (header,
   rank test, main loop), `t20_R2/iian_verify.py` (header and the re-traversal), `t20_R3_I/stage1c.py` (header and
   the generation of the types), `t20_R3_I/in_verify.py` (header), `t20_R3_I/r3lib.py`, `t20/t20_enum.py`,
   `t20/t20_verify.py` and `t20/t20_common.py` (headers and main loops); for the others (`eng3.py`, `eng4.py`,
   `eng6.py`, `engv.py`, `t20_kernel.py`, `r2c.py`, the checkers and the summary scripts) only the header, or
   nothing. That each program enumerates exactly the search described in the text is supported by the agreement of
   programs written separately where there are two, not by a proof.
3. **The second programs follow the first ones.** `engv.py`, `iian_verify.py` and `in_verify.py` read the unit
   chosen at every node from a plan written by the first program. They regenerate and test all candidates of that
   unit and compare the number kept. So they verify the kept / rejected decisions node by node; they do not form an
   independent search. By Lemma 6.5 the choice of the units is irrelevant for exhaustiveness, so this does not
   weaken the conclusion, but it means that the node counts were never reproduced by a search with another order.
4. **Shared inputs.** The structure files `structures_I.json` and `structures_III_IIb_IIa.json` (written by
   `t20_enum.py`) are read by `cases.py`, `r3lib.py`, `iian_verify.py`, `in_verify.py`; `check_model.py` compares
   the base graphs and units built from them with edge lists typed in by hand, for III.0, III.1, IIa.0. The list
   `iia_w.json` is read by both programs of Computation 8.9 (the second compares it with its own). For III.0 the two
   engines share the model file `cases.py`. For case I the two programs share the hand model.
5. **Single programs.** III.1; ten of the twelve cases of n_3 = 0 (section 10.2). In particular everything about
   the graphs I.1, I.2, I.3, I.4 rests on one program, and for I.1 on the rank bound as well.
6. **Saved certificates.** Only samples were saved and re-checked: 15,000 for III.0, 6,358 for IIa.0 (5 type sets
   of 87; the others were deleted), ten for I.0 (4,2,1). The plan files, logs and certificates of III.1 and the
   per-base files of the three laptop cases of n_3 = 0 are not in git.
7. **Completeness of the runs** is checked by bookkeeping scripts (`summary_III0.py`, `summary_parts.py`,
   `summary_IIa.py`, `summary2.py`, `check_cloud.py`: all parts present, no time-out, same task list or same list
   of bases in every part), not by a rerun in one piece. The working reports mention abandoned or interrupted
   launches (III.1 was started three times before the run reported here; the first version of two programs of
   rounds 1 and 2 gave wrong or no results and was discarded); nothing of them is used.
8. **Generated and patched engines.** `eng4.py`, `eng5.py`, `eng6.py`, `engv.py` are produced from earlier engines
   by scripts (`mk_eng*.py`, `patch_*.py`). That the stored outputs were produced by exactly the versions now in
   the repository was not verified.
9. **The table of Computation 9.20** is copied from `final_table.out`; the script that wrote it is not in the
   repository folder. For the nine cloud cases the same numbers appear in `cloud_check_t20_I_rest.out`, which was
   compared for this text (all nine lines agree); for the three laptop cases they could be compared only with the
   working report.
10. **Computation 4.12:** see the paragraph after it. The classification into classes by the second enumerator
    rests on an invariant, not on an isomorphism test.
11. **Not verified at all, and not used:** the lattice dictionary and the bridge of section 1.4, (E14), the lemma of
    04/10, T18 itself, the computed statements about n_3 = 2 (section 9.B.6), the statement of the working reports
    that B is connected with its eigenvalues other than 4 in [-3, 3].
12. **Parts of this text that only its author has checked.** The following proofs or formulations are not in the
    working reports, or are there in one line, and were written for this text: Corollary 2.3 (c); the equality case
    of Lemma 3.1 as used in Lemma 3.2; Lemma 4.6; Lemma 4.9 as a separate statement; the completeness argument
    after Computation 4.12; Lemma 5.5 (a) (the reports state U(s) != V(s) without proof); the formula
    x^T M2 x = 22 c^T (7I - G_odd) c of section 6.3; Lemma 6.5 in this form, and Lemma 7.3; Lemma 9.8 (c), (d); in
    Lemma 9.11, the proof of c <= 1 and the derivation of the list by hand; the definition of c in Lemma 9.12; the
    definition of an N-configuration and the comparison of the bounds in Lemma 9.18; Lemma 9.23 (c) (the bound
    a_0(s) <= 4) and (f); Lemma 10.2 in graph language. The transcription script
    `lemma/t20_PROOF/_check_text_data.py` rebuilds the nine structures from the lists printed in section 4.10 and confirms (S1)-(S5),
    the codegrees, the numbers of triangles and of automorphisms, the units, the numbers r_i and the count 180 of
    Lemma 8.5, the labelling by the edges of K4, the arithmetic of (9.6), (9.7), (9.8), (9.11) and the list of
    Lemma 9.11. It is a check of transcription, not part of the proof.

### 10.5 Statements of the working reports that are not used and are left out

- Round 1, B3 and B4: exact PSD on S u {p} and on S u N[p] (quoted in two remarks); the scan of the types of the
  vertices with d = 3 or d = 4 on 23 vertices. Superseded by Lemma 5.3 and Lemmas 9.1, 9.2.
- Round 1, A10: the inequality h_2 + 4 h_3 + n_3 / 2 <= 7 and the two profiles with h_3 = 1 (superseded by Lemma
  9.1); the equivalence between PSD on S and the spectrum of B.
- Round 1, A9: the path counts from the vertices of S in case III and the numbers alpha, beta, gamma (consistent,
  not needed); the hand classification of the case "two triangles" (the classification is Computation 4.12).
- Round 2: the by-product "X_0 contains no 4-cycle" in case II; the explorations B4; the variants of the model of
  case II with X_0 in the base (`CaseIIa`, `CaseIIaW`); the exploratory script `latt9.py` (section 10.3).
- Round 3: the paragraph "tried, closes nothing".
- NOTES: H2 (the computed list of the types of z, and the facts read off it), H5 (the description of N(p) by ten
  roots of D7; it is a reformulation of Lemma 9.8), H6 (D1)-(D3) and the searches for dual-norm certificates, H7,
  H8, H9, H10 (computed; section 9.B.6).
- `lemma/t20_CODEX/HAND.md`: Propositions 1, 2, Corollary 3 and the computed tables (they depend on (E14));
  `TRIANGLE_REDUCTION.md`: the two tables of class sizes of the sets Delta, Gamma and their complement (correct by
  Corollary 9.15 and Lemma 9.24, not needed).

### 10.6 Where the sources disagree or are imprecise, and what was chosen

1. **III.1.** Round 2 says "open, not completed (about 900 tasks done)". `lemma/t20_III1/README.md`,
   `T20_WORK.md` and `T20_BOARD.md`, written later, say: completed by one program, 0 configurations, verifier
   running. Chosen: the later files (Computation 7.5, one program).
2. **Upper bounds of stage 2 of case I.** The round 3 report says that the candidates are enumerated "under the caps
   of C4 and C5". The headers of `cases6.py` and `in_verify.py` give 4 - h_0, 8 - h_0 and min(10, 12 - h_0); for a
   vertex of W in profile (3,4,0) this is 8, while C4 (Lemma 9.9) gives 7. Chosen: the bounds of the code, since
   they are what was run; they are weaker than those of Lemma 9.9 and therefore valid (Lemma 9.18 (c)).
3. **Progress of n_3 = 2.** 168 of 700 classes closed (NOTES H10 and `SPEC_N3.md`, 11:30 UTC); 183 bases closed,
   run stopped at 11:43 UTC (`T20_BOARD.md`). Both are quoted (section 9.B.6); neither is used.
4. **Bound on a_2 of a vertex of X_2 for n_3 = 2.** `SPEC_N3.md` and NOTES H9: a_2 <= 5 (a_3 = 0), a_2 <= 3
   (a_3 = 1). Header of `cases6.py`: a_0 <= 4. Both valid; the second is proved in Lemma 9.23 (c).
5. **Number of configurations of N(p) for I.0 (4,2,1).** Round 2 (explorations): 1,784,786, of which 48,587 pass.
   Round 3: 178,768 N-configurations, 11,322 orbits, 3,022 bases. These are different objects (the first is a count
   of an exploratory program that, in the words of its report, proves nothing); they were not reconciled. Chosen:
   round 3.
6. **"Two independent programs" for the nine support structures** (round 1, header). Its section B2 says that the
   second program has no isomorphism test and that the automorphism orders come from the first only. Stated as such
   after Computation 4.12, with the argument that makes the list complete.
7. **"Two programs" for III.0** (`T20_BOARD.md`). Round 2 is more precise: two implementations, one shared model
   file. Stated as in round 2 (section 7.4).
8. **Round 3, C6 and C7.** C6 asserts c <= 1 without proof and refers to a script for the list of solutions; C7
   uses c without defining it. Proof and definition supplied (Lemmas 9.11, 9.12).
9. **NOTES H6** says "N(k, m) is 0 or >= 10", quoting the three earlier statements (norms <= 14, 16, 18). By the
   congruence of Lemma 10.2 only the first is needed, as the same note says a few lines below.
10. **Which statement.** Round 1, section 0: the task text said squared norm 40; the statement is squared norm 20
    (section 1.4).

No mathematical error was found in the working reports while writing this text.


## Appendix A. Programs, outputs and commands

Paths are relative to the root of the repository `conway99-c2-aws`. "python" is Python 3 with numpy; `t20_enum.py`
needs numba, and the rank tests need python-flint. Each command is run in the folder of the script. The command
lines are those recorded in the working reports, in the README files, in the driver scripts or in the headers of
the scripts; where the exact arguments of a run were not recorded, the usage line is given and the names of the
output files show how the work was split.

### A.1 Computation 4.12 (the support structures), folder `lemma/t20`

| program | command | output |
|---|---|---|
| `t20_enum.py` (with `t20_kernel.py`, `t20_common.py`) | `python t20_enum.py I` ; `python t20_enum.py III IIb IIa` (the arguments are the names of the types; not recorded, deduced from the outputs) | `enum_I.out`, `structures_I.json`; `enum_III_IIb_IIa.out`, `structures_III_IIb_IIa.json` (earlier run of III and IIb, same numbers: `enum_III_IIb.out`, `structures_III_IIb.json`) |
| `t20_verify.py` | `python t20_verify.py III I` ; `python t20_verify.py IIa2` ; `python t20_verify.py IIb IIa` ; `python t20_verify.py IIb2` (deduced likewise) | `verify_III_I.out`; `verify_IIa.out`; `verify_II.out` (IIb complete, then cut by the time limit: "exit 124"); `verify_IIb.out`. `verify.out` holds only the exit line of a discarded first version |
| data of section 4.10 | `python t20_survivors.py` ; `python t20_deficiency.py` ; `python t20_names.py` | `survivors.out`, `deficiency.out`, `names.out` |
| transcription check of this text | `python lemma/t20_PROOF/_check_text_data.py` | `_check_text_data.out` |

### A.2 Computation 7.4 (III.0), folder `lemma/t20_R2`

| program | command | output |
|---|---|---|
| `eng3.py`, model `cases.py` | `python run_eng3.py III.0 <part> 3 <time limit> 3 e3_III0` (part = 0, 1, 2) | `e3_III0_{0,1,2}of3.json`, `.log`, `.out` |
| `eng4.py`, model `cases.py` | `python run_eng4.py III.0 <part> 3 <time limit> 3 e4_III0 plan` | `e4_III0_{0,1,2}of3.json`, `.log`, `.out`; the plan files are not in git |
| `engv.py`, model `cases.py` | `python run_engv.py III.0 <part> 3 <time limit> 3 v_III0 plan=<plan file of eng4.py>` | `v_III0_{0,1,2}of3.json`, `.log`, `.out` |
| totals | `python summary_III0.py` | `summary_III0.out` |
| certificates | `python check_certs.py III.0 <certificate files>` | `check_certs_III0.out` |
| model | `python check_model.py` | `check_model.out` |

The time limits of these runs were not recorded; the result files record: 3 parts, split parameter 3 (tasks of level 4), the group of
order 48, pointwise stabilisers, rank test enabled, no time-out.

### A.3 Computation 7.5 (III.1), folders `lemma/t20_R2` (programs) and `lemma/t20_III1` (outputs)

| program | command | output |
|---|---|---|
| `eng5.py`, model `cases.py` | `OPENBLAS_NUM_THREADS=1 python run_eng5.py III.1 <i> 8 80000 3 e5_III1 setwise plan certs=2500` (i = 0..7) | `lemma/t20_III1/e5_III1_{0..7}of8.json`; logs, plans and certificates not in git |
| totals | `python summary_parts.py e5_III1 8` | `lemma/t20_III1/summary_III1.out` |

### A.4 Computations 8.8 and 8.9 (IIa.0), folder `lemma/t20_R2`

| line | program | command | output |
|---|---|---|---|
| 8.8 | `iia_w.py` (uses `r2c.py`) | `python iia_w.py` | `iia_w.json` (the printed output was not saved) |
| 8.8 | `iian_verify.py` | `python iian_verify.py types` | `iian_verify_types.out` |
| 8.9 | `eng5.py`, model `cases.CaseIIaN` | `python run_iian.py 0:44 <time limit> all` ; `python run_iian.py 44:87 <time limit> all` | `iian/all_w<k>_0of1.json`, `.log`, `.plan` (k = 0..86); `iian/all_summary_0-44.json`, `iian/all_summary_44-87.json`; `iian_all_a.out`, `iian_all_b.out` |
| 8.9 | totals | `python summary_IIa.py` | `summary_IIa.out` |
| 8.9 | `iian_verify.py` | `python iian_verify.py follow <a> <b> iian all` for (a, b) = (0, 30), (30, 38), (38, 44), (44, 66), (66, 87) | `iian_verify_<a>_<b>.out`, `.json` |
| 8.9 | certificates | `python check_certs.py IIa.0 iian_certs_sample/*.jsonl` | `check_certs_IIa.out` |

`hand_checks.py` -> `hand_checks.out` contains arithmetic guards for the hand lemmas of round 2 (not part of the
proofs).

### A.5 Computations 9.19 and 9.20 (case I, n_3 = 0), folder `lemma/t20_R3_I`

| what | program | command | output |
|---|---|---|---|
| one case, whole pipeline | `cloud_case.sh` | `bash cloud_case.sh <out dir> <graph> <h2> <h1> <h0>` with PY and NPROC set; `T20_SKIP_VERIFY=1` stops before the second program | `<out dir>/<graph>_<profile>/`: `s1_*.json`, `stage1_*.out`, `stage2_*.out`, `verify_*.out`, `parts/`, `logs/`, `timing.txt` |
| stage 1 | `stage1c.py`, `stage1_merge.py` (with `r3lib.py`, `eng.py`) | `python stage1c.py <graph> <h2> <h1> <h0> <prefix>.part<i>of<n>.json part=i/n` ; `python stage1_merge.py <prefix> <n> <stage1.json>` | the stage-1 file (list of bases) |
| stage 2 | `run_stage2.py` (engine `eng6.py`, model `cases6.py`), `summary2.py` | `python run_stage2.py <stage1.json> <part> <nparts> 400000 <prefix> width=3` ; `python summary2.py <stage1.json> <prefix> <nparts>` | `<prefix>_<part>of<nparts>.jsonl` (one line per base, with its plan), `.sum.json`; the summary |
| second program | `in_verify.py` | `python in_verify.py bases <graph> <h2> <h1> <h0> <prefix>_<i>of<n>.json part=i/n` ; `python in_verify.py follow <stage1.json> <stage2 prefix> <part> <nparts> <out>` ; `python in_verify.py merge <stage1.json> <prefix> <n> <follow prefix>` | `verify_<graph>_<profile>.out` |
| the nine cloud cases, first program | job `lemma/cloud/jobs/t20_I_rest.sh`, run by `lemma/cloud/run.sh` | - | git branch `lemma-run/t20_I_rest-i-02f356c70da99d700` (status "FINISHED exit=0"): `ALL.txt`, and the folders `I1_340`, `I1_421`, `I2_340`, `I2_421`, `I3_340`, `I3_421`, `I4_340`, `I4_421`, `I5_340`, each with `s1_*.json`, `stage1_*.out`, `stage2_*.out`, `parts/s2_<i>of128.jsonl`, `parts/s2_<i>of128.sum.json`, `logs/` |
| re-count of the cloud run | `check_cloud.py` | `git archive origin/lemma-run/<job>-<id> \| tar -x -C <dir>` ; `python check_cloud.py <dir> <out file>` | `cloud_check_t20_I_rest.out` |
| the three laptop cases | the same programs | - | per-base files in the session scratchpad (not in git) |
| table of the twelve cases | - | - | `final_table.out` |
| comparisons | - | - | `cloud_vs_laptop_stage1.out`, `cmp_eng5_I0_421.out` |
| sample of certificates | `sample_certs.py`, `check_sample.py` | `python sample_certs.py <stage1.json> <stage2 prefix> <nparts> <out.jsonl>` ; `python check_sample.py <file.jsonl>` | `sample_certs_I0_421.jsonl` |
| cells (Lemma 9.11) | script `hand_cells.py` (not in the repository folder) | - | `hand_cells.out` |

Runs of the second program in progress at the time of writing (**not used**): cloud jobs
`lemma/cloud/jobs/t20_Iv_A.sh` to `t20_Iv_F.sh` and `t20_I1_340.sh`; git branches
`lemma-run/t20_Iv_A-i-0390fd53333c148ad` (status "INSTALLING" only), `lemma-run/t20_Iv_B-i-0a03ce79bff09fa5d`,
`lemma-run/t20_Iv_C-i-092f5550d84f61e09`, `lemma-run/t20_Iv_D-i-09169834049067883`,
`lemma-run/t20_Iv_E-i-0cd9427b48ee5704e`, `lemma-run/t20_Iv_F-i-0c5414832a6ac4ff5` and
`lemma-run/t20_I1_340-i-019e86d399c17954f` (status "RUNNING" in the last commit of each that was present in the
local copy of the repository when this text was written).

### A.6 Section 9.B (n_3 = 2)

Computation 9.29 (route B), folder `lemma/t20_R3_I`: specification `SPEC_ROUTE_B_N3.txt`; types of z `ztypes.py`,
`ztypes.json`, `ztypes.out`; one case, both programs: `n3_case.py`; all cases: `python n3_all.py <out> <workers> both 340 421`;
first program `stage1c.py` (option `z=`), `stage1_merge.py`, `cases6.py`, `eng6.py`, `run_stage2.py`, `summary2.py`;
second program `in_verify.py` (modes `basesz`, `follow`, `mergez`); checks `check_n3.py`, `check_n3_verify.py`,
`table_n3.py`. Outputs kept in the repository: `n3_check.out` (first program, per case), `n3_table.out`,
`n3_verify.out` (agreement per case, totals on its last lines), `n3_stage1_regen_compare.out` (the 25 stage-1 lists
of profile (4,2,1) regenerated and identical). The base lists, the stage-2 files with plans and the second
program's raw outputs (41 MB) are not in the repository; the command above regenerates them.

Not used by the proof. Route A: `lemma/t20_HAND/n3_cases.py` (bases), `eng5z.py` (generated by `mk_eng5z.py`), `run_n3.py`,
`summary_n3.py`, cloud job `lemma/cloud/jobs/t20_n3.sh`; git branches `lemma-run/t20_n3-i-0b8ae938c1fc89c62` and
`lemma-run/t20_n3-i-04bb3ac564f658b79` (both with status "RUNNING" in their last commit present locally). Small
scripts of the hand notes: `x3_types.py`, `n3_base.py`, `dual_test_S.py`, `dual_test_X3.py`, `check_inner.py`.
Route B: `lemma/t20_R3_I/stage1c.py` with the option `z=`, `cases6.py`. Specification for a second program:
`lemma/t20_HAND/SPEC_N3.md`. Scripts of the Codex session: `lemma/t20_CODEX/*.py`.


## Appendix B. Correspondence with the labels of the working reports

| label in the working reports | here |
|---|---|
| round 1 (`t20/T20_REPORT.md`): A0 | Lemma 2.1, Corollaries 2.2, 2.3 |
| A1 | Lemma 3.1, Proposition 3.3 |
| A2 | Lemma 3.2 |
| A3 | Lemma 4.1 |
| A4 | Lemmas 4.2, 4.3 |
| A5 | Lemma 4.4, Corollary 4.5 |
| A6 | Lemma 5.1, Corollary 5.2, Lemma 5.3 |
| A7, A8 | Lemmas 4.7, 4.8 (and Lemma 4.6) |
| A9 | Lemma 4.9, Lemma 5.3 (III), Lemma 7.1 |
| A10 | Lemma 4.10, Lemma 5.3 (I), Lemma 9.3 |
| A11 | Lemma 5.3 (II), Lemma 8.1 |
| B1, B2; section C | Computation 4.12; section 4.10 |
| B3, B4 | not used (section 10.5) |
| round 2 (`t20_R2/REPORT.md`): (M) | Lemma 2.1, Corollary 2.3 |
| G0, G1 | Lemma 5.1, Lemma 5.4 |
| II.1 - II.6 | Lemmas 8.1 - 8.6 |
| "Case III: model" | Lemmas 7.1, 7.2 |
| I.1, I.2, I.3 | Lemma 9.1, Lemma 9.2, Proposition 9.4 |
| B1 (III.0); B2 (IIa.0); B3 (III.1) | Computation 7.4; Computations 8.8, 8.9; Computation 7.5 (with `t20_III1/`) |
| round 3 (`t20_R3_I/REPORT.md`): C1 | (9.1), Lemma 9.5 |
| C2, C3 | Lemma 9.6, Lemma 9.7 |
| C4 | Lemmas 9.8, 9.9 |
| C5 | Lemma 9.10 |
| C6, C7 | Lemmas 9.11, 9.12 |
| C8 | Lemma 9.13 |
| C9 | Lemma 6.3, Proposition 6.4 |
| "Determined sets", stage 1, stage 2 | Lemma 9.18, Computations 9.19, 9.20 |
| lab notes (`t20_HAND/NOTES.md`): H0 | (9.1), Lemma 9.5 |
| H1 | Lemma 9.22 |
| H3 | Lemma 9.25 |
| H4 | Lemma 9.13 (n_3 = 0), Lemma 9.26 (n_3 = 2) |
| H6, the rule and its dependency | Lemma 10.2 |
| H2, H5, H6 (D1)-(D3), H7 - H10 | not used (sections 9.B.6, 10.5) |
| `t20_HAND/SPEC_N3.md`, sections 2 - 4 | Lemmas 9.22, 9.23, 6.5 |
| `t20_CODEX/PROFILE_421.md` | Theorem 9.14, Corollary 9.15 |
| `t20_CODEX/EDGE_BOUND.md` | Theorem 9.16, Corollary 9.17 |
| `t20_CODEX/TRIANGLE_REDUCTION.md` | Lemma 9.24 |
| `t20_CODEX/HAND.md` | not used (sections 10.3, 10.5) |


## Appendix C. Numbering of the vertices in the files

- All the programs: x_i = i and y_i = 10 + i (i = 0..9); p = 20. Further vertices are added in orbits (v, v + 1).
- Structure files (`structures_I.json`, `structures_III_IIb_IIa.json`): field `m` is the 10 x 10 matrix of the
  states of the pairs of orbits (bit 1 = minus edge, bit 2 = plus edge), field `H` the list of the inner indices.
- Case III (`cases.CaseIII`): X_0 = the three mate pairs (21, 22), (23, 24), (25, 26); the added orbits of X_2 are
  (27 + 2q, 28 + 2q), q = 0, 1, ... in the order of the search.
- Case II (`cases.CaseIIaN`, `iian_verify.py`): W = the five mate pairs (21, 22), ..., (29, 30); the pair number t,
  of type (i ; l), has 21 + 2t adjacent to p, to its mate, to x_i and to y_l; the added orbits start at 31.
- Case I, n_3 = 0 (`cases6.CaseIN6`, `in_verify.py`): the seven pairs of N(p) are (21, 22), ..., (33, 34), in the
  order of the stage-1 record; a pair is ("A", U, V), ("W", i, l) or ("Z",); the added orbits start at 35.
- A plan line (first engines): level, the two indices of the chosen unit, number of candidates, number kept.
