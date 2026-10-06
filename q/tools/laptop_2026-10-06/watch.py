"""Poll the queue (read-only) and exit as soon as something worth reporting happens:
  - a lattice has no job left to do;  - a machine left the fleet (interrupted, error, stop);  - the ledger passed 85 % of the cap;
  - or MAXMIN minutes went by.   python watch.py <repo> [MAXMIN=25] [POLL_S=120]"""
import sys, json, subprocess, time, collections
REPO = sys.argv[1]; MAXMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 25; POLL = float(sys.argv[3]) if len(sys.argv) > 3 else 120
TERMINAL = {"FINI", "DRAINED", "STOP", "INTERRUPTED", "STOP CALIB", "ERREUR INSTALLATION", "REFUS", "ERREUR AGENT"}
g = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout


def snap():
    g("fetch", "-q", "--prune", "origin", "+refs/heads/queue:refs/remotes/origin/queue", "+refs/heads/run/q-*:refs/remotes/origin/run/q-*")
    order = g("show", "origin/queue:order.txt").split()
    ev = [json.loads(l) for l in g("show", "origin/queue:events.jsonl").splitlines() if l.strip()]
    ctl = json.loads(g("show", "origin/queue:control.json"))
    done = {j for e in ev if e["op"] == "done" for j in e["jobs"]}
    left = collections.Counter(j.split(":")[0] for j in order if j not in done)
    now = time.time(); live = set(); gone = {}; led = 0.0
    for ref in g("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*").split():
        st = dict(l.split("=", 1) for l in g("show", ref + ":status.txt").splitlines() if "=" in l)
        if not st.get("NAME") or st.get("CAMPAIGN") != ctl.get("campaign"):
            continue
        if st.get("STATE") in TERMINAL:
            gone[st["NAME"]] = st.get("STATE")
        elif now - float(st.get("NOW") or 0) <= 1500:
            live.add(st["NAME"])
        try:
            led = max(led, float(st.get("LEDGER_USD") or 0)) if st["NAME"] in live else led
        except ValueError:
            pass
    return left, live, gone, led, float(ctl["cap_usd"])


left0, live0, gone0, led0, cap = snap(); t0 = time.time()
while True:
    time.sleep(POLL)
    try:
        left, live, gone, led, cap = snap()
    except Exception as e:
        print("poll error:", e); continue
    why = []
    fin = [l for l in left0 if left0[l] > 0 and left.get(l, 0) == 0]
    if fin: why.append("lattice(s) fully computed: " + ", ".join(sorted(fin)))
    lost = sorted(live0 - live)
    if lost: why.append("machine(s) left the fleet: " + ", ".join("%s (%s)" % (m, gone.get(m, "silent")) for m in lost))
    if led >= cap - 2.5: why.append("ledger %.2f $ is within 2.5 $ of the cap %.0f $" % (led, cap))
    if (time.time() - t0) / 60 >= MAXMIN: why.append("%.0f minutes elapsed" % MAXMIN)
    if why:
        print("WATCH EVENT (%s UTC): %s" % (time.strftime("%H:%M", time.gmtime()), " | ".join(why)))
        print("machines alive: %d | ledger %.2f $ of %.0f $" % (len(live), led, cap))
        break
