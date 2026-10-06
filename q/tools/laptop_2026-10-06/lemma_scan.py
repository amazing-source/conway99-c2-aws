"""Where does the search time go, and which "dual minimum" lemma would remove it?  (laptop analysis, 2026-10-06, read-only)

For lattice LID: take the searched pairs sampled in the result files on the run/* branches (field sample_search: y1, y2, nodes),
and for each pair compute, with the package's own lattice_data():
  E(v) = 7 N(v) - (v,y1)^2 - (v,y2)^2  for every vector v of U of norm 2, 3, 4   (7 x the norm of the projection of v on {y1,y2}^perp).
The v10 lemma (min L* >= 9/7) kills a pair as soon as some v has E(v) = 8. A lemma "min L* >= m/7" would kill every pair whose
smallest positive E is below m. Output: histogram of Emin over the searched pairs, weighted by nodes, and which vectors realise it.
Optionally (--time N) re-runs search() on N of the pairs with the production flags and prints the time anatomy.
  .venv/Scripts/python.exe lemma_scan.py <repo> <pkg dir> <LID> [--time N]"""
import sys, os, json, subprocess, io, zipfile, time, collections
REPO, PKG, LID = sys.argv[1], sys.argv[2], "%03d" % int(sys.argv[3])
NT = int(sys.argv[sys.argv.index("--time") + 1]) if "--time" in sys.argv else 0
for k, v in dict(FD_LEMMA_U="1", FD_SYM="1", FD_SYM3="1", FD_MIN97="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1").items():
    os.environ[k] = v
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
from fractions import Fraction as F
from frame_dfs_next import lattice_data, search, char_trap, min97_witness

# ---- sampled searched pairs of this lattice, from every result on GitHub
refs = subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*"], capture_output=True, text=True).stdout.split()
pairs = {}; nrec = 0; tot_search = 0; tot_filt = 0; wall = 0.0
for r in refs:
    data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", r, "results"], capture_output=True).stdout
    if not data:
        continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in z.namelist():
        if not n.split("/")[-1].startswith(LID + "_") or not n.endswith(".jsonl"):
            continue
        for l in z.read(n).decode(errors="replace").splitlines():
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if "sample_search" not in d or "dual min" not in json.dumps(d.get("verdicts", {})) and d.get("code_sha", {}).get("frame_dfs_next.py") != "1591aeeac9c0be5c":
                continue                                             # v10 results only (pairs that survive the Y=13 filter)
            nrec += 1; wall += d.get("wall_secs", 0)
            tot_search += sum(c for k, c in d["verdicts"].items() if "stage 1 empty" in k or "star sums" in k or "Lemma Z" in k)
            tot_filt += sum(c for k, c in d["verdicts"].items() if "dual min" in k)
            for s in d["sample_search"]:
                pairs[(tuple(s["y1"]), tuple(s["y2"]))] = s
print("lattice %s: %d v10 result records, wall %.1f h, searched pairs %d, removed by the Y=13 filter %d, sampled searched pairs %d" % (
    LID, nrec, wall / 3600, tot_search, tot_filt, len(pairs)))
if not pairs:
    sys.exit(0)

t0 = time.time()
gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % LID)))["gens"]
L = lattice_data(gens, F(1)); G = L["G"]
Bq = np.array([[F(x) for x in row] for row in L["B"]], dtype=object); Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
print("lattice_data: %.0f s | roots %d, norm-3 pairs %d, norm-4 pairs %d, shadow roots %d" % (time.time() - t0, len(L["R"]), len(L["X3"]), len(L["X4"]), len(L["S2"])))


def conv(v):
    ex = np.array([F(t) for t in v], dtype=object)
    cf = np.rint(np.array([float(t) for t in ex]) @ Binv).astype(np.int64)
    assert np.array_equal(cf @ Bq, ex), "y not in U"
    return cf


