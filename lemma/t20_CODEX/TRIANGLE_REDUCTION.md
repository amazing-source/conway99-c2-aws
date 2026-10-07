# T20 profile (4,2,1): the isolated X0 triangle and its neighbourhood

Codex, 2026-10-07. Hand deductions from `PROFILE_421.md`.

Reviewed by the desktop Claude peer in bridge message 34. The independent
small local check `rigidity_n3.py --require-x3-neighbour` leaves the same
PSD-surviving counts (21,110,39,59,72,33) as isolation alone. Thus beta=1
replaces a computational exclusion by a hand proof; it does not remove
additional bases from that already PSD-filtered list. See
`rigidity_n3_attached.json` for this consistency check.

Let T={p,u,u'} be the inner X0 triangle. The isolation theorem states
that it is a connected component of the graph induced on X0. Put
U=N(T) minus T and Z=V minus (T union U).

## The triangle partition

Each vertex outside a triangle has at most one neighbour in it: two
would make a second common neighbour for an edge of that triangle.
Consequently U is the disjoint union of three sets U_t=N(t) minus T,
t in T, each of size 12. Thus |U|=36 and |Z|=60.

Every vertex of Z has exactly two neighbours in each U_t. Indeed it is
nonadjacent to t and its two common neighbours with t cannot be in T.
Thus every vertex of Z has six neighbours in U and eight in Z.

Every vertex a in U_t has exactly one neighbour in U_t, from the perfect
matching in N(t). For t' in T minus {t}, a and t' are nonadjacent and
already have t as a common neighbour. Their unique other common
neighbour lies in U_t'. Thus a has exactly one neighbour in each of
the other two U-groups. U induces a cubic graph: each group has a
perfect matching and each pair of groups is joined by a perfect matching.

These assertions use only strong regularity and the fact that T is a
triangle. Its additional X0-isolation implies

    U intersect S = empty,       U intersect X0 = empty.   (1)

The first holds because an X0 vertex has no support neighbour; the
second is the isolation theorem.

## Theorem: when n3=2, the X3 orbit must meet U

Suppose n3=2, write X3={z,z'}, and put beta=a3(u)=a3(u') in {0,1}.
Then **beta=1**: after exchanging z,z' if necessary, z~u and z'~u'.

Proof. If beta=0, neither z nor z' is adjacent to T (they are also
nonadjacent to p by the established reductions). Thus z belongs to Z
and has six neighbours in U. By (1), none can be in S or X0. Nor can
one be in X3: z' is nonadjacent to z. They must all lie in X1 or X2.

But G0 for z gives a0(z)=a2(z)+3 and a1(z)=5-2a2(z). In particular

    a1(z)+a2(z) = 5-a2(z) <= 5,

contradicting six neighbours in U. Hence beta cannot be zero. Since
beta<=1, it is one. QED.

In the terminology of H1 of the lab notes, this removes the whole
sub-case (ii) in which the inner X0 orbit is the third orbit, the one
not met by N(z) intersect X0. No enumeration or PSD test is used.

## Residual class sizes

For n3=0, the group at p has eight X2 and four X1 vertices. Each of
the two other groups has eight X2 and four X1 vertices as well, by
the isolation theorem and G0 at u,u'. Thus:

| set | S | X0 | X1 | X2 | X3 |
|---|---:|---:|---:|---:|---:|
| T | 0 | 3 | 0 | 0 | 0 |
| U | 0 | 0 | 12 | 24 | 0 |
| Z | 20 | 6 | 28 | 6 | 0 |

For n3=2, the theorem gives beta=1. The group at p again has eight
X2 and four X1 vertices; each other group has six X2, five X1, and
one X3 vertex. Thus:

| set | S | X0 | X1 | X2 | X3 |
|---|---:|---:|---:|---:|---:|
| T | 0 | 3 | 0 | 0 | 0 |
| U | 0 | 0 | 14 | 20 | 2 |
| Z | 20 | 4 | 32 | 4 | 0 |

All entries follow from the previously proved class sizes and G0.
In both branches, Z contains equally many X0 and X2 vertices: six
or four. This is a reduction of the remaining model, **not a proof
that it cannot exist**.
