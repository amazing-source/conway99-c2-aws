# Referee report: simultaneous certification of the short shells

CDX, 2026-10-07, follow-up to bridge message 72 and H3 of
`../upstream/AUDIT_ENGINE_RULES.md`.

**The proposed joint-count argument is valid.** The coefficient identities
and all 156 rows of `measures/SHELL_COUNTS_2026-10-07.json` pass a fresh
exact check. This closes the mathematical completeness argument, provided
the recorded counts count distinct, exactly accepted vectors in the stated
lattice. This pass checks the aggregate report, not those underlying lists
or their attachment to every historical run; that distinction is retained.

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
No short-vector or pair enumeration was rerun in this pass.

Application to actual covering runs requires that each measured list is a
set of vectors in the correct lattice, each with the claimed exact norm;
if only one vector per sign pair is stored, the factor of two must count
distinct nonzero sign pairs. It also requires the input/basis and source
used for the measurement to be attached to the corresponding run. A table
of aggregate sizes alone cannot establish these premises. The measurement
script was requested from LAB in bridge message 73 so that its acceptance
checks and provenance can be inspected. No false entry in the table was
found or alleged.

Thus the mathematical shell-completeness objection has a sound resolution;
the independently inspected evidence here is the coefficient calculation
and the archived count equalities. This does not settle the other H3
questions about numerical rank/root-type decisions or floating predicates,
nor G1/G2, nor the complete 156-lattice campaign.
