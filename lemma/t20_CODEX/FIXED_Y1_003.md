# The last 003 job has a fixed-y1 root obstruction

CDX, 2026-10-07. User-requested work on the costly job `003:181:182`.

**The entire job is excluded by R, T18 and T20, without enumerating a
single y2 or running the frame search.** This is a new coverage certificate
for a fixed first normal, not a claim that the unfinished stream completed.
Acceptance of the cited lemmas and identification of the input remain
explicit dependencies. It does not by itself certify every other 003 job
or all 156 lattices.

## Fixed-normal lemma

Suppose a frame satisfies Theorem R in `../upstream/AUDIT_REDUCTION.md`,
and that U contains a root r with `|(r,y1)|=2`. Put `b=(r,y2)`, an integer.
The normal plane's integral intersection is `J=Zy1+Zy2`, whose minimum is
7. Since r has norm 2, it is outside J. Therefore R-vi and R-vii give

    8 <= E(r) = 7*2 - (r,y1)^2 - (r,y2)^2 = 10-b^2,
    ||phi_r||^2 = 2 E(r),   A phi_r = -4 phi_r,

with phi_r a nonzero integer sigma-odd function. Thus b is -1, 0 or 1.
If b is +/-1 then E(r)=9, contrary to T18; if b=0 then E(r)=10,
contrary to T20. No such frame exists. For `|(r,y1)|>2`, R-vi alone
already gives a contradiction. No T16, swap, twin or exhaustive y2
enumeration is required for this lemma.

The statement is invariant under every lattice isometry and under the
sign of y1: carry r along with y1. Consequently one verified witness for
a representative excludes its entire first-normal orbit.

**Corollary.** With these dependencies, every root satisfies
`|(r,y1)|<=1` and `|(r,y2)|<=1`, hence their squared-height sum is at
most 2. Thus the certificate criterion can be applied before starting
the y2 producer, rather than rediscovered separately for each pair.

## Exact instance for 003:181:182

Input: package v10 `external_runs/structures_3eceb4d/U/003.json`.
Plan: `data/finishC/stream/003/plan.json`, 182 representatives, producer
basis hash `2de252651d1979f8`. Indices are zero-based. The producer uses
`reps1[k::n]`, so chunk 181/182 is exactly representative 181.

The coefficient vector stored in the plan is

    (-1,0,0,1,1,1,2,-2,-2,0,-2,1,2,1,0,1,1,0,-1,-1,0,-1,-1,1).

In the original ambient Euclidean coordinates it is

    y1 = (0,3/16,23/16,-3/16,-1/4,7/16,-1/2,-1/8,
          1/16,-9/16,0,5/16,-3/16,3/4,-3/16,-13/16,
          -1/2,5/8,-9/8,-7/16,-9/16,-1/4,-1/8,-3/8).

Take `r=-e_3+e_10` (one-based ambient indices). It is the first row of
the plan basis, so its basis coefficient vector is `(1,0,...,0)`. The
certificate verifies membership directly against the original generator
rows, rather than relying on this description alone. Exactly:

    (r,r)=2,   (y1,y1)=7,   (r,y1)=-23/16-9/16=-2.

This is the fixed-normal lemma's hypothesis. The same r also works for
representatives 158, 159, 162 and 176. Their witnesses are included, but
the bottleneck resolved here is specifically representative 181.

## Certificate and verification

`CERT_003_FIXED_Y1.json` contains the original lattice and plan inputs,
canonical SHA256 hashes, the plan basis, its integer change-of-basis
matrix from the original generators, and all five witnesses.

`verify_003_fixed_y1.py` uses the Python standard library and exact
`Fraction` arithmetic only. It verifies the integral unimodular
change of basis, exact equality of the two bases, integrality and
determinant one of the Gram matrix, the producer's basis hash, the
plan rows, membership, norms, root products, and the remaining E values.
It neither imports an enumeration engine nor trusts floating arithmetic
or completeness of a short-vector list. Passing `--lattice` and `--plan`
additionally compares the certificate with the intended external inputs:

    python lemma/t20_CODEX/verify_003_fixed_y1.py \
      --lattice <package>/external_runs/structures_3eceb4d/U/003.json \
      --plan <package>/data/finishC/stream/003/plan.json

The standalone verifier passed against the local v10 input and plan.
Two negative controls, corrupting the root coefficients and the ambient
y1 respectively, were both rejected. `check_003_y1.py` is the discovery
and certificate-generation script; its use of the existing short-vector
enumerator is unnecessary for verification of the resulting certificate.

LAB independently confirmed the root membership, all five norms/products,
and the mathematical argument in bridge message 63 (14:53 UTC). This
confirmation is separate from the standalone certificate check above.

## Integration and operational scope

Use a distinct **fixed-y1 theorem certificate** for this job, gated by
acceptance of R, T18 and T20, rather than fabricating a completed stream,
pair count or per-pair record. Verify its plan/input hashes against the
running campaign. Together with accepted coverage for the other 181
representatives, this supplies the remaining first-normal case; it does
not discharge unrelated H2/H4 or provenance conditions elsewhere.

No running process, queue event, cloud instance or historical record was
modified by this work. The runtime cause has not been directly observed.
The source of `q/par_consumer.py` reads the whole producer stream before
starting any shard; therefore elapsed time does not establish that a hard
pair has reached the frame DFS. LAB reported no residual y2 available at
14:49 UTC. The obstruction above removes the mathematical need to finish
that enumeration irrespective of which phase currently consumes the time.

### Integration confirmed later on 07/10

LAB commit `2d36a5b60` added its operational certificate generator/checker
and the importer/conversion support. CDX read those changes: coverage is
derived from the checked `reps` keys, indices are bounded and compared with
`covered`, and conversion rechecks the certificate and requires both lemmas.
The lab's resulting sweep record for 003 has **182 first-normal classes,
zero uncovered, zero incomplete**, with `[181]` covered by the fixed-y1
certificate and no invented pair count. Its `full` flag correctly remains
false pending the lemma/certificate/twin conversion requirements.

The updated `T20_BOARD.md` records LAP's independent check against the
package and that all production/diagnostic runs of this job were stopped
at 14:54 UTC. That operational confirmation comes from the coordinating
session; CDX did not operate those machines directly.
