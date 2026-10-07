# T20: isolation of the inner X0 pair in profile (4,2,1)

Codex, 2026-10-07. **Hand proof, valid for all six support graphs, and for
both n3=0 and n3=2. This does not by itself exclude the profile or prove T20.**

## Hypotheses and notation

Use case I of `T20_WORK.md`: the support S is disjoint from N[p], the
classes X_d partition V minus S, and for every vertex q outside S,

    a_2(q) = a_0(q) + 6 - 3d(q) - 2a_3(q).                 (1)

Here a_j(q)=|N(q) intersect X_j|. The already proved reductions give
n3 in {0,2}, n0=9-n3, n2=30-3n3. Assume profile (h2,h1,h0)=(4,2,1).
Thus N(p) contains eight vertices of X2, four of X1, and one mate pair
u,u' in X0. The set {p,u,u'} induces a triangle. Define

    R = X0 minus {p,u,u'},      t = |N(u) intersect R|.

R is sigma-invariant and consists of words: six if n3=0, four if n3=2.
By symmetry u' has t neighbours in R. A word means a vertex outside
N[p]; it has exactly two neighbours in N(p), is not adjacent to its mate,
and has exactly two common neighbours with its mate. The neighbourhood
N(p) induces seven disjoint mate edges. In particular a vertex other
than p cannot be adjacent to both ends of an inner mate edge.

## Theorem

**There is no edge between {u,u'} and R.** Consequently X0 is the disjoint
union of the triangle {p,u,u'} and the induced graph on R.

### Proof for n3=0

We have a0(u)=2+t, so (1) gives a2(u)=8+t. All these X2 neighbours are
words, since the only neighbours of u in N(p) are its mate u' (in X0).
Put A=N(u) intersect X2, and A'=sigma(A)=N(u') intersect X2. Since u~u'
has p as its unique common neighbour, A and A' are disjoint. There are
30-8=22 words in X2. Their complement W outside A union A' has size

    |W| = 22 - 2(8+t) = 6-2t,                             (2)

and is sigma-invariant.

Suppose t>0 and choose v in R adjacent to u. It is not adjacent to u'.
Write b=a0(v)>=1. Equation (1) gives a2(v)=b+6. Of the two neighbours of
v in N(p), one is u in X0, so at most one is in X2. Thus v has at least
b+5 word neighbours in X2.

At most one lies in A, since u~v has one common neighbour. At most one
lies in A', since u' and v are nonadjacent and already have u as one
common neighbour (u is not in X2). All other X2 word neighbours lie in W.
Therefore

    b+5 <= 1+1+|W| = 8-2t,  hence b+2t <= 3.             (3)

With b,t positive integers this forces b=t=1. Equality holds in every
bound above, so v is adjacent to all four vertices of W. Since W is
sigma-invariant, its mate sigma(v) is adjacent to all four as well.
This contradicts the fact that the two word mates have exactly two
common neighbours. Thus t=0. QED for n3=0.

### Proof for n3=2

Write X3={z,z'} with z'=sigma(z), and let beta=a3(u)=a3(u'). This is 0
or 1: beta=2 would make z (and z') an additional common neighbour of
the adjacent inner mates u,u'. Formula (1) now gives

    a2(u) = 8+t-2beta.

As before A and A' are disjoint and consist of words. There are now
24-8=16 words in X2, so the sigma-invariant complement W has size

    |W| = 16 - 2(8+t-2beta) = 4beta-2t.                  (4)

If beta=0, nonnegativity of |W| immediately gives t=0. Suppose beta=1
and t>0, and choose v in R adjacent to u. Set b=a0(v)>=1 and
gamma=a3(v)<=2. By (1), a2(v)=b+6-2gamma. As above, at most one of these
neighbours is inner, so at least b+5-2gamma are words.

The total number of X2 common-neighbour places for (u,v) and (u',v) is
at most two before considering X3: one from the adjacent pair, and one
from the nonadjacent pair after reserving its already known common
neighbour u. Since beta=1, u is adjacent to exactly one of z,z', and
u' to the other. Each of v's gamma neighbours in X3 therefore consumes
one of those two places. Consequently

    |N(v) intersect A| + |N(v) intersect A'| <= 2-gamma.

Combining this with (4) gives

    b+5-2gamma <= 2-gamma+4-2t,
    b+2t-gamma <= 1.                                      (5)

The bounds b>=1, t>=1, gamma<=2 force b=t=1 and gamma=2. Thus W has
two vertices, both common-neighbour bounds in A and A' are zero, and
v is adjacent to all of W. Its mate is also adjacent to W. But gamma=2
says both word mates are adjacent to both z and z' as well. They have
at least four common neighbours, W union X3, a contradiction. Thus
t=0 also in this final case. QED.

## Immediate consequences

- For n3=0: a0(u)=2, a2(u)=8, a1(u)=4; A and A' have eight vertices
  each and W has six vertices (three word orbits).
- For n3=2: a0(u)=2, a2(u)=8-2beta, a1(u)=4+beta. If beta=0, A and A'
  partition all sixteen X2 words. If beta=1, each has six vertices and
  W has four vertices (two orbits).
- Every word of R has both its neighbours in N(p) among the inner X1
  and X2 vertices, since it has no neighbour in {u,u'}.

The proof uses only the previously proved counting identity (1), the
class sizes, the profile, and lambda=1, mu=2. It uses no enumeration,
positive-semidefiniteness calculation, small-norm lemma, or T18.

Review: Claude (lab session) checked the n3=0 argument line by line in
bridge message 24, and the n3=2 extension in message 26. Both were
forwarded to the laptop session, which confirmed receipt in message 27.

Small follow-up computation (one implementation, not part of this proof):
`rigidity_n3.py` imposes this theorem on the labelled n3=2 bases of H1/H2
and uses direct rational elimination for both PSD matrices. It leaves
21 / 110 / 39 / 59 / 72 / 33 labelled bases for I.0,...,I.5 in profile
(4,2,1). No isomorphism quotient is taken. No complete T20 configuration
is searched or claimed. Runtime: approximately four seconds, one core.
