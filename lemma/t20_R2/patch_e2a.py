s = open("eng2.py").read()
# faster exact quadratic form (still Python integers)
i = s.index("def pform(B, x):"); j = s.index("def exact_psd(Q):")
s = s[:i] + '''def pform(B, x):
    """x^T B x with Python integers (B: list of lists of Python ints, x: list of Python ints)"""
    tot = 0
    for row, xa in zip(B, x):
        if xa:
            tot += xa * sum(map(_mul, row, x))
    return tot


''' + s[j:]
s = s.replace("from fractions import Fraction\n", "from fractions import Fraction\nfrom operator import mul as _mul\n", 1)
old = '''    __slots__ = ("B", "Bp", "N", "name")

    def __init__(self, B, name):
        self.B = B
        self.name = name
'''
new = '''    __slots__ = ("B", "Bp", "N", "name", "Bf", "Bl")

    def __init__(self, B, name):
        self.B = B
        self.name = name
        self.Bf = B.astype(np.float64)
        self.Bl = B.tolist()           # Python integers
'''
assert old in s; s = s.replace(old, new, 1)
i = s.index("    def psd_fail(self, row, zz, stats):"); j = s.index("    def child(self, row, zz):")
s = s[:i] + '''    def psd_fail(self, row, zz, stats):
        """None if the candidate is kept; else (block name, x, q): x integer vector in block coordinates (last
        coordinate = the new orbit), q = x^T Block' x < 0 evaluated in Python integers, Block' = [[B, b], [b^T, c]]
        (x None if the rejection was decided by exact rational elimination)"""
        vecs = self.vectors(row, zz)
        for blk, (b, c) in zip(self.blocks, vecs):
            bf = b.astype(np.float64)
            y = blk.Bp @ bf
            s = c - float(bf @ y)
            res = blk.N @ bf
            r2 = float(res @ res)
            if s >= -TOL_S and r2 <= TOL_R:
                continue
            bl = b.tolist()
            ci = int(c)
            cert = None
            if r2 > TOL_R:
                t = (abs(s) + 2.0) / (2.0 * r2)
                cands = [-y - t * res]
                if s < -TOL_S:
                    cands.append(-y)
            else:
                cands = [-y]
            for u in cands:
                for sc in (1, 2, 3, 4, 6, 12, 30, 60, 120, 420, 1000, 2520, 10 ** 4, 10 ** 5, 10 ** 6):
                    uf = np.rint(u * sc)
                    qf = float(uf @ (blk.Bf @ uf)) + 2.0 * sc * float(uf @ bf) + sc * sc * c
                    if qf < -0.5:
                        ui = [int(v) for v in uf.tolist()]
                        q = pform(blk.Bl, ui) + 2 * sc * sum(map(_mul, ui, bl)) + sc * sc * ci
                        if q < 0:
                            cert = (ui + [sc], q)
                            break
                if cert:
                    break
            if cert is None:
                Bn = [rw + [bb] for rw, bb in zip(blk.Bl, bl)]
                Bn.append(bl + [ci])
                w, V = np.linalg.eigh(np.array(Bn, dtype=np.float64))
                if w[0] < 0:
                    v = V[:, 0]
                    mx = float(np.max(np.abs(v)))
                    for sc in (2, 3, 6, 12, 30, 100, 300, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8, 10 ** 10):
                        x = [int(round(float(tt) * sc / mx)) for tt in v]
                        q = pform(Bn, x)
                        if q < 0:
                            cert = (x, q)
                            break
                if cert is None:
                    if exact_psd(Bn):
                        stats.add("float_reject_but_exactly_psd_" + blk.name)
                        continue
                    stats.add("rejected_by_exact_elimination_" + blk.name)
                    return (blk.name, None, None)
            stats.add("psd_reject_" + blk.name)
            return (blk.name, cert[0], cert[1])
        return None

''' + s[j:]
open("eng2.py", "w").write(s)
