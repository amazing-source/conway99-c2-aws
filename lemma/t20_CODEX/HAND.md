# T20: short dual-norm obstructions (Codex, 2026-10-07)

Status: **T20 remains open.** These are necessary local conditions, with full hand
proofs. The small computations below enumerate one or two outside orbits only.
They neither enumerate all bases at p nor prove that any surviving type extends.

## Setting and dependency

We work in case I of `T20_WORK.md`. The ten support representatives x_i have
frame vectors F_i, with Gram 3I+B. Their mates are y_i. Let
v = (sum_i F_i)/7. Then v is in the dual frame lattice L*, v.F_i=1,
v.f_w=0 for every orbit outside the support, and v.v=10/7.
An outside **word** orbit has f_w.f_w=3; an inner orbit has norm 4 and is
not included in the word assertions below. For distinct word orbits,

    f_w.f_t = [w adjacent to sigma(t)] - [w adjacent to t] in {-1,0,1}.

We use the previously established exclusion of nonzero dual vectors with
7u.u equal to 5 or 6 (equivalently odd integer eigenfunctions of squared
norm 10 or 12). These are among the earlier small-norm exclusions cited
in `t20_HAND/NOTES.md`, H6. **Neither T18 nor the norm-16 lemma is needed
for the propositions here.** They also follow from the earlier bound
min(L*) >= 8/7. This dependency is explicit, not a new proof of that bound.

For I contained in {0,...,9}, define

    s_I(w) = |N(w) intersect {x_i:i in I}| - |N(w) intersect {y_i:i in I}|.

Thus f_w.(sum_{i in I} F_i) = -s_I(w).

## Proposition 1: two families of forced cross edges

Suppose either

1. |I|=3 and e_B(I)=0, or
2. |I|=4 and e_B(I)=1.

If w and t represent distinct outside word orbits and s_I(w)=s_I(t)=2,
then w is adjacent to sigma(t), sigma(w) is adjacent to t, and neither
w~t nor sigma(w)~sigma(t) holds.

Proof. Set k=2 in case 1, k=3 in case 2, and put

    u = k v - sum_{i in I} F_i - f_w - f_t in L*.

Write g=f_w.f_t. Since the F_i have norm 3 and off-diagonal Gram B,

    7u.u = 10k^2 + 7((3-2k)|I| + 2e_B(I) + 6 - 2s_I(w)-2s_I(t) + 2g).

This is 5+14g in case 1 and 6+14g in case 2. The choice g=-1 makes a
squared norm negative. The choice g=0 gives a forbidden positive dual
norm. Hence g=1, which is exactly the asserted edge pattern. QED.

Part 1 is D2 of the lab notes with the word-orbit hypothesis made explicit.
Part 2 is its extension to a four-set carrying one B-edge.

## Proposition 2: at most three oriented words per family

Under either hypothesis of Proposition 1, at most three outside word
vertices w satisfy s_I(w)=2.

Proof. A word and its mate have opposite s_I, so such vertices belong
to distinct orbits. Suppose four exist, w_1,...,w_4. Proposition 1 says
w_a~sigma(w_b) whenever a!=b, and w_a is not adjacent to w_b.
Each pair w_a,w_b already has the two distinct common neighbours
sigma(w_c),sigma(w_d), where {c,d} is the complementary pair of indices.
Both lie outside S. Since mu=2, w_a and w_b can have no further common
neighbour in S. But each set N(w_a) intersect {x_i:i in I} has at least
two elements. Four pairwise disjoint such sets would require at least
eight elements in a set of size three or four. Two intersect, giving
a third common neighbour for that pair. Contradiction. QED.

## Corollary 3: the three-word equality case for an independent triple

If I={a,b,c} is independent and exactly three words have s_I=2, their
neighbour sets in x_I are precisely the three distinct two-subsets of
x_I, and none has a neighbour in y_I. For any pair of these words, its
two common neighbours are their unique common vertex of x_I and the
mate of the third word. In particular the pair has no other common
neighbour anywhere in G.

Proof. Proposition 1 gives the mate of the third word as one common
neighbour of each pair. Thus their x_I-neighbour sets, each of size at
least two, intersect in at most one element. In a three-set this forces
the three distinct two-subsets. The equation s_I=2 then gives zero
y_I-neighbours. The two identified common neighbours exhaust mu=2. QED.

## Small exact local computations

