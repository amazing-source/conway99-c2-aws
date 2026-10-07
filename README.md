# Lab PC records of route (C), as they are on 2026-10-07

Copy of `data/finishC/` of the lab PC (repository conway99-c2-experimental, where this folder is not tracked), deposited by the
lab session so that the records of the lattices computed on the lab PC between 27/09 and 07/10 exist somewhere else than on one
machine. Nothing here was recomputed for the deposit; it is not a certified archive.

- `data/finishC/finishC_tracker.json`: the tracker (143 excluded of 156 on 07/10) and its backups.
- `data/finishC/stream/<lid>/`: plan, chunk records (`chunks.jsonl`), resolutions of incomplete pairs, logs: the stream sweeps.
- `data/finishC/frame_dfs/<lid>/`: records of the frame_dfs and h-stage runs of 27-29/09.
- `data/finishC/golay/`, `o24_dfs/`, `o24_cloud/`, `o24_globallp/`, `pack/`, `compbudget*.jsonl`: the other methods.
- `data/finishC/sweep/`: reports of 07/10 (import of the deferral sweep, certificates of the Golay lattices, fixed-y1 certificate,
  rigid-kernel audit on the lab PC, coverage and census reports). The stream certificates are NOT copied: they are on the
  machine branches `run/q-*` of this repository.
- Left out: caches (`*.pkl`).

Which lattice has which kind of record, and which records also exist on a machine branch: `measures/RECONCILE_RECORDS_2026-10-07.json`
on master (script `q/tools/lab_2026-10-07/reconcile_records.py`).
