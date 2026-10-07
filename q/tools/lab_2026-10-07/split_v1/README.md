# frame_dfs_split.py: branch split of ONE pair, for the v1 engine only (lab, 27/09/2026)

**Scope. This tool belongs to the v1 engine `scripts/frame_dfs.py` (sha256 b48cf844..., present unchanged in package v10). It is
not a split of the v10 engine `frame_dfs_next.py`, and no such split exists.**

- What it does: its own copies of two v1 kernels, `dfs_generic_split` (pairs without flex point) and `dfs_general_u_split`
  (general mode with Lemma U+; needs FD_LEMMA_U=1), in which the branches of depth 0 are dealt round-robin to K processes: branch
  number b is explored only if (b - 1) mod K = r; a skipped branch is removed from the candidates exactly as after its exploration,
  so the union of the K runs is the sequential v1 search.
- Command: `python frame_dfs_split.py U.json pairs.json k K r out.jsonl` from a folder where `frame_dfs.py` is importable
  (the package's `scripts/`). `pairs.json` = {"pairs": [[y1, y2], ...]} in ambient coordinates (fraction strings), k = index of the
  pair, K = number of parts, r = this part (0..K-1). Environment: FD_LEMMA_U=1, FD_NODE_LIMIT (0 = none).
- Output, one line per part: nodes per depth, complete, leaves, lemmaZ, local_star_sums, joint, frame, bmod = K, brem = r.
  The pair is EXCLUDED when all K parts exist with complete = true and frame = 0 and joint = 0 (if joint > 0 the capped list of
  `joint` must be looked at: hole H1); a part with complete = false makes the pair INCOMPLETE.
- Validation on record (27/09): rigid mode, lattice 087, pair 1199: node counts per depth identical to the sequential run;
  general U+ mode, lattice 124, pair 1231: summed counts identical (lab note 49; tracker entry of 087). Used then for three
  symmetric pairs of 087 and for O24 classes. Nothing since.
- What it lacks compared with v10: every rule added after 27/09 (symmetry breaking by reflections at depth 0, 1 and at every depth;
  endpoint confinement and boundary points of 29/09; the Y = 13 rule; the fast set-up). So its tree is larger than v10's for the
  same pair, possibly much larger.
- Caveat H2 applies to `dfs_generic_split` as to every rigid kernel: a pair without flex point must first be checked for a
  zero-footprint candidate (`q/audit_rigid.py`).
