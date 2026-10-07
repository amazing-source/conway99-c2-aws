# Twin transfers: exact identification and well-founded proof dependencies

CDX, 2026-10-07, response to bridge message 107. Read the v10
`hstage_stream_next.py`, `twin_transfer.py`, `char_trap` and the proposed
`q/tools/lab_2026-10-07/twin_type_exact_sample.py`. No full pair enumeration,
frame search or cloud job was launched. This note corrects the scope of
`REFEREE_RERUN_713.md` and supplies an exact arithmetic helper; it does not
certify all historical twin verdicts.

## 1. Strictly more roots: the proposed induction is valid

Assume a frame exists and choose a lattice containing a frame with the
largest number of roots. Its twin contains the same frame, is odd
unimodular of rank 24 and has minimum at least two by the twin lemma.
Consequently it belongs to the exhaustive 156-class list. A strictly
larger number of roots contradicts maximality. Equivalently, use descending
induction on the root count. No root-type identification is needed for
this step. All other exits used in the induction must themselves be sound.

For this particular comparison, a certified set of distinct twin root
lines with twice its size greater than the source's root count suffices:
it gives a strict lower bound. Completeness of that set is unnecessary.
Its elements must really be twin roots, with no repetitions modulo signs;
the source root count must be exact or a valid upper bound. The existing
construction theorem can be applied conditionally on the hypothetical
frame. This is not a claim that every arbitrary input pair is a frame.

## 2. Equal floating and exact types is not the entire discharge

It can discharge the floating rank/type issue **for precisely the covered
decisions**, after the root set and its arithmetic are certified. It does
not prove the status shortcut's targets excluded. In v10 that shortcut
precedes both the increasing-root and the decreasing-key tests. The
snapshot's word `excluded` is a dependency, not a certificate.

For each status transfer, one sufficient final certificate is:

- a strictly richer twin, as above;
- the same root type, unique in the list, with the existing intrinsic
  normal/root key strictly smaller, checked exactly;
- all possible target classes having independently grounded exclusions
  in an explicitly acyclic proof dependency graph; or
- a separate exclusion of this pair without the unresolved twin shortcut.

For the second case, the twin is isometric to the same lattice and the
complete pair enumeration includes its normal pair up to the permitted
isometries, signs and interchange. The key is intrinsic under those
operations. Choose a minimum-key counterexample within the current class
to rule out an infinite descent. Completeness of the twin root set matters
for this key and for type recognition. A nonunique type cannot use this
same-class argument merely because its label agrees.

The involution is useful but does not by itself certify the stored
lattice-level dependency graph, which can branch among all classes of a
root type and invoke exclusions proved using other pairs. A correct
identification of a self-transfer is still a circular proof unless a
strict key descent or an independent proof supplies the missing argument.
Do not combine individually successful reruns by dropping their earlier
dependencies and then treating every final tracker label as an axiom.

## 3. The integer rank formula, with a direct proof

Let C consist of one representative of every sign class in an irreducible
simply-laced root system, with norm-two roots; put m=|C| and r=rank(C).
Define T = sum over beta in C of beta tensor beta on its span. T commutes
with every root reflection, since reflection permutes the root lines.
Thus every root is an eigenvector of the self-adjoint operator T.
Nonorthogonal roots have the same eigenvalue; connectedness then makes T
scalar. Taking its trace gives T=(2m/r)I.

For alpha in C, the diagonal term in (alpha,T alpha) is 4, and every other
nonzero term is 1. If n1 counts the other root lines having inner product
of absolute value one with alpha, then

    4 + n1 = 4m/r,     r = 4m/(n1+4).

