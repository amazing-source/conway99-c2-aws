"""Park job keys: remove them from order.txt of the live queue (atomically, non-forced push retried like queue_insert.py), so no agent
claims them, and append them to a local park file for later re-insertion with queue_insert.py --back/--front (C2, 2026-10-03).
Only keys that are in order.txt and neither done nor currently claimed are removed. events.jsonl and control.json are never touched.
  python q/tools/queue_park.py KEYFILE PARKFILE"""
import os, sys, json, subprocess, tempfile, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); QBR = os.environ.get("Q_QUEUE", "queue")


def git(*a, cwd):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()[-300:]))
    return r.stdout


def main():
    keys = [l.strip() for l in open(sys.argv[1]) if l.strip()]; park = sys.argv[2]
    url = git("remote", "get-url", "origin", cwd=REPO).strip(); d = tempfile.mkdtemp(prefix="q_park_")
    git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
    for attempt in range(8):
        git("fetch", "-q", "origin", QBR, cwd=d); git("checkout", "-q", "-f", "-B", QBR, "FETCH_HEAD", cwd=d)
        order = [l.strip() for l in open(os.path.join(d, "order.txt")) if l.strip()]
        busy = set()
        for l in open(os.path.join(d, "events.jsonl")):
            if l.strip():
                e = json.loads(l)
                for j in e.get("jobs", []):
                    if e["op"] in ("claim", "done"): busy.add(j)
                    elif e["op"] in ("release", "fail") and j in busy: busy.discard(j)
        rm = [k for k in keys if k in set(order) and k not in busy]
        if not rm: print("nothing to park"); return
        s = set(rm); new = [k for k in order if k not in s]
        open(os.path.join(d, "order.txt"), "w", newline="\n").write("".join(k + "\n" for k in new))
        git("-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com", "commit", "-qam",
            "queue: park %d job keys (removed from order.txt, kept in a local park file)" % len(rm), cwd=d)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + QBR], cwd=d, capture_output=True).returncode == 0:
            open(park, "a", newline="\n").write("".join(k + "\n" for k in rm))
            print("parked %d keys (appended to %s); order.txt now has %d keys" % (len(rm), park, len(new))); return
        time.sleep(3 + 2 * attempt)
    sys.exit("could not update order.txt (8 refused pushes)")


if __name__ == "__main__":
    main()
