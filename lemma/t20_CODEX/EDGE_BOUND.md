# T20, n3=0: the extremal edge count e(X0)=9 is impossible

Codex, 2026-10-07. **Hand proof.** In case I with n3=0, this strengthens
the existing bounds to

    e(X0) <= 8,          e(X2) <= 35.

It applies to both remaining profiles and all six support graphs.
It does not exclude every remaining case of T20.

## Identities and an equality case

Let b(q)=a0(q)=|N(q) intersect X0| and s=e(X0). We have
|X0|=9, |X1|=40, |X2|=30, and the identity G0 gives

    a2=b+6 on X0,   a2=b+3 on X1,   a2=b on X2.

The proved edge identities in `t20_HAND/NOTES.md` H4 give
e(X2)=s+27 and

    sum_{q in X1} b(q) = e(X0,X1) = 72-4s.

Substitute G0 into H4's identity Q0 and use
(b-1)(b-2)=b(b-1)-2b+2. This gives

    sum_X0 b^2 + sum_X1 b(b-1)
        + sum_X2 (b-2)(b-3) = 108-8s.                    (1)

Both product sums are nonnegative because b is a nonnegative integer.
The known bound is s<=9. Suppose for contradiction s=9. Since
sum_X0 b=2s=18, Cauchy gives sum_X0 b^2 >= 18^2/9=36, which equals
the entire right side of (1). Equality holds in all three inequalities:

- b=2 on X0;
- b is 0 or 1 on X1;
- b is 2 or 3 on X2.

Define D={q in X1:b(q)=0}, H=X1 minus D, E={q in X2:b(q)=3}, and
F=X2 minus E. Then

    |D|=4, |H|=36, |E|=12, |F|=18.                      (2)

Indeed sum_X1 b=36, while sum_X2 b=2e(X2)=72, so
2|F|+3|E|=72 with |E|+|F|=30. Each of these sets is sigma-invariant.

## An even eigenfunction

Put q=1_X0 and define the integer-valued function

    psi = 3q - A q + 1.

Using A^2=12I-A+2J, A1=14*1, and Jq=9*1, we obtain

    A psi = 3Aq - (12q-Aq+18*1) + 14*1
          = -4(3q-Aq+1) = -4 psi.                       (3)

No small-norm result is being applied to psi. Its role is just to
encode a counting identity at individual vertices. Its values are

| set | X0 | S | D | H | E | F |
|---|---:|---:|---:|---:|---:|---:|
| psi | 2 | 1 | 1 | 0 | -2 | -1 |

Here b=0 on S because no X0 vertex has a neighbour in the support.

## The forced structure on X2

For any subset T write d_T(x)=|N(x) intersect T|.

Take d in D. It has two neighbours in S, no neighbour in X0, and by
G0 exactly three neighbours in X2 and nine in X1. Evaluate (3):

    -4 = (A psi)(d) = 2 - 3 - d_E(d) + d_D(d),
    d_E(d) - d_D(d) = 3.

Since d_E(d)<=3 and d_D(d)>=0, all three X2 neighbours of d are in E
and d_D(d)=0. Thus D is independent and e(D,E)=4*3=12.

Now take e in E. It has four neighbours in S and, by G0, three in X0,
three in X2, and four in X1. Equation (3) gives

    8 = (A psi)(e) = 4+6-3-d_E(e)+d_D(e),
    d_D(e)-d_E(e)=1.

Every one of the twelve vertices of E therefore has at least one
neighbour in D. But there are exactly twelve D--E edges in total.
Hence d_D(e)=1 and d_E(e)=0 for every e in E: E is independent.

Each vertex of E has three X2 neighbours, now all in F, so e(E,F)=36.
Every vertex of F has exactly two X2 neighbours, and |F|=18. These
36 incident edges are already exhausted by E--F edges. Consequently
F is independent as well. Thus the graph induced on X2 is bipartite
with parts E and F.

## Contradiction from an inner mate edge

The remaining profiles have h2=3 or 4, so some mate edge {a,sigma(a)}
of N(p) is contained in X2. But b(a)=b(sigma(a)), since X0 is
sigma-invariant. Therefore both endpoints belong to E, or both belong
to F, contradicting the independence of those two sets.

Thus s=9 is impossible. Since s is an integer with s<=9, s<=8, and
e(X2)=s+27<=35. QED.

## Useful restatement

Expanding sum_X0(b-2)^2 in (1) gives the exact nonnegative identity

    sum_X0 (b-2)^2 + sum_X1 b(b-1)
        + sum_X2 (b-2)(b-3) = 16(9-s).                  (4)

The argument above shows that its right side cannot be zero. For
profile (4,2,1), `PROFILE_421.md` further gives X0=K3 disjoint union R,
so e(R)<=5. This excludes the entire six-edge possibility on R.

Dependencies: the already proved identities G0/Q0, the class sizes,
strong regularity, and the existence of an inner X2 mate edge. No
computed list of support graphs, PSD computation, dual-norm lemma,
T18, or exhaustive search is used in this argument.
