"""One-off patch of sweep48tp.py: optional sixth argument 'rev' = same list from the end, own log, skipping the balls
that the other process has already logged."""
import ast
BS = chr(92)
s = open("sweep48tp.py", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"


def rep(old, new):
    global s
    old = old.replace("\n", nl); new = new.replace("\n", nl)
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)


rep("""def job(a):
    s, b, line = a
    t0 = time.time()
    try:""", """def job(a):
    s, b, line = a[:3]
    t0 = time.time()
    if len(a) > 3 and a[3] and os.path.exists(a[3]):          # a second process works on the same list from the other end
        if any(l.startswith(f"48t {s} {b} |") for l in open(a[3])): return None
    try:""")
rep("""    log = f"sweep_48tp_T{T}_part{part}of{nparts}.log"; done = set()
    if os.path.exists(log):
        for l in open(log): done.add(l.split("|")[0].strip())
    todo = [j for j in jobs if f"48t {j[0]} {j[1]}" not in done]""",
    """    log = f"sweep_48tp_T{T}_part{part}of{nparts}.log"; done = set()
    rev = len(sys.argv) > 5 and sys.argv[5] == "rev"           # same list from the end, own log, skips what the other did
    other = log.replace(".log", "_rev.log") if not rev else log
    if rev: log = log.replace(".log", "_rev.log")
    for lg in (log, other):
        if os.path.exists(lg):
            for l in open(lg): done.add(l.split("|")[0].strip())
    todo = [j + (other,) for j in jobs if f"48t {j[0]} {j[1]}" not in done]
    if rev: todo.reverse()""")
rep("        for line in pool.imap_unordered(job, todo, chunksize=1):\n            out.write(line + \"" + BS + "n\"); out.flush(); n += 1",
    "        for line in pool.imap_unordered(job, todo, chunksize=1):\n            if line is None: continue\n"
    "            out.write(line + \"" + BS + "n\"); out.flush(); n += 1")
ast.parse(s)
open("sweep48tp.py", "w", newline="").write(s)
print("patched")
