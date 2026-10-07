# Checked campaign checkpoint: 156 recorded exclusions

CDX, 2026-10-07. Read-only check following bridge message 80, against master
`414e68d23`. This records the completed tracker conversion and final F4
comparison; it is not the promised referee pass on a future unified proof.

**Confirmed: the live lab tracker and the archived snapshot agree, and all
156 entries, with distinct IDs 000-155, are marked excluded.**

## Conversion and acceptance records

The backup `logs/finishC_tracker_before_convert_1007_1947.json` has 143
excluded entries. Exactly these 13 entries changed:

    001, 002, 003, 005, 006, 007, 008, 009, 011, 012, 013, 014, 015.

Only conversion-related fields changed (`status`, `by`, `reviewed_by`,
and possibly `status_note`); lattice identities and top-level metadata
were unchanged. The JSON snapshot is
`measures/finishC_tracker_2026-10-07_156.json`.

The live and archived T18/T20 acceptance records also agree. Their proof
blob IDs match the files at the recorded commit `3272aee0f`:

- T18: `6cbcf896a7ec76a5498943ac5cd9d9524a1ba13c`.
- T20: `e50d5be079a594101ed9078ed2a12596687dac95`.

This checks the stored acceptance record and its document references; it
does not independently attest to the quoted user exchange. Its written
scope and the G2/III.1 reservations are preserved. The acceptance JSON
files use Windows cp1252; the checker decodes them explicitly and records
that fact. Their contents were not changed.

## Archived F4 result for 064

Read `f4/064_compare.json` and the merged producer log at
`origin/run/q-i-011dce74cd612fc52`, pinned to commit
`a0ade8b74c5af101cc9b464dcef1594ecb55d517`:

| Recorded check | Result |
|---|---:|
| Canonical pairs in each enumeration | 1,050,528 |
| First-normal orbits in each enumeration | 1,856 |
| Pairs found only by either enumeration | 0 |
| Producer stream lines | 2,100,288 |
| Duplicate lines after canonicalisation | 1,049,760 |
| Complete producer chunks | 28 of 28 |
| Lines of norm seven | 22,892,544 |

All chunk indices 0-27 occur once, every chunk is marked complete, and
their pair counts sum to 2,100,288. The comparison marks the stream complete
and the two canonical sets equal. The raw count is **not** exactly twice
the canonical count; the relevant check is equality of the canonical sets
with zero differences, not a presumed factor of two.

The 140 control on that machine matches all non-timing fields of the
sequential reference at `origin/run/q-i-02aa613ee361fbc10`, commit
`8e4c29cf29166ebc7f41566ae636e7fa87aa072d`. The timestamp and elapsed time
are naturally different. The comparison program `q/f4_compare.py` was
also read; the hour-long comparison and pair enumerations were not rerun.

## Reproduction and scope

```text
python lemma/t20_CODEX/check_campaign_checkpoint.py <lab-root>
```

The checker reads the backup, live/archived tracker, acceptance records and
pinned Git run artifacts. It writes only
`lemma/t20_CODEX/campaign_checkpoint_156.json`, including canonical hashes
and the changed fields. No tracker, acceptance record, job or manifest is
modified by this review.

This is the milestone **156 recorded exclusions under the stated proof
dependencies and reservations**. The unified proof still needs its frozen
document/manifest and whole-text referee pass. G1's inferred historical
versions, the exact G2 checker contract, shared components in III.1,
historical lab runs and the stated limits of local catalogue checks remain
visible. No human referee pass or Lean formalisation is claimed here.
