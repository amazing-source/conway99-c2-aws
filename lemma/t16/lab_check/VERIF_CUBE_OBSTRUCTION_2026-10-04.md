# Check of the external note "C2: obstruction to extending the support of size 16" (04/10/2026)

The note is by ChatGPT. The user pasted it into the Claude session, and its text is not stored in this workspace. Its control file
`C2_PREUVE_CUBE_CONTROLE.json` is not on the PC either.

## Result checked

**Hypotheses:**

- A is the adjacency matrix of a real srg(99,14,1,2).
- σ is an involution with one fixed vertex p; its 7 adjacent pairs are the pairs of N(p).
- f is an eigenvector for −4, σ-odd, with values in {0,±1}, eight +1 and eight −1.
- The 8 active orbits are exterior.

**Conclusion:** B = A[P,σP] cannot be the complement of the cube Q_3.

**Place in the project.** This is exactly the configuration "B4" left open in `Desktop\c2_experimental\notes\54_SOLO_MODELE_JOINT_TEMOIN_28_09.md`,
within the case k = 0, n = 8 of the witness approach (equality case of min N* ≥ 8/7). Note 54 had found it locally consistent:
41,207,680 raw configurations, and "global information is needed".

## Check: all steps re-derived by hand by Claude

| § | What was re-derived |
|---|---|
| 8 | D = m(m−7) − 7e − Σd_i², hence e = 0. Also (B²)_ij = 2C_ij + (C²)_ij for i ≠ j, from (J − I − C)² with JC = 3J. |
| 2 | d_z ≤ 2 (union of three 4-sets ≥ 9 > 8); Σd = 80, ΣC(d,2) = 8, hence \|X_0\|, \|X_1\|, \|X_2\| = 11, 64, 8. |
| 3 | b + 2a = 16 − 5d and c = a + 3d − 2 (2-paths to the support, via the neighbours of z); Σ_{X_0}(a − 2) = 10 + 2t. |
| 4 | Co-degrees in the cube complement: 0 for antipodal pairs, 2 otherwise. So X_2 consists of the 4 antipodal pairs, each twice, on both the P side and the Q side. The orbit multigraph is simple and 2-regular, hence a C_4. |
| 5 | Common support neighbours = 2·[same origin] + 2·[same end]. So the concurrence graph is 2 disjoint C_4, and N(z) ∩ X_2 is independent in each of them. |
| 6 | C(r,2) ≥ r − 1 for r ∈ {0,1,2}. So Σq ≥ 10 against Σq ≤ 4 diagonals × μ = 8. |
| 7 | Σa = 80, Σa² = 160 − 2t, hence t ≤ 1; in C2, t = 1 and a_p = 2; the two profiles A and B; the possible graphs on X_0 (no edge z—σz, because c_p = 0). |

**Verdict:** correct. No gap was found.

Minor points that do not change the result:

- §8 only uses the "no triangle" part of the condition co-degree ≤ 2. This is enough, because the classification it gives (cube,
  Wagner) is complete.
- In §7, the profile "(2,1,…,1)" counts one vertex per pair.

## Novelty

This is new relative to the lab. Note 54 is the only place where B4 appears, and it stops before any obstruction. The counts of §2–3
and t ≤ 1 were already known (Wave 81, according to the note).

## Scope: a sub-case of the witness approach, not route (C)

- It closes half of the last case k = 0 (n = 8) of note 54. Note 54 excludes n = 5, 6, 7 for k = 0 using min N* ≥ 8/7.
- **Still open:**
  - B5, the complement of the Wagner graph. There the deficits are the 8 pairs (i, i+2) of the cycle, each once, instead of 4 pairs
    twice. Two X_2 vertices therefore share at most 1 support vertex, and the argument of §5 does not apply as written.
  - The cut cases k = 1, 2, 3 with n = 5..8. Note 54 left them unresolved (CP-SAT UNKNOWN, abandoned).
- According to note 54, the reduction of the witness approach also rests on n ≤ 8, which is COMPUTED by the team.
- No lattice excluded; nothing changes for the AWS campaign.

## Addendum (about 14:00 UTC): the pair criterion that min N* >= 9/7 would give

**Claim (ChatGPT).** The Wagner obstruction raises the bound to min N* >= 9/7 and gives a criterion for excluding pairs: on 400
archived pairs of 011, it found an exact witness for 363.

**Reduction (Claude, re-derived by hand).**

- The frame lattice N (rank 22) lies in K = U cap {y1,y2}^perp, so K* is contained in N*. Since U is unimodular, K* = pi(U).
- A witness of norm exactly 8/7 is a v in U with 7|v|^2 - Y(v) = 8, where Y(v) = (v,y1)^2 + (v,y2)^2.
- Subtract multiples of y1 and y2 (which lie in U) to get |(v,y_i)| <= 3. Then |v|^2 <= 26/7, so |v|^2 is 2 or 3. Norm 2 would need
  Y = 6, which is not a sum of two squares.
- **Criterion: a norm-3 vector v of U with {|(v,y1)|, |(v,y2)|} = {2, 3}.** It costs 2,048 dot products per pair.

**Measurement.** `Desktop\c2_experimental\scripts\analysis\min97_probe.py`; samples of searched pairs, i.e. pairs that reach the
DFS; single process; under 1 GB.

- Violations of the proved 8/7 bound: 0 on every lattice, which is consistent.

| Lattice | Searched pairs killed | Share of their search nodes | Costliest 10 % of pairs: share of nodes killed |
|---|---|---|---|
| 003 | 99 % | 93 % | 89 % |
| 006 | 89 % | 51 % | 40 % |
| 009 | 93 % | 70 % | 62 % |
| 011 | 90 % | 70 % | 52 % |
| 012 | 91 % | 62 % | 47 % |
| 013 | 82 % | 43 % | 33 % |
| 014 | 89 % | 65 % | 50 % |
| 015 | 88 % | 55 % | 19 % (only 5 pairs) |

