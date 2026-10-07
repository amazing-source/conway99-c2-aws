"""Recertification of the pairs of one y1 representative without the status form of the transfer rule (C2 lab, 2026-10-07).
Pure function of its inputs: no tracker is read, no network, no symmetry of the run-time order of exclusions.

  python twin_recert.py <package dir> <lid> <y1 index> <out dir> [--gamma <file>] [--plan <file>] [--lll <file>] [--max-seconds S]

Inputs: the package (lattice files, producer, engine lists), the plan and symmetry file of the lattice (default: the package's
data/finishC/stream/<lid>/plan.json and gamma/<lid>/*.json; --lll gives reduced bases for a lattice outside the package's basis
cache, through q/producer_lll.py). The producer is run for the single representative <y1 index> (chunk i/n, n = representatives
of the plan). EVERY pair (y1, y2) of its stream receives exactly one class, by exact integer arithmetic:
  W  a vector v of norm 2, 3 or 4 with 0 < E(v) = 7 (v,v) - (v,y1)^2 - (v,y2)^2 <= 10          ((R-vi), T16, T18, T20);
  Z  a characteristic vector z of norm 16 with (z,y1)^2 + (z,y2)^2 > 66                          ((R-v) and parity);
  M  the twin has STRICTLY MORE ROOTS than the lattice: its roots are rebuilt in integers, Q = 7x + (c-a) y1 + (d-b) y2, checked
     (Q G Q^T = 98 on the diagonal, all products divisible by 49, (Q,y) divisible by 7, rows distinct up to sign), and counted;
  C  the twin has the lattice's own root type, that type is carried by one lattice of the list only, and the engine's key
     decreases strictly: kkey of the twin's products < kkey of the lattice's (exact integers); the type is read from the integer
     product matrix alone (component with m lines: 2h - 4 lines non-orthogonal to a given one, rank = 2m / h);
  H  none of these: the pair must be examined directly (engine with the transfer rule and the swap rule off): it is listed.
The witness of W and Z is stored for every pair. Soundness of M and C does not use any status: M by descending induction on the
number of roots (the twin contains the same frame and is a lattice of the list), C because the image pair lies in the same
lattice with a smaller key and is itself of class W, Z, M or H there.
Output <out dir>/<lid>_<i>.json (counts per class, pairs, stream sha256, complete, hashes of the inputs and of this file) and
<lid>_<i>.npz (per pair: class, y2, witness; y1; all in integer coordinates of the basis written in the json), and
<lid>_<i>_H.jsonl (the pairs of class H in ambient coordinates, with an end record, ready for the engine).
A job whose producer does not end in the time limit writes "complete": false and NO class counts: it is never read as done.
ACCEPTANCE (written before any run): a representative is recertified when its json says complete, its stream has the number of
pairs of the producer's end record, the counts add up to the pairs, and the standalone checker passes on its npz; its class-H
pairs are then closed only by engine records with FD_TWIN=0 and FD_SWAP=0 in which every pair is EXCLUDED."""
import sys, os, json, time, hashlib, subprocess, math, collections, glob, re
from fractions import Fraction as F
import numpy as np


def parse(s):
    c = collections.Counter()
    for t, n, e in re.findall(r"([ade])_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?", s or ""): c[(t.upper(), int(n))] += int(e or 1)
    return tuple(sorted(c.items()))


def twin_Q(shells, y1, y2):
    out = []
    for X, XG, Ys in shells:
        a = XG @ y1; b = XG @ y2; m = np.isin(a * a + b * b, Ys); a, b, Xm = a[m], b[m], X[m]
        c = (2 * a + 2 * b + 3) % 7 - 3; d = (-2 * a + 2 * b + 3) % 7 - 3
        out.append(7 * Xm + np.outer(c - a, y1) + np.outer(d - b, y2))
    return np.vstack(out)


def exact_twin(Q, G, y1, y2):
    """(type, a_t, b_t): exact root type of the twin and the products of its roots with y1, y2"""
    assert np.abs(Q).max(initial=0) < 2 ** 20
    QG = Q @ G; P49 = QG @ Q.T; assert (np.diag(P49) == 98).all() and (P49 % 49 == 0).all(), "not twin roots"
    a7 = QG @ y1; b7 = QG @ y2; assert (a7 % 7 == 0).all() and (b7 % 7 == 0).all()
    S = {tuple(int(v) for v in q) for q in Q}; assert len(S) == len(Q) and not any(tuple(-v for v in q) in S for q in S), "rows not distinct up to sign"
    P = P49 // 49; n = len(Q); comp = -np.ones(n, int); k = 0
    for s in range(n):
        if comp[s] >= 0: continue
        st = [s]; comp[s] = k
        while st:
            x = st.pop()
            for y in np.flatnonzero(P[x] != 0):
                if comp[y] < 0: comp[y] = k; st.append(y)
        k += 1
    c = collections.Counter()
    for q in range(k):
        idx = np.flatnonzero(comp == q); m = len(idx); h2 = int((np.abs(P[idx[0], idx]) == 1).sum()) + 4
        assert (4 * m) % h2 == 0, "component is not a root system"; r = 4 * m // h2
        t = ("E", r) if (r, m) in ((6, 36), (7, 63), (8, 120)) else ("A", r) if m == r * (r + 1) // 2 else ("D", r)
        assert t[0] != "D" or m == r * (r - 1), "component is none of A, D, E"
        c[t] += 1
    return tuple(sorted(c.items())), a7 // 7, b7 // 7


