"""Third computation of the packing test (1) for the 18 lattices (C2 lab, 2026-10-07): review of Codex's independent implementation.

  .venv/Scripts/python.exe scripts/cloud/packing_test1_third.py <SUMMARY.json of measures/codex_independent_packing> <out.json>

Code path different from C1's envelope_pack.py and from Codex's program: the lists of frame_dfs_next.lattice_data (norm-3 vectors
X3 and doubled new roots S2 = 2 beta, one per pair +-, complete by the shell check of 07/10), and its own split of the new roots in
the two shadow classes (beta, beta' in the same class iff beta - beta' is in U with even norm). For each class: number of new
roots; m(x) = number of new roots beta of the class with |(beta,x)| = 3/2, both signs counted; sum of the 42 smallest m over the
2048 norm-3 vectors up to sign. Compared with Codex's record (new_shadow_roots_by_coset, sum_42_smallest) for each lattice.
Only test (1); the dual-trap step of 117, 134, 145, 146 is NOT recomputed here."""
import sys, json, os
from fractions import Fraction as F
import numpy as np
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(LAB, "c2_cloud_run_v10", "scripts"))


def main():
    import frame_dfs_next as FD
    R = json.load(open(sys.argv[1]))["records"]; out = {}
    for lid, r in sorted(R.items()):
        lid = "%03d" % int(lid)
        L = FD.lattice_data(json.load(open(os.path.join(LAB, "c2_cloud_run_v10", "external_runs", "structures_3eceb4d", "U", lid + ".json")))["gens"], F(1))
        G = np.asarray(L["G"], dtype=np.int64); X3 = np.asarray(L["X3"], dtype=np.int64).reshape(-1, 24); S2 = np.asarray(L["S2"], dtype=np.int64).reshape(-1, 24)
        assert len(X3) == 2048
        d = S2 - S2[0]; same = np.array([(x % 2 == 0).all() and int((x // 2) @ G @ (x // 2)) % 2 == 0 for x in d])
        hits = np.abs(X3 @ G @ S2.T) == 3; mine = []
        for cls in (same, ~same):
            m = 2 * hits[:, cls].sum(axis=1); mine.append([2 * int(cls.sum()), int(np.sort(m)[:42].sum())])
        mine.sort(); nb, s42 = r["new_shadow_roots_by_coset"], r["sum_42_smallest"]
        cod = sorted([int(a), int(b)] for a, b in zip(nb.values() if isinstance(nb, dict) else nb, s42.values() if isinstance(s42, dict) else s42))
        out[lid] = {"roots": r["roots"], "new_roots_and_sum_of_42_smallest_per_class": mine, "codex": cod, "equal": mine == cod,
                    "test_1_excludes": any(s > c for c, s in mine), "codex_test_1_excludes": r["test_1_excludes"]}
    ok = all(v["equal"] and v["test_1_excludes"] == v["codex_test_1_excludes"] for v in out.values())
    json.dump({"what": "third computation of packing test (1), lab, other code path; see scripts/cloud/packing_test1_third.py", "all_equal_to_codex": ok, "lattices": out}, open(sys.argv[2], "w"), indent=1)
    print("lattices %d; equal to Codex's numbers and verdicts of test (1): %s; test (1) excludes: %s" % (len(out), ok, [l for l, v in out.items() if v["test_1_excludes"]]))


if __name__ == "__main__":
    main()
