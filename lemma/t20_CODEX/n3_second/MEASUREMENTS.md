# Route A measurements, 2026-10-07

**No base in this pilot was completely excluded. No cloud launch is
recommended from these measurements.** Each run used one Python process;
the first prototype capped numerical library threads at one. The current
integer program does not use a numerical library.

## Five initial 60-second measurements

This prototype tested the full projector blocks with certified integer
negative forms suggested by numerical eigenvectors. Every run timed out.
These are historical performance observations, not proof artifacts.

| base ID | graph / case / profile | seconds | nodes at levels 0 through deepest | complete configurations found |
|---|---|---:|---|---:|
| 4240840c3e42edcaf335 | I.0 / i / 340 | 60.000 | 1,1,4,75,400,931,951,170,8 | 0 |
| 9e877d606a5dd1331da0 | I.0 / i / 421 | 60.016 | 1,2,16,247,904,930,1210,148,16,2 | 0 |
| 986ecf936eb50f5d36a6 | I.0 / ii / 340 | 60.000 | 1,1,13,59,543,1207,950,291,44 | 0 |
| 2b1c382e5907bc156c60 | I.0 / ii / 421 | 60.000 | 1,9,80,673,1844,1970,776,56 | 0 |
| bdcd62329f888fde34ee | I.0 / iii / 340 | 60.000 | 1,1,9,180,759,928,1128,514,38 | 0 |

Five different (case,profile) kinds were selected deterministically. This is
not a random sample of 533 classes, and the unmeasured (iii,421) kind remains
unmeasured. Zero found before timeout does not imply zero in the full tree.

## Exact Schur and full fail-first version

Code: commit `7880a1ff3`; source digest
`c56bfda4853d15159aa78548e5bdfc024b0a63e014035e15a84b36d622042b07`.

Base `4240840c3e42edcaf335` (I.0 / i / 340):

- timeout at 300.000 seconds;
- catalog: 1570 candidates in 0.500 seconds;
- nodes per level 0..12:
  `[1,2,59,1050,4366,9119,6657,736,4,0,0,0,0]`;
- 507479 cached candidate-pair tests;
- zero complete configurations found, **search incomplete**.

The run was stopped before finishing the other four 300-second measurements.
An additional propagation experiment was stopped when the coordination
message arrived, without a completed result; it is not part of this commit's
search or any claimed exclusion.

## Decision

The first program's author compared the corresponding I.0/i/340 tree in
bridge messages 41 and 43 and reported the same expensive structure, with
an estimated several CPU-hours for that individual base. The earlier
3.7-minute average for the first program was based only on completed bases
and was explicitly withdrawn by its author. It must not be used for cost.

The unfinished pilot cannot provide a reliable mean cost over all classes.
It does establish that a 60-second timeout and depth eight are consistent
with both independent implementations, and that automatic deployment of
this route is unwarranted. Route-A performance work is on hold pending the
shared route decision at 12:45 UTC. The fixed-base Schur checker, bitset
budgets, coverage manifest and resumable runner are available for the
alternative decomposition including N(p).
