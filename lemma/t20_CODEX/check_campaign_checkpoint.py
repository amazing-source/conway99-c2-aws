"""Read-only audit of the 156-entry conversion and archived final F4 result.

Usage: python check_campaign_checkpoint.py <lab-root>
This checks archived results and tracker changes, not the full proof or a
replay of its enumerations. It never writes the lab tracker or lemma file.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    lab = Path(sys.argv[1]).resolve()
    input_encodings = {}

    def git(*args):
        return subprocess.check_output(
            ["git", "-c", f"safe.directory={repo.as_posix()}", *args], cwd=repo)

    def read(path):
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            # The lab acceptance record was emitted with the Windows
            # default encoding. Decode explicitly; preserve the quote.
            text = raw.decode("cp1252")
            encoding = "cp1252"
        input_encodings[path.as_posix()] = encoding
        return json.loads(text)

    def canon_sha(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    archived = read(repo / "measures/finishC_tracker_2026-10-07_156.json")
    live = read(lab / "data/finishC/finishC_tracker.json")
    backup_path = lab / "logs/finishC_tracker_before_convert_1007_1947.json"
    before = read(backup_path)
    assert archived == live
    old, new = ({r["id"]: r for r in t["lattices"]} for t in (before, archived))
    assert len(before["lattices"]) == len(archived["lattices"]) == 156
    assert set(old) == set(new) == set(range(156))
    assert sum(r["status"] == "excluded" for r in old.values()) == 143
    assert all(r["status"] == "excluded" for r in new.values())
    assert {k: v for k, v in before.items() if k != "lattices"} == {
        k: v for k, v in archived.items() if k != "lattices"}
    changed = [i for i in sorted(new) if old[i] != new[i]]
    assert changed == [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15]
    fields = {}
    for i in changed:
        assert old[i]["status"] != "excluded"
        fields[str(i)] = sorted(k for k in old[i].keys() | new[i].keys() if old[i].get(k) != new[i].get(k))
        assert set(fields[str(i)]) <= {"status", "by", "reviewed_by", "status_note"}
    accepted = read(repo / "measures/lemmas_accepted_2026-10-07.json")
    assert accepted == read(lab / "data/finishC/lemmas_accepted.json")
    assert set(accepted) == {"T18", "T20"}
    blobs = {}
    for name, record in accepted.items():
        assert re.fullmatch(r"[0-9a-f]{40}", record["repo_commit"])
        actual = git("rev-parse", f'{record["repo_commit"]}:lemma/{name}_PROOF.md').decode().strip()
        assert actual == record["git_blob"]
        blobs[name] = actual

    run_ref = "origin/run/q-i-011dce74cd612fc52"
    run_commit = git("rev-parse", run_ref).decode().strip()
    f4 = json.loads(git("show", f"{run_commit}:f4/064_compare.json"))
    assert f4["id"] == 64 and f4["equal"] is True
    assert f4["only_in_independent"] == f4["only_in_producer"] == 0
    assert f4["independent"]["pairs"] == f4["producer"]["distinct_after_canonical_form"] == 1050528
    assert f4["independent"]["y1_orbits"] == f4["producer"]["y1_orbits"] == 1856
    assert f4["producer"]["stream_complete"] is True
    assert f4["producer"]["pairs_in_stream"] == 2100288
    assert f4["producer"]["duplicates"] == 1049760
    assert f4["producer"]["pairs_in_stream"] == f4["producer"]["duplicates"] + f4["producer"]["distinct_after_canonical_form"]
    assert f4["norm7_lines"] == f4["norm7_lines_expected"] == 22892544 and f4["norm7_count_ok"] is True
    log = git("show", f"{run_commit}:f4/064_producer.log").decode()
    merged = json.loads([line for line in log.splitlines() if line.startswith("{")][-1])
    assert merged["complete"] is True and merged["merged_chunks"] == len(merged["chunks"]) == 28
    assert sorted(c["chunk"] for c in merged["chunks"]) == [[k, 28] for k in range(28)]
    assert all(c["complete"] is True for c in merged["chunks"])
    assert sum(c["pairs"] for c in merged["chunks"]) == merged["pairs"] == 2100288

    control = json.loads(git("show", f"{run_commit}:f4/140_compare.json"))
    reference_commit = git("rev-parse", "origin/run/q-i-02aa613ee361fbc10").decode().strip()
    reference = json.loads(git("show", f"{reference_commit}:f4/140_compare.json"))
    without_timing = lambda d: {k: v for k, v in d.items() if k not in {"t", "seconds"}}
    assert without_timing(control) == without_timing(reference)

    result = {
        "verified": True, "checkpoint_commit": "414e68d23",
        "tracker_before_excluded": 143, "tracker_after_excluded": 156,
        "changed_lattice_ids": changed, "changed_fields": fields,
        "live_tracker_matches_archived": True,
        "tracker_canonical_sha256": canon_sha(archived),
        "backup_canonical_sha256": canon_sha(before),
        "accepted_record_matches_live": True, "accepted_proof_blobs_checked": blobs,
        "accepted_record_canonical_sha256": canon_sha(accepted),
        "input_encodings": input_encodings,
        "f4_run_commit": run_commit, "f4_064_result": f4,
        "f4_064_all_28_chunk_counters_checked": True,
        "f4_140_reference_run_commit": reference_commit,
        "f4_140_control_matches_except_timing": True,
        "proof_or_enumerations_replayed": False,
        "whole_proof_referee_pass_completed": False,
        "lean_formalisation_completed": False,
    }
    here.joinpath("campaign_checkpoint_156.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"f4_064_result", "changed_fields"}}, indent=2))


if __name__ == "__main__":
    main()
