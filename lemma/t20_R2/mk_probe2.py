# experimental: "A1 probe".  For n = sum of +-e_O over <= 4 placed orbits with n^T G n = 2 c.n, the vector c - G n is
# another eigenvector of norm 10, so (A1) its entries on outer orbits are in {0,+-1} (inner: |.| <= 2).  Count nodes
# where a placed orbit violates this.  Non-pruning, exact integers.
s = open("eng4.py").read()
old = """        node.prepare()
        visited[t] += 1
        best = None
        newdoms = {}"""
new = """        node.prepare()
        visited[t] += 1
        if t >= 2:
            G = node.blocks[0].B
            k = G.shape[0]
            cvec = np.zeros(k, dtype=np.int64); cvec[:10] = 1
            inner = np.zeros(k, dtype=bool)
            for ii, v in enumerate(node.reps):
                if node.A[v, node.sig[v]]:
                    inner[ii] = True
            viol = False
            nfound = 0
            import itertools as _it
            idxs = list(range(k))
            for size in (2, 3, 4):
                for comb in _it.combinations(idxs, size):
                    sub = G[np.ix_(comb, comb)]
                    for signs in _it.product((1, -1), repeat=size - 1):
                        sg = np.array((1,) + signs)
                        for flip in (1, -1):
                            nv = sg * flip
                            q = int(nv @ sub @ nv)
                            sdot = int((cvec[list(comb)] * nv).sum())
                            if q == 2 * sdot and q > 0:
                                nfound += 1
                                full = np.zeros(k, dtype=np.int64); full[list(comb)] = nv
                                cp = cvec - G @ full
                                if (np.abs(cp[~inner]) > 1).any() or (np.abs(cp[inner]) > 2).any():
                                    viol = True
            probe_app[t] += 1 if nfound else 0
            probe_dead[t] += 1 if viol else 0
        best = None
        newdoms = {}"""
assert old in s; s = s.replace(old, new, 1)
old = """    looked = [0]"""
new = """    looked = [0]
    probe_app = [0] * L
    probe_dead = [0] * L"""
assert old in s; s = s.replace(old, new, 1)
old = """    print("lookahead candidates evaluated"""
new = """    print("PROBE2 nodes with some mutation n:", probe_app)
    print("PROBE2 nodes with an A1 violation:", probe_dead)
    print("lookahead candidates evaluated"""
assert old in s; s = s.replace(old, new, 1)
open("eng4probe2.py", "w").write(s)
