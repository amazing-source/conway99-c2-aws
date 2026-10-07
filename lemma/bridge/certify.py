"""Exact certificate for the conversion "DEFERRED (pending T18 / T20)" -> excluded (BRIDGE.txt, section 8).

certificate(G, y1, y2, R) takes the integral Gram matrix G of a basis of U and integer coefficient vectors, and checks IN EXACT
INTEGERS every hypothesis the bridge theorem puts on the lattice side:
    G symmetric, integral, 24 x 24      (rank 24 and positive definiteness are those of the engine's lattice_data: det G = 1, LLL basis)
    (y1,y1) = (y2,y2) = 7,  (y1,y2) = 0
    a root r, (r,r) = 2, with (r,y1)^2 + (r,y2)^2 = 5  -> ("T18", r, a, b)       [E(r) = 9,  phi_r of squared norm 18]
    else a root r with (r,y1)^2 + (r,y2)^2 = 4         -> ("T20", r, a, b)       [E(r) = 10, phi_r of squared norm 20; T20 is OPEN]
It returns None if there is no such root, and raises AssertionError if a hypothesis fails (the pair is then INVALID, not excluded).
The quick variant of q/defer_consumer.py does NOT make the norm / orthogonality checks on the pairs it defers (the engine makes
them in pair_setup, which the quick variant does not reach), so they have to be made at conversion time: this function does it.

Self-test: python certify.py   (lattice 011 and the 400 pairs of the dossier; needs the package for lattice_data only)"""
import numpy as np


def ip(G, u, v):
    return sum(int(u[i]) * int(G[i][j]) * int(v[j]) for i in range(len(u)) for j in range(len(v)) if u[i] and v[j])


def certificate(G, y1, y2, R):
    n = len(G); assert n == 24 and all(len(row) == 24 for row in G)
    assert all(int(G[i][j]) == G[i][j] and G[i][j] == G[j][i] for i in range(n) for j in range(n))
    assert ip(G, y1, y1) == 7 and ip(G, y2, y2) == 7 and ip(G, y1, y2) == 0, "y1, y2 are not orthogonal vectors of norm 7"
    Gy1 = [sum(int(G[i][j]) * int(y1[j]) for j in range(n)) for i in range(n)]
    Gy2 = [sum(int(G[i][j]) * int(y2[j]) for j in range(n)) for i in range(n)]
    best = None
    for r in R:
        a = sum(int(r[i]) * Gy1[i] for i in range(n)); b = sum(int(r[i]) * Gy2[i] for i in range(n)); Y = a * a + b * b
        if Y in (5, 4) and (best is None or (Y == 5 and best[0] == "T20")):
            assert ip(G, r, r) == 2, "witness is not a root"
            best = ("T18" if Y == 5 else "T20", [int(x) for x in r], a, b)
            if Y == 5: break
    return best


if __name__ == "__main__":
    import sys, os, json, collections
    HERE = os.path.dirname(os.path.abspath(__file__)); SP = os.path.dirname(HERE)
    os.environ["NUMBA_CACHE_DIR"] = os.path.join(HERE, "numba_cache"); sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(SP, "pkgfull", "scripts"))
    from fractions import Fraction as F
    import frame_dfs_next as FD
    DOS = os.path.join(SP, "dossiers", "DOSSIER_WAGNER_2026-10-04")
    L = FD.lattice_data(json.load(open(os.path.join(DOS, "SOURCE_U_011.json")))["gens"], F(1)); G = L["G"].tolist()
    Bq = [[F(x) for x in row] for row in L["B"]]; Binv = np.linalg.inv(np.array([[float(x) for x in row] for row in L["B"]]))
    c = collections.Counter()
    for pr in json.load(open(os.path.join(DOS, "SOURCE_011_SAMPLE_PAIRS.json"))):
        yy = []
        for key in ("y1", "y2"):
            q = [F(x) for x in pr[key]]; cf = np.rint(np.array([float(x) for x in q]) @ Binv).astype(np.int64)
            assert [sum(int(cf[i]) * Bq[i][j] for i in range(24)) for j in range(24)] == q
            yy.append(cf.tolist())
        cert = certificate(G, yy[0], yy[1], L["R"].tolist())
        c[cert[0] if cert else "none"] += 1
    bad = [list(yy[0]), [2 * t for t in yy[1]]]
    try: certificate(G, bad[0], bad[1], L["R"].tolist()); print("ERROR: invalid pair accepted")
    except AssertionError as e: print("invalid pair rejected:", e)
    print(dict(c))
