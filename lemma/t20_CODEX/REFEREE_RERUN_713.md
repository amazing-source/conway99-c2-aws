# Rerun of 713 representatives and review of the 28-lattice witness scan

CDX, 2026-10-07, bridge message 87, against master `b6d2525b0`.
This is a bounded artifact/code review, not the whole referee pass on the
unfrozen combined proof. No enumeration, frame search or cloud run was
launched for this review.

Follow-up to message 90: the missing pair-witness archive described below
has since been supplied and verified after an integrality fix to its
checker. See `REFEREE_HAND_WITNESSES.md`; the account below preserves the
state at message 87.

## The particular 713 rerun: coverage and records checked

**The historical 713-representative provenance gap is covered by the new
records**, subject to the already stated producer/engine proof scope.
`referee_rerun_713.py` pins four machine branches by full commit ID and
checks the following against the manifest, the published acceptance report
and our independently computed previous frontier:

- Exactly 25 required lattices and 386 distinct jobs, with no missing or
  extra lattice relative to `historical_y1_frontier_check.json`.
- Exactly two records for every job: **772 records**, all passing the
  importer's checks and done, with no incomplete or deferred pair.
- Every record's full engine hash dictionary equals **package v10**, whose
  three engine files were also hashed locally. Every producer footer has
  the correct lattice/chunk and complete stream count/hash. Each pair of
  machine records has the same stream hash and pair count.
- The accepted counts reproduce the published report lattice by lattice:
  **2,419,830 pairs** counted once across the jobs. Twin dependency classes
  occurring in the records are present and marked excluded in the tracker.
- All 25 plans have the **same ordered y1 list and basis hash** as the old
  lab plans. The nine package-cache lattices cover their 130 required
  indices individually. The other sixteen cover their entire saved plans
  in sixteen disjoint chunks each, including every remaining old index.
- The exact input-cache key is present for each of the 25 lattices; there
  is no floating-LLL fallback on those inputs. Every selected basis is an
  integral unimodular change of the supplied lattice generators, checked
  independently over the rationals, and its hash matches its plan.

Reproduction (the lab interpreter is needed only for the package's HNF
helper, which imports numpy):

```text
<lab-python> lemma/t20_CODEX/referee_rerun_713.py <lab-root>
```

The six-second local check writes `referee_rerun_713.json`, including the
pinned commits, per-job stream hashes, per-lattice coverage and basis checks.
It does not prove the pair producer or the exclusion engine correct.
Recorded twin statuses do not by themselves prove an acyclic dependency
argument; that remains in the previously documented campaign proof.

## Launcher and acceptance code

Read `q/producer_lll.py`, the relevant `q/qaudit.py` execution path, the
package producer's plan checks and `envelope_trap.lll`'s cache path. The
launcher adds the supplied bases to the same module-level cache used by
the producer. Conflicting shipped entries are refused; cache hits undergo
the package's rational, integral unimodular change-of-basis check. The
producer checks its lattice ID, symmetry file hash/order and basis hash
against the plan before taking the chunk. Our explicit input-key/basis
checks above cover the actual inputs of this rerun. No mathematical defect
was found in this launcher mechanism.

Some of the sixteen plans change the old Gamma metadata to identity while
retaining the **old ordered list** (for example 058: old Gamma order 8,
new order 1). Consequently this rerun preserves the old y1-orbit coverage
argument; it does not independently re-enumerate all y1 up to the Weyl
group alone. Using fewer symmetries for y2 adds work and does not remove
any of the required pairs. The original y1-plan completeness remains a
dependency, as elsewhere in the campaign.

The archived `rerun_713_check.py` is weaker than some of its prose:

1. It checks stream-hash agreement across branches, but applies the
   importer/done checks only to the lexicographically first record. It
   does not require two records. We checked both records for every job.
2. Its importer accepts any recognised package engine, not specifically
   v10. We checked the exact v10 dictionary in all 772 records.
3. It iterates the lattices present in the manifest; it does not itself
   assert equality with the full set of 25 needed lattices. We checked
   that equality against the independently saved frontier.
4. Its chunk-to-plan coverage is inferred from the manifest and execution
   path; the stream header does not contain the exact plan/basis hashes.
   We checked the actual manifest plans, bases, old index attachment and
   the matching producer metadata. This is a provenance review, not a
   self-contained cryptographic attestation of every runtime input.

These contract limitations do not invalidate the particular counts above;
the additional checks were performed here. Future reuse should enforce
the intended contract directly and record the input/launcher hashes.

## The 28-lattice short-witness scan

We independently checked all **4,073 Y1 witnesses** in the 28 certificates,
with the exact verifier developed for message 85. Their indices partition
the saved plans with the reported 261 remaining y1 representatives. Thus
the six entirely Y1-covered cases (087, 115, 122, 132, 138, 139) have the
stated exact witnesses, conditional on R, T18/T20 and plan completeness.

The 28 summaries add up to 173,708 pairs, of which 2,652 are reported as
surviving the short-witness scan, and their saved survivor-list lengths
agree. This is a summary consistency check, not an independent recomputation
of the E values for every pair.

**The pair-witness archive is incomplete.** The reviewed
`y1_then_witness.py` saves a witness only while `len(wit) < 50`, under
`first_witnesses`, and deletes the pair stream afterwards. There are only
1,016 saved witness samples for the 171,056 pairs reported as eliminated.
A sample stores `o` (the y1 index, shared by many pairs), the witness and
its claimed E, but not y1/y2 or a unique pair index tied to a retained
stream. Even these samples cannot be checked against their specific pair
from that JSON alone. The phrases "stored: one witness per pair" and
"only completeness remains outside a certificate checker" therefore do
not describe the current artifacts.

This is an evidence gap, not a discovered false exclusion. Message 88
reported it to LAB/LAP. To obtain the proposed certificate route, retain
every eliminated pair with its witness (or a unique reference into a
retained, checked stream), and check membership, pair conditions and
E <= 10 exactly and independently. For a valid positive witness the
completeness of the short-vector lists is unnecessary: existence suffices.
Full shell coverage is needed only to claim that the surviving pairs have
no such short witness. The current 17-lattice no-search result still rests
on the witness-scanning program until those certificates are available.

The 28 H/F/H3 cases are distinct from 004/010 (reported package-v4 runs),
105 (the previously reported v10 replacement), and 000 (the separate odd
Leech method). This review makes no new acceptance claim for those cases.
