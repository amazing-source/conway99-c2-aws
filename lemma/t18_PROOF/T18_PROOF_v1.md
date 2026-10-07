# T18: no sigma-odd integer (-4)-eigenfunction of squared norm 18 on a srg(99,14,1,2)

Self-contained proof text, written on 2026-10-07 from the working reports of the repository `conway99-c2-aws`
(folders `lemma/t18`, `lemma/t18_STRUCT`, `lemma/t18_VERIF331`, `lemma/t18_B2`, `lemma/t18_B0`, `lemma/t18_B0_VERIFC`,
`lemma/t18_REFEREE`, and `LEMMA_TARGET_2026-10-06.md`). The working reports are sources, not part of the proof: every
hand statement used below is proved below, from the definitions. The finite computations are described precisely
(what is enumerated, by which tests, with which result), and for each of them the programs and their output files
are listed in the appendix.

## 0. Front matter

### 0.1 GAP boxes

**GAP boxes in this document: none.** Every hand statement was re-derived while it was written and no step was found
that could not be justified. What is *not* a hand proof is listed in section 9.2 (the finite computations) and what
has not been independently verified is listed in section 9.3. Three points of section 9.3 deserve to be known before
reading:

- the list of 16 isomorphism classes of 4-regular graphs on 9 vertices comes from one program only; the selection of
  the three classes that matter is done by three programs, two of which share an isomorphism routine (section 4.10);
