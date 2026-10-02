"""Move job keys that are already in order.txt to the front of the live queue (C2, 2026-10-02), atomically (non-forced push, retried on
refusal, exactly like queue_insert.py). Keys keep the order of KEYFILE; keys absent from order.txt are reported and ignored; events.jsonl and
control.json are never touched. Only the claiming ORDER changes: no job is added or removed.
  python q/tools/queue_move_front.py KEYFILE"""
import os, sys, subprocess, tempfile, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); QBR = os.environ.get("Q_QUEUE", "queue")


def git(*a, cwd):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()[-300:]))
    return r.stdout


def main():
    keys = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    url = git("remote", "get-url", "origin", cwd=REPO).strip(); d = tempfile.mkdtemp(prefix="q_mv_")
    git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
    for attempt in range(8):
        git("fetch", "-q", "origin", QBR, cwd=d); git("checkout", "-q", "-f", "-B", QBR, "FETCH_HEAD", cwd=d)
        p = os.path.join(d, "order.txt"); order = [l.strip() for l in open(p) if l.strip()]
        have = set(order); mv = [k for k in keys if k in have]; missing = [k for k in keys if k not in have]
        if missing: print("not in the queue (ignored): %d keys, e.g. %s" % (len(missing), missing[:3]))
        if not mv: print("nothing to move"); return
        sm = set(mv); new_order = mv + [k for k in order if k not in sm]
        assert sorted(new_order) == sorted(order) and len(new_order) == len(order)          # a permutation: nothing added or lost
        open(p, "w", newline="\n").write("".join(k + "\n" for k in new_order))
        git("-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com", "commit", "-qam",
            "queue: move %d job keys to the front" % len(mv), cwd=d)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + QBR], cwd=d, capture_output=True).returncode == 0:
            print("moved %d keys to the front; order.txt still has %d keys" % (len(mv), len(new_order))); return
        time.sleep(3 + 2 * attempt)
    sys.exit("could not update order.txt (8 refused pushes)")


if __name__ == "__main__":
    main()
