# t18_B0_VERIFC / run_parts.py -- LAUNCHER ONLY (no mathematics, no test of the proof).
# Runs the unchanged copy of c_mine.py that sits in <run dir> for a list of parts, at most <maxproc> processes at once.
# Each part:  python c_mine.py <s> <part> <nparts> <TL> <input json ...>   (cwd = run dir)
#   stdout -> <run dir>/c_mine_<s>_<part>of<nparts><tag>.out, stderr -> same name .err; c_mine.py itself writes the .json.
# A part whose .json already exists with timed_out == False is not started again (resumable).
# The environment is passed through unchanged (C_TAUS is how c_mine.py restricts to some matchings; tag = "_t<first>").
# usage: python run_parts.py <run dir> <maxproc> <s> <nparts> <TL s> <parts: all | a,b,c> <input json ...>
import subprocess, sys, os, time, json

rd = os.path.abspath(sys.argv[1]); maxproc = int(sys.argv[2]); s = sys.argv[3]; nparts = int(sys.argv[4]); TL = sys.argv[5]
parts = list(range(nparts)) if sys.argv[6] == "all" else [int(x) for x in sys.argv[6].split(",")]
files = [os.path.abspath(f) for f in sys.argv[7:]]
assert maxproc <= 6
tag = ("_t" + os.environ["C_TAUS"].split(",")[0]) if os.environ.get("C_TAUS") else ""
assert not os.environ.get("C_NOPSD")
logf = open(os.path.join(rd, f"driver_{s}_of{nparts}{tag}.log"), "a")


def say(m):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + m
    print(line, flush=True)
    logf.write(line + "\n"); logf.flush()


say(f"driver start: run dir {rd}; s {s}; nparts {nparts}; TL {TL}; parts {sys.argv[6]}; maxproc {maxproc}; "
    f"C_TAUS {os.environ.get('C_TAUS')}; python {sys.executable}; inputs {files}")
pending = []
for p in parts:
    js = os.path.join(rd, f"c_mine_{s}_{p}of{nparts}{tag}.json")
    if os.path.exists(js) and not json.load(open(js))["timed_out"]:
        say(f"part {p}/{nparts}: json already there with timed_out False, not started again")
        continue
    pending.append(p)
running = {}
T0 = time.time()
while pending or running:
    while pending and len(running) < maxproc:
        p = pending.pop(0)
        base = os.path.join(rd, f"c_mine_{s}_{p}of{nparts}{tag}")
        out = open(base + ".out", "w"); err = open(base + ".err", "w")
        cmd = [sys.executable, os.path.join(rd, "c_mine.py"), s, str(p), str(nparts), TL] + files
        pr = subprocess.Popen(cmd, stdout=out, stderr=err, cwd=rd)
        running[p] = (pr, time.time(), out, err)
        say(f"start part {p}/{nparts} pid {pr.pid}: " + " ".join(cmd))
    time.sleep(2)
    for p in list(running):
        pr, t0, out, err = running[p]
        rc = pr.poll()
        if rc is not None:
            out.close(); err.close()
            say(f"end part {p}/{nparts}: return code {rc}, wall {time.time() - t0:.0f}s")
            del running[p]
say(f"driver end: wall {time.time() - T0:.0f}s")