- the programs of the first implementation read a file `types.json` that was produced with a filter depending on
  another lemma (called H16 in the working reports); the saved output `rows.out` shows that this filter removed
  nothing on the entries that are read, and the second implementations do not read the file (section 9.3, item 6;
  this point is not mentioned in the working reports nor in the referee's report);
- a "kept" decision of a positive-semidefiniteness test is a floating-point decision in most programs. It is never
  used as a proof: only rejections are used, and they are exact (sections 6.3 and 9.3, item 1).

### 0.2 Notation and conventions

- `u` between two sets is the union, `n` the intersection, `\` the difference; `|T|` is the number of elements.
- `x ~ y` means "x and y are adjacent"; `x not~ y` means "x and y are not adjacent".
- `N(x)` is the set of neighbours of x, `N[x] = N(x) u {x}`.
- `C(a,2) = a(a-1)/2`. `[P]` is 1 if the statement P is true and 0 otherwise.
- `I` is the identity matrix, `J` the all-ones matrix, `1_T` the indicator vector of a vertex set T, `e_x = 1_{x}`.
- For a matrix M and a vertex set Y, `M[Y]` is the principal submatrix on Y; for two lists R, R' of vertices,
  `A[R,R']` is the submatrix with rows R and columns R'.
- "PSD" means positive semidefinite.
- Labels in square brackets such as [A3], [N3], [P2], [C-b] are the names of the same statements in the working
  reports. They are given only so that a reader of those reports can find the correspondence (appendix C); no
  proof below refers to them.
- A statement marked **Computation** is the result of a finite enumeration by programs. A statement marked
  **Lemma**, **Proposition**, **Theorem** or **Corollary** without that word is proved by hand in the text, except
  that the three final statements (Propositions 7.7 and 8.9, Theorem 9.1) combine hand statements with
  Computations and say so.


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

> **Theorem T18.** Let G be a strongly regular graph with parameters (99,14,1,2) and sigma an automorphism of G of
> order 2 with exactly one fixed vertex. There is no function phi from the vertex set of G to the integers such that
> (i) phi(sigma x) = -phi(x) for every vertex x, (ii) A phi = -4 phi, (iii) sum over all vertices of phi(x)^2 = 18.

The proof is by contradiction: a triple (G, sigma, phi) satisfying the hypotheses is called a **configuration**, and
the document shows that no configuration exists. Its logical chain is:

    phi integer-valued
      -> section 3 (hand):  phi takes the values 0, +1, -1 only; S+ = {phi = +1} has 9 vertices
      -> section 4 (hand + Computation 4.10): S+ is independent, no vertex of the support is in N[p], and the
                            "orbit graph" B of the support is one of three explicit graphs B0, B1, B2
      -> section 5 (hand):  no outside vertex has 3 neighbours in S+; the neighbourhood of p has one of three
                            "profiles" (2,5,0), (3,3,1), (4,1,2); profile (4,1,2) is impossible
      -> section 7 (hand model + Computations 7.3, 7.6): profile (3,3,1) is impossible for B0, B1, B2
      -> section 8 (hand model + Computations 8.4, 8.5, 8.6, 8.8): profile (2,5,0) is impossible for B0, B1, B2
      -> contradiction.

Section 6 contains the three tests used by the computations (common-neighbour budgets, two PSD matrices, a rank
bound), with their proofs.

### 1.4 Context (not part of the lemma)

In the project, T18 is the graph form of a statement about a lattice: `LEMMA_TARGET_2026-10-06.md`, section 2, gives
a dictionary under which "every non-zero sigma-odd integer function phi with A phi = -4 phi has squared norm >= 2m"
is equivalent to a lower bound m/7 on the minimum of a dual lattice; the case of squared norm <= 16 is an earlier
lemma, T18 is the case 18. That dictionary is presented in its own source as reconstructed during a session, with
the warning "check it against the project's own notes before building on it", and it was not verified by the
referee. **It is outside this document**: what is proved here is the graph statement of section 1.3 and nothing
else. The campaign only needs phi with values 0, +1, -1; section 3 shows that this is not a
restriction.


## 2. Basic facts about sigma  [A0]

**Lemma 2.1.** Let x be a vertex, x != p.

(a) x ~ sigma x if and only if x ~ p.

(b) N(p) consists of 7 orbits {a_c, b_c}, c = 1..7, with b_c = sigma a_c; the 7 mate edges {a_c, b_c} are the only
    edges with both ends in N(p). In other words N(p) induces a perfect matching, made of mate edges.

(c) For c = 1..7 the only common neighbour of a_c and b_c is p. Hence no vertex other than p is adjacent to both
    a_c and b_c.

(d) If x is outside N[p], then x not~ sigma x, and N(x) n N(sigma x) = {z, sigma z} for a vertex z which is outside
    N[p] (and z != sigma z).

*Proof.* Let C = N(x) n N(sigma x). Since sigma is an automorphism and an involution,
sigma C = N(sigma x) n N(x) = C: the set C is sigma-invariant. Also x != sigma x, because p is the only fixed vertex.

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

**Corollary 2.2.** Every vertex x outside N[p] has exactly 2 neighbours in N(p).

*Proof.* x and p are distinct and non-adjacent, so they have exactly 2 common neighbours, and the common neighbours
of x and p are the neighbours of x in N(p). QED

Corollary 2.2 is used many times below in the form "the two common neighbours of x and p".

*Remark (not used below).* By (d), sending the orbit of x to the orbit {z, sigma z} defines a map iota on the
(99 - 1 - 14)/2 = 42 orbits outside N[p]; it is a fixed-point-free involution, because x is a common neighbour of
z and sigma z.


## 3. From integer values to the values 0, +1, -1

This step is missing in the working reports for squared norm 18 (referee's remark 1); the proof below is the
referee's, checked.

**Proposition 3.1.** Let phi be an integer-valued sigma-odd function with A phi = -4 phi and sum phi(x)^2 = 18.
Then phi takes only the values 0, +1, -1, and the set S+ = {x : phi(x) = +1} has exactly 9 vertices. Moreover
S- = {x : phi(x) = -1} = sigma S+, and p is in neither.

*Proof.* phi(p) = 0. For an orbit O = {x, sigma x} put c_O = |phi(x)| = |phi(sigma x)|, an integer >= 0.
Then sum over the 49 orbits of 2 c_O^2 = 18, i.e.

    sum_O c_O^2 = 9.                                                                             (3.1)

*Claim: if c_O = c > 0, then the sum of c_O' over the orbits O' != O is at least 3c.* Choose x in O with
phi(x) = c > 0. The eigen-equation at x is

    -4c = sum over the neighbours y of x of phi(y).

Sort the neighbours of x by orbit. The neighbour p (if x ~ p) contributes 0. The mate sigma x, if it is a neighbour
of x, contributes phi(sigma x) = -c. An orbit O' = {y, sigma y} different from O contributes 0 if x is adjacent to
none of its two vertices, +-phi(y) if x is adjacent to exactly one of them, and phi(y) + phi(sigma y) = 0 if x is
adjacent to both; in all cases at least -c_O'. Hence -4c >= -c - sum_{O' != O} c_O', which is the claim.

By (3.1) the multiset of the non-zero values c_O is one of {3}, {2,2,1}, {2,1,1,1,1,1}, {1,1,1,1,1,1,1,1,1}
(the ways of writing 9 as a sum of squares 9, 4, 1). The claim excludes the first three:

    {3}:           c = 3, the others sum to 0  <  9;
    {2,2,1}:       c = 2, the others sum to 3  <  6;
    {2,1,1,1,1,1}: c = 2, the others sum to 5  <  6.

So exactly 9 orbits have c_O = 1 and the other 40 have c_O = 0. In each of the 9 orbits one vertex has phi = +1 and
its mate has phi = -1. QED

From now on a configuration is a triple (G, sigma, phi) with phi as in Proposition 3.1, and

    S+ = {phi = +1} (9 vertices),   S- = sigma S+ = {phi = -1},   S = S+ u S-  (the support, 18 vertices).


## 4. Reductions on the support

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
in S-, so k is the number of active orbits of N(p), S n N(p) has 2k vertices and S \ N(p) has 18 - 2k vertices.
p is not in S.

### 4.2 k is 0 or 2

**Lemma 4.2.** k is in {0, 2}.

*Proof.* Fix c. By Lemma 2.1 (b) the neighbours of a_c are p, b_c and 12 vertices outside N[p]; call the latter the
outer neighbours of a_c. The eigen-equation at a_c is

    -4 phi(a_c) = phi(p) + phi(b_c) + (sum of phi over the 12 outer neighbours) = 0 - phi(a_c) + (that sum),

so the sum of phi over the outer neighbours of a_c is -3 phi(a_c). Let n_c be the number of outer neighbours of
a_c that lie in S. As phi is +-1 on S and 0 elsewhere,

    n_c = phi(a_c) (mod 2)   and   n_c >= 3 |phi(a_c)|.

So n_c is odd and >= 3 if the orbit c is active, and n_c is even otherwise. By sigma, b_c has the same number n_c of
outer neighbours in S.

Now count the pairs (s, v) with s in S \ N(p), v in N(p), s ~ v. By Corollary 2.2 each s contributes 2, so the
number is 2 (18 - 2k). Counting by v it is sum over c of 2 n_c. Hence sum_c n_c = 18 - 2k.

Parity: sum_c n_c = k (mod 2) and 18 - 2k is even, so k is even. Size: sum_c n_c >= 3k, so 18 - 2k >= 3k and
k <= 3. Hence k is 0 or 2. QED

### 4.3 e is at most 2

**Lemma 4.3.** e <= 2.

*Proof.* Let e(S) be the number of edges with both ends in S. By sigma there are e edges inside S-, and the number
of edges between S+ and S- is sum_{x in S+} d-(x) = sum_{x in S+} (d+(x) + 4) = 2e + 36 by (4.2). So e(S) = 4e + 36
and 1_S^T A 1_S = 2 e(S) = 8e + 72. On the other hand A = 14 E_0 + 3 E_3 - 4 E_{-4} <= 14 E_0 + 3 (I - E_0) as
quadratic forms, and 1_S^T E_0 1_S = 18^2/99 = 36/11, so

    1_S^T A 1_S <= 14 * 36/11 + 3 (18 - 36/11) = 54 + 11 * 36/11 = 90.

Hence 8e + 72 <= 90 and e <= 2. QED

### 4.4 Two counting identities

**Lemma 4.4.** With the sums taken over all vertices z outside S (p included, with d(p) = k):

    (I1)   sum_z C(d(z), 2) = 18 - 7e - Q;
    (I2)   sum_z d(z)       = 90 - 4e.

*Proof.* (I2). A vertex x of S+ has d+(x) neighbours in S+, d+(x) + 4 in S-, hence 10 - 2 d+(x) outside S. Summing
over S+, the number of edges between S+ and the outside of S is 90 - 2 * 2e = 90 - 4e, and it is also
sum_z d+(z) = sum_z d(z).

(I1). Count the triples ({x, x'}, v) where {x, x'} is a pair of distinct vertices of S+ and v is a common neighbour
of x and x'. There are C(9,2) = 36 pairs; the e adjacent ones have 1 common neighbour and the others 2, so the
number of triples is 72 - e. Counting by v: a vertex v contributes C(d+(v), 2). For v = x in S+ this is
C(d+(x), 2). For v = sigma x in S- it is C(d-(x), 2) = C(d+(x) + 4, 2) by (4.1) and (4.2). For v = z outside S it is
C(d(z), 2). Since C(d,2) + C(d+4,2) = d^2 + 3d + 6,

    72 - e = sum_{x in S+} (d+(x)^2 + 3 d+(x) + 6) + sum_z C(d(z),2) = Q + 6e + 54 + sum_z C(d(z),2).   QED

### 4.5 The parity law  [A1]

**Lemma 4.5.** e = C(k,2) (mod 2). So k = 0 forces e even and k = 2 forces e odd.

*Proof.* The complement of S is sigma-invariant and p is its only fixed vertex, so the 80 vertices z != p outside S
are paired by sigma, with d(sigma z) = d(z). Hence sum_{z outside S, z != p} C(d(z),2) is even, and by (I1)
18 - 7e - Q = C(k,2) (mod 2). Finally Q = sum d+(x)^2 = sum d+(x) = 2e = 0 (mod 2). So 7e + C(k,2) is even. QED

By Lemmas 4.2, 4.3 and 4.5 the pair (k, e) is one of (0,0), (0,2), (2,1).

### 4.6 e = 2 is impossible  [A2]

**Lemma 4.6.** e != 2.

*Proof.* Let e = 2. Either the two edges inside S+ are disjoint, and then four vertices have d+ = 1 and Q = 4; or
they share a vertex, and then Q = 4 + 1 + 1 = 6. By (I1), sum_z C(d(z),2) = 4 - Q. If Q = 6 this is negative,
impossible. If Q = 4 it is 0, so d(z) <= 1 for every z outside S; but by (I2) sum_z d(z) = 82, and there are only
81 vertices outside S. QED

### 4.7 e = 1 is impossible  [A3]

Label S+ = {x_0, ..., x_8} and put y_i = sigma x_i, so S- = {y_0, ..., y_8}. Call the index i **inner** if x_i is in
N(p) and **outer** otherwise, and put h_i = 1 if i is inner, 0 if i is outer. By Lemma 2.1 (a),

    x_i ~ y_i  if and only if  i is inner.                                                       (4.4)

For an index j let M_j = {i != j : x_j ~ y_i}. Applying sigma, x_j ~ y_i if and only if x_i ~ y_j, so

    i is in M_j  if and only if  j is in M_i.                                                    (4.5)

d-(x_j) = |M_j| + h_j by (4.4), so by (4.2)

    |M_j| = d+(x_j) + 4 - h_j.                                                                   (4.6)

**Lemma 4.7.** e != 1.

*Proof.* Let e = 1, and let the unique edge inside S+ be {x_a, x_b}. Then d+(x_a) = d+(x_b) = 1 and d+ = 0 on the
other seven vertices of S+. There are three cases.

*Case C: a and b are both inner.* Then x_a and x_b are adjacent vertices of N(p). By Lemma 2.1 (b) the only edges
inside N(p) are mate edges, so x_b would be the mate of x_a; but the mate of x_a is y_a, which is in S-, not in S+.
Impossible. (This case is not mentioned in the working report.)

*Case A: a and b are both outer.* Renumber so that a = 0, b = 1. By (4.6), |M_0| = |M_1| = 5 and
|M_j| = 4 - h_j for j >= 2.

The pair x_0, x_1 is adjacent, so it has exactly one common neighbour. For i in M_0 n M_1 the vertex y_i is
adjacent to x_0 and to x_1. So

    |M_0 n M_1| <= 1.                                                                            (4.7)

Suppose first that 1 is not in M_0. By (4.5), 0 is not in M_1. Then M_0 and M_1 are 5-subsets of the 7-set {2,...,8},
so |M_0 n M_1| >= 3, contradicting (4.7).

So 1 is in M_0 and 0 is in M_1. Put P = M_0 \ {1} and P' = M_1 \ {0}: two 4-subsets of {2,...,8} with
P n P' = M_0 n M_1. By (4.7), |P n P'| <= 1; and |P u P'| <= 7 gives |P n P'| >= 1. Hence

    P n P' = {r} for one index r,   and   P u P' = {2,...,8}.

Let j be in P \ {r}. Then j is in M_0 and not in M_1; by (4.5), 0 is in M_j and 1 is not in M_j.

- The vertices x_j and x_0 are not adjacent (the only edge inside S+ is {x_0, x_1} and j >= 2), so they have at most
  2 common neighbours. For i in M_j n M_0 the vertex y_i is a common neighbour; and y_j is a common neighbour when
  h_j = 1 (x_j ~ y_j by (4.4), and x_0 ~ y_j because j is in M_0). These vertices are distinct (i != j for i in
  M_j). As 1 is not in M_j, M_j n M_0 = M_j n P. Hence |M_j n P| + h_j <= 2.
- The vertices x_j and x_1 are not adjacent. y_0 is a common neighbour (0 is in M_j and 0 is in M_1), and so is y_i
  for every i in M_j n P' (P' is contained in M_1). Hence 1 + |M_j n P'| <= 2, i.e. |M_j n P'| <= 1.
- M_j contains 0, does not contain 1, and has 4 - h_j elements, so |M_j n {2,...,8}| = 3 - h_j. Since
  {2,...,8} = P u P' and P n P' = {r},

      3 - h_j = |M_j n P| + |M_j n P'| - [r in M_j] <= (2 - h_j) + 1 - [r in M_j].

  Hence r is not in M_j.

The same argument with the roles of 0 and 1 (and of P and P') exchanged shows that r is not in M_j for j in
P' \ {r}. So r is not in M_j for every j in {2,...,8} \ {r}; by (4.5), M_r contains no such j, i.e. M_r is a
subset of {0, 1} and |M_r| <= 2. But |M_r| = 4 - h_r >= 3 by (4.6). Contradiction.

*Case B: a is outer and b is inner.* By Lemma 4.2 the number of inner indices is k = 2 (it is not 0 since b is
inner). Renumber so that a = 0, b = 7, and the other inner index is 8. (The working report uses the label 8
without saying that this relies on k = 2.) By (4.6), |M_0| = 5 and |M_7| = 1 + 4 - 1 = 4.

- 7 is not in M_0: otherwise x_0 would be adjacent to x_7 and to its mate y_7, which is excluded by Lemma 2.1 (c)
  because x_0 != p. By (4.5), 0 is not in M_7.
- 8 is not in M_7: x_7 and y_8 are two vertices of N(p) that are not mates of each other, so they are not adjacent
  (Lemma 2.1 (b)). (This justification is missing in the working report.)

So M_0 is a 5-subset of {1,...,6,8} and M_7 is a 4-subset of {1,...,6}; both lie in the 7-set {1,...,6,8}, so
|M_0 n M_7| >= 2. For i in M_0 n M_7 the vertex y_i is a common neighbour of the adjacent vertices x_0 and x_7,
which have only one. Contradiction. QED

### 4.8 The support is independent and avoids N[p]  [A4, A5]

**Corollary 4.8.** k = 0 and e = 0. Consequently:

(a) S+ and S- are independent sets;
(b) no vertex of S is in N[p]; in particular d(p) = 0;
(c) x_i not~ y_i for every i;
(d) every vertex of S has exactly 4 neighbours in S, and they are on the other side: d-(x_i) = 4, d+(x_i) = 0.

*Proof.* (k, e) is one of (0,0), (0,2), (2,1) (section 4.5), and e is neither 2 (Lemma 4.6) nor 1 (Lemma 4.7). So
(k, e) = (0, 0). (a) e = 0, and S- = sigma S+. (b) k = 0 says that no vertex of S+ is in N(p); apply sigma for S-;
p is not in S. (c) is (4.4) with all indices outer. (d) is (4.2) with d+ = 0. QED

*Remark.* The case k = 2, called "pattern (ii)" in the working reports, is thus excluded by the parity law together
with Lemmas 4.6 and 4.7. Said directly for e = 0: (I1) gives sum_z C(d(z),2) = 18, p contributes C(2,2) = 1 and the
80 other outside vertices contribute an even number, but 17 is odd.

### 4.9 The orbit graph B

Keep the labelling S+ = {x_0,...,x_8}, y_i = sigma x_i. Define a graph B on the index set {0,...,8} by

    i ~_B j   if and only if   x_i ~ y_j.

**Lemma 4.9.** B is a well-defined simple graph, it is 4-regular, and any two distinct indices i, j have at most 2
common neighbours in B. Moreover, for i != j the number of common neighbours of x_i and x_j that lie in S is exactly
the codegree codeg_B(i,j) = |B(i) n B(j)|, where B(i) is the set of B-neighbours of i.

*Proof.* The relation is symmetric by (4.5), and there is no loop by Corollary 4.8 (c). The B-neighbours of i are the
indices j with y_j in N(x_i), and d-(x_i) = 4, so B is 4-regular. Let i != j. The vertices x_i and x_j are distinct
and non-adjacent (Corollary 4.8 (a)), so they have exactly 2 common neighbours in G. Their common neighbours inside
S are in S- (S+ is independent), and y_l is a common neighbour exactly when l is in B(i) n B(j). So
codeg_B(i,j) <= 2. QED

A relabelling of the nine orbits (a permutation g of {0,...,8}, x_i becoming x_{g i} and y_i becoming y_{g i})
replaces B by an isomorphic graph. So B matters only up to isomorphism, and once B is fixed, the labellings that
give exactly this B differ by the elements of Aut(B).

### 4.10 The three possible graphs B

> **Computation 4.10.** Up to isomorphism there are exactly three 4-regular graphs on 9 vertices in which any two
> distinct vertices have at most 2 common neighbours. In each of them every pair of distinct vertices has exactly 1
> or exactly 2 common neighbours (never 0). Representatives, with the vertices 0..8 and the edges written as pairs
> of digits:
>
>     B0:  01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78
>     B1:  01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78
>     B2:  01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78

Further data on these graphs (identification only; not used in the proof except for the codegrees):

| | automorphisms | triangles | codegrees of adjacent pairs | codegrees of non-adjacent pairs | spectrum | name |
|---|---|---|---|---|---|---|
| B0 | 72 | 6 | 18 pairs with 1 | 18 pairs with 2 | 4, 1 (x4), -2 (x4) | K3 x K3 (Paley graph on 9 vertices) |
| B1 | 12 | 8 | 12 with 1, 6 with 2 | 6 with 1, 12 with 2 | 4, 2, 1 (x2), -1 (x2), -2 (x3) | - |
| B2 | 18 | 9 | 9 with 1, 9 with 2 | 9 with 1, 9 with 2 | 4, -2 (x2), the roots of t^3 - 3t - 1 twice | circulant C9(1,2) |

What exactly was computed, and by whom:

- `lemma/t18_REFEREE/ref1_quartic9.py` enumerates all 1,024,380 labelled 4-regular graphs on 9 vertices and sorts
  them into isomorphism classes: 16 classes, all connected. Exactly 3 classes have all codegrees <= 2; they contain
  5040 + 30240 + 20160 = 55440 = 9!/72 + 9!/12 + 9!/18 labelled graphs, they have minimum codegree 1, and they are
  the classes of B0, B1, B2. Each of the other 13 classes has a pair of vertices with 3 or 4 common neighbours.
  **The list of 16 classes comes from this program only.**
- `lemma/t18/enum_S.py` enumerates directly the labelled 4-regular graphs with all codegrees <= 2 in which the
  neighbours of vertex 0 are 1, 2, 3, 4: 792 graphs (= 55440 / C(8,4)), in 3 isomorphism classes.
- `lemma/t18/verify_S.py` enumerates them without that normalisation: 55440 labelled graphs, 3 classes.

So the selection "4-regular, all codegrees <= 2 => B0, B1 or B2" is a finite computation done by three programs.
Two caveats: `verify_S.py` imports the isomorphism-class routine of `enum_S.py` (its enumeration is independent, its
class count is not), and `enum_S.py` / `verify_S.py` impose the condition in the form "common-neighbour budgets on
the 18 vertices of S", which for a bipartite graph between S+ and S- given by B is exactly "all codegrees of B are
<= 2" (two vertices on different sides have no common neighbour in S).

*Hand remark.* A 4-regular graph on 9 vertices is connected (a component has at least 5 vertices), in agreement
with the output of `ref1_quartic9.py`.

**Corollary 4.11.** In a configuration, after a suitable labelling of the nine orbits of the support, B is equal to
one of B0, B1, B2. For each of the three graphs, 18 of the 36 pairs {i, j} have codegree 1 and 18 have codegree 2.

*Proof.* Lemma 4.9 and Computation 4.10. If a pairs have codegree 1 and b pairs codegree 2, then a + b = 36 and
a + 2b = sum_l C(4,2) = 54 (count the pairs inside the neighbourhoods B(l)), so a = b = 18. QED

A pair {i, j} with codeg_B(i,j) = 1 is called a **deficient pair**. In the order used by all the programs (the pairs
{i,j}, i < j, in lexicographic order; the position in this list, from 0 to 17, is the *index* of the pair):

    B0:  01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78      (for B0 the deficient pairs are the edges)
    B1:  01 02 03 04 13 16 18 24 27 28 35 37 45 46 56 57 68 78
    B2:  01 02 05 07 12 16 17 25 28 34 36 37 38 45 46 48 58 67


## 5. The vertices outside the support

From here on: k = 0, e = 0, S+ = {x_i}, S- = {y_i} are independent, S is disjoint from N[p], x_i ~ y_j if and only
if i ~_B j, and B is one of B0, B1, B2 (Corollaries 4.8 and 4.11). There are 99 - 18 = 81 vertices outside S, and p
is one of them.

### 5.1 The classes X_d and the path-count identity

For d >= 0 let X_d be the set of vertices z outside S with d(z) = d, i.e. with exactly d neighbours in S+ and d in
S- (see (4.3)), and n_d = |X_d|. Each X_d is sigma-invariant, because d(sigma z) = d(z). p is in X_0 (Corollary 4.8).
For a vertex v and an integer j let

    a_j(v) = |N(v) n X_j|.

**Lemma 5.1 (path count).** Let z be outside S with d(z) = d. Then

    sum over the neighbours w of z outside S of d(w) = 18 - 5d,     i.e.   a_1(z) + 2 a_2(z) + 3 a_3(z) + ... = 18 - 5d.

In particular d <= 3: X_d is empty for d >= 4. Moreover

    a_0(z) = a_2(z) + 2 a_3(z) + 3d - 4.                                                         (5.1)

*Proof.* Count the pairs (w, s) with s in S+, w ~ z and w ~ s. For a fixed s (s != z since z is outside S) the
number of w is the number of common neighbours of z and s: 1 if s ~ z, 2 otherwise. So the count is
d + 2 (9 - d) = 18 - d. For a fixed neighbour w of z the number of s is d+(w): this is 0 if w is in S+ (S+ is
independent), 4 if w is in S- (Corollary 4.8 (d) and sigma), and d(w) if w is outside S. z has d neighbours in S-.
So 18 - d = 4d + sum_{w ~ z, w outside S} d(w).

The sum is >= 0, so d <= 3; then all outside vertices have d in {0,1,2,3} and the sum is a_1 + 2 a_2 + 3 a_3.
The degree of z is 14 = 2d + a_0 + a_1 + a_2 + a_3. Subtracting the two relations gives (5.1). QED

### 5.2 The sizes n_d

**Lemma 5.2.** n_0 = 9 - n_3, n_1 = 54 + 3 n_3, n_2 = 18 - 3 n_3.

*Proof.* n_0 + n_1 + n_2 + n_3 = 81. By (I2) with e = 0: n_1 + 2 n_2 + 3 n_3 = 90. By (I1) with e = 0 and Q = 0:
n_2 + 3 n_3 = 18. Solve. QED

### 5.3 No outside vertex has d = 3  [N3]

This is placed here, before anything that uses it (referee's remark 2: the working report used it in the proof of
the bound of section 5.6 through a computed fact; the hand proof below removes that dependence).

**Theorem 5.3.** X_3 is empty. Hence (n_0, n_1, n_2) = (9, 54, 18) and every outside vertex has d in {0, 1, 2}.

*Proof.* Suppose z is in X_3. Its 14 - 6 = 8 neighbours outside S have d-values summing to 18 - 15 = 3 (Lemma 5.1),
so at least 5 of them have d = 0: T = N(z) n X_0 has at least 5 elements. The vertex z' = sigma z is in X_3 too,
and z' != z because the only fixed vertex is p and d(p) = 0. So n_3 >= 2 and |X_0| = 9 - n_3 <= 7 (Lemma 5.2).
T' = N(z') n X_0 also has at least 5 elements. T and T' are subsets of X_0, so |T n T'| >= 5 + 5 - 7 = 3: the
distinct vertices z and z' have at least 3 common neighbours, but two distinct vertices have at most 2. QED

The argument uses neither the graph B, nor the neighbourhood of p, nor any computation.

### 5.4 The identities when X_3 is empty  [A8]

Since a_3 = 0 everywhere, write for a vertex v outside S:

    a(v) = a_2(v)  (neighbours in X_2),   b(v) = a_1(v)  (in X_1),   c(v) = a_0(v)  (in X_0).

**Lemma 5.4.**

(a) For z in X_0:  c = a - 4,  b = 18 - 2a;  in particular a >= 4.
    For z in X_1:  c = a - 1,  b = 13 - 2a;  in particular a >= 1.
    For z in X_2:  c = a + 2,  b = 8 - 2a;   in particular a <= 4.

(b) Every vertex of S has exactly 4 neighbours in X_2 and 6 in X_1 (and 4 in S, none in X_0).

(c) Let t be the number of edges with both ends in X_2. Then the number of edges inside X_0 is also t, and

        sum_{X_2} a = 2t,     sum_{X_0} a = 36 + 2t,     sum_{X_1} a = 144 - 4t.

(d) sum over all 81 outside vertices of a^2 = 576 - 2t, and

    (*)   sum_{X_0} (a - 4)^2 + sum_{X_1} (a - 2)(a - 3) + sum_{X_2} a (a - 1) = 36.

    Each of the three sums is >= 0, and t <= 9.

*Proof.* (a) Lemma 5.1 with a_3 = 0 gives b + 2a = 18 - 5d and c = a + 3d - 4. The inequalities follow from
c >= 0 and b >= 0.

(b) Let x be in S+. It has 4 neighbours in S- and none in S+, hence 10 neighbours outside S, each with d >= 1
(it is adjacent to x), so none in X_0. Count the pairs (w, s) with s in S+ \ {x}, w ~ x and w ~ s: each of the 8
vertices s is non-adjacent to x, so the count is 16. A neighbour w of x in S- has 3 neighbours in S+ other than x;
an outside neighbour w has d(w) - 1. So 16 = 12 + sum_{w ~ x, w outside} (d(w) - 1), i.e. the ten values d(w), each 1
or 2, sum to 14: four are 2 and six are 1. Apply sigma for S-.

(c) sum_{X_2} a counts each edge inside X_2 twice. The number of edges between X_0 and X_2 is
sum_{s in X_2} c(s) = sum_{X_2} (a + 2) = 2t + 36, and it is also sum_{z in X_0} a(z). The number of edges inside X_0
is half of sum_{X_0} c = sum_{X_0} (a - 4) = 36 + 2t - 36 = 2t. The number of edges between X_1 and X_2 is
sum_{X_2} b = sum_{X_2} (8 - 2a) = 144 - 4t = sum_{X_1} a.

(d) sum over all 99 vertices v of |N(v) n X_2|^2 is the number of triples (v, s, s') with s, s' in X_2 and v adjacent
to both, i.e. sum over the ordered pairs (s, s') of X_2 of |N(s) n N(s')|: 14 for each of the 18 pairs with s = s',
and 2 - [s ~ s'] for each of the 18 * 17 ordered pairs with s != s'. Total 252 + 612 - 2t = 864 - 2t. The 18
vertices of S contribute 16 each by (b). So the outside vertices contribute 576 - 2t. Then, using (c) and
n_0 = 9, n_1 = 54,

    sum_{X_0}(a-4)^2 + sum_{X_1}(a-2)(a-3) + sum_{X_2} a(a-1)
       = (576 - 2t) - 8 (36 + 2t) + 16 * 9 - 5 (144 - 4t) + 6 * 54 - 2t = 36.

For an integer a, (a-2)(a-3) >= 0 and a(a-1) >= 0. So sum_{X_0} (a-4)^2 <= 36; by the Cauchy-Schwarz inequality on
the 9 terms, (2t)^2 = (sum_{X_0} (a - 4))^2 <= 9 * 36, so t <= 9. QED

Identity (*) is used below only as a filter inside some programs ((F7) of Lemma 7.5 and (C4) of Lemma 8.3), where
it turns out to remove nothing. It is not needed for the hand part.

### 5.5 The profile of the neighbourhood of p

N(p) is disjoint from S and consists of the 7 orbits {a_c, b_c} (Lemma 2.1). Put

    delta_c = d(a_c) = d(b_c)   (in {0,1,2} by Theorem 5.3),      h_j = the number of c with delta_c = j   (j = 0,1,2).

So N(p) n X_j consists of h_j orbits (2 h_j vertices), and a_2(p) = 2 h_2.

**Lemma 5.5.** sum_c delta_c = 9, hence h_2 = 2 + h_0 and h_1 = 5 - 2 h_0, and (h_2, h_1, h_0) is one of

    (2,5,0),   (3,3,1),   (4,1,2).

This triple is called the **profile** of the configuration. The list is exhaustive.

*Proof.* Each of the 9 vertices of S+ is outside N[p], so it has exactly 2 neighbours in N(p) (Corollary 2.2).
Hence sum over v in N(p) of d+(v) = 18, i.e. 2 sum_c delta_c = 18. So h_1 + 2 h_2 = 9 and h_0 + h_1 + h_2 = 7, which
gives h_2 = 2 + h_0, h_1 = 5 - 2 h_0, and h_1 >= 0 forces h_0 in {0, 1, 2}. The list is exhaustive because
delta_c <= 2, which is Theorem 5.3. QED

### 5.6 The bound h_0 <= 1; profile (4,1,2) is impossible  [A9]

**Lemma 5.6.** sum over the 14 neighbours w of p of a_2(w) = 36 - 2 h_2. Moreover, for a neighbour w of p:

- if w is in X_2 then a_2(w) >= 1;
- if w is in X_1 then a_2(w) >= 2;
- if w is in X_0 then a_2(w) >= 6.

*Proof.* sum_{w ~ p} a_2(w) is the number of pairs (w, s) with s in X_2, w ~ p, w ~ s, i.e. the sum over s in X_2 of
the number of common neighbours of p and s. p is not in X_2, so this number is 2 - [s ~ p], and the sum is
2 * 18 - a_2(p) = 36 - 2 h_2.

If w is in N(p) n X_2, its mate sigma w is adjacent to w (Lemma 2.1 (a)) and lies in X_2: a_2(w) >= 1.
If w is in N(p) n X_1, then c(w) = a_2(w) - 1 by Lemma 5.4 (a), and p is a neighbour of w in X_0: c(w) >= 1.
If w is in N(p) n X_0, then c(w) = a_2(w) - 4, and p and sigma w are two neighbours of w in X_0: c(w) >= 2. QED

**Proposition 5.7.** h_0 <= 1. So profile (4,1,2) is impossible, for B0, B1 and B2. In profile (3,3,1) all the
inequalities of Lemma 5.6 are equalities: a_2 = 1 on N(p) n X_2, a_2 = 2 on N(p) n X_1, a_2 = 6 on N(p) n X_0.

*Proof.* By Lemma 5.6, 2 h_2 * 1 + 2 h_1 * 2 + 2 h_0 * 6 <= 36 - 2 h_2, i.e. 4 h_2 + 4 h_1 + 12 h_0 <= 36. With
h_2 = 2 + h_0 and h_1 = 5 - 2 h_0 this reads 28 + 8 h_0 <= 36, so h_0 <= 1. For h_0 = 1, i.e. profile (3,3,1), the
sum of the lower bounds is 6 * 1 + 6 * 2 + 2 * 6 = 30 and the exact value is 36 - 2 * 3 = 30: the two are equal, so
every lower bound is attained. For h_0 = 2, i.e. profile (4,1,2), the lower bounds sum to 8 + 4 + 24 = 36 while the
exact value is 36 - 8 = 28: impossible. QED

This is a pure hand proof: it uses Theorem 5.3 (through Lemma 5.4 (a) and delta_c <= 2) and nothing computed.
What remains is profile (3,3,1) (section 7) and profile (2,5,0) (section 8).


## 6. The tests used by the computations

A computation of sections 7 and 8 enumerates the possible induced subgraphs of G on certain vertex sets and discards
those that violate a necessary condition. Three kinds of necessary conditions are used. **Both PSD matrices of 6.1
are used** (referee's remark 3: the working report says in one place that the violated matrix is always the first
one; that sentence is wrong, see section 7.6).

### 6.1 Two positive-semidefinite matrices

    M1 = 9 (3I - A) + J = 27 I - 9 A + J,          M2 = 11 (4I + A) - 2J = 44 I + 11 A - 2 J.

**Lemma 6.1.** M1 = 63 E_{-4} and M2 = 77 E_3. Both are PSD, M1 has rank 44 and M2 has rank 54. For every vertex set
Y the principal submatrices M1[Y] and M2[Y] are PSD.

*Proof.* M1 and M2 are polynomials in A and J, so they act as scalars on the three eigenspaces. On the all-ones
vector (A = 14, J = 99): M1 = 27 - 126 + 99 = 0 and M2 = 44 + 154 - 198 = 0. On V_3 (A = 3, J = 0): M1 = 27 - 27 = 0
and M2 = 44 + 33 = 77. On V_{-4} (A = -4, J = 0): M1 = 27 + 36 = 63 and M2 = 44 - 44 = 0. A principal submatrix of a
PSD matrix is PSD. QED

M1[Y] and M2[Y] depend only on the induced subgraph of G on Y: with A_Y its adjacency matrix,
M1[Y] = 27 I - 9 A_Y + J and M2[Y] = 44 I + 11 A_Y - 2J (I and J of size |Y|).

A **PSD violation** on Y is an integer vector x indexed by Y with x^T M1[Y] x < 0 or x^T M2[Y] x < 0. Checking a
given violation is one integer computation.

### 6.2 The common-neighbour budget

**Lemma 6.2.** Let Y be a vertex set and let H' be a graph on Y all of whose edges are edges of G (a spanning
subgraph of the induced subgraph G[Y]). Then for any two distinct vertices u, v of Y,

    |N_H'(u) n N_H'(v)| <= 2 - [u ~ v in H'].

*Proof.* N_H'(u) n N_H'(v) is contained in N(u) n N(v), which has 1 element if u ~ v in G and 2 otherwise. If
u ~ v in H' then u ~ v in G and the bound is 1. If u not~ v in H' the bound 2 holds in both cases. QED

A pair u, v violating the inequality is a **budget violation**. The point of allowing a spanning subgraph is that a
partially specified graph (some adjacencies not yet decided and provisionally absent) may be rejected by a budget
violation: adding edges can only increase the numbers of common neighbours and decrease the bound. A PSD violation,
on the contrary, is meaningful only on a vertex set all of whose adjacencies are decided.

### 6.3 Determined sets, and what a computation proves

Let D be some data extracted from a configuration (for instance the matching tau of section 7.1). A vertex set Y
(described in terms of the configuration, e.g. "S u {p} u X_2") is **determined by D** if the induced subgraph G[Y],
with the names of its vertices, can be written down from D alone. For every determined set used below, the text
gives a table that says, for every pair of classes of vertices of Y, whether the adjacency is a parameter in D or
is forced, and by which lemma.

The computations have the following form. A finite list L of candidate data D is defined (all values of the
parameters). For each D in L the graph on Y is built and tested; D is **rejected** if a budget violation or a PSD
violation is found on Y or on a subset of Y (for partial data: a budget violation on the partial graph, or a PSD
violation on a subset whose adjacencies are all decided), or if a forced number proved in the text fails. The data
that are not rejected are the **survivors**. Since the data of a configuration pass every necessary condition:

    the data D of any configuration belong to the list of survivors.                              (6.1)

So an empty list of survivors is a contradiction, and a non-empty list reduces the problem to its members.

Exactness. According to their sources (for the programs read for this text) or their headers (for the others; see
section 9.3, item 3), in all the programs of the repository a rejection is exact: a budget violation is an integer
count, and a PSD violation is an integer vector x whose quadratic form is evaluated in integer arithmetic (or, in
some programs, an exact elimination or an exact characteristic polynomial). A candidate for which no violation is found
is kept; for most programs this "kept" rests on a floating-point eigenvalue (smallest eigenvalue above a threshold
of about -10^-7) and **is not a proof of positive semidefiniteness and is never used as one**: keeping too much can
only make the list of survivors larger, which is harmless for (6.1). The referee's own programs are different: they
reject on the floating-point eigenvalue alone, without an exact certificate; they are used here only as count
checks (section 9.3).

### 6.4 The rank bound  [P2]

Let P be the permutation matrix of sigma (P e_x = e_{sigma x}). P is symmetric, P^2 = I, and P commutes with A
(sigma is an automorphism) and with J.

**Lemma 6.3.** trace(P E_{-4}) = 0 and trace(P E_3) = 0. Hence sigma acts on V_{-4} with the eigenvalues +1 and -1,
each with multiplicity 22, and on V_3 with the eigenvalues +1 and -1, each with multiplicity 27.

*Proof.* trace P is the number of fixed vertices, 1. trace(PA) = sum_x A_{x, sigma x} is the number of vertices x
with x ~ sigma x, which is |N(p)| = 14 by Lemma 2.1 (a). trace(PJ) = 99. By Lemma 6.1,

    trace(P E_{-4}) = (27 * 1 - 9 * 14 + 99) / 63 = 0,       trace(P E_3) = (44 * 1 + 11 * 14 - 2 * 99) / 77 = 0.

P preserves V_{-4} and V_3 and has eigenvalues +-1 there; the trace is the difference of the two multiplicities,
and their sums are 44 and 54. QED

**Proposition 6.4 (rank bound).** Let Y be a sigma-invariant vertex set, and let R be a set containing exactly one
vertex of each orbit {x, sigma x} contained in Y (x != p).

(a) (odd part) The |R| x |R| integer matrix

        G_odd = 3 I - A[R,R] + A[R, sigma R]     (entry (x,y): 3 [x = y] - [x ~ y] + [x ~ sigma y])

    has rank at most 22. In particular, if |R| >= 23 then every 23 x 23 principal minor of G_odd is 0; if |R| = 23,
    det G_odd = 0.

(b) (even part) Let the vectors g_x = e_x + e_{sigma x} (x in R), together with g_p = e_p if p is in Y, be the
    "even generators". The matrix G_even with entries g^T M1 g' has rank at most 22. Explicitly, for x != y in R:
    G_even(x,y) = 4 - 18 ([x ~ y] + [x ~ sigma y]),  G_even(x,x) = 58 - 18 [x ~ sigma x],
    G_even(p,x) = 2 - 18 [p ~ x],  G_even(p,p) = 28.

*Proof.* (a) For x in R put u_x = e_x - e_{sigma x}. Since M1 commutes with P, M1(sigma x, sigma y) = M1(x, y) and
M1(sigma x, y) = M1(x, sigma y), so

    u_x^T M1 u_y = 2 (M1(x,y) - M1(x, sigma y)) = 2 (27 [x = y] - 9 [x ~ y] + 9 [x ~ sigma y]) = 18 G_odd(x,y)

(the terms +1 coming from J cancel, and x = sigma y does not happen for x, y in R). On the other hand
M1 = 63 E_{-4} and E_{-4} is a symmetric idempotent, so u_x^T M1 u_y = 63 (E_{-4} u_x) . (E_{-4} u_y): the matrix
18 G_odd is 63 times the Gram matrix of the vectors E_{-4} u_x. These vectors lie in V_{-4} and satisfy
P E_{-4} u_x = E_{-4} P u_x = - E_{-4} u_x, so they lie in the (-1)-eigenspace of sigma on V_{-4}, which has
dimension 22 by Lemma 6.3. A Gram matrix of vectors in a space of dimension 22 has rank at most 22.

(b) The same computation with g_x: g^T M1 g' = 63 (E_{-4} g) . (E_{-4} g'), and the vectors E_{-4} g lie in the
(+1)-eigenspace of sigma on V_{-4}, of dimension 22. The explicit entries are 2 (M1(x,y) + M1(x, sigma y)),
M1(p,x) + M1(p, sigma x) and M1(p,p). QED

G_odd and G_even depend only on the induced subgraph on Y and on sigma. So for a sigma-invariant *determined* set Y
with at least 23 orbits, "some 23 x 23 principal minor of G_odd is non-zero" is a contradiction, checked by one
exact integer determinant. Positive semidefiniteness does not see this condition: the matrix can be positive
definite (see section 8.6). The analogous bounds for M2 (odd and even parts of rank at most 27) are true by the same
proof and are not used.


## 7. Profile (3,3,1)

Section 7.1 is common to sections 7 and 8: it describes X_2 and the first stage of both enumerations.

### 7.1 X_2, the matching tau of the deficient pairs, and stage 1

Notation: for a set U of indices, x_U = {x_i : i in U} and y_U = {y_i : i in U}.

**Lemma 7.1.** (a) For every deficient pair U = {i, j} there is exactly one vertex outside S adjacent to both x_i and
x_j. Call it s_U. It lies in X_2 and N(s_U) n S+ = x_U. The map U -> s_U is a bijection from the 18 deficient pairs
onto X_2. A pair {i, j} that is not deficient has no common neighbour outside S.

(b) There is a permutation tau of the set of deficient pairs such that, for every deficient pair U,

    N(s_U) n S- = y_{tau U}     and     sigma s_U = s_{tau U}.

tau is an involution without fixed point.

*Proof.* (a) Let i != j. The vertices x_i and x_j have exactly 2 common neighbours, of which codeg_B(i,j) lie in S
(Lemma 4.9); codeg_B(i,j) is 1 or 2 (Corollary 4.11). So they have exactly one common neighbour outside S if
{i,j} is deficient and none otherwise. A vertex outside S adjacent to x_i and x_j has d >= 2, hence d = 2 (Theorem
5.3): it is in X_2 and its neighbours in S+ are exactly x_i and x_j. Conversely a vertex z of X_2 has exactly two
neighbours x_i, x_j in S+; it is an outside common neighbour of them, so {i,j} is deficient and z = s_{i,j}. The map
is injective because U is read off from N(s_U) n S+.

(b) sigma s_U is in X_2 and N(sigma s_U) n S+ = sigma (N(s_U) n S-). So if V denotes the set of the two indices l
with y_l ~ s_U, then sigma s_U is a vertex of X_2 whose neighbours in S+ are x_V; by (a), V is a deficient pair and
sigma s_U = s_V. Put tau U = V. Since sigma^2 = 1, tau^2 = 1. If tau U = U, then sigma s_U = s_U, so s_U = p; but p
is in X_0. QED

So the 9 orbits of X_2 are the 9 pairs {U, tau U}; such a pair of deficient pairs is called a **rectangle**, and
the vertex s_U is said to be of type (U ; tau U): it is adjacent to x_U and y_{tau U}; its mate is of type
(tau U ; U). tau is a perfect matching of the 18 deficient pairs into 9 rectangles. Once B is fixed, the adjacency
between S and X_2 is determined by tau.

**Lemma 7.2 (necessary conditions on tau; these are the stage-1 tests).**

(R1) For every deficient pair U, with V = tau U: every index i of U has at most one B-neighbour in V, and every
     index l of V has at most one B-neighbour in U.

(R2) For all indices i, l in {0,...,8}, the case i = l included: the number of deficient pairs U with i in U and
     l in tau U is at most 2 - [i ~_B l].

(R3) The orbit {s_U, s_V} (V = tau U) is contained in N(p) if and only if s_U ~ s_V; and in that case U n V is
     empty.

*Proof.* (R1) Let s = s_U and i in U, so s ~ x_i. Every y_l with l in V n B(i) is adjacent to s (l in V) and to
x_i (l in B(i)): it is a common neighbour of the adjacent pair s, x_i, which has only one. The second half is the
same with the adjacent pair s, y_l and the vertices x_i, i in U n B(l).

(R2) Every such s_U is adjacent to x_i and to y_l. These two vertices are distinct, and they are adjacent if and
only if i ~_B l (for i = l they are not adjacent, by Corollary 4.8 (c), and [i ~_B i] = 0). So they have exactly
2 - [i ~_B l] common neighbours, and the vertices s_U are distinct for distinct U.

(R3) The first statement is Lemma 2.1 (a). If s_U ~ s_V, their only common neighbour is p (Lemma 2.1 (c)); for
i in U n V the vertex x_i would be adjacent to s_U and to s_V. QED

*Remarks on the tests.* The header of the first stage-1 program lists four tests, by reference to a note that is
not in the repository; here is what they are. Its test (i) is (R1). Its test (iii), "cell budgets", is (R2): the
"cell" (i,l) is the pair of vertices x_i, y_l. Its test (i'), |U n tau U| <= 1, is automatic, since U and tau U are
two distinct 2-sets. Its test (P) requires in addition that the type (U ; tau U) be in the list `types.json`; that
list was produced by a test on the 21 vertices S u {p, s_U, s_{tau U}}, in at least one of the two statuses of the
orbit (inside or outside N(p)); see section 9.3, item 6, for what that test contains. Computation 7.3 below shows
that (P) removes nothing.

Call an unordered pair {U, V} of distinct deficient pairs an **admissible rectangle** if (R1) holds for it (the
condition is symmetric in U and V), and **usable in N(p)** if moreover U n V is empty. Call a fixed-point-free
involution tau of the 18 deficient pairs an **admissible matching** if its 9 rectangles are admissible and (R2)
holds. By Lemma 7.2 the tau of a configuration is an admissible matching, and the orbits of X_2 contained in N(p)
correspond to rectangles of tau that are usable in N(p).

Aut(B) acts on the deficient pairs and hence on the admissible matchings. By the remark after Lemma 4.9, relabelling
the nine orbits of the support by an element g of Aut(B) keeps B and replaces tau by its image under g. Hence:

    in a configuration with orbit graph B one may assume, after relabelling, that tau is any chosen
    representative of its orbit under Aut(B).                                                      (7.1)

> **Computation 7.3 (stage 1).** For each of B0, B1, B2 there are 99 admissible rectangles, 63 of which are usable
> in N(p). The numbers of admissible matchings and of their orbits under Aut(B) are:
>
> | | B0 | B1 | B2 |
> |---|---|---|---|
> | admissible matchings tau | 25514 | 13799 | 9229 |
> | order of Aut(B) | 72 | 12 | 18 |
> | orbits under Aut(B) | 425 | 1259 | 528 |
>
> One representative of each orbit is stored in `lemma/t18/r2_tau_<s>.json` (s = 0, 1, 2 for B0, B1, B2). "Matching
> #n" below means the n-th entry (from 0) of that file.

Programs (four, in agreement on every number of the table):

- `lemma/t18/r2_stage1.py`: tests (R1), (i'), (R2) and (P); it writes `r2_tau_<s>.json`.
- `lemma/t18/r3_verify.py stage1`: another algorithm, with its own 21-vertex test; it also checks that the stored
  representatives are admissible matchings, pairwise inequivalent, one in each orbit.
- `lemma/t18_VERIF331/v1_stage1.py`: runs twice, with (R1) and (R2) only, and with an exact 21-vertex PSD test in
  addition; the two runs give the same 99 rectangles and the same numbers of matchings and orbits. It builds its
  own list of representatives.
- `lemma/t18_REFEREE/ref2_stage1.py`: (R1) and (R2) only; `ref10_tau_files.py` checks that the stored
  representatives are the referee's own, in the same order.

Test (P) removes nothing: the first program, which applies it, finds 99 admissible rectangles and the same numbers
of matchings as the programs that apply (R1) and (R2) only.

All the later programs except those of `lemma/t18_VERIF331` and `lemma/t18_REFEREE` read the representatives from
`r2_tau_<s>.json`.

### 7.2 The forced structure of profile (3,3,1)  [A10]

In this section the profile is (h_2, h_1, h_0) = (3, 3, 1). Notation:

    A_p  = N(p) n X_2      (6 vertices, 3 orbits);
    W    = N(p) n X_1      (6 vertices, 3 orbits);
    {z_0, sigma z_0} = N(p) n X_0;
    X_2' = X_2 \ A_p       (12 vertices, 6 orbits);
    X_0' = X_0 \ {p, z_0, sigma z_0}   (6 vertices, 3 orbits; X_0 has 9 vertices by Theorem 5.3);
    A_{z_0} = N(z_0) n X_2;
    f_i  = the number of vertices of A_p adjacent to x_i.

**Lemma 7.4.**

(a) A vertex of A_p has no neighbour in X_2 except its mate. It has exactly 3 neighbours in X_0: p and two vertices
    of X_0'.

(b) A vertex w of W has exactly 2 neighbours in X_2; they lie in X_2' and they are not mates of each other. Its
    only neighbour in X_0 is p. It has exactly one neighbour x_i in S+ and one neighbour y_j in S-, and i != j;
    w is said to be of type (i ; j), and sigma w is of type (j ; i). The three orbits of W have three different
    unordered types {i, j}.

(c) z_0 has no neighbour in S, in A_p or in W; its neighbours in X_0 are exactly p and sigma z_0; A_{z_0} has 6
    elements, is contained in X_2' and contains exactly one vertex of each of the 6 orbits of X_2';
    N(sigma z_0) n X_2 = sigma A_{z_0} is the complement of A_{z_0} in X_2'.

(d) A vertex s of X_2' is adjacent to exactly one of z_0, sigma z_0, to exactly one vertex of W, to no vertex of
    A_p, and to exactly a_2(s) + 1 vertices of X_0'.

(e) A vertex q of X_0' has no neighbour in S and is not adjacent to p, to sigma q, to z_0, to sigma z_0, or to any
    vertex of W. It has exactly 2 neighbours in A_p, and they lie in two different orbits of A_p. a_2(q) >= 4, and q
    has exactly a_2(q) - 4 neighbours in X_0'.

(f) For every i, x_i has exactly f_i neighbours in A_p and 2 - f_i in W. In particular f_i <= 2.

*Proof.* By Proposition 5.7, a_2 = 1 on A_p, a_2 = 2 on W and a_2 = 6 on z_0 and sigma z_0. Recall that inside N(p)
a vertex is adjacent only to its mate (Lemma 2.1 (b)), and that mates lie in the same class X_d.

(a) The mate is a neighbour in X_2 and a_2 = 1. By Lemma 5.4 (a), c = a + 2 = 3; p is one of the three neighbours in
X_0; z_0 and sigma z_0 are vertices of N(p) other than the mate, so they are not neighbours; the two remaining ones
are in X_0'.

(b) a_2(w) = 2 and c(w) = a_2(w) - 1 = 1, and p is a neighbour of w in X_0. The two neighbours in X_2 are not in
A_p, which is inside N(p). If they were s and sigma s, then w would be a common neighbour of s and sigma s, where s
is outside N[p]; by Lemma 2.1 (d) the common neighbours of s and sigma s are outside N[p], but w is in N(p). The
same argument shows i != j: if i = j, then w would be a common neighbour of x_i and its mate y_i, and x_i is outside
N[p]. sigma w is adjacent to sigma x_i = y_i and sigma y_j = x_j. Finally let w and w' be in two different orbits
of W and suppose they have the same unordered type; replacing w' by its mate we may assume that both are of type
(i ; j). Then w and w' are distinct, not adjacent (they are in N(p) and not mates), and have the three common
neighbours p, x_i, y_j: impossible.

(c) z_0 is in X_0, so it has no neighbour in S. Inside N(p) it is adjacent only to sigma z_0. c(z_0) = 6 - 4 = 2 and
p, sigma z_0 are two neighbours in X_0. So A_{z_0} is a 6-subset of X_2'. Applying sigma, the neighbours of
sigma z_0 in X_2 form sigma A_{z_0}. A vertex in both A_{z_0} and sigma A_{z_0} would be a common neighbour of z_0
and sigma z_0 other than p, which Lemma 2.1 (c) forbids. So A_{z_0} and sigma A_{z_0} are disjoint 6-subsets of the
12-set X_2': they are complementary, and A_{z_0} contains exactly one vertex of each orbit.

(d) The first statement is (c). s is outside N[p], so it has exactly 2 neighbours in N(p) (Corollary 2.2): none in
A_p by (a), exactly one in {z_0, sigma z_0}, hence exactly one in W. By Lemma 5.4 (a) s has a_2(s) + 2 neighbours in
X_0; p is not one of them, exactly one of z_0, sigma z_0 is; the other a_2(s) + 1 are in X_0'.

(e) q is in X_0: no neighbour in S. q is not in N(p), so q not~ p and q not~ sigma q (Lemma 2.1 (a)). By (a) there
are exactly 6 * 2 = 12 edges between A_p and X_0'. By Corollary 2.2 each of the 6 vertices of X_0' has exactly 2
neighbours in N(p), hence at most 2 in A_p; as the total is 12, each has exactly 2 neighbours in A_p, and
therefore **none in the rest of N(p), i.e. none in W u {z_0, sigma z_0}**. (This consequence is used for the 45-
and 51-vertex sets and is not stated in the working report: referee's remark 7.) The two neighbours in A_p are not
mates of each other, by Lemma 2.1 (c). By Lemma 5.4 (a), a_2(q) >= 4 and q has a_2(q) - 4 neighbours in X_0; they
are none of p, z_0, sigma z_0, so they are in X_0'.

(f) x_i is outside N[p]: it has exactly 2 neighbours in N(p) = A_p u W u {z_0, sigma z_0}, and none of them is z_0
or sigma z_0. QED

### 7.3 The determined sets of 39, 45 and 51 vertices

    Y1    = S u {p} u X_2 u {z_0, sigma z_0}        (18 + 1 + 18 + 2 = 39 vertices);
    Y     = Y1 u X_0' = S u X_0 u X_2               (45 vertices);
    Y u W                                            (51 vertices).

All three are sigma-invariant. The data:

- **tau**, the matching of section 7.1 (a representative, by (7.1));
- **F**, the set of the three rectangles of tau whose orbits form A_p; each must be usable in N(p) (Lemma 7.2 (R3));
- **H**, the set of edges inside X_2'. It is invariant under sigma (which acts on X_2 by s_U -> s_{tau U}) and
  contains no mate edge (Lemma 2.1 (a));
- **A_{z_0}**, a choice of one vertex in each of the 6 orbits of X_2'. Exchanging the names z_0 and sigma z_0
  replaces A_{z_0} by its complement; the programs fix the names by requiring that A_{z_0} contain a prescribed
  vertex of the first orbit, so there are 2^5 choices;
- **the rows**: for each q in X_0' the set R_q = N(q) n X_2, with R_{sigma q} = sigma R_q; and **G'**, the set of
  edges inside X_0', invariant under sigma. (rows, G') is called a **table**;
- **for W**: the three types (i ; j), and for each w in W the 2-set K_w = N(w) n X_2', with K_{sigma w} = sigma K_w.

**Lemma 7.5.** Y1 is determined by (tau, F, H, A_{z_0}); Y is determined by these data and the table; Y u W is
determined by all the data. More precisely every adjacency between two vertices of Y u W is given by the following
list, in which "parameter" means "read from the data" and every other entry is forced by the lemma quoted.

| pair of classes | adjacency | reason |
|---|---|---|
| S+ with S+, S- with S- | none | Corollary 4.8 (a) |
| S+ with S- | x_i ~ y_j iff i ~_B j | definition of B |
| S with p | none | Corollary 4.8 (b) |
| S with X_2 | s_U ~ x_i iff i in U; s_U ~ y_l iff l in tau U | parameter tau (Lemma 7.1) |
| p with X_2 | exactly the 6 vertices of A_p | parameter F |
| A_p with A_p | the 3 mate edges only | Lemma 2.1 (b) |
| A_p with X_2' | none | Lemma 7.4 (a) |
| X_2' with X_2' | parameter H; no mate edge | Lemma 2.1 (a) |
| z_0, sigma z_0 with p; z_0 with sigma z_0 | adjacent | definition; Lemma 2.1 (a) |
| z_0, sigma z_0 with S, with A_p | none | Lemma 7.4 (c) |
| z_0 with X_2' | exactly A_{z_0}; sigma z_0: the complement | parameter A_{z_0} (Lemma 7.4 (c)) |
| X_0' with S, p, z_0, sigma z_0 | none | Lemma 7.4 (e) |
| q with sigma q (q in X_0') | not adjacent | Lemma 7.4 (e) |
| X_0' with X_2 | parameter rows | - |
| X_0' with X_0' | parameter G' | - |
| W with p | adjacent | definition |
| W with W | the 3 mate edges only | Lemma 2.1 (b) |
| W with A_p, with z_0, sigma z_0 | none | Lemma 2.1 (b) |
| W with X_0' | none | Lemma 7.4 (e) (or (b)) |
| W with S | w ~ x_i, y_j only; sigma w ~ x_j, y_i only | parameter types (Lemma 7.4 (b)) |
| W with X_2' | parameter K_w | - |

Moreover the data satisfy the following **forced numbers**:

- (F1) each of the three rectangles of F is usable in N(p);
- (F2) every vertex of X_2 has at most 4 neighbours in X_2 (Lemma 5.4 (a));
- (F3) every s in A_p has exactly 2 neighbours in X_0'; every s in X_2' has exactly (number of its H-neighbours) + 1;
- (F4) every q in X_0' has exactly 2 neighbours in A_p, |R_q| >= 4, and exactly |R_q| - 4 neighbours in G';
- (F5) the three unordered types are distinct, i != j in each, and every index i occurs in exactly 2 - f_i of the
  three unordered types (x_i has exactly one neighbour in each orbit of W whose unordered type contains i);
- (F6) each K_w has 2 elements and contains no mate pair; every vertex of X_2' lies in K_w for exactly one w in W;
- (F7) sum over X_2 of a_2 (a_2 - 1) <= 24.

*Proof.* The table is a restatement of the lemmas quoted; note that on X_2 one has a_2(s) = 1 for s in A_p and
a_2(s) = the number of H-neighbours of s for s in X_2'. (F1) is Lemma 7.2 (R3). (F3) is Lemma 7.4 (a), (d). (F4) is
Lemma 7.4 (e). (F5) is Lemma 7.4 (b), (f): a vertex of W of type (i ; j) contributes one neighbour in W to x_i and
its mate, of type (j ; i), one to x_j. (F6) is Lemma 7.4 (b), (d). (F7): in identity (*) of Lemma 5.4 the three
vertices p, z_0, sigma z_0 of X_0 have a_2 = 6 (for p: a_2(p) = 2 h_2 = 6) and contribute 3 * (6 - 4)^2 = 12 to the
first sum; all other terms of the first two sums are >= 0; so the third sum is at most 36 - 12 = 24. QED

(F2) and (F7) are the only filters, in the programs read for this text (`r2_hfirst.py`, `v2_stage2.py`,
`v3_stage34.py`), that are not budgets, PSD violations or the structure of Lemma 7.4: `r2_hfirst.py` uses (F2) and
(F7) in step 2; `v2_stage2.py` uses neither (its 39-vertex survivors are defined by budgets and PSD on Y1 alone);
`v3_stage34.py` uses (F2) in step 3 and only records (*). Since the two programs produce the same 39-vertex
survivors (section 7.5), (F2) and (F7) remove nothing there.

### 7.4 What is enumerated, and the result

> **Computation 7.6.** For each B in {B0, B1, B2} and each representative tau of Computation 7.3:
>
> - step 1: all sets F of three rectangles of tau that are usable in N(p), such that the graph on the 25 vertices
>   S u {p} u A_p has no budget violation;
> - step 2: for each such (tau, F), all (H, A_{z_0}) such that the graph on Y1 (39 vertices) has no budget violation
>   and no PSD violation for M1 and M2 is found; these (tau, F, H, A_{z_0}) are the **39-vertex survivors**;
> - step 3: for each 39-vertex survivor, all tables satisfying (F3), (F4); among them those for which the graph on
>   Y (45 vertices) has no budget violation; among those, the ones for which no PSD violation is found on Y;
> - step 4: for each table of the last kind, all (types, K) satisfying (F5), (F6); among them those for which the
>   graph on Y u W (51 vertices) has no budget violation; among those, the ones with no PSD violation.
>
> Result: the last list is empty for B0, B1 and B2. The counts are in the table of section 7.5.

**Proposition 7.7.** Profile (3,3,1) is impossible for B0, B1 and B2.

*Proof.* Suppose a configuration has profile (3,3,1) and orbit graph B. By (7.1) its matching tau may be taken to be
one of the representatives. By Lemma 7.5 its sets Y1, Y, Y u W are determined by its data, which satisfy (F1)-(F7),
and by Lemmas 6.1 and 6.2 the corresponding graphs have no budget violation and no PSD violation. So its data
survive all four steps (this is (6.1)), contradicting Computation 7.6. QED

Status: hand part (Lemmas 7.1, 7.2, 7.4, 7.5) plus Computations 7.3 and 7.6.

### 7.5 Counts, and the number of implementations of each line

Implementations:

- **I1** = `lemma/t18/r2_hfirst.py` (steps 1-2: H is completed first, then A_{z_0}), `lemma/t18/r2_stage2.py` run with
  the switch R2_SURV (step 3, restricted to the 39-vertex survivors), `lemma/t18/r2_ext2.py` (step 4, by a pruned
  search). These programs read `structures.json`, `types.json` and `r2_tau_<s>.json`.
- **I2** = `lemma/t18_VERIF331/`: `v1_stage1.py` (own stage 1 and own representatives), `v2_stage2.py` (steps 1-2:
  the orbits of X_2' are added one at a time, each with its side relative to z_0, so A_{z_0} is chosen before H is
  complete), `v3_stage34.py` (step 3; it also adds W directly to the 39 vertices and combines), `v7_step4_direct.py`
  (step 4: every (types, K), budgets as the only pre-filter, then an exact PSD decision). Written from the
  mathematical description; no program of `lemma/t18` was opened; the output files of I1 were read only for the
  comparison of the sets (`v4_compare39.py`, `v4_compare45.py`). In I2 a rejection is an integer vector re-evaluated
  in Python integers or an exact characteristic polynomial, and the acceptances at 39, 45 and 51 vertices are
  decided by the exact characteristic polynomial.
- **I3** = `lemma/t18_B2/e331.py` (B2 only, steps 1-3); shares no code with I1 and does not read `types.json`.
- **R** = the referee's programs `lemma/t18_REFEREE/ref2_stage1.py`, `ref6_p331.py`, `ref7_p331_ext.py`,
  `ref7b_p331_ext.py` (own model, no repository code; floating-point PSD rejections: a count check only).

| line | B0 | B1 | B2 | programs |
|---|---|---|---|---|
| 0. admissible matchings / orbits (Computation 7.3) | 25514 / 425 | 13799 / 1259 | 9229 / 528 | 4 programs (section 7.1) |
| 1. pairs (tau, F) with no budget violation on the 25 vertices S u {p} u A_p | 3510 | 7224 | 2406 | I1, I2, R |
| 2. 39-vertex survivors (tau, F, H, A_{z_0}) | 383 | 481 | 7 | I1, I2 (identical sets, see below), R (same counts); I3 for B2 (identical graphs) |
| 2'. matchings / pairs (tau, F) carrying them | 50 / 95 | 55 / 76 | 1 / 1 | I1, I2, R |
| 3a. tables with no budget violation on Y (45 vertices) | 8639 | 27203 | 0 | I1, I2, R; I3 for B2 |
| 3b. of which no PSD violation on Y | 23 | 164 | 0 | I1, I2 (identical sets), R |
| 4a. graphs on the 51 vertices with no budget violation, over the tables of 3b | 52 | 1839 | - | I2, R |
| 4b. of which no PSD violation | **0** | **0** | - | I1, I2 (twice: `v3_stage34.py` and `v7_step4_direct.py`), R |

So every line except 4a has two exact implementations (I1 and I2) that share no code, plus the referee's count
check; for B2, where the enumeration stops at line 3a, there are three exact implementations. Line 4a is an
intermediate count, not needed for the result (line 4b); it has one exact implementation (I2) and the referee's.

Notes on the table.

- Lines 2 and 3b, "identical sets": I1 and I2 do not use the same representative in each orbit of matchings, so
  every survivor is brought to a canonical form under Aut(B) and the multisets of canonical forms are compared
  (`lemma/t18_VERIF331/v4_compare.out`): identical for the 39-vertex survivors of the three graphs (383
  configurations in 232 canonical forms for B0, 481 in 383 for B1, 7 in 7 for B2) and for the tables of line 3b
  (23 in 15 forms for B0, 164 in 116 for B1). For B2, I3 and I1 give the same 7 labelled graphs up to the exchange
  of z_0 and sigma z_0, all in matching #385 (`lemma/t18_B2/e331_compare_2.out`).
- Line 3b: the 23 tables of B0 and the 164 tables of B1 lie in 9 matchings each.
- Line 4a is not produced by I1, whose step 4 prunes during the search; its own counters are: 242 type solutions
  and 14520 search nodes for B0 (14165 rejections by a budget violation, 355 by a PSD violation, 0 by exact
  elimination alone), 2060 and 124992 for B1 (119016, 5918, 0), and no graph left in both cases. A separate
  brute-force check of I1 (`r2_ext2_bruteforce.py`, 9 tables, 86400 complete assignments per table) finds 12, 12, 2
  (B0) and 39, 39, 39, 0, 0, 0 (B1) graphs without budget violation, none without PSD violation.
- For B1, step 4 is confirmed by a different test: `lemma/t18/r4_rank331.py` applies the rank bound (Proposition
  6.4) to the 47 vertices Y u {w, sigma w}, a determined sigma-invariant set with 23 orbits, for one orbit of W at a
  time. Over the 164 tables there are 295200 candidates (type, K_w), 16334 without budget violation; G_odd is
  singular for 2 of them only, and none satisfies both rank conditions. So every one of the 164 tables dies as soon
  as one orbit of W is added, by the rank bound alone.

### 7.6 Remarks and corrections to the working reports

**Both matrices are needed.** The working report states that "the violated matrix is 9(3I - A) + J". This is false
in general. I2 and R ran the whole enumeration with M1 alone:

| with M1 alone | B0 | B1 | B2 |
|---|---|---|---|
| 39-vertex survivors | 887 | 672 | 7 |
| tables with no violation on 45 vertices | 102 | 190 | 0 |
| graphs with no violation on 51 vertices | 0 | 10 | 0 |

(39 and 51 vertices: I2 and R; 45 vertices: I2.) So with M1 alone ten configurations of B1 would survive on 51
vertices. They all lie in one orbit of matchings, have t = 3 and no edge of H, satisfy every budget, and M1 is
exactly PSD on them; each is rejected by an explicit integer vector x with x^T M2 x = -88, -594 or -726
(`lemma/t18_VERIF331/v6_m1_final.out`). In the direct step 4 of I2, 1829 of the 1839 graphs of line 4a are rejected
by M1 and exactly these 10 by M2 only. At 39 vertices, 504 configurations of B0 and 191 of B1 are rejected by M2
only. I1 tests both matrices (this is visible in the source of `r2_hfirst.py`, `r2_stage2.py`, `r2_ext2.py`), which
is why its counts agree with the two-matrix runs.

**Line 1 (referee's remark 6).** The working report describes the numbers 3510, 7224, 2406 as the pairs (tau, F)
"passing the N(p) tests ... [such that] the 3 pairs of N(p) n X_1 exist". They are in fact the numbers of pairs
with no budget violation on S u {p} u A_p, as defined in line 1: the existence test coded in `r2_hfirst.py` does
not include the condition that the cell (i, j) of a vertex of W of type (i ; j) still has room (see (C6) in section
8.2 for this condition) and removes nothing. With a complete existence test the referee counts 1834, 4096, 1265
(`ref2_stage1_B*.out`). This changes nothing downstream: the omitted condition is a valid necessary condition and
the extra pairs die later.

**Counters that are not comparable between programs.** The working report gives "completions C": 23155 (B0),
93684 (B1), 44 (B2). I2 gives 11797, 45362, 88, and so does R ("covers"). These are two different objects: I1
counts the choices of rows before H is fixed, I2 and R count, for each 39-vertex survivor, the triples of rows with
the right numbers (F3). Neither is used in the proof; lines 3a and 3b, which are well defined, agree. The same
holds for the counters "after the pair tests" (624, 750, 114) and "(H, A_{z_0}) tested" (3810, 4416, 121) of the
working report, which depend on the order of the tests in `r2_hfirst.py`; the number of complete H on the 37
vertices S u {p} u X_2 (1618, 927, 16) is found by both I1 and R.

**Profile (3,3,1) does not need X_0' for B0 and B2**: in I2, adding W directly to the 39 vertices leaves 0, 2, 0
configurations for B0, B1, B2 (`v5_summary.out`, "dual order"). This is an observation, not used.


## 8. Profile (2,5,0)

In this section the profile is (h_2, h_1, h_0) = (2, 5, 0). Notation:

    A_p  = N(p) n X_2      (4 vertices, 2 orbits);
    W    = N(p) n X_1      (10 vertices, 5 orbits);          N(p) n X_0 is empty, so N(p) = A_p u W;
    X_2' = X_2 \ A_p       (14 vertices, 7 orbits);
    X_0 \ {p}              (8 vertices, 4 orbits);
    f_i  = the number of vertices of A_p adjacent to x_i;
    t    = the number of edges inside X_2 (as in Lemma 5.4).

tau, the vertices s_U, the rectangles and the representatives are those of section 7.1.

### 8.1 The forced structure  [A14]

**Lemma 8.1.**

(a) Inside N(p) = A_p u W the only edges are the 7 mate edges: there is no edge between the two orbits of A_p, none
    between A_p and W, and none between two different orbits of W.

(b) A vertex w of W has exactly one neighbour x_i in S+ and one neighbour y_j in S-, and i != j; w is of type
    (i ; j) and sigma w of type (j ; i). The five orbits of W have five different unordered types {i, j}.
    The set K_w = N(w) n X_2 is contained in X_2', has a_2(w) >= 2 elements, contains no mate pair, and
    K_{sigma w} = sigma K_w. w has exactly a_2(w) - 1 neighbours in X_0, one of which is p.

(c) sum over A_p of (a_2 - 1) + sum over W of (a_2 - 2) = 8, and all the terms are >= 0.

(d) Every s in X_2' satisfies |N(s) n A_p| + |N(s) n W| = 2.

(e) For every i, x_i has exactly f_i neighbours in A_p and 2 - f_i in W; in particular f_i <= 2.

(f) p has no neighbour in X_0. A vertex z of X_0 \ {p} has no neighbour in S, is not adjacent to p nor to sigma z,
    and satisfies |N(z) n A_p| + |N(z) n W| = 2.

*Proof.* (a) Lemma 2.1 (b). (b) d(w) = 1 gives x_i and y_j. If i = j, w would be a common neighbour of x_i and its
mate, with x_i outside N[p], whereas by Lemma 2.1 (d) such common neighbours are outside N[p]. If w and w' lie in
different orbits of W and have the same unordered type, replace w' by its mate so that both are of type (i ; j):
then w and w' are distinct, non-adjacent by (a), with the three common neighbours p, x_i, y_j. K_w avoids A_p by (a).
a_2(w) >= 2 is Lemma 5.6. If K_w contained s and sigma s, then w would be a common neighbour of s and sigma s with s
outside N[p], contradicting Lemma 2.1 (d) again. K_{sigma w} = sigma K_w because sigma is an automorphism. The last
statement is Lemma 5.4 (a), c = a_2 - 1.
(c) By Lemma 5.6 the sum of a_2 over N(p) is 36 - 2 * 2 = 32, and 32 - 4 * 1 - 10 * 2 = 8; the lower bounds of
Lemma 5.6 give the signs. (d) and (e): s and x_i are outside N[p]; Corollary 2.2. (f) N(p) contains no vertex of
X_0. z is in X_0: no neighbour in S. z is not in N(p), so z not~ sigma z by Lemma 2.1 (a); Corollary 2.2. QED

### 8.2 The determined sets of 37 and 47 vertices  [C-a to C-d]

    Y37 = S u {p} u X_2          (18 + 1 + 18 = 37 vertices; 18 orbits and p);
    Y47 = Y37 u W                (47 vertices; 9 + 9 + 5 = 23 orbits and p).

Both are sigma-invariant. The data:

- **tau** (a representative, by (7.1));
- **F**, the set of the two rectangles of tau whose orbits form A_p; each must be usable in N(p);
- **H**, the set of all edges inside X_2 (here H includes the two mate edges of A_p); it is invariant under sigma;
- **the types**: five unordered pairs {i_c, j_c}, c = 1..5; w_c denotes the vertex of type (i_c ; j_c) and sigma w_c
  the vertex of type (j_c ; i_c);
- **K_c** = N(w_c) n X_2, a subset of X_2', for c = 1..5.

**Lemma 8.2.** Y37 is determined by (tau, F, H) and Y47 by (tau, F, H, types, K_1, ..., K_5). More precisely:

| pair of classes | adjacency | reason |
|---|---|---|
| S+ with S+, S- with S-; S+ with S-; S with p; S with X_2 | as in Lemma 7.5 | Corollary 4.8, definition of B, Lemma 7.1 |
| p with X_2 | exactly the 4 vertices of A_p | parameter F |
| X_2 with X_2 | parameter H; s ~ sigma s iff s is in A_p | Lemma 2.1 (a) |
| W with p | adjacent | definition |
| W with W | the 5 mate edges only | Lemma 8.1 (a) |
| W with A_p | none | Lemma 8.1 (a) |
| W with S | w_c ~ x_{i_c}, y_{j_c} only; sigma w_c ~ x_{j_c}, y_{i_c} only | parameter types (Lemma 8.1 (b)) |
| W with X_2' | w_c ~ s iff s in K_c; sigma w_c ~ s iff s in sigma K_c | parameter K_c (Lemma 8.1 (b)) |

The same list shows that the following subsets are determined by the corresponding part of the data; they are the
sets on which the programs test partial data:

- S u {p} u A_p (23 vertices), by (tau, F);
- S u N[p] = S u {p} u A_p u W (33 vertices), by (tau, F, types);
- S u {p} u X_2 u (some orbits of W) (39, 41, ... vertices), by (tau, F, H) and the types and sets K_c of these orbits;
- S u {p} u A_p u (some orbits of X_2') u (one orbit {w, sigma w} of W) (27 or 29 vertices for one or two orbits of
  X_2'), by (tau, F), the edges of H inside the set, the type of w and the intersection of K_w with the set. In
  particular the hypothesis "K_w contains neither s nor sigma s" determines the 27-vertex set of the orbit of s
  with no edge between {w, sigma w} and {s, sigma s}; if that graph has a violation, then K_w must contain s or
  sigma s (this is the "forced orbit" test of the first program).

**Lemma 8.3 (forced numbers).** The data of a configuration satisfy:

- (C1) both rectangles of F are usable in N(p);
- (C2) H contains the mate edge {s, sigma s} if and only if s is in A_p, and every vertex of X_2 has at most 4
  neighbours in X_2;
- (C3) FL := sum over A_p of (a_2 - 1) is the number of edges between A_p and X_2'; it is even and FL <= 8;
- (C4) t <= 9 and  sum over X_2 of a_2 (a_2 - 1) + m(t) <= 36,  where m(t) is twice the minimum of
  y_1^2 + y_2^2 + y_3^2 + y_4^2 over the non-negative integers with y_1 + y_2 + y_3 + y_4 = t
  (m = 0, 2, 4, 6, 8, 14, 20, 26, 32, 42 for t = 0, ..., 9);
- (C5) the five unordered types are distinct, i != j in each, and every index i occurs in exactly 2 - f_i of them;
- (C6) ("cell room") for every c, the number of deficient pairs U with i_c in U and j_c in tau U is at most
  1 - [i_c ~_B j_c], and the same with i_c and j_c exchanged;
- (C7) K_c is a subset of X_2' without mate pair, 2 <= |K_c| <= 2 + slack with slack = 4 - FL/2, and
  sum over c of (|K_c| - 2) = slack;
- (C8) every s in X_2' belongs to exactly req(s) = 2 - |N(s) n A_p| of the ten sets K_1, sigma K_1, ..., K_5,
  sigma K_5. In particular req(s) >= 0, and req(sigma s) = req(s).

*Proof.* (C1) Lemma 7.2 (R3). (C2) Lemma 2.1 (a) and Lemma 5.4 (a). (C3) A vertex of A_p has a_2 - 1 neighbours in
X_2 other than its mate, and they are in X_2' by Lemma 8.1 (a). a_2 takes the same value on mates, so FL is even.
FL <= 8 by Lemma 8.1 (c). (C4) t <= 9 is Lemma 5.4 (d). In identity (*), the vertex p has a_2(p) = 4 and contributes
0 to the first sum; the other 8 vertices of X_0 form 4 orbits, a_2 - 4 is a non-negative integer y_q constant on
each orbit, and 2 (y_1 + y_2 + y_3 + y_4) = sum_{X_0} (a_2 - 4) = 2t by Lemma 5.4 (c); so the first sum is
2 (y_1^2 + ... + y_4^2) >= m(t); the second sum is >= 0. (C5) Lemma 8.1 (b), (e): x_i has exactly one neighbour in
each orbit of W whose unordered type contains i. (C6) w_c and the vertices s_U with i_c in U and j_c in tau U are
distinct common neighbours of x_{i_c} and y_{j_c}, which have 2 - [i_c ~_B j_c] common neighbours; the same for
sigma w_c with x_{j_c} and y_{i_c}. (C7) Lemma 8.1 (b); by Lemma 8.1 (c), sum over W of (a_2 - 2) = 8 - FL, and
a_2(w_c) = a_2(sigma w_c) = |K_c|, so 2 sum_c (|K_c| - 2) = 8 - FL. (C8) Lemma 8.1 (d): s is adjacent to w_c iff
s is in K_c, and to sigma w_c iff s is in sigma K_c. QED

### 8.3 Stage B: the 37 vertices

> **Computation 8.4 (stage B).** For each B in {B0, B1, B2} and each representative tau, list all (F, H) where F is
> a set of two rectangles of tau usable in N(p) and H is a sigma-invariant set of edges on X_2 satisfying (C2),
> such that the graph on Y37 has no budget violation and no PSD violation for M1, M2 is found. The triples
> (tau, F, H) obtained are the **stage-B triples**:
>
> | | B0 | B1 | B2 |
> |---|---|---|---|
> | pairs (tau, F) with no budget violation on the 23 vertices S u {p} u A_p | 5545 | 12366 | 4347 |
> | of which no PSD violation found on these 23 vertices | 4904 | 11509 | 3863 |
> | **stage-B triples (tau, F, H)** | **5595** | **4977** | **196** |
> | matchings / pairs (tau, F) carrying them | 133 / 901 | 275 / 1015 | 53 / 74 |
> | triples with t = 2 / 4 / 6 | 459 / 2584 / 2552 | 386 / 2351 / 2240 | 6 / 80 / 110 |
> | triples with largest a_2 on X_2 equal to 1 / 2 | 5232 / 363 | 3791 / 1186 | 141 / 55 |

Programs:

- **E** ("the enumerator") = `lemma/t18/r3_p250.py`, stage B: the orbits of X_2' are added one at a time, with the
  states of their edges to the earlier orbits; budgets on partial graphs, PSD when an orbit is complete; it uses
  (C2), (C3) during the search and applies (C4) to the complete H. It reads `types.json`.
- **V** ("the verifier") = `lemma/t18/r3_verify.py B250`: no shared code, graphs re-entered as edge lists, orbits
  added in the reverse order, budgets by integer matrix products; it uses (C2), (C3) and not (C4).
- **R** = `lemma/t18_REFEREE/ref4_stageB.py` (own model; floating-point PSD).

E and V produce **identical sets of triples** for the three graphs (`lemma/t18/r3_finalB.out` for B1,
`lemma/t18_B0/b0_compareB.out` for B0, `lemma/t18_B2/b2_compareB.out` for B2). R finds the same numbers of triples,
of pairs (tau, F), of matchings, and the same distributions by t and by largest a_2. So the list of stage-B triples
has two exact implementations and one count check.

Notes. The first row is given by E and R for B0 and B2, and by R alone for B1 (for B1 the runs of E overlap and its
counter cannot be summed). The second row is given by V and R for the three graphs and by E for B0 and B2.
E and V also discard a pair (tau, F) when some f_i exceeds 2 or when no set of five types satisfies (C5) (Lemma 8.3;
E takes the types from `types.json`, V from its own 21-vertex test); R does not. This removes nothing: in every
output of E and of V the counter is the same before and after this test (for instance 5545 = 5545 for B0 and
4347 = 4347 for B2 in E), and R obtains the same triples counts without it.
Condition (C4) removes nothing: in every run the number of complete H is the same before and after it (E:
5595 = 5595 and 196 = 196; comparison files: "4977 after the counting conditions"; R: (C4) true on all triples).
The last two rows are data, not proved facts: on all stage-B triples t is 2, 4 or 6 and a_2 <= 2 on X_2. (Hand
proofs that t is even and different from 8 exist in the working report `lemma/t18_STRUCT`; they are not needed.)

For B1 the stage-B list of E was produced in five launches, some of them cut by a time limit; the bookkeeping
script `lemma/t18_B0_VERIFC/b1_coverage.py` checks that each of the 1259 matchings is completed by exactly one of
the 14 files used and that the 4977 triples so obtained are the set of V (`04_b1_coverage.out`).

### 8.4 Stage C: the 47 vertices

> **Computation 8.5 (stage C).** For every stage-B triple (tau, F, H), list all (types, K_1, ..., K_5) satisfying
> (C5), (C7), (C8) such that the graph on Y47 has no budget violation and no PSD violation for M1, M2 is found.
> The (tau, F, H, types, K) obtained are the **stage-C survivors**.
>
> - For **B0**: there is no stage-C survivor.
> - For **B2**: there is no stage-C survivor.
> - For **B1**: there are exactly 4 stage-C survivors: matching #813 with F = [2, 9], matching #813 with
>   F = [3, 6], matching #975 with F = [1, 2], matching #975 with F = [3, 6]. (F is written with the indices, in the
>   list of deficient pairs of B1 given after Corollary 4.11, of one deficient pair of each of its two rectangles.
>   The four graphs are given explicitly in appendix B.)

(C6) is not listed among the conditions because it is implied by the absence of budget violation on Y47; the
programs use it, or an equivalent budget test on a partial graph, as a filter.

Programs:

- **E** = `lemma/t18/r3_p250.py`, stage C: the orbits of W are added one at a time, each with its set K_c; tests on
  the 27-, 29- and 33-vertex subsets of section 8.2 and on S u {p} u X_2 u (the orbits of W already placed).
- **C** = `c_mine.py` (written in `lemma/t18_B2`; the copy used for B0 and B1 is in `lemma/t18_B0_VERIFC`): for
  every type, all sets K with no violation on the 39 vertices S u {p} u X_2 u {w, sigma w}; then an exact cover of
  the numbers req(s) by one K per orbit of W, with a test on 41 vertices for every two orbits; then the test on 47
  vertices. It shares no code with E or V, does not read `types.json`, and takes the stage-B triples as input.
  A PSD rejection is an integer vector evaluated in Python integers, or else an exact fraction-free elimination.
- **V** = `lemma/t18/r3_verify.py C250`: "dual" order (one orbit of X_2' at a time: which vertices of W it sees).
  Complete for B2, partial for B0 and B1. Two further partial programs for B1: `lemma/t18/r4_verifyC.py` and
  `lemma/t18/r4_verifyC2.py`.
- **R** = `lemma/t18_REFEREE/ref5_stageC.py`, on the referee's own stage-B triples (floating-point PSD).

| graph | program | scope | stage-C survivors | where |
|---|---|---|---|---|
| B0 | E (as `b0_stageC.py`, `b0_stageC2.py`) | 2667 representatives of the 5595 triples modulo the stabilisers of the matchings | 0 | `lemma/t18_B0/REPORT.md` (section "FINAL STATE", generated from the logs `b0_stageC_done_*.jsonl`) |
| B0 | C | all 5595 triples, each exactly once (24 parts) | 0 | `lemma/t18_B0_VERIFC/09_B0_check_complete.out` |
| B0 | R | all 5595 triples | 0 | `lemma/t18_REFEREE/ref9_totals.out` |
| B0 | V | a sample of 29 triples | 0 | `lemma/t18_B0/b0_verC_sample.out` |
| B1 | E | all 1259 matchings (4977 triples) | 4 | `lemma/t18/r3_finalB.out`, `r3_round5.out` |
| B1 | C | all 4977 triples, each exactly once (24 parts) | 4, the same 47-vertex graphs as E | `lemma/t18_B0_VERIFC/11_B1_check_complete.out`, `13_B1_survivors_compare.out` |
| B1 | R | all 4977 triples | 4, same matchings and F | `lemma/t18_REFEREE/ref9_totals.out` |
| B1 | V, `r4_verifyC.py`, `r4_verifyC2.py` | 2086 of the 4977 triples, including the 170 triples of matchings #813 and #975 | the same 4, no other | `lemma/t18/r4_compareC_final.out` |
| B2 | E | all 528 matchings (196 triples) | 0 | `lemma/t18_B2/b2_BC_0of2.out`, `b2_BC_1of2.out` |
| B2 | V | all 196 triples (four runs) | 0 | `lemma/t18_B2/b2v_C250_*.out` |
| B2 | C | all 196 triples | 0 | `lemma/t18_B2/c_mine_2_all.out` |
| B2 | R | all 196 triples | 0 | `lemma/t18_REFEREE/ref5_stageC_B2.out` |

So for each of the three graphs the stage-C result has at least two complete exact implementations sharing no code
(E and C; for B2 also V), plus the referee's complete count check.

Notes.

- *Status in the working reports.* `LEMMA_TARGET_2026-10-06.md` (section 8) and `lemma/t18/T18_REPORT.md` say that B0
  is open and that stage C of B1 has one complete implementation, the second covering 2086 triples;
  `lemma/t18_B0/REPORT.md` says that stage C of B0 has one implementation. These statements are superseded by the
  later complete runs of C stored in `lemma/t18_B0_VERIFC` (run on 2026-10-06/07, after those reports) and by the
  referee's runs.
- *The reduction modulo stabilisers (B0, program E only).* An automorphism g of B fixing tau maps a stage-B triple
  (tau, F, H) to (tau, gF, gH) and maps the completions of the first to the completions of the second (it is a
  relabelling of the orbits of the support, as in (7.1)). So it is enough to complete one triple in each orbit. This
  reduction exists in one implementation (`b0_orbitsB.py`, which asserts that the set of triples is closed); it is
  not needed for the result, since C and R treat all 5595 triples.
- *Inputs of C.* For B0, C reads the stage-B file of E, which is the set of V (`08_b0_input_crosscheck.out`). For B1
  it reads the list built by `b1_coverage.py`, equal to the set of V; `12_B1_check_complete_verifier_list.out`
  checks the completeness of the run against the list of V directly. A control run of C on the 170 triples of
  matchings #813 and #975, read from the files of V, gives the same four graphs (`05_control_B1_check.out`,
  `06_control_B1_compare.out`).
- *Work done* (program-specific counters, not comparable between programs). E on the 2667 representatives of B0:
  262850 (triple, type solution) pairs examined, 170382 of them dead by the counting and forced-orbit tests, 701270
  search nodes, 340605 rejections by a budget violation and 704789 by a PSD violation. C on B0: 132132 types
  tested, 603053 sets K without budget violation on 39 vertices, 52580 without PSD violation, 3165 cover nodes, no
  cover reaching the 47-vertex test, 611642 PSD certificates and no use of the exact fallback. C on B1: 115473
  types, 905578 and 75295 sets K, 9248 cover nodes, 43 tests on 47 vertices, 4 survivors, 959041 certificates, no
  fallback. C on B2: 4222 types, 39107 and 1535 sets K, 173 cover nodes, no 47-vertex test, 40845 certificates.
- *"Type solutions" (referee's remark 6).* The B2 report gives "11235 type solutions over the 74 pairs (tau, F), of
  which 4227 pass on the 33 vertices S u N[p]", found by E and by C. These numbers count the sets of five types
  satisfying (C5) only, i.e. **without the cell-room condition (C6)**; with (C6) the referee counts 770 type
  solutions, 514 of which pass on the 33 vertices (`ref5b_types_variants_B2.out`). Both programs apply (C6) later,
  as a budget test, so nothing changes downstream.

### 8.5 The four survivors of B1

For the four stage-C survivors of B1 (appendix B), the following is established exactly by programs that share no
code with the enumerations (`lemma/t18/r3_survivors.py`, by rational elimination, for both matrices;
`lemma/t18/r4_verifyD.py`, for M1; `lemma/t18_REFEREE/ref8_survivors.py`, by exact characteristic polynomials, for
both matrices):

| survivor | t | a_2 on A_p | orbits of W with a_2 = 3 / with a_2 = 2 | M1 on the 47 vertices | M2 on the 47 vertices |
|---|---|---|---|---|---|
| #813, F = [2, 9] | 4 | 1, 2, 2, 1 | 3 / 2 | PSD, rank 46 | PSD, rank 45 |
| #813, F = [3, 6] | 4 | 1, 2, 2, 1 | 3 / 2 | PSD, rank 46 | PSD, rank 45 |
| #975, F = [1, 2] | 2 | 1, 1, 1, 1 | 4 / 1 | PSD, rank 46 | PSD, rank 45 |
| #975, F = [3, 6] | 2 | 1, 1, 1, 1 | 4 / 1 | PSD, rank 46 | PSD, rank 45 |

They satisfy every budget, they are sigma-invariant, and both matrices are exactly PSD. So budgets and
semidefiniteness cannot exclude them on 47 vertices. They are excluded in two independent ways (sections 8.6 and
8.7); each way alone suffices.

The working report of round 3 presents these four configurations as "an open case" (PSD, rank 46 of 47). That
wording is superseded: rank 46 is itself impossible, by the rank bound.

### 8.6 First exclusion: the rank bound

Y47 is a sigma-invariant determined set (Lemma 8.2) with 23 orbits and the fixed vertex p. Take for R the 9 vertices
x_i, one vertex of each of the 9 orbits of X_2 and the 5 vertices w_c. By Proposition 6.4 (a), in a configuration
the 23 x 23 integer matrix G_odd = 3I - A[R,R] + A[R, sigma R] is singular, and by Proposition 6.4 (b) the 24 x 24
matrix G_even has rank at most 22.

> **Computation 8.6.** For the four stage-C survivors of B1:
>
> | survivor | det G_odd (23 x 23) | rank G_odd | rank G_even (24 x 24) |
> |---|---|---|---|
> | #813, F = [2, 9] | 47684 | 23 | 23 |
> | #813, F = [3, 6] | 47684 | 23 | 23 |
> | #975, F = [1, 2] | 874944 | 23 | 23 |
> | #975, F = [3, 6] | 874944 | 23 | 23 |

det G_odd != 0 contradicts Proposition 6.4 (a); rank G_even = 23 > 22 contradicts Proposition 6.4 (b)
independently. So none of the four graphs is the induced subgraph on Y47 of a configuration.

Programs (five codes written separately, all exact): `lemma/t18/r4_rank.py`
(fraction-free Bareiss determinant, ranks by rational elimination), `lemma/t18_STRUCT/rank_survivors.py` (ranks) and
`rank_survivors_check2.py` (Bareiss determinant; rank modulo two primes), `lemma/t18_B2/rank_B1_survivors.py` with
`rankbound.py` (determinant and ranks, on the survivors as found by C), `lemma/t18_B0/b0_rank47.py` (ranks),
`lemma/t18_REFEREE/ref8_survivors.py` (determinant and ranks, on the survivors as found by R). All give the values
of the table. The smallest eigenvalue of G_odd is about 0.011 (#813) and 0.012 (#975) in floating point: the matrix
is positive definite, which is why a PSD test cannot see the obstruction.

### 8.7 Second exclusion: the vertices of X_0 other than p  (stage D)  [A18, A19]

X_0 has 9 vertices (Theorem 5.3), so X_0 \ {p} has 8 vertices: at least one vertex z of X_0 \ {p} exists.

**Lemma 8.7.** Let z be a vertex of X_0 \ {p} and Z = N(z) n (X_2 u W). Then:

- (D1) z has no neighbour in S u {p} and is not adjacent to sigma z; N(sigma z) n (X_2 u W) = sigma Z. Hence
  Y47 u {z} (48 vertices) and Y47 u {z, sigma z} (49 vertices) are determined by the data of Y47 together with Z;
- (D2) |Z n (A_p u W)| = 2;
- (D3) 4 <= |Z n X_2| <= 4 + t;
- (D4) every s in X_2 has exactly need(s) = a_2(s) + 2 - [s in A_p] neighbours in X_0 \ {p}, and every w in W has
  exactly need(w) = a_2(w) - 2. Hence, for every vertex v of X_2 u W, [v in Z] + [v in sigma Z] <= need(v); in
  particular Z contains no vertex with need = 0.

*Proof.* (D1) and (D2) are Lemma 8.1 (f). (D3): |Z n X_2| = a_2(z) >= 4 by Lemma 5.4 (a), and z has a_2(z) - 4
neighbours in X_0; so has sigma z. By Lemma 5.4 (c) the sum over X_0 of the numbers of neighbours in X_0 is 2t; z
and sigma z are two distinct vertices of X_0, so 2 (a_2(z) - 4) <= 2t. (D4): by Lemma 5.4 (a), s in X_2 has
a_2(s) + 2 neighbours in X_0, and p is one of them exactly when s is in A_p; w in W has a_2(w) - 1 neighbours in
X_0, one of which is p (Lemma 8.1 (b)). v is adjacent to z iff v is in Z and to sigma z iff v is in sigma Z, and
these are neighbours of v in X_0 \ {p}. QED

The upper bound in (D3) is not in the list of forced numbers of the working report, but the three programs of the
repository apply it (referee's remark 6); this is why they report 846 below where the referee, without it, counts
849.

> **Computation 8.8 (stage D).** For each of the four stage-C survivors of B1, list all subsets Z of X_2 u W
> satisfying (D2), (D3), (D4) such that the graph on the 49 vertices Y47 u {z, sigma z} has no budget violation.
> The numbers of unordered pairs {Z, sigma Z} are
>
>     #813, F = [2, 9]: 678;    #813, F = [3, 6]: 678;    #975, F = [1, 2]: 846;    #975, F = [3, 6]: 846.
>
> For every one of them a PSD violation is found on the 49 vertices (an integer vector x with x^T M x < 0;
> 3048 = 2 (678 + 846) certificates), and according to the second program already on the 48 vertices Y47 u {z}.

By (6.1) and Lemma 8.7, the set Z of the vertex z of a configuration would be one of the listed sets and would
have no PSD violation. So none of the four graphs is the induced subgraph on Y47 of a configuration.

Programs (three exact, plus the referee):

- `lemma/t18/r4_stageD.py`: 678, 678, 846, 846 candidates, 0 without PSD violation; its 3048 certificates
  (`r4cert_stageD_B1.jsonl`) were re-checked by `r3_verify.py certs`: 3048 checked, 0 invalid, all on 49 vertices;
- `lemma/t18/r4_verifyD.py` (no shared code, own generator): 1356, 1356, 1692, 1692 oriented sets Z with an
  admissible mate (twice the numbers above), a PSD violation found for each on the 48 vertices, budgets satisfied on
  all the 49-vertex graphs, no ambiguous floating-point case;
- `lemma/t18_B2/d_stage.py` (no shared code): 678, 678, 846, 846 candidates, 0 without PSD violation, 3048
  certificates, re-checked (`lemma/t18_B2/b2_certs_check.out`);
- `lemma/t18_REFEREE/ref8_survivors.py`: 678 and 678; 849 and 849 without the upper bound of (D3), of which 846
  satisfy it; none passes the (floating-point) PSD test.

*Remark (not used).* On the four survivors the kernel of M1[Y47] is spanned by the vector 4 e_p + 1_{N(p)}, which
is in the kernel of M1 for the whole graph; so the condition "the row of a new vertex is orthogonal to the kernel"
mentioned in the working report reduces to Corollary 2.2 and gives nothing.

### 8.8 Conclusion for profile (2,5,0)

**Proposition 8.9.** Profile (2,5,0) is impossible for B0, B1 and B2.

*Proof.* Suppose a configuration has profile (2,5,0) and orbit graph B. By (7.1) take tau among the
representatives. By Lemmas 8.2 and 8.3 its (tau, F, H) is a stage-B triple (Computation 8.4) and its
(tau, F, H, types, K) is a stage-C survivor (Computation 8.5): this is (6.1). For B0 and B2 there is no stage-C
survivor: contradiction. For B1 the graph induced on Y47 is one of four graphs, each of which contradicts
Proposition 6.4 by Computation 8.6 (and, independently, contradicts Lemma 8.7 by Computation 8.8). QED

Status: hand part (Lemmas 7.1, 7.2, 8.1, 8.2, 8.3, Proposition 6.4, Lemma 8.7) plus Computations 7.3, 8.4, 8.5 and
8.6 (or 8.8).

Summary of section 8:

| | B0 | B1 | B2 |
|---|---|---|---|
| matchings / orbits | 25514 / 425 | 13799 / 1259 | 9229 / 528 |
| stage-B triples on 37 vertices | 5595 | 4977 | 196 |
| stage-C survivors on 47 vertices | 0 | 4 | 0 |
| excluded by the rank bound (det G_odd != 0) | - | 4 of 4 | - |
| excluded by stage D (no vertex of X_0 \ {p} can be added) | - | 4 of 4 | - |


## 9. Conclusion and status

### 9.1 Conclusion

**Theorem 9.1 (= T18).** There is no configuration: for G and sigma as in section 1, no integer-valued sigma-odd
function phi satisfies A phi = -4 phi and sum phi^2 = 18.

*Proof, given the Computations.* Suppose (G, sigma, phi) is a configuration. By Proposition 3.1, phi takes the
values 0, +1, -1 and its support is S = S+ u S- with |S+| = 9. By Corollary 4.8, S+ is independent and S avoids
N[p]; by Lemma 4.9 and Computation 4.10, the orbit graph B is one of B0, B1, B2 after a suitable labelling. By
Theorem 5.3 no outside vertex has three neighbours in S+, and by Lemma 5.5 the profile is (2,5,0), (3,3,1) or
(4,1,2). Profile (4,1,2) is impossible by Proposition 5.7, profile (3,3,1) by Proposition 7.7, profile (2,5,0) by
Proposition 8.9. Contradiction. QED

The theorem therefore rests on the hand statements of sections 2-8 and on six finite computations: 4.10 (the three
graphs), 7.3 (stage 1), 7.6 (profile (3,3,1)), 8.4 and 8.5 (stages B and C of profile (2,5,0)), and 8.6 (the rank
of the four survivors of B1; Computation 8.8 is an independent alternative to 8.6).

### 9.2 What is proved by hand and what is computed

| statement | content | nature | implementations |
|---|---|---|---|
| Lemma 2.1, Corollary 2.2 | sigma and N(p) | hand | - |
| Proposition 3.1 | integer values => 0, +1, -1, nine at +1 | hand | - |
| Lemmas 4.2-4.7, Corollary 4.8, Lemma 4.9 | k = 0, e = 0, B is 4-regular with codegrees <= 2 | hand | - |
| Computation 4.10 | B is B0, B1 or B2; their codegrees are 1 or 2 | computed | 3 programs (`enum_S.py`, `verify_S.py`, `ref1_quartic9.py`), see 9.3 item 5 |
| Lemmas 5.1, 5.2, Theorem 5.3 | path count; n_3 = 0 | hand | - |
| Lemmas 5.4, 5.5, 5.6, Proposition 5.7 | identities; the three profiles; (4,1,2) impossible | hand | - |
| Lemmas 6.1, 6.2, 6.3, Proposition 6.4 | the two PSD matrices, the budget, the rank bound | hand | - |
| Lemmas 7.1, 7.2 | X_2 and the matching tau; stage-1 tests | hand | - |
| Computation 7.3 | the admissible matchings and their orbits | computed | 4 programs, same numbers; representatives checked by 2 of them |
| Lemmas 7.4, 7.5 | structure and determined sets of profile (3,3,1) | hand | - |
| Computation 7.6 | profile (3,3,1): nothing survives on 51 vertices (B0, B1), on 45 (B2) | computed | 2 exact implementations sharing no code (I1, I2), identical intermediate sets; a third for B2 (I3); referee's count check (R) |
| Lemmas 8.1, 8.2, 8.3 | structure and determined sets of profile (2,5,0) | hand | - |
| Computation 8.4 | stage B: 5595 / 4977 / 196 triples | computed | 2 exact implementations (E, V), identical sets; R: same counts |
| Computation 8.5 | stage C: 0 / 4 / 0 survivors | computed | 2 complete exact implementations sharing no code (E, C); a third for B2 (V); partial ones for B0, B1; R: same result |
| Computation 8.6 | the four survivors violate the rank bound | computed | 5 exact codes written separately |
| Lemma 8.7 | forced numbers of stage D | hand | - |
| Computation 8.8 | no vertex of X_0 \ {p} can be added to the four survivors | computed | 3 exact programs sharing no code; R |

The hand part was audited by a referee who re-derived every statement from the definitions before reading the
given proof (`lemma/t18_REFEREE/REPORT.md`): every load-bearing hand statement was found correct, and the referee's
list of defects of the written text is addressed in section 9.5. The referee also tested the general facts (Lemma
2.1, Lemma 6.3, the counting identities, the parity law, the path count) on two real graphs with lambda = 1, mu = 2
and an involution with one fixed point, the Paley graph on 9 vertices and the srg(243,22,1,2), with x -> -x
(`ref3_bvls.out`).

### 9.3 What has not been independently verified, and other caveats

1. **Floating-point "kept" decisions.** In E (`r3_p250.py`), V (`r3_verify.py`), C (`c_mine.py`), I1, `e331.py`,
   `d_stage.py`, `r4_stageD.py`, a candidate is kept when the smallest floating-point eigenvalue is above about
   -10^-7; this is never used as a proof of semidefiniteness. A rejection requires an exact witness: an integer
   vector with negative quadratic form (64-bit integers in `r3_p250.py` and `r4_stageD.py`, with the bound
   |x^T M x| < 2 * 10^15 stated in the source of `r3_p250.py`; Python integers elsewhere), or an exact elimination
   (fallback of `c_mine.py`, `r2_hfirst.py`, `r2_ext2.py`; it produced no rejection in the runs reported), or an
   exact characteristic polynomial (I2). When the eigenvalue is negative and no witness is found, `r3_p250.py`
   keeps the candidate and counts it ("psd_float_neg_no_cert"): 0 cases in every run reported; `r3_verify.py` and
   `r4_verifyD.py` report 0 "ambiguous" cases. The only places where a positive statement of semidefiniteness is
   made are exact: the four survivors of B1 (section 8.5), and the acceptances of I2 at 39, 45, 51 vertices; none
   of these positive statements is needed for Theorem 9.1.
2. **The referee's runs use floating-point PSD rejections** (threshold -10^-7) with no exact certificate. They are
   checks of the model and of the counts, not further exact proofs. Exception: the ranks and determinants of the
   four survivors in `ref8_survivors.py` are exact.
3. **The programs were not audited line by line.** The referee states that it did not verify "the repo's programs
   themselves and their exact certificates (only that they agree with the referee's model at every checkpoint)".
   For this text the following were read in full: `r2_stage1.py`, `r2_hfirst.py`, `r3_p250.py`, `c_mine.py`,
   `v1_stage1.py`, `v3_stage34.py`, `vcommon.py`, `rows.py`; in part: `r3_verify.py`, `v2_stage2.py`,
   `r4_verifyD.py`, `ref4_stageB.py`; for the others only the header. That each program enumerates exactly the list
   described in the text is supported by the agreement of implementations that share no code, not by a proof.
4. **Shared inputs.** Every program except those of I2 and R reads the matching representatives from
   `lemma/t18/r2_tau_<s>.json` (file checked by `r3_verify.py stage1` and by `ref10_tau_files.py`). C takes the
   stage-B triples as input (lists shown identical to the set of V). I1 and E read `structures.json` (the three
   graphs; the other programs re-enter them as edge lists).
5. **Computation 4.10.** The list of the 16 classes of 4-regular graphs on 9 vertices comes from one program
   (`ref1_quartic9.py`). The three classes with codegrees <= 2 are found by three programs, but `verify_S.py`
   imports the isomorphism routine of `enum_S.py`. The printed output of `enum_S.py` is quoted in the working
   report and not saved in a file; its result file `structures.json` is in the repository.
6. **`types.json` and the lemma H16.** I1 and E (`r2_stage1.py`, `r2_hfirst.py`, `r2_stage2.py`, `r2_ext2.py`,
   `r3_p250.py` and its copies `b0_stageC.py`, `b0_stageC2.py`) read lists of admissible "types" from
   `lemma/t18/types.json`, produced by `lemma/t18/rows.py`. The last filter of `rows.py` (called L in its header) is
   conditional on H16, an earlier lemma (no configuration of squared norm <= 16) that is **not proved in this
   document**. The saved output `lemma/t18/rows.out` shows that, for the entries that are read (types with one or
   two neighbours in S+), the three counters "graph filters", "graph filters + PSD", "graph filters + PSD + L" are
   equal for B0, B1 and B2 (81 = 81 = 81 and 72 = 72 = 72 for d = 1; 198 = 198 = 198 and 126 = 126 = 126 for
   d = 2). So neither the PSD filter nor L removed anything there, and the lists that are read are those of the
   graph filters alone, which are instances of Lemma 6.2 and Lemma 2.1. In addition, every computed line has an
   implementation that does not read `types.json` (V, C, I2, I3, `d_stage.py`, R). H16 is therefore not used; but
   this was not pointed out in the working reports nor by the referee, and it rests on `rows.out`.
7. **Saved certificates.** Only samples of the PSD witnesses were saved and re-checked: 50000 for stages B and C of
   B1 (out of roughly 1.6 million rejections), 12000 for B2, all valid; the 3048 witnesses of stage D are complete
   and were re-checked in both implementations; the witnesses saved for B0 (`r3cert_0_*.jsonl`) were not
   re-checked. Files larger than 1 MB (among them `r4cert_stageD_B1.jsonl` and `t18_B0/r3_p250_0_0of1_B.json`) are
   not in git; `lemma/LARGE_FILES_NOT_IN_GIT.txt` lists them, and they are regenerated by the scripts.
8. **Runs cut by time limits.** The B1 runs of E were made in five launches; the stage-B run of V for B0 in two
   (matchings 0..417, then 418..424); the stage-C run of V for B2 in four. Completeness is checked by bookkeeping
   scripts (`b1_coverage.py`, `b0_input_crosscheck.py`, `check_complete.py`), not by a rerun in one piece. The runs
   of C are complete, every triple being processed exactly once.
9. **Patched scripts.** Several scripts were edited during the sessions (`_patch_*.py`). The working reports state
   that the scripts in place are the final ones; that the stored outputs were produced by exactly these versions
   was not verified.
10. **Single implementations** (none is load-bearing): the reduction of the B0 stage-B triples modulo stabilisers
    (section 8.4); the rank-bound confirmation of step 4 of profile (3,3,1) for B1 (`r4_rank331.py`). Line 4a of
    the table of section 7.5 has one exact implementation (I2) and the referee's.
11. **Not verified at all, and not used:** the dictionary between T18 and the lattice statement (section 1.4), the
    lemma H16, everything about the analogous statement for squared norm 20.
12. **Parts of this text that only its author has checked:** Proposition 3.1 as written here (it is the referee's
    proof); the completed case analysis of Lemma 4.7; the proofs of (F7) in Lemma 7.5 and of the upper bound of
    (D3) in Lemma 8.7; item 6 above. Two small scripts written for this text (`_check_text_defs.py`,
    `_check_survivors.py`, in the folder of this document) confirm that the definitions (R1), (R2) of section 7.1
    reproduce the numbers 99, 63, 25514, 13799, 9229, and that the data printed in appendix B reproduce the
    determinants 47684 and 874944; they are transcription checks, not part of the proof.

### 9.4 Statements of the working reports that are not used and are left out

- **A7** (consequences of H16 for independent triples of B): conditional on H16, not verified by the referee, and
  no enumeration uses it.
- **P6, P7, P8** of `lemma/t18_STRUCT` (a_2 <= 2 on X_2; a_2 in {2,3,4} on W; a multigraph reformulation at p): no
  written proof, not verified by the referee, no enumeration prunes with them.
- P1, P3, P4, P5 of `lemma/t18_STRUCT` (three integer eigenvectors; a rank-nullity count; t is even; t != 8): found
  correct by the referee, not needed. Identity (*) is proved directly in Lemma 5.4.
- The by-product of the n_3 = 0 report (a_0 <= 5 outside S, a_2 <= 3 on X_2, a_2 <= 6 on X_1, a_2 <= 8 on
  X_0 \ {p}): found correct by the referee; used only in a partial side route for B0 (`b0_x0.py`), not here.
- The computed bullets of A6 (`rows.py`: d(a_c) <= 2; no vertex with d = 3 for B1; "6 classes of d = 3 types remain
  for B0, 9 for B2"): superseded by Theorem 5.3.
- The enumerations of the cases e = 1, e = 2 and k = 2 by `enum_S.py`, `verify_S.py`, `level1.py` (all empty or
  dead): machine confirmations of Lemmas 4.5-4.7, not needed.
- The "X_0-first" route for B0 (`b0_x0.py`, 81 of 2667 representatives), the lattice tests, the "level-1" and
  "star" experiments, the kernel condition of stage D: partial or inconclusive, not used.

### 9.5 Corrections made with respect to the working reports (the referee's nine remarks)

1. First step missing for squared norm 18: Proposition 3.1.
2. The bound h_0 <= 1 depended on a computed fact: Theorem 5.3 is now placed before Lemma 5.4-Proposition 5.7,
   which are pure hand proofs.
3. Wrong sentence on the violated matrix: both matrices are defined in section 6.1 and section 7.6 gives the
   counts with M1 alone.
4. Lemma 4.7: case C added; the two missing justifications of case B added; the use of k = 2 made explicit.
5. Stage-1 tests: defined and proved in Lemma 7.2, with the meaning of the four tests of the program header.
6. Counters: line 1 of section 7.5 (budget-only counts), the "type solutions" of section 8.4 (counted without
   (C6)), and the 846 of section 8.7 (with the upper bound of (D3)) are described as what they count.
7. Lemma 7.4 (e) states that the six other vertices of X_0 have no neighbour in W u {z_0, sigma z_0}.
8. Superseded statements removed: the "open case" of the four survivors (section 8.5), "B0 is open" and "one
   implementation for stage C of B1" (section 8.4), the d = 3 classes of A6 (section 9.4).
9. Unverified and unused statements left out: section 9.4.


## Appendix A. Programs, outputs and commands

Paths are relative to the root of the repository `conway99-c2-aws`. "python" is Python 3 with numpy; the programs
of `lemma/t18_VERIF331` and `ref8_survivors.py` also need python-flint, and `show_structs.py` needs sympy. Each
command is run in the folder of the script (the scripts read their inputs next to themselves). The command lines
are those recorded in the working reports, in the driver logs, or in the headers of the scripts; where the exact
arguments of a run were not recorded, the usage line is given and the names of the output files show how the work
was split. s (or g) is 0, 1, 2 for B0, B1, B2.

### A.1 Computation 4.10 (the three graphs)

| program | command | output |
|---|---|---|
| `lemma/t18/enum_S.py` | `python enum_S.py` | `structures.json` (printed counts quoted in `T18_REPORT.md`, section D: "(i) e=0: labelled 792, iso classes 3") |
| `lemma/t18/verify_S.py` | `python verify_S.py` | `verify_S.out` ("(i) e=0: labelled 55440, iso classes 3") |
| `lemma/t18/show_structs.py`, `check_iso.py` | `python show_structs.py`, `python check_iso.py` | `show_structs.out` (edges, automorphisms, codegrees), `check_iso.out` |
| `lemma/t18_REFEREE/ref1_quartic9.py` | `python ref1_quartic9.py` | `ref1_quartic9.out` (1024380 labelled graphs, 16 classes, 3 with codegrees <= 2) |

### A.2 Computation 7.3 (stage 1)

| program | command | output |
|---|---|---|
| `lemma/t18/rows.py` (prerequisite of the next line) | `python rows.py` | `rows.out`, `types.json` |
| `lemma/t18/r2_stage1.py` | `python r2_stage1.py <s>` | `r2_stage1_<s>.out`, `r2_tau_<s>.json` |
| `lemma/t18/r3_verify.py` | `python r3_verify.py stage1 <s>` | `r3v_stage1_<s>.out` (for B2 also `lemma/t18_B2/b2v_stage1.out`) |
| `lemma/t18_VERIF331/v1_stage1.py` | `python v1_stage1.py <g>` | `v1_stage1_<g>.out`, `v1_tau_<g>.json`, `v1_tau_<g>_nopsd.json` |
| `lemma/t18_REFEREE/ref2_stage1.py` | `python ref2_stage1.py B0 B1 B2` | `ref2_stage1_B<g>.out` |
| `lemma/t18_REFEREE/ref10_tau_files.py` | `python ref10_tau_files.py` (after `ref4_stageB.py`) | `ref10_tau_files.out` |

### A.3 Computation 7.6 (profile (3,3,1))

| line of section 7.5 | program | command | output |
|---|---|---|---|
| 1, 2 | I1: `lemma/t18/r2_hfirst.py` | `python r2_hfirst.py <s> <part> <nparts> <time limit>` (B0, B2: one part; B1: three parts; R2_CAP large enough to save all survivors) | `r2hf_0_all.out`, `r2hf_1_0.out`, `r2hf_1_1.out`, `r2hf_1_2.out`, `r2hf_2_all.out`; `r2_hfirst_0_0of1.json`, `r2_hfirst_1_{0,1,2}of3.json`, `r2_hfirst_2_0of1.json` |
| 3a, 3b | I1: `lemma/t18/r2_stage2.py` | `R2_SURV=<files of r2_hfirst.py> [R2_IDX=<matchings>] python r2_stage2.py <s> <part> <nparts> <time limit>` | B0: `r2ext_0_g0.out`, `r2ext_0_g1.out`, `r2ext_0_g2.out`, `r2_stage2_0_0of1_surv_idx{0,1,2}.json`, summary `r2_summary_0.out`; B1: `r2ext_1_0.out`, `r2ext2_1_g0.out`, `r2ext2_1_g1.out`, `r2ext2_1_g2.out`, `r2_stage2_1_0of3_surv.json`, `r2_stage2_1_0of1_surv_idx{1,2,4}.json`, summary `r2_summary_1.out` (`python r2_summary.py`); B2: `r2ext_2.out`, `r2_stage2_2_0of1_surv.json` |
| 4b | I1: `lemma/t18/r2_ext2.py` | `python r2_ext2.py <s> <files of r2_stage2.py>` | B0: `r2_ext2_B0.out`; B1: `r2_ext2_part0.out`, `r2_ext2_g0.out`, `r2_ext2_g12.out` |
| (check of 4) | I1: `lemma/t18/r2_ext2_bruteforce.py` | `python r2_ext2_bruteforce.py <s> <file> <number of tables>` | `r2_bf_B0.out`, `r2_bf_B1.out`, `r2_bf_B1b.out` |
| (check of 4, B1) | `lemma/t18/r4_rank331.py` | `python r4_rank331.py <max tables> <time limit> <files of r2_stage2.py>` | `r4_rank331.out` |
| 1, 2 | I2: `lemma/t18_VERIF331/v2_stage2.py` | `python v2_stage2.py <g> <part> <nparts>` (default T18_MATS=2; T18_MATS=1 for M1 alone) | `v2_stage2_<g>_m2.out`, `v2_surv_<g>_m2_0of1.json` (and `_m1` for M1 alone) |
| 3a, 3b, 4b | I2: `lemma/t18_VERIF331/v3_stage34.py` | `python v3_stage34.py <g> <part> <nparts>` (T18_ROWPSD=0 for the raw counts) | `v3_stage34_<g>_m2*.out`, `v3_out_<g>_m2_*.json` |
| 4a, 4b | I2: `lemma/t18_VERIF331/v7_step4_direct.py` | `python v7_step4_direct.py <g>` (g = 0, 1) | `v7_step4_0.out`, `v7_step4_1.out` |
| comparison of the sets | I2: `v4_compare39.py`, `v4_compare45.py` | `python v4_compare39.py <g>`, `python v4_compare45.py <g>` | `v4_compare.out` |
| summary; M1 alone | I2: `v5_summary.py`, `v6_m1_final.py` | `python v5_summary.py`, `python v6_m1_final.py 1` | `v5_summary.out`, `v6_m1_final.out` |
| 1-3 (B2) | I3: `lemma/t18_B2/e331.py` | `python e331.py 2 0 1 280` ; `python e331_compare.py 2 r2_hfirst_2_0of1.json` | `e331_2.out`, `e331_compare_2.out` |
| 1, 2 | R: `lemma/t18_REFEREE/ref6_p331.py` | `python ref6_p331.py <B0, B1 or B2>` (REF_M1ONLY=1 for M1 alone) | `ref6_p331_B<g>.out`, `ref6_p331_B<g>_0of1.json` (and `_M1only`) |
| 3a-4b | R: `ref7_p331_ext.py` (B2), `ref7b_p331_ext.py` (B0, B1) | `python ref7b_p331_ext.py <B0 or B1> ref6_p331_B<g>_0of1.json <part> 3` | `ref7_p331_ext_B2.out`, `ref7b_p331_ext_B<g>_<part>of3.out`; totals in `ref9_totals.out` (`python ref9_totals.py`) |

### A.4 Computation 8.4 (stage B of profile (2,5,0))

| graph | program | command | output |
|---|---|---|---|
| B1 | E: `lemma/t18/r3_p250.py` | `python r3_p250.py 1 <part> <nparts> <time limit> BC`, with R3_IDX=<matchings> for the later launches | 14 files `r3_p250_1_*_BC.json` (listed, with the launch of each, in `lemma/t18_B0_VERIFC/04_b1_coverage.out`); logs `r3_1_*.out` |
| B1 | V: `lemma/t18/r3_verify.py` | `python r3_verify.py B250 1 <part> 3 <time limit>` | `r3v_B250_1_{0,1,2}.out`, `r3v_B250_1_{0,1,2}of3.json` |
| B1 | comparison | `python r3_finalB.py` | `lemma/t18/r3_finalB.out` |
| B0 | E: `lemma/t18_B0/r3_p250.py` (unchanged copy) | `python r3_p250.py 0 0 1 540 B` | `b0_enumB.out`, `r3_p250_0_0of1_B.json` (not in git) |
| B0 | V: `lemma/t18_B0/r3_verify.py`, `b0_verify.py` | `python r3_verify.py B250 0 0 1 540`, then `b0_verify.py` (the same program with the list R3V_TAUS of matchings 418..424) | `b0_verB.out`, `b0_verB_t418.out`, `r3v_B250_0_0of1.json`, `r3v_B250_0_0of1_t418.json` |
| B0 | comparison | `python b0_compareB.py` | `lemma/t18_B0/b0_compareB.out` |
| B2 | E: `lemma/t18_B2/r3_p250.py` (unchanged copy) | `python r3_p250.py 2 0 2 560 BC` ; `python r3_p250.py 2 1 2 560 BC` | `b2_BC_0of2.out`, `b2_BC_1of2.out`, `r3_p250_2_{0,1}of2_BC.json`, statistics `b2_stats.out` |
| B2 | V: `lemma/t18_B2/r3_verify.py` | `python r3_verify.py B250 2 0 1 540` | `b2v_B250.out`, `r3v_B250_2_0of1.json` |
| B2 | comparison | `python r3_verify.py compareB 2 r3_p250_2_0of2_BC.json r3_p250_2_1of2_BC.json` | `lemma/t18_B2/b2_compareB.out` |
| all | R: `lemma/t18_REFEREE/ref4_stageB.py` | `python ref4_stageB.py <B0, B1 or B2>` | `ref4_stageB_B<g>.out`, `ref4_stageB_B<g>_0of1.json` |
| all | observed distributions | `python check_lemmas_stageB.py` (`lemma/t18_STRUCT`) | `check_lemmas_stageB.out` |

### A.5 Computation 8.5 (stage C of profile (2,5,0))

| graph | program | command | output |
|---|---|---|---|
| B1 | E | the runs of A.4 (stages "BC") | `r3_finalB.out`, `r3_round5.out`; survivors in `r3_p250_1_0of3_idx752_BC.json` (#813) and `r3_p250_1_2of3_idx758_BC.json` (#975) |
| B1 | C: `lemma/t18_B0_VERIFC/c_mine.py` | `python b1_coverage.py in_B1 in_B1v B1/b1_stageB_all.json` ; `python run_parts.py B1 6 1 24 3000 all B1/b1_stageB_all.json` (which runs `python c_mine.py 1 <part> 24 3000 b1_stageB_all.json` for the 24 parts) ; `python check_complete.py B1 1 4977 275 - B1/b1_stageB_all.json` ; `python b1_survivors_compare.py B1 in_B1 control_B1/c_mine_1_0of1_t813.json` | `04_b1_coverage.out`; `B1/c_mine_1_<part>of24.json`, `.out`; `11_B1_check_complete.out`, `12_B1_check_complete_verifier_list.out`, `13_B1_survivors_compare.out` |
| B1 | C, control on #813 and #975 | `C_TAUS=813,975 python run_parts.py control_B1 1 1 1 3000 all in_B1v/r3v_B250_1_{0,1,2}of3.json` ; `python check_complete.py control_B1 1 170 2 813,975 <the same three files>` | `control_B1/c_mine_1_0of1_t813.json`, `05_control_B1_check.out`, `06_control_B1_compare.out`, `07_control_B1_vs_B2session.out` |
| B1 | partial: V, `r4_verifyC.py`, `r4_verifyC2.py` | `python r3_verify.py C250 1 ...` ; `R4V_FULL=1 python r4_verifyC2.py 1 <part> 2 470` ; `python r4_compareC_final.py` | `lemma/t18/r4_compareC_final.out` |
| B0 | E: `lemma/t18_B0/b0_stageC.py`, `b0_stageC2.py` | `python b0_orbitsB.py` ; `bash b0_loopC.sh` (slices of at most 560 s) ; `python b0_summaryC.py` | `b0_orbitsB.out`, `b0_stageB_reps.json`; `b0_stageC_done_*.jsonl`, `b0_stageC_r*_*.out`; summary in `lemma/t18_B0/REPORT.md` ("FINAL STATE") |
| B0 | C: `lemma/t18_B0_VERIFC/c_mine.py` | `python run_parts.py B0 6 0 24 3000 all in_B0/r3_p250_0_0of1_B.json` ; `python check_complete.py B0 0 5595 133 - in_B0/r3_p250_0_0of1_B.json` ; `python b0_input_crosscheck.py <enumerator file> <the two verifier files> r2_tau_0.json` | `B0/c_mine_0_<part>of24.json`, `.out`; `09_B0_check_complete.out`; `08_b0_input_crosscheck.out` |
| B0 | V on a sample | `python b0_verify.py C250 0 0 150 270` | `lemma/t18_B0/b0_verC_sample.out` |
| B2 | E | the runs of A.4 | `b2_BC_0of2.out`, `b2_BC_1of2.out` |
| B2 | V | `python r3_verify.py C250 2 0 2 550`, then with R3V_SKIP / R3V_TAKE (0/86 and 86/86 with part 1 of 2, 172/24 with part 0 of 1) | `b2v_C250_0of2.out`, `b2v_C250_odd_skip0.out`, `b2v_C250_odd_skip86.out`, `b2v_C250_skip172.out` |
| B2 | C: `lemma/t18_B2/c_mine.py` | `python c_mine.py 2 0 1 520 r3_p250_2_0of2_BC.json r3_p250_2_1of2_BC.json` | `c_mine_2_all.out`, `c_mine_2_0of1.json` |
| all | R: `lemma/t18_REFEREE/ref5_stageC.py` | `python ref5_stageC.py <B0, B1 or B2> ref4_stageB_B<g>_0of1.json full ...` ; `python ref9_totals.py` | `ref5_stageC_B0_all_*of3.out`, `ref5_stageC_B1_all_*of3.out`, `ref5_stageC_B2.out`, `ref9_totals.out`; type-solution variants in `ref5b_types_variants_B2.out` |

The input file `in_B0/r3_p250_0_0of1_B.json` of the B0 run of C is the stage-B file of E (1.2 MB, not in git); the
log `00_setup_hashes.log` records its hash and that of the copies of `c_mine.py` and `r2_tau_<s>.json`.

### A.6 Computations 8.6 and 8.8 (the four survivors of B1)

| what | program | command | output |
|---|---|---|---|
| exact re-examination | `lemma/t18/r3_survivors.py` | `python r3_survivors.py 1 <files r3_p250_1_*_BC.json>` | `r3_survivors.out` |
| rank bound | `lemma/t18/r4_rank.py` | `python r4_rank.py 1 <files r3_p250_1_*_BC.json>` | `r4_rank.out` |
| rank bound | `lemma/t18_STRUCT/rank_survivors.py`, `rank_survivors_check2.py` | `python rank_survivors.py` ; `python rank_survivors_check2.py` | `rank_survivors.out`, `rank_survivors_check2.out` |
| rank bound | `lemma/t18_B2/rank_B1_survivors.py` (uses `rankbound.py`) | `python rank_B1_survivors.py` | `rank_B1_survivors.out` |
| rank bound | `lemma/t18_B0/b0_rank47.py` | `python b0_rank47.py 1 ../t18/r3_p250_1_*_BC.json` | `b0_rank47_B1control.out` |
| rank bound, stage D | `lemma/t18_REFEREE/ref8_survivors.py` | `python ref8_survivors.py` | `ref8_survivors.out` |
| stage D | `lemma/t18/r4_stageD.py` | `python r4_stageD.py 1 <files r3_p250_1_*_BC.json>` ; `python r3_verify.py certs r4cert_stageD_B1.jsonl` | `r4_stageD_B1.out`, `r4_stageD_B1.json`, `r4cert_stageD_B1.jsonl` (not in git) |
| stage D | `lemma/t18/r4_verifyD.py` | `python r4_verifyD.py 1 <files r3_p250_1_*_BC.json>` | `r4_verifyD.out` |
| stage D | `lemma/t18_B2/d_stage.py` | `python d_stage.py 1 B1check <file with the survivors>` ; `python r3_verify.py certs ...` | `d_stage_B1check.out`, `d_stage_B1check.json`, `b2_certs_check.out` |


## Appendix B. The four stage-C survivors of B1, explicitly

The data below are copied from the output files of C (`lemma/t18_B0_VERIFC/B1/c_mine_1_{3,4,5}of24.json`), which
contain the same four 47-vertex graphs as the output files of E. They allow Computation 8.6 to be redone
independently of all the files.

Graph B1: edges 01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78. Its deficient pairs, with their indices k:

    0:01  1:02  2:03  3:04  4:13  5:16  6:18  7:24  8:27  9:28  10:35  11:37  12:45  13:46  14:56  15:57  16:68  17:78

Vertices of Y47: x_0..x_8, y_0..y_8, p, s_0..s_17 (s_k is the vertex of X_2 attached to the deficient pair of index
k), w_0..w_4 and their mates. Adjacencies:

- x_i ~ y_j iff ij is an edge of B1; no other edge inside S; p has no neighbour in S;
- s_k ~ x_i for the two indices i of the deficient pair k, and s_k ~ y_l for the two indices l of the deficient pair
  tau k; sigma s_k = s_{tau k};
- p ~ s_k for k in A_p; p ~ w_c and p ~ sigma w_c for all c; w_c ~ sigma w_c;
- s_k ~ s_l for the pairs k-l listed under "H";
- w_c of type (i ; j): w_c ~ x_i, w_c ~ y_j, sigma w_c ~ x_j, sigma w_c ~ y_i; w_c ~ s_k for k in K_c and
  sigma w_c ~ s_k for k in tau K_c;
- no other edges.

sigma exchanges x_i and y_i, s_k and s_{tau k}, w_c and sigma w_c, and fixes p. For the rank bound take
R = {x_0, ..., x_8} u {s_k : k < tau k} u {w_0, ..., w_4} (23 vertices).

**Matching #813**: tau = 0-5, 1-8, 2-15, 3-14, 4-7, 6-10, 9-12, 11-17, 13-16 (pairs of indices), i.e. the rectangles
01|16, 02|27, 03|57, 04|56, 13|24, 18|35, 28|45, 37|78, 46|68.

*Survivor #813, F = [2, 9].* A_p = {s_2, s_9, s_12, s_15}. H: 0-12, 2-15, 5-9, 9-12 (t = 4).

    w_0: type (0;4), K = {6, 11, 13}      (tau K = {10, 16, 17})
    w_1: type (1;3), K = {3, 8, 16}       (tau K = {1, 13, 14})
    w_2: type (1;6), K = {6, 7}           (tau K = {4, 10})
    w_3: type (2;8), K = {3, 4, 17}       (tau K = {7, 11, 14})
    w_4: type (6;7), K = {0, 8}           (tau K = {1, 5})

*Survivor #813, F = [3, 6].* A_p = {s_3, s_6, s_10, s_14}. H: 1-10, 3-14, 6-8, 6-10 (t = 4).

    w_0: type (0;3), K = {9, 11, 13}      (tau K = {12, 16, 17})
    w_1: type (1;8), K = {2, 7, 16}       (tau K = {4, 13, 15})
    w_2: type (2;4), K = {2, 5, 17}       (tau K = {0, 11, 15})
    w_3: type (2;7), K = {4, 9}           (tau K = {7, 12})
    w_4: type (6;7), K = {0, 8}           (tau K = {1, 5})

**Matching #975**: tau = 0-5, 1-12, 2-17, 3-14, 4-11, 6-10, 7-9, 8-15, 13-16, i.e. the rectangles
01|16, 02|45, 03|78, 04|56, 13|37, 18|35, 24|28, 27|57, 46|68.

*Survivor #975, F = [1, 2].* A_p = {s_1, s_2, s_12, s_17}. H: 1-12, 2-17 (t = 2).

    w_0: type (1;2), K = {6, 11, 13}      (tau K = {4, 10, 16})
    w_1: type (1;8), K = {3, 9, 15}       (tau K = {7, 8, 14})
    w_2: type (3;4), K = {5, 8, 13}       (tau K = {0, 15, 16})
    w_3: type (5;6), K = {5, 7, 11}       (tau K = {0, 4, 9})
    w_4: type (6;7), K = {3, 10}          (tau K = {6, 14})

*Survivor #975, F = [3, 6].* A_p = {s_3, s_6, s_10, s_14}. H: 3-14, 6-10 (t = 2).

    w_0: type (0;2), K = {4, 8, 13}       (tau K = {11, 15, 16})
    w_1: type (1;2), K = {1, 17}          (tau K = {2, 12})
    w_2: type (3;4), K = {5, 7, 8}        (tau K = {0, 9, 15})
    w_3: type (6;7), K = {2, 9, 11}       (tau K = {4, 7, 17})
    w_4: type (7;8), K = {0, 12, 16}      (tau K = {1, 5, 13})

Transcription check made for this text (`_check_survivors.py`, in the folder of this document; not part of the
proof): the four graphs built from these lists are sigma-invariant, satisfy every budget, coincide with the
graphs stored by E, and give det G_odd = 47684, 47684, 874944, 874944 (fraction-free Bareiss in Python integers)
and rank G_even = 23.


## Appendix C. Correspondence with the labels of the working reports

| label in the working reports | here |
|---|---|
| A0 (`T18_REPORT.md`) | Lemma 2.1, Corollary 2.2 |
| first step, integer => 0/+-1 (`t18_REFEREE/REPORT.md`, section 3) | Proposition 3.1 |
| items 1-5 of `LEMMA_TARGET`, section 3 | sections 4.1-4.4 and 4.9 |
| A1 (parity law) | Lemma 4.5 |
| A2, A3, A4 | Lemmas 4.6, 4.7; Corollary 4.8 and the remark after it |
| A5 | Corollary 4.8, Lemma 4.9, Computation 4.10, Corollary 4.11 |
| A6, hand bullets | Lemmas 5.1, 5.2 |
| N3: Lemma 1, Lemma 2, Theorem (`N3_REPORT.md`) | Lemma 5.1, Lemma 5.2, Theorem 5.3 |
| A8 | Lemma 5.4 |
| A9; the profile split | Lemma 5.6, Proposition 5.7; Lemma 5.5 |
| P2 (`t18_STRUCT/REPORT.md`) | Lemma 6.3, Proposition 6.4 |
| stage-1 tests (i), (i'), (iii), (P) (header of `r2_stage1.py`) | Lemma 7.2 and the remarks after it; Computation 7.3 |
| A10 | Lemmas 7.4, 7.5 |
| A11, A12, A13 | Computation 7.6, Proposition 7.7, sections 7.5 and 7.6 |
| A14 a-h; C-a to C-d (`t18_B2/REPORT.md`) | Lemmas 8.1, 8.2, 8.3 |
| A15, A16, A17, A20 | Computations 8.4, 8.5 |
| A18 | Lemma 8.7 |
| A19; A19b | Computation 8.8; Computation 8.6 |
| A21 | note in section 7.5 (`r4_rank331.py`) |
| A7; P1, P3-P8 | not used (section 9.4) |


## Appendix D. Numbering of the vertices in the files

- Programs of `lemma/t18`, `lemma/t18_B0`, `lemma/t18_B2`, `lemma/t18_B0_VERIFC` and of the referee:
  x_i = i and y_i = 9 + i (i = 0..8); p = 18; the vertex s_k of X_2 attached to the deficient pair of index k is
  19 + k, its mate is 19 + tau k; in profile (2,5,0), w_c = 37 + 2c and sigma w_c = 38 + 2c (c = 0..4), and in
  stage D the vertices of X_0 \ {p} are 47..54; in profile (3,3,1) (`r2_hfirst.py`, `e331.py`, `ref6_p331.py`),
  z_0 = 37 and sigma z_0 = 38. `r2_ext2.py` and `r4_rank331.py` renumber: support 0..17, X_0 = 18..26 (p = 18),
  X_2 = 27..44, W from 45.
- Programs of `lemma/t18_VERIF331`: x_i = i, y_i = 9 + i, p = 18, z_0 = 19, sigma z_0 = 20, A_p = 21..26 (three mate
  pairs), X_2' = 27..38 (orbit number k is 27 + 2k, 28 + 2k), then the added vertices.
- "F = [a, b]" (or [a, b, c]) lists, for each rectangle of F, the smaller of the two indices of its deficient pairs.
- "Matching #n" is the entry n (from 0) of the list "reps" of `lemma/t18/r2_tau_<s>.json`; an entry is the list
  (tau 0, tau 1, ..., tau 17) of the images of the 18 indices.
