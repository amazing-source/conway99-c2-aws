# T20 round 3, case I (k = 0), n_3 = 0: report

Agent report of 07/10, saved by the main session. Notation of rounds 1 and 2 (`lemma/t20/T20_REPORT.md`, `lemma/t20_R2/REPORT.md`).
Scripts: this folder. Outputs of the cloud runs: branches `lemma-run/t20_I_rest-...`, `lemma-run/t20_Iv_...`, `lemma-run/t20_I1_340-...`.

**Outcome.** For n_3 = 0, all twelve cases (six graphs x two profiles) are excluded by exhaustive exact computation: 615,405
bases, 15,762,181 search nodes, 0 complete configurations. No profile or graph is removed by hand. n_3 = 2 is the lab session's
branch (`lemma/t20_HAND/`). T18, the 04/10 lemma and the dual-norm test are not used anywhere; the rank bound is used at 15 nodes
of I.1 by the first program only.

## 1. Table

| Graph | Profile | n_3 = 0 | Programs (state at the time of the report) |
|---|---|---|---|
| I.0 | (4,2,1) | excluded, computed (laptop) | **two, both complete** |
| I.0 | (3,4,0) | excluded, computed (laptop) | first complete; second: stage 1 identical, stage 2 on 372 of 11,150 bases |
| I.5 | (4,2,1) | excluded, computed (laptop) | **two, both complete** |
| I.5 | (3,4,0) | excluded, computed (cloud) | first only |
| I.2, I.3, I.4 | both | excluded, computed (cloud) | first only |
| I.1 | (4,2,1) | excluded, computed (cloud); 2 nodes by the rank bound | first only; second tested on the base holding those 2 nodes: closes both without rank |
| I.1 | (3,4,0) | excluded, computed (cloud); 13 nodes by the rank bound | first only |
| all | (5,0,2) | excluded by hand (round 2, I.3) | - |

The second program is being run on all twelve cases (jobs `t20_Iv_B..F` and `t20_I1_340`).

Counts per case (recomputed from the stage-1 files and the jsonl parts, `final_table.out`; level = number of X_2 orbits placed):

| Case | N-configurations | Orbits under Aut(B) | Bases kept | Stage-2 nodes | Deepest level | Complete | Rank |
|---|---|---|---|---|---|---|---|
| I.0 (4,2,1) | 178,768 | 11,322 | 3,022 | 33,511 | 4 | 0 | 0 |
| I.0 (3,4,0) | 1,229,304 | 77,391 | 11,150 | 250,504 | 5 | 0 | 0 |
| I.1 (4,2,1) | 722,524 | 180,920 | 56,300 | 1,406,917 | 5 | 0 | 2 |
| I.1 (3,4,0) | 3,508,550 | 878,137 | 219,589 | 7,279,961 | 5 | 0 | 13 |
| I.2 (4,2,1) | 412,875 | 41,441 | 13,925 | 421,773 | 5 | 0 | 0 |
| I.2 (3,4,0) | 2,301,905 | 230,609 | 55,573 | 2,053,687 | 5 | 0 | 0 |
| I.3 (4,2,1) | 506,294 | 126,655 | 32,022 | 427,984 | 5 | 0 | 0 |
| I.3 (3,4,0) | 2,663,180 | 666,032 | 112,368 | 2,055,948 | 5 | 0 | 0 |
| I.4 (4,2,1) | 495,024 | 124,367 | 21,561 | 237,408 | 5 | 0 | 0 |
| I.4 (3,4,0) | 2,606,408 | 653,570 | 76,509 | 1,200,322 | 5 | 0 | 0 |
| I.5 (4,2,1) | 435,540 | 22,111 | 2,710 | 27,524 | 4 | 0 | 0 |
| I.5 (3,4,0) | 2,335,670 | 117,846 | 10,676 | 366,642 | 5 | 0 | 0 |

Totals: 17,396,042 N-configurations, 3,130,401 orbits.

## 2. Hand part (n_3 = 0)

Used from earlier rounds: (M) and the facts on words (round 1 A0), n_4 = 0 (A6), G0 and G1 (round 2), (5,0,2) impossible (round 2
I.3). Here X_3 is empty, so (n_0, n_1, n_2) = (9, 40, 30).

