"""Recheck the archived T16 certificates; do not rewrite the received dossier.

This is a certificate pass, not a third coverage enumeration. In particular,
profile B checks witness membership missing from the received verifier.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
DOSSIER = ROOT / "lemma/t16/dossier_2026-10-04"


def hall_membership(record):
    demands = {i for i, value in enumerate(record["demand"]) if value}
    witness = set(record["independent_demand_set"])
    assert witness and witness <= demands, "Hall witness outside demand vertices"
    return witness


def main():
    started = time.monotonic()
    verifier = DOSSIER / "VERIFIER_WAGNER_CERTIFICATS.py"
    source = verifier.read_text(encoding="utf-8")
    # Load the inspected definitions only, avoiding its top-level output write.
    definitions, tail = source.split("\nAdata=", 1)
    assert "WAGNER_VERIFICATION_INDEPENDANTE.json" in tail
    namespace = {"__file__": str(verifier), "__name__": "referee_loaded_verifier"}
    exec(compile(definitions, str(verifier), "exec"), namespace)

    data_a = json.loads((DOSSIER / "WAGNER_PROFIL_A_CERTIFICATS.json").read_text())
    data_b = json.loads((DOSSIER / "WAGNER_PROFIL_B_CERTIFICATS.json").read_text())
    assert len(data_a["records"]) == 240 and len(data_b["records"]) == 32
    candidates = sum(namespace["check_A"](record) for record in data_a["records"])
    assert candidates == 6544
    for record in data_b["records"]:
        witness = hall_membership(record)
        assert len(witness) == 3 and len(set(record["possible_partners"])) == 2
        namespace["check_B"](record)

    # Negative control: use a real zero-demand position, not an invalid index.
    bad = deepcopy(data_b["records"][0])
    non_demand = next(i for i, value in enumerate(bad["demand"]) if not value)
    bad["independent_demand_set"] = [non_demand]
    bad["possible_partners"] = []
    namespace["check_B"](bad)  # Received verifier incorrectly accepts this.
    try:
        hall_membership(bad)
    except AssertionError:
        supplemental_rejects = True
    else:
        raise AssertionError("Negative control was not rejected")

    paths = [ROOT / "lemma/T16_PROOF.md", *sorted(DOSSIER.glob("*.txt")),
             *sorted(DOSSIER.glob("*.py")),
             DOSSIER / "WAGNER_PROFIL_A_CERTIFICATS.json",
             DOSSIER / "WAGNER_PROFIL_B_CERTIFICATS.json"]
    hashes = {}
    for path in paths:
        raw = path.read_bytes()
        hashes[str(path.relative_to(ROOT)).replace("\\", "/")] = {
            "sha256_bytes": sha256(raw).hexdigest(),
            "sha256_lf": sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        }
    result = {
        "source_commit": "9ad23660d9e7d6a3f525f26b094f900ed59ff698",
        "profile_A_obstructions_verified": len(data_a["records"]),
        "profile_A_candidate_orbits_recomputed": candidates,
        "profile_B_obstructions_verified": len(data_b["records"]),
        "profile_B_all_witnesses_three_demand_vertices_two_partners": True,
        "negative_control": {
            "zero_demand_position": non_demand,
            "received_verifier_accepts_non_demand_singleton": True,
            "supplemental_membership_check_rejects": supplemental_rejects,
        },
        "coverage_enumerators_rerun": False,
        "seconds": time.monotonic() - started,
        "sources": hashes,
    }
    output = Path(__file__).with_suffix(".json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "sources"}))


if __name__ == "__main__":
    main()
