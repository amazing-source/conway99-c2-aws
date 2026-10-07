# Upstream reduction: copies from the lab PC (deposited 2026-10-07 at the user's request)

These two files are copies. The originals stay on the lab PC and are not edited here.

| File | Original | What it is |
|---|---|---|
| `MODEL.md` | research workspace, root | The exact model: signed candidates N, the completion system L_N, T4, the question EX. Sections 5-6 state that every srg(99,14,1,2) with an involution fixing exactly one vertex gives a pair (N, D); this direction does not use T4. |
| `PROOF_SKELETON_C2.md` | `Desktop\c2_experimental\notes\` | Skeleton of the route-(C) proof, generated on 2026-10-01. Part I: the reduction to the 156 envelopes. Part II: the lemmas used by the exclusions. Part III: the table of the 156. Its status line and table are those of 01/10, not current. |

**Status of the reduction steps** (lab audit, `work/AUDIT_156_PLAN_2026-10-04.md` on the lab PC):

- The list of the 156 lattices was recomputed and is complete: 156 pairwise non-isometric odd unimodular lattices of rank 24 without
  norm-1 vector. One label erratum: the neighbours of 150 are E8^3 / D10E7^2, not D10E7^2 / D16E8. No effect on any exclusion.
- The twin rules of the engine were reread: conservative.
- The four items of Part I (involution structure, signed quotient and 7-tight frame, envelope theorem, frame identity at the new
  roots) are **source only, not reread** by the lab audit. Their sources are named in the skeleton: Makhnev-Minakova (2004) for the
  involution structure, the Astra dossier (AUDIT_NORME1) for min N* >= 8/7, Borcherds' classification, C1 notes 142/145.
- T4 is hand-reviewed according to the supplied transcript, not formally verified. It is needed only to restate a result as
  "EX is false" in the model, not for the statement about graphs.
