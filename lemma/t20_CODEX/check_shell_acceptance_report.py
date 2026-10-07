"""Cross-check the fresh guarded run, both lab tables, and actual input hashes."""
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    lab = Path(sys.argv[1]).resolve()
    result_path = here / "referee_shell_acceptance.json"
    result = json.loads(result_path.read_text())
    first = json.loads((repo / "measures/SHELL_COUNTS_2026-10-07.json").read_text())
    second = json.loads((repo / "measures/SHELL_COUNTS_EXACT_2026-10-07.json").read_text())
    assert set(result) == set(first) == set(second) == {f"{i:03d}" for i in range(156)}
    engine_sha = digest(lab / "c2_cloud_run_v10/scripts/frame_dfs_next.py")
    bounds = []
    coordinates = []
    for lid, row in sorted(result.items()):
        assert all(row[k] is True for k in ("basis_of_U", "norms_exact", "distinct_up_to_sign", "identity", "ok"))
        assert all(row[k] == first[lid][k] == second[lid][k] for k in ("N2", "N3", "N4"))
        assert row["N4"] + 24*row["N2"] + 24*row["N3"] == 196560
        assert row["N3"] == 4096
        assert row["engine_sha256"] == engine_sha[:16] == second[lid]["engine_sha256"]
        assert row["basis_sha"] == second[lid]["basis_sha"]
        source = lab / f"external_runs/structures_3eceb4d/U/{lid}.json"
        package_source = lab / f"c2_cloud_run_v10/external_runs/structures_3eceb4d/U/{lid}.json"
        assert digest(source)[:16] == row["lattice_file_sha256"] == second[lid]["lattice_file_sha256"]
        source_record, package_record = json.loads(source.read_text()), json.loads(package_source.read_text())
        assert source_record["id"] == package_record["id"] == int(lid)
        assert source_record["gens"] == package_record["gens"]
        assert set(row["integer_norm_bounds"]) == {"N2", "N3", "N4"}
        for b in row["integer_norm_bounds"].values():
            assert type(b["absolute_sum_bound"]) is int and 0 <= b["absolute_sum_bound"] < 2**63
            bounds.append(b["absolute_sum_bound"])
            coordinates.append(b["max_abs_coordinate"])
    summary = {
        "verified": True, "lattices": len(result), "shells_with_overflow_bounds": len(bounds),
        "max_norm_contraction_absolute_sum_bound": max(bounds),
        "max_absolute_coordinate": max(coordinates),
        "all_counts_match_both_lab_tables": True,
        "all_input_hashes_checked": True, "all_package_generators_match_lab_input": True,
        "all_bases_match_second_lab_table": True,
        "engine_sha256": engine_sha, "fresh_report_sha256": digest(result_path),
        "historical_runs_individually_certified": False,
        "run_elapsed_seconds_reported": 148,
    }
    print(json.dumps(summary, indent=2))
    here.joinpath("referee_shell_acceptance_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