`dual_local.py` was written from the work-page edge lists, without importing
any project enumeration code. It generates unordered (U,V) types, allowing
U=V where legal, for one outside orbit and d=0,1,2,3, word or inner. On
S union {p,w,sigma(w)}, it tests all common-neighbour budgets and four
exact rational Schur complements (odd/even sectors of both PSD matrices).
It then tries k=1,2,3, every support subset I, and either sign of f_w in
the dual vector. Result: **no new one-orbit rejection** beyond budgets and
PSD. This tests that family of coefficients only, not every integer m.

`dual_pairs.py` considers two distinct word X2 types, up to reversing each
orbit. It scans precisely the pairs touched by Proposition 1, and all four
possible edge patterns between the orbits. It recomputes all graph budgets
on the induced 25-vertex graph, then checks both PSD matrices exactly by
2-by-2 rational Schur complements, before applying the hand rule.
The rule gives the following additional exclusions of labelled edge patterns:

| B | word X2 types | affected type pairs | budget-valid patterns | PSD-valid patterns | additional rejected patterns | type pairs newly impossible |
|---|---:|---:|---:|---:|---:|---:|
| I.0 | 166 | 104 | 64 | 40 | 8 | 0 |
| I.1 | 253 | 451 | 322 | 122 | 1 | 0 |
| I.2 | 220 | 265 | 205 | 90 | 10 | 5 |
| I.3 | 222 | 288 | 152 | 64 | 0 | 0 |
| I.4 | 222 | 218 | 108 | 46 | 0 | 0 |
| I.5 | 215 | 240 | 180 | 70 | 0 | 0 |

Times on this machine: approximately 3.4 s and 0.9 s, one process, one
numerical-library thread. All arithmetic used to reject is integral or
rational. Output files `dual_local.json` and `dual_pairs.json` include
counts and explicit small-norm witnesses. These are **one implementation**;
computed claims need an independent program before serving as a project
exclusion. The hand propositions do not depend on these counts.

### Exact PSD construction

For the odd sectors, the base matrices are H=3I+B and K=4I-B. K has kernel
span(1); outside coupling b=1_V-1_U has sum zero, so (K+J)^(-1) gives the
correct Schur term on that orthogonal complement. Diagonal entries of an
outside orbit are 3+epsilon and 4-epsilon respectively.

For the even sectors use equal coefficients on x_i,y_i and keep p as a
separate coordinate. The bases are

    E1 = [[18(3I-B)+4J, 2*1], [2*1^T, 28]],
    E2 = [[22(4I+B)-8J, -4*1], [-4*1^T, 42]].

The new even couplings are (4*1-18(1_U+1_V), 2-18epsilon) and
(22(1_U+1_V)-8*1, -4+22epsilon), and diagonal entries are 58-18epsilon
and 80+22epsilon. Between two word orbits with direct/cross edge bits
a,b, the unprojected off-diagonal terms are b-a, a-b, 4-18(a+b), and
-8+22(a+b). Exact Schur determinants produce all PSD decisions quoted.

## Next question

Can Proposition 2, or incompatible requirements coming from several I,
be combined with the forced deficient-pair counts and the seven inner
orbits to exclude an entire profile? No such contradiction is claimed yet.

## Further checks and unsuccessful extensions

`verify_certificates.py` directly reconstructs the two full 25-by-25 PSD
matrices and performs rational elimination. It verifies all 19 saved
additional two-word certificates, independently of the Schur-complement
formula used to discover them. It also recomputes their dual norms from
the signed orbit adjacency matrix. All 19 pass this recheck.

`double_defect.py` tests whether Proposition 1 forces one of the two
outside common neighbours of a doubly deficient support pair to be inner.
It does not: word-word options remain for every such pair in all six
graphs. In I.2 there remain 176 labelled edge patterns for each of its
five doubly deficient pairs. There is no resulting contradiction with
the profile bound h_2<=4.

`dual_n3.py` reconstructs the small bases S union X3 union X0 directly
from the written H1/H2 cases and edge choices, not from the other engine.
Its labelled and budget/degree counts agree with the lab notes:
640/186, 4608/1356, 1536/452, 2176/638, 2432/718, 1536/452.
It searches support coefficients in {0,1}, z coefficient in [-3,3], and
the three X0-orbit coefficients in [-2,2], for k=1,2,3. It finds 119
positive small-norm witnesses after budgets, but **every one of those
bases already fails one of the full PSD tests**, as checked by direct
rational elimination in `verify_certificates.py`. Consequently this
coefficient box gives **no additional n3=2 exclusion**. The search and
certificate recheck each took approximately one second, on one core.
