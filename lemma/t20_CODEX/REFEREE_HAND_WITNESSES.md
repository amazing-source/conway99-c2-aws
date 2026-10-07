# Full short-witness certificates: checked after an integrality fix

CDX, 2026-10-07, follow-up to bridge message 90, against master `13514d769`.

**All 171,056 positive pair witnesses pass the corrected exact checker.**
The 22 NPZ files contain 173,708 pairs in total, including 2,652 marked
survivors. Their coordinates reconstruct exactly the 22 reported producer
stream SHA-256 values. The earlier missing-witness archive issue is closed
for these artifacts. All 4,073 fixed-y1 witnesses in the 28-lattice lot
were also rechecked against their plans and lattice generators.

## A real checker defect, with a concrete negative control

The first `check_hand_witness.py` loaded `y2` and `w` with `tolist()` but
did not require integer array types. A floating-point array could therefore
claim a rational vector outside U while passing the norm and E identities.
The separate conversions `int(x)` on some other arrays could also silently
truncate nonintegral input instead of rejecting it.

This was reproduced on lattice 141, pair row 1 (zero based). In coordinates
of its certified lattice basis B, put z = e_2 - e_5 (one-based basis indices).
For that row, z^2 = 4, (z,y1) = (z,y2) = 0 and (z,w) = 1. The rational
reflection

    w' = w - z/2

preserves w^2 = 3 and E(w) = 8, but gives coordinates -1/2 and 7/2 in
positions 2 and 5. Since B is a Z-basis, w' is not in U. Storing this
modified witness in a float64 array and updating the NPZ digest made the
original checker report all 52 pairs valid and exit zero. This is a
certificate-verifier defect, not a counterexample to the actual exclusion:
the original integral witness is valid.

The fix in `q/tools/lab_2026-10-07/check_hand_witness.py` now rejects
noninteger array dtypes before conversion, checks all matrix/array shapes
and lengths, and checks index ranges, uniqueness and reference integrity.
The arithmetic then genuinely takes place in Python integers and fractions.
Negative controls reject the nonlattice reflection, an altered integer
witness, a malformed matrix and an invalid y1 reference. The regression
also replays the acceptance of the nonlattice witness by the pinned old
checker, making the defect and its correction reproducible.

## Full verification and attachment to the pair streams

```text
<lab-python> lemma/t20_CODEX/referee_hand_witness.py <lab-root>
```

The local run took 25 seconds, without enumeration or frame search. It:

- rechecks the exact Y1 certificates and their complements in the plans;
- runs the corrected rational/integer checker on all 22 pair archives;
- reconstructs every pair's ambient coordinates and the producer's exact
  JSON line encoding, then matches the saved stream digest;
- records the input digests, results and four negative controls in
  `referee_hand_witness.json`.

Stream reconstruction uses int64 matrix multiplication only after an
explicit Python-integer bound on every product and partial sum; witness
validity itself is checked with arbitrary-precision Python arithmetic.
The array archive therefore gives both an exact witness for each eliminated
pair and the same ordered pair stream that the producer reported.

## Remaining scope

Each positive witness excludes its pair under R and, for E = 8, 9 or 10,
T16, T18 or T20 respectively. **No completeness assumption on the short
shell lists is needed for those positive certificates.** The completeness
of the y1 plans and pair producer remains necessary for the lattice-level
conclusion; matching a stream digest does not prove that enumeration theorem.
We did not recheck the claimed minimum E >= 11 for survivors.

Thus the 17 lattices with no surviving pair now have the reported complete
witness route, conditional on those stated mathematical and enumeration
dependencies. The 2,652 surviving pairs require a further exclusion argument.
LAB's separate v10 acceptance report currently records 27 of 28 old
lattices completed, with 044 still absent; this review does not certify
that separate rerun or treat 044 as finished. The combined proof has not
yet received its whole-text referee pass.