Writing h=2m/r recovers n1=2h-4 and r=2m/h. Therefore LAB's formula is
correct, including A1 (n1=0). "Nonorthogonal lines" must exclude the line
of alpha itself; the sample's test `abs(P)==1` does so correctly.
The conventional relation |roots|=rh and the corresponding second-moment
identity are also given in Heckman's
[Coxeter Groups, Corollary 2.46 and Proposition 6.11](https://www.math.ru.nl/~heckman/CoxeterGroups.pdf).
The calculation above does not require looking up the Coxeter number.

ADE recognition from (r,m) is unique with the usual convention D_r for
r>=4, A_r for m=r(r+1)/2, D_r for m=r(r-1), and E6,E7,E8 for
(r,m)=(6,36),(7,63),(8,120). These numerical equalities alone do not prove
that an arbitrary list is a complete root system. Its completeness and
reflection closure must follow from the transfer theorem and source
shell completeness, or be verified separately. Checking n1 on every row
is a useful consistency check but does not replace that proof.

## 4. Make the arithmetic genuinely exact

The supplied sample still forms `rint(Rt @ G @ Rt.T)` from floating rows
containing divisions by 7. It removes the floating rank call but does not
independently certify this Gram matrix. Also v10 constructs some source
pairings using cached float64 matrix products. Without proved error bounds
or exact recomputation, "integers only" overstates this sample.

For each eligible source vector x, calculate a=x.G.y1, b=x.G.y2 exactly,
reduce c=2a+2b and d=-2a+2b modulo 7 into [-3,3], and retain the integer row

    Q = 7x + (c-a)y1 + (d-b)y2.

The twin Gram matrix is Q.G.Q^t / 49. Require exact divisibility, diagonal
2, no duplicate sign lines, and valid integer inner products. Compute the
canonical normal pairings as Q.G.ya / 7 with exact divisibility too.
Python integers work directly; int64 products need explicit bounds on
every product and partial sum, including the first intermediate product.

`q/codex_exact_twin_type.py` implements these operations and the rank
formula with those integer bounds and dtype checks. Its control run:

- agrees with the independently computed rational-rank classification on
  all 156 input root systems saved in `codex_exact_lattice_identity.json`;
- rejects six bad inputs: duplicate signs, wrong norm, float coordinates,
  nonintegral Gram, incomplete A2 and unsafe multiplication bound;
- passes an exact twin-row/normal-pairing construction control.

The saved report is `exact_twin_type_controls.json`. This verifies the
helper on the stated controls; **it has not checked historical twin
streams**. Root-system completeness remains an explicit caller hypothesis.

## 5. Cheapest useful replay and its acceptance contract

First recompute exact root counts. Increasing counts immediately discharge
both deferred verdicts and any status shortcuts having the same property,
without type classification or frame search. Then classify only residual
transfers and check exact same-class key descent when applicable. For the
remaining status shortcuts use independently proved target classes; search
only the ungrounded residue with the shortcut disabled. Cache identical
exact root configurations where useful, but retain pair/stream attachment.

To repair historical decisions by replay, preserve each input basis,
ordered stream digest/count, shell provenance, relevant engine version,
tracker snapshot and environment switches. Reproduce which branch the
historical program took, then certify that branch mathematically. Matching
only the total number of pairs, using the current v10 branch choices for
older versions, or matching an aggregate type histogram is insufficient.
Check exact canonical key comparisons in addition to the type. No frame
search is needed for this replay's purely algebraic part.

The 112/114 sample's 40,652 pairs are useful arithmetic controls, but the
supplied historical verdict tally has **no twin verdicts for either
lattice**. It therefore does not sample the actual historical twin exits
whose correctness is being repaired.

## 6. Counts and correction of the 713 report

Summing the supplied 102-lattice tally reproduces 592,864,217 pairs:
32,265,417 strictly richer deferrals, 1,300,094 status transfers and
2,863,005 canonical transfers. This is an independent sum of a supplied
tally, not a recount of all underlying streams.

Our pinned 713 checker was actually rerun: 386 jobs, two records per job,
2,419,830 pairs counted once. All duplicate job verdict counts also agree.
The exact split is **59,697 status transfers, 428 richer deferrals and
183 canonical transfers**, totaling 60,308. Thus message 107's attribution
of all 60,308 to the packaged status shortcut is too broad. The package
snapshot has 102 excluded lattices and SHA256
`488646967b9782536c2b203342ef26229947f8e5561b8fd74f7918482ed4f1ac`.
The original script checked named deferred types against the current lab
tracker, not every status shortcut's target. That limitation and the
inherited dependencies are now explicit in the report and JSON output.

## 7. Characteristic witnesses and the residual 28-lattice lot

The characteristic rule is valid: for z characteristic of norm 16,
the 42 odd word pairings give E(z)>=42. The two odd normal squares have
sum Y=2 modulo 8, so E=112-Y=6 modulo 8 and E>=46; hence Y<=66.
An exact positive certificate needs integral lattice coordinates z,
z.G.z=16, Gz=diag(G) modulo 2, and Y>66. No completeness of a shadow
enumeration is needed to verify an individual positive certificate.

LAB's reported 586+1,024 characteristic witnesses would leave
2,652-1,610=1,042 pairs outside the expanded short-witness route, namely
108+38+896. That arithmetic is correct. I have not independently replayed
all 1,610 witnesses here, so 1,042 remains a reported count. Save the z
certificates tied to the existing pair archives to make that claim exact.

The three supplied `notwin_106/111/131.jsonl` records were read. They
contain 32+320+4 pairs and only characteristic, empty-stage and swap exits;
no twin exits. This is bounded record evidence, not my own search replay.
For a residual-pair stream, every swap exit still needs the reverse pair's
coverage. An empty twin count alone does not certify that coverage.
