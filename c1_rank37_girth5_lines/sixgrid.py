"""The line in six grids at rank 37: six components with one line per layer.  Such a component is a prism (a 6-vertex
component of K_{3,3} type is impossible at every rank: the apex of one of its transversal edges would have two shadow
points in it, against "exactly m_i shadow points in C_i").  So the ball is unique: six prisms.
Rank test: every far vertex carries a vector of a non-degenerate space of dimension 5; the 10 x 10 matrix of a star must
have rank <= 5 and zero row sums.   usage: sixgrid.py [u]"""
import sys, time
from multi import make_ball, kmatrix
from rankD import run_rankD

PRISM = ((1, 0), (1, 0), (1, 0), (0, 1))      # iota, t1, t2, pi = identity: triangles i^0 i^1 i^2
if __name__ == "__main__":
    keys = [PRISM] * 6; rhos = [(0, 1, 2)] * 6
    adj, lay, comp = make_ball(keys, rhos); K = kmatrix(adj, lay); quota = [1] * 6
    Z = [[(1 if comp[v] == k else (-1 if comp[v] == k + 1 else 0)) % 7 for v in range(36)] for k in range(5)]
    for u in ([int(sys.argv[1])] if len(sys.argv) > 1 else [0]):
        t0 = time.time()
        for D in (5,):
            res = run_rankD(adj, lay, comp, K, quota, Z, [], D, u, tag=f"six{D}", limit=1, maxnodes=20000000000)
            print(f"six grids, u = {u}, rank <= {D}: {res} | {time.time()-t0:.1f}s", flush=True)
