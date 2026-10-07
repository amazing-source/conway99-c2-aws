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
scope and the G2/III.1 reservations are preserved. At this checkpoint the
acceptance JSON files used Windows cp1252; the checker decoded them
explicitly and recorded that fact. LAB subsequently rewrote both as ASCII
JSON (message 83). Their parsed contents and canonical SHA-256 are unchanged:
`41ce373abcaba774b916ef089c241b0f8c7a8b6161e2e153047728259ba7cd1d`.

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

## Historical provenance addendum (message 83)

The new `measures/STREAM_RECOUNT_2026-10-07.json`, archived on master
`c1814f6a4`, sharpens the historical-program reservation. Its 91 stream
lattices report complete first-normal coverage, no overlap and no other
importer fault **after relaxing the packaged-engine-version requirement**.
The total is 220,260,576 pairs, replacing the earlier unreproduced total
212,825,691. We checked the new report's per-lattice arithmetic and totals:

| Recorded engine provenance | Pairs | Lattices affected |
|---|---:|---:|
| P: engine hashes match a lab package | 212,804,047 | 36 have entirely P coverage |
| L: code hash recorded, unmatched to a package | 4,409,816 | 39 have some L coverage |
| N: no code version recorded | 3,046,713 | 26 have some N coverage |

The union of L and N comprises **55 lattices and 7,456,529 pairs** (ten
lattices have both). A reported L hash identifies an unavailable historical
version; it does not restore its source. P identifies a packaged engine;
that alone does not prove the engine or its enumeration correct.

The four displayed verdict totals (97,628,147 at once, 22,702,398 search,
6,107,330 twin, 93,822,540 swap) omit **161 originally INCOMPLETE pairs**.
These are separately recorded as resolved. We compared the exact pairs
in the original `not_excluded` lists with the local resolution files for
018, 023, 024, 026, 028, 037, 049, 052 and 080: the sets match and account
for all 161. The resolution file for 037 repeats one identical pair and
verdict, giving 31 lines for 30 distinct pairs. All final verdicts are
`EXCLUDED (stage 1 empty: no 7 h)` or `EXCLUDED (no local star sums)`.
This validates the record links, not the searches producing those verdicts.

Reproduce this bounded audit with:

```text
python lemma/t20_CODEX/check_stream_provenance_report.py <lab-root>
```

Its output `stream_provenance_report_check.json` pins the report and the
nine source/resolution file pairs by SHA-256. It does not replay the
recount's record selection or the long enumerations. The 29 older pair-list
lattices plus 000, 004 and 010 are outside this 91-lattice recount, as are
the 13 newly converted entries and the 20 lattice-level exclusions.
In particular, **003 is not in this historical lot**; its fixed-first-normal
certificate and the previously documented T18/T20 dependencies stand as
before. The number 156 still denotes recorded exclusions, with these
provenance gaps explicitly open. The combined proof is not yet frozen.
