"""Route (C), root-poor lattices: plan + chunked y-pair STREAM (C1's y_pairs_gamma --stream) piped into hstage_stream.py (C2).
No pair list is written. Every chunk leaves one record in data/finishC/stream/<id>/chunks.jsonl (count, sha256 of the pair
stream checked against the producer, verdict counts, every non-EXCLUDED pair in full). Resumable: chunks already done are skipped.
Gamma: conway99-c1 data/finishC/gamma_ps/gamma_<id>.json (carries its basis; y_pairs_gamma converts and VERIFIES it in this
machine's basis, abort on mismatch), or the identity when Borcherds' group is 1. The plan is made HERE (plans carry basis_sha).
Priority BELOW_NORMAL, BLAS 1 thread; <par> chunks at a time (each = 1 producer + 1 consumer).
Usage: python stream_lattice.py <id> <n_chunks> [par=1] [max_seconds_per_chunk=86400]"""
import sys, os, json, time, subprocess, hashlib
LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
CLONE = r"C:\Users\RESEARCHER\AppData\Local\Temp\claude\C--Users-RESEARCHER-Desktop\19a7c411-3446-4f59-9793-6c42892ed6cd\scratchpad\ext\conway99-c1"
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMBA_NUM_THREADS="1", FD_LEMMA_U="1")
BN = 0x4000


def gamma_file(lid):
    g = os.path.join(CLONE, "data", "finishC", "gamma_ps", "gamma_%s.json" % lid)
    if os.path.exists(g): return g
    g2 = os.path.join(LAB, "data", "finishC", "gamma_c2", "gamma_%s.json" % lid)       # C2's own Gamma (make_gammas.py, C1's gamma_general.py)
    if os.path.exists(g2): return g2
    D = json.load(open(os.path.join(CLONE, "data", "borcherds_odd24.json"))); L = D if isinstance(D, list) else D.get("lattices", D)
    grp = {x["id"]: x.get("group") for x in L}.get(int(lid))
    if str(grp) == "1" or os.environ.get("STREAM_IDENTITY_OK") == "1":   # C2 29/09: Gamma={I} is a subgroup of Aut(U): orbits are finer, enumeration still complete (more pairs)
        g = os.path.join(LAB, "data", "finishC", "stream", lid, "gamma_identity_%s.json" % lid)
        if not os.path.exists(g):
            os.makedirs(os.path.dirname(g), exist_ok=True)
            I = [[1 if i == j else 0 for j in range(24)] for i in range(24)]
            json.dump({"id": int(lid), "matrices": [I], "note": "Gamma = {I} (table group 1, or fallback subgroup when no portable Gamma); the identity is basis-free"}, open(g, "w"))
        return g
    return None


def main():
    lid = "%03d" % int(sys.argv[1]); n = int(sys.argv[2]); par = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    maxs = sys.argv[4] if len(sys.argv) > 4 else "86400"
    D = os.path.join(LAB, "data", "finishC", "stream", lid); os.makedirs(D, exist_ok=True)
    LOG = os.path.join(D, "driver.log")
    def log(m):
        line = "%s %s" % (time.strftime("%H:%M:%S"), m); print(line, flush=True); open(LOG, "a").write(line + "\n")
    U = os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)
    gam = gamma_file(lid)
    if gam is None: log("no portable Gamma for %s: stop" % lid); return
    commit = subprocess.run(["git", "-C", CLONE, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    plan = os.path.join(D, "plan.json")
    if not os.path.exists(plan):
        r = subprocess.run([PY, os.path.join(CLONE, "code", "y_pairs_gamma.py"), U, gam, plan, "--plan"], env=ENV, cwd=os.path.join(CLONE, "code"),
                           capture_output=True, text=True, creationflags=BN)
        log("plan: %s %s" % (r.stdout.strip()[-400:], r.stderr.strip()[-300:]))
        if not os.path.exists(plan): log("plan FAILED: stop"); return
    out = os.path.join(D, "chunks.jsonl")
    done = set()
    if os.path.exists(out):
        for l in open(out):
            r = json.loads(l)
            if r.get("chunk_done") and r.get("chunk") and r["chunk"][1] == n: done.add(r["chunk"][0])
    todo = [k for k in range(n) if k not in done]
    log("lattice %s: %d chunks, %d done, gamma %s (sha %s), plan sha %s, conway99-c1 %s" % (lid, n, len(done), os.path.basename(os.path.dirname(gam)) + "/" + os.path.basename(gam),
        hashlib.sha256(open(gam, "rb").read()).hexdigest()[:12], hashlib.sha256(open(plan, "rb").read()).hexdigest()[:12], commit))
    running = []
    while todo or running:
        for x in list(running):
            prod, cons, k = x
            if cons.poll() is None: continue
            prod.wait(); running.remove(x)
            log("chunk %d/%d finished (producer exit %s, consumer exit %s)" % (k, n, prod.returncode, cons.returncode))
        while todo and len(running) < par:
            k = todo.pop(0)
            prod = subprocess.Popen([PY, os.path.join(CLONE, "code", "y_pairs_gamma.py"), U, gam, os.path.join(D, "stats_%d_%d.json" % (k, n)),
                                     "--from-plan", plan, "--chunk", "%d/%d" % (k, n), "--stream", "-", "--max-seconds", maxs],
                                    env=ENV, cwd=os.path.join(CLONE, "code"), stdout=subprocess.PIPE, stderr=open(os.path.join(D, "prod_%d.err" % k), "w"),
                                    creationflags=BN)
            cons = subprocess.Popen([PY, os.path.join(LAB, "scripts", "hstage_stream.py"), lid, "-", out], env=ENV, stdin=prod.stdout,
                                    stdout=open(os.path.join(D, "cons_%d.out" % k), "w"), stderr=subprocess.STDOUT, creationflags=BN)
            prod.stdout.close()                                              # the consumer owns the pipe now
            running.append((prod, cons, k)); log("chunk %d/%d started" % (k, n))
        time.sleep(15)
    recs = [json.loads(l) for l in open(out)] if os.path.exists(out) else []
    recs = [r for r in recs if r.get("chunk") and r["chunk"][1] == n]
    ok = {r["chunk"][0] for r in recs if r.get("chunk_done")}
    log("lattice %s: %d/%d chunks done, %d pairs in done chunks%s" % (lid, len(ok), n, sum(r["n_pairs"] for r in recs if r.get("chunk_done") and r["chunk"][0] in ok),
        "" if len(ok) == n else " -- NOT all chunks done: see chunks.jsonl (not_excluded / chunk_ok)"))


if __name__ == "__main__":
    main()
