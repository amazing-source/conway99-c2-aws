"""Read-only progress of the route-(C) queue, per lattice, in twin-dependency order (laptop session, 2026-10-06).
  python progress.py <repo> [--since EPOCH]
A lattice is READY when every one of its queue jobs is done, its result files hold no INCOMPLETE pair and no not_excluded pair, and
every lattice it defers to is READY. Pairs set aside by the deferral mode (verdict DEFERRED, pending the lemmas T18 / T20; column
"defer") are never counted as excluded: a lattice with such pairs is "swept", not READY. READY is this script's own reading of the queue and the result files; the exclusion itself is
pronounced by the lab's stream_finish.py / import_golay.py at import time."""
import sys, os, json, subprocess, collections, time, io, zipfile
REPO = sys.argv[1]
SINCE = float(sys.argv[sys.argv.index("--since") + 1]) if "--since" in sys.argv else 0.0
ORDER = ["016", "002", "001", "014", "015", "013", "012", "011", "008", "009", "006", "007", "005", "003"]
BIG = ["013", "014", "015", "016"]
DEPS = {"012": BIG, "011": BIG, "006": ["011", "012"] + BIG, "007": ["011", "012"] + BIG, "008": ["011", "012"] + BIG,
        "009": ["011", "012"] + BIG, "005": ["006", "007", "008", "009", "011", "012"] + BIG,
        "003": ["005", "006", "007", "008", "009", "011", "012"] + BIG}
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress_cache2.json")


def git(*a, binary=False):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=not binary).stdout


git("fetch", "-q", "--prune", "origin", "+refs/heads/queue:refs/remotes/origin/queue", "+refs/heads/run/q-*:refs/remotes/origin/run/q-*")
order = [l.strip() for l in git("show", "origin/queue:order.txt").splitlines() if l.strip()]
ev = [json.loads(l) for l in git("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
ctl = json.loads(git("show", "origin/queue:control.json"))
now = time.time()
own, done, tdone = {}, set(), {}
for e in ev:
    for j in e.get("jobs", []):
        if e["op"] == "claim":
            own[j] = e["m"]
        elif e["op"] == "done":
            done.add(j); tdone[j] = e["t"]; own.pop(j, None)
        elif own.get(j) == e["m"]:
            own.pop(j)

# machines
ms = {}
for r in git("for-each-ref", "--format=%(refname:short) %(objectname)", "refs/remotes/origin/run/q-*").splitlines():
    ref, sha = r.split()
    st = dict(l.split("=", 1) for l in git("show", ref + ":status.txt").splitlines() if "=" in l)
    if st.get("NAME"):
        st["_sha"] = sha; ms[st["NAME"]] = st
TERMINAL = {"FINI", "DRAINED", "STOP", "INTERRUPTED", "STOP CALIB", "ERREUR INSTALLATION", "REFUS", "ERREUR AGENT"}
live = {n for n, st in ms.items() if st.get("STATE") not in TERMINAL and now - float(st.get("NOW") or 0) <= 1800}
running = collections.Counter(j.split(":")[0] for j, m in own.items() if m in live and j not in done)

# result files: INCOMPLETE / not_excluded per lattice (cached per branch head)
try:
    cache = json.load(open(CACHE))
except Exception:
    cache = {}
bad = collections.defaultdict(lambda: [0, 0, 0, 0])  # lid -> [INCOMPLETE pairs, not_excluded pairs, result records, DEFERRED pairs]
for n, st in ms.items():
    c = cache.get(n)
    if not c or c["sha"] != st["_sha"]:
        per = {}
        data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", "origin/run/" + n, "results"], capture_output=True).stdout
        if data:
            z = zipfile.ZipFile(io.BytesIO(data))
            for f in z.namelist():
                b = f.split("/")[-1]
                if not b.endswith(".jsonl") or not b[:3].isdigit():
                    continue
                for l in z.read(f).decode(errors="replace").splitlines():
                    try:
                        d = json.loads(l)
                    except ValueError:
                        continue
                    if "verdicts" not in d:
                        continue
                    p = per.setdefault(b[:3], [0, 0, 0, 0])
                    p[0] += sum(v for k, v in d["verdicts"].items() if "INCOMPLETE" in k)
                    ne = d.get("not_excluded")
                    p[1] += sum(1 for e in ne if not str(e.get("verdict", "")).startswith("DEFERRED")) if isinstance(ne, list) else 0
                    p[2] += 1; p[3] += sum(v for k, v in d["verdicts"].items() if k.startswith("DEFERRED"))
        c = cache[n] = {"sha": st["_sha"], "per": per}
    for lid, p in c["per"].items():
        for i in range(4):
            bad[lid][i] += p[i]
json.dump(cache, open(CACHE, "w"))

tot = collections.Counter(); dn = collections.Counter(); recent = collections.Counter()
for j in order:
    lid = j.split(":")[0]
    if lid in ORDER:
        tot[lid] += 1
        if j in done:
            dn[lid] += 1
            if tdone[j] >= SINCE and SINCE:
                recent[lid] += 1
ready = {}
for lid in ["016", "015", "014", "013", "002", "001", "012", "011", "009", "008", "007", "006", "005", "003"]:
    own_ok = dn[lid] == tot[lid] and bad[lid][0] == 0 and bad[lid][1] == 0 and bad[lid][3] == 0
    ready[lid] = own_ok and all(ready.get(d) for d in DEPS.get(lid, []))

print("=== %s UTC | cap %.0f $ | machines alive %d | jobs: done %d, running %d, free %d" % (
    time.strftime("%d/%m %H:%M", time.gmtime(now)), float(ctl["cap_usd"]), len(live), len(done & set(order)),
    sum(running.values()), sum(1 for j in order if j not in done) - sum(running.values())))
print("%-4s %12s %6s %7s %6s %6s %7s  %s" % ("lid", "done/total", "%", "running", "INCOMP", "not_ex", "defer", "state"))
for lid in ORDER:
    left = tot[lid] - dn[lid]
    if ready[lid]:
        s = "READY: excluded at the lab import"
    elif left == 0 and bad[lid][3] and not (bad[lid][0] or bad[lid][1]):
        s = "swept; %d pairs set aside, pending T18 / T20 (not excluded)" % bad[lid][3]
    elif left == 0 and (bad[lid][0] or bad[lid][1]):
        s = "computed, but %d INCOMPLETE / %d not excluded pairs to resolve" % (bad[lid][0], bad[lid][1])
    elif left == 0:
        s = "computed; waits on " + ", ".join(d for d in DEPS.get(lid, []) if not ready.get(d))
    elif bad[lid][3]:
        s = "%d jobs left; %d pairs set aside so far" % (left, bad[lid][3])
    else:
        s = "%d jobs left" % left + ((" (+%d done since start)" % recent[lid]) if recent[lid] else "")
    print("%-4s %12s %5.1f%% %7d %6d %6d %7d  %s" % (lid, "%d/%d" % (dn[lid], tot[lid]), 100.0 * dn[lid] / tot[lid] if tot[lid] else 100.0,
                                                   running[lid], bad[lid][0], bad[lid][1], bad[lid][3], s))
print("READY now: %s" % (", ".join(l for l in ORDER if ready[l]) or "none"))
if SINCE:
    h = (now - SINCE) / 3600; n = sum(recent.values())
    print("since the fleet started (%.2f h): %d jobs done, %.0f jobs/h" % (h, n, n / h if h > 0 else 0))
