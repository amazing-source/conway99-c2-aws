"""F4 runner (C2 lab, 2026-10-07): independent enumeration of the pairs of a few lattices, compared with the sweep's producer.
Started by q/qmachine.sh when Q_F4=1 (same install as production). No queue event, no write to the queue branch; outputs on run/<NAME>.
  Q_F4_LIDS="140 141 135 064"     the lattices (default); one lattice = one worker; Q_F4_WORKERS at a time (default: number of lattices)
For each lattice, in the package environment:
  1. the sweep's producer c1/code/y_pairs_gamma.py with the identity-only symmetry file q/audit_data/gamma_<lid>_identity.json
     (written on the fly if absent), whole stream -> f4/<lid>_stream.jsonl (not pushed: large);
  2. q/ypairs_c2.py (the lab's independent enumerator: all vectors of norm 7 by Fincke-Pohst, filters, W(R)-dominant y1, W_J-dominant
     y2 up to sign) -> its json (not pushed) and its log (pushed);
  3. q/f4_compare.py: both lists in one canonical form; they must be EQUAL -> f4/<lid>_compare.json (pushed), with the count of
     norm-7 lines against the theta series.
Exit 0 = finished or interrupted."""
import os, sys, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import qagent as Q


def main():
    a = Q.Agent(); lids = (Q.env("Q_F4_LIDS", "140 141 135 064") or "").split(); W = int(Q.env("Q_F4_WORKERS", str(len(lids))))
    sys.path.insert(0, a.pkg)
    import run_jobs as RJ
    RJ.check_manifest(); envx = RJ.env_exact(); envx["PYTHONPATH"] = os.path.join(a.pkg, "scripts") + os.pathsep + envx.get("PYTHONPATH", "")
    work = os.path.join(a.pkg, "results_f4"); os.makedirs(work, exist_ok=True)
    a.est = {}; Q.init_repo(a.qd, a.url); a.fetch(queue_only=True); a.campaign = "?"
    if not a.push_status("EN_COURS", "F4: independent pair enumeration on %s" % " ".join(lids)): raise RuntimeError("cannot push the first status")
    a.rearm_deadman(); od = os.path.join(a.pd, "f4"); os.makedirs(od, exist_ok=True)
    script = os.path.join(work, "one.sh")
    open(script, "w", newline="\n").write('''#!/bin/bash
PKG="$1"; LID="$2"; WORK="$3"; OD="$4"; REPO="$5"; PY="$6"
GAM="$REPO/q/audit_data/gamma_${LID}_identity.json"
[ -f "$GAM" ] || "$PY" -c "import json,sys; I=[[1 if i==j else 0 for j in range(24)] for i in range(24)]; json.dump({'id': int(sys.argv[1]), 'gamma_order': 1, 'matrices': [I]}, open(sys.argv[2], 'w'))" "$LID" "$GAM"
U="$PKG/external_runs/structures_3eceb4d/U/$LID.json"
( cd "$PKG/c1/code" && "$PY" y_pairs_gamma.py "$U" "$GAM" "$WORK/${LID}_stats.json" --stream "$WORK/${LID}_stream.jsonl" --max-seconds 86400 ) > "$OD/${LID}_producer.log" 2>&1 || exit 11
( cd "$PKG/scripts" && "$PY" "$REPO/q/ypairs_c2.py" "$U" "$WORK/${LID}_independent.json" ) > "$OD/${LID}_ypairs_c2.log" 2>&1 || exit 12
( cd "$PKG/scripts" && "$PY" "$REPO/q/f4_compare.py" "$PKG" "$LID" "$WORK/${LID}_stream.jsonl" "$WORK/${LID}_independent.json" "$OD/${LID}_compare.json" --log "$OD/${LID}_ypairs_c2.log" ) > "$OD/${LID}_compare.log" 2>&1 || exit 13
''')
    todo = [l for l in lids if not os.path.exists(os.path.join(od, "%s_compare.json" % l))]; running = {}; res = {}; last = time.time(); t00 = time.time()
    while todo or running:
        while todo and len(running) < W:
            l = todo.pop(0); running[l] = subprocess.Popen(["bash", script, a.pkg, l, work, od, REPO, sys.executable], env=envx)
        for l, p in list(running.items()):
            if p.poll() is None: continue
            del running[l]; res[l] = p.returncode; a.done_here.append(l); a.log("F4 %s: exit %s" % (l, p.returncode))
            a.push_status("EN_COURS", "F4: %s finished (exit %s); %d running, %d left" % (l, p.returncode, len(running), len(todo)))
        if a.spot_interrupted():
            for p in running.values():
                try: p.kill()
                except Exception: pass
            a.push_status("INTERRUPTED", "F4 interrupted"); return 0
        if time.time() - last >= 240:
            if a.push_status("EN_COURS", "F4: %d running (%s), %d left; %.1f h" % (len(running), " ".join(running), len(todo), (time.time() - t00) / 3600)): a.rearm_deadman()
            last = time.time()
        time.sleep(5)
    json.dump({"exit_codes": res, "hours": round((time.time() - t00) / 3600, 2)}, open(os.path.join(od, "SUMMARY.json"), "w"), indent=1)
    a.push_status("FINI", "F4: " + ", ".join("%s exit %s" % kv for kv in sorted(res.items())))
    return 0


if __name__ == "__main__":
    try: sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc(); sys.exit(2)
