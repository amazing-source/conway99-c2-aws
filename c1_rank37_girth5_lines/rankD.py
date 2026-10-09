"""Python side of fastrD.exe: rank-mode star search when the radical of the Gram is made of true relations only
(component relations Z and balanced torsion vectors B), so that every far vertex carries a vector of a non-degenerate
space N0 of dimension D = 36 - rank(span):   Y_ii = -g(i,i), Y_ij = 3 + A_ij - g(i,j), rank(Y) <= D, Y 1 = 0,
g(i,j) = (3 + n_i)^T Gm (3 + n_j), Gm = (M0 + sum of z z^T over Z and B)^(-1) mod 7, shadows balanced for B."""
import os, subprocess
from fastlib import inv_mod7

EXE = os.path.abspath("fastrD.exe")


def run_rankD(adj, lay, comp, K, quota, Z, B, D, u, tag="x", limit=1, maxnodes=4000000000):
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    rel = Z + B
    for z in rel: assert all(sum(M0[i][j] * z[j] for j in range(36)) % 7 == 0 for i in range(36)), "not in the radical"
    Gm = inv_mod7([[(M0[i][j] + sum(z[i] * z[j] for z in rel)) % 7 for j in range(36)] for i in range(36)])
    assert Gm is not None, "the radical is larger than the given relations"
    path = f"frD_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {D} {len(quota)} {len(B)} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, Gm):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for tv in B: f.write(" ".join(map(str, tv)) + "\n")
    r = subprocess.run([EXE, path], capture_output=True, text=True)
    os.remove(path)
    out = r.stdout.strip().split("\n")
    return (out[-1] if out and out[-1] else "NO OUTPUT") + ((" ERR " + r.stderr.strip()) if r.stderr.strip() else "")


EXE2 = os.path.abspath("fastr2.exe")


def run_rank2(adj, lay, comp, K, quota, Z, B, D, u, tag="x", limit=1, maxnodes=4000000000):
    """two stars at once (fastr2.exe): u and its mate; same model as run_rankD"""
    M0 = [[(3 - (3 if i == j else 0) + (1 if j in adj[i] else 0)) % 7 for j in range(36)] for i in range(36)]
    rel = Z + B
    for z in rel: assert all(sum(M0[i][j] * z[j] for j in range(36)) % 7 == 0 for i in range(36)), "not in the radical"
    Gm = inv_mod7([[(M0[i][j] + sum(z[i] * z[j] for z in rel)) % 7 for j in range(36)] for i in range(36)])
    assert Gm is not None, "the radical is larger than the given relations"
    u2 = next(z for z in adj[u] if lay[z] == lay[u])
    path = f"fr2_{tag}_{os.getpid()}.txt"
    with open(path, "w") as f:
        f.write(f"{u} {u2} {D} {len(quota)} {len(B)} {limit} {maxnodes}\n" + " ".join(map(str, quota)) + "\n")
        f.write(" ".join(map(str, lay)) + "\n" + " ".join(map(str, comp)) + "\n")
        for v in range(36): f.write(" ".join(map(str, sorted(adj[v]))) + "\n")
        for M in (K, Gm):
            for row in M: f.write(" ".join(map(str, row)) + "\n")
        for tv in B: f.write(" ".join(map(str, tv)) + "\n")
    r = subprocess.run([EXE2, path], capture_output=True, text=True)
    os.remove(path)
    out = r.stdout.strip().split("\n")
    return (out[-1] if out and out[-1] else "NO OUTPUT") + ((" ERR " + r.stderr.strip()) if r.stderr.strip() else ""), out[:-1]
