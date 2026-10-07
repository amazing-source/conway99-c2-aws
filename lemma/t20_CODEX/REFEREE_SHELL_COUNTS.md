# Referee report: simultaneous certification of the short shells

CDX, 2026-10-07, follow-up to bridge message 72 and H3 of
`../upstream/AUDIT_ENGINE_RULES.md`.

**The joint-count argument is valid, and the rebuilt local shells of all
156 inputs now pass exact acceptance.** Both lab count tables agree.
Following message 74, CDX ran the archived acceptance checker on every
input, with an added bound making its int64 norm evaluations provably
exact. This certifies the rebuilt local norm-two, norm-three and norm-four
catalogues under the stated lattice hypotheses. It does not attach those
catalogues to every historical covering run.

## Primary formulas and exact coefficient extraction

Conway and Sloane, [A Note on Optimal Unimodular Lattices](https://arxiv.org/pdf/math/0207292),
section 1, equations (2)-(3), state the theta-space and shadow formulas.
The relevant PDF page was read in text and visually. In rank 24,

    Theta_U(q) = sum_(r=0)^3 a_r theta_3(q)^(24-8r) Delta_8(q)^r,
    Theta_shadow(q) = sum_(r=0)^3 (-1)^r a_r/16^r
                     * theta_2(q)^(24-8r) theta_4(q^2)^(8r).

These are cited mathematical inputs, not theorems proved by the scripts.
The second formula uses **theta_4(q^2)**. This argument was omitted in the
local docstring; it is now explicit. The constant-term reasoning is
unaffected by that notational correction.

The fresh standard-library check `referee_shell_counts.py` expands the
Jacobi sums in `t=q^(1/4)` through degree 28. It constructs Delta_8 from
`theta_2^4 theta_4^4 / 16`, independently checks the product definition,
and compares the resulting coefficients with `theta_odd24.py`. It obtains

    a0 = 1, a1 = -48, a2 = N2 + 48, a3 = N3 - 4096,
    N4 = 196560 - 24 N2 - 24 N3,
    N5 = 276 N3,     N7 = 11178 N3.

The absence of norm-one vectors is used in `a1=-48`. Odd unimodularity,
rank 24 and N1=0 are properties required of the source lattice; counts
alone do not establish them.

## The joint-count proof

Let N2,N3,N4 be the true signed shell sizes, and E2,E3,E4 the numbers of
distinct validated vectors in the respective enumerated shells. Thus
`d_i=N_i-E_i >= 0`. Suppose the measured counts satisfy

    E4 + 24 E2 + 24 E3 = 196560.

Subtracting this from the exact theta identity gives

    d4 + 24 d2 + 24 d3 = 0.

Every summand is nonnegative and every weight is positive, so all three
deficits vanish. All three shells are complete simultaneously. This needs
no prior assumption that the root shell or the norm-three shell is complete,
and does not assume N3=4096. It is stronger than checking N4 against an
expected value while silently treating the other two measured counts as
already exhaustive.

## Optional shadow derivation and the norm-seven count

For an odd lattice the shadow is `U_0^* \ U^*`, so it does not contain zero.
In rank 24 only r=3 in the shadow formula can have a constant term; it is
`-a3/4096`. Therefore `a3=0`. The coefficient extraction above then proves
`N3=4096`, `N4=98256-24 N2` and

    N7/2 = 11178 * 4096 / 2 = 22,892,544.

Division by two counts lines {x,-x}; no nonzero vector is its own negative.
This supplies the expected count used by the norm-seven comparisons. It
does not certify that a particular norm-seven enumeration contains that
many distinct, valid lines. The shadow coefficient of q^2 is a2, hence
the signed norm-two shadow count is `N2+48` as used by the engine.

## Archived evidence and limits

The fresh check confirms IDs 000 through 155, nonnegative even integer
counts, zero residual in the joint identity for every row, N3=4096 in every
row, and `2*shadow_pairs=N2+48`. Its complete output is
`referee_shell_counts.json`; the canonical JSON SHA256 of the shell report is
`d05f41b2d3d13166b2f2c24f4d9b90f7f49e49518d89e25c570e5a9b3071dff5`.
No short-vector or pair enumeration was rerun in this initial coefficient
pass. The later short-shell rebuild is recorded below.

Application to actual covering runs requires that each measured list is a
set of vectors in the correct lattice, each with the claimed exact norm;
if only one vector per sign pair is stored, the factor of two must count
distinct nonzero sign pairs. It also requires the input/basis and source
used for the measurement to be attached to the corresponding run. A table
of aggregate sizes alone cannot establish these premises. The measurement
script was requested in message 73 and supplied in message 74. No false
count was found.

## Follow-up to message 74: all 156 local catalogues checked

LAB recovered the first measurement command as
`q/tools/lab_2026-10-07/shell_counts_first_run.txt`. It checked only the
count identity and norm-four norms, not all the acceptance premises. LAB
replaced it with `shell_counts.py` in the same directory, checking exact
basis membership/change of basis, Gram determinant one, norms and
distinctness up to sign. Its output is
`measures/SHELL_COUNTS_EXACT_2026-10-07.json`. CDX read both sources.

One arithmetic qualification remained: norms use NumPy int64 `einsum`,
not arbitrary-precision arithmetic. CDX added a check that coordinates
already have integer dtype, and, before every norm contraction, the
Python-integer bound

    M^2 * sum_ij abs(G_ij) < 2^63,

where M bounds every coordinate's absolute value in that shell. This
bounds the sum of absolute values of all terms, hence every product and
partial sum. Overflow cannot counterfeit a norm. Each bound is recorded.

A fresh run on all 156 inputs completed in **148 seconds**: every basis,
norm, distinctness and count-identity check passed. All **468 shell bounds**
passed; the largest was **2,928,240**, and the largest coordinate was 84.
The data are `referee_shell_acceptance.json` (byte SHA256
`a240c51d41407d13b9df0a8a89f85fba0dcdd67b2d2712347ae2317ffa638ab4`).

`check_shell_acceptance_report.py` checked every result against both lab
tables, actual source-file hashes, the engine hash and basis hashes: all
agreed. It also checked that all 156 package inputs have exactly the same
generator matrices as the lab inputs. The engine SHA256 is
`1591aeeac9c0be5c529a2ff492e66d390138cd221cba2ab67aac81748de9b759`.
The summary is `referee_shell_acceptance_summary.json`.

Reproduction (use a fresh output for the resumable checker):

```text
python lemma/t20_CODEX/run_shell_acceptance.py <lab-root> <fresh-output.json>
python lemma/t20_CODEX/check_shell_acceptance_report.py <lab-root>
```

The second command expects the fresh output at
`lemma/t20_CODEX/referee_shell_acceptance.json`. The wrapper sets only the
lab/package paths; acceptance arithmetic is in the archived checker.

This discharges short-shell completeness for **these rebuilt local bases
and inputs**. Odd unimodular rank 24 and absence of norm-one vectors remain
the stated R2 input hypotheses; the basis and determinant were checked
here. Shadow-list sizes were recorded but their vector membership, norm
and distinctness were not part of this run. Historical machines may have
rebuilt their lists in other bases, and older engines lack these
certificates. Their acceptance/provenance, other numerical rank/type or
floating-predicate questions, G1/G2 and the overall 156-lattice conclusion
are not certified by this local check.
