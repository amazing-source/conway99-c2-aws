# PROOF_C2: the single proof document (opened 2026-10-07)

Statement: **a strongly regular graph with parameters (99, 14, 1, 2) has no automorphism of order 2.**

| File | Content | Owner | State |
|---|---|---|---|
| `MAIN.md` | the statement, the chain of the proof in order, what it rests on | LAP + LAB | first assembly 07/10; reservations of the final statement to merge at the freeze |
| `A1_REDUCTION.md` | Theorem R, (R-i) to (R-vii), proofs A.0 to A.9 | LAP | refereed text in place; prose to polish |
| `A2_BRIDGE.md` | the energy, the witness rules for E <= 10 and their completeness, Corollary Y1 | LAP | assembled 07/10; prose to polish |
| `A3_LEMMAS.md` | statements of T16, T18, T20, what each rests on, pointers to `T16_PROOF.md`, `T18_PROOF.md`, `T20_PROOF.md` | LAP | assembled 07/10; prose to polish |
| `B_LATTICES.md`, `B_TABLE_156.md` + generator | the 156 lattices: what excludes each, records, certificates, audits; "what it rests on" | LAB | started |
| `MANIFEST` | sha256 of every file cited, frozen for the referee pass | LAP + LAB | at the end |

Rule: (R-i) to (R-vii) are stated once, in A1, and cited by number everywhere else. One complete referee pass (CDX) on the frozen
merged text. Nothing computed is cited without its two programs and its file (`lemma/ARTIFACTS_T18_T20.md` for the lemmas).