- None of these samples contains a K = 0 pair.
- 005, 007, 008 and 016 have no sample on the PC. Golay 001/002 were not measured (separate pipeline).
- With the split 112 ms setup + 392 ms DFS per searched pair measured on 011, the expected gain is about ×2 to ×4 depending on the
  lattice. **This is an estimate from samples, not a measurement on real jobs.**

**Status: NOT USABLE for verdicts at this point.** min N* >= 9/7 requires excluding EVERY a in Z^49 with S a = -4a and
Sum a^2 = 8. The argument of AUDIT_NORME1 §2, re-derived for Sum a^2 = 8 (a coefficient +-2 would leave an absolute sum of at most 4,
against the 6 or 8 its row needs), shows that all such a have entries in {0, +-1} with support m = 8. The full list of cases is:

1. 8 exterior active orbits, B = cube complement: closed (checked above).
2. 8 exterior active orbits, B = Wagner complement: claimed by ChatGPT, not seen yet.
3. **Cases with interior active orbits** (B with diagonal entries; p then sees the support, d_p = number of interior active orbits,
   at most 2). The coefficients (v, h_c) of a witness are not zero in general, so the pair criterion needs these cases.
   It is not known yet whether ChatGPT treated them.

## Addendum 2 (about 15:00 UTC): ChatGPT's Wagner dossier, check by Claude

The dossier is in `work/chatgpt_wagner_2026-10-04/`; the re-runs are in `rerun/`.

### Point 3, active h (`LEMME_EGALITE_8_SUR_7_C2.txt`)

Re-derived by hand: correct.

- Column sums of C are even, so k (the number of active h) is even.
- 3k <= 2(8 - k) gives k in {0, 2}.
- k = 2 is impossible: in the two-diagonal B, rows 0 and 1 meet in at most 1 index, since p is already a common neighbour. If
  A ∩ C is empty, a 1-regular graph on 3 vertices would be needed. If |A ∩ C| = 1, rows a and b would meet in 3 indices.

### Wagner (`C2_WAGNER_BORNE_9_SUR_7.txt` §3–6)

The structural reductions were reread; their scope is sound.

- The 8 deficient pairs, each exactly once, give perfect matchings of the orbits.
- Constraints (i)–(iii) are necessary. Rows and columns are covered through the reversed rectangle.
- {x,y}: U ∩ V empty.
- The formula for (C^t C)_st: there is no X2 term, because X2 has a single edge. The E term covers the exceptional X1 orbit,
  including the σ-invariant case.
- Profile B: the 8 demands give a perfect matching, the allowed pairs are a superset, and the 3-against-2 obstruction is a Hall
  violation.
- Profile A: the identity A^2 1_{X2} at x gives Σ_T a = 12 - q, hence q = 0. The induced matching in N(x) gives e + f >= 2. The
  4-cliques use safe relaxations (edges left out only lower the counts).

### Finite parts

Re-run on the PC:

- **Profile A:** 105 / 31 / 76 / 48 / 640; (e,f) = (1,0) ×400 and (1,1) ×240; 0 four-cliques; 151 s.
- **Profile B:** 16 / 32; 32 certificates.
- **Verifier:** 240 + 32 obstructions, 6,544 candidates.
- **Records** identical to the supplied certificates; only timing and source metadata differ.
- **011 witnesses:** 363 checked exactly. My criterion (min97_probe) finds **exactly the same 363 pairs**.

### Pending

An independent re-implementation of the enumeration from the mathematical text alone, without the ChatGPT code (agent).

### Chain if it agrees

min L* >= 8/7 (AUDIT_NORME1, PROVED-ELSEWHERE) + equality case (cube: hand; Wagner: hand + computed finite classification; active
h: hand) => min L* >= 9/7 for the frame of a real graph. The Y = 13 pair criterion then follows.

## Addendum 3 (about 17:30 UTC): independent re-implementation of Wagner — AGREES

`work/indep_wagner_check/` (agent; written from the mathematical statement only, without reading ChatGPT's code).

**Stage 1 (configurations on Y):** identical counts.

| Count | Value |
|---|---|
| Perfect matchings | 105 |
| Pass the P–Q bound | 75 |
| Pass all bounds on P∪Q∪X2 | **31** |
| (matching, xy-orbit) pairs | **76** |
| X0–X2 incidences | **48 (A) / 16 (B)** |
| X0 graphs | **48 / 18** |
| Valid labelled Y configurations | **640 / 32**; up to isomorphism, 40 / 2 |

- The normalisation was checked by switching each rule off: the normal forms are identical.

**Stage 2 (the 4 X1-neighbours of x):** a different argument from ChatGPT's, with zero survivors.

- **All of B, and 25 of the 40 classes of A:** only 2 edges inside N(x) ∩ Y, so 6 vertices need a partner among the 4 t. Impossible.
- **The other 15 classes of A:** each t needs σt to have exactly 2 common neighbours with x, and the λ/μ bounds must hold. Every
  assignment fails one of these.
- **Second stage-2 implementation** (generic, brute force over the T–σT edges): 0 survivors over 80 + 4 runs.
- The only relaxation: unknown X1 vertices and edges are left out, which is safe.

**Conclusion.** The 9/7 lemma rests on:

- the 8/7 bound (AUDIT_NORME1, PROVED-ELSEWHERE);
- the active-h lemma and the cube case (hand, rechecked);
- Wagner: hand reductions, plus a finite classification computed by two independent implementations that agree, plus ChatGPT's
  certificates, re-run identically.

**Y = 13 criterion: usable** (verdict label separate from the others).
