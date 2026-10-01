"""Insert new job keys into order.txt of the live queue branch (C2, 2026-10-02), atomically (non-forced push, retried on refusal, exactly
like monitor_q.set_control). events.jsonl and control.json are never touched; keys already in order.txt are skipped.
Agents only claim keys present in THEIR package's jobs.json, so keys of a newer package (v3 job kinds) are ignored by older machines.
  python q/tools/queue_insert.py --front KEYFILE     insert the keys (one per line) at the front, in file order
  python q/tools/queue_insert.py --back  KEYFILE     append them at the end"""
import os, sys, json, subprocess, tempfile, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); QBR = os.environ.get("Q_QUEUE", "queue")


def git(*a, cwd):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()[-300:]))
    return r.stdout


def main():
    where, kf = sys.argv[1], sys.argv[2]; assert where in ("--front", "--back")
    keys = [l.strip() for l in open(kf) if l.strip()]
    url = git("remote", "get-url", "origin", cwd=REPO).strip(); d = tempfile.mkdtemp(prefix="q_ins_")
    git("init", "-q", cwd=d); git("remote", "add", "origin", url, cwd=d)
    for attempt in range(8):
        git("fetch", "-q", "origin", QBR, cwd=d); git("checkout", "-q", "-f", "-B", QBR, "FETCH_HEAD", cwd=d)
        p = os.path.join(d, "order.txt"); order = [l.strip() for l in open(p) if l.strip()]
        have = set(order); new = [k for k in keys if k not in have]
        if not new: print("nothing to insert (all %d keys already in the queue)" % len(keys)); return
        order = new + order if where == "--front" else order + new
        open(p, "w", newline="\n").write("".join(k + "\n" for k in order))
        git("-c", "user.name=amazing-source", "-c", "user.email=206353265+amazing-source@users.noreply.github.com", "commit", "-qam",
            "queue: insert %d job keys (%s)" % (len(new), where[2:]), cwd=d)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + QBR], cwd=d, capture_output=True).returncode == 0:
            print("inserted %d keys at the %s; order.txt now has %d keys" % (len(new), where[2:], len(order))); return
        time.sleep(3 + 2 * attempt)
    sys.exit("could not update order.txt (8 refused pushes)")


if __name__ == "__main__":
    main()
