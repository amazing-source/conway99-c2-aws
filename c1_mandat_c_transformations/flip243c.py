"""Pilot 1c.  Question: is the BvLS triangle flip exactly a simultaneous re-ruling of 3x3 grids of the far set
(keep the ruling parallel to T, replace the other ruling by one of the two diagonal rulings)?"""
import numpy as np, itertools, collections
R = "C:/home/researcher/Desktop/Nouveau/conway99-c1/data/srg243/"
def load(p, n=243):
    M = np.zeros((n, n), dtype=np.int64)
    for l in open(p):
        if l.strip():
            i, j = map(int, l.split()); M[i, j] = M[j, i] = 1
    return M
def vec(i): return tuple((i // 3 ** k) % 3 for k in range(5))
def idx(v): return sum((v[k] % 3) * 3 ** k for k in range(5))
def add(u, v, c=1): return tuple((a + c * b) % 3 for a, b in zip(u, v))
A = load(R + "bvls243.edges"); B = load(R + "twin243_switched.edges"); D = B - A
S = set(vec(j) for j in range(243) if A[0, j]); e0 = (1, 0, 0, 0, 0)
far = [i for i in range(243) if (D[i] != 0).any()]
def is_grid(M, pts):
    sub = M[np.ix_(pts, pts)]
    return sub.sum() == 36 and (sub.sum(1) == 4).all() and all((sub @ sub)[i, j] == 1 for i in range(9) for j in range(9) if sub[i, j])
grids = set(); bad = 0; newdir = collections.Counter()
for i in far:
    x = vec(i)
    for s in S:
        j = idx(add(x, s))
        if D[i, j] != -1: continue
        pts = sorted(idx(add(add(x, s, a), e0, b)) for a in range(3) for b in range(3))
        key = tuple(pts)
        if key in grids: continue
        grids.add(key)
        okA, okB = is_grid(A, pts), is_grid(B, pts)
        sub = D[np.ix_(pts, pts)]
        # new direction: differences of added edges inside the 9 points
        dirs = set()
        for p in pts:
            for q in pts:
                if D[p, q] == 1:
                    d = add(vec(q), vec(p), -1); dirs.add(min(d, add((0,) * 5, d, -1)))
        newdir[len(dirs)] += 1
        if not (okA and okB and (sub != 0).sum() == 36 and all(set(pts) <= set(far) for _ in [0])): bad += 1
print("far grids containing removed edges:", len(grids), " not (grid in A, grid in A', 9+9 edges exchanged):", bad)
print("number of new directions per grid:", dict(newdir))
print("removed edges covered:", len(grids) * 9, "of", int((D == -1).sum()) // 2)
# every changed pair lies inside one of these 9-sets
cov = np.zeros((243, 243), dtype=np.int64)
for g in grids:
    for p in g:
        for q in g: cov[p, q] += 1
print("changed pairs outside the grids:", int(((D != 0) & (cov == 0)).sum()), " max multiplicity of a changed pair:", int(cov[D != 0].max()))
per = collections.Counter(sum(1 for g in grids if i in g) for i in far)
print("grids per far vertex:", dict(per))
# the line parallel to T inside each grid is kept
kept = all(A[p, idx(add(vec(p), e0))] == 1 and B[p, idx(add(vec(p), e0))] == 1 for g in grids for p in g)
print("lines parallel to T kept in both graphs:", kept)
# grids of the new graph through the kept lines: are the re-ruled grids all the grids of A' containing a parallel far line?
