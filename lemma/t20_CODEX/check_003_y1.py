"""Check fixed-y1 root witnesses exactly; no y2 or frame enumeration."""
import os
for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ[name] = "1"
from fractions import Fraction as F
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--package", type=Path, default=Path("C:/home/researcher/Desktop/c2_experimental/c2_cloud_run_v10"))
parser.add_argument("--plan", type=Path)
args = parser.parse_args()
PKG = args.package.resolve()
LAB = PKG.parent
sys.path.insert(0, str(PKG / "scripts"))
import frame_dfs_next as FD
from verify_003_fixed_y1 import canonical_sha, matmul, verify

started = time.monotonic()
source = PKG / "external_runs/structures_3eceb4d/U/003.json"
plan_path = args.plan or PKG / "data/finishC/stream/003/plan.json"
if not plan_path.exists():
    plan_path = LAB / "data/finishC/stream/003/plan.json"
plan = json.loads(plan_path.read_text())
gens = json.loads(source.read_text())["gens"]
L = FD.lattice_data(gens, F(1))
B = L["B"]
basis_sha = sha256(json.dumps([[str(x) for x in row] for row in B]).encode()).hexdigest()[:16]
assert basis_sha == plan["basis_sha"], (basis_sha, plan["basis_sha"])
Y = np.asarray(plan["y1_reps"], dtype=np.int64)
assert len(Y) == 182
assert (np.einsum("ij,jk,ik->i", Y, L["G"], Y) == 7).all()
heights = Y @ L["G"] @ L["R"].T
energies = (heights * heights).sum(axis=1)
print("lattice_seconds", L["secs"], "basis_sha", basis_sha, "root_lines", len(L["R"]))
selected = []
for index in [i for i, e in enumerate(energies) if e == max(energies)]:
    c = Y[index]
    root_index = int(np.argmax(np.abs(heights[index])))
    r = L["R"][root_index]
    record = {"y1_class": index, "root_energy": int(energies[index]),
              "max_abs_root_height": int(abs(heights[index, root_index])),
              "y1_coefficients": list(map(int, c)), "root_coefficients": list(map(int, r)),
              "y1_ambient": [str(sum(F(int(c[i])) * B[i][j] for i in range(24))) for j in range(24)],
              "root_ambient": [str(sum(F(int(r[i])) * B[i][j] for i in range(24))) for j in range(24)],
              "root_norm": int(r @ L["G"] @ r), "root_y1_product": int(r @ L["G"] @ c)}
    selected.append(record)
print(json.dumps(selected))
result = {"basis_sha": basis_sha, "source_sha256": sha256(source.read_bytes()).hexdigest(),
          "plan_sha256": sha256(plan_path.read_bytes()).hexdigest(), "selected": selected,
          "seconds": time.monotonic() - started}
Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

# Produce a certificate whose checker uses only exact arithmetic and the
# original generator rows, without trusting the lattice enumeration above.
from envelope_trap import inverse_exact
change = matmul(B, inverse_exact([[F(x) for x in row] for row in gens]))
assert all(x.denominator == 1 for row in change for x in row)
lattice_input = json.loads(source.read_text())
certificate = {
    "statement": "No frame satisfying R for any second normal when y1 is one of these representatives, conditional on T18 and T20.",
    "lattice_input": lattice_input,
    "plan_input": plan,
    "lattice_canonical_sha256": canonical_sha(lattice_input),
    "plan_canonical_sha256": canonical_sha(plan),
    "plan_basis": [[str(x) for x in row] for row in B],
    "plan_basis_in_input_generators": [[int(x) for x in row] for row in change],
    "witnesses": [{"y1_index": r["y1_class"], "root_coefficients": r["root_coefficients"],
                   "y1_ambient": r["y1_ambient"], "root_ambient": r["root_ambient"]} for r in selected],
    "dependencies": ["lemma/upstream/AUDIT_REDUCTION.md R-vi and R-vii", "lemma/T18_PROOF.md", "lemma/T20_PROOF.md"],
}
print("standalone_check", json.dumps(verify(certificate, lattice_input, plan)))
Path(__file__).with_name("CERT_003_FIXED_Y1.json").write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
