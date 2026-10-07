# builds eng3.py from eng2.py (Node class and exact certificate code are kept; the search is replaced)
s = open("eng2.py").read()
s = s.replace("# T20 round 2: fast orbit-by-orbit engine.  Same model as eng.py (see its header), different tests:",
"""# T20 round 2: orbit-by-orbit engine with DYNAMIC unit order ("fail first").  Same model as eng.py (see its header).
# At every node all uncovered units are examined (floating-point selection, vectorised); the unit with the fewest
# surviving candidates is chosen (the first one, in increasing order, among ties; the scan stops at the first
# unit with no survivor).  Exhaustiveness: the chosen unit must be N(z) n S+ of some vertex z of X_2 whose orbit
# is not yet placed, and ALL candidates (V, N0, edges to the earlier orbits) of that unit are either kept or
# rejected exactly (budget count, or integer certificate, or exact elimination).  The other units only serve to
# choose; nothing is concluded from them.
# Tests:""")
old = "    def budget_fail(self, row, zz):"
new = '''    def evaluate(self, R):
        """vectorised selection for a batch of candidate rows (zz = 0): returns (budget_bad [exact], psd_bad [float])"""
        A = self.A
        RS = R[:, self.sigarr]
        bad = ((R @ A + R) > 2).any(1)
        bad |= (R * RS).sum(1) > 2
        bad |= ((R @ self.W1) * R).sum(1) > 0
        T = R * RS
        bad |= ((T @ self.W2) * T).sum(1) > 0
        a = R[:, self.reps]
        b = R[:, self.sreps]
        aodd = (b - a).astype(np.float64)
        aev = a + b
        rf = R[:, self.fixed]
        vecs = ((aodd, 3.0), (-aodd, 4.0),
                (np.hstack((2 - 18 * rf, 4 - 18 * aev)).astype(np.float64), 58.0),
                (np.hstack((22 * rf - 4, 22 * aev - 8)).astype(np.float64), 80.0))
        pb = np.zeros(R.shape[0], dtype=bool)
        for blk, (Bv, c) in zip(self.blocks, vecs):
            Y = Bv @ blk.Bp
            s = c - np.einsum("ij,ij->i", Bv, Y)
            Res = Bv @ blk.N
            r2 = np.einsum("ij,ij->i", Res, Res)
            pb |= (s < -TOL_S) | (r2 > TOL_R)
        return bad, pb

    def budget_fail(self, row, zz):'''
assert old in s
s = s.replace(old, new, 1)
old = "        self.C = A @ A\n"
new = '''        self.C = A @ A
        CA = self.C + A
        self.W1 = (CA >= 2).astype(np.int64)
        np.fill_diagonal(self.W1, 0)
        self.W2 = (CA >= 1).astype(np.int64)
        np.fill_diagonal(self.W2, 0)
'''
assert old in s
s = s.replace(old, new, 1)
i = s.index("def run(prob")
s = s[:i] + open("eng3_run.txt").read()
open("eng3.py", "w").write(s)
print("eng3.py written")
