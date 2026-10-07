"""Route (C) h-stage on a STREAM of y-pairs (C2, 27/09 night; with C1's y_pairs_gamma --stream, conway99-c1 86aa064).
For the root-poor lattices (~10^7 pairs in all) no pair list is written: C1's enumerator streams the pairs of one chunk, this
consumer runs frame_dfs (general mode with C1's Lemma U+, same code as run_lattice) on EVERY pair and writes one record per chunk.

Input: JSON lines {"o": y1 orbit, "y1": [24 fraction strings], "y2": [24]} in AMBIENT coordinates (basis-free, protocol 27/09),
then a final line {"end": true, "id", "chunk": [k, n], "pairs": N, "complete": bool, "sha256"} where sha256 covers the pair
lines, each with its "\\n". Each y is converted to lattice coordinates EXACTLY (rounded coefficients must give the ambient vector
back, else the pair is INVALID, never EXCLUDED).
Output: one JSON line per chunk in <out.jsonl>: id, chunk, n_pairs, sha256 (recomputed here, must equal the producer's), complete,
verdict counts, and every pair that is not EXCLUDED in full (INCOMPLETE -> to be re-run with frame_dfs_split, INVALID, or a
leaf). A chunk counts as done only if complete, sha256 equal, count equal, and every pair EXCLUDED.
Usage: python hstage_stream.py <id> <stream path | -> <out.jsonl> [node_limit=200000000]"""
import sys, os, json, time, hashlib, collections, subprocess
os.environ.setdefault("FD_LEMMA_U", "1")                              # same mode as run_lattice.py (U+ general mode)
os.environ.setdefault("FD_SYM", "1")                                   # C2 28/09 symmetry breaking (proven)
SWAP = os.environ.get("FD_SWAP", "1") == "1"                           # C2 28/09 swap redundancy (Astra, proven)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fractions import Fraction as F
from frame_dfs import lattice_data, search

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLONE = r"C:\Users\RESEARCHER\AppData\Local\Temp\claude\C--Users-RESEARCHER-Desktop\19a7c411-3446-4f59-9793-6c42892ed6cd\scratchpad\ext\conway99-c1"


def main():
    lid = "%03d" % int(sys.argv[1]); src = sys.argv[2]; outp = sys.argv[3]
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 200_000_000
    gens = json.load(open(os.path.join(LAB, "external_runs", "structures_3eceb4d", "U", "%s.json" % lid)))["gens"]
    L = lattice_data(gens, F(1)); Bq = np.array([[F(x) for x in row] for row in L["B"]], dtype=object)
    Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
    commit = subprocess.run(["git", "-C", CLONE, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    co = (L["S2"] @ L["G"] @ L["S2"].T)[0] % 4 == 0
    def inv(y):
        h = np.abs(L["S2"] @ L["G"] @ y) == 3
        return (int(((L["R"] @ L["G"] @ y) ** 2).sum()),) + tuple(sorted((int(h[co].sum()), int(h[~co].sum()))))   # sorted: Aut may swap the cosets
    fh = sys.stdin.buffer if src == "-" else open(src, "rb")
    sh = hashlib.sha256(); n = 0; cnt = collections.Counter(); keep = []; end = None; t0 = time.time(); orbits = set(); info_lines = []
    for raw in fh:
        line = raw.rstrip(b"\r\n")
        if not line: continue
        rec = json.loads(line)
        if rec.get("end"): end = rec; break
        if "o" not in rec or "y1" not in rec:                               # producer info line (plan / stats): not a pair, not hashed
            info_lines.append(rec); continue
        sh.update(line + b"\n"); n += 1; orbits.add(rec["o"])
        yy = []; valid = True
        for key in ("y1", "y2"):
            ex = np.array([F(x) for x in rec[key]], dtype=object)
            cf = np.rint(np.array([float(x) for x in ex]) @ Binv).astype(np.int64)
            if not np.array_equal(cf @ Bq, ex): valid = False; break
            yy.append(cf)
        if not valid:
            cnt["INVALID (y not in U)"] += 1; keep.append({"o": rec["o"], "y1": rec["y1"], "y2": rec["y2"], "verdict": "INVALID"}); continue
        if SWAP and inv(yy[0]) > inv(yy[1]):
            # Unordered pairs: the ordered enumeration is complete up to Aut(U) x signs, so the orientation (y2, y1) is also
            # enumerated (as a pair of the y1-orbit of y2) and searched there; stage 1 is symmetric in y1, y2. I = Aut-invariant.
            cnt["SWAP-COVERED (I(y1)>I(y2))"] += 1; continue
        try:
            r = search(L, yy[0], yy[1], node_limit=lim)
        except AssertionError as e:                                        # e.g. norm/orthogonality assertions: never an exclusion
            r = {"verdict": "INVALID (%s)" % str(e)[:80]}
        v = r["verdict"]; cnt[v] += 1
        if not v.startswith("EXCLUDED"):
            keep.append({"o": rec["o"], "y1": rec["y1"], "y2": rec["y2"], "verdict": v, "nodes": r.get("nodes"), "counts": r.get("counts")})
    out = {"id": int(lid), "chunk": end.get("chunk") if end else None, "n_pairs": n, "orbits": len(orbits), "sha256": sh.hexdigest(),
           "producer": end, "producer_info": info_lines[:3], "verdicts": dict(cnt), "not_excluded": keep, "wall_secs": round(time.time() - t0, 1),
           "machine": "labpc", "frame_dfs": "U+ general mode", "node_limit": lim, "conway99_c1_commit": commit,
           "t": time.strftime("%Y-%m-%d %H:%M:%S")}
    ok = bool(end) and end.get("complete") is True and end.get("pairs") == n and end.get("sha256") == out["sha256"]
    out["chunk_ok"] = ok
    out["chunk_done"] = ok and n == sum(c for v, c in cnt.items() if v.startswith("EXCLUDED") or v.startswith("SWAP-COVERED"))
    open(outp, "a").write(json.dumps(out) + "\n")
    print(json.dumps({k: out[k] for k in ("id", "chunk", "n_pairs", "orbits", "verdicts", "chunk_ok", "chunk_done", "wall_secs")}), flush=True)


if __name__ == "__main__":
    main()