VEC = [(2, L["R"]), (3, L["X3"]), (4, L["X4"])]
VG = [(N, (X @ G).astype(np.float64)) for N, X in VEC if len(X)]
hist = collections.Counter(); histn = collections.Counter(); real = collections.Counter(); rows = []
for (y1s, y2s), s in pairs.items():
    y1, y2 = conv(y1s), conv(y2s); f1, f2 = y1.astype(np.float64), y2.astype(np.float64)
    best = None; cnt = collections.Counter()
    for N, XG in VG:
        a = np.rint(XG @ f1).astype(np.int64); b = np.rint(XG @ f2).astype(np.int64)
        E = 7 * N - a * a - b * b
        for e in (8, 9, 10, 11, 12, 13, 14):
            c = int((E == e).sum())
            if c:
                cnt[(e, N)] = c
        assert E.min() >= 0, "negative projection norm"
        pos = E[E > 0]; m = int(pos.min())
        if best is None or m < best[0]:
            i = int(np.flatnonzero(E == m)[0]); best = (m, N, tuple(sorted((abs(int(a[i])), abs(int(b[i]))))))
    nodes = int(sum(s["nodes"]))
    hist[best[0]] += 1; histn[best[0]] += nodes; real[best] += 1
    rows.append((best[0], nodes, y1, y2, s, cnt))
tn = sum(histn.values())
print("\nEmin = smallest positive 7*|projection|^2 over the vectors of norm 2, 3, 4   (v10 already kills Emin = 8)")
print("%5s %8s %7s %14s %7s   realised by (norm of v, |(v,y1)|,|(v,y2)| sorted)" % ("Emin", "pairs", "%", "nodes", "%"))
for e in sorted(hist):
    who = ", ".join("N=%d %s x%d" % (k[1], k[2], c) for k, c in sorted(real.items()) if k[0] == e)
    print("%5d %8d %6.1f%% %14d %6.1f%%   %s" % (e, hist[e], 100.0 * hist[e] / len(rows), histn[e], 100.0 * histn[e] / tn, who))
cum = 0; cn = 0
print("\na lemma 'min L* >= m/7' would remove (of the pairs searched today):")
for e in sorted(hist):
    cum += hist[e]; cn += histn[e]
    print("   m = %2d : %5.1f%% of the pairs, %5.1f%% of the nodes" % (e + 1, 100.0 * cum / len(rows), 100.0 * cn / tn))

if NT:
    rows.sort(key=lambda r: r[1]); step = max(1, len(rows) // NT); sel = rows[::step][:NT]
    print("\ntime anatomy on %d pairs spread over the node-count range (laptop, 1 thread):" % len(sel))
    agg = collections.Counter(); tt = 0.0
    search(L, sel[0][2], sel[0][3], node_limit=4_000_000_000)      # JIT warm-up
    for emin, nodes, y1, y2, s, cnt in sel:
        t = time.time(); r = search(L, y1, y2, node_limit=4_000_000_000); dt = time.time() - t; tt += dt
        tm = r.get("tm", {}); sc = r.get("secs", {})
        agg["setup"] += sc.get("setup", 0); agg["dfs"] += sc.get("dfs", 0); agg["stage2"] += sc.get("stage2", 0)
        for k in ("pre", "compat", "packs", "sym", "sym3"):
            agg["  " + k] += tm.get(k, 0)
        agg["nodes"] += sum(r.get("nodes", [0])); agg["nH"] += r.get("nH", 0); agg["n"] += 1
    n = agg["n"]
    print("   total %.1f s for %d pairs = %.2f s/pair | nodes/pair %.0f | candidates h per pair %.0f" % (tt, n, tt / n, agg["nodes"] / n, agg["nH"] / n))
    for k in ("setup", "  pre", "  compat", "  packs", "  sym", "dfs", "  sym3", "stage2"):
        print("   %-10s %7.2f s  (%4.1f%%)" % (k, agg[k], 100.0 * agg[k] / tt))
