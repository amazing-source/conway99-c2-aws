# Referee report on T16

Reviewer: CDX, 2026-10-07. Single errors-only pass requested in bridge
message 56. Reviewed the index at master
`9ad23660d9e7d6a3f525f26b094f900ed59ff698` and the received dossier in
`../t16/dossier_2026-10-04/`. The accompanying
`referee_t16_checks.json` pins the inspected primary texts, enumeration
sources, verifier and certificates, both as local bytes and with LF endings.

**No blocking mathematical error found in the T16 proof.** Two corrections
are listed below. The verifier omission does not invalidate any of the
supplied certificates: the missing condition was checked on all 32 records.

## Corrections

1. **The profile-B verifier omits membership of the Hall witness in the
   demand set.** In `VERIFIER_WAGNER_CERTIFICATS.py`, `check_B`, lines 96-101,
   `W` is checked for independence and for `|N(W)| < |W|`, but not for
   `W <= set(V)`. A vertex with zero demand is not an obligation that must
   be matched. Insert `assert W and W <= set(V)` immediately after forming
   `W`. If the verifier is also meant to enforce the advertised witness
   format, require three distinct entries in W and two partners.

   This is an executable contract defect, confirmed by a negative control:
   in the first archived B record, replacing W by the zero-demand singleton
   `[0]` and the partner list by `[]` is accepted by the received verifier.
   The supplementary membership check rejects it. **All 32 actual records
   have three distinct demand vertices and exactly two partners**, and their
   recomputed partner graphs pass the original checks. The B enumerator
   itself constructs W from combinations of V, so its construction already
   enforces membership. No shipped obstruction is lost.

2. **The index overstates an equivalence.** In `../T16_PROOF.md`, Statement,
   replace "Equivalently, with Theorem R" by "Consequently, with Theorem R"
   when passing to E(v) on the chosen U. The eigenfunction assertion is
   equivalent to `min N* >= 9/7`, using the integral eigenspace identification
   and A.5. It implies `E(v) >= 9` for v in U outside J. The reverse
   implication from the latter assertion for a fixed U is not supplied:
   its projection is `Nmax*`, possibly a proper sublattice of `N*`.
   The forward implication required by FD_MIN97 is unaffected.

## Scope of this pass and exact verification

The three primary proof texts were read in full, as were both
`ENUMERER_WAGNER_PROFIL_*.py` programs and the dense integer verifier.
In particular, no error was found in the k=2 active-inner-orbit exclusion
(equality note, section 5), or the classification into cube and Wagner
(cube note, section 8). The latter uses the induced graph on the four
remaining vertices, which must be K1,3 or P4; it does not assume a catalogue
of cubic graphs. The cube double count and the two global Wagner profiles
also pass this review.

The Wagner coverage review included the 105 matchings and every eligible
marked orbit; the partial-matching rectangle condition; canonical row
orientations and the justification for distinct equal-weight row orbits;
all three-edge-orbit choices for G; the invariant exceptional pair in A;
and the necessary relaxations used by the B matching obstruction and the
A four-clique obstruction. No coverage error was found in these sources.
Their deadlines raise exceptions, rather than returning an exclusion.

`referee_t16_checks.py` reran the received dense integer verifier's check
functions without rewriting the dossier, and added the missing B condition.
The run checked all **240 A obstructions, 6,544 candidate orbits and 32 B
obstructions**, including reconstruction of the allowed/compatibility graphs
and absence of a four-clique. It took approximately 5.4 seconds. The int16
matrix products in this pass have sums below 100, so there is no overflow.
The negative control above also ran and behaved as stated.

The coverage enumerators were reviewed as source but **not rerun in this
pass**. Their archived results and the separate lab cross-check outputs
remain the computational coverage evidence; this report does not claim a
third independent enumeration or a full audit of the separate cross-check
implementation. Neither the received dossier nor any engine was modified.

**H5 disposition:** T16 is now a separately reviewed dependency, with no
remaining mathematical objection identified in this pass. Together with
R-vii, it justifies the norm-three Y=13 / FD_MIN97 rule. This conclusion
does not close H1-H4, prove T20, or certify all 156 lattice exclusions.
