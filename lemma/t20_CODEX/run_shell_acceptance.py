"""Run the archived, overflow-guarded lab checker against an explicit lab root.

This wrapper sets paths only; the archived checker performs acceptance.
Use a fresh output path: existing result rows would be skipped by its resume
logic and would not receive the new bounds.
"""
import importlib.util
from pathlib import Path
import sys


lab = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
assert not output.exists(), "A fresh output is required for this referee run"
checker = Path(__file__).resolve().parents[2] / "q/tools/lab_2026-10-07/shell_counts.py"
spec = importlib.util.spec_from_file_location("lab_shell_acceptance", checker)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.LAB = str(lab)
module.PKG = str(lab / "c2_cloud_run_v10")
sys.path.insert(0, str(lab / "c2_cloud_run_v10/scripts"))
sys.argv = [str(checker), str(output), "600"]
module.main()
