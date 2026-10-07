# Independent second program for T20, n3=2

Author: Codex, 2026-10-07. **No completed exclusion is claimed yet.**
Pilot results and the current hold are recorded in `MEASUREMENTS.md`.
The program was written from `../../t20_HAND/SPEC_N3.md` and the mathematical
notes. The first program's `eng5.py`, `eng5z.py`, `n3_cases.py`, and `run_n3.py`
were neither read nor imported. No SAT, CP, ILP, or LP solver is used.

## Base coverage

`model.py` reconstructs all six graphs from their edge lists and enumerates
their automorphisms directly. It generates all pairs of three-element
support neighbourhoods, then quotients by those automorphisms and exchanging
the two neighbourhoods. The 29-vertex bases are generated from all three H1
cases, all allowed choices of the inner X0 orbit, and all 64 inter-orbit edge
patterns. Budgets, G0 degrees, and four exact projector blocks filter them.
The remaining relabellings of the three X0 pairs are enumerated explicitly.

The independently obtained counts match every entry of the specification:

| B | types | labelled | budget + degrees | PSD | classes | hand excluded | searched |
|---|---:|---:|---:|---:|---:|---:|---:|
| I.0 | 1 | 640 | 186 | 136 | 44 | 11 | 33 |
| I.1 | 9 | 4608 | 1356 | 712 | 227 | 55 | 172 |
| I.2 | 3 | 1536 | 452 | 262 | 87 | 21 | 66 |
| I.3 | 4 | 2176 | 638 | 365 | 121 | 28 | 93 |
| I.4 | 5 | 2432 | 718 | 439 | 146 | 34 | 112 |
| I.5 | 3 | 1536 | 452 | 225 | 75 | 18 | 57 |
| total | 25 | 12928 | 3802 | 2139 | 700 | 167 | 533 |

The hand exclusions use `../PROFILE_421.md` and `../TRIANGLE_REDUCTION.md`.
The attachment lemma removes no additional base beyond PSD and isolation
in these counts. Base generation takes about 4.2 seconds on the local CPU.

## Search and exhaustiveness

For each base the program enumerates all possible data of one X2 orbit:
two distinct support pairs, inner/word status, its adjacency to z or z', and
its subset of the six X0 words/inner vertices. The smaller support-pair
index fixes its orientation; every orbit has exactly such an orientation.
Its required number of neighbours in other X2 orbits is |W|-2a3.

A state consists of k complete orbit data, their induced graph, the remaining
unit multiplicities and base incidences, and the current X2 degrees. For an
unfilled unit, every matching catalog entry and every direct/cross adjacency
pattern to the placed orbits is considered. Pair tests are cached, but the
full state is checked before an extension survives. The next unit is chosen
with the fewest surviving full extensions. Stopping a count when it reaches
the best known count only discards that unit as a *choice*, not an extension.

Any genuine completion supplies a candidate for whichever unfilled unit is
chosen and supplies one of its edge patterns. Every rejection is a necessary
condition: an integer degree or common-neighbour budget, an exact target
upper bound, a capacity bound of two neighbours per remaining orbit, or PSD.
Thus a genuine completion follows some branch to twelve orbits. At that
point all specified target equalities are required and full-matrix exact
PSD is rechecked. No rank bound or additional unproved lemma is used.

Repeated placement orders can cause redundant branches; they do not remove
any configuration. Completeness does not depend on the unit-choice heuristic.

## Exact arithmetic

All mathematical tests use Python integers or `fractions.Fraction`.
`model.exact_psd` uses Schur elimination, multiplying by a positive pivot,
then dividing by a common positive gcd. A zero pivot requires a zero row.
This handles singular matrices exactly.

`schur.py` selects a positive definite principal block K of each fixed base
projector. It calculates H=D K^-1 with positive integer D and integer H.
Every omitted base coordinate's range condition is checked for every new
column. The residual matrix is D C - B^T H B. Its PSD is equivalent to full
PSD after these range checks. Hence at most 12-by-12 integer matrices need
elimination inside the search. No floating-point spectral rejection remains
in this version. Floating point is used only for elapsed time.

## Checks and running

`validate.py` compares optimized budgets with direct bitset budgets on 2620
extensions, the parity blocks with direct full-matrix congruences in 46
cases, full exact PSD with the blocks in 46 cases, and the fixed-base Schur
reductions with full exact PSD in 363 cases. These small checks pass; they
do not replace an exhaustive run. The optional validation script uses NumPy
as a direct matrix-arithmetic oracle. The actual enumeration is standard
library only.

```
python bases.py --output bases.json
python validate.py
python run.py --output pilot --pilot 5 --seconds 300 --workers 1
python run.py --output results --workers NUMBER_OF_PROCESSES
```

Each base receives one atomically written JSON result. Only a completed
result from the identical source digest is resumed. Timeouts remain explicit
and are retried, never treated as exclusions. The summary lists all covered
base IDs and sets `exclusion_verified` only for full coverage, no timeout,
and zero complete configurations. The 167 hand exclusions are included as
separate, labelled results in the same coverage count.

Before a cloud run, five single-core measurements must finish and be reviewed
for cost. This directory itself neither starts nor changes any cloud job.
