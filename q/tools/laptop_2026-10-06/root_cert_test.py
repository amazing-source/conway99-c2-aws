"""Experiment (laptop, 2026-10-06): the 9 frame vectors that must meet a root r with E(r) = 9.

For a pair (y1,y2) and a root r of U with (r,y1)^2 + (r,y2)^2 = 5, a frame would give phi_f = (f, r) with (proved in the note):
  phi_u in {0,+-1};  the h meeting r: none, or exactly two at +-1;  the words meeting r: 9, or 7.
Orient g = phi_f f, so (g, r) = 1. Then sum g = s = 7 r - (r,y1) y1 - (r,y2) y2, i.e. every g_i has
  sum_{j != i} (g_i, g_j) = 7 - N(g_i)   (4 for a word, 3 for an h),  with pairwise products in {0,+-1} (and 0 between two h).
Case (i): 9 words.  Case (ii): 2 h + 7 words.
This script measures, on sampled searched pairs: the sizes of the candidate sets through r, and the number of case-(i) solutions
found by a small exhaustive search (with a node budget). Case (ii) is only sized here.
  .venv/Scripts/python.exe root_cert_test.py <repo> <pkg dir> <LID> <N pairs> [node budget]"""
import sys, os, json, subprocess, io, zipfile, time, collections
REPO, PKG, LID, NP = sys.argv[1], sys.argv[2], "%03d" % int(sys.argv[3]), int(sys.argv[4])
BUDGET = int(sys.argv[5]) if len(sys.argv) > 5 else 2_000_000
for k, v in dict(FD_LEMMA_U="1", FD_SYM="1", FD_SYM3="1", FD_MIN97="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1").items():
    os.environ[k] = v
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
from fractions import Fraction as F
import frame_dfs_next as FD

refs = subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/run/q-*"], capture_output=True, text=True).stdout.split()
pairs = {}
for r in refs:
    data = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", r, "results"], capture_output=True).stdout
    if not data:
        continue
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in z.namelist():
        if n.split("/")[-1].startswith(LID + "_") and n.endswith(".jsonl"):
            for l in z.read(n).decode(errors="replace").splitlines():
                try:
                    d = json.loads(l)
                except ValueError:
                    continue
                if d.get("code_sha", {}).get("frame_dfs_next.py") == "1591aeeac9c0be5c":
                    for s in d.get("sample_search", []):
                        pairs[(tuple(s["y1"]), tuple(s["y2"]))] = s
gens = json.load(open(os.path.join(PKG, "external_runs", "structures_3eceb4d", "U", "%s.json" % LID)))["gens"]
L = FD.lattice_data(gens, F(1)); G = L["G"]
Bq = np.array([[F(x) for x in row] for row in L["B"]], dtype=object); Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
RG = L["R"] @ G


def conv(v):
    ex = np.array([F(t) for t in v], dtype=object)
    cf = np.rint(np.array([float(t) for t in ex]) @ Binv).astype(np.int64)
    assert np.array_equal(cf @ Bq, ex)
    return cf


def nine_words(T, budget):
    """count the 9-subsets I of the candidates with T_ij in {-1,0,1} (i != j in I) and every row sum over I equal to 4.
    Returns (number of solutions, nodes, complete)."""
    n = len(T); ok = (np.abs(T) <= 1); np.fill_diagonal(ok, False)
    sols = 0; nodes = 0; complete = True
    # iterative DFS: stack of (chosen list, candidate index array, row sums of chosen, partial sums of the candidates)
    order = np.arange(n)
    stack = [([], order, np.zeros(0, dtype=np.int64), np.zeros(n, dtype=np.int64))]
    while stack:
        chosen, cand, rs, ps = stack.pop()
        k = len(chosen); need = 9 - k
        if need == 0:
            if (rs == 4).all(): sols += 1          # every row sum must be exactly 4
            continue
        # prune: every chosen row must still reach 4 with `need` more entries of at most +1 (and not exceed it by more than `need`)
        if k and ((rs + need < 4).any() or (rs - need > 4).any()):
            continue
        # candidates must also be able to reach 4: partial sum with the chosen + (need - 1) >= 4 and partial - (need - 1) <= 4
        keep = (ps[cand] + (need - 1) >= 4) & (ps[cand] - (need - 1) <= 4)
        cand = cand[keep]
        if len(cand) < need:
            continue
        for t, c in enumerate(cand):
            nodes += 1
            if nodes > budget:
                return sols, nodes, False
            rest = cand[t + 1:]
            rest = rest[ok[c, rest]]
            if len(rest) < need - 1:
                continue
            stack.append((chosen + [int(c)], rest, np.append(rs + T[c, chosen], ps[c]) if k else np.array([0], dtype=np.int64), ps + T[c]))
    return sols, nodes, complete


rows = sorted(pairs.items(), key=lambda kv: sum(kv[1]["nodes"]))
sel = []
for (y1s, y2s), s in rows:
    y1, y2 = conv(y1s), conv(y2s)
    a = RG @ y1; b = RG @ y2
    i9 = np.flatnonzero(a * a + b * b == 5)
    if len(i9):
        sel.append((y1, y2, s, i9))
step = max(1, len(sel) // NP); sel = sel[::step][:NP]
print("lattice %s: testing %d sampled searched pairs that have a root with E = 9" % (LID, len(sel)))
print("%9s %5s %5s | %5s %5s | %10s %9s %8s %7s" % ("dfs nodes", "nW", "nH", "W_r", "H_r", "case(i)", "nodes", "complete", "secs"))
agg = collections.Counter(); tot_t = 0.0
for y1, y2, s, i9 in sel:
    ps, why = FD.pair_setup_fast(L, y1, y2)
    W, H = ps["W"], ps["H"]
    best = None
    for ri in i9:                                    # try every E = 9 root, keep the most constraining one
        r = L["R"][ri]; rg = RG[ri]
        wr = W @ rg; hr = H @ rg
        Wr = np.concatenate([W[wr == 1], -W[wr == -1]]); nHr = int((np.abs(hr) == 1).sum())
        if best is None or len(Wr) < len(best[0]):
            best = (Wr, nHr, int((np.abs(hr) == 2).sum()))
    Wr, nHr, nH2 = best
    T = Wr @ G @ Wr.T
    t = time.time(); sols, nodes, comp = nine_words(T.astype(np.int64), BUDGET); dt = time.time() - t; tot_t += dt
    agg["pairs"] += 1; agg["sol0"] += (sols == 0 and comp); agg["incomplete"] += (not comp); agg["Hr0"] += (nHr == 0)
    agg["dead"] += (sols == 0 and comp and nHr < 2)
    print("%9d %5d %5d | %5d %5d | %10d %9d %8s %7.2f" % (sum(s["nodes"]), len(W), len(H), len(Wr), nHr, sols, nodes, comp, dt))
n = agg["pairs"]
print("\ncase (i) has NO solution (complete search): %d / %d pairs | incomplete (budget): %d | pairs with fewer than 2 h through r: %d" % (
    agg["sol0"], n, agg["incomplete"], agg["Hr0"]))
print("pairs killed by the root alone (no 9 words, and case (ii) impossible because < 2 candidate h meet r): %d / %d" % (agg["dead"], n))
print("mini-search time: %.2f s per pair on average" % (tot_t / max(1, n)))
