"""Test of the root rule R9 on real searched pairs (laptop, 2026-10-06).

Claim (from the tight-frame identity on {y1,y2}^perp, |(u,r)| <= 1, the local star sums 3 a_c = sum of the +-b_u of star c, each word
in two stars, and Lemma Z): for a root r of U with (r,y1)^2 + (r,y2)^2 = 5, i.e. E(r) = sum_h (h,r)^2 + #{u: (u,r) != 0} = 9,
the 7 frame h meet r either not at all or exactly twice at +-1. In particular NO frame h has |(h,r)| = 2.
Rule R9a: delete every candidate h with |(h,r)| = 2 for such a root r, before the search.
This script runs the production search with and without R9a on sampled searched pairs and compares nodes, time and verdicts.
  .venv/Scripts/python.exe root_rule_test.py <repo> <pkg dir> <LID> <N pairs>"""
import sys, os, json, subprocess, io, zipfile, time, collections
REPO, PKG, LID, NP = sys.argv[1], sys.argv[2], "%03d" % int(sys.argv[3]), int(sys.argv[4])
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


def conv(v):
    ex = np.array([F(t) for t in v], dtype=object)
    cf = np.rint(np.array([float(t) for t in ex]) @ Binv).astype(np.int64)
    assert np.array_equal(cf @ Bq, ex)
    return cf


RG = L["R"] @ G
orig_setup = FD.pair_setup_fast
STAT = {}


def setup_r9(L_, y1, y2):
    ps, why = orig_setup(L_, y1, y2)
    if ps is None:
        return ps, why
    a = RG @ y1; b = RG @ y2; sel = (a * a + b * b) == 5
    STAT["roots9"] = int(sel.sum()); STAT["nH0"] = len(ps["H"])
    if sel.any():
        HR = ps["H"] @ RG[sel].T
        keep = ~(np.abs(HR) == 2).any(axis=1)
        ps["H"] = ps["H"][keep]; ps["HS"] = ps["HS"][keep]; ps["V"] = ps["V"][keep]; ps["HSfull"] = ps["HS"]
        STAT["met1"] = int((np.abs(HR[keep]) == 1).any(axis=1).sum())
    STAT["nH1"] = len(ps["H"])
    return ps, why


rows = sorted(pairs.items(), key=lambda kv: sum(kv[1]["nodes"]))
with9 = []
for (y1s, y2s), s in rows:
    y1, y2 = conv(y1s), conv(y2s)
    if (((RG @ y1) ** 2 + (RG @ y2) ** 2) == 5).any():
        with9.append((y1, y2, s))
step = max(1, len(with9) // NP); sel = with9[::step][:NP]
print("lattice %s: %d sampled searched pairs, %d with a root of E = 9; testing %d of them (spread over the node counts)" % (LID, len(rows), len(with9), len(sel)))
FD.search(L, sel[0][0], sel[0][1], node_limit=4_000_000_000)        # JIT warm-up
T0 = T1 = 0.0; N0 = N1 = 0; H0 = H1 = 0; bad = 0; verd = collections.Counter(); r9 = 0
for y1, y2, s in sel:
    FD.pair_setup_fast = orig_setup
    t = time.time(); r0 = FD.search(L, y1, y2, node_limit=4_000_000_000); t0 = time.time() - t
    FD.pair_setup_fast = setup_r9
    t = time.time(); r1 = FD.search(L, y1, y2, node_limit=4_000_000_000); t1 = time.time() - t
    T0 += t0; T1 += t1; N0 += sum(r0["nodes"]); N1 += sum(r1["nodes"]); H0 += STAT["nH0"]; H1 += STAT["nH1"]; r9 += STAT["roots9"]
    verd[(r0["verdict"], r1["verdict"])] += 1
    if not (r0["verdict"].startswith("EXCLUDED") and r1["verdict"].startswith("EXCLUDED")):
        bad += 1
FD.pair_setup_fast = orig_setup
n = len(sel)
print("roots with E = 9 per pair: %.1f" % (r9 / n))
print("candidates h per pair : %7.0f -> %7.0f   (%.0f%% removed by R9a)" % (H0 / n, H1 / n, 100.0 * (H0 - H1) / max(1, H0)))
print("search nodes per pair : %7.0f -> %7.0f   (x%.2f fewer)" % (N0 / n, N1 / n, N0 / max(1, N1)))
print("time per pair         : %7.2f -> %7.2f s (x%.2f faster)" % (T0 / n, T1 / n, T0 / max(1e-9, T1)))
print("verdicts (without -> with):")
for k, c in verd.most_common():
    print("   %4d  %s  ->  %s" % (c, k[0], k[1]))
print("pairs not EXCLUDED in either run:", bad)