**C1. Classes.** G0 with a_3 = 0 gives: X_0: a_0 = a_2 - 6, a_1 = 20 - 2 a_2. X_1: a_0 = a_2 - 3, a_1 = 15 - 2 a_2.
X_2: a_0 = a_2, a_1 = 10 - 2 a_2. A vertex x of S+ has 4 neighbours in S, 6 in X_2, 4 in X_1, none in X_0 (the 9 other vertices
of S+ are non-adjacent to x, so 18 = 4 * 3 + sum over the 10 outside neighbours of (d - 1)).

**C2. Units.** x_i and x_j have 2 - codeg_B(i,j) = m_ij common neighbours outside S; they lie in X_2. So s -> U(s) = {i : s ~ x_i}
maps X_2 onto the deficient pairs, each taken m_ij times (30 in all). With V(s) = {l : s ~ y_l}: U(sigma s) = V(s), U(s) != V(s).
x_i and y_l have exactly 2 - B_il common neighbours outside S; hence for s in X_2 each i in U has at most one B-neighbour in V, and
conversely.

**C3. Slots (new).** Let w, w' be vertices of N(p) in two different mate pairs. They are non-adjacent, so they have exactly two
common neighbours: p, and a second one [w,w'], which is not in N(p), hence a word. Conversely a word has exactly two neighbours in
N(p), in two different pairs. So [.,.] is a bijection from the 84 slots onto the 84 words, with sigma[w,w'] = [sigma w, sigma w'].
Each cell {c,c'} of two pairs carries exactly two word orbits. The 12 word-neighbours of w are the words [w,u], u outside the pair
of w.

**C4. N(p).** Let w be in N(p) with d(w) = delta. delta <= 2. delta = 2: type (U;V) with U, V disjoint. delta = 1: type (i;k) with
i != k. Every index lies in exactly two of the sets U u V, {i,k}. So h_2 = 3 + h_0, h_1 = 4 - 2 h_0; (3,4,0) and (4,2,1) remain.
Let Q = X_0 minus N[p]: 8 - 2 h_0 words in 4 - h_0 orbits. s(w) = |N(w) n Q| <= 4 - h_0. G0 at w splits the 12 word-neighbours:

| Kind of pair | In S | In Q | In X_2' = X_2 minus N(p) | In X_1' = X_1 minus N(p) | Bound on s |
|---|---|---|---|---|---|
| A (delta = 2) | 4 | s | s | 8 - 2s | 4 - h_0 |
| W (delta = 1) | 2 | s | 4 + s | 6 - 2s | 3 |
| Z (delta = 0) | 0 | s | 8 + s | 4 - 2s | 2 |

The sum of s over the seven pairs is 8 - 2 h_0.

**C5. Words of X_2.** s in X_2' has exactly two neighbours in N(p), in different pairs, and a_2(s) = a_0(s) <= 5
(T = N(s) n X_0 avoids p, T n sigma T lies in N(s) n N(sigma s), so 2|T| - 2 <= 8).

**C6. Profile (4,2,1): where the X_2 words sit (new).** n_XY = number of X_2' orbits in cells of kind XY, c = number of support
orbits in the WW cell (c <= 1), s_W = s_W1 + s_W2. Counting the 11 orbits through each kind of pair: n_AZ + n_WZ = 8 + s_Z;
n_AW + 2 n_WW + n_WZ = 8 + s_W; 2 n_AA + n_AW + n_AZ = 6 - s_Z - s_W; n_WW <= 2 - c; n_WZ <= 4. Hence
2 n_AA + n_AW = n_WZ - 2 - 2 s_Z - s_W and n_WW - n_AA = 5 + s_W + s_Z - n_WZ, so n_WZ >= 3 + s_Z + s_W and **s_Z + s_W <= 1**.
All solutions (`hand_cells.py`), written (AA, AW, WW, WZ, AZ): s_Z = s_W = 0: (0,1,2,3,5); (0,2,1,4,4) with c = 0 or 1; (1,0,2,4,4).
s_W = 1: (0,1,2,4,4). s_Z = 1: (0,0,2,4,5). (The Codex lemma `lemma/t20_CODEX/PROFILE_421.md` proves s_Z = 0.)

**C7. Profile (3,4,0).** With sigma_A the sum of s over the three A pairs (0 to 8): n_AW = sigma_A - 2 n_AA,
n_WW = 12 - sigma_A + n_AA >= 4, n_AA + c <= sigma_A.

**C8. Identity (Q0) of H4.** Re-derived: e(X_0) = e(X_2) - 27, and the sum equals 44. As bounds on single degrees it is weaker than
C4 and C5; its global form needs a nearly complete X_2, and the searches stop at 5 orbits of 11 or 12. Not used by the programs.

**C9. Rank bound** (statement of T18_PROOF 6.4; it does not use theorem T18): the odd and even M1 blocks of a sigma-invariant set
have rank at most 22.

**Tried, closes nothing.** A^2 on the indicators of X_0, X_1, X_2 at p and at a Z vertex: identities only. Matchings in N(z_0) and
N(w): compatible with every solution of C6. C6 as a filter on bases: rejects 20 of the first 300 bases of I.0 (4,2,1). The
dual-norm test on S u N(p): no certificate on 61 + 61 sampled bases of I.0, smallest N > 0 is 10.

## 3. Computations

**Determined sets.** Base S u N[p] (35 vertices): S with S: B; p with S: none; p with N(p): all; N(p) with N(p): the seven mate
edges; N(p) with S: the types (parameter). Node = base plus t orbits of X_2': with S: (U;V), parameter; with p and with the mate:
none (words); with N(p): exactly two vertices in different pairs (parameter, C5); between orbits: one of four patterns (parameter).

**Stage 1 (`stage1c.py`).** An N-configuration is a set of typed pairs with coverage exactly two and pairwise "two vertices of
different pairs share at most one neighbour in S". Each is generated once; one representative per Aut(B)-orbit is kept; the orbit
sizes add up to the total (asserted). Each representative is rejected by an exact budget count or an integer PSD vector, or kept.

**Stage 2 (`eng6.py` = round-2 `eng5.py` plus lazy certificates, model `cases6.py`).** A unit not yet realised is chosen; some
unplaced vertex of X_2' realises it; all its data are enumerated (V, the two neighbours in N(p), the pattern to every earlier
orbit) under the caps of C4 and C5; each candidate is rejected exactly (budget count in int64, integer vector in Python integers,
or exact rank) or kept by a float decision.

**Completeness.** Laptop: `summary2.py` reports "COMPLETE: True" for I.0 (4,2,1), I.0 (3,4,0), I.5 (4,2,1). Cloud run t20_I_rest:
re-counted from the branch files (`check_cloud.py`, not from ALL.txt): all nine cases: 128 of 128 parts, every base index once and
in its part, no time-out, no error, sha1 of the base list recomputed and equal in every part, 0 complete.

**Second program (`in_verify.py`, no shared code, own enumeration and tests).** Stage 1: identical numbers and identical lists for
I.0 (4,2,1), I.0 (3,4,0), I.5 (4,2,1). Stage 2, full re-traversal, same kept count at every node: I.0 (4,2,1): 3,022 bases, 33,511
nodes, 1,144,830 certificates; I.5 (4,2,1): 2,710 bases, 27,524 nodes, 1,088,445 certificates.

**Rank nodes.** The second program does not reject by rank: it explores the subtree below such a node with its own tests. On base
12632 of I.1 (4,2,1) both nodes die at once (4 candidates, all rejected by budget counts).

**Caveats.** The two programs share the hand model (C3 to C5), not code. The second program follows the first program's choice of
unit and regenerates all candidates of that unit. "Kept" is always a float decision.

## 4. Commands (from this folder, with PY and NPROC set)

- One case, whole pipeline: `bash cloud_case.sh <out> I.1 3 4 0`
- Check a run branch: `git archive origin/lemma-run/<job>-<id> | tar -x -C <dir>` then `python check_cloud.py <dir> <out file>`
- Repair a part stopped by the verifier of commit a318b7419 at a rank node (I.1 (4,2,1) on the small machines: the part holding
  base 12632): `python in_verify.py follow <s1.json> <.../parts/s2> <part> <N> <.../parts/vf_<part>of<N>.json>` then
  `python in_verify.py merge <s1.json> <.../parts/vb> <N> <.../parts/vf>`
