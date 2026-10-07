# engv2.py = engv.py with the same tests computed faster: float64 (BLAS) products of small-integer matrices
# (exact), block bases cached per vertex-set size.  The integer certificates are unchanged (Python integers, full M).
s = open("engv.py").read()
old = """    def blocks(self, A, sig):
        n = A.shape[0]"""
new = """    def blocks(self, A, sig):
        n = A.shape[0]
        key = (n, tuple(sig))
        hit = self._bc.get(key) if hasattr(self, "_bc") else None
        if hit is not None:
            return hit
        if not hasattr(self, "_bc"):
            self._bc = {}
        r = self._blocks(A, sig)
        self._bc[key] = r
        return r

    def _blocks(self, A, sig):
        n = A.shape[0]"""
assert old in s; s = s.replace(old, new, 1)
old = """        n = A.shape[0]
        I = np.eye(n, dtype=np.int64)
        M1 = 9 * (3 * I - A) + 1
        M2 = 11 * (4 * I + A) - 2
        D, P = self.blocks(A, sig)
        # odd part: D^T M1 D = 18 G, D^T M2 D = 22 (7I - G),  G = 3I - A[R,R] + A[R,sigma R]
        G2 = D.T @ (3 * I - A) @ D            # = 2 G
        w, v = np.linalg.eigh(G2.astype(np.float64))"""
new = """        n = A.shape[0]
        I = np.eye(n, dtype=np.int64)
        M1 = 9 * (3 * I - A) + 1
        M2 = 11 * (4 * I + A) - 2
        D, P = self.blocks(A, sig)
        Df = D.astype(np.float64)
        Pf = P.astype(np.float64)
        Af = A.astype(np.float64)
        # odd part: D^T M1 D = 18 G, D^T M2 D = 22 (7I - G),  G = 3I - A[R,R] + A[R,sigma R]
        G2 = Df.T @ (3.0 * np.eye(n) - Af) @ Df            # = 2 G   (integer-valued, exact)
        w, v = np.linalg.eigh(G2)"""
assert old in s; s = s.replace(old, new, 1)
old = """            E1 = P.T @ M1 @ P
            w, v = np.linalg.eigh(E1.astype(np.float64))"""
new = """            E1 = Pf.T @ M1.astype(np.float64) @ Pf
            w, v = np.linalg.eigh(E1)"""
assert old in s; s = s.replace(old, new, 1)
old = """            E2 = P.T @ M2 @ P
            w, v = np.linalg.eigh(E2.astype(np.float64))"""
new = """            E2 = Pf.T @ M2.astype(np.float64) @ Pf
            w, v = np.linalg.eigh(E2)"""
assert old in s; s = s.replace(old, new, 1)
old = """def budgets_fail(A):
    C = A @ A
    V = C + A > 2"""
new = """def budgets_fail(A):
    Af = A.astype(np.float64)
    C = Af @ Af                       # integer-valued, exact
    V = C + Af > 2.5"""
assert old in s; s = s.replace(old, new, 1)
s = s.replace('"engine": "engv"', '"engine": "engv2"')
open("engv2.py", "w").write(s)
t = open("run_engv.py").read().replace("import engv, cases", "import engv2 as engv, cases")
t = t.replace('order = "first" if "first" in sys.argv[7:] else "mincand"', 'order = "first" if "first" in sys.argv[7:] else "mincand"\nsetw = "setwise" in sys.argv[7:]')
t = t.replace('use_rank=("norank" not in sys.argv[7:]), plan_file=planf)', 'use_rank=("norank" not in sys.argv[7:]), plan_file=planf, setwise=setw)')
open("run_engv2.py", "w").write(t)
print("engv2.py, run_engv2.py written")

# faster exact evaluation of x^T M x (still Python integers): M = a I + b A + c J with (a, b, c) = (27, -9, 1) for M1
# and (44, 11, -2) for M2, so x^T M x = a |x|^2 + b * sum_{(u,v): A_uv = 1} x_u x_v + c (sum x)^2.
s = open("engv2.py").read()
old = """def int_cert(M, P, vec):"""
new = """def qf_python(M, x):
    \"\"\"x^T M x with Python integers, M = 9(3I-A)+J or 11(4I+A)-2J (recognised by its diagonal)\"\"\"
    xs = [int(t) for t in x]
    d0 = int(M[0, 0])
    if d0 == 28:
        a, b, c = 27, -9, 1
    elif d0 == 42:
        a, b, c = 44, 11, -2
    else:
        raise ValueError("unexpected matrix")
    n = M.shape[0]
    R = M - c - a * np.eye(n, dtype=np.int64)        # = b * A
    assert int(np.abs(np.diag(R)).sum()) == 0
    us, vs = np.nonzero(R)
    assert bool((R[us, vs] == b).all())
    xAx = sum(xs[u] * xs[v] for u, v in zip(us.tolist(), vs.tolist()))
    sx = sum(xs)
    xx = sum(t * t for t in xs)
    return a * xx + b * xAx + c * sx * sx


def int_cert(M, P, vec):"""
assert old in s; s = s.replace(old, new, 1)
open("engv2.py", "w").write(s)
print("qf patched")