def kkey(a, b):
    e1, e2 = int((a * a).sum()), int((b * b).sum())
    return (max(e1, e2), min(e1, e2), tuple(sorted(collections.Counter((a * a + b * b).tolist()).items())))


def main():
    pkg, lid, i, od = os.path.abspath(sys.argv[1]), "%03d" % int(sys.argv[2]), int(sys.argv[3]), os.path.abspath(sys.argv[4]); os.makedirs(od, exist_ok=True)
    opt = lambda f, d=None: sys.argv[sys.argv.index(f) + 1] if f in sys.argv else d
    U = os.path.join(pkg, "external_runs", "structures_3eceb4d", "U", lid + ".json")
    plan = os.path.abspath(opt("--plan", os.path.join(pkg, "data", "finishC", "stream", lid, "plan.json")))
    gam = opt("--gamma") or sorted(glob.glob(os.path.join(pkg, "gamma", lid, "*.json")))[0]; gam = os.path.abspath(gam); lll = opt("--lll"); ms = int(opt("--max-seconds", "3600"))
    sys.path.insert(0, os.path.join(pkg, "scripts")); import frame_dfs_next as FD
    t0 = time.time(); NR = len(json.load(open(plan))["y1_reps"]); tag = "%s_%d" % (lid, i); st = os.path.join(od, tag + ".stream.tmp")
    sha16 = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    head = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "producer_lll.py"), pkg, os.path.abspath(lll), "0"] if lll else [os.path.join(pkg, "c1", "code", "y_pairs_gamma.py")]
    r = subprocess.run([sys.executable] + head + [U, gam, os.path.join(od, tag + ".stats.tmp"), "--from-plan", plan, "--chunk", "%d/%d" % (i, NR), "--stream", st, "--max-seconds", str(ms)],
                       cwd=os.path.join(pkg, "c1", "code"), capture_output=True, text=True)
    base = {"id": int(lid), "y1_index": i, "y1_reps_in_plan": NR, "plan_sha256": sha16(plan), "gamma_sha256": sha16(gam), "lattice_file_sha256": sha16(U),
            "engine_sha256": sha16(os.path.join(pkg, "scripts", "frame_dfs_next.py")), "twin_recert_sha256": sha16(os.path.abspath(__file__)), "seconds_producer": round(time.time() - t0, 1)}
    end = None
    if r.returncode == 0 and os.path.exists(st):
        for line in open(st, "rb"):
            if b'"end"' in line: end = json.loads(line)
    if not (end and end.get("complete") is True):
        json.dump(dict(base, complete=False, why="producer: return code %s, end record %s" % (r.returncode, end)), open(os.path.join(od, tag + ".json"), "w"), indent=1)
        print(json.dumps({"id": lid, "y1": i, "complete": False})); return
    rec = json.load(open(U)); L = FD.lattice_data(rec["gens"], F(1)); G = np.asarray(L["G"], dtype=np.int64)
    Bq = [[x if isinstance(x, F) else F(int(x)) for x in row] for row in L["B"]]; DEN = 1
    for row in Bq:
        for x in row: DEN = DEN * int(x.denominator) // math.gcd(DEN, int(x.denominator))
    BD = np.array([[int(x * DEN) for x in row] for row in Bq], dtype=np.int64); Binv = np.linalg.inv(BD.astype(np.float64))
    lists = {k: np.asarray(L[k], dtype=np.int64).reshape(-1, 24) for k in ("R", "X3", "X4")}
    wsh = [(7 * n, lists[k] @ G, lists[k], n) for k, n in (("R", 2), ("X3", 3), ("X4", 4))]
    tsh = [(lists[k], lists[k] @ G, Ys) for k, Ys in (("R", (0, 5)), ("X3", (8, 9)), ("X4", (18,)))]
    own = parse(rec.get("roots")); nown = len(lists["R"]); RG = lists["R"] @ G
    own_unique = sum(1 for f in glob.glob(os.path.join(os.path.dirname(U), "*.json")) if parse(json.load(open(f)).get("roots")) == own) == 1
    sh = hashlib.sha256(); n = 0; cnt = collections.Counter(); A_cls = []; A_y2 = []; A_w = []; A_wn = []; A_e = []; y1c = None; H = []
    for raw in open(st, "rb"):
        line = raw.rstrip(b"\r\n")
        if not line: continue
        d = json.loads(line)
        if d.get("end") or "o" not in d or "y1" not in d: continue
        sh.update(line + b"\n"); n += 1; cs = []
        for key in ("y1", "y2"):
            v = np.array([int(F(x) * DEN) for x in d[key]], dtype=np.int64); c = np.rint(v.astype(np.float64) @ Binv).astype(np.int64); assert (c @ BD == v).all(), "y not in U"; cs.append(c)
        c1, c2 = cs; g1 = G @ c1; g2 = G @ c2; assert int(c1 @ g1) == 7 and int(c2 @ g2) == 7 and int(c1 @ g2) == 0
        if y1c is None: y1c = c1.copy()
        assert (y1c == c1).all(), "more than one y1 in the stream of one representative"
        cls = None; w = np.zeros(24, dtype=np.int64); wn = 0; e = 0
        for c7, XG, X, nrm in wsh:                                        # W: norm 2, then 3, then 4
            if not len(X): continue
            E = c7 - (XG @ c1) ** 2 - (XG @ c2) ** 2; j = int(E.argmin()); assert int(E[j]) > 0
            if int(E[j]) <= 10: cls = "W"; w = X[j]; wn = nrm; e = int(E[j]); break
        if cls is None:
            z = FD.char_trap(L, c1, c2)
            if z is not None:
                z = np.asarray(z, dtype=np.int64); yz = int(z @ g1) ** 2 + int(z @ g2) ** 2
                assert int(z @ G @ z) == 16 and ((G @ z - np.diag(G)) % 2 == 0).all() and yz > 66; cls = "Z"; w = z; wn = 16; e = yz
        if cls is None:
            Q = twin_Q(tsh, c1, c2); cls = "H"
            if len(Q):
                ty, at, bt = exact_twin(Q, G, c1, c2)
                if len(Q) > nown: cls = "M"; e = len(Q)
                elif own_unique and ty == own and kkey(at, bt) < kkey(RG @ c1, RG @ c2): cls = "C"; e = len(Q)
            if cls == "H": H.append(line)
        cnt[cls] += 1; A_cls.append("WZMCH".index(cls)); A_y2.append(c2); A_w.append(w); A_wn.append(wn); A_e.append(e)
    ok = end.get("pairs") == n and end.get("sha256") == sh.hexdigest()
    arr = {"cls": np.array(A_cls, dtype=np.int8), "y2": np.array(A_y2, dtype=np.int64).reshape(-1, 24), "w": np.array(A_w, dtype=np.int64).reshape(-1, 24), "wn": np.array(A_wn, dtype=np.int16),
           "e": np.array(A_e, dtype=np.int32), "y1": (y1c if y1c is not None else np.zeros(24, dtype=np.int64)).reshape(1, 24)}
    for k_ in ("y2", "w", "y1"): assert np.abs(arr[k_]).max(initial=0) < 30000; arr[k_] = arr[k_].astype(np.int16)
    npz = os.path.join(od, tag + ".npz"); np.savez_compressed(npz, **arr)
    hs = hashlib.sha256(); hf = os.path.join(od, tag + "_H.jsonl")
    with open(hf, "wb") as f:
        for line in H: f.write(line + b"\n"); hs.update(line + b"\n")
        f.write(json.dumps({"end": True, "id": int(lid), "chunk": [0, 1], "pairs": len(H), "complete": True, "sha256": hs.hexdigest()}).encode() + b"\n")
    out = dict(base, complete=bool(ok), pairs=n, stream_sha256=sh.hexdigest(), classes={k: cnt.get(k, 0) for k in "WZMCH"}, own_root_lines=nown, own_type_unique=bool(own_unique),
               basis=[[str(x) for x in row] for row in Bq], npz_sha256=hashlib.sha256(open(npz, "rb").read()).hexdigest(), seconds=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(od, tag + ".json"), "w"), indent=1)
    for f in (st, os.path.join(od, tag + ".stats.tmp")):
        if os.path.exists(f): os.remove(f)
    print(json.dumps({k: out[k] for k in ("id", "y1_index", "complete", "pairs", "classes", "seconds_producer", "seconds")}))


if __name__ == "__main__":
    main()
