"""Run ONE stream job on the laptop exactly as q/qtail.py does on a machine: q/producer_big.py (higher y2 cap) piped into
q/par_consumer.py in quick deferral mode (laptop, 2026-10-07; the AWS sessions had expired and five jobs of 003 / 005 fail on AWS
because the package's producer truncates at 10^6 y2 candidates).
  <venv python> local_big_job.py <repo> <pkg> <key> <out dir> [max_out=50000000] [P=6] [W=3]
Writes <out dir>/<lid>_<k>_<n>.jsonl (the record), _producer.err, _consumer.out. The record is NOT published to the queue."""
import sys, os, json, subprocess, time
REPO, PKG, KEY, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3], os.path.abspath(sys.argv[4])
MAXOUT = sys.argv[5] if len(sys.argv) > 5 else "50000000"; P = sys.argv[6] if len(sys.argv) > 6 else "6"; W = sys.argv[7] if len(sys.argv) > 7 else "3"
sys.path.insert(0, PKG)
import run_jobs as RJ
env = dict(RJ.env_exact(), Q_DEFER="1", Q_DEFER_NODES="0", Q_PRODUCER_MAXOUT=MAXOUT); os.makedirs(OUT, exist_ok=True)
job = {"%s:%d:%d" % (j["lid"], j["k"], j["n"]): j for j in json.load(open(os.path.join(PKG, "jobs.json")))}[KEY]
lid, k, n = job["lid"], job["k"], job["n"]; tag = "%s_%d_%d" % (lid, k, n); res = os.path.join(OUT, tag + ".jsonl")
U = os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid); t0 = time.time()
prod = subprocess.Popen([sys.executable, os.path.join(REPO, "q", "producer_big.py"), PKG, MAXOUT, U, os.path.join(PKG, job["gamma"]), os.path.join(OUT, tag + "_producer_stats.json"),
                         "--from-plan", os.path.join(PKG, job["plan"]), "--chunk", "%d/%d" % (k, n), "--stream", "-", "--max-seconds", "86400"],
                        env=env, cwd=os.path.join(PKG, "c1", "code"), stdout=subprocess.PIPE, stderr=open(os.path.join(OUT, tag + "_producer.err"), "w"))
cons = subprocess.Popen([sys.executable, os.path.join(REPO, "q", "par_consumer.py"), PKG, lid, "-", res, "4000000000", P, W], env=env, cwd=PKG,
                        stdin=prod.stdout, stdout=open(os.path.join(OUT, tag + "_consumer.out"), "w"), stderr=subprocess.STDOUT)
prod.stdout.close(); cons.wait(); prod.wait()
print("%s: producer exit %s, consumer exit %s, %.0f s" % (KEY, prod.returncode, cons.returncode, time.time() - t0))
